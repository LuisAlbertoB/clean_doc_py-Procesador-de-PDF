import tkinter as tk
from tkinter import filedialog, messagebox
import cv2
import numpy as np
from pdf2image import convert_from_path
from PIL import Image

def procesar_imagen_avanzada(imagen_cv, tolerancia=15):
    # 1. Análisis Cromático (Espacio HSV) para firmas en bolígrafo azul
    # El espacio HSV aísla el color real (Matiz) de las sombras del escaneo
    hsv = cv2.cvtColor(imagen_cv, cv2.COLOR_BGR2HSV)
    
    # Rango de tolerancia para agrupar tonos azules (matices del 100 al 140)
    # Saturación y Brillo inician en 40 para omitir grises azulados del ruido
    azul_bajo = np.array([100, 40, 40])
    azul_alto = np.array([140, 255, 255])
    mascara_azul = cv2.inRange(hsv, azul_bajo, azul_alto)
    
    # 2. Análisis de Intensidad (Escala de grises) para información documental
    gris = cv2.cvtColor(imagen_cv, cv2.COLOR_BGR2GRAY)
    
    # Aplicación de tolerancia matemática a los límites de opacidad
    limite_nivel1 = min(120 + tolerancia, 255) # Vectores negros
    limite_nivel2 = min(180 + tolerancia, 255) # Sombreado estético (celdas)
    
    # Agrupar píxeles según los nuevos límites flexibilizados
    _, mascara_vectores = cv2.threshold(gris, limite_nivel1, 255, cv2.THRESH_BINARY_INV)
    _, mascara_sombreado = cv2.threshold(gris, limite_nivel2, 255, cv2.THRESH_BINARY_INV)
    
    # 3. Aislamiento y protección (Radio de 4 píxeles)
    kernel = np.ones((9, 9), np.uint8)
    
    # Expandir y proteger tanto los vectores negros como la tinta azul
    mascara_azul_protegida = cv2.dilate(mascara_azul, kernel, iterations=1)
    mascara_vectores_protegida = cv2.dilate(mascara_vectores, kernel, iterations=1)
    
    # 4. Consolidación de la estructura semántica
    # Unir firmas azules protegidas, vectores negros y sombreados
    mascara_info_vital = cv2.bitwise_or(mascara_azul_protegida, mascara_vectores_protegida)
    mascara_conservar = cv2.bitwise_or(mascara_info_vital, mascara_sombreado)
    
    # 5. Mimetización del fondo (eliminación del reverso transparentado)
    # Se genera un lienzo blanco y se pegan estrictamente los píxeles agrupados en la máscara
    resultado = np.ones_like(imagen_cv) * 255
    indices_conservar = mascara_conservar > 0
    resultado[indices_conservar] = imagen_cv[indices_conservar]
    
    return resultado

def cargar_y_procesar():
    ruta_entrada = filedialog.askopenfilename(
        title="Cargar documento PDF",
        filetypes=[("Archivos PDF", "*.pdf")]
    )
    
    if not ruta_entrada:
        return
        
    ruta_salida = filedialog.asksaveasfilename(
        title="Guardar PDF procesado como",
        defaultextension=".pdf",
        filetypes=[("Archivos PDF", "*.pdf")]
    )
    
    if not ruta_salida:
        return
        
    try:
        imagenes_pil = convert_from_path(ruta_entrada)
        imagenes_procesadas_pil = []
        
        # Variable de tolerancia general. Un valor de 15 a 25 absorbe bien 
        # las variaciones de opacidad generadas por la lámpara del escáner.
        nivel_tolerancia = 20 
        
        for img_pil in imagenes_pil:
            img_cv = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
            img_limpia_cv = procesar_imagen_avanzada(img_cv, tolerancia=nivel_tolerancia)
            img_limpia_pil = Image.fromarray(cv2.cvtColor(img_limpia_cv, cv2.COLOR_BGR2RGB))
            imagenes_procesadas_pil.append(img_limpia_pil)
            
        if imagenes_procesadas_pil:
            imagenes_procesadas_pil[0].save(
                ruta_salida, 
                save_all=True, 
                append_images=imagenes_procesadas_pil[1:]
            )
            
        messagebox.showinfo("Éxito", "Documento procesado preservando tintas de color.")
        
    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error crítico:\n{e}")

# Interfaz gráfica Tkinter
root = tk.Tk()
root.title("Procesamiento Documental con Tolerancia Cromática")
root.geometry("420x200")
root.eval('tk::PlaceWindow . center')

etiqueta = tk.Label(root, text="Eliminador de Transparencias (Soporte Tinta Azul)", font=("Arial", 11, "bold"))
etiqueta.pack(pady=20)

boton_procesar = tk.Button(root, text="Cargar PDF y Procesar", command=cargar_y_procesar, padx=20, pady=10)
boton_procesar.pack(pady=10)

root.mainloop()