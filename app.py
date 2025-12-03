import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import random
from collections import deque
import os
import json

# --- Auth Setup ---
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
if "GOOGLE_CREDENTIALS" in os.environ:
    creds_dict = json.loads(os.environ["GOOGLE_CREDENTIALS"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
else:
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)

# --- Load questions ---
@st.cache_data(ttl=3600)  # cache questions for 1 hour
def load_questions():
    sheet = client.open_by_key("1zW6EmhzKKvpjkeIsbPasrFT6lPly8HWtpDxQS0YGZ9k")

    light_df = pd.DataFrame(sheet.worksheet("Light Questions").get_all_records())
    heavy_df = pd.DataFrame(sheet.worksheet("Heavy Questions").get_all_records())
    kinky_df  = pd.DataFrame(sheet.worksheet("Kinky").get_all_records())
    wholesome_df = pd.DataFrame(sheet.worksheet("Wholesome").get_all_records())
    who_here_df   = pd.DataFrame(sheet.worksheet("Who Here Is").get_all_records())
    drink_if_df = pd.DataFrame(sheet.worksheet("Drink If You").get_all_records())

    return {
        "Light":    light_df['Question'].dropna().tolist(),
        "Heavy":    heavy_df['Question'].dropna().tolist(),
        "Kinky":     kinky_df['Question'].dropna().tolist(),
        "Wholesome": wholesome_df['Question'].dropna().tolist(),
        "Who_Here": who_here_df['Question'].dropna().tolist(),
        "Drink_If": drink_if_df['Question'].dropna().tolist()
    }

# only shows spinner the *first* time cache is empty/expired
with st.spinner("Loading questions..."):
    all_questions = load_questions()

light_questions    = all_questions["Light"]
heavy_questions    = all_questions["Heavy"]
kinky_questions     = all_questions["Kinky"]
wholesome_questions = all_questions["Wholesome"]
who_here_questions = all_questions["Who_Here"]
drink_if_questions = all_questions["Drink_If"]

# --- Session State ---
if 'recent_questions' not in st.session_state:
    st.session_state.recent_questions = deque(maxlen=100)
if 'current_question' not in st.session_state:
    st.session_state.current_question = ""
if 'question_type' not in st.session_state:
    st.session_state.question_type = "None"

# --- Themes ---
themes = {
    "Light": {  # Yellow
        "card_bg": "#FFF7D6",
        "text_color": "#C28A00",
        "border_color": "#D9A400",
        "button_bg": "#FFEEA8",
        "button_text": "#8B6500",
        "button_border": "#D9A400"
    },
    "Heavy": {  # Orange
        "card_bg": "#FFE7D6",
        "text_color": "#D36A1C",
        "border_color": "#D36A1C",
        "button_bg": "#FFCCAF",
        "button_text": "#A84E14",
        "button_border": "#D36A1C"
    },
    "Kinky": {  # Pink
        "card_bg": "#FFEAF4",
        "text_color": "#D81B77",
        "border_color": "#D81B77",
        "button_bg": "#FFB6E5",
        "button_text": "#A31258",
        "button_border": "#D81B77"
    },
    "Wholesome": {  # Red
        "card_bg": "#FFA8A8",
        "text_color": "#C21807",
        "border_color": "#C21807",
        "button_bg": "#FFA8A8",
        "button_text": "#8E0000",
        "button_border": "#C21807"
    },
    "Who_Here": {  # Blue
        "card_bg": "#E6F2FF",
        "text_color": "#1E63B4",
        "border_color": "#1E63B4",
        "button_bg": "#A9C9FF",
        "button_text": "#124170",
        "button_border": "#1E63B4"
    },
    "Drink_If": {  # Green
        "card_bg": "#E6F7EC",
        "text_color": "#2E7D32",
        "border_color": "#2E7D32",
        "button_bg": "#B8E6C2",
        "button_text": "#1F5422",
        "button_border": "#2E7D32"
    },
    "Default": {
        "card_bg": "#2c2c2c",
        "text_color": "#ffffff",
        "border_color": "#444444",
        "button_bg": "#444444",
        "button_text": "#ffffff",
        "button_border": "#666666"
    }
}

# --- Always-on charcoal background and title ---
st.markdown("""
    <style>
        /* Remove the anchor link icon next to Streamlit headings to fix the centering of the title on mobile */
        .stMarkdown .css-10trblm.e1nzilvr1 a {
            display: none !important;
        }
        body, .stApp {
            background-color: #2c2c2c !important;
            color: #ffffff !important;
        }
        h3 {
            color: #ffffff !important;
            text-align: center;
            font-size: 0.5rem;
            line-height: 1.2;
            margin-bottom: 1rem;
        }
        .main-title {
            text-align: center;
            margin: 0 auto;
            font-size: 1.5rem;
            color: #ffffff !important;
        }
        .stButton > button {
            font-size: 28px !important;
            font-weight: 900 !important;
            line-height: 32px !important;
            letter-spacing: 0.5px;
            text-shadow: 1px 1px 1px rgba(0,0,0,0.15);
            padding: 0.3rem 0.3rem !important;
            width: auto !important;
            min-width: 185px;
            border-radius: 12px;
            margin-bottom: 0.1rem;
            transition: all 0.3s ease;
            display: flex;
            justify-content: center;
            align-items: center;
            text-align: center;
        }
    </style>
""", unsafe_allow_html=True)

# --- Title ---
st.markdown("<h3 class='main-title'>🃏 Kirby’s Question Game</h3>", unsafe_allow_html=True)

# --- Choose a question ---
def get_question(category: str):
    if category == "Light":
        questions = light_questions
    elif category == "Heavy":
        questions = heavy_questions
    elif category == "Kinky":
        questions = kinky_questions
    elif category == "Wholesome":
        questions = wholesome_questions
    elif category == "Who_Here":
        questions = who_here_questions
    elif category == "Drink_If":
        questions = drink_if_questions
    else:
        questions = []

    if not questions:
        return

    available = [q for q in questions if q not in st.session_state.recent_questions]
    if not available:
        st.session_state.recent_questions.clear()
        available = questions

    question = random.choice(available)
    st.session_state.current_question = question
    st.session_state.question_type = category
    st.session_state.recent_questions.append(question)

# --- Layout tweaks for the button rows ---
st.markdown("""
<style>
/* Force 2-column grid and center each row of columns */
div[data-testid="stHorizontalBlock"] {
    display: grid !important;
    grid-template-columns: repeat(2, auto) !important;
    column-gap: 20px !important;
    justify-content: center !important;
    margin-left: auto !important;
    margin-right: auto !important;
}

/* Kill Streamlit’s column padding */
div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {
    padding-left: 0 !important;
    padding-right: 0 !important;
}

div[data-testid="stVerticalBlock"] {
    gap: 0.5rem !important;
}
</style>
""", unsafe_allow_html=True)

# --- Buttons: 2x2 grid (two horizontal blocks / rows) ---
# Row 1: Light / Heavy
row_1_col_1, row_1_col_2 = st.columns([1, 1])
# Row 2: Kinky / Wholesome
row_2_col_1, row_2_col_2 = st.columns([1, 1])
# Row 3: Who Here Is / Drink If You've
row_3_col_1, row_3_col_2 = st.columns([1, 1])

with row_1_col_1:
    if st.button("🌞 Light Question", key="light"):
        get_question("Light")

with row_1_col_2:
    if st.button("🔥 Heavy Question", key="heavy"):
        get_question("Heavy")

with row_2_col_1:
    if st.button("🫦 Kinky", key="kinky"):
        get_question("Kinky")

with row_2_col_2:
    if st.button("❤️ Wholesome", key="wholesome"):
        get_question("Wholesome")

with row_3_col_1:
    if st.button("🔄 Who Here Is", key="who_here"):
        get_question("Who_Here")

with row_3_col_2:
    if st.button("😇 Drink If You've", key="drink_if"):
        get_question("Drink_If")

# --- Active theme (updated after click) ---
qtype = st.session_state.question_type
theme = themes.get(qtype, themes["Default"])

# --- Restyle buttons for all four types ---
light_theme = themes["Light"]
heavy_theme = themes["Heavy"]
kinky_theme  = themes["Kinky"]
wholesome_theme = themes["Wholesome"]
who_here_theme   = themes["Who_Here"]
drink_if_theme = themes["Drink_If"]

st.markdown(f"""
<style>
    /* Light button */
    .st-key-light .stButton button {{
        background-color: {light_theme["button_bg"]} !important;
        color: {light_theme["button_text"]} !important;
        border: 2px solid {light_theme["button_border"]} !important;
        {"border: 3px solid " + light_theme["button_border"] + "; box-shadow: 0 0 14px 4px " + light_theme["button_border"] + ";" if qtype == "Light" else ""}
    }}

    /* Heavy button */
    .st-key-heavy .stButton button {{
        background-color: {heavy_theme["button_bg"]} !important;
        color: {heavy_theme["button_text"]} !important;
        border: 2px solid {heavy_theme["button_border"]} !important;
        {"border: 3px solid " + heavy_theme["button_border"] + "; box-shadow: 0 0 14px 4px " + heavy_theme["button_border"] + ";" if qtype == "Heavy" else ""}
    }}

    /* Kinky button */
    .st-key-kinky .stButton button {{
        background-color: {kinky_theme["button_bg"]} !important;
        color: {kinky_theme["button_text"]} !important;
        border: 2px solid {kinky_theme["button_border"]} !important;
        {"border: 3px solid " + kinky_theme["button_border"] + "; box-shadow: 0 0 14px 4px " + kinky_theme["button_border"] + ";" if qtype == "Kinky" else ""}
    }}
    
    /* Give A Wholesome button */
    .st-key-wholesome .stButton button {{
        background-color: {wholesome_theme["button_bg"]} !important;
        color: {wholesome_theme["button_text"]} !important;
        border: 2px solid {wholesome_theme["button_border"]} !important;
        {"border: 3px solid " + wholesome_theme["button_border"] + "; box-shadow: 0 0 14px 4px " + wholesome_theme["button_border"] + ";" if qtype == "Wholesome" else ""}
    }}
    
    /* Who Here button */
    .st-key-who_here .stButton button {{
        background-color: {who_here_theme["button_bg"]} !important;
        color: {who_here_theme["button_text"]} !important;
        border: 2px solid {who_here_theme["button_border"]} !important;
        {"border: 3px solid " + who_here_theme["button_border"] + "; box-shadow: 0 0 14px 4px " + who_here_theme["button_border"] + ";" if qtype == "Who_Here" else ""}
    }}
    
    /* Drink If You've button */
    .st-key-drink_if .stButton button {{
        background-color: {drink_if_theme["button_bg"]} !important;
        color: {drink_if_theme["button_text"]} !important;
        border: 2px solid {drink_if_theme["button_border"]} !important;
        {"border: 3px solid " + drink_if_theme["button_border"] + "; box-shadow: 0 0 14px 4px " + drink_if_theme["button_border"] + ";" if qtype == "Drink_If" else ""}
    }}
</style>
""", unsafe_allow_html=True)


# --- Output question card ---
if st.session_state.current_question:
    st.markdown(
        f"""
        <div style='background-color: {theme['card_bg']};
                    color: {theme['text_color']};
                    padding: 2rem;
                    margin-top: 1rem;
                    border-radius: 1rem;
                    font-size: 2rem;
                    font-weight: bold;
                    text-align: center;
                    max-width: 700px;
                    margin-left: auto;
                    margin-right: auto;
                    border: 2px solid {theme['border_color']};
                    box-shadow: 0 0 10px rgba(0,0,0,0.1);'>
            {st.session_state.current_question}
        </div>
        """,
        unsafe_allow_html=True
    )
else:
    st.markdown(
        """<div style='margin-top: 1rem; text-align: center; font-size: 1.5rem; color: #999;'>
        Click a question option above to begin<br>
        <br>
        <strong style="color: white;"><b>Patch 3.0 Now Live!</b><br></strong>
        4 new categories!<br>
        Much faster response time!<br>
        New questions in each category<br>
        All new categories are still in BETA
        </div>""",
        unsafe_allow_html=True
    )

## Reminders for local running
## streamlit run app.py
## http://localhost:8501/