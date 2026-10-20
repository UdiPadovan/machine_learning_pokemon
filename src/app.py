import json
import re
import base64
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

# Imagem de Fundo (Se estiver na mesma pasta ou na pasta assets)
BACKGROUND_IMAGE_PATH = BASE_DIR / "assets" / "image" / "fundo_floresta.jpg"

ICON_URL = "https://img.icons8.com/?size=100&id=45658&format=png&color=000000"

st.set_page_config(
    page_title="PokéVision",
    page_icon=ICON_URL,
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Função para converter imagem local para Base64 (para uso direto no CSS/HTML)
def get_image_base64(image_path):
    if Path(image_path).exists():
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return ""

bg_base64 = get_image_base64(BACKGROUND_IMAGE_PATH)
bg_css_url = f"data:image/jpeg;base64,{bg_base64}" if bg_base64 else "https://i.imgur.com/8QzX9ZW.jpg"

# Cores por Tipo
TYPE_COLORS = {
    "grass": "#48d0b0", "fire": "#fb6c6c", "water": "#76bdfe",
    "electric": "#ffd86f", "poison": "#a040a0", "bug": "#a8b820",
    "normal": "#a8a878", "flying": "#a890f0", "ground": "#e0c068",
    "rock": "#b8a038", "ice": "#98d8d8", "fighting": "#c03028",
    "psychic": "#f85888", "ghost": "#705898", "dragon": "#7038f8",
    "dark": "#705848", "steel": "#b8b8d0", "fairy": "#f0b6bc"
}

TRANSLATE_TYPES = {
    "normal": "Normal", "fire": "Fogo", "water": "Água",
    "electric": "Elétrico", "grass": "Planta", "ice": "Gelo",
    "fighting": "Luta", "poison": "Veneno", "ground": "Terra",
    "flying": "Voador", "psychic": "Psíquico", "bug": "Inseto",
    "rock": "Pedra", "ghost": "Fantasma", "dragon": "Dragão",
    "dark": "Sombrio", "steel": "Aço", "fairy": "Fada"
}

TRANSLATE_STATS = {
    "HP": "HP",
    "ATTACK": "Ataque",
    "DEFENSE": "Defesa",
    "SP. ATTACK": "Atq. Esp.",
    "SP. DEFENSE": "Def. Esp.",
    "SPEED": "Velocidade"
}

MAX_STATS = {
    "HP": 255, "ATTACK": 190, "DEFENSE": 230,
    "SP. ATTACK": 194, "SP. DEFENSE": 230, "SPEED": 180
}

# ============================================================
# ESTILIZAÇÃO CSS GLOBAL (FUNDO FLORESTA DE GRAMA)
# ============================================================

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&family=Outfit:wght@600;800;900&display=swap');

    header[data-testid="stHeader"], footer, #MainMenu {{
        display: none !important;
        visibility: hidden !important;
    }}

    html, body, .stAppViewContainer, .stApp {{
        margin: 0 !important;
        padding: 0 !important;
        background-image: url('{bg_css_url}') !important;
        background-size: cover !important;
        background-position: center !important;
        background-repeat: no-repeat !important;
        background-attachment: fixed !important;
        font-family: 'Outfit', sans-serif !important;
        overflow-x: hidden !important;
    }}
    
    .stMainBlockContainer, .block-container {{
        padding: 20px 0rem !important;
        max-width: 700px !important;
        margin: 0 auto !important;
    }}

    div[data-element-id="stElementContainer"]:has(button[key="hidden_close_btn"]),
    div:has(> button[key="hidden_close_btn"]) {{
        display: none !important;
        height: 0px !important;
        margin: 0px !important;
        padding: 0px !important;
    }}

    iframe {{
        border: none !important;
        width: 100vw !important;
        height: 100vh !important;
        display: block !important;
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
    }}

    /* CARD RETRO COMPLETO DA POKÉDEX (TELA 1) */
    .retro-pokedex-frame {{
        background-color: #ff3b30;
        border: 4px solid #000000;
        border-radius: 24px;
        padding: 20px;
        box-shadow: 0 15px 35px rgba(0,0,0,0.6);
        position: relative;
    }}

    .retro-top-bar {{
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        position: relative;
        padding-bottom: 15px;
        border-bottom: 4px solid #000000;
        margin-bottom: 20px;
    }}

    .retro-big-lens {{
        width: 65px;
        height: 65px;
        background: radial-gradient(circle at 35% 35%, #00e5ff 0%, #0088cc 60%, #003366 100%);
        border-radius: 50%;
        border: 4px solid #000000;
        box-shadow: inset 0 0 10px rgba(255,255,255,0.8);
    }}

    .retro-title-area {{
        text-align: right;
    }}

    .retro-pokedex-title {{
        font-family: 'Press Start 2P', cursive;
        font-size: 1rem;
        color: #000000;
        margin: 0;
        line-height: 1.4;
        text-transform: uppercase;
    }}

    .retro-pokeball-icon {{
        width: 32px;
        height: 32px;
        background: linear-gradient(#ff3b30 50%, #ffffff 50%);
        border: 3px solid #000000;
        border-radius: 50%;
        display: inline-block;
        position: relative;
        margin-left: 8px;
        vertical-align: middle;
    }}
    .retro-pokeball-icon::after {{
        content: '';
        position: absolute;
        top: 50%; left: 50%;
        transform: translate(-50%, -50%);
        width: 10px; height: 10px;
        background: #ffffff;
        border: 2px solid #000000;
        border-radius: 50%;
    }}

    /* TELA CENTRAL BRANCA COM MOLDURA PRETA */
    div[data-testid="stTabs"] {{
        background: #ffffff !important;
        border: 4px solid #000000 !important;
        border-radius: 12px !important;
        padding: 15px !important;
        box-shadow: inset 0 0 8px rgba(0,0,0,0.2) !important;
    }}

    div[data-testid="stTabHeaderList"] {{
        border-bottom: 3px solid #000000 !important;
        padding-bottom: 6px !important;
        gap: 8px !important;
    }}

    button[data-baseweb="tab"] {{
        background-color: #e0e0e0 !important;
        color: #000000 !important;
        border-radius: 6px !important;
        font-family: 'Press Start 2P', cursive !important;
        font-size: 0.65rem !important;
        padding: 8px 12px !important;
        border: 2px solid #000000 !important;
    }}

    button[data-baseweb="tab"][aria-selected="true"] {{
        background-color: #8bac0f !important;
        color: #0f380f !important;
    }}

    div[data-testid="stFileUploadDropzone"] {{
        background-color: #f8f9fa !important;
        border: 2px dashed #000000 !important;
        border-radius: 8px !important;
    }}

    /* PAINEL INFERIOR RETRO */
    .retro-bottom-panel {{
        margin-top: 20px;
        background-color: #4a4a4a;
        border: 4px solid #000000;
        border-radius: 12px;
        padding: 15px;
        display: flex;
        flex-direction: column;
        gap: 12px;
    }}

    .retro-name-type-bar {{
        background-color: #8bac0f;
        border: 3px solid #000000;
        border-radius: 8px;
        padding: 8px 12px;
        font-family: 'Press Start 2P', cursive;
        font-size: 0.75rem;
        color: #0f380f;
        display: flex;
        justify-content: space-between;
    }}

    .retro-controls-row {{
        display: flex;
        align-items: center;
        justify-content: space-between;
    }}

    .retro-dpad {{
        width: 60px;
        height: 60px;
        position: relative;
    }}
    .retro-dpad-cross {{
        background: #222222;
        border: 2px solid #000000;
        position: absolute;
    }}
    .retro-dpad-v {{ width: 20px; height: 60px; left: 20px; top: 0; border-radius: 4px; }}
    .retro-dpad-h {{ width: 60px; height: 20px; left: 0; top: 20px; border-radius: 4px; }}

    .retro-screen-desc {{
        background-color: #9bbc0f;
        border: 3px solid #000000;
        border-radius: 8px;
        padding: 10px;
        font-family: 'Press Start 2P', cursive;
        font-size: 0.65rem;
        color: #0f380f;
        text-align: center;
        flex: 1;
        margin: 0 15px;
        line-height: 1.4;
    }}

    .retro-action-btns {{
        display: flex;
        flex-direction: column;
        gap: 8px;
    }}

    .retro-btn-circle {{
        width: 28px;
        height: 28px;
        border-radius: 50%;
        border: 2px solid #000000;
        display: flex;
        align-items: center;
        justify-content: center;
        font-family: 'Press Start 2P', cursive;
        font-size: 0.6rem;
        font-weight: bold;
    }}
    .btn-red {{ background-color: #ff3b30; color: #ffffff; }}
    .btn-green {{ background-color: #4cd964; color: #000000; }}
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
    if not text:
        return "Um Pokémon fascinante registrado na Pokédex oficial."
    
    replacements = {
        "It ": "Ele ", "Its ": "Seu ", "They ": "Eles ",
        "When it ": "Quando ele ", "If it ": "Se ele "
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
            
            weaknesses = set()
            for t in data["types"]:
                type_url = t["type"]["url"]
                type_resp = requests.get(type_url, timeout=3)
                if type_resp.status_code == 200:
                    damage_rel = type_resp.json()["damage_relations"]
                    for double_damage in damage_rel["double_damage_from"]:
                        weaknesses.add(double_damage["name"])

            encounters_url = data["location_area_encounters"]
            encounters_resp = requests.get(encounters_url, timeout=3)
            locations = []
            if encounters_resp.status_code == 200:
                encounters_data = encounters_resp.json()
                for enc in encounters_data[:3]:
                    loc_name = enc["location_area"]["name"].replace("-", " ").title()
                    locations.append(loc_name)
            
            location_text = ", ".join(locations) if locations else "Inicial / Evolução"

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
        "id": 4,
        "name": pokemon_name.capitalize(),
        "height": 0.6,
        "weight": 8.5,
        "types": ["fire"],
        "weaknesses": ["water", "ground", "rock"],
        "location": "Rota 3 e Kanto",
        "pokedex_entry": "A chama que queima na ponta de sua cauda indica sua força vital.",
        "image_url": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/4.png",
        "stats": {"HP": 39, "ATTACK": 52, "DEFENSE": 43, "SP. ATTACK": 60, "SP. DEFENSE": 50, "SPEED": 65}
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
# TELA 1: CÂMERA / UPLOAD (MOLDURA POKÉDEX CLASSIC)
# ============================================================

if st.session_state.current_view == "input":
    st.markdown("""
        <div class="retro-pokedex-frame">
            <div class="retro-top-bar">
                <div class="retro-big-lens"></div>
                <div class="retro-title-area">
                    <span class="retro-pokedex-title">POKÉDEX OF<br>ANOMALIES</span>
                    <div class="retro-pokeball-icon"></div>
                </div>
            </div>
    """, unsafe_allow_html=True)

    col_cam, col_up = st.tabs(["📷 CÂMERA", "🖼️ UPLOAD"])

    camera_image = None
    uploaded_image = None

    with col_cam:
        camera_image = st.camera_input("Centralize o Pokémon")

    with col_up:
        uploaded_image = st.file_uploader("Selecione a imagem do Pokémon", type=["jpg", "jpeg", "png"])

    st.markdown("""
            <div class="retro-bottom-panel">
                <div class="retro-name-type-bar">
                    <span>NOME DO POKEMON</span>
                    <span>TIPO(S)</span>
                </div>
                <div class="retro-controls-row">
                    <div class="retro-dpad">
                        <div class="retro-dpad-cross retro-dpad-v"></div>
                        <div class="retro-dpad-cross retro-dpad-h"></div>
                    </div>
                    <div class="retro-screen-desc">
                        APONTE A CÂMERA OU ENVIE UMA FOTO PARA IDENTIFICAR O POKÉMON!
                    </div>
                    <div class="retro-action-btns">
                        <div class="retro-btn-circle btn-red">X</div>
                        <div class="retro-btn-circle btn-green">✓</div>
                    </div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    image_source = camera_image if camera_image is not None else uploaded_image

    if image_source is not None:
        st.session_state.image_source = image_source
        st.session_state.current_view = "card"
        st.rerun()


# ============================================================
# TELA 2: CARD SOBRE O FUNDO DA FLORESTA
# ============================================================

elif st.session_state.current_view == "card":
    
    if st.button("close_trigger", key="hidden_close_btn"):
        st.session_state.current_view = "input"
        st.rerun()

    pil_image = Image.open(st.session_state.image_source).convert("RGB")

    with st.spinner("🔍 Analisando Pokémon..."):
        results = predict(pil_image)
        best = results[0]
        poke_data = fetch_pokeapi_data(best["name"])

    primary_type = poke_data["types"][0].lower() if poke_data["types"] else "grass"
    card_theme_color = TYPE_COLORS.get(primary_type, "#fb6c6c")

    type_badges_html = ""
    for t in poke_data["types"]:
        translated_type = TRANSLATE_TYPES.get(t.lower(), t.capitalize())
        type_badges_html += f'<span class="type-badge">{translated_type}</span>'

    stats_bars_html = ""
    total_stats = sum(poke_data["stats"].values())
    
    for stat_key, stat_val in poke_data["stats"].items():
        translated_stat = TRANSLATE_STATS.get(stat_key, stat_key)
        max_val = MAX_STATS.get(stat_key, 200)
        percentage = min(int((stat_val / max_val) * 100), 100)
        bar_color = "#48d0b0" if percentage >= 50 else "#fb6c6c"
        
        stats_bars_html += f"""
        <div class="stat-row">
            <span class="stat-label">{translated_stat}</span>
            <span class="stat-value">{stat_val}</span>
            <div class="stat-bar-bg">
                <div class="stat-bar-fill" style="width: {percentage}%; background-color: {bar_color};"></div>
            </div>
        </div>
        """

    top5_html = ""
    for i, result in enumerate(results, start=1):
        clean_name = clean_pokemon_name(result["name"]).capitalize()
        percentage = result["confidence"] * 100
        top5_html += f"""
        <div class="prob-row">
            <span>{i}. {clean_name}</span>
            <span style="font-weight: 700;">{percentage:.1f}%</span>
        </div>
        """

    component_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
        }}
        html, body {{
            width: 100vw;
            height: 100vh;
            overflow: hidden;
            background-image: url('{bg_css_url}');
            background-size: cover;
            background-position: center;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        
        .pokedex-app-container {{
            width: 95%;
            max-width: 780px;
            height: 88vh;
            max-height: 820px;
            background-color: {card_theme_color};
            border-radius: 32px;
            position: relative;
            display: flex;
            flex-direction: column;
            overflow: hidden;
            box-shadow: 0 25px 50px rgba(0, 0, 0, 0.7);
        }}

        .pokeball-watermark {{
            position: absolute;
            right: -60px;
            top: 40px;
            width: 280px;
            height: 280px;
            opacity: 0.15;
            background: radial-gradient(circle, transparent 40%, #ffffff 40%, #ffffff 50%, transparent 50%),
                        linear-gradient(#ffffff 45%, transparent 45%, transparent 55%, #ffffff 55%);
            border-radius: 50%;
            pointer-events: none;
        }}

        .app-header {{
            padding: 24px 32px 10px 32px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            color: white;
            z-index: 10;
        }}
        
        .back-btn {{
            background: rgba(255, 255, 255, 0.22);
            border: none;
            color: white;
            font-size: 22px;
            cursor: pointer;
            width: 42px;
            height: 42px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            backdrop-filter: blur(5px);
            transition: background 0.2s;
        }}

        .back-btn:hover {{
            background: rgba(255, 255, 255, 0.4);
        }}

        .poke-title-section {{
            padding: 0 32px;
            color: white;
            z-index: 10;
            display: flex;
            justify-content: space-between;
            align-items: flex-end;
        }}

        .poke-name {{
            font-size: 2.6rem;
            font-weight: 800;
            letter-spacing: -0.5px;
            margin-bottom: 6px;
        }}

        .poke-id {{
            font-size: 1.3rem;
            font-weight: 700;
            opacity: 0.85;
        }}

        .type-badges-container {{
            display: flex;
            gap: 10px;
            margin-top: 6px;
        }}

        .type-badge {{
            background: rgba(255, 255, 255, 0.25);
            backdrop-filter: blur(8px);
            color: white;
            padding: 6px 18px;
            border-radius: 20px;
            font-size: 0.9rem;
            font-weight: 700;
            text-transform: capitalize;
        }}

        .artwork-container {{
            width: 100%;
            height: 270px;
            display: flex;
            align-items: center;
            justify-content: center;
            position: relative;
            z-index: 20;
            margin-top: 0px;
        }}

        .artwork-img {{
            max-height: 290px;
            max-width: 85%;
            object-fit: contain;
            filter: drop-shadow(0 16px 20px rgba(0,0,0,0.32));
            transition: transform 0.3s ease;
        }}

        .sheet-container {{
            flex: 1;
            background: white;
            border-top-left-radius: 36px;
            border-top-right-radius: 36px;
            padding: 40px 32px 24px 32px;
            margin-top: -35px;
            z-index: 15;
            display: flex;
            flex-direction: column;
            overflow-y: auto;
        }}

        .sheet-tabs {{
            display: flex;
            justify-content: space-between;
            border-bottom: 2px solid #f0f0f5;
            padding-bottom: 12px;
            margin-bottom: 22px;
        }}

        .tab-item {{
            font-size: 1rem;
            font-weight: 700;
            color: #8e8e93;
            cursor: pointer;
            position: relative;
            padding: 6px 0;
            transition: color 0.2s ease;
        }}

        .tab-item.active {{
            color: #1c1c1e;
        }}

        .tab-item.active::after {{
            content: '';
            position: absolute;
            bottom: -14px;
            left: 0;
            width: 100%;
            height: 3px;
            background-color: #6c5ce7;
            border-radius: 3px;
        }}

        .tab-page {{
            display: none;
            animation: fadeIn 0.3s ease-in-out;
        }}

        .tab-page.active {{
            display: block;
        }}

        .about-row {{
            display: flex;
            margin-bottom: 14px;
            font-size: 1rem;
        }}

        .about-label {{
            width: 130px;
            color: #8e8e93;
            font-weight: 600;
        }}

        .about-value {{
            color: #2c3e50;
            font-weight: 700;
            flex: 1;
        }}

        .stat-row {{
            display: flex;
            align-items: center;
            margin-bottom: 12px;
            font-size: 0.95rem;
        }}

        .stat-label {{
            width: 110px;
            color: #8e8e93;
            font-weight: 700;
        }}

        .stat-value {{
            width: 50px;
            font-weight: 800;
            color: #2c3e50;
        }}

        .stat-bar-bg {{
            flex: 1;
            height: 8px;
            background-color: #f0f0f5;
            border-radius: 10px;
            overflow: hidden;
        }}

        .stat-bar-fill {{
            height: 100%;
            border-radius: 10px;
            transition: width 0.6s ease;
        }}

        .pokedex-quote {{
            background: #f8f9fa;
            border-left: 5px solid {card_theme_color};
            padding: 16px 20px;
            border-radius: 10px;
            font-style: italic;
            color: #4a5568;
            font-size: 1rem;
            line-height: 1.6;
            margin-bottom: 15px;
        }}

        .prob-row {{
            display: flex;
            justify-content: space-between;
            padding: 10px 16px;
            background: #f8f9fa;
            border-radius: 10px;
            margin-bottom: 8px;
            font-size: 0.95rem;
            color: #2d3748;
        }}

        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(6px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
    </style>
    </head>
    <body>

    <div class="pokedex-app-container">
        <div class="pokeball-watermark"></div>

        <div class="app-header">
            <button class="back-btn" onclick="closeCard()">←</button>
            <span style="font-weight: 700; font-size: 1.1rem; opacity: 0.9;">PokéVision UI</span>
            <span style="font-size: 20px;">♡</span>
        </div>

        <div class="poke-title-section">
            <div>
                <div class="poke-name">{poke_data['name']}</div>
                <div class="type-badges-container">
                    {type_badges_html}
                </div>
            </div>
            <div class="poke-id">#{poke_data['id']:03d}</div>
        </div>

        <div class="artwork-container">
            <img src="{poke_data['image_url']}" class="artwork-img" alt="{poke_data['name']}">
        </div>

        <div class="sheet-container">
            <div class="sheet-tabs">
                <span class="tab-item active" onclick="switchTab('about', this)">Sobre</span>
                <span class="tab-item" onclick="switchTab('stats', this)">Estatísticas</span>
                <span class="tab-item" onclick="switchTab('pokedex', this)">Pokédex</span>
                <span class="tab-item" onclick="switchTab('ia', this)">Precisão IA</span>
            </div>

            <div id="tab-about" class="tab-page active">
                <div class="about-row">
                    <span class="about-label">Altura</span>
                    <span class="about-value">{poke_data['height']} m</span>
                </div>
                <div class="about-row">
                    <span class="about-label">Peso</span>
                    <span class="about-value">{poke_data['weight']} kg</span>
                </div>
                <div class="about-row">
                    <span class="about-label">Localização</span>
                    <span class="about-value">{poke_data['location']}</span>
                </div>
                <div class="about-row">
                    <span class="about-label">Fraquezas</span>
                    <span class="about-value" style="text-transform: capitalize;">{", ".join(poke_data['weaknesses'])}</span>
                </div>
            </div>

            <div id="tab-stats" class="tab-page">
                {stats_bars_html}
                <div class="stat-row" style="margin-top: 15px; border-top: 1px solid #f0f0f5; padding-top: 10px;">
                    <span class="stat-label">Total Base</span>
                    <span class="stat-value" style="color: #6c5ce7;">{total_stats}</span>
                </div>
            </div>

            <div id="tab-pokedex" class="tab-page">
                <div class="pokedex-quote">"{poke_data['pokedex_entry']}"</div>
            </div>

            <div id="tab-ia" class="tab-page">
                <div style="font-weight: 700; color: #8e8e93; font-size: 0.85rem; margin-bottom: 10px;">TOP PREDIÇÕES DA IA</div>
                {top5_html}
            </div>
        </div>
    </div>

    <script>
        function switchTab(tabName, element) {{
            document.querySelectorAll('.tab-item').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('.tab-page').forEach(el => el.classList.remove('active'));
            
            element.classList.add('active');
            document.getElementById('tab-' + tabName).classList.add('active');
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