"""Streamlit UI helpers for the Artemis Base Camp game.
This module contains all the rendering logic, state initialisation and event handling.
Images and audio are loaded from local folders or directly from GitHub.
"""
import os
import streamlit as st
from simulation import LunarSimulation, TEXTS, POSSIBLE_ASSET_DIRS, POSSIBLE_SONG_DIRS

# URLs base direta do GitHub
GITHUB_RAW_BASE = "https://raw.githubusercontent.com/DaviKidsPlanet-oficial/BRAVEN---Survival-on-the-Moon/images"
GITHUB_SONGS_BASE = "https://raw.githubusercontent.com/DaviKidsPlanet-oficial/BRAVEN---Survival-on-the-Moon/main/songs"

def locate_asset(filename: str) -> str:
    """Busca primeiro nos diretórios locais de assets ou songs.
    Se não encontrar, retorna a URL correspondente no GitHub.
    """
    is_mp3 = filename.lower().endswith(".mp3")
    
    if is_mp3:
        search_paths = [
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "songs"),
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets"),
            r"C:\Users\Pichau\Desktop\Clube Nicolinha\space_outpost_game\songs",
            r"C:\Users\Pichau\.gemini\antigravity\brain\b5c774e8-cb64-4879-b8f8-f3535b4adb02\streamlit_app\songs",
        ]
        for base in search_paths:
            candidate = os.path.join(base, filename)
            if os.path.exists(candidate):
                return candidate
        # Fallback para o GitHub se a pasta songs for enviada ao repositório
        return f"{GITHUB_SONGS_BASE}/{filename}"

    search_paths = [
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets"),
        r"C:\Users\Pichau\Desktop\Clube Nicolinha\space_outpost_game\assets",
        r"C:\Users\Pichau\.gemini\antigravity\brain\b5c774e8-cb64-4879-b8f8-f3535b4adb02\streamlit_app\assets",
        r"C:\Users\Pichau\.gemini\antigravity\brain\b5c774e8-cb64-4879-b8f8-f3535b4adb02",
    ]
    for base in search_paths:
        candidate = os.path.join(base, filename)
        if os.path.exists(candidate):
            return candidate

    return f"{GITHUB_RAW_BASE}/{filename}"

def init_state():
    """Inicializa as variáveis de sessão no Streamlit."""
    if "sim" not in st.session_state:
        st.session_state.sim = LunarSimulation()
    if "lang" not in st.session_state:
        st.session_state.lang = "pt"
    if "game_state" not in st.session_state:
        st.session_state.game_state = "SELECT_LANG"
    if "music_enabled" not in st.session_state:
        st.session_state.music_enabled = False
    if not st.session_state.get("playlist"):
        playlist = []
        for name in ["song1.mp3", "song2.mp3", "song3.mp3"]:
            path = locate_asset(name)
            if path:
                playlist.append(path)
        st.session_state.playlist = playlist
    if "current_song" not in st.session_state:
        st.session_state.current_song = 0
    if "bg_current" not in st.session_state:
        st.session_state.bg_current = locate_asset("bg_lunar.png")
    if "feedback_msg" not in st.session_state:
        st.session_state.feedback_msg = "[STATUS]: Base operacional! Selecione uma ordem diária, Comandante."

