import json
from pathlib import Path

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.applications import MobileNetV2


# ============================================================
# CONFIGURAÇÕES
# ============================================================

DATASET_DIR = Path("dataset") 

TRAIN_DIR = DATASET_DIR / "train"
VAL_DIR = DATASET_DIR / "validation"

MODEL_DIR = Path("model")
MODEL_DIR.mkdir(exist_ok=True)

IMAGE_SIZE = (224, 224)
BATCH_SIZE = 32
EPOCHS = 15

SEED = 42


# ============================================================
# DATASETS
# ============================================================

print("=" * 60)
print("CARREGANDO DATASET")
print("=" * 60)

train_dataset = tf.keras.utils.image_dataset_from_directory(
    TRAIN_DIR,
    image_size=IMAGE_SIZE,
    batch_size=BATCH_SIZE,
    shuffle=True,
    seed=SEED
)

validation_dataset = tf.keras.utils.image_dataset_from_directory(
    VAL_DIR,
    image_size=IMAGE_SIZE,
    batch_size=BATCH_SIZE,
    shuffle=False
)

class_names = train_dataset.class_names

print(f"\nClasses encontradas: {len(class_names)}")

if len(class_names) != 151:
    raise ValueError(
        f"Esperadas 151 classes, mas foram encontradas {len(class_names)}."
    )


# ============================================================
# SALVAR NOMES DAS CLASSES
# ============================================================

with open(MODEL_DIR / "class_names.json", "w", encoding="utf-8") as arquivo:
    json.dump(class_names, arquivo, ensure_ascii=False, indent=4)

print("✓ class_names.json salvo")


# ============================================================
# PERFORMANCE DO DATASET
# ============================================================

AUTOTUNE = tf.data.AUTOTUNE

train_dataset = train_dataset.prefetch(AUTOTUNE)
validation_dataset = validation_dataset.prefetch(AUTOTUNE)


# ============================================================
# DATA AUGMENTATION
# ============================================================

data_augmentation = keras.Sequential([
    layers.RandomFlip("horizontal"),
    layers.RandomRotation(0.08),
    layers.RandomZoom(0.15),
    layers.RandomContrast(0.1),
])


# ============================================================
# MODELO BASE
# ============================================================

print("\n" + "=" * 60)
print("CARREGANDO MOBILENETV2")
print("=" * 60)

base_model = MobileNetV2(
    input_shape=(224, 224, 3),
    include_top=False,
    weights="imagenet"
)

# Congelar MobileNetV2 inicialmente
base_model.trainable = False


# ============================================================
# MODELO COMPLETO
# ============================================================

inputs = keras.Input(shape=(224, 224, 3))

x = data_augmentation(inputs)

x = keras.applications.mobilenet_v2.preprocess_input(x)

x = base_model(x, training=False)

x = layers.GlobalAveragePooling2D()(x)

x = layers.Dropout(0.3)(x)

outputs = layers.Dense(
    151,
    activation="softmax"
)(x)

model = keras.Model(inputs, outputs)


# ============================================================
# COMPILAÇÃO
# ============================================================

model.compile(
    optimizer=keras.optimizers.Adam(
        learning_rate=0.001
    ),
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"]
)

model.summary()


# ============================================================
# CALLBACKS
# ============================================================

checkpoint = keras.callbacks.ModelCheckpoint(
    MODEL_DIR / "pokemon_model.keras",
    monitor="val_accuracy",
    save_best_only=True,
    verbose=1
)

early_stopping = keras.callbacks.EarlyStopping(
    monitor="val_accuracy",
    patience=4,
    restore_best_weights=True,
    verbose=1
)


# ============================================================
# TREINAMENTO
# ============================================================

print("\n" + "=" * 60)
print("INICIANDO TREINAMENTO")
print("=" * 60)

history = model.fit(
    train_dataset,
    validation_data=validation_dataset,
    epochs=EPOCHS,
    callbacks=[
        checkpoint,
        early_stopping
    ]
)


# ============================================================
# RESULTADO
# ============================================================

print("\n" + "=" * 60)
print("TREINAMENTO FINALIZADO")
print("=" * 60)

print(
    f"Melhor modelo salvo em: "
    f"{MODEL_DIR / 'pokemon_model.keras'}"
)

print("Classes salvas em:")
print(MODEL_DIR / "class_names.json")