import json
import re
from pathlib import Path
import numpy as np
import requests
import streamlit as st
import streamlit.components.v1 as components
from PIL import Image
from tensorflow import keras

# ============================================================
# CAMINHOS E CONFIGURAÇÕES DA PÁGINA
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_PATH = BASE_DIR / "model" / "pokemon_model_v2.keras"
CLASS_NAMES_PATH = BASE_DIR / "model" / "class_names.json"

st.set_page_config(
    page_title="PokéVision",
    page_icon="🔴",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Cores oficiais dos tipos
TYPE_COLORS = {
    "normal": "#A8A77A", "fire": "#EE8130", "water": "#6390F0",
    "electric": "#F7D02C", "grass": "#7AC74C", "ice": "#96D9D6",
    "fighting": "#C22E28", "poison": "#A33EA1", "ground": "#E2BF65",
    "flying": "#A98FF3", "psychic": "#F95587", "bug": "#A6B91A",
    "rock": "#B6A136", "ghost": "#735797", "dragon": "#6F35FC",
    "dark": "#705746", "steel": "#B7B7CE", "fairy": "#D685AD"
}

# Tradução dos tipos
TRANSLATE_TYPES = {
    "normal": "Normal", "fire": "Fogo", "water": "Água",
    "electric": "Elétrico", "grass": "Planta", "ice": "Gelo",
    "fighting": "Luta", "poison": "Veneno", "ground": "Terra",
    "flying": "Voador", "psychic": "Psíquico", "bug": "Inseto",
    "rock": "Pedra", "ghost": "Fantasma", "dragon": "Dragão",
    "dark": "Sombrio", "steel": "Aço", "fairy": "Fada"
}

# Tradução das estatísticas
TRANSLATE_STATS = {
    "HP": "PV",
    "ATTACK": "Ataque",
    "DEFENSE": "Defesa",
    "SP. ATTACK": "Atq. Esp.",
    "SP. DEFENSE": "Def. Esp.",
    "SPEED": "Velocidade"
}

# ============================================================
# ESTILIZAÇÃO CSS GLOBAL (FULLSCREEN TOTAL SEM BORDAS)
# ============================================================

st.markdown("""
<style>
    /* Oculta completamente elementos nativos do Streamlit */
    header[data-testid="stHeader"], footer, #MainMenu {
        display: none !important;
        visibility: hidden !important;
    }

    html, body, .stAppViewContainer, .stApp {
        margin: 0 !important;
        padding: 0 !important;
        background-color: #121214 !important;
        overflow: hidden !important;
    }
    
    .stMainBlockContainer, .block-container {
        padding: 0rem !important;
        max-width: 100% !important;
    }

    /* Esconde o botão acionador nativo que escuta o fechamento */
    div[data-element-id="stElementContainer"]:has(button[key="hidden_close_btn"]),
    div:has(> button[key="hidden_close_btn"]) {
        display: none !important;
        height: 0px !important;
        margin: 0px !important;
        padding: 0px !important;
    }

    /* Força o iframe a preencher 100% da altura da tela sem barras pretas */
    iframe {
        border: none !important;
        width: 100vw !important;
        height: 100vh !important;
        display: block !important;
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
    }
</style>
""", unsafe_allow_html=True)


# ============================================================
# CARREGAMENTO DO MODELO & POKÉAPI
# ============================================================

@st.cache_resource
def load_model():
    return keras.models.load_model(str(MODEL_PATH))


@st.cache_data
def load_class_names():
    with open(CLASS_NAMES_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def clean_pokemon_name(raw_name):
    clean_name = re.sub(r'^[0-9]+[-_]*', '', str(raw_name))
    return clean_name.lower().strip().replace(" ", "-")


def translate_pokedex_text(text):
    """Tradução simples para termos e frases recorrentes da Pokédex em inglês."""
    if not text:
        return "Um Pokémon fascinante registrado na Pokédex oficial."
    
    replacements = {
        "It ": "Ele ", "Its ": "Seu ", "They ": "Eles ",
        "When it ": "Quando ele ", "If it ": "Se ele ",
        "is said to": "dizem ser capaz de",
        "has a": "possui um(a)",
        "in the": "no(a)",
        "with its": "com seu(sua)",
        "to protect itself": "para se proteger",
        "body": "corpo",
        "fire": "fogo",
        "water": "água",
        "tail": "cauda",
        "head": "cabeça"
    }
    
    translated = text
    for en, pt in replacements.items():
        translated = re.sub(r'\b' + re.escape(en) + r'\b', pt, translated, flags=re.IGNORECASE)
    
    return translated


@st.cache_data
def fetch_pokeapi_data(raw_pokemon_name):
    pokemon_name = clean_pokemon_name(raw_pokemon_name)
    url = f"https://pokeapi.co/api/v2/pokemon/{pokemon_name}"
    
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            stats_map = {s["stat"]["name"]: s["base_stat"] for s in data["stats"]}
            
            # Fraquezas
            weaknesses = set()
            for t in data["types"]:
                type_url = t["type"]["url"]
                type_resp = requests.get(type_url, timeout=3)
                if type_resp.status_code == 200:
                    damage_rel = type_resp.json()["damage_relations"]
                    for double_damage in damage_rel["double_damage_from"]:
                        weaknesses.add(double_damage["name"])

            # Localização
            encounters_url = data["location_area_encounters"]
            encounters_resp = requests.get(encounters_url, timeout=3)
            locations = []
            if encounters_resp.status_code == 200:
                encounters_data = encounters_resp.json()
                for enc in encounters_data[:3]:
                    loc_name = enc["location_area"]["name"].replace("-", " ").title()
                    locations.append(loc_name)
            
            location_text = ", ".join(locations) if locations else "Inicial / Evolução / Evento"

            # Texto da Pokédex
            species_url = data["species"]["url"]
            species_resp = requests.get(species_url, timeout=3)
            pokedex_entry = "Um Pokémon fascinante registrado na Pokédex oficial."
            
            if species_resp.status_code == 200:
                species_data = species_resp.json()
                flavor_entries = species_data.get("flavor_text_entries", [])
                pt_entry = next((e["flavor_text"] for e in flavor_entries if e["language"]["name"] == "pt"), None)
                en_entry = next((e["flavor_text"] for e in flavor_entries if e["language"]["name"] == "en"), None)
                
                if pt_entry:
                    pokedex_entry = pt_entry.replace("\n", " ").replace("\f", " ")
                elif en_entry:
                    raw_text = en_entry.replace("\n", " ").replace("\f", " ")
                    pokedex_entry = translate_pokedex_text(raw_text)

            return {
                "id": data["id"],
                "name": data["name"].capitalize(),
                "height": data["height"] / 10.0,
                "weight": data["weight"] / 10.0,
                "types": [t["type"]["name"] for t in data["types"]],
                "weaknesses": list(weaknesses),
                "location": location_text,
                "pokedex_entry": pokedex_entry,
                "image_url": data["sprites"]["other"]["official-artwork"]["front_default"],
                "stats": {
                    "HP": stats_map.get("hp", 0),
                    "ATTACK": stats_map.get("attack", 0),
                    "DEFENSE": stats_map.get("defense", 0),
                    "SP. ATTACK": stats_map.get("special-attack", 0),
                    "SP. DEFENSE": stats_map.get("special-defense", 0),
                    "SPEED": stats_map.get("speed", 0)
                }
            }
    except Exception:
        pass

    return {
        "id": 52,
        "name": pokemon_name.capitalize(),
        "height": 0.4,
        "weight": 4.2,
        "types": ["normal"],
        "weaknesses": ["fighting"],
        "location": "Rota 5 e Rota 6 de Kanto",
        "pokedex_entry": "Ele adora objetos brilhantes. Quando encontra algo reluzente, suas moedas e olhos brilham intensamente.",
        "image_url": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/52.png",
        "stats": {"HP": 40, "ATTACK": 45, "DEFENSE": 35, "SP. ATTACK": 40, "SP. DEFENSE": 40, "SPEED": 90}
    }


try:
    model = load_model()
    class_names = load_class_names()
except Exception as e:
    st.error(f"Erro ao carregar o modelo: {e}")
    st.stop()


# ============================================================
# PREDIÇÃO DA IA
# ============================================================

def crop_center_square(image):
    width, height = image.size
    size = min(width, height)
    left = (width - size) // 2
    top = (height - size) // 2
    return image.crop((left, top, left + size, top + size))


def prepare_image(image):
    image = image.convert("RGB")
    image = crop_center_square(image)
    image = image.resize((224, 224))
    image_array = np.array(image, dtype=np.float32)
    return np.expand_dims(image_array, axis=0)


def predict(image):
    image_array = prepare_image(image)
    predictions = model.predict(image_array, verbose=0)[0]
    top_indices = np.argsort(predictions)[-5:][::-1]

    results = []
    for index in top_indices:
        results.append({
            "name": class_names[index],
            "confidence": float(predictions[index])
        })

    return results


# ============================================================
# ESTADOS E NAVEGAÇÃO
# ============================================================

if "current_view" not in st.session_state:
    st.session_state.current_view = "input"


# ============================================================
# TELA 1: CÂMERA / UPLOAD (TELA INICIAL)
# ============================================================

if st.session_state.current_view == "input":
    st.markdown('<div style="padding: 40px 60px;">', unsafe_allow_html=True)
    st.title("PokéVision")
    st.subheader("Reconhecimento de Pokémon com Inteligência Artificial")
    st.write("Tire uma foto ou envie uma imagem de um Pokémon para identificá-lo.")

    st.divider()

    col_cam, col_up = st.tabs(["Câmera", "Upload"])

    camera_image = None
    uploaded_image = None

    with col_cam:
        camera_image = st.camera_input("Centralize o Pokémon e tire uma foto")

    with col_up:
        uploaded_image = st.file_uploader("Escolha uma imagem", type=["jpg", "jpeg", "png"])

    image_source = camera_image if camera_image is not None else uploaded_image

    if image_source is not None:
        st.session_state.image_source = image_source
        st.session_state.current_view = "card"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)


# ============================================================
# TELA 2: CARD FULLSCREEN 100% TELA CHEIA E GIRO FLUIDO
# ============================================================

elif st.session_state.current_view == "card":
    
    # Gatilho oculto para o evento de fechamento
    if st.button("close_trigger", key="hidden_close_btn"):
        st.session_state.current_view = "input"
        st.rerun()

    pil_image = Image.open(st.session_state.image_source).convert("RGB")

    with st.spinner("🔍 Analisando Pokémon e carregando dados..."):
        results = predict(pil_image)
        best = results[0]
        poke_data = fetch_pokeapi_data(best["name"])

    primary_type = poke_data["types"][0].lower() if poke_data["types"] else "normal"
    card_bg_color = TYPE_COLORS.get(primary_type, "#7B78B5")

    type_badges_html = ""
    for t in poke_data["types"]:
        bg_color = TYPE_COLORS.get(t.lower(), "#777777")
        translated_type = TRANSLATE_TYPES.get(t.lower(), t.capitalize())
        type_badges_html += f'<div class="type-badge-circle" style="background-color: {bg_color};">{translated_type}</div>'

    weakness_badges_html = ""
    for w in poke_data["weaknesses"]:
        w_color = TYPE_COLORS.get(w.lower(), "#555555")
        translated_weakness = TRANSLATE_TYPES.get(w.lower(), w.capitalize())
        weakness_badges_html += f'<span class="weakness-badge" style="background-color: {w_color};">{translated_weakness}</span>'

    stats_html = ""
    for stat_name, stat_val in poke_data["stats"].items():
        translated_stat = TRANSLATE_STATS.get(stat_name, stat_name)
        stats_html += f'<div class="stat-pill"><span>{translated_stat}</span><span>{stat_val}</span></div>'

    art_html = f'<img src="{poke_data["image_url"]}" class="card-art-img">' if poke_data["image_url"] else ''

    top5_html = ""
    for i, result in enumerate(results, start=1):
        clean_name = clean_pokemon_name(result["name"]).capitalize()
        percentage = result["confidence"] * 100
        top5_html += f'<div class="prob-bar-box"><span>{i}. {clean_name}</span><span>{percentage:.2f}%</span></div>'

    component_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}
        html, body {{
            width: 100vw;
            height: 100vh;
            overflow: hidden;
            background-color: #121214;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }}
        .flip-scene {{
            width: 100vw;
            height: 100vh;
            perspective: 1200px;
        }}
        .flip-card {{
            width: 100%;
            height: 100%;
            position: relative;
            transform-style: preserve-3d;
            transition: transform 0.8s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        }}
        .flip-card.is-flipped {{
            transform: rotateY(180deg);
        }}
        .card-face {{
            position: absolute;
            width: 100vw;
            height: 100vh;
            backface-visibility: hidden;
            -webkit-backface-visibility: hidden;
            padding: 30px 50px 20px 50px;
            color: white;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }}
        .card-face-back {{
            transform: rotateY(180deg);
        }}
        .card-top-bar {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
        }}
        .card-poke-id {{
            font-size: 1.3rem;
            font-weight: 700;
            opacity: 0.85;
        }}
        .card-poke-name {{
            font-size: 3.4rem;
            font-weight: 800;
            margin: 0;
            text-transform: capitalize;
            line-height: 1.1;
        }}
        .card-poke-meta {{
            font-size: 0.95rem;
            opacity: 0.95;
            margin-top: 8px;
            line-height: 1.5;
        }}
        .type-badge-circle {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            padding: 8px 20px;
            border-radius: 25px;
            color: white;
            font-weight: 800;
            font-size: 0.9rem;
            text-transform: uppercase;
            margin-left: 8px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
            border: 2px solid rgba(255, 255, 255, 0.4);
        }}
        .weakness-badge {{
            display: inline-block;
            padding: 3px 10px;
            border-radius: 12px;
            font-size: 0.75rem;
            font-weight: 700;
            text-transform: uppercase;
            margin-right: 5px;
            margin-top: 3px;
            color: white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }}
        .card-body-grid {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 40px;
            flex: 1;
            margin-top: 10px;
            margin-bottom: 10px;
        }}
        .card-art-box {{
            flex: 1;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100%;
        }}
        .card-art-img {{
            max-height: 52vh;
            max-width: 100%;
            width: auto;
            height: auto;
            object-fit: contain;
            filter: drop-shadow(0 12px 20px rgba(0,0,0,0.35));
        }}
        .card-stats-box {{
            flex: 1.1;
        }}
        .stats-title {{
            font-size: 1.4rem;
            font-weight: 800;
            margin-bottom: 10px;
        }}
        .stat-pill {{
            background: #FFFFFF;
            color: #2D3748;
            border-radius: 12px;
            padding: 8px 18px;
            margin: 6px 0;
            font-size: 0.95rem;
            font-weight: 800;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 3px 6px rgba(0,0,0,0.1);
        }}
        .embedded-btn {{
            background-color: rgba(0, 0, 0, 0.25);
            color: white !important;
            border: 1px solid rgba(255, 255, 255, 0.4);
            border-radius: 20px;
            padding: 8px 20px;
            font-weight: 700;
            font-size: 0.88rem;
            cursor: pointer;
            backdrop-filter: blur(5px);
            transition: all 0.2s ease-in-out;
            text-decoration: none !important;
            display: inline-block;
        }}
        .embedded-btn:hover {{
            background-color: rgba(0, 0, 0, 0.5);
            border-color: white;
            transform: scale(1.03);
        }}
        .pokedex-quote-box {{
            background: rgba(255, 255, 255, 0.12);
            border-left: 6px solid #FFFFFF;
            border-radius: 14px;
            padding: 20px 25px;
            font-size: 1.2rem;
            line-height: 1.6;
            font-style: italic;
            margin-bottom: 20px;
            backdrop-filter: blur(5px);
        }}
        .prob-bar-box {{
            background: rgba(255, 255, 255, 0.15);
            border-radius: 12px;
            padding: 8px 16px;
            margin: 5px 0;
            display: flex;
            justify-content: space-between;
            font-weight: 700;
            font-size: 0.95rem;
        }}
        .card-footer-nav {{
            text-align: center;
            padding-bottom: 10px;
        }}
    </style>
    </head>
    <body>

    <div class="flip-scene">
        <div class="flip-card" id="poke3DCard">
            
            <!-- LADO FRENTE (ESTATÍSTICAS) -->
            <div class="card-face" style="background: linear-gradient(135deg, {card_bg_color} 0%, rgba(0,0,0,0.3) 100%), {card_bg_color};">
                <div class="card-top-bar">
                    <div>
                        <div class="card-poke-id">#{poke_data['id']:03d}</div>
                        <div class="card-poke-name">{poke_data['name']}</div>
                        <div class="card-poke-meta">
                            <b>Altura:</b> {poke_data['height']} m &nbsp;|&nbsp; <b>Peso:</b> {poke_data['weight']} kg<br>
                            <b>Locais:</b> {poke_data['location']}<br>
                            <b>Fraquezas:</b> {weakness_badges_html}
                        </div>
                    </div>
                    <div style="display: flex; align-items: center;">
                        {type_badges_html}
                        <button onclick="closeCard()" class="embedded-btn" style="margin-left: 15px;">✖ Fechar</button>
                    </div>
                </div>
                <div class="card-body-grid">
                    <div class="card-art-box">{art_html}</div>
                    <div class="card-stats-box">
                        <div class="stats-title">Estatísticas Base:</div>
                        {stats_html}
                    </div>
                </div>
                <div class="card-footer-nav">
                    <button onclick="flipCard()" class="embedded-btn"> Ver Pokédex & Precisão</button>
                </div>
            </div>
            
            <!-- LADO VERSO (POKÉDEX & PRECISÃO IA) -->
            <div class="card-face card-face-back" style="background: linear-gradient(135deg, {card_bg_color} 0%, rgba(0,0,0,0.3) 100%), {card_bg_color};">
                <div class="card-top-bar">
                    <div>
                        <div class="card-poke-id">#{poke_data['id']:03d}</div>
                        <div class="card-poke-name">{poke_data['name']}</div>
                        <div class="card-poke-meta">
                            <b>Altura:</b> {poke_data['height']} m &nbsp;|&nbsp; <b>Peso:</b> {poke_data['weight']} kg<br>
                            <b>Locais:</b> {poke_data['location']}<br>
                            <b>Fraquezas:</b> {weakness_badges_html}
                        </div>
                    </div>
                    <div style="display: flex; align-items: center;">
                        {type_badges_html}
                        <button onclick="closeCard()" class="embedded-btn" style="margin-left: 15px;">✖ Fechar</button>
                    </div>
                </div>
                <div style="flex: 1; margin-top: 15px; display: flex; flex-direction: column; justify-content: center; padding-bottom: 20px;">
                    <div class="stats-title"> Registro Oficial da Pokédex:</div>
                    <div class="pokedex-quote-box">"{poke_data['pokedex_entry']}"</div>
                    <div class="stats-title"> Precisão da Identificação (IA):</div>
                    <div>{top5_html}</div>
                </div>
                <div class="card-footer-nav">
                    <button onclick="flipCard()" class="embedded-btn"> Voltar para Estatísticas</button>
                </div>
            </div>
            
        </div>
    </div>

    <script>
        function flipCard() {{
            var card = document.getElementById('poke3DCard');
            if (card) {{
                card.classList.toggle('is-flipped');
            }}
        }}

        function closeCard() {{
            var btn = window.parent.document.querySelector('button[key="hidden_close_btn"]');
            if (btn) {{
                btn.click();
            }} else {{
                window.parent.location.reload();
            }}
        }}
    </script>
    </body>
    </html>
    """

    components.html(component_code)