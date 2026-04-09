import os
import pandas as pd
from tkinter import filedialog, Tk, messagebox

def seleccionar_ruta(titulo, es_archivo=True):
    """Abre una ventana nativa de Windows para seleccionar archivos o carpetas"""
    root = Tk()
    root.withdraw()  # Oculta la ventana pequeña de Tkinter
    root.attributes("-topmost", True)  # Asegura que la ventana aparezca al frente

    if es_archivo:
        ruta = filedialog.askopenfilename(
            title=titulo,
            filetypes=[("Excel files", "*.xlsx *.xls")]
        )
    else:
        ruta = filedialog.askdirectory(title=titulo)
    
    root.destroy()
    return ruta if ruta else None

def run_relocation_windows():
    print("--- 🏠 Gestor de Inventario Inmobiliario (Windows Version) ---")
    
    # 1. Selección de insumos
    path_excel = seleccionar_ruta("Selecciona el archivo Excel de Inventario", es_archivo=True)
    if not path_excel: 
        print("❌ No se seleccionó ningún Excel."); return

    path_fotos_raiz = seleccionar_ruta("Selecciona la carpeta raíz de las fotos", es_archivo=False)
    if not path_fotos_raiz: 
        print("❌ No se seleccionó la carpeta de fotos."); return

    print(f"\n🚀 Procesando...\n📍 Excel: {path_excel}\n📸 Carpeta: {path_fotos_raiz}\n")

    try:
        # Cargar datos
        df = pd.read_excel(path_excel)
        
        # Limpieza básica de la columna 'whatsapp' si existe
        if 'whatsapp' in df.columns:
            df['whatsapp'] = df['whatsapp'].apply(
                lambda x: str(x).split('/')[0].strip() if pd.notnull(x) and x != "" else x
            )

        nombres_finales_columna = []
        carpetas_encontradas = 0

        for _, row in df.iterrows():
            # Obtener ID (ej: C-001) y limpiar espacios
            prop_id = str(row['id']).strip()
            ruta_carpeta_prop = os.path.join(path_fotos_raiz, prop_id)
            fotos_renombradas = []

            if os.path.exists(ruta_carpeta_prop) and os.path.isdir(ruta_carpeta_prop):
                # Filtrar solo imágenes reales
                archivos = [f for f in os.listdir(ruta_carpeta_prop) 
                           if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))]
                
                # Ordenar para que el 1, 2, 3 sea consistente
                archivos.sort()

                for i, nombre_original in enumerate(archivos, start=1):
                    ext = os.path.splitext(nombre_original)[1].lower()
                    nuevo_nombre = f"{prop_id}_{i}{ext}"
                    
                    ruta_vieja = os.path.join(ruta_carpeta_prop, nombre_original)
                    ruta_nueva = os.path.join(ruta_carpeta_prop, nuevo_nombre)
                    
                    # Renombrar solo si el nombre es diferente
                    if ruta_vieja != ruta_nueva:
                        try:
                            os.rename(ruta_vieja, ruta_nueva)
                        except OSError as e:
                            print(f"⚠️ No se pudo renombrar {nombre_original}: {e}")
                    
                    fotos_renombradas.append(nuevo_nombre)
                
                carpetas_encontradas += 1
            
            # Guardar la lista de fotos separadas por coma para el JSON posterior
            nombres_finales_columna.append(",".join(fotos_renombradas))

        # 2. Guardar el nuevo Excel con los IDs de las fotos vinculados
        df['ids_imagenes'] = nombres_finales_columna
        output_path = path_excel.replace(".xlsx", "_PROCESADO.xlsx")
        df.to_excel(output_path, index=False)

        # Mensaje final
        print(f"✅ ¡Éxito!")
        print(f"📂 Carpetas de propiedades vinculadas: {carpetas_encontradas}")
        print(f"📝 Nuevo archivo creado: {os.path.basename(output_path)}")
        
        # Alerta visual en Windows
        final_root = Tk()
        final_root.withdraw()
        messagebox.showinfo("Proceso Completado", f"Se procesaron {carpetas_encontradas} carpetas.\nArchivo guardado como: {os.path.basename(output_path)}")
        final_root.destroy()

    except Exception as e:
        print(f"❌ Error crítico durante la ejecución: {e}")

if __name__ == "__main__":
    run_relocation_windows()