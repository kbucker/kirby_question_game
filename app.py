## streamlit run app.py
## http://localhost:8501/

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
sheet = client.open_by_key("1zW6EmhzKKvpjkeIsbPasrFT6lPly8HWtpDxQS0YGZ9k")
light_df = pd.DataFrame(sheet.worksheet("Light Questions").get_all_records())
heavy_df = pd.DataFrame(sheet.worksheet("Heavy Questions").get_all_records())
light_questions = light_df['Question'].dropna().tolist()
heavy_questions = heavy_df['Question'].dropna().tolist()

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
        "button_text": "#B85C00",
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
            font-size: 28px !important;      /* Force larger font */
            font-weight: 900 !important;     /* Max bold */
            line-height: 32px !important;    /* Prevent cutoff */
            letter-spacing: 0.5px;
            text-shadow: 1px 1px 1px rgba(0,0,0,0.15);
            padding: 0.3rem 0.75rem !important;
            /* width: 100% !important;   <-- REMOVE THIS */
            width: auto !important;        /* Let button size to its content */
            min-width: 200px;              /* Optional: keeps nice tactile size */
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
def get_question(category):
    questions = light_questions if category == "Light" else heavy_questions
    available = [q for q in questions if q not in st.session_state.recent_questions]
    if not available:
        st.session_state.recent_questions.clear()
        available = questions
    question = random.choice(available)
    st.session_state.current_question = question
    st.session_state.question_type = category
    st.session_state.recent_questions.append(question)
    return category

# --- Buttons ---
clicked = None
col1, col2 = st.columns([1, 1])

st.markdown("""
<style>
/* Force 2-column grid and center it */
div[data-testid="stHorizontalBlock"] {
    display: grid !important;
    grid-template-columns: repeat(2, auto) !important;  /* shrink to fit content */
    column-gap: 20px !important;                        /* adjust gap */
    justify-content: center !important;                 /* center whole grid */
    margin-left: auto !important;
    margin-right: auto !important;
}

/* Kill Streamlit’s column padding */
div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {
    padding-left: 0 !important;
    padding-right: 0 !important;
}

div[data-testid="stVerticalBlock"] {
    gap: 0.5rem !important;   /* tighten vertical spacing */
}

</style>
""", unsafe_allow_html=True)

with col1:
    if st.button("🌞 Light Question", key="light"):
        clicked = get_question("Light")
with col2:
    if st.button("🧠 Heavy Question", key="heavy"):
        clicked = get_question("Heavy")

# --- Active theme (updated after click) ---
qtype = st.session_state.question_type
theme = themes.get(qtype, themes["Default"])

# --- Restyle buttons ---
light_theme = themes["Light"]
heavy_theme = themes["Heavy"]

st.markdown(f"""
<style>
    div[data-testid="stHorizontalBlock"] > div:first-child button {{
        background-color: {light_theme["button_bg"]} !important;
        color: {light_theme["button_text"]} !important;
        border: 2px solid {light_theme["button_border"]} !important;
        {"border: 3px solid " + theme['button_border'] + "; box-shadow: 0 0 14px 4px " + theme['button_border'] + ";" if qtype == "Light" else ""}
}}
    div[data-testid="stHorizontalBlock"] > div:nth-child(2) button {{
        background-color: {heavy_theme["button_bg"]} !important;
        color: {heavy_theme["button_text"]} !important;
        border: 2px solid {heavy_theme["button_border"]} !important;
        {"border: 3px solid " + theme['button_border'] + "; box-shadow: 0 0 14px 4px " + theme['button_border'] + ";" if qtype == "Heavy" else ""}

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
