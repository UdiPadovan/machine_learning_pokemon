import json
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

# =========================
# CONFIGURAÇÕES
# =========================

IMG_SIZE = (224, 224)
BATCH_SIZE = 32
NUM_CLASSES = 151

MODEL_PATH = "model/pokemon_model.keras"
OUTPUT_PATH = "model/pokemon_model_v2.keras"

TRAIN_DIR = "dataset/train"
VAL_DIR = "dataset/validation"

# =========================
# DATASETS
# =========================

train_ds = keras.utils.image_dataset_from_directory(
    TRAIN_DIR,
    image_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    shuffle=True
)

val_ds = keras.utils.image_dataset_from_directory(
    VAL_DIR,
    image_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    shuffle=False
)

# =========================
# CARREGAR MODELO
# =========================

model = keras.models.load_model(MODEL_PATH)

print("Modelo carregado.")

# =========================
# ENCONTRAR MOBILENETV2
# =========================

base_model = None

for layer in model.layers:
    if isinstance(layer, keras.Model) and "mobilenetv2" in layer.name.lower():
        base_model = layer
        break

if base_model is None:
    raise ValueError("MobileNetV2 não encontrada dentro do modelo.")

print("Base encontrada:", base_model.name)

# =========================
# DESCONGELAR PARTE DA BASE
# =========================

base_model.trainable = True

# Congela quase tudo e libera apenas
# as últimas 30 camadas

for layer in base_model.layers[:-30]:
    layer.trainable = False

for layer in base_model.layers[-30:]:
    layer.trainable = True

print("Camadas treináveis:")

for layer in base_model.layers:
    if layer.trainable:
        print(layer.name)

# =========================
# COMPILE
# =========================

model.compile(
    optimizer=keras.optimizers.Adam(
        learning_rate=1e-5
    ),
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"]
)

# =========================
# CALLBACKS
# =========================

checkpoint = keras.callbacks.ModelCheckpoint(
    OUTPUT_PATH,
    monitor="val_accuracy",
    save_best_only=True,
    verbose=1
)

early_stop = keras.callbacks.EarlyStopping(
    monitor="val_accuracy",
    patience=4,
    restore_best_weights=True,
    verbose=1
)

# =========================
# TREINAMENTO
# =========================

history = model.fit(
    train_ds,
    validation_data=val_ds,
    epochs=10,
    callbacks=[
        checkpoint,
        early_stop
    ]
)

print("\nFine-tuning finalizado!")
print("Modelo salvo em:", OUTPUT_PATH)