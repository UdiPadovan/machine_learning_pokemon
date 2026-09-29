import os

POKEMON = [
    "bulbasaur", "ivysaur", "venusaur",
    "charmander", "charmeleon", "charizard",
    "squirtle", "wartortle", "blastoise",
    "caterpie", "metapod", "butterfree",
    "weedle", "kakuna", "beedrill",
    "pidgey", "pidgeotto", "pidgeot",
    "rattata", "raticate",
    "spearow", "fearow",
    "ekans", "arbok",
    "pikachu", "raichu",
    "sandshrew", "sandslash",
    "nidoran-f", "nidorina", "nidoqueen",
    "nidoran-m", "nidorino", "nidoking",
    "clefairy", "clefable",
    "vulpix", "ninetales",
    "jigglypuff", "wigglytuff",
    "zubat", "golbat",
    "oddish", "gloom", "vileplume",
    "paras", "parasect",
    "venonat", "venomoth",
    "diglett", "dugtrio",
    "meowth", "persian",
    "psyduck", "golduck",
    "mankey", "primeape",
    "growlithe", "arcanine",
    "poliwag", "poliwhirl", "poliwrath",
    "abra", "kadabra", "alakazam",
    "machop", "machoke", "machamp",
    "bellsprout", "weepinbell", "victreebel",
    "tentacool", "tentacruel",
    "geodude", "graveler", "golem",
    "ponyta", "rapidash",
    "slowpoke", "slowbro",
    "magnemite", "magneton",
    "farfetchd",
    "doduo", "dodrio",
    "seel", "dewgong",
    "grimer", "muk",
    "shellder", "cloyster",
    "gastly", "haunter", "gengar",
    "onix",
    "drowzee", "hypno",
    "krabby", "kingler",
    "voltorb", "electrode",
    "exeggcute", "exeggutor",
    "cubone", "marowak",
    "hitmonlee", "hitmonchan",
    "lickitung",
    "koffing", "weezing",
    "rhyhorn", "rhydon",
    "chansey",
    "tangela",
    "kangaskhan",
    "horsea", "seadra",
    "goldeen", "seaking",
    "staryu", "starmie",
    "mr-mime",
    "scyther",
    "jynx",
    "electabuzz",
    "magmar",
    "pinsir",
    "tauros",
    "magikarp", "gyarados",
    "lapras",
    "ditto",
    "eevee",
    "vaporeon", "jolteon", "flareon",
    "porygon",
    "omanyte", "omastar",
    "kabuto", "kabutops",
    "aerodactyl",
    "snorlax",
    "articuno", "zapdos", "moltres",
    "dratini", "dragonair", "dragonite",
    "mewtwo", "mew"
]

BASE_DIR = "dataset"

for split in ["raw", "train", "validation", "test"]:
    for i, pokemon in enumerate(POKEMON, start=1):

        folder = f"{i:03d}-{pokemon}"

        path = os.path.join(BASE_DIR, split, folder)

        os.makedirs(path, exist_ok=True)

print("Dataset criado!")
print(f"Classes: {len(POKEMON)}")