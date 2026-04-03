import pandas as pd
import json
import os
import re
import subprocess
from datetime import datetime

def slugify(text):
    """Convierte un título en un slug válido"""
    text = str(text).lower()
    text = re.sub(r'[^\w\s-]', '', text)
    return re.sub(r'[-\s]+', '-', text).strip('-')

def pedir_archivo_mac():
    """Selector nativo de macOS (Finder)"""
    print("📂 Abriendo selector de archivos de macOS...")
    script = 'choose file with prompt "Selecciona el Excel de Propiedades" of type {"xlsx", "xls"}'
    try:
        proc = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
        if proc.returncode == 0:
            ruta_mac = proc.stdout.strip()
            if ":" in ruta_mac:
                ruta_final = "/" + ruta_mac.replace(":", "/").split("/", 1)[1]
                return ruta_final
            return ruta_mac
    except Exception:
        return None
    return None

def procesar_excel():
    file_path = pedir_archivo_mac()
    
    if not file_path or not os.path.exists(file_path):
        print("\n❌ Operación cancelada o archivo no encontrado.")
        return

    try:
        print(f"🚀 Procesando: {file_path}")
        df = pd.read_excel(file_path)
        propiedades_list = []

        for _, row in df.iterrows():
            titulo = str(row.get('titulo', '')).strip()
            if not titulo or titulo == 'nan':
                continue

            # --- MANEJO DE FECHA ---
            fecha_raw = row.get('fecha_publicacion')
            if pd.isna(fecha_raw):
                fecha_str = datetime.now().strftime('%Y-%m-%d')
            elif isinstance(fecha_raw, datetime):
                fecha_str = fecha_raw.strftime('%Y-%m-%d')
            else:
                fecha_str = str(fecha_raw).split(' ')[0]

            # --- MANEJO DE ESTATUS ---
            estatus = str(row.get('estatus', 'disponible')).lower().strip()
            if estatus not in ['disponible', 'vendido', 'rentado']:
                estatus = 'disponible'

            # --- MANEJO DE IMÁGENES (CON PAUSA) ---
            # Guardamos los IDs reales por si acaso, pero usamos placeholder
            imagenes_excel = str(row.get('ids_imagenes', '')).split(',')
            imagenes_limpias = [img.strip() for img in imagenes_excel if img.strip() != 'nan' and img.strip() != '']
            
            # ⬇️ PAUSA ACTIVA: Descomenta la línea de abajo cuando tengas las fotos en /public/images/properties/
            # lista_fotos = [f"/images/properties/{img}" for img in imagenes_limpias] if imagenes_limpias else ["/images/placeholder.jpg"]
            
            # Por ahora usamos Unsplash para que la demo se vea llena:
            lista_fotos = ["https://images.unsplash.com/photo-1568605114967-8130f3a36994"]

            prop = {
                "id": str(row.get('id', 'prop-default')),
                "slug": str(row.get('slug', '')) if str(row.get('slug', '')) != 'nan' else slugify(titulo),
                "titulo": titulo,
                "descripcion": str(row.get('descripcion', 'Sin descripción.')).strip(),
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
                "fechaPublicacion": fecha_str,
                "estatus": estatus,
                "imagenes": lista_fotos,
                "contacto": {
                    "whatsapp": str(row.get('whatsapp', '5212281234567')),
                    "mensajeBase": f"Hola, me interesa la propiedad: {titulo}"
                }
            }
            propiedades_list.append(prop)

        # Ordenar por fecha: las más nuevas primero
        propiedades_list.sort(key=lambda x: x['fechaPublicacion'], reverse=True)

        # Guardar en Astro
        output_path = os.path.join('src', 'data', 'propiedades.json')
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(propiedades_list, f, indent=2, ensure_ascii=False)
        
        print(f"✅ ¡Éxito! Se procesaron {len(propiedades_list)} propiedades.")
        print(f"📅 Ordenadas por fecha de publicación.")

    except Exception as e:
        print(f"❌ Error crítico: {str(e)}")

if __name__ == "__main__":
    procesar_excel()