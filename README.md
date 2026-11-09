# clean_doc_py: Procesador PDF

## 1. Problemática que soluciona
Al escanear documentos físicos (como el formato "ASESOR ACADEMICO DE BATALLA.pdf"), es común que la luz del escáner traspase el papel, provocando que la información del reverso de la hoja se refleje en el documento digitalizado (efecto de "reverso transparentado"). `clean_doc_py` es una herramienta no invasiva que elimina este ruido visual (píxeles no deseados) sin alterar ni destruir la armonía estética del documento ni la validación legal proporcionada por firmas autógrafas y sellos oficiales. 

## 2. Fundamentos Teóricos de la Problemática
Un escaneo PDF no es más que luz convertida en píxeles. En este entorno, la información documental se agrupa en diferentes niveles de opacidad:
*   **Vectores críticos:** Tienen el negro más profundo (textos, bordes de tablas, sellos oficiales).
*   **Estética frontal:** Niveles de opacidad media (sombreados de celdas, logotipos de fondo).
*   **Información transparentada (Ruido):** Bajos niveles de intensidad de color (alta opacidad respecto a la luz del escáner), generados por la sombra del reverso de la hoja.
*   **Elementos cromáticos:** Firmas manuales (ej. bolígrafo azul) que operan en frecuencias de color distintas a la escala de grises.

El reto teórico es aislar el reverso transparentado y mimetizarlo con el fondo blanco sin tocar la información semántica fundamental.

## 3. Fundamentos Matemáticos de la Solución Elegida
La solución modela la imagen como una matriz bidimensional (un arreglo NumPy) donde cada elemento representa un píxel.

*   **Espacios de Color:** La matriz original $RGB$ se transforma en dos espacios distintos: Grises ($Y$) y Matiz-Saturación-Valor ($HSV$). 
*   **Umbralización (Thresholding):** Se aplica una función matemática de segmentación por partes para agrupar píxeles. Si $p(x, y)$ es la intensidad de un píxel, se define una máscara binaria $M$ mediante un límite de tolerancia $T$:
    $$M(x,y) = \begin{cases} 255 & \text{si } p(x,y) \le T \\ 0 & \text{si } p(x,y) > T \end{cases}$$
*   **Morfología Matemática (Dilatación):** Para proteger firmas y sellos en un radio de $4$ píxeles, se utiliza la operación de dilatación con un kernel estructurante $K$ de dimensiones $9 \times 9$. Esto expande los píxeles de interés matemático para blindarlos antes de la limpieza:
    $$A \oplus K = \{ z \mid (\hat{K})_z \cap A \neq \emptyset \}$$
*   **Álgebra de Máscaras:** Se utilizan compuertas lógicas (Bitwise OR, representadas por el operador $\lor$) para sumar las áreas protegidas.

## 4. Flujo de la Lógica Matemática del Script
El algoritmo sigue una cascada estricta de evaluación:
1.  **Extracción:** Se descompone el PDF en matrices de píxeles por página.
2.  **Aislamiento Cromático (Capa Azul):** Se filtra la matriz $HSV$ buscando rangos angulares de color azul. Se genera la máscara $M_{azul}$ y se dilata en $4$ píxeles.
3.  **Aislamiento de Vectores (Capa Negra):** Se convierte a escala de grises. Se umbraliza desde el negro absoluto ($0$) hasta $120 + \text{tolerancia}$. Se genera la máscara $M_{vectores}$ y se dilata en $4$ píxeles.
4.  **Aislamiento de Sombreados (Capa Gris):** Se umbraliza desde $120$ hasta $180 + \text{tolerancia}$. Se genera la máscara $M_{sombras}$.
5.  **Unión Semántica:** Se calcula la máscara final a conservar: $M_{final} = M_{azul} \lor M_{vectores} \lor M_{sombras}$.
6.  **Sustracción:** Se crea un lienzo blanco ($255$ en toda la matriz). Se copian los píxeles de la imagen original *exclusivamente* en las coordenadas $(x, y)$ donde $M_{final}(x, y) > 0$. Los valores que caen fuera (el reverso de la hoja) se descartan.

## 5. Construcción del Script
El código está construido en lenguaje **Python** utilizando el paradigma de programación funcional y el diseño de interfaces mediante eventos. 
*   **Interfaz Gráfica:** `tkinter` proporciona ventanas nativas ligeras para las interacciones del usuario (carga y guardado).
*   **Procesamiento Vectorial de Imágenes:** `OpenCV` (`cv2`) y `numpy` se encargan de la carga matricial, conversiones de espacio de color, dilatación y operaciones booleanas.
*   **Gestión de Archivos:** `pdf2image` y `Pillow` (PIL) actúan como puentes para decodificar la estructura del archivo PDF a imagen rasterizada y viceversa, empaquetando finalmente las matrices limpias en el archivo PDF de salida.

## 6. Instalación en Entorno Virtual
Es altamente recomendable ejecutar este script dentro de un entorno virtual para aislar las dependencias del sistema.

### Prerrequisitos de Sistema
Para que `pdf2image` funcione, debes tener instalado **Poppler**:
*   *Windows:* Descarga los binarios de Poppler y agrega la carpeta `bin` a tu variable de entorno PATH.
*   *macOS:* Ejecuta `brew install poppler`.
*   *Linux (Debian/Ubuntu):* Ejecuta `sudo apt-get install poppler-utils`.

### Pasos de Instalación
1.  Abre tu terminal o símbolo del sistema.
2.  Crea el entorno virtual:
    ```bash
    python -m venv pdf_env
    ```
3.  Activa el entorno virtual:
    *   *Windows:* `pdf_env\Scripts\activate`
    *   *Linux/macOS:* `source pdf_env/bin/activate`
4.  Instala las dependencias necesarias:
    ```bash
    pip install opencv-python numpy pdf2image Pillow
    ```

## 7. Breve Manual de Uso
1.  Con el entorno virtual activado, ejecuta el script desde tu terminal:
    ```bash
    python clean_doc.py
    ```
2.  Aparecerá una pequeña ventana titulada "Procesamiento Documental con Tolerancia Cromática".
3.  Haz clic en el botón **"Cargar PDF y Procesar"**.
4.  Se abrirá un explorador de archivos; selecciona tu documento escaneado (ej. `ASESOR ACADEMICO DE BATALLA.pdf`).
5.  Inmediatamente, se abrirá otra ventana pidiéndote que elijas el nombre y la ubicación donde deseas **guardar** el PDF limpio.
6.  El script procesará matemáticamente los píxeles de cada página y, al finalizar, te mostrará un cuadro de diálogo confirmando el éxito de la operación.