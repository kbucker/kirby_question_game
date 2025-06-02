import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import random
from collections import deque
import os
import json

## python -m streamlit run app.py

# --- Auth Setup (local vs cloud) ---
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

# --- Initialize session state ---
if 'recent_questions' not in st.session_state:
    st.session_state.recent_questions = deque(maxlen=50)
if 'current_question' not in st.session_state:
    st.session_state.current_question = ""
if 'question_type' not in st.session_state:
    st.session_state.question_type = "Default"

# --- Themes ---
themes = {
    "Default": {
        "page_bg": "#2c2c2c",
        "card_bg": "#2c2c2c",
        "text_color": "#ffffff",
        "button_bg": "#444444",
        "button_text": "#ffffff"
    },
    "Light": {
        "page_bg": "#FFF7DC",
        "card_bg": "#FFEFCB",
        "text_color": "#F68B1E",
        "button_bg": "#FFD580",
        "button_text": "#B85C00"
    },
    "Heavy": {
        "page_bg": "#FFE4E6",
        "card_bg": "#FFD6DC",
        "text_color": "#CC0000",
        "button_bg": "#FFB3C6",
        "button_text": "#990000"
    }
}

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

# --- Handle Button Clicks BEFORE Rendering ---
clicked = None
col1, col2 = st.columns([1, 1])
with col1:
    if st.button("🌞 Light Question", key="light_button"):
        clicked = "Light"
with col2:
    if st.button("🧠 Heavy Question", key="heavy_button"):
        clicked = "Heavy"
if clicked:
    get_question(clicked)

# --- Apply theme now ---
theme = themes.get(st.session_state.question_type, themes["Default"])
page_style = f"""
    <style>
        body, .stApp {{
            background-color: {theme['page_bg']};
            color: {theme['text_color']};
        }}
        .stButton > button {{
            width: 100%;
            font-size: 1.2rem;
            padding: 0.8rem;
            margin-bottom: 0.5rem;
            border-radius: 10px;
            font-weight: bold;
            background-color: {theme['button_bg']};
            color: {theme['button_text']};
            border: none;
        }}
        .stButton > button:hover {{
            filter: brightness(0.95);
        }}
    </style>
"""
st.markdown(page_style, unsafe_allow_html=True)

# --- Title ---
st.markdown("<h1 style='text-align: center; margin-top: 1rem;'>🎲 Kirby’s Question Game</h1>", unsafe_allow_html=True)

# --- Display Question Card ---
if st.session_state.current_question:
    st.markdown(
        f"""
        <div style='
            background-color: {theme['card_bg']};
            color: {theme['text_color']};
            padding: 2rem;
            margin-top: 3rem;
            border-radius: 1rem;
            font-size: 2rem;
            font-weight: bold;
            text-align: center;
            max-width: 700px;
            margin-left: auto;
            margin-right: auto;
            box-shadow: 0 0 15px rgba(0, 0, 0, 0.1);
        '>
            {st.session_state.current_question}
        </div>
        """,
        unsafe_allow_html=True
    )
else:
    st.markdown(
        f"<div style='margin-top: 3rem; text-align: center; font-size: 1.2rem; color: {theme['text_color']}70;'>"
        "Click a question type above to begin."
        "</div>",
        unsafe_allow_html=True
    )