def render():
    """Renderiza a interface conforme o estado atual."""
    # Topo: Banner da Missão à esquerda e Controles (Idioma / Música) à direita
    col_banner, col_ctrl1, col_ctrl2 = st.columns([3, 1, 1])
    with col_banner:
        banner_url = locate_asset("banner_mission.png")
        if banner_url:
            st.image(banner_url, width=320)
    with col_ctrl1:
        if st.button(TEXTS[st.session_state.lang]["btn_lang"], key="lang_toggle", use_container_width=True):
            st.session_state.lang = "en" if st.session_state.lang == "pt" else "pt"
            st.session_state.sim.evento_clima = st.session_state.sim.sortear_clima(st.session_state.lang)
            st.rerun()
    with col_ctrl2:
        label_musica = TEXTS[st.session_state.lang]["btn_music_on"] if st.session_state.music_enabled else TEXTS[st.session_state.lang]["btn_music_off"]
        if st.button(label_musica, key="music_toggle", use_container_width=True):
            st.session_state.music_enabled = not st.session_state.music_enabled
            if st.session_state.music_enabled:
                st.session_state.current_song = 0
            st.rerun()

    # Reprodução de áudio com Autoplay quando ativada
    if st.session_state.music_enabled:
        if st.session_state.playlist:
            song_source = st.session_state.playlist[st.session_state.current_song]
            col_audio, col_skip = st.columns([4, 1])
            with col_audio:
                if isinstance(song_source, str) and song_source.startswith("http"):
                    st.audio(song_source, format="audio/mp3", autoplay=True, loop=True)
                elif os.path.exists(song_source):
                    with open(song_source, "rb") as f:
                        st.audio(f.read(), format="audio/mp3", autoplay=True, loop=True)
            with col_skip:
                if st.button("⏭ Próxima // Next", key="next_song", use_container_width=True):
                    st.session_state.current_song = (st.session_state.current_song + 1) % len(st.session_state.playlist)
                    st.rerun()
        else:
            st.warning("⚠️ Nenhuma música (.mp3) encontrada. Certifique-se de que a pasta 'songs' com 'song1.mp3' e 'song2.mp3' está presente!")

    # Telas do Jogo
    if st.session_state.game_state == "SELECT_LANG":
        render_lang_select()
    elif st.session_state.game_state == "INTRO_DONKI":
        render_donki_intro()
    elif st.session_state.game_state == "PLAYING":
        render_gameplay()
    elif st.session_state.game_state in ("FAIL_O2", "FAIL_RAD", "VICTORY"):
        render_modal()

def render_lang_select():
    """Tela de Seleção de Idioma."""
    st.markdown("---")
    st.subheader("SELECIONE O IDIOMA // SELECT LANGUAGE")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🇧🇷 1. PORTUGUÊS (BRASIL)", key="lang_pt", use_container_width=True):
            st.session_state.lang = "pt"
            st.session_state.sim.evento_clima = st.session_state.sim.sortear_clima("pt")
            st.session_state.game_state = "INTRO_DONKI"
            st.rerun()
    with c2:
        if st.button("🇺🇸 2. ENGLISH (UNITED STATES)", key="lang_en", use_container_width=True):
            st.session_state.lang = "en"
            st.session_state.sim.evento_clima = st.session_state.sim.sortear_clima("en")
            st.session_state.game_state = "INTRO_DONKI"
            st.rerun()

def render_donki_intro():
    """Tela com o mascote Luna-Bot explicando o sistema DONKI."""
    st.markdown("---")
    col_img, col_text = st.columns([1, 2])
    with col_img:
        mascot_url = locate_asset("mascot.png")
        if mascot_url:
            st.image(mascot_url, caption="Luna-Bot (LB-01)", use_container_width=True)
    with col_text:
        st.subheader(TEXTS[st.session_state.lang]["intro_greeting"])
        linhas = [
            TEXTS[st.session_state.lang]["intro_p1"],
            TEXTS[st.session_state.lang]["intro_p2"],
            TEXTS[st.session_state.lang]["intro_p3"],
            TEXTS[st.session_state.lang]["intro_p4"],
            TEXTS[st.session_state.lang]["intro_p5"],
        ]
        for l in linhas:
            st.write(l)
        if st.button(TEXTS[st.session_state.lang]["intro_btn"], key="start_mission", use_container_width=True):
            st.session_state.game_state = "PLAYING"
            st.rerun()
    st.markdown("---")

