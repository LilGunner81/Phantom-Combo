import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# --- CONFIG & STYLING ---
st.set_page_config(page_title="The Phantom Combo", page_icon="👻")

st.markdown("""
    <style>
    .stApp { background-color: #121212; color: #FFFFFF; }
    .stButton>button { width: 100%; background-color: #06C167 !important; color: #121212 !important; font-weight: bold; border-radius: 8px; border: none; }
    .stTextInput>div>div>input, .stNumberInput>div>div>input, .stSelectbox>div>div>div {
        background-color: #2a2a2a !important; color: white !important; border: 1px solid #444 !important;
    }
    h2, h3 { color: #06C167 !important; text-align: center; }
    .score-box { text-align: center; font-size: 3.5rem; font-weight: bold; color: #06C167; margin-top: -10px; }
    .player-label { font-size: 1.2rem; font-weight: bold; color: #FFFFFF; text-align: center; display: block; }
    </style>
    """, unsafe_allow_html=True)

# --- GOOGLE SHEETS CONNECTION ---
conn = st.connection("gsheets", type=GSheetsConnection)

# Fetch data safely
try:
    df = conn.read()
except:
    # Creates a blank dataframe if the sheet is totally empty
    df = pd.DataFrame(columns=["Name", "Score"])

# --- GAME LOGIC ---
FOOD_CATEGORIES = ["Italian", "Sushi", "Mediterranean", "Eastern Asian", "Sandwiches", "Asian", "Mexican", "South Asian", "Chicken", "Shop and Deliver", "Liquor", "Other"]
WIN_LIMIT = 25

# Check if we already have players set up in the Sheet
has_players = len(df) >= 2 and not df['Name'].isnull().all()

# --- SCREEN 1: SETUP (Only runs if Sheet is empty) ---
if not has_players:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("Logo.png", use_container_width=True)
    
    st.write("<p style='text-align: center;'>New Tournament: Enter names to save to the Cloud.</p>", unsafe_allow_html=True)
    p1_input = st.text_input("Player 1 Name")
    p2_input = st.text_input("Player 2 Name")

    if st.button("Initialize Tournament"):
        if p1_input and p2_input:
            new_data = pd.DataFrame([
                {"Name": p1_input, "Score": 0},
                {"Name": p2_input, "Score": 0}
            ])
            conn.update(data=new_data)
            st.rerun()
        else:
            st.error("Please enter both names.")

# --- SCREEN 2: THE GAME ---
else:
    p1_name, p1_score = df.iloc[0]['Name'], int(df.iloc[0]['Score'])
    p2_name, p2_score = df.iloc[1]['Name'], int(df.iloc[1]['Score'])

    # Winner Check
    if p1_score >= WIN_LIMIT or p2_score >= WIN_LIMIT:
        winner = p1_name if p1_score >= WIN_LIMIT else p2_name
        st.balloons()
        st.markdown(f"<h1 style='text-align:center;'>🏆 {winner} WINS! 🏆</h1>", unsafe_allow_html=True)
        st.image("Logo.png", width=300)
        if st.button("Reset Tournament"):
            df['Score'] = 0
            conn.update(data=df)
            st.rerun()
    else:
        # Standard Game Header
        c_logo, c_score = st.columns([1, 3])
        with c_logo:
            st.image("Logo.png", width=100)
        with c_score:
            st.markdown(f'<div class="score-box">{p1_score} — {p2_score}</div>', unsafe_allow_html=True)
        
        st.markdown(f"<h3>{p1_name} vs {p2_name}</h3>", unsafe_allow_html=True)

        # --- GUESSES & SUBMIT (Your existing logic) ---
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown(f'<p class="player-label">{p1_name}</p>', unsafe_allow_html=True)
            p1_p = st.number_input("Price Guess", key="p1p", format="%.2f")
            p1_c = st.selectbox("Category", FOOD_CATEGORIES, key="p1s")
        with col_b:
            st.markdown(f'<p class="player-label">{p2_name}</p>', unsafe_allow_html=True)
            p2_p = st.number_input("Price Guess", key="p2p", format="%.2f")
            p2_c = st.selectbox("Category", FOOD_CATEGORIES, key="p2s")

        st.divider()
        actual_price = st.number_input("Actual Price", format="%.2f")
        actual_cat = st.selectbox("Actual Category", FOOD_CATEGORIES, key="act")

        if st.button("Submit Round"):
            # Points Calculation
            p1_round = 0
            p2_round = 0
            if p1_c == actual_cat: p1_round += 1
            if p2_c == actual_cat: p2_round += 1
            
            p1_diff = abs(p1_p - actual_price)
            p2_diff = abs(p2_p - actual_price)
            if p1_diff < p2_diff: p1_round += 1
            elif p2_diff < p1_diff: p2_round += 1

            # Update DF and push to Google Sheets
            df.at[0, 'Score'] = p1_score + p1_round
            df.at[1, 'Score'] = p2_score + p2_round
            conn.update(data=df)
            st.rerun()
