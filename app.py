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
        "card_bg": "#ffffff",
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
        body, .stApp {
            background-color: #2c2c2c !important;
            color: #ffffff !important;
        }
        h1 {
            color: #ffffff !important;
            text-align: center;
        }
    </style>
""", unsafe_allow_html=True)

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

# --- Handle button click ---
clicked = None
col1, col2 = st.columns([1, 1])
with col1:
    if st.button("🌞 Light Question", key="light"):
        clicked = "Light"
with col2:
    if st.button("🧠 Heavy Question", key="heavy"):
        clicked = "Heavy"
if clicked:
    get_question(clicked)

# --- Active theme ---
qtype = st.session_state.question_type
theme = themes.get(qtype, themes["Default"])

# --- Style Buttons ---
highlight_style = """
    border: 3px solid {border};
    box-shadow: 0 0 8px {border};
"""
st.markdown(f"""
    <style>
        .stButton > button {{
            width: 100%;
            padding: 0.75rem;
            font-size: 1.1rem;
            font-weight: bold;
            border-radius: 10px;
            margin-bottom: 0.5rem;
            transition: all 0.3s ease;
        }}
        div.stButton > button:first-child {{
            background-color: {themes["Light"]["button_bg"]};
            color: {themes["Light"]["button_text"]};
            border: 2px solid {themes["Light"]["button_border"]};
            {"border: 3px solid " + themes["Light"]["button_border"] + "; box-shadow: 0 0 10px " + themes["Light"]["button_border"] + ";" if qtype == "Light" else ""}
        }}
        div.stButton > button:nth-child(1) {{
            background-color: {themes["Heavy"]["button_bg"]};
            color: {themes["Heavy"]["button_text"]};
            border: 2px solid {themes["Heavy"]["button_border"]};
            {"border: 3px solid " + themes["Heavy"]["button_border"] + "; box-shadow: 0 0 10px " + themes["Heavy"]["button_border"] + ";" if qtype == "Heavy" else ""}
        }}
    </style>
""", unsafe_allow_html=True)

# --- Title ---
st.markdown("<h1>🎲 Kirby’s Question Game</h1>", unsafe_allow_html=True)

# --- Output question card ---
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
            border: 2px solid {theme['border_color']};
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        '>
            {st.session_state.current_question}
        </div>
        """,
        unsafe_allow_html=True
    )
else:
    st.markdown(
        "<div style='margin-top: 3rem; text-align: center; font-size: 1.2rem; color: #999;'>"
        "Click a question type above to begin."
        "</div>",
        unsafe_allow_html=True
    )
