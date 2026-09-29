from pathlib import Path
from PIL import Image

DATASET_DIR = Path("dataset/organized")

EXTENSOES_VALIDAS = {".jpg", ".jpeg", ".png", ".webp"}

total_imagens = 0
classes_ok = 0
problemas = []

pastas = sorted(DATASET_DIR.iterdir())

print("=" * 60)
print("VALIDAÇÃO DO DATASET")
print("=" * 60)

for pasta in pastas:
    if not pasta.is_dir():
        continue

    imagens = [
        arquivo for arquivo in pasta.iterdir()
        if arquivo.suffix.lower() in EXTENSOES_VALIDAS
    ]

    classe_ok = True

    for imagem in imagens:
        try:
            with Image.open(imagem) as img:
                img.verify()
        except Exception as e:
            problemas.append((imagem, str(e)))
            classe_ok = False

    total_imagens += len(imagens)

    if len(imagens) == 100 and classe_ok:
        classes_ok += 1
        print(f"✓ {pasta.name}: {len(imagens)} imagens")
    else:
        print(f"⚠ {pasta.name}: {len(imagens)} imagens")

print("\n" + "=" * 60)
print(f"Classes corretas: {classes_ok}/151")
print(f"Imagens encontradas: {total_imagens}")
print(f"Imagens esperadas: 15100")
print(f"Arquivos com problema: {len(problemas)}")
print("=" * 60)

if problemas:
    print("\nARQUIVOS COM PROBLEMA:")
    for arquivo, erro in problemas:
        print(f"- {arquivo}: {erro}")

if classes_ok == 151 and total_imagens == 15100 and not problemas:
    print("\n DATASET 100% VALIDADO!")
else:
    print("\n⚠ O dataset precisa de atenção antes do treinamento.")