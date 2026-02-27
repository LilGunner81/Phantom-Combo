import streamlit as st

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
    .player-label { font-size: 1.2rem; font-weight: bold; color: #FFFFFF; margin-bottom: 5px; text-align: center; display: block; }
    </style>
    """, unsafe_allow_html=True)

# --- YOUR CUSTOM CATEGORY LIST ---
FOOD_CATEGORIES = [
    "Italian", "Sushi", "Mediterranean", "Eastern Asian", 
    "Sandwiches", "Asian", "Mexican", "South Asian", 
    "Chicken", "Shop and Deliver", "Liquor", "Other"
]

# --- SESSION STATE ---
if 'game_started' not in st.session_state:
    st.session_state.game_started = False
if 'p1_score' not in st.session_state:
    st.session_state.p1_score = 0
if 'p2_score' not in st.session_state:
    st.session_state.p2_score = 0

# --- SCREEN 1: SETUP ---
if not st.session_state.game_started:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        try:
            st.image("Logo.png", use_container_width=True)
        except:
            st.title("👻 Phantom Combo")
    
    st.write("<p style='text-align: center; color: #a0a0a0;'>Enter your names to begin the duel.</p>", unsafe_allow_html=True)
    p1_name = st.text_input("Player 1 Name", placeholder="e.g. Ghost")
    p2_name = st.text_input("Player 2 Name", placeholder="e.g. Phantom")

    if st.button("Start Game"):
        if p1_name and p2_name:
            st.session_state.p1_name = p1_name
            st.session_state.p2_name = p2_name
            st.session_state.game_started = True
            st.rerun()
        else:
            st.error("Enter both names to play!")

# --- SCREEN 2: GAME ---
else:
    # Header Area
    c_logo, c_score = st.columns([1, 3])
    with c_logo:
        try:
            st.image("Logo.png", width=100)
        except:
            st.write("👻")
    with c_score:
        st.markdown(f'<div class="score-box">{st.session_state.p1_score} — {st.session_state.p2_score}</div>', unsafe_allow_html=True)
    
    st.markdown(f"<h3 style='margin-top: -20px;'>{st.session_state.p1_name} vs {st.session_state.p2_name}</h3>", unsafe_allow_html=True)

    st.divider()

    # --- GUESSING SECTION ---
    st.write("### 🔮 The Guesses")
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.markdown(f'<p class="player-label">{st.session_state.p1_name}</p>', unsafe_allow_html=True)
        p1_p = st.number_input("Price Guess", min_value=0.0, step=0.01, key="p1p", format="%.2f")
        p1_c_sel = st.selectbox("Category", FOOD_CATEGORIES, key="p1_sel")
        p1_final_cat = p1_c_sel
        if p1_c_sel == "Other":
            p1_final_cat = st.text_input("Type category...", key="p1_custom")

    with col_b:
        st.markdown(f'<p class="player-label">{st.session_state.p2_name}</p>', unsafe_allow_html=True)
        p2_p = st.number_input("Price Guess", min_value=0.0, step=0.01, key="p2p", format="%.2f")
        p2_c_sel = st.selectbox("Category", FOOD_CATEGORIES, key="p2_sel")
        p2_final_cat = p2_c_sel
        if p2_c_sel == "Other":
            p2_final_cat = st.text_input("Type category...", key="p2_custom")

    st.divider()

    # --- RESULTS SECTION ---
    st.write("### 🧾 The Reality")
    actual_price = st.number_input("Actual Total Price", min_value=0.0, step=0.01, format="%.2f")
    actual_c_sel = st.selectbox("Actual Category", FOOD_CATEGORIES, key="actual_sel")
    actual_final_cat = actual_c_sel
    if actual_c_sel == "Other":
        actual_final_cat = st.text_input("Type actual category...", key="actual_custom")

    if st.button("Submit Round Results"):
        # Logic for Category Points
        if p1_final_cat and actual_final_cat and p1_final_cat.lower().strip() == actual_final_cat.lower().strip():
            st.session_state.p1_score += 1
            st.toast(f"Point for {st.session_state.p1_name} (Category)!")
            
        if p2_final_cat and actual_final_cat and p2_final_cat.lower().strip() == actual_final_cat.lower().strip():
            st.session_state.p2_score += 1
            st.toast(f"Point for {st.session_state.p2_name} (Category)!")

        # Logic for Price Points
        p1_diff = abs(p1_p - actual_price)
        p2_diff = abs(p2_p - actual_price)

        if p1_diff < p2_diff:
            st.session_state.p1_score += 1
            st.success(f"{st.session_state.p1_name} was closer!")
        elif p2_diff < p1_diff:
            st.session_state.p2_score += 1
            st.success(f"{st.session_state.p2_name} was closer!")
        else:
            st.info("It's a price tie!")
            
        st.rerun()

    if st.button("End Tournament / Reset", type="secondary"):
        st.session_state.game_started = False
        st.session_state.p1_score = 0
        st.session_state.p2_score = 0
        st.rerun()
