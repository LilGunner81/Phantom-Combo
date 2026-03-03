import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import base64

# --- CONFIG & STYLING ---
st.set_page_config(page_title="The Phantom Combo", page_icon="👻")

# 1. DEFINE PWA MANIFEST
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
    .stApp {{ background-color: #0E1117; color: #FFFFFF; }}
    [data-testid="stForm"] {{
        background-color: #1A1C23 !important; 
        padding: 2.5rem;
        border-radius: 20px;
        border: 1px solid #333;
        box-shadow: 0 4px 15px rgba(0,0,0,0.5);
    }}
    .stProgress > div > div > div > div {{ background-color: #06C167 !important; }}
    .stButton>button {{ 
        width: 100%; 
        background-color: #06C167 !important; 
        color: #121212 !important; 
        font-weight: bold; 
        border-radius: 8px; 
        border: none; 
        height: 3em;
    }}
    .summary-box {{
        background-color: #1A1C23;
        border: 2px solid #06C167;
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
        text-align: center;
    }}
    h2, h3 {{ color: #06C167 !important; text-align: center; font-weight: 800; }}
    .score-box {{ text-align: center; font-size: 4rem; font-weight: bold; color: #06C167; padding: 5px 0; }}
    .player-label {{ font-size: 1.4rem; font-weight: bold; color: #06C167; text-align: center; display: block; margin-bottom: 5px; }}
    </style>
    """, unsafe_allow_html=True)

# --- DB & CONSTANTS ---
DB_COLUMNS = ["Name", "Score", "P1 Cat1", "P1 Cat2", "P1 $", "P2 Cat1", "P2 Cat2", "P2 $"]
FOOD_CATEGORIES = ["Italian", "Sushi", "Mediterranean", "Eastern Asian", "Sandwiches", "Asian", "Mexican", "South Asian", "Chicken", "Shop and Deliver", "Liquor", "Bakery", "Fish and Chips", "Other"]
WIN_LIMIT = 25

conn = st.connection("gsheets", type=GSheetsConnection)

def get_data():
    try:
        data = conn.read(ttl=0)
        if not data.empty:
            data['Score'] = pd.to_numeric(data['Score'], errors='coerce').fillna(0).astype(float)
            for col in ['P1 $', 'P2 $']:
                data[col] = pd.to_numeric(data[col], errors='coerce').fillna(0.0)
        return data
    except:
        return pd.DataFrame(columns=DB_COLUMNS)

df = get_data()

# --- CALLBACK LOGIC ---
def handle_submission():
    fresh_df = get_data()
    p1_n = fresh_df.iloc[0]['Name']
    p2_n = fresh_df.iloc[1]['Name']
    
    actual_p = st.session_state.actual_p
    actual_cats = st.session_state.actual_cats
    is_stacked = st.session_state.is_stacked
    target_p = actual_p * 0.5 if is_stacked else actual_p
    
    def calc_pts(g1, g2, actuals, stacked):
        pts = 0.0
        if g1 in actuals: pts += 1.0
        if g2 in actuals: pts += 1.0 if stacked else 0.5
        return pts

    p1_cat_pts = calc_pts(st.session_state.p1c1, st.session_state.p1c2, actual_cats, is_stacked)
    p2_cat_pts = calc_pts(st.session_state.p2c1, st.session_state.p2c2, actual_cats, is_stacked)
    
    # Price logic
    p1_price_pts = 0
    p2_price_pts = 0
    d1, d2 = abs(st.session_state.p1p - target_p), abs(st.session_state.p2p - target_p)
    if d1 < d2: p1_price_pts = 1
    elif d2 < d1: p2_price_pts = 1
    else: p1_price_pts, p2_price_pts = 1, 1
    
    p1_total = p1_cat_pts + p1_price_pts
    p2_total = p2_cat_pts + p2_price_pts

    # Update Data
    fresh_df.at[0, 'Score'] += p1_total
    fresh_df.at[1, 'Score'] += p2_total
    
    # Update state for summary display
    st.session_state.last_result = {
        "p1_name": p1_n, "p1_total": p1_total, "p1_cat": p1_cat_pts, "p1_price": p1_price_pts,
        "p2_name": p2_n, "p2_total": p2_total, "p2_cat": p2_cat_pts, "p2_price": p2_price_pts,
        "target": target_p
    }

    conn.update(data=fresh_df)
    st.session_state.guesses_locked = False

# --- UI HELPERS ---
def get_cat_index(val):
    try: return FOOD_CATEGORIES.index(val)
    except: return 0

def display_logo():
    try: st.image("Logo.png", use_container_width=True)
    except: st.markdown("<h1 style='text-align:center; color:#06C167;'>👻 THE PHANTOM COMBO</h1>", unsafe_allow_html=True)

# --- APP FLOW ---
if 'guesses_locked' not in st.session_state: st.session_state.guesses_locked = False

with st.sidebar:
    st.header("Admin Controls")
    if st.button("🗑️ Reset All"):
        st.session_state.guesses_locked = False
        st.session_state.last_result = None
        conn.update(data=pd.DataFrame(columns=DB_COLUMNS))
        st.rerun()

if not df.empty and any(df['Score'] >= WIN_LIMIT):
    winner = df[df['Score'] >= WIN_LIMIT].iloc[0]['Name']
    st.balloons()
    display_logo()
    st.markdown(f"<h1 style='text-align:center; color:#FFD700;'>🏆 {winner} WINS! 🏆</h1>", unsafe_allow_html=True)
    if st.button("Start New Tournament"):
        df['Score'] = 0
        conn.update(data=df)
        st.session_state.last_result = None
        st.rerun()

elif len(df) < 2:
    display_logo()
    st.subheader("Tournament Setup")
    p1_in = st.text_input("Player 1 Name")
    p2_in = st.text_input("Player 2 Name")
    if st.button("Save Players & Start"):
        if p1_in and p2_in:
            new_df = pd.DataFrame([
                {"Name": p1_in, "Score": 0.0, "P1 Cat1": "Other", "P1 Cat2": "Other", "P1 $": 0.0, "P2 Cat1": "Other", "P2 Cat2": "Other", "P2 $": 0.0},
                {"Name": p2_in, "Score": 0.0, "P1 Cat1": "Other", "P1 Cat2": "Other", "P1 $": 0.0, "P2 Cat1": "Other", "P2 Cat2": "Other", "P2 $": 0.0}
            ])
            conn.update(data=new_df)
            st.rerun()

else:
    display_logo()
    row = df.iloc[0]
    p1_n, p1_s = row['Name'], row['Score']
    p2_n, p2_s = df.iloc[1]['Name'], df.iloc[1]['Score']

    st.markdown(f'<div class="score-box">{int(p1_s)} — {int(p2_s)}</div>', unsafe_allow_html=True)
    st.progress(min(p1_s / WIN_LIMIT, 1.0), text=f"{p1_n}'s Path")
    st.progress(min(p2_s / WIN_LIMIT, 1.0), text=f"{p2_n}'s Path")

    # --- ROUND SUMMARY SECTION ---
    if st.session_state.get('last_result'):
        res = st.session_state.last_result
        st.markdown(f"""
        <div class="summary-box">
            <h3 style="margin-top:0;">📊 LAST ROUND RECAP</h3>
            <p>Target Price: <b>${res['target']:.2f}</b></p>
            <hr style="border: 0.5px solid #333;">
            <div style="display: flex; justify-content: space-around;">
                <div>
                    <p style="color:#06C167; font-weight:bold;">{res['p1_name']}</p>
                    <p>+{res['p1_cat']} (Cats) <br> +{res['p1_price']} (Price)</p>
                    <p style="font-size:1.2rem;"><b>Total: +{res['p1_total']}</b></p>
                </div>
                <div style="border-left: 1px solid #333; height: 100px;"></div>
                <div>
                    <p style="color:#06C167; font-weight:bold;">{res['p2_name']}</p>
                    <p>+{res['p2_cat']} (Cats) <br> +{res['p2_price']} (Price)</p>
                    <p style="font-size:1.2rem;"><b>Total: +{res['p2_total']}</b></p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with st.form("round_form"):
        st.markdown("### 🎲 ROUND GUESSES")
        is_locked = st.session_state.guesses_locked
        col_p1, col_p2 = st.columns(2)
        
        with col_p1:
            st.markdown(f'<p class="player-label">{p1_n}</p>', unsafe_allow_html=True)
            st.selectbox("Guess 1", FOOD_CATEGORIES, key="p1c1", disabled=is_locked, index=get_cat_index(row['P1 Cat1']))
            st.selectbox("Guess 2", FOOD_CATEGORIES, key="p1c2", disabled=is_locked, index=get_cat_index(row['P1 Cat2']))
            st.number_input("Price Guess", key="p1p", format="%.2f", step=0.01, disabled=is_locked, value=float(row['P1 $']))
        
        with col_p2:
            st.markdown(f'<p class="player-label">{p2_n}</p>', unsafe_allow_html=True)
            st.selectbox("Guess 1", FOOD_CATEGORIES, key="p2c1", disabled=is_locked, index=get_cat_index(df.iloc[1]['P2 Cat1']))
            st.selectbox("Guess 2", FOOD_CATEGORIES, key="p2c2", disabled=is_locked, index=get_cat_index(df.iloc[1]['P2 Cat2']))
            st.number_input("Price Guess", key="p2p", format="%.2f", step=0.01, disabled=is_locked, value=float(df.iloc[1]['P2 $']))

        if not is_locked:
            if st.form_submit_button("🔒 LOCK IN GUESSES"):
                for idx in [0, 1]:
                    p_prefix = f"P{idx+1}"
                    df.at[idx, f'{p_prefix} Cat1'] = st.session_state[f'p{idx+1}c1']
                    df.at[idx, f'{p_prefix} Cat2'] = st.session_state[f'p{idx+1}c2']
                    df.at[idx, f'{p_prefix} $'] = float(st.session_state[f'p{idx+1}p'])
                conn.update(data=df)
                st.session_state.guesses_locked = True
                st.rerun()
        
        if is_locked:
            st.divider()
            st.markdown("### 🏁 ACTUAL RESULTS")
            st.checkbox("Stacked Order? (0.5x Price)", key="is_stacked")
            st.number_input("Actual Total Price", format="%.2f", step=0.01, key="actual_p")
            st.multiselect("Actual Food Category(s)", FOOD_CATEGORIES, key="actual_cats")
            
            c_sub, c_unl = st.columns([3, 1])
            c_sub.form_submit_button("🚀 SUBMIT ROUND", on_click=handle_submission)
            
            if c_unl.form_submit_button("🔓 UNLOCK"):
                st.session_state.guesses_locked = False
                st.rerun()
