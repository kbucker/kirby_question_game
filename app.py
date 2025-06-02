## terminal command to run app locally with local creds --> python -m streamlit run app.py

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
    st.session_state.question_type = None

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
    }
}

# --- Global Styling ---
st.markdown("""
    <style>
        body, .stApp {
            background-color: #2c2c2c !important;
            color: white !important;
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        h1 {
            text-align: center;
            color: white !important;
        }
        .question-box {
            text-align: center;
            max-width: 700px;
            margin: 2rem auto;
            padding: 2rem;
            font-size: 1.75rem;
            font-weight: bold;
            border-radius: 1rem;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }
        .button-container {
            display: flex;
            justify-content: center;
            gap: 2rem;
            margin-bottom: 2rem;
        }
    </style>
""", unsafe_allow_html=True)

# --- Render Header ---
st.markdown("<h1>🎲 Kirby’s Question Game</h1>", unsafe_allow_html=True)

# --- Generate Question ---
def get_question(category):
    questions = light_questions if category == "Light" else heavy_questions
    available = [q for q in questions if q not in st.session_state.recent_questions]
    if not available:
        st.session_state.recent_questions.clear()
        available = questions
    question = random.choice(available)
    st.session_state.current_question = question
    st.session_state.question_type = category

# --- Active Theme ---
light_active = st.session_state.question_type == "Light"
heavy_active = st.session_state.question_type == "Heavy"
light_styles = themes["Light"]
heavy_styles = themes["Heavy"]

# --- Button HTML Render ---
st.markdown('<div class="button-container">', unsafe_allow_html=True)
col1, col2 = st.columns([1, 1], gap="large")
with col1:
    light_clicked = st.button("🌞 Light Question", key="light_button")
with col2:
    heavy_clicked = st.button("🧠 Heavy Question", key="heavy_button")
st.markdown('</div>', unsafe_allow_html=True)

# --- Handle Click ---
if light_clicked:
    get_question("Light")
elif heavy_clicked:
    get_question("Heavy")

# --- Button Styling ---
st.markdown(f"""
    <style>
    div[data-testid="stButton"][key="light_button"] button {{
        background-color: {light_styles['button_bg']};
        color: {light_styles['button_text']};
        border: {'3px' if light_active else '2px'} solid {light_styles['button_border']};
        box-shadow: {'0 0 12px ' + light_styles['button_border'] if light_active else 'none'};
        font-weight: bold;
        border-radius: 10px;
        padding: 0.6rem 2rem;
        font-size: 1rem;
    }}
    div[data-testid="stButton"][key="heavy_button"] button {{
        background-color: {heavy_styles['button_bg']};
        color: {heavy_styles['button_text']};
        border: {'3px' if heavy_active else '2px'} solid {heavy_styles['button_border']};
        box-shadow: {'0 0 12px ' + heavy_styles['button_border'] if heavy_active else 'none'};
        font-weight: bold;
        border-radius: 10px;
        padding: 0.6rem 2rem;
        font-size: 1rem;
    }}
    </style>
""", unsafe_allow_html=True)

# --- Show Question Output ---
if st.session_state.current_question:
    theme = themes[st.session_state.question_type]
    st.markdown(
        f"""
        <div class="question-box" style="
            background-color: {theme['card_bg']};
            color: {theme['text_color']};
            border: 2px solid {theme['border_color']};
        ">
            {st.session_state.current_question}
        </div>
        """,
        unsafe_allow_html=True
    )
else:
    st.markdown(
        "<div style='text-align:center; margin-top:2rem; color:#aaa;'>Click a question type above to begin.</div>",
        unsafe_allow_html=True
    )