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
    kinky_df  = pd.DataFrame(sheet.worksheet("Kinky Questions").get_all_records())
    compliment_df = pd.DataFrame(sheet.worksheet("Give A Compliment").get_all_records())
    who_here_df   = pd.DataFrame(sheet.worksheet("Who Here Is").get_all_records())
    drink_if_df = pd.DataFrame(sheet.worksheet("Drink If You've").get_all_records())

    return {
        "Light":    light_df['Question'].dropna().tolist(),
        "Heavy":    heavy_df['Question'].dropna().tolist(),
        "Kinky":     kinky_df['Question'].dropna().tolist(),
        "Compliment": compliment_df['Question'].dropna().tolist(),
        "Who_Here": who_here_df['Question'].dropna().tolist(),
        "Drink_If": drink_if_df['Question'].dropna().tolist()
    }

# only shows spinner the *first* time cache is empty/expired
with st.spinner("Loading questions..."):
    all_questions = load_questions()

light_questions    = all_questions["Light"]
heavy_questions    = all_questions["Heavy"]
kinky_questions     = all_questions["Kinky"]
compliment_questions = all_questions["Compliment"]
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
# themes = {
#     "Light": {
#         "card_bg": "#FFEFCB",
#         "text_color": "#F68B1E",
#         "border_color": "#B85C00",
#         "button_bg": "#FFD580",
#         "button_text": "#8F4600",
#         "button_border": "#B85C00"
#     },
#     "Heavy": {
#         "card_bg": "#FFF1E6",      # pale peach/orange background
#         "text_color": "#D35400",   # deep pumpkin orange
#         "border_color": "#D35400",
#         "button_bg": "#FFC9A6",    # soft pastel orange button
#         "button_text": "#A84300",  # deeper orange for high readability
#         "button_border": "#D35400"
#     },
#     "Kinky": {
#         "card_bg": "#FFD6DC",
#         "text_color": "#CC0000",
#         "border_color": "#990000",
#         "button_bg": "#FFB3C6",
#         "button_text": "#990000",
#         "button_border": "#990000"
#     },
#     "Compliment": {
#         "card_bg": "#E6F7E6",      # pale soft green
#         "text_color": "#2E7D32",   # warm forest green
#         "border_color": "#2E7D32",
#         "button_bg": "#BDE8BD",    # pale mint/green button
#         "button_text": "#2E7D32",  # strong but friendly forest green
#         "button_border": "#2E7D32"
#     },
#     "Who_Here": {
#         "card_bg": "#EAF8FF",
#         "text_color": "#2596BE",
#         "border_color": "#2596BE",
#         "button_bg": "#A2CCDC",
#         "button_text": "#175D7A",
#         "button_border": "#2596BE"
#     },
#     "Default": {
#         "card_bg": "#2c2c2c",
#         "text_color": "#ffffff",
#         "border_color": "#444444",
#         "button_bg": "#444444",
#         "button_text": "#ffffff",
#         "button_border": "#666666"
#     },
#     "Drink_If": {
#         "card_bg": "#F4ECFF",
#         "text_color": "#730FC3",
#         "border_color": "#730FC3",
#         "button_bg": "#AB91D5",
#         "button_text": "#5C0A9A",
#         "button_border": "#730FC3"
#     }
# }

# themes = {
#     "Light": {  # Yellow
#         "card_bg": "#FFF9DC",      # very pale yellow
#         "text_color": "#C28A00",   # warm golden yellow
#         "border_color": "#C28A00",
#         "button_bg": "#FFE48A",    # soft pastel yellow
#         "button_text": "#8B6500",  # deeper golden-brown for readability
#         "button_border": "#C28A00"
#     },
#     "Heavy": {  # Orange
#         "card_bg": "#FFE9DC",      # pale peach/orange
#         "text_color": "#D35400",   # strong orange
#         "border_color": "#D35400",
#         "button_bg": "#FFBE99",    # pastel orange
#         "button_text": "#A84300",  # deeper orange
#         "button_border": "#D35400"
#     },
#     "Kinky": {  # Red
#         "card_bg": "#FFE5EA",      # very soft red/pink
#         "text_color": "#C21807",   # rich red
#         "border_color": "#C21807",
#         "button_bg": "#FFB3BF",    # light rosy red
#         "button_text": "#8E0000",  # deep red for contrast
#         "button_border": "#C21807"
#     },
#     "Compliment": {  # Pink
#         "card_bg": "#FFE8F4",      # pale pink
#         "text_color": "#C2185B",   # raspberry pink
#         "border_color": "#C2185B",
#         "button_bg": "#FFB6DE",    # pastel pink
#         "button_text": "#8B1340",  # darker berry pink
#         "button_border": "#C2185B"
#     },
#     "Who_Here": {  # Blue
#         "card_bg": "#E6F2FF",      # very light blue
#         "text_color": "#1E63B4",   # strong medium blue
#         "border_color": "#1E63B4",
#         "button_bg": "#A9C9FF",    # pastel sky blue
#         "button_text": "#124170",  # deep navy-ish blue
#         "button_border": "#1E63B4"
#     },
#     "Drink_If": {  # Green
#         "card_bg": "#E6F7EC",      # light minty green
#         "text_color": "#2E7D32",   # rich green
#         "border_color": "#2E7D32",
#         "button_bg": "#B8E6C2",    # pastel green
#         "button_text": "#1F5422",  # darker forest green
#         "button_border": "#2E7D32"
#     },
#     "Default": {
#         "card_bg": "#2c2c2c",
#         "text_color": "#ffffff",
#         "border_color": "#444444",
#         "button_bg": "#444444",
#         "button_text": "#ffffff",
#         "button_border": "#666666"
#     }
# }

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
    "Compliment": {  # Red
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
    elif category == "Kinky":
        questions = kinky_questions
    elif category == "Compliment":
        questions = compliment_questions
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
# Row 2: Kinky / Give A Compliment
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
    if st.button("🫦 Kinky Question", key="kinky"):
        get_question("Kinky")

with row_2_col_2:
    if st.button("❤️ Give A Compliment", key="compliment"):
        get_question("Compliment")

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
compliment_theme = themes["Compliment"]
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
    
    /* Give A Compliment button */
    .st-key-compliment .stButton button {{
        background-color: {compliment_theme["button_bg"]} !important;
        color: {compliment_theme["button_text"]} !important;
        border: 2px solid {compliment_theme["button_border"]} !important;
        {"border: 3px solid " + compliment_theme["button_border"] + "; box-shadow: 0 0 14px 4px " + compliment_theme["button_border"] + ";" if qtype == "Compliment" else ""}
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
        2 new question categories!<br>
        2 new party style modes!<br>
        Much faster response time!<br>
        New questions in each category<br>
        All new categories are still in BETA
        </div>""",
        unsafe_allow_html=True
    )

## Reminders for local running
## streamlit run app.py
## http://localhost:8501/