import os
import pandas as pd
import shutil
import json
import re
import unicodedata
from tkinter import filedialog, Tk

# --- CONFIGURACIÓN ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RUTA_DESTINO_FOTOS = os.path.join(BASE_DIR, "public", "images", "properties")
RUTA_JSON_ASTRO = os.path.join(BASE_DIR, "src", "data", "propiedades.json")

def slugify(text):
    """Convierte texto en slug apto para URL."""
    text = str(text).strip().lower()
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[-\s]+", "-", text).strip("-")
    return text

def pedir_ruta(tipo="archivo"):
    root = Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    ruta = filedialog.askopenfilename() if tipo == "archivo" else filedialog.askdirectory()
    root.destroy()
    return ruta

def run_pipeline():
    path_excel = pedir_ruta("archivo")
    path_fotos = pedir_ruta("carpeta")

    if not path_excel or not path_fotos: 
        print("❌ Selección cancelada.")
        return

    # Limpiar destino de imágenes para evitar duplicados viejos
    if os.path.exists(RUTA_DESTINO_FOTOS): shutil.rmtree(RUTA_DESTINO_FOTOS)
    os.makedirs(RUTA_DESTINO_FOTOS, exist_ok=True)

    try:
        # 1. Leer Excel
        df = pd.read_excel(path_excel)
        
        # 2. MANEJO DE CELDAS COMBINADAS
        # Rellena hacia abajo valores nulos en columnas clave
        df['titulo'] = df['titulo'].ffill()
        df['zona'] = df['zona'].ffill()
        df['ciudad'] = df['ciudad'].ffill()

        propiedades_json_list = []

        print(f"🚀 Procesando {len(df)} registros...")

        for _, row in df.iterrows():
            # ID único
            prop_id = str(row.get("id", "")).strip().upper()
            if not prop_id or prop_id == "NAN": continue

            # Título de la propiedad
            titulo_final = str(row.get("titulo", "")).strip()
            
            # --- GENERACIÓN DE SLUG (Título + ID para unicidad) ---
            slug_compuesto = slugify(f"{titulo_final}-{prop_id}")

            # --- GESTIÓN DE FOTOS ---
            fotos_registradas = []
            folder_origen = os.path.join(path_fotos, prop_id)
            
            if os.path.isdir(folder_origen):
                dest_path = os.path.join(RUTA_DESTINO_FOTOS, prop_id)
                os.makedirs(dest_path, exist_ok=True)
                
                # Obtener y ordenar imágenes
                archivos = sorted([f for f in os.listdir(folder_origen) 
                                 if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))])
                
                for i, f in enumerate(archivos, 1):
                    ext = os.path.splitext(f)[1].lower()
                    nuevo_nombre = f"{prop_id}_{i}{ext}"
                    shutil.copy2(os.path.join(folder_origen, f), os.path.join(dest_path, nuevo_nombre))
                    fotos_registradas.append(f"/images/properties/{prop_id}/{nuevo_nombre}")

            # --- LIMPIEZA DE DATOS NUMÉRICOS ---
            def clean_num(val, is_int=False):
                if pd.isna(val): return 0
                try:
                    return int(float(val)) if is_int else float(val)
                except:
                    return 0

            # --- CONSTRUCCIÓN DEL OBJETO ---
            prop_data = {
                "id": prop_id,
                "slug": slug_compuesto,
                "titulo": titulo_final,
                "operacion": str(row.get("operacion", "venta")).strip().lower(),
                "tipo": str(row.get("tipo", "casa")).strip().lower(),
                "precio": clean_num(row.get("precio"), True),
                "zona": str(row.get("zona", "")).strip(),
                "ciudad": str(row.get("ciudad", "Xalapa")).strip(),
                "m2Terreno": clean_num(row.get("m2Terreno")),
                "m2Construccion": clean_num(row.get("m2Construccion")),
                "recamaras": clean_num(row.get("recamaras"), True),
                "banos": clean_num(row.get("banos"), True),
                "estacionamientos": clean_num(row.get("estacionamientos"), True),
                "descripcion": str(row.get("descripcion", "")).strip(),
                "whatsapp": str(row.get("whatsapp", "2281852255")).split('.')[0].strip(),
                "fecha_publicacion": str(row.get("fecha_publicacion", "")).strip(),
                "estatus": str(row.get("estatus", "disponible")).strip().lower(),
                "imagenes": fotos_registradas if fotos_registradas else ["/images/placeholder.jpg"]
            }
            
            propiedades_json_list.append(prop_data)
            print(f"✅ {prop_id} | Slug: {slug_compuesto}")

        # Guardar JSON Final
        os.makedirs(os.path.dirname(RUTA_JSON_ASTRO), exist_ok=True)
        with open(RUTA_JSON_ASTRO, "w", encoding="utf-8") as f:
            json.dump(propiedades_json_list, f, indent=2, ensure_ascii=False)
        
        print(f"\n✨ ¡Pipeline completado! {len(propiedades_json_list)} propiedades exportadas.")

    except Exception as e:
        print(f"❌ Error crítico durante el proceso: {e}")

if __name__ == "__main__":
    run_pipeline()