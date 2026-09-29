import json
from pathlib import Path

import numpy as np
import tensorflow as tf
from tensorflow import keras
from sklearn.metrics import classification_report, confusion_matrix


# ============================================================
# CONFIGURAÇÕES
# ============================================================

TEST_DIR = Path("dataset/test")
MODEL_PATH = Path("model/pokemon_model_v2.keras")
CLASS_NAMES_PATH = Path("model/class_names.json")

IMAGE_SIZE = (224, 224)
BATCH_SIZE = 32


# ============================================================
# CARREGAR MODELO
# ============================================================

print("=" * 60)
print("CARREGANDO MODELO")
print("=" * 60)

model = keras.models.load_model(MODEL_PATH)

print("✓ Modelo carregado")


# ============================================================
# CARREGAR NOMES DAS CLASSES
# ============================================================

with open(CLASS_NAMES_PATH, "r", encoding="utf-8") as arquivo:
    class_names = json.load(arquivo)

print(f"✓ {len(class_names)} classes carregadas")


# ============================================================
# CARREGAR DATASET DE TESTE
# ============================================================

print("\n" + "=" * 60)
print("CARREGANDO DATASET DE TESTE")
print("=" * 60)

test_dataset = tf.keras.utils.image_dataset_from_directory(
    TEST_DIR,
    image_size=IMAGE_SIZE,
    batch_size=BATCH_SIZE,
    shuffle=False
)

print(f"✓ Imagens de teste carregadas")


# ============================================================
# AVALIAÇÃO
# ============================================================

print("\n" + "=" * 60)
print("AVALIANDO MODELO")
print("=" * 60)

loss, accuracy = model.evaluate(test_dataset, verbose=1)

print("\n" + "=" * 60)
print("RESULTADO FINAL")
print("=" * 60)

print(f"Loss:      {loss:.4f}")
print(f"Accuracy:  {accuracy:.4%}")
print("=" * 60)


# ============================================================
# PREVISÕES
# ============================================================

print("\nGerando previsões...")

predictions = model.predict(test_dataset, verbose=1)

predicted_classes = np.argmax(predictions, axis=1)

true_classes = np.concatenate([
    labels.numpy()
    for images, labels in test_dataset
])


# ============================================================
# RELATÓRIO POR POKÉMON
# ============================================================

print("\n" + "=" * 60)
print("RELATÓRIO POR POKÉMON")
print("=" * 60)

report = classification_report(
    true_classes,
    predicted_classes,
    target_names=class_names,
    digits=3,
    zero_division=0
)

print(report)


# ============================================================
# MATRIZ DE CONFUSÃO
# ============================================================

cm = confusion_matrix(
    true_classes,
    predicted_classes
)

np.save(
    "model/confusion_matrix.npy",
    cm
)

print("✓ Matriz de confusão salva em:")
print("  model/confusion_matrix.npy")


# ============================================================
# TOP 10 POKÉMON MAIS CONFUNDIDOS
# ============================================================

print("\n" + "=" * 60)
print("PRINCIPAIS CONFUSÕES")
print("=" * 60)

confusions = []

for real in range(len(class_names)):
    for predicted in range(len(class_names)):

        if real != predicted and cm[real][predicted] > 0:

            confusions.append(
                (
                    cm[real][predicted],
                    class_names[real],
                    class_names[predicted]
                )
            )

confusions.sort(reverse=True)

for quantidade, real, predicted in confusions[:20]:

    print(
        f"{real} → {predicted}: "
        f"{quantidade} vezes"
    )


# ============================================================
# TOP 5 PIORES CLASSES
# ============================================================

print("\n" + "=" * 60)
print("POKÉMON COM MENOR DESEMPENHO")
print("=" * 60)

class_accuracies = []

for i, nome in enumerate(class_names):

    total = cm[i].sum()

    if total > 0:
        acertou = cm[i][i]
        acc = acertou / total

        class_accuracies.append(
            (acc, nome, acertou, total)
        )

class_accuracies.sort()

for acc, nome, acertou, total in class_accuracies[:10]:

    print(
        f"{nome}: "
        f"{acc:.1%} "
        f"({acertou}/{total})"
    )


print("\n" + "=" * 60)
print("TESTE FINALIZADO")
print("=" * 60)