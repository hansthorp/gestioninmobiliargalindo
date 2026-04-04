import os
import pandas as pd
import subprocess
import re

def pedir_ruta_mac(tipo="archivo"):
    """Llama al Finder de macOS para seleccionar archivo o carpeta"""
    if tipo == "archivo":
        print("📂 Selecciona el Excel...")
        script = 'choose file with prompt "Selecciona el Excel de Inventario" of type {"xlsx", "xls"}'
    else:
        print("📂 Selecciona la carpeta de Fotos...")
        script = 'choose folder with prompt "Selecciona la carpeta raíz de las fotos (donde están C-001, etc.)"'

    try:
        proc = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
        if proc.returncode == 0:
            # Limpiar la ruta que devuelve AppleScript
            ruta_mac = proc.stdout.strip()
            # Convertir formato 'alias Macintosh HD:Users:...' a '/Users/...'
            if ":" in ruta_mac:
                partes = ruta_mac.replace(":", "/").split("/", 1)
                ruta_final = "/" + partes[1] if len(partes) > 1 else ruta_mac
                # Quitar la palabra 'alias ' si aparece al inicio
                ruta_final = ruta_final.replace("alias ", "")
                return ruta_final.strip()
        return None
    except Exception as e:
        print(f"❌ Error en selector: {e}")
        return None

def run_relocation():
    # 1. Seleccionar Archivo
    path_excel = pedir_ruta_mac("archivo")
    if not path_excel: return

    # 2. Seleccionar Carpeta
    path_fotos_raiz = pedir_ruta_mac("carpeta")
    if not path_fotos_raiz: return

    print(f"🚀 Iniciando reubicación...\nExcel: {path_excel}\nFotos: {path_fotos_raiz}")

    try:
        df = pd.read_excel(path_excel)
        
        # Limpieza de WhatsApp (Solo el primer número)
        if 'whatsapp' in df.columns:
            df['whatsapp'] = df['whatsapp'].apply(
                lambda x: str(x).split('/')[0].strip() if pd.notnull(x) else x
            )

        nombres_finales = []
        conteo_carpetas = 0

        for index, row in df.iterrows():
            prop_id = str(row['id']).strip()
            # Buscamos la carpeta con el ID (ej: C-001)
            ruta_carpeta_prop = os.path.join(path_fotos_raiz, prop_id)
            fotos_en_propiedad = []

            if os.path.exists(ruta_carpeta_prop) and os.path.isdir(ruta_carpeta_prop):
                archivos = [f for f in os.listdir(ruta_carpeta_prop) 
                           if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))]
                archivos.sort()

                for i, archivo_orig in enumerate(archivos, start=1):
                    ext = os.path.splitext(archivo_orig)[1].lower()
                    nuevo_nombre = f"{prop_id}_{i}{ext}"
                    
                    old_p = os.path.join(ruta_carpeta_prop, archivo_orig)
                    new_p = os.path.join(ruta_carpeta_prop, nuevo_nombre)
                    
                    if old_p != new_p:
                        os.rename(old_p, new_p)
                    
                    fotos_en_propiedad.append(nuevo_nombre)
                
                conteo_carpetas += 1
            
            nombres_finales.append(",".join(fotos_en_propiedad))

        # 3. Guardar resultados
        df['ids_imagenes'] = nombres_finales
        output_path = path_excel.replace(".xlsx", "_READY.xlsx")
        df.to_excel(output_path, index=False)

        print(f"\n✅ ¡Proceso terminado!")
        print(f"📂 Carpetas procesadas: {conteo_carpetas}")
        print(f"📝 Excel generado: {os.path.basename(output_path)}")

    except Exception as e:
        print(f"❌ Error crítico: {e}")

if __name__ == "__main__":
    run_relocation()