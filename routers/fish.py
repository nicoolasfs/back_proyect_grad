#Esta es otra forma de realizar la API 

from fastapi import FastAPI, File, UploadFile
from PIL import Image
import io
import torch
import cv2
import numpy as np

app = FastAPI()

# Cargar el modelo de red neuronal convolucional
model = torch.load('modelo.h5', map_location=torch.device('cpu'))
model.eval()

# Definir la ruta de la API para procesar las imágenes
@app.post("/medir_longitud_peces/")
async def medir_longitud_peces(file: UploadFile = File(...)):
    # Leer la imagen en memoria
    contents = await file.read()
    image = Image.open(io.BytesIO(contents)).convert('RGB')

    # Preprocesar la imagen
    image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    image = cv2.resize(image, (224, 224))
    image = image.transpose((2, 0, 1))
    image = image.astype(np.float32) / 255.0
    image = np.expand_dims(image, axis=0)
    
    # Pasar la imagen por la red neuronal convolucional y obtener la longitud del pez
    with torch.no_grad():
        outputs = model(torch.tensor(image))
        length = outputs.item()

    return {"longitud_pez": length}
