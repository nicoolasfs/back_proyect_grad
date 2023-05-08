# import cv2
# import os

# # directorio donde se encuentran las imágenes de los peces
# dir_path = 'C:/Users/nfons/Documents/Proyecto_grado/API/Backend/Dataset/'

# # para cada imagen en el directorio
# for file_name in os.listdir(dir_path):
    
#     # lee la imagen
#     img_path = os.path.join(dir_path, file_name)
#     img = cv2.imread(img_path)
    
#     # convierte la imagen a escala de grises
#     gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
#     # aplica un umbral para segmentar el pez
#     ret, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    
#     # encuentra los contornos del pez
#     contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
#     # obtiene el contorno más grande (el pez)
#     fish_contour = max(contours, key=cv2.contourArea)
    
#     # calcula la longitud del pez
#     length = cv2.arcLength(fish_contour, True)
    
#     # guarda la longitud como un valor de metadato en la imagen
#     img_metadata = {'length': length}
    
#     # guarda la imagen con la etiqueta de longitud
#     cv2.imwrite(img_path, img, [int(cv2.IMWRITE_JPEG_QUALITY), 100])
    
#     # Usar otra función para guardar la imagen con la etiqueta de longitud
    
#     print(f'Longitud del pez en {file_name} es de: {length} px')

import cv2
import os
import piexif
from PIL import Image

# Directorio donde se encuentran las imágenes
dir_path = "C:/Users/nfons/Documents/Proyecto_grado/API/Backend/Dataset/"

# Leer cada imagen en el directorio y medir la longitud del pez
for file in os.listdir(dir_path):
    # Leer la imagen
    img_path = os.path.join(dir_path, file)
    img = cv2.imread(img_path)

    # Convertir la imagen a escala de grises y aplicar un filtro de mediana para reducir el ruido
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, 5)

    # Detectar los bordes de los objetos en la imagen utilizando el algoritmo Canny
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)

    # Encontrar los contornos de los objetos en la imagen
    contours, hierarchy = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # Encontrar el contorno más grande en la imagen
    biggest_contour = max(contours, key=cv2.contourArea)

    # Medir la longitud del contorno más grande en la imagen
    length = cv2.arcLength(biggest_contour, True)

    # Agregar la etiqueta de longitud como un campo personalizado en los datos EXIF de la imagen utilizando piexif
    exif_data = piexif.load(img_path)
    exif_data["Exif"][piexif.ExifIFD.UserComment] = str.encode(f"Length: {length}", 'ascii')

    # Guardar la imagen con los nuevos datos EXIF
    exif_bytes = piexif.dump(exif_data)
    with open(img_path, "rb") as f:
        img_data = f.read()
    with Image.open(img_path) as img_pil:
        img_pil.save(img_path, "JPEG", quality=95, exif=exif_bytes)
        
    # Imprimir la longitud del pez
    print(f"Longitud del pez en {file} es de: {length} px")
