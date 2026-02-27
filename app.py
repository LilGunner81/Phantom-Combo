import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import base64

# --- CONFIG & STYLING ---
st.set_page_config(page_title="The Phantom Combo", page_icon="👻")

# 1. DEFINE PWA MANIFEST (Base64 Injection for Streamlit Cloud)
manifest_data = """
{
  "name": "The Phantom Combo",
  "short_name": "Phantom",
  "start_url": ".",
  "display": "standalone",
  "background_color": "#0E1117",
  "theme_color": "#06C167",
  "icons": [
    {
      "src": "https://raw.githubusercontent.com/LilGunner/Phantom-Combo/main/Logo.png",
      "sizes": "512x512",
      "type": "image/png"
    }
  ]
}
"""
manifest_b64 = base64.b64encode(manifest_data.encode()).decode()
manifest_link = f"data:application/json;base64,{manifest_b64}"

st.markdown(f"""
    <link rel="manifest" href="{manifest_link}">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <link rel="apple-touch-icon" href="https://raw.githubusercontent.com/LilGunner/Phantom-Combo/main/Logo.png">
    
    <style>
    /* Main Background */
    .stApp {{ background-color: #0E1117; color: #FFFFFF; }}
    
    /* THE CONTRAST BOX */
    [data-testid="stForm"] {{
        background-color: #1A1C23 !important; 
        padding: 2.5rem;
        border-radius: 20px;
        border: 1px solid #333;
        box-shadow: 0 4px 15px rgba(0,0,0,0.5);
    }}

    /* FULL WIDTH IMAGE */
    [data-testid="stImage"] {{
        display: flex;
        justify-content: center;
        width: 100%;
    }}
    
    [data-testid="stImage"] > img {{
        width: 100% !important;
        height: auto;
    }}

    /* PHANTOM GREEN PROGRESS BARS */
    .stProgress > div > div > div > div {{
        background-color: #06C167 !important;
    }}

    .block-container {{
        padding-top: 0.5rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }}

    /* Buttons */
    .stButton>button {{ 
        width: 100%; 
        background-color: #06C167 !important; 
        color: #121212 !important; 
        font-weight: bold; 
        border-radius: 8px; 
        border: none; 
        height: 3em;
    }}

    /* Input Boxes */
    .stTextInput>div>div>input, .stNumberInput>div>div>input, .stSelectbox>div>div>div {{
        background-color: #2D2D2D !important; 
        color: white !important; 
        border: 1px solid #444 !important;
    }}
    
    h2, h3 {{ color: #06C167 !important; text-align: center; font-weight: 800; }}
    .score-box {{ text-align: center; font-size: 4rem; font-weight: bold; color: #06C167; padding: 5px 0; }}
    .player-label {{ font-size: 1.4rem; font-weight: bold; color: #06C167; text-align: center; display: block; margin-bottom: 5px; }}
    </style>
    """, unsafe_allow_html=True)

# --- DB CONNECTION ---
conn = st.connection("gsheets", type=GSheetsConnection)

try:
    df = conn.read(ttl=0)
except Exception as e:
    st.error(f"Connection Error: {e}")
    df = pd.DataFrame(columns=["Name", "Score"])

if not df.empty:
    df['Score'] = pd.to_numeric(df['Score'], errors='coerce').fillna(0).astype(int)

# --- SIDEBAR RESET ---
with st.sidebar:
    st.header("Admin Controls")
    if st.button("🗑️ Reset All (New Players)"):
        empty_df = pd.DataFrame(columns=["Name", "Score"])
        conn.update(data=empty_df)
        st.success("Tournament Reset!")
        st.rerun()

FOOD_CATEGORIES = ["Italian", "Sushi", "Mediterranean", "Eastern Asian", "Sandwiches", "Asian", "Mexican", "South Asian", "Chicken", "Shop and Deliver", "Liquor", "Other"]
WIN_LIMIT = 25

def display_logo():
    try:
        st.image("Logo.png", use_container_width=True)
    except:
        st.markdown("<h1 style='text-align:center; color:#06C167;'>👻 THE PHANTOM COMBO</h1>", unsafe_allow_html=True)

# --- NAVIGATION LOGIC ---
if not df.empty and any(df['Score'] >= WIN_LIMIT):
    winner_name = df[df['Score'] >= WIN_LIMIT].iloc[0]['Name']
    st.balloons()
    display_logo()
    st.markdown(f"<h1 style='text-align:center; color:#FFD700;'>🏆 {winner_name} WINS! 🏆</h1>", unsafe_allow_html=True)
    if st.button("Start New Tournament"):
        df['Score'] = 0
        conn.update(data=df)
        st.rerun()

elif len(df) < 2:
    display_logo()
    st.subheader("Tournament Setup")
    p1_in = st.text_input("Player 1 Name")
    p2_in = st.text_input("Player 2 Name")
    if st.button("Save Players & Start"):
        if p1_in and p2_in:
            new_df = pd.DataFrame([{"Name": p1_in, "Score": 0}, {"Name": p2_in, "Score": 0}])
            conn.update(data=new_df)
            st.rerun()

else:
    display_logo()
    p1_n, p1_s = df.iloc[0]['Name'], int(df.iloc[0]['Score'])
    p2_n, p2_s = df.iloc[1]['Name'], int(df.iloc[1]['Score'])

    st.markdown(f'<div class="score-box">{p1_s} — {p2_s}</div>', unsafe_allow_html=True)
    
    st.progress(min(p1_s / WIN_LIMIT, 1.0), text=f"{p1_n}'s Path")
    st.progress(min(p2_s / WIN_LIMIT, 1.0), text=f"{p2_n}'s Path")

    with st.form("round_form"):
        st.markdown("### 🎲 ROUND DATA")
        st.markdown(f'<p class="player-label">{p1_n}</p>', unsafe_allow_html=True)
        p1_p = st.number_input("Price Guess", key="p1p", format="%.2f", step=0.01)
        p1_c = st.selectbox("Category Guess", FOOD_CATEGORIES, key="p1c")
        st.divider()
        st.markdown(f'<p class="player-label">{p2_n}</p>', unsafe_allow_html=True)
        p2_p = st.number_input("Price Guess", key="p2p", format="%.2f", step=0.01)
        p2_c = st.selectbox("Category Guess", FOOD_CATEGORIES, key="p2c")
        st.divider()
        actual_p = st.number_input("Actual Total Price", format="%.2f", step=0.01)
        actual_c = st.selectbox("Actual Category", FOOD_CATEGORIES, key="actc")
        
        if st.form_submit_button("Submit Round Results"):
            p1_r, p2_r = 0, 0
            if p1_c == actual_c: p1_r += 1
            if p2_c == actual_c: p2_r += 1
            d1, d2 = abs(p1_p - actual_p), abs(p2_p - actual_p)
            if d1 < d2: p1_r += 1
            elif d2 < d1: p2_r += 1
            else: p1_r += 1; p2_r += 1
            
            df.at[0, 'Score'] = p1_s + p1_r
            df.at[1, 'Score'] = p2_s + p2_r
            conn.update(data=df)
            st.rerun()
