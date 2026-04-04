import os
import pandas as pd
import subprocess
import shutil
import json
import re
from datetime import datetime

# --- CONFIGURACIÓN DE RUTAS ---
# ✅ CAMBIO CLAVE: Dejamos BASE_URL vacío para que las rutas empiecen con /images/
BASE_URL = "" 
RUTA_DESTINO_FOTOS = "./public/images/properties/"
RUTA_JSON_ASTRO = "./src/data/propiedades.json"

def slugify(text):
    text = str(text).lower()
    # Limpieza de acentos y caracteres especiales para URLs limpias
    text = re.sub(r'[áéíóúüñ]', lambda m: {'á':'a','é':'e','í':'i','ó':'o','ú':'u','ü':'u','ñ':'n'}[m.group()], text)
    text = re.sub(r'[^\w\s-]', '', text)
    return re.sub(r'[-\s]+', '-', text).strip('-')

def pedir_ruta_mac(tipo="archivo"):
    script = 'choose file' if tipo == "archivo" else 'choose folder'
    prompt = 'Selecciona el Excel' if tipo == "archivo" else 'Selecciona carpeta de fotos originales'
    cmd = f'osascript -e \'{script} with prompt "{prompt}"\''
    try:
        proc = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if proc.returncode == 0:
            # Limpieza de la ruta que devuelve AppleScript
            ruta = proc.stdout.strip().replace("alias ", "").replace(":", "/")
            # Ajuste para convertir ruta Mac a ruta POSIX
            if not ruta.startswith("/"):
                parts = ruta.split("/")
                ruta = "/" + "/".join(parts[1:])
            return ruta
        return None
    except: return None

def run_full_pipeline():
    path_excel = pedir_ruta_mac("archivo")
    path_fotos_origen = pedir_ruta_mac("carpeta")
    
    if not path_excel or not path_fotos_origen:
        print("❌ Operación cancelada por el usuario.")
        return

    print("🧹 Iniciando limpieza profunda...")
    
    # Borrar JSON anterior
    if os.path.exists(RUTA_JSON_ASTRO):
        os.remove(RUTA_JSON_ASTRO)

    # Borrar y recrear carpeta de fotos
    if os.path.exists(RUTA_DESTINO_FOTOS):
        shutil.rmtree(RUTA_DESTINO_FOTOS)
    os.makedirs(RUTA_DESTINO_FOTOS, exist_ok=True)

    try:
        df = pd.read_excel(path_excel)
        propiedades_json_list = []
        
        print(f"🚀 Procesando {len(df)} filas...")

        for index, row in df.iterrows():
            # Limpieza de ID (Carpeta de fotos)
            prop_id = str(row.get('id', '')).strip()
            titulo = str(row.get('titulo', '')).strip()
            
            if not prop_id or prop_id == 'nan' or not titulo:
                continue

            # --- PROCESAMIENTO DE FOTOS ---
            # Normalizamos nombres de carpetas para evitar errores de Mayúsculas/Minúsculas
            folder_origen = None
            for d in os.listdir(path_fotos_origen):
                if d.lower().strip() == prop_id.lower().strip():
                    folder_origen = os.path.join(path_fotos_origen, d)
                    break

            fotos_registradas = []
            if folder_origen and os.path.isdir(folder_origen):
                folder_destino_web = os.path.join(RUTA_DESTINO_FOTOS, prop_id)
                os.makedirs(folder_destino_web, exist_ok=True)
                
                archivos = [f for f in os.listdir(folder_origen) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))]
                archivos.sort()

                for i, archivo_orig in enumerate(archivos, start=1):
                    ext = os.path.splitext(archivo_orig)[1].lower()
                    nuevo_nombre = f"{prop_id}_{i}{ext}"
                    shutil.copy2(os.path.join(folder_origen, archivo_orig), os.path.join(folder_destino_web, nuevo_nombre))
                    
                    # ✅ RUTA LIMPIA PARA ASTRO: /images/properties/ID/foto.jpg
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

        # Guardar JSON
        os.makedirs(os.path.dirname(RUTA_JSON_ASTRO), exist_ok=True)
        with open(RUTA_JSON_ASTRO, 'w', encoding='utf-8') as f:
            json.dump(propiedades_json_list, f, indent=2, ensure_ascii=False)

        print(f"\n✅ PROCESO COMPLETADO")
        print(f"🏠 Propiedades en catálogo: {len(propiedades_json_list)}")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    run_full_pipeline()