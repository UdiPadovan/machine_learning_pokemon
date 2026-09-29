from pathlib import Path
import shutil
import random

SOURCE_DIR = Path("dataset/organized")
DEST_DIR = Path("dataset")

TRAIN_DIR = DEST_DIR / "train"
VAL_DIR = DEST_DIR / "validation"
TEST_DIR = DEST_DIR / "test"

SEED = 42
random.seed(SEED)

EXTENSOES_VALIDAS = {".jpg", ".jpeg", ".png", ".webp"}

# Limpar pastas antigas
for pasta in [TRAIN_DIR, VAL_DIR, TEST_DIR]:
    if pasta.exists():
        shutil.rmtree(pasta)

    pasta.mkdir(parents=True)

print("=" * 60)
print("SEPARANDO DATASET")
print("=" * 60)

total_train = 0
total_val = 0
total_test = 0

classes = sorted(
    [p for p in SOURCE_DIR.iterdir() if p.is_dir()],
    key=lambda x: int(x.name.split("-")[0])
)

for classe in classes:

    imagens = [
        arquivo for arquivo in classe.iterdir()
        if arquivo.suffix.lower() in EXTENSOES_VALIDAS
    ]

    random.shuffle(imagens)

    total = len(imagens)

    train_count = int(total * 0.70)
    val_count = int(total * 0.15)

    train_images = imagens[:train_count]
    val_images = imagens[train_count:train_count + val_count]
    test_images = imagens[train_count + val_count:]

    for destino, arquivos in [
        (TRAIN_DIR, train_images),
        (VAL_DIR, val_images),
        (TEST_DIR, test_images)
    ]:

        pasta_destino = destino / classe.name
        pasta_destino.mkdir(parents=True, exist_ok=True)

        for imagem in arquivos:
            shutil.copy2(imagem, pasta_destino / imagem.name)

    total_train += len(train_images)
    total_val += len(val_images)
    total_test += len(test_images)

    print(
        f"✓ {classe.name}: "
        f"{len(train_images)} treino | "
        f"{len(val_images)} validação | "
        f"{len(test_images)} teste"
    )

print("\n" + "=" * 60)
print("DIVISÃO CONCLUÍDA")
print("=" * 60)

print(f"Treino:      {total_train}")
print(f"Validação:   {total_val}")
print(f"Teste:       {total_test}")
print(f"TOTAL:       {total_train + total_val + total_test}")

print("=" * 60)