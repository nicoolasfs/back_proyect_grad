#Este archivo se creará el modelo de la red neuronal convolucional y se guardará en el archivo modelo.h5.

import tensorflow as tf
from tensorflow import keras
from keras import layers
from keras.models import Sequential

model = Sequential([
    layers.Conv2D(32, (3,3), activation='relu', input_shape=(224,224,3)),
    layers.MaxPooling2D((2,2)),
    layers.Conv2D(64, (3,3), activation='relu'),
    layers.MaxPooling2D((2,2)),
    layers.Conv2D(128, (3,3), activation='relu'),
    layers.MaxPooling2D((2,2)),
    layers.Flatten(),
    layers.Dense(128, activation='relu'),
    layers.Dense(1, activation='sigmoid')
])

model.compile(loss='binary_crossentropy',
              optimizer='adam',
              metrics=['accuracy'])

train_data = keras.preprocessing.image_dataset_from_directory(
    'train_dir', label_mode='binary', image_size=(224,224), batch_size=32
)

val_data = keras.preprocessing.image_dataset_from_directory(
    'val_dir', label_mode='binary', image_size=(224,224), batch_size=32
)

model.fit(train_data, validation_data=val_data, epochs=10)

model.save('model.h5')
