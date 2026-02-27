import streamlit as st

# --- CONFIG & STYLING ---
st.set_page_config(page_title="The Phantom Combo", page_icon="👻")

# Uber Eats / Phantom Combo Branding
st.markdown("""
    <style>
    .stApp {
        background-color: #121212;
        color: #FFFFFF;
    }
    .stButton>button {
        width: 100%;
        background-color: #06C167 !important;
        color: #121212 !important;
        font-weight: bold;
        border-radius: 8px;
        border: none;
        padding: 0.6rem;
    }
    .stTextInput>div>div>input, .stNumberInput>div>div>input {
        background-color: #2a2a2a !important;
        color: white !important;
        border: 1px solid #444 !important;
    }
    h2, h3 {
        color: #06C167 !important;
        text-align: center;
    }
    .score-box {
        text-align: center;
        font-size: 3.5rem;
        font-weight: bold;
        color: #06C167;
        margin-top: -20px;
    }
    .player-label {
        font-size: 1.2rem;
        font-weight: bold;
        color: #FFFFFF;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# --- SESSION STATE INITIALIZATION ---
if 'game_started' not in st.session_state:
    st.session_state.game_started = False
if 'p1_score' not in st.session_state:
    st.session_state.p1_score = 0
if 'p2_score' not in st.session_state:
    st.session_state.p2_score = 0

# --- SCREEN 1: SETUP ---
if not st.session_state.game_started:
    # Centering the logo
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("Logo.png", use_container_width=True)
    
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
            st.error("Both players need names to compete!")

# --- SCREEN 2: GAME ---
else:
    # Small logo at the top for game screen
    st.image("Logo.png", width=150)
    
    st.markdown(f'<div class="score-box">{st.session_state.p1_score} — {st.session_state.p2_score}</div>', unsafe_allow_html=True)
    st.markdown(f"<h3 style='text-align: center;'>{st.session_state.p1_name} vs {st.session_state.p2_name}</h3>", unsafe_allow_html=True)

    st.divider()

    # --- GUESSING SECTION ---
    st.write("### 🔮 The Guesses")
    c1, c2 = st.columns(2)
    
    with c1:
        st.markdown(f'<p class="player-label">{st.session_state.p1_name}</p>', unsafe_allow_html=True)
        p1_p = st.number_input("Price Guess", min_value=0.0, step=0.01, key="p1p", format="%.2f")
        p1_c = st.text_input("Category", placeholder="Pizza...", key="p1c")

    with c2:
        st.markdown(f'<p class="player-label">{st.session_state.p2_name}</p>', unsafe_allow_html=True)
        p2_p = st.number_input("Price Guess", min_value=0.0, step=0.01, key="p2p", format="%.2f")
        p2_c = st.text_input("Category", placeholder="Burgers...", key="p2c")

    st.divider()

    # --- RESULTS SECTION ---
    st.write("### 🧾 The Reality")
    actual_price = st.number_input("Actual Total Price", min_value=0.0, step=0.01, format="%.2f")
    actual_cat = st.text_input("Actual Category", placeholder="What actually arrived?")

    if st.button("Submit Result & Award Points"):
        # Category Points
        if p1_c.lower().strip() == actual_cat.lower().strip():
            st.session_state.p1_score += 1
            st.toast(f"Point for {st.session_state.p1_name} (Category)!")
        
        if p2_c.lower().strip() == actual_cat.lower().strip():
            st.session_state.p2_score += 1
            st.toast(f"Point for {st.session_state.p2_name} (Category)!")

        # Price Points (Who is closer?)
        p1_diff = abs(p1_p - actual_price)
        p2_diff = abs(p2_p - actual_price)

        if p1_diff < p2_diff:
            st.session_state.p1_score += 1
            st.success(f"{st.session_state.p1_name} was closer to the price!")
        elif p2_diff < p1_diff:
            st.session_state.p2_score += 1
            st.success(f"{st.session_state.p2_name} was closer to the price!")
        else:
            st.info("Price tie! No points awarded.")
            
        st.rerun()

    if st.button("Reset Tournament", type="secondary"):
        st.session_state.game_started = False
        st.session_state.p1_score = 0
        st.session_state.p2_score = 0
        st.rerun()
