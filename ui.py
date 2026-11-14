"""Streamlit UI helpers for the Artemis Base Camp game.
This module contains all the rendering logic, state initialisation and event handling.
It works together with `simulation.py` which holds the core game mechanics.
"""
import os
import streamlit as st
from simulation import LunarSimulation, TEXTS, POSSIBLE_ASSET_DIRS, POSSIBLE_SONG_DIRS

# ---------------------------------------------------------------------------
# Helper to locate an asset (image or audio) in the possible directories.
def locate_asset(filename: str) -> str:
    """Return the absolute path of *filename* if it exists in one of the
    POSSIBLE_ASSET_DIRS (or POSSIBLE_SONG_DIRS for audio). Returns an empty
    string if not found – callers should handle the missing case.
    """
    search_paths = POSSIBLE_ASSET_DIRS if not filename.lower().endswith('.mp3') else POSSIBLE_SONG_DIRS
    for base in search_paths:
        candidate = os.path.join(base, filename)
        if os.path.exists(candidate):
            return candidate
    return ""

# ---------------------------------------------------------------------------
# Session‑state initialisation ------------------------------------------------
def init_state():
    """Create all required ``st.session_state`` keys if they are missing.
    This function is idempotent – calling it multiple times does not reset
    existing values.
    """
    if "sim" not in st.session_state:
        st.session_state.sim = LunarSimulation()
    if "lang" not in st.session_state:
        st.session_state.lang = "pt"
    if "game_state" not in st.session_state:
        st.session_state.game_state = "SELECT_LANG"
    if "music_enabled" not in st.session_state:
        st.session_state.music_enabled = False
    if "playlist" not in st.session_state:
        # Build playlist of absolute paths for the two songs
        playlist = []
        for name in ["song1.mp3", "song2.mp3"]:
            path = locate_asset(name)
            if path:
                playlist.append(path)
        st.session_state.playlist = playlist
    if "current_song" not in st.session_state:
        st.session_state.current_song = 0
    if "bg_current" not in st.session_state:
        # default background image filename
        st.session_state.bg_current = locate_asset("bg_lunar.png")

# ---------------------------------------------------------------------------
# UI Rendering ---------------------------------------------------------------
def render():
    """Render the whole UI based on ``st.session_state.game_state``.
    This function is called once per Streamlit run.
    """
    # --- top bar with language & music toggle --------------------------------
    col_lang, col_music = st.columns([1, 1])
    with col_lang:
        if st.button(TEXTS[st.session_state.lang]["btn_lang"], key="lang_toggle"):
            # Switch language, keep current game state where appropriate
            st.session_state.lang = "en" if st.session_state.lang == "pt" else "pt"
            # Refresh climate for the new language
            st.session_state.sim.evento_clima = st.session_state.sim.sortear_clima(st.session_state.lang)
    with col_music:
        label = TEXTS[st.session_state.lang]["btn_music_on"] if st.session_state.music_enabled else TEXTS[st.session_state.lang]["btn_music_off"]
        if st.button(label, key="music_toggle"):
            st.session_state.music_enabled = not st.session_state.music_enabled
            # Reset song index when (re)starting music
            if st.session_state.music_enabled:
                st.session_state.current_song = 0
    # If music is enabled and we have a playlist, embed an audio player
    if st.session_state.music_enabled and st.session_state.playlist:
        song_path = st.session_state.playlist[st.session_state.current_song]
        # Read bytes – Streamlit can stream the file directly
        with open(song_path, "rb") as f:
            st.audio(f.read(), format="audio/mp3")
        # Simple "Next" button to advance the playlist
        if st.button("Next Track"):
            st.session_state.current_song = (st.session_state.current_word + 1) % len(st.session_state.playlist) if False else (st.session_state.current_song + 1) % len(st.session_state.playlist)
    # -----------------------------------------------------------------------
    # Render the main content area based on the game state
    if st.session_state.game_state == "SELECT_LANG":
        render_lang_select()
    elif st.session_state.game_state == "INTRO_DONKI":
        render_donki_intro()
    elif st.session_state.game_state == "PLAYING":
        render_gameplay()
    elif st.session_state.game_state in ("FAIL_O2", "FAIL_RAD", "VICTORY"):
        render_modal()

# ---------------------------------------------------------------------------
def render_lang_select():
    """Initial language selection screen with two large buttons."""
    st.title("NASA ARTEMIS BASE CAMP")
    st.subheader("SELECIONE O IDIOMA // SELECT LANGUAGE")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("1️⃣  PORTUGUÊS (BRASIL)", key="lang_pt"):
            st.session_state.lang = "pt"
            st.session_state.sim.evento_clima = st.session_state.sim.sortear_clima("pt")
            st.session_state.game_state = "INTRO_DONKI"
    with col2:
        if st.button("2️⃣  ENGLISH (UNITED STATES)", key="lang_en"):
            st.session_state.lang = "en"
            st.session_state.sim.evento_clima = st.session_state.sim.sortear_clima("en")
            st.session_state.game_state = "INTRO_DONKI"

