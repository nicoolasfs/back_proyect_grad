# from PIL import Image

# # Cargar la imagen
# img = Image.open('C:/Users/nfons/Documents/Proyecto_grado/API/Backend/Dataset/prueba.jpg')

# # Leer el valor de la etiqueta de metadatos
# length = img.info.get('length')

# # Imprimir el valor de la etiqueta de metadatos
# print('La longitud del pez en la imagen es:', length)
import exifread
import os

# Directorio donde se encuentran las imágenes
dir_path = "C:/Users/nfons/Documents/Proyecto_grado/API/Backend/Dataset/"

# Leer cada imagen en el directorio y verificar si la etiqueta de longitud se ha guardado correctamente
for file in os.listdir(dir_path):
    # Leer la imagen
    img_path = os.path.join(dir_path, file)

    # Leer los metadatos de la imagen
    with open(img_path, 'rb') as f:
        tags = exifread.process_file(f)

    # Verificar si la etiqueta de longitud se ha guardado correctamente
    if 'Image Tag 0x8769' in tags:
        length = tags['Image Tag 0x8769'].values
        print("La longitud de la imagen {} es {}".format(file, length))
    else:
        print("La imagen {} no tiene etiqueta de longitud".format(file))
