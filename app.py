import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# --- CONFIG & STYLING ---
st.set_page_config(page_title="The Phantom Combo", page_icon="👻")

st.markdown("""
    <style>
    .stApp { background-color: #121212; color: #FFFFFF; }
    .stButton>button { 
        width: 100%; 
        background-color: #06C167 !important; 
        color: #121212 !important; 
        font-weight: bold; 
        border-radius: 8px; 
        border: none; 
    }
    .stTextInput>div>div>input, .stNumberInput>div>div>input, .stSelectbox>div>div>div {
        background-color: #2a2a2a !important; 
        color: white !important; 
        border: 1px solid #444 !important;
    }
    h2, h3 { color: #06C167 !important; text-align: center; }
    .score-box { text-align: center; font-size: 3.5rem; font-weight: bold; color: #06C167; margin-top: -10px; }
    .player-label { font-size: 1.2rem; font-weight: bold; color: #FFFFFF; text-align: center; display: block; }
    </style>
    """, unsafe_allow_html=True)

# --- DB CONNECTION ---
conn = st.connection("gsheets", type=GSheetsConnection)

try:
    df = conn.read(ttl=0)
except Exception as e:
    st.error(f"Connection Error: {e}")
    df = pd.DataFrame(columns=["Name", "Score"])

# Ensure data types
if not df.empty:
    df['Score'] = pd.to_numeric(df['Score'], errors='coerce').fillna(0).astype(int)

# --- SIDEBAR RESET ---
with st.sidebar:
    st.header("Admin Controls")
    if st.button("🗑️ Reset All (New Players)"):
        # Create an empty dataframe with the correct columns
        empty_df = pd.DataFrame(columns=["Name", "Score"])
        conn.update(data=empty_df)
        st.success("Data wiped! Redirecting...")
        st.rerun()

FOOD_CATEGORIES = ["Italian", "Sushi", "Mediterranean", "Eastern Asian", "Sandwiches", "Asian", "Mexican", "South Asian", "Chicken", "Shop and Deliver", "Liquor", "Other"]
WIN_LIMIT = 25

def display_logo(width=None, stretch=False):
    try:
        if stretch:
            st.image("Logo.png", use_container_width=True)
        else:
            st.image("Logo.png", width=width)
    except:
        st.markdown("### 👻 THE PHANTOM COMBO")

# --- SCREEN 1: WINNER ---
if not df.empty and any(df['Score'] >= WIN_LIMIT):
    winner_name = df[df['Score'] >= WIN_LIMIT].iloc[0]['Name']
    st.balloons()
    st.markdown(f"<h1 style='text-align:center; color:#FFD700;'>🏆 {winner_name} WINS! 🏆</h1>", unsafe_allow_html=True)
    display_logo(stretch=True)
    if st.button("Start New Tournament"):
        df['Score'] = 0
        conn.update(data=df)
        st.rerun()

# --- SCREEN 2: SETUP (Shows if 0 or 1 players found) ---
elif len(df) < 2:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2: 
        display_logo(stretch=True)
    
    st.subheader("Tournament Setup")
    p1_in = st.text_input("Player 1 Name", placeholder="Enter Name")
    p2_in = st.text_input("Player 2 Name", placeholder="Enter Name")
    
    if st.button("Save Players & Start"):
        if p1_in and p2_in:
            new_df = pd.DataFrame([{"Name": p1_in, "Score": 0}, {"Name": p2_in, "Score": 0}])
            conn.update(data=new_df)
            st.rerun()
        else:
            st.warning("Please enter both names.")

# --- SCREEN 3: GAME ---
else:
    p1_n, p1_s = df.iloc[0]['Name'], int(df.iloc[0]['Score'])
    p2_n, p2_s = df.iloc[1]['Name'], int(df.iloc[1]['Score'])

    c_logo, c_score = st.columns([1, 3])
    with c_logo: 
        display_logo(width=100)
    with c_score: 
        st.markdown(f'<div class="score-box">{p1_s} — {p2_s}</div>', unsafe_allow_html=True)
    
    st.progress(min(p1_s / WIN_LIMIT, 1.0), text=f"{p1_n}'s Path to Victory")
    st.progress(min(p2_s / WIN_LIMIT, 1.0), text=f"{p2_n}'s Path to Victory")

    with st.form("round_form"):
        st.divider()
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown(f'<p class="player-label">{p1_n}</p>', unsafe_allow_html=True)
            p1_p = st.number_input("Price Guess", key="p1p", format="%.2f", min_value=0.0)
            p1_c = st.selectbox("Category Guess", FOOD_CATEGORIES, key="p1c")
        with col_b:
            st.markdown(f'<p class="player-label">{p2_n}</p>', unsafe_allow_html=True)
            p2_p = st.number_input("Price Guess", key="p2p", format="%.2f", min_value=0.0)
            p2_c = st.selectbox("Category Guess", FOOD_CATEGORIES, key="p2c")

        st.divider()
        actual_p = st.number_input("Actual Total Price", format="%.2f", min_value=0.0)
        actual_c = st.selectbox("Actual Category", FOOD_CATEGORIES, key="actc")
        
        submit_btn = st.form_submit_button("Submit Round Results")

    if submit_btn:
        p1_r, p2_r = 0, 0
        if p1_c == actual_c: p1_r += 1
        if p2_c == actual_c: p2_r += 1
        
        d1, d2 = abs(p1_p - actual_p), abs(p2_p - actual_p)
        if d1 < d2: p1_r += 1
        elif d2 < d1: p2_r += 1
        else:
            p1_r += 1; p2_r += 1
        
        df.at[0, 'Score'] = p1_s + p1_r
        df.at[1, 'Score'] = p2_s + p2_r
        conn.update(data=df)
        st.rerun()