# ---------------------------------------------------------------------------
def render_donki_intro():
    """Show the Luna‑Bot mascot and introductory text. A single button proceeds to the game."""
    st.markdown("---")
    # Layout: image on the left, text on the right
    col_img, col_text = st.columns([1, 2])
    with col_img:
        mascot_path = locate_asset("mascot.png")
        if mascot_path:
            st.image(mascot_path, width=250)
    with col_text:
        st.header(TEXTS[st.session_state.lang]["intro_greeting"])
        intro_lines = [
            TEXTS[st.session_state.lang]["intro_p1"],
            TEXTS[st.session_state.lang]["intro_p2"],
            TEXTS[st.session_state.lang]["intro_p3"],
            TEXTS[st.session_state.lang]["intro_p4"],
            TEXTS[st.session_state.lang]["intro_p5"],
        ]
        for line in intro_lines:
            st.write(line)
        if st.button(TEXTS[st.session_state.lang]["intro_btn"], key="start_mission"):
            st.session_state.game_state = "PLAYING"
    st.markdown("---")

# ---------------------------------------------------------------------------
def render_gameplay():
    """Main gameplay screen – telemetry, background image, and option cards."""
    # --- telemetry panel ----------------------------------------------------
    sim = st.session_state.sim
    lang = st.session_state.lang
    st.subheader(f"{TEXTS[lang]["day"]} {sim.dia}")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(TEXTS[lang]["res_o2"], f"{sim.oxigenio}%")
        st.metric(TEXTS[lang]["res_ice"], f"{sim.gelo}%")
    with col2:
        st.metric(TEXTS[lang]["res_energy"], f"{sim.energia} kW")
        st.metric(TEXTS[lang]["res_science"], f"{sim.ciencia}/100")
    with col3:
        st.metric(TEXTS[lang]["res_radiation"], f"{sim.radiacao:.1f} mSv")
        st.metric(TEXTS[lang]["res_health"], f"{sim.saude}%")

    # --- background image ---------------------------------------------------
    if st.session_state.bg_current:
        st.image(st.session_state.bg_current, use_column_width=True)

    # --- action cards -------------------------------------------------------
    st.write(TEXTS[lang]["prompt"])
    col_opt1, col_opt2, col_opt3 = st.columns(3)
    with col_opt1:
        if st.button(f"{TEXTS[lang]["opt1_title"]}\n{TEXTS[lang]["opt1_desc"]}", key="opt1"):
            _apply_choice(1)
    with col_opt2:
        if st.button(f"{TEXTS[lang]["opt2_title"]}\n{TEXTS[lang]["opt2_desc"]}", key="opt2"):
            _apply_choice(2)
    with col_opt3:
        if st.button(f"{TEXTS[lang]["opt3_title"]}\n{TEXTS[lang]["opt3_desc"]}", key="opt3"):
            _apply_choice(3)

# ---------------------------------------------------------------------------
def _apply_choice(choice: int):
    """Process a player choice, update simulation, background and game state."""
    sim = st.session_state.sim
    lang = st.session_state.lang
    feedback = sim.aplicar_turno(choice, lang)
    st.session_state.feedback_msg = feedback

    # Update background according to the chosen option
    if choice == 1:
        st.session_state.bg_current = locate_asset("bg_lunar.png")
    elif choice == 2:
        st.session_state.bg_current = locate_asset("bunker_background.png")
    elif choice == 3:
        st.session_state.bg_current = locate_asset("rover_background.png")

    # Check for end‑game conditions
    if sim.oxigenio <= 0:
        st.session_state.game_state = "FAIL_O2"
    elif sim.saude <= 0:
        st.session_state.game_state = "FAIL_RAD"
    elif sim.ciencia >= sim.meta_ciencia:
        st.session_state.game_state = "VICTORY"
    else:
        st.session_state.game_state = "PLAYING"

# ---------------------------------------------------------------------------
def render_modal():
    """Show win / lose modal with a restart button."""
    lang = st.session_state.lang
    if st.session_state.game_state == "FAIL_O2":
        title = TEXTS[lang]["fail_o2_title"]
        desc = TEXTS[lang]["fail_o2_desc"]
        st.error(f"## {title}\n{desc}")
    elif st.session_state.game_state == "FAIL_RAD":
        title = TEXTS[lang]["fail_rad_title"]
        desc = TEXTS[lang]["fail_rad_desc"]
        st.error(f"## {title}\n{desc}")
    elif st.session_state.game_state == "VICTORY":
        title = TEXTS[lang]["win_title"]
        desc = TEXTS[lang]["win_desc"]
        st.success(f"## {title}\n{desc}")
    if st.button(TEXTS[lang]["btn_restart"], key="restart"):
        # Reset everything to start a new game
        st.session_state.sim.reset()
        st.session_state.bg_current = locate_asset("bg_lunar.png")
        st.session_state.game_state = "PLAYING"
        st.session_state.feedback_msg = ""
        st.session_state.music_enabled = False

# ---------------------------------------------------------------------------
# End of ui.py
