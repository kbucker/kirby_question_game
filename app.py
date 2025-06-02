import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import random
from collections import deque

# --- Google Sheets Setup ---
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)

# Open your Google Sheet by name
sheet = client.open("Kirby's Question Game")  # <-- Update this to match your actual sheet title

# Read "Light" and "Heavy" tabs into lists
light_df = pd.DataFrame(sheet.worksheet("Light").get_all_records())
heavy_df = pd.DataFrame(sheet.worksheet("Heavy").get_all_records())

light_questions = light_df['Question'].dropna().tolist()
heavy_questions = heavy_df['Question'].dropna().tolist()

# --- Streamlit Frontend ---
st.set_page_config(page_title="Kirby's Question Game", layout="centered")
st.title("🎲 Kirby’s Question Game")

# Track last 50 questions
if 'recent_questions' not in st.session_state:
    st.session_state.recent_questions = deque(maxlen=50)

def get_question(category):
    questions = light_questions if category == "Light" else heavy_questions
    available = [q for q in questions if q not in st.session_state.recent_questions]
    if not available:
        st.session_state.recent_questions.clear()
        available = questions
    question = random.choice(available)
    st.session_state.recent_questions.append(question)
    return question

col1, col2 = st.columns(2)

if col1.button("🌞 Light Question"):
    st.session_state.current_question = get_question("Light")

if col2.button("🌚 Heavy Question"):
    st.session_state.current_question = get_question("Heavy")

if 'current_question' in st.session_state:
    st.markdown(f"### 💬 {st.session_state.current_question}")
