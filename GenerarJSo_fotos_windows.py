import os
import pandas as pd
import shutil
import json
import re
from datetime import datetime
from tkinter import filedialog, Tk

# --- CONFIGURACIÓN DE RUTAS ---
BASE_URL = "" 
RUTA_DESTINO_FOTOS = "./public/images/properties/"
RUTA_JSON_ASTRO = "./src/data/propiedades.json"

def slugify(text):
    text = str(text).lower()
    text = re.sub(r'[áéíóúüñ]', lambda m: {'á':'a','é':'e','í':'i','ó':'o','ú':'u','ü':'u','ñ':'n'}[m.group()], text)
    text = re.sub(r'[^\w\s-]', '', text)
    return re.sub(r'[-\s]+', '-', text).strip('-')

def pedir_ruta_windows(tipo="archivo"):
    """Selector de archivos nativo para Windows"""
    root = Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    if tipo == "archivo":
        ruta = filedialog.askopenfilename(title="Selecciona el Excel", filetypes=[("Excel", "*.xlsx *.xls")])
    else:
        ruta = filedialog.askdirectory(title="Selecciona carpeta de fotos originales")
    root.destroy()
    return ruta if ruta else None

def run_full_pipeline():
    # 1. Pedir rutas
    path_excel = pedir_ruta_windows("archivo")
    path_fotos_origen = pedir_ruta_windows("carpeta")
    
    if not path_excel or not path_fotos_origen:
        print("❌ Operación cancelada por el usuario.")
        return

    print("🧹 Iniciando limpieza profunda en Windows...")
    
    # Borrar JSON anterior
    if os.path.exists(RUTA_JSON_ASTRO):
        os.remove(RUTA_JSON_ASTRO)

    # Borrar y recrear carpeta de fotos destino
    if os.path.exists(RUTA_DESTINO_FOTOS):
        shutil.rmtree(RUTA_DESTINO_FOTOS)
    os.makedirs(RUTA_DESTINO_FOTOS, exist_ok=True)

    try:
        df = pd.read_excel(path_excel)
        propiedades_json_list = []
        
        print(f"🚀 Procesando {len(df)} filas...")

        for index, row in df.iterrows():
            prop_id = str(row.get('id', '')).strip()
            titulo = str(row.get('titulo', '')).strip()
            
            if not prop_id or prop_id == 'nan' or not titulo:
                continue

            # --- PROCESAMIENTO DE FOTOS ---
            folder_origen = None
            # Buscamos la carpeta del ID ignorando mayúsculas
            for d in os.listdir(path_fotos_origen):
                if d.lower().strip() == prop_id.lower().strip():
                    folder_origen = os.path.join(path_fotos_origen, d)
                    break

            fotos_registradas = []
            if folder_origen and os.path.isdir(folder_origen):
                folder_destino_web = os.path.join(RUTA_DESTINO_FOTOS, prop_id)
                os.makedirs(folder_destino_web, exist_ok=True)
                
                archivos = [f for f in os.listdir(folder_origen) 
                           if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))]
                archivos.sort()

                for i, archivo_orig in enumerate(archivos, start=1):
                    ext = os.path.splitext(archivo_orig)[1].lower()
                    nuevo_nombre = f"{prop_id}_{i}{ext}"
                    
                    # Copiamos la foto del origen a la carpeta public de Astro
                    shutil.copy2(os.path.join(folder_origen, archivo_orig), 
                                 os.path.join(folder_destino_web, nuevo_nombre))
                    
                    # Ruta relativa que usará Astro
                    fotos_registradas.append(f"/images/properties/{prop_id}/{nuevo_nombre}")

            # --- CONSTRUCCIÓN DEL OBJETO JSON ---
            prop_data = {
                "id": prop_id,
                "slug": slugify(titulo),
                "titulo": titulo,
                "descripcion": str(row.get('descripcion', '')).strip(),
                "operacion": str(row.get('operacion', 'venta')).lower().strip(),
                "tipo": str(row.get('tipo', 'casa')).lower().strip(),
                "precio": int(row.get('precio', 0)) if pd.notnull(row.get('precio')) else 0,
                "moneda": "MXN",
                "zona": str(row.get('zona', '')).strip(),
                "ciudad": str(row.get('ciudad', 'Veracruz')).strip(),
                "m2Terreno": int(row.get('m2Terreno', 0)) if pd.notnull(row.get('m2Terreno')) else 0,
                "m2Construccion": int(row.get('m2Construccion', 0)) if pd.notnull(row.get('m2Construccion')) else 0,
                "recamaras": int(row.get('recamaras', 0)) if pd.notnull(row.get('recamaras')) else 0,
                "banos": int(row.get('banos', 0)) if pd.notnull(row.get('banos')) else 0,
                "estacionamientos": int(row.get('estacionamientos', 0)) if pd.notnull(row.get('estacionamientos')) else 0,
                "fechaPublicacion": str(row.get('fecha_publicacion', '')),
                "estatus": str(row.get('estatus', 'disponible')).lower().strip(),
                "imagenes": fotos_registradas if fotos_registradas else ["/images/placeholder-galindo.jpg"],
                "contacto": {
                    "whatsapp": str(row.get('whatsapp', '')).split('.')[0].strip(),
                    "mensajeBase": f"Hola, me interesa la propiedad: {titulo}"
                }
            }
            propiedades_json_list.append(prop_data)

        # 2. Guardar JSON final
        os.makedirs(os.path.dirname(RUTA_JSON_ASTRO), exist_ok=True)
        with open(RUTA_JSON_ASTRO, 'w', encoding='utf-8') as f:
            json.dump(propiedades_json_list, f, indent=2, ensure_ascii=False)

        print(f"\n✅ PIPELINE COMPLETADO")
        print(f"🏠 Propiedades procesadas: {len(propiedades_json_list)}")
        print(f"📂 Fotos copiadas a: {RUTA_DESTINO_FOTOS}")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    run_full_pipeline()