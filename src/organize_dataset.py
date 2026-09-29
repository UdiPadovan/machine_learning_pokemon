import os
import shutil

# Pasta onde está o dataset original
SOURCE_DIR = "dataset/kaggle/pkm_c_aug_new"

# Pasta onde será criado o dataset organizado
DEST_DIR = "dataset/organized"


POKEMON = [
    "Bulbasaur",
    "Ivysaur",
    "Venusaur",
    "Charmander",
    "Charmeleon",
    "Charizard",
    "Squirtle",
    "Wartortle",
    "Blastoise",
    "Caterpie",
    "Metapod",
    "Butterfree",
    "Weedle",
    "Kakuna",
    "Beedrill",
    "Pidgey",
    "Pidgeotto",
    "Pidgeot",
    "Rattata",
    "Raticate",
    "Spearow",
    "Fearow",
    "Ekans",
    "Arbok",
    "Pikachu",
    "Raichu",
    "Sandshrew",
    "Sandslash",
    "Nidoran_female",
    "Nidorina",
    "Nidoqueen",
    "Nidoran_male",
    "Nidorino",
    "Nidoking",
    "Clefairy",
    "Clefable",
    "Vulpix",
    "Ninetales",
    "Jigglypuff",
    "Wigglytuff",
    "Zubat",
    "Golbat",
    "Oddish",
    "Gloom",
    "Vileplume",
    "Paras",
    "Parasect",
    "Venonat",
    "Venomoth",
    "Diglett",
    "Dugtrio",
    "Meowth",
    "Persian",
    "Psyduck",
    "Golduck",
    "Mankey",
    "Primeape",
    "Growlithe",
    "Arcanine",
    "Poliwag",
    "Poliwhirl",
    "Poliwrath",
    "Abra",
    "Kadabra",
    "Alakazam",
    "Machop",
    "Machoke",
    "Machamp",
    "Bellsprout",
    "Weepinbell",
    "Victreebel",
    "Tentacool",
    "Tentacruel",
    "Geodude",
    "Graveler",
    "Golem",
    "Ponyta",
    "Rapidash",
    "Slowpoke",
    "Slowbro",
    "Magnemite",
    "Magneton",
    "Farfetchd",
    "Doduo",
    "Dodrio",
    "Seel",
    "Dewgong",
    "Grimer",
    "Muk",
    "Shellder",
    "Cloyster",
    "Gastly",
    "Haunter",
    "Gengar",
    "Onix",
    "Drowzee",
    "Hypno",
    "Krabby",
    "Kingler",
    "Voltorb",
    "Electrode",
    "Exeggcute",
    "Exeggutor",
    "Cubone",
    "Marowak",
    "Hitmonlee",
    "Hitmonchan",
    "Lickitung",
    "Koffing",
    "Weezing",
    "Rhyhorn",
    "Rhydon",
    "Chansey",
    "Tangela",
    "Kangaskhan",
    "Horsea",
    "Seadra",
    "Goldeen",
    "Seaking",
    "Staryu",
    "Starmie",
    "Mr. Mime",
    "Scyther",
    "Jynx",
    "Electabuzz",
    "Magmar",
    "Pinsir",
    "Tauros",
    "Magikarp",
    "Gyarados",
    "Lapras",
    "Ditto",
    "Eevee",
    "Vaporeon",
    "Jolteon",
    "Flareon",
    "Porygon",
    "Omanyte",
    "Omastar",
    "Kabuto",
    "Kabutops",
    "Aerodactyl",
    "Snorlax",
    "Articuno",
    "Zapdos",
    "Moltres",
    "Dratini",
    "Dragonair",
    "Dragonite",
    "Mewtwo",
    "Mew"
]


def encontrar_pasta(nome):
    """
    Procura a pasta correspondente ao Pokémon.
    Ignora diferenças entre maiúsculas e minúsculas.
    """

    if not os.path.exists(SOURCE_DIR):
        return None

    pastas = os.listdir(SOURCE_DIR)

    nome_normalizado = nome.lower().replace(" ", "").replace(".", "")

    for pasta in pastas:

        if not os.path.isdir(os.path.join(SOURCE_DIR, pasta)):
            continue

        pasta_normalizada = (
            pasta.lower()
            .replace(" ", "")
            .replace(".", "")
        )

        if pasta_normalizada == nome_normalizado:
            return pasta

    return None


def main():

    print("Organizando dataset...")
    print()

    os.makedirs(DEST_DIR, exist_ok=True)

    sucesso = 0
    erros = []

    for numero, pokemon in enumerate(POKEMON, start=1):

        pasta_original = encontrar_pasta(pokemon)

        if pasta_original is None:

            print(f"❌ Não encontrada: {pokemon}")
            erros.append(pokemon)
            continue

        nome_destino = f"{numero:03d}-{pokemon}"

        pasta_origem = os.path.join(
            SOURCE_DIR,
            pasta_original
        )

        pasta_destino = os.path.join(
            DEST_DIR,
            nome_destino
        )

        os.makedirs(pasta_destino, exist_ok=True)

        arquivos = os.listdir(pasta_origem)

        contador = 0

        for arquivo in arquivos:

            caminho_origem = os.path.join(
                pasta_origem,
                arquivo
            )

            caminho_destino = os.path.join(
                pasta_destino,
                arquivo
            )

            if os.path.isfile(caminho_origem):

                shutil.copy2(
                    caminho_origem,
                    caminho_destino
                )

                contador += 1

        print(
            f"✓ {numero:03d} - {pokemon}: "
            f"{contador} imagens"
        )

        sucesso += 1

    print()
    print("=" * 50)
    print(f"Pokémon organizados: {sucesso}/151")

    if erros:
        print()
        print("Pastas não encontradas:")
        for erro in erros:
            print(f" - {erro}")

    print("=" * 50)


if __name__ == "__main__":
    main()