def render_gameplay():
    """Tela principal do jogo com telemetria, ícones ampliados, cenário e ações."""
    sim = st.session_state.sim
    lang = st.session_state.lang

    # Status do Dia e Clima Solar DONKI
    clima = sim.evento_clima
    cor_clima = "🟢" if clima["classe"] == "Normal" else "🟡" if "M" in clima["classe"] else "🔴"
    
    st.markdown(
        f"### 🚀 {TEXTS[lang]['day']} {sim.dia} &nbsp;&nbsp;|&nbsp;&nbsp; "
        f"{cor_clima} **{TEXTS[lang]['weather_label']}** {clima['tipo']} ({clima['classe']}) — {clima['radiacao_uSv']} µSv/h"
    )

    # Alerta visual de CME se ativo
    if clima.get("is_cme", False):
        cme_url = locate_asset("alert_cme.png")
        if cme_url:
            st.image(cme_url, width=280)

    # Painel de Telemetria com os ÍCONES REAIS DO JOGO (85px)
    cols = st.columns(6)
    recursos = [
        ("icon_o2.png", TEXTS[lang]["res_o2"], f"{sim.oxigenio}%"),
        ("icon_ice.png", TEXTS[lang]["res_ice"], f"{sim.gelo}%"),
        ("icon_energy.png", TEXTS[lang]["res_energy"], f"{sim.energia} kW"),
        ("icon_science.png", TEXTS[lang]["res_science"], f"{sim.ciencia}/100"),
        ("icon_radiation.png", TEXTS[lang]["res_radiation"], f"{sim.radiacao:.1f} mSv"),
        ("icon_health.png", TEXTS[lang]["res_health"], f"{sim.saude}%"),
    ]

    for i, (icon_name, nome_rec, val_rec) in enumerate(recursos):
        with cols[i]:
            icon_url = locate_asset(icon_name)
            if icon_url:
                st.image(icon_url, width=85)
            st.metric(nome_rec, val_rec)

    # Cenário Lunar Atual (bg_lunar, bunker_background ou rover_background)
    if st.session_state.bg_current:
        st.image(st.session_state.bg_current, use_container_width=True)

    # Se o fundo for o padrão, mostramos as entidades da base
    bg_lunar_path = locate_asset("bg_lunar.png")
    if st.session_state.bg_current == bg_lunar_path:
        cb, cr = st.columns(2)
        with cb:
            b_url = locate_asset("bunker.png")
            if b_url:
                st.image(b_url, caption="Bunker de Regolito", width=180)
        with cr:
            r_url = locate_asset("rover.png")
            if r_url:
                st.image(r_url, caption="Rover Artemis", width=180)

    # Barra de Feedback do Mascote Luna-Bot
    col_mini, col_msg = st.columns([1, 8])
    with col_mini:
        mini_mascot = locate_asset("mascot.png")
        if mini_mascot:
            st.image(mini_mascot, width=70)
    with col_msg:
        if "ALERTA" in st.session_state.feedback_msg:
            st.error(st.session_state.feedback_msg)
        else:
            st.info(st.session_state.feedback_msg)

    # Ações diárias
    st.write(f"**{TEXTS[lang]['prompt']}**")
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button(f"{TEXTS[lang]['opt1_title']}\n\n{TEXTS[lang]['opt1_desc']}", key="opt1", use_container_width=True):
            _apply_choice(1)
            st.rerun()
    with c2:
        if st.button(f"{TEXTS[lang]['opt2_title']}\n\n{TEXTS[lang]['opt2_desc']}", key="opt2", use_container_width=True):
            _apply_choice(2)
            st.rerun()
    with c3:
        if st.button(f"{TEXTS[lang]['opt3_title']}\n\n{TEXTS[lang]['opt3_desc']}", key="opt3", use_container_width=True):
            _apply_choice(3)
            st.rerun()

def _apply_choice(choice: int):
    """Processa o turno e atualiza o fundo e feedback."""
    sim = st.session_state.sim
    lang = st.session_state.lang
    feedback = sim.aplicar_turno(choice, lang)
    st.session_state.feedback_msg = feedback

    # Atualiza o fundo lunar correspondente
    if choice == 1:
        st.session_state.bg_current = locate_asset("bg_lunar.png")
    elif choice == 2:
        st.session_state.bg_current = locate_asset("bunker_background.png")
    elif choice == 3:
        st.session_state.bg_current = locate_asset("rover_background.png")

    # Verifica vitória ou derrota
    if sim.oxigenio <= 0:
        st.session_state.game_state = "FAIL_O2"
    elif sim.saude <= 0:
        st.session_state.game_state = "FAIL_RAD"
    elif sim.ciencia >= sim.meta_ciencia:
        st.session_state.game_state = "VICTORY"

def render_modal():
    """Tela de fim de jogo (Vitória / Derrota)."""
    lang = st.session_state.lang
    if st.session_state.game_state == "FAIL_O2":
        st.error(f"## {TEXTS[lang]['fail_o2_title']}\n\n{TEXTS[lang]['fail_o2_desc']}")
    elif st.session_state.game_state == "FAIL_RAD":
        st.error(f"## {TEXTS[lang]['fail_rad_title']}\n\n{TEXTS[lang]['fail_rad_desc']}")
    elif st.session_state.game_state == "VICTORY":
        st.success(f"## {TEXTS[lang]['win_title']}\n\n{TEXTS[lang]['win_desc']}")

    if st.button(TEXTS[lang]["btn_restart"], key="restart", use_container_width=True):
        st.session_state.sim.reset()
        st.session_state.bg_current = locate_asset("bg_lunar.png")
        st.session_state.game_state = "PLAYING"
        st.session_state.feedback_msg = "[STATUS]: Missão reiniciada! Prepare a base, Comandante."
        st.rerun()
