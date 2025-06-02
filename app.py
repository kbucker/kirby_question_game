import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import random
from collections import deque

## python -m streamlit run app.py

# --- Google Sheets API Setup ---
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)

# --- Open Google Sheet by ID ---
spreadsheet_id = "1zW6EmhzKKvpjkeIsbPasrFT6lPly8HWtpDxQS0YGZ9k"
sheet = client.open_by_key(spreadsheet_id)

# --- Load Light and Heavy Questions ---
light_df = pd.DataFrame(sheet.worksheet("Light Questions").get_all_records())
heavy_df = pd.DataFrame(sheet.worksheet("Heavy Questions").get_all_records())

light_questions = light_df['Question'].dropna().tolist()
heavy_questions = heavy_df['Question'].dropna().tolist()

# --- Streamlit UI Setup ---
st.set_page_config(page_title="Kirby's Question Game", layout="wide")
st.markdown(
    """
    <style>
        .question-box {
            font-size: 2rem;
            text-align: center;
            padding: 3rem;
        }
        .stButton>button {
            font-size: 1.2rem;
            width: 100%;
            padding: 1rem;
        }
        .button-container {
            position: fixed;
            bottom: 1rem;
            left: 0;
            width: 100%;
            display: flex;
            justify-content: center;
            gap: 2rem;
            z-index: 999;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Initialize recent question memory
if 'recent_questions' not in st.session_state:
    st.session_state.recent_questions = deque(maxlen=50)

# Question selection logic
def get_question(category):
    questions = light_questions if category == "Light" else heavy_questions
    available = [q for q in questions if q not in st.session_state.recent_questions]
    if not available:
        st.session_state.recent_questions.clear()
        available = questions
    question = random.choice(available)
    st.session_state.recent_questions.append(question)
    return question

# Display the current question
st.write("<div class='question-box'>", unsafe_allow_html=True)
if 'current_question' in st.session_state:
    st.markdown(f"### 💬 {st.session_state.current_question}")
else:
    st.markdown("### 💬 Click a button below to get your first question!")
st.write("</div>", unsafe_allow_html=True)

# Bottom-aligned buttons
st.markdown("<div class='button-container'>", unsafe_allow_html=True)

col1, col2 = st.columns([1, 1])
with col1:
    if st.button("🌞 Light Question"):
        st.session_state.current_question = get_question("Light")
with col2:
    if st.button("🌚 Heavy Question"):
        st.session_state.current_question = get_question("Heavy")

st.markdown("</div>", unsafe_allow_html=True)