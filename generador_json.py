import pandas as pd
import json
import os
import re
import subprocess # Para hablar con el selector de archivos de Mac

def slugify(text):
    """Convierte un título en un slug válido"""
    text = str(text).lower()
    # Limpiamos caracteres especiales para evitar errores de ruteo
    text = re.sub(r'[^\w\s-]', '', text)
    return re.sub(r'[-\s]+', '-', text).strip('-')

def pedir_archivo_mac():
    """Llama al Finder de Mac para seleccionar el Excel de forma nativa"""
    print("📂 Abriendo selector de archivos de macOS...")
    script = 'choose file with prompt "Selecciona el Excel de Propiedades" of type {"xlsx", "xls"}'
    try:
        # Ejecutamos un comando de AppleScript para abrir el Finder
        proc = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
        if proc.returncode == 0:
            # Limpiamos la ruta que devuelve Mac (formato alias:posix)
            ruta_mac = proc.stdout.strip()
            # Convertimos formato Mac a ruta de sistema usable por Python
            if ":" in ruta_mac:
                ruta_final = "/" + ruta_mac.replace(":", "/").split("/", 1)[1]
                return ruta_final
            return ruta_mac
    except Exception:
        return None
    return None

def procesar_excel():
    # 1. USAMOS EL SELECTOR NATIVO DE MAC (Finder)
    file_path = pedir_archivo_mac()
    
    if not file_path or not os.path.exists(file_path):
        print("\n❌ No se seleccionó ningún archivo o el archivo no existe.")
        return

    try:
        print(f"🚀 Procesando archivo: {file_path}")
        df = pd.read_excel(file_path)
        
        propiedades_list = []

        for _, row in df.iterrows():
            titulo = str(row.get('titulo', '')).strip()
            # Ignorar filas vacías o sin título
            if not titulo or titulo == 'nan':
                continue

            # Manejo del Slug (Si no existe, lo creamos del título)
            slug = str(row.get('slug', '')).strip()
            if not slug or slug == 'nan':
                slug = slugify(titulo)

            # Construcción del objeto Propiedad (Estructura para Astro)
            prop = {
                "id": str(row.get('id', 'prop-default')),
                "slug": slug,
                "titulo": titulo,
                "descripcion": str(row.get('descripcion', 'Sin descripción disponible.')).strip(),
                "operacion": str(row.get('operacion', 'venta')).lower(),
                "tipo": str(row.get('tipo', 'casa')).lower(),
                "precio": int(row.get('precio', 0)),
                "moneda": "MXN",
                "zona": str(row.get('zona', 'Xalapa')).strip(),
                "ciudad": str(row.get('ciudad', 'Veracruz')).strip(),
                "m2Terreno": int(row.get('m2Terreno', 0)),
                "m2Construccion": int(row.get('m2Construccion', 0)),
                "recamaras": int(row.get('recamaras', 0)),
                "banos": int(row.get('banos', 0)),
                "estacionamientos": int(row.get('estacionamientos', 0)),
                
                # --- PAUSA DE IMÁGENES CONFIRMADA ---
                # Usamos una imagen genérica para pruebas para no buscar fotos reales
                "imagenes": ["https://images.unsplash.com/photo-1568605114967-8130f3a36994"], 
                # ------------------------------------
                
                "contacto": {
                    "whatsapp": str(row.get('whatsapp', '5212281234567')),
                    "mensajeBase": f"Hola, me interesa la propiedad: {titulo}"
                }
            }
            propiedades_list.append(prop)

        # Ruta de salida: src/data/propiedades.json
        output_dir = os.path.join('src', 'data')
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, 'propiedades.json')
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(propiedades_list, f, indent=2, ensure_ascii=False)
        
        print(f"✅ ¡Listo! Se procesaron {len(propiedades_list)} propiedades.")
        print(f"📂 Archivo actualizado: {output_path}\n")

    except Exception as e:
        print(f"❌ Error de procesamiento: {str(e)}")

if __name__ == "__main__":
    procesar_excel()