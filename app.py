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
    sexy_df  = pd.DataFrame(sheet.worksheet("Sexy Questions").get_all_records())
    who_df   = pd.DataFrame(sheet.worksheet("Who Here").get_all_records())

    return {
        "Light":    light_df['Question'].dropna().tolist(),
        "Heavy":    heavy_df['Question'].dropna().tolist(),
        "Sexy":     sexy_df['Question'].dropna().tolist(),
        "Who Here": who_df['Question'].dropna().tolist()
    }

# only shows spinner the *first* time cache is empty/expired
with st.spinner("Loading questions..."):
    all_questions = load_questions()

light_questions    = all_questions["Light"]
heavy_questions    = all_questions["Heavy"]
sexy_questions     = all_questions["Sexy"]
who_here_questions = all_questions["Who Here"]

# --- Session State ---
if 'recent_questions' not in st.session_state:
    st.session_state.recent_questions = deque(maxlen=50)
if 'current_question' not in st.session_state:
    st.session_state.current_question = ""
if 'question_type' not in st.session_state:
    st.session_state.question_type = "None"

# --- Themes ---
themes = {
    "Light": {
        "card_bg": "#FFEFCB",
        "text_color": "#F68B1E",
        "border_color": "#B85C00",
        "button_bg": "#FFD580",
        "button_text": "#8F4600",
        "button_border": "#B85C00"
    },
    "Heavy": {
        "card_bg": "#FFD6DC",
        "text_color": "#CC0000",
        "border_color": "#990000",
        "button_bg": "#FFB3C6",
        "button_text": "#990000",
        "button_border": "#990000"
    },
    # New purple theme (Sexy Questions)
    "Sexy": {
        "card_bg": "#F4ECFF",
        "text_color": "#730FC3",   # deep purple
        "border_color": "#730FC3",
        "button_bg": "#AB91D5",   # light purple
        "button_text": "#5C0A9A",
        "button_border": "#730FC3"
    },
    # New blue theme (Who Here)
    "Who Here": {
        "card_bg": "#EAF8FF",
        "text_color": "#2596BE",  # deep blue
        "border_color": "#2596BE",
        "button_bg": "#A2CCDC",   # light blue
        "button_text": "#175D7A",
        "button_border": "#2596BE"
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
            padding: 0.3rem 0.75rem !important;
            width: auto !important;
            min-width: 200px;
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
    elif category == "Sexy":
        questions = sexy_questions
    elif category == "Who Here":
        questions = who_here_questions
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
top_left_col, top_right_col = st.columns([1, 1])
# Row 2: Sexy / Who Here
bottom_left_col, bottom_right_col = st.columns([1, 1])

with top_left_col:
    if st.button("🌞 Light Question", key="light"):
        get_question("Light")

with top_right_col:
    if st.button("🧠 Heavy Question", key="heavy"):
        get_question("Heavy")

with bottom_left_col:
    if st.button("🫦 Sexy Question BETA", key="sexy"):
        get_question("Sexy")

with bottom_right_col:
    if st.button("🔄 Who Here... BETA", key="who_here"):
        get_question("Who Here")

# --- Active theme (updated after click) ---
qtype = st.session_state.question_type
theme = themes.get(qtype, themes["Default"])

# --- Restyle buttons for all four types ---
light_theme = themes["Light"]
heavy_theme = themes["Heavy"]
sexy_theme  = themes["Sexy"]
who_theme   = themes["Who Here"]

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

    /* Sexy button */
    .st-key-sexy .stButton button {{
        background-color: {sexy_theme["button_bg"]} !important;
        color: {sexy_theme["button_text"]} !important;
        border: 2px solid {sexy_theme["button_border"]} !important;
        {"border: 3px solid " + sexy_theme["button_border"] + "; box-shadow: 0 0 14px 4px " + sexy_theme["button_border"] + ";" if qtype == "Sexy" else ""}
    }}

    /* Who Here button */
    .st-key-who_here .stButton button {{
        background-color: {who_theme["button_bg"]} !important;
        color: {who_theme["button_text"]} !important;
        border: 2px solid {who_theme["button_border"]} !important;
        {"border: 3px solid " + who_theme["button_border"] + "; box-shadow: 0 0 14px 4px " + who_theme["button_border"] + ";" if qtype == "Who Here" else ""}
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
        Click a question option above to begin.
        </div>""",
        unsafe_allow_html=True
    )

## Reminders for local running
## streamlit run app.py
## http://localhost:8501/