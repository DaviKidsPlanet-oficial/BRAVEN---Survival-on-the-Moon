"""
Artemis Base Camp: Lunar Outpost Commander (Pygame Edition)
- Fluxo: 1) Seleção de Idioma -> 2) Briefing do Luna-Bot sobre o DONKI -> 3) Jogo Ativo.
- Título do mascote reposicionado para a esquerda, sem vazar da caixa.
- Sem caracteres de emojis (evita retângulos vazios).
- Imagens em proporção natural (sem esticar).
"""

import os
import sys
import math
import random
import pygame

# ==========================================
# 1. CONFIGURAÇÃO DE DIRETÓRIOS E ASSETS
# ==========================================
POSSIBLE_ASSET_DIRS = [
    r"C:\Users\Pichau\Desktop\Clube Nicolinha\space_outpost_game\assets",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets"),
    r"C:\Users\Pichau\.gemini\antigravity\brain\b5c774e8-cb64-4879-b8f8-f3535b4adb02",
]

POSSIBLE_SONG_DIRS = [
    r"C:\Users\Pichau\Desktop\Clube Nicolinha\space_outpost_game\songs",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "songs"),
    r"C:\Users\Pichau\.gemini\antigravity\brain\b5c774e8-cb64-4879-b8f8-f3535b4adb02\songs",
]

def load_image(filename, fallback_size=(64, 64), fallback_color=(80, 80, 100)):
    """Carrega uma imagem PNG com suporte a fallback."""
    for asset_dir in POSSIBLE_ASSET_DIRS:
        full_path = os.path.join(asset_dir, filename)
        if os.path.exists(full_path):
            try:
                return pygame.image.load(full_path).convert_alpha()
            except Exception as e:
                print(f"Erro ao carregar {full_path}: {e}")
    
    surf = pygame.Surface(fallback_size, pygame.SRCALPHA)
    surf.fill(fallback_color)
    return surf

def scale_keep_aspect(img, max_w, max_h):
    """Redimensiona preservando a proporção original e recortando margens vazias."""
    orig_w, orig_h = img.get_size()
    try:
        bbox = img.get_bounding_rect()
        if bbox.width > 20 and bbox.height > 20 and (bbox.width < orig_w - 15 or bbox.height < orig_h - 15):
            img = img.subsurface(bbox)
            orig_w, orig_h = img.get_size()
    except Exception:
        pass

    ratio = min(max_w / orig_w, max_h / orig_h)
    new_w = max(1, int(orig_w * ratio))
    new_h = max(1, int(orig_h * ratio))
    return pygame.transform.smoothscale(img, (new_w, new_h))

# ==========================================
# 2. DICIONÁRIO DE IDIOMAS (100% SEM EMOJIS)
# ==========================================
TEXTS = {
    "pt": {
        "title": "NASA ARTEMIS BASE CAMP // POLO SUL LUNAR",
        "day": "Dia da Missão",
        "res_o2": "Oxigênio",
        "res_ice": "Gelo Polar",
        "res_energy": "Energia",
        "res_science": "Ciência",
        "res_radiation": "Radiação",
        "res_health": "Saúde",
        "prompt": "Selecione a operação do Artemis Base Camp para hoje (100 kW disponíveis):",
        "opt1_title": "1. Usina de Oxigênio",
        "opt1_desc": "+25% O2 | +10 Ciência (Gasta 60 kW no regolito)",
        "opt2_title": "2. Abrigo Subterrâneo",
        "opt2_desc": "Bunker de Regolito (-90% Radiação, Imune a CME)",
        "opt3_title": "3. Expedição Rover",
        "opt3_desc": "+15 Ciência | +5% Gelo | Pouco O2 (-2%)",
        "feedback_opt1": "[OK] Oxigênio extraído do solo lunar com sucesso! (+25% O2)",
        "feedback_opt2": "[OK] Tripulação segura no abrigo subterrâneo de regolito!",
        "feedback_opt3": "[OK] Rover coletou amostras valiosas nas crateras escuras!",
        "alert_acute": "[ALERTA MÉDICO]: Tripulação irradiada pela tempestade! -{dano}% de Saúde!",
        "alert_safe": "[DEFESA]: O bunker de regolito bloqueou a tempestade solar!",
        "weather_label": "Detector Solar DONKI:",
        "fail_o2_title": "FALHA: OXIGÊNIO ESGOTADO",
        "fail_o2_desc": "O oxigênio acabou. A tripulação teve que evacuar na cápsula Orion.",
        "fail_rad_title": "FALHA: RADIAÇÃO LETAL",
        "fail_rad_desc": "Exposição excessiva a partículas solares. Retorno de emergência à Terra.",
        "win_title": "VITÓRIA: MISSÃO ARTEMIS CONCLUÍDA!",
        "win_desc": "Você provou que a presença humana sustentável na Lua é viável!",
        "btn_restart": "Jogar Novamente",
        "bunker_label": "Bunker de Regolito",
        "rover_label": "Rover Artemis",
        "btn_lang": "IDIOMA: PT",
        "btn_music_on": "MUSICA: ON",
        "btn_music_off": "MUSICA: OFF",
        # Transmissão de Apresentação do DONKI
        "intro_tag": "TRANSMISSÃO DE ENTRADA // NASA ARTEMIS",
        "intro_greeting": "Olá, Comandante! Sou o Luna-Bot, seu assistente na Lua!",
        "intro_p1": "Antes de começar a missão, preciso te explicar o que é o sistema DONKI da NASA.",
        "intro_p2": "DONKI significa 'Banco de Dados de Notificações de Clima Espacial'.",
        "intro_p3": "Ele vigia o Sol 24 horas por dia para detectar erupções e tempestades solares (CME).",
        "intro_p4": "Na Lua NÃO há atmosfera para nos proteger! Quando o DONKI acusar perigo vermelho,",
        "intro_p5": "você deve ordenar a tripulação para o Bunker de Regolito, evitando radiação letal!",
        "intro_btn": "ENTENDIDO, INICIAR MISSÃO!",
        "scene_bunker_title": "ABRIGO DE REGOLITO ATIVADO",
        "scene_bunker_desc": "A tripulação está segura dentro do bunker subterrâneo.",
        "scene_rover_title": "EXPEDIÇÃO ROVER EM ANDAMENTO",
        "scene_rover_desc": "O rover está coletando amostras nas crateras escuras.",
        "scene_continue": "CONTINUAR",
    },
    "en": {
        "title": "NASA ARTEMIS BASE CAMP // LUNAR SOUTH POLE",
        "day": "Mission Day",
        "res_o2": "Oxygen",
        "res_ice": "Polar Ice",
        "res_energy": "Energy",
        "res_science": "Science",
        "res_radiation": "Radiation",
        "res_health": "Health",
        "prompt": "Select operations plan for today (Available: 100 kW):",
        "opt1_title": "1. Oxygen Extraction",
        "opt1_desc": "+25% O2 | +10 Science (60 kW to regolith reactor)",
        "opt2_title": "2. Regolith Shelter",
        "opt2_desc": "Underground Bunker (-90% Radiation, Immune to CME)",
        "opt3_title": "3. Rover Ice Mission",
        "opt3_desc": "+35 Science | +15% Ice | Minimal O2 (+4%)",
        "feedback_opt1": "[OK] Breathable oxygen extracted from lunar soil! (+25% O2)",
        "feedback_opt2": "[OK] Crew secured safely inside the regolith bunker!",
        "feedback_opt3": "[OK] Rover harvested primordial ice in dark craters!",
        "alert_acute": "[MEDICAL ALERT]: Crew irradiated by solar storm! -{dano}% Health!",
        "alert_safe": "[DEFENSE]: The bunker successfully shielded the crew from solar particles!",
        "weather_label": "DONKI Solar Monitor:",
        "fail_o2_title": "MISSION FAILED: OXYGEN DEPLETED",
        "fail_o2_desc": "Life support drained. Crew evacuated aboard the Orion spacecraft.",
        "fail_rad_title": "MISSION FAILED: LETHAL RADIATION",
        "fail_rad_desc": "Severe solar radiation incapacitated the crew. Mission aborted.",
        "win_title": "VICTORY: ARTEMIS MISSION ACCOMPLISHED!",
        "win_desc": "You proved humanity can thrive sustainably on the Moon!",
        "btn_restart": "Play Again",
        "bunker_label": "Regolith Bunker",
        "rover_label": "Artemis Rover",
        "btn_lang": "LANG: EN",
        "btn_music_on": "MUSIC: ON",
        "btn_music_off": "MUSIC: OFF",
        # DONKI Intro Briefing
        "intro_tag": "INCOMING TRANSMISSION // NASA ARTEMIS",
        "intro_greeting": "Hello, Commander! I am Luna-Bot, your lunar assistant!",
        "intro_p1": "Before you take command, I must explain NASA's DONKI space weather system.",
        "intro_p2": "DONKI stands for 'Database Of Notifications, Knowledge, and Information'.",
        "intro_p3": "It monitors the Sun 24/7 to detect solar flares and proton storms (CMEs).",
        "intro_p4": "The Moon has NO atmosphere to shield us! Whenever DONKI shows high radiation,",
        "intro_p5": "you must shelter the crew in the Regolith Bunker to prevent acute injury!",
        "intro_btn": "UNDERSTOOD, START MISSION!",
        "scene_bunker_title": "REGOLITH SHELTER ACTIVATED",
        "scene_bunker_desc": "The crew is safely inside the underground bunker.",
        "scene_rover_title": "ROVER EXPEDITION UNDERWAY",
        "scene_rover_desc": "The rover is collecting samples in the dark craters.",
        "scene_continue": "CONTINUE",
    }
}

# ==========================================
# 3. LÓGICA DO JOGO E SIMULAÇÃO DONKI
# ==========================================
class LunarSimulation:
    def __init__(self):
        self.reset()

    def reset(self):
        self.dia = 1
        self.oxigenio = 100
        self.gelo = 80
        self.energia = 100
        self.ciencia = 0
        self.radiacao = 0.0
        self.saude = 100
        self.meta_ciencia = 100
        self.evento_clima = self.sortear_clima("pt")

    @staticmethod
    def sortear_clima(lang):
        if lang == "pt":
            eventos = [
                {"tipo": "Vento Solar Calmo", "classe": "Normal", "radiacao_uSv": 20, "is_cme": False},
                {"tipo": "Erupção Solar M", "classe": "M2.4", "radiacao_uSv": 75, "is_cme": False},
                {"tipo": "Ejeção de Massa Coronal X", "classe": "X3.1", "radiacao_uSv": 160, "is_cme": True}
            ]
        else:
            eventos = [
                {"tipo": "Calm Solar Wind", "classe": "Normal", "radiacao_uSv": 20, "is_cme": False},
                {"tipo": "Solar Flare M-Class", "classe": "M2.4", "radiacao_uSv": 75, "is_cme": False},
                {"tipo": "Coronal Mass Ejection X", "classe": "X3.1", "radiacao_uSv": 160, "is_cme": True}
            ]
        return random.choices(eventos, weights=[0.55, 0.30, 0.15], k=1)[0]

    def aplicar_turno(self, escolha, lang):
        self.oxigenio = max(0, self.oxigenio - 12)
        em_abrigo = False
        feedback = ""

        if escolha == 1:
            self.oxigenio = min(100, self.oxigenio + 25)
            self.ciencia += 10
            feedback = TEXTS[lang]["feedback_opt1"]
        elif escolha == 2:
            em_abrigo = True
            self.oxigenio = min(100, self.oxigenio + 8)
            feedback = TEXTS[lang]["feedback_opt2"]
        elif escolha == 3:
            # Rover expedition is tougher: slight oxygen loss, reduced gains
            self.oxigenio = max(0, self.oxigenio - (2/100) * self.oxigenio)  # -2% O2
            self.gelo = min(100, self.gelo + 5)
            self.ciencia += 10
            feedback = TEXTS[lang]["feedback_opt3"]

        dose_uSv = self.evento_clima["radiacao_uSv"]
        classe = self.evento_clima["classe"]

        dose_real = dose_uSv * 0.10 if em_abrigo else dose_uSv
        self.radiacao += (dose_real / 10.0)

        # Dano agudo imediato
        dano_agudo = 0
        if not em_abrigo:
            if "X" in classe:
                dano_agudo = 35
            elif "M" in classe:
                dano_agudo = 15

        if dano_agudo > 0:
            self.saude = max(0, self.saude - dano_agudo)
            feedback += " " + TEXTS[lang]["alert_acute"].format(dano=dano_agudo)
        elif em_abrigo and classe != "Normal":
            feedback += " " + TEXTS[lang]["alert_safe"]

        if self.radiacao > 45:
            dano_cronico = int((self.radiacao - 45) * 0.4)
            self.saude = max(0, self.saude - dano_cronico)

        self.dia += 1
        self.evento_clima = self.sortear_clima(lang)
        return feedback

# ==========================================
# 4. INTERFACE GRÁFICA PRINCIPAL
# ==========================================
class ArtemisGameGUI:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        
        self.WIDTH = 1280
        self.HEIGHT = 720
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        self.screen = pygame.display.set_mode(
            (self.WIDTH, self.HEIGHT),          # size you already use
            pygame.FULLSCREEN                    # <‑‑ add this flag
        )
        pygame.display.set_caption("NASA Artemis Base Camp - Lunar Outpost Commander")
        
        self.clock = pygame.time.Clock()
        self.lang = "pt"
        self.sim = LunarSimulation()
        self.feedback_msg = "[STATUS]: Base operacional! Selecione uma ordem diária, Comandante."
        
        # 1) O jogo começa na tela de ESCOLHA DE IDIOMA!
        self.game_state = "SELECT_LANG"

        # Sistema de Música (Playlist song1 -> song2 -> song1)
        self.music_enabled = False
        self.playlist = []
        self.current_song_index = 0
        self.MUSIC_END_EVENT = pygame.USEREVENT + 1
        pygame.mixer.music.set_endevent(self.MUSIC_END_EVENT)
        self.carregar_musicas()

        # Fontes limpas e legíveis
        self.font_title = pygame.font.SysFont("segoe ui, arial, sans-serif", 24, bold=True)
        self.font_intro_title = pygame.font.SysFont("segoe ui, arial, sans-serif", 20, bold=True)
        self.font_med = pygame.font.SysFont("segoe ui, arial, sans-serif", 16, bold=True)
        self.font_small = pygame.font.SysFont("segoe ui, arial, sans-serif", 14)
        self.font_intro = pygame.font.SysFont("segoe ui, arial, sans-serif", 15)
        self.font_btn = pygame.font.SysFont("segoe ui, arial, sans-serif", 15, bold=True)

        self.carregar_assets()

    def carregar_assets(self):
        # Fundos Lunares (Padrão, Bunker e Rover)
        raw_bg = load_image("bg_lunar.png", (1280, 720), (10, 15, 30))
        self.bg_default = pygame.transform.smoothscale(raw_bg, (1280, 720))

        raw_bunker_bg = load_image("bunker_background.png", (1280, 720), (20, 30, 50))
        self.bg_bunker = pygame.transform.smoothscale(raw_bunker_bg, (1280, 720))

        raw_rover_bg = load_image("rover_background.png", (1280, 720), (20, 30, 50))
        self.bg_rover = pygame.transform.smoothscale(raw_rover_bg, (1280, 720))

        # Fundo lunar atualmente ativo na tela principal
        self.bg_current = self.bg_default

        # Banner Superior
        raw_banner = load_image("banner_mission.png", (480, 80))
        self.banner = scale_keep_aspect(raw_banner, max_w=480, max_h=75)

        # Painel UI ampliado
        self.PANEL_W = 640
        self.PANEL_H = 455
        raw_panel = load_image("ui_panel.png", (self.PANEL_W, self.PANEL_H), (15, 25, 45))
        self.panel = pygame.transform.smoothscale(raw_panel, (self.PANEL_W, self.PANEL_H))

        # Alerta CME
        raw_cme = load_image("alert_cme.png", (320, 160))
        self.alert_cme = scale_keep_aspect(raw_cme, max_w=330, max_h=170)

        # Entidades da base
        raw_bunker = load_image("bunker.png", (240, 240))
        self.img_bunker = scale_keep_aspect(raw_bunker, max_w=240, max_h=240)

        raw_rover = load_image("rover.png", (240, 160))
        self.img_rover = scale_keep_aspect(raw_rover, max_w=240, max_h=160)

        # Mascote Luna-Bot
        raw_mascot = load_image("mascot.png", (220, 240), (40, 120, 180))
        self.img_mascot_big = scale_keep_aspect(raw_mascot, max_w=220, max_h=240)
        self.img_mascot_mini = scale_keep_aspect(raw_mascot, max_w=75, max_h=80)

        # Ícones dos recursos
        ICON_SZ = 44
        self.icons = {
            "o2": scale_keep_aspect(load_image("icon_o2.png"), ICON_SZ, ICON_SZ),
            "ice": scale_keep_aspect(load_image("icon_ice.png"), ICON_SZ, ICON_SZ),
            "energy": scale_keep_aspect(load_image("icon_energy.png"), ICON_SZ, ICON_SZ),
            "science": scale_keep_aspect(load_image("icon_science.png"), ICON_SZ, ICON_SZ),
            "radiation": scale_keep_aspect(load_image("icon_radiation.png"), ICON_SZ, ICON_SZ),
            "health": scale_keep_aspect(load_image("icon_health.png"), ICON_SZ, ICON_SZ),
        }

        # Cursor
        raw_cursor = load_image("cursor.png", (34, 34))
        self.cursor = scale_keep_aspect(raw_cursor, 34, 34)
        pygame.mouse.set_visible(False)

    def carregar_musicas(self):
        """Encontra as músicas song1.mp3 e song2.mp3 nas pastas configuradas."""
        self.playlist = []
        for song_name in ["song1.mp3", "song2.mp3"]:
            for s_dir in POSSIBLE_SONG_DIRS:
                full_path = os.path.join(s_dir, song_name)
                if os.path.exists(full_path):
                    self.playlist.append(full_path)
                    break
        print(f"[AUDIO]: {len(self.playlist)} músicas carregadas na playlist.")

    def tocar_musica_atual(self):
        """Toca a música correspondente ao índice atual da playlist."""
        if not self.music_enabled or not self.playlist:
            return
        try:
            song_path = self.playlist[self.current_song_index]
            pygame.mixer.music.load(song_path)
            pygame.mixer.music.set_volume(0.6)
            pygame.mixer.music.play()
            print(f"[AUDIO]: Tocando {os.path.basename(song_path)}")
        except Exception as e:
            print(f"[AUDIO] Erro ao reproduzir música: {e}")

    def avancar_musica(self):
        """Passa para a próxima música e reinicia em loop se chegar ao fim."""
        if not self.playlist:
            return
        self.current_song_index = (self.current_song_index + 1) % len(self.playlist)
        self.tocar_musica_atual()

    def alternar_musica(self):
        """Liga ou desliga a música de fundo."""
        self.music_enabled = not self.music_enabled
        if self.music_enabled:
            self.tocar_musica_atual()
        else:
            pygame.mixer.music.stop()

    def draw_bar(self, x, y, w, h, value, max_val, color):
        pygame.draw.rect(self.screen, (20, 25, 40), (x, y, w, h), border_radius=4)
        pct = max(0.0, min(1.0, value / max_val))
        fill_w = int(w * pct)
        if fill_w > 0:
            pygame.draw.rect(self.screen, color, (x, y, fill_w, h), border_radius=4)
        pygame.draw.rect(self.screen, (80, 110, 160), (x, y, w, h), 1, border_radius=4)

    def draw_telemetry(self):
        px, py = 0, 88
        self.screen.blit(self.panel, (px, py))

        OFFSET_X = 45

        t_label = self.font_med.render(f"[STATUS] {TEXTS[self.lang]['day']} {self.sim.dia}", True, (220, 240, 255))
        self.screen.blit(t_label, (px + 22 + OFFSET_X, py + 16))

        resources = [
            ("o2", TEXTS[self.lang]["res_o2"], f"{self.sim.oxigenio}%", self.sim.oxigenio, 100, 
             (50, 220, 100) if self.sim.oxigenio > 40 else (240, 60, 60)),
            ("ice", TEXTS[self.lang]["res_ice"], f"{self.sim.gelo}%", self.sim.gelo, 100, (100, 190, 255)),
            ("energy", TEXTS[self.lang]["res_energy"], f"{self.sim.energia} kW", self.sim.energia, 100, (255, 215, 0)),
            ("science", TEXTS[self.lang]["res_science"], f"{self.sim.ciencia}/100", self.sim.ciencia, 100, (220, 130, 255)),
            ("radiation", TEXTS[self.lang]["res_radiation"], f"{self.sim.radiacao:.1f} mSv", self.sim.radiacao, 45, 
             (255, 70, 70) if self.sim.radiacao > 35 else (255, 160, 50)),
            ("health", TEXTS[self.lang]["res_health"], f"{self.sim.saude}%", self.sim.saude, 100, 
             (50, 220, 100) if self.sim.saude > 50 else (240, 50, 50)),
        ]

        row_y = py + 50
        for key, name, val_str, val, max_v, bar_color in resources:
            icon_img = self.icons[key]
            self.screen.blit(icon_img, (px + 20 + OFFSET_X, row_y))

            lbl = self.font_med.render(name, True, (210, 225, 245))
            val_txt = self.font_small.render(val_str, True, (255, 255, 255))
            
            self.screen.blit(lbl, (px + 72 + OFFSET_X, row_y + 2))
            self.screen.blit(val_txt, (px + 72 + OFFSET_X, row_y + 22))

            self.draw_bar(px + 225 + OFFSET_X, row_y + 12, 240, 18, val, max_v, bar_color)
            row_y += 50

        clima = self.sim.evento_clima
        cor_clima = (100, 255, 120) if clima["classe"] == "Normal" else (255, 215, 0) if "M" in clima["classe"] else (255, 70, 70)
        info_txt = f"{TEXTS[self.lang]['weather_label']} {clima['tipo']} ({clima['classe']})  |  {clima['radiacao_uSv']} µSv/h"
        lbl_clima = self.font_small.render(info_txt, True, cor_clima)
        self.screen.blit(lbl_clima, (px + 22 + OFFSET_X, py + 368))

    def draw_lunar_entities(self):
        # Apenas exibe as entidades isoladas quando o fundo padrão estiver ativo.
        # Quando um fundo temático (Bunker ou Rover) estiver ativo, ele assume o cenário.
        if self.bg_current == self.bg_default:
            bx, by = 710, 230
            rx, ry = 970, 290

            # Bunker de regolito
            self.screen.blit(self.img_bunker, (bx, by))
            lbl_b = self.font_med.render(TEXTS[self.lang]["bunker_label"], True, (220, 235, 255))
            self.screen.blit(lbl_b, (bx + (self.img_bunker.get_width() - lbl_b.get_width()) // 2, by + self.img_bunker.get_height() + 5))

            # Rover
            self.screen.blit(self.img_rover, (rx, ry))
            lbl_r = self.font_med.render(TEXTS[self.lang]["rover_label"], True, (220, 235, 255))
            self.screen.blit(lbl_r, (rx + (self.img_rover.get_width() - lbl_r.get_width()) // 2, ry + self.img_rover.get_height() + 5))

        # Alerta CME proporcional e pulsante (sempre visível em caso de tempestade solar)
        if self.sim.evento_clima.get("is_cme", False):
            alpha = int(200 + 55 * math.sin(pygame.time.get_ticks() * 0.009))
            temp_alert = self.alert_cme.copy()
            temp_alert.set_alpha(alpha)
            self.screen.blit(temp_alert, (780, 50))

    def draw_action_buttons(self, mouse_pos):
        prompt_lbl = self.font_med.render(TEXTS[self.lang]["prompt"], True, (255, 220, 100))
        self.screen.blit(prompt_lbl, (25, 520))

        btn_y = 545
        btn_w, btn_h = 390, 82
        
        cards = [
            (1, 25, btn_y, TEXTS[self.lang]["opt1_title"], TEXTS[self.lang]["opt1_desc"], (25, 75, 45)),
            (2, 445, btn_y, TEXTS[self.lang]["opt2_title"], TEXTS[self.lang]["opt2_desc"], (35, 50, 95)),
            (3, 865, btn_y, TEXTS[self.lang]["opt3_title"], TEXTS[self.lang]["opt3_desc"], (30, 70, 90)),
        ]

        self.btn_rects = []
        for opt_num, bx, by, title, desc, base_color in cards:
            rect = pygame.Rect(bx, by, btn_w, btn_h)
            self.btn_rects.append((opt_num, rect))

            is_hover = (self.game_state == "PLAYING") and rect.collidepoint(mouse_pos)
            color = (min(255, base_color[0] + 35), min(255, base_color[1] + 35), min(255, base_color[2] + 45)) if is_hover else base_color

            pygame.draw.rect(self.screen, color, rect, border_radius=8)
            border_col = (255, 230, 100) if is_hover else (90, 130, 180)
            pygame.draw.rect(self.screen, border_col, rect, 2, border_radius=8)

            t_surf = self.font_btn.render(title, True, (255, 255, 255))
            d_surf = self.font_small.render(desc, True, (210, 230, 250))
            self.screen.blit(t_surf, (bx + 14, by + 14))
            self.screen.blit(d_surf, (bx + 14, by + 44))

    def draw_feedback_bar(self):
        fy = 638
        pygame.draw.rect(self.screen, (12, 18, 30), (25, fy, 1230, 68), border_radius=6)
        pygame.draw.rect(self.screen, (50, 75, 120), (25, fy, 1230, 68), 1, border_radius=6)

        self.screen.blit(self.img_mascot_mini, (32, fy - 6))

        color = (255, 90, 90) if "ALERTA" in self.feedback_msg else (180, 240, 255)
        txt = self.font_small.render(self.feedback_msg, True, color)
        self.screen.blit(txt, (115, fy + 24))

    def draw_lang_select(self, mouse_pos):
        """Tela inicial de seleção de idioma."""
        overlay = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
        overlay.fill((5, 12, 25, 235))
        self.screen.blit(overlay, (0, 0))

        mw, mh = 660, 340
        mx = (self.WIDTH - mw) // 2
        my = (self.HEIGHT - mh) // 2

        pygame.draw.rect(self.screen, (15, 24, 44), (mx, my, mw, mh), border_radius=14)
        pygame.draw.rect(self.screen, (60, 160, 255), (mx, my, mw, mh), 2, border_radius=14)

        t1 = self.font_title.render("NASA ARTEMIS BASE CAMP", True, (100, 220, 255))
        t2 = self.font_med.render("SELECIONE O IDIOMA // SELECT LANGUAGE", True, (255, 225, 100))
        self.screen.blit(t1, (mx + (mw - t1.get_width()) // 2, my + 40))
        self.screen.blit(t2, (mx + (mw - t2.get_width()) // 2, my + 80))

        # Botão Português
        btn_w, btn_h = 420, 56
        bx = mx + (mw - btn_w) // 2
        by_pt = my + 145
        self.btn_lang_pt = pygame.Rect(bx, by_pt, btn_w, btn_h)

        is_hover_pt = self.btn_lang_pt.collidepoint(mouse_pos)
        col_pt = (35, 100, 60) if is_hover_pt else (25, 75, 45)
        pygame.draw.rect(self.screen, col_pt, self.btn_lang_pt, border_radius=8)
        pygame.draw.rect(self.screen, (100, 255, 160), self.btn_lang_pt, 2, border_radius=8)

        txt_pt = self.font_btn.render("1. PORTUGUÊS (BRASIL)", True, (255, 255, 255))
        self.screen.blit(txt_pt, (bx + (btn_w - txt_pt.get_width()) // 2, by_pt + 18))

        # Botão Inglês
        by_en = my + 225
        self.btn_lang_en = pygame.Rect(bx, by_en, btn_w, btn_h)

        is_hover_en = self.btn_lang_en.collidepoint(mouse_pos)
        col_en = (35, 75, 120) if is_hover_en else (25, 55, 90)
        pygame.draw.rect(self.screen, col_en, self.btn_lang_en, border_radius=8)
        pygame.draw.rect(self.screen, (100, 200, 255), self.btn_lang_en, 2, border_radius=8)

        txt_en = self.font_btn.render("2. ENGLISH (UNITED STATES)", True, (255, 255, 255))
        self.screen.blit(txt_en, (bx + (btn_w - txt_en.get_width()) // 2, by_en + 18))

    def draw_donki_intro(self, mouse_pos):
        """Tela de tutorial com o mascote Luna-Bot explicando o DONKI."""
        overlay = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
        overlay.fill((5, 12, 25, 230))
        self.screen.blit(overlay, (0, 0))

        # Janela holográfica ampliada para 920px
        dw, dh = 920, 480
        dx = (self.WIDTH - dw) // 2
        dy = (self.HEIGHT - dh) // 2

        pygame.draw.rect(self.screen, (15, 25, 48), (dx, dy, dw, dh), border_radius=14)
        pygame.draw.rect(self.screen, (60, 160, 255), (dx, dy, dw, dh), 2, border_radius=14)

        # Cabeçalho da comunicação
        tag_surf = self.font_med.render(TEXTS[self.lang]["intro_tag"], True, (100, 220, 255))
        self.screen.blit(tag_surf, (dx + 30, dy + 22))
        pygame.draw.line(self.screen, (50, 100, 160), (dx + 30, dy + 52), (dx + dw - 30, dy + 52), 1)

        # Animação suave de flutuação do Luna-Bot
        float_y = int(math.sin(pygame.time.get_ticks() * 0.005) * 8)
        mascot_x = dx + 25
        mascot_y = dy + 85 + float_y
        self.screen.blit(self.img_mascot_big, (mascot_x, mascot_y))

        # Bloco de texto movido mais para a esquerda (tx = dx + 240)
        tx = dx + 240
        ty = dy + 75

        # Título amarelo ajustado para caber perfeitamente sem vazar
        greeting = self.font_intro_title.render(TEXTS[self.lang]["intro_greeting"], True, (255, 235, 100))
        self.screen.blit(greeting, (tx, ty))

        linhas = [
            TEXTS[self.lang]["intro_p1"],
            "",
            TEXTS[self.lang]["intro_p2"],
            TEXTS[self.lang]["intro_p3"],
            "",
            TEXTS[self.lang]["intro_p4"],
            TEXTS[self.lang]["intro_p5"],
        ]

        text_y = ty + 44
        for line in linhas:
            if line:
                cor = (255, 130, 130) if ("NÃO" in line or "NO atmosphere" in line or "Bunker" in line) else (215, 235, 255)
                f_surf = self.font_intro.render(line, True, cor)
                self.screen.blit(f_surf, (tx, text_y))
            text_y += 26

        # Botão [ INICIAR MISSÃO ]
        btn_w, btn_h = 280, 50
        btn_x = dx + (dw - btn_w) // 2 + 100
        btn_y = dy + dh - 75
        self.intro_btn_rect = pygame.Rect(btn_x, btn_y, btn_w, btn_h)

        is_hover = self.intro_btn_rect.collidepoint(mouse_pos)
        b_color = (40, 140, 80) if is_hover else (30, 105, 60)
        pygame.draw.rect(self.screen, b_color, self.intro_btn_rect, border_radius=8)
        pygame.draw.rect(self.screen, (100, 255, 160), self.intro_btn_rect, 2, border_radius=8)

        btn_txt = self.font_btn.render(TEXTS[self.lang]["intro_btn"], True, (255, 255, 255))
        self.screen.blit(btn_txt, (btn_x + (btn_w - btn_txt.get_width()) // 2, btn_y + 15))

    def draw_modal(self, title, desc, is_victory):
        overlay = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
        overlay.fill((5, 10, 20, 225))
        self.screen.blit(overlay, (0, 0))

        mw, mh = 700, 320
        mx, my = (self.WIDTH - mw) // 2, (self.HEIGHT - mh) // 2

        border_color = (60, 230, 120) if is_victory else (240, 60, 60)
        pygame.draw.rect(self.screen, (15, 22, 38), (mx, my, mw, mh), border_radius=12)
        pygame.draw.rect(self.screen, border_color, (mx, my, mw, mh), 2, border_radius=12)

        t_lbl = self.font_title.render(title, True, border_color)
        d_lbl = self.font_med.render(desc, True, (220, 230, 245))
        self.screen.blit(t_lbl, (mx + (mw - t_lbl.get_width()) // 2, my + 50))
        self.screen.blit(d_lbl, (mx + (mw - d_lbl.get_width()) // 2, my + 115))

        btn_w, btn_h = 240, 52
        btn_x = mx + (mw - btn_w) // 2
        btn_y = my + 210
        self.restart_rect = pygame.Rect(btn_x, btn_y, btn_w, btn_h)

        is_hover = self.restart_rect.collidepoint(pygame.mouse.get_pos())
        btn_col = (45, 120, 70) if is_hover else (35, 90, 55)
        pygame.draw.rect(self.screen, btn_col, self.restart_rect, border_radius=8)
        pygame.draw.rect(self.screen, (100, 255, 150), self.restart_rect, 1, border_radius=8)

        r_lbl = self.font_btn.render(TEXTS[self.lang]["btn_restart"], True, (255, 255, 255))
        self.screen.blit(r_lbl, (btn_x + (btn_w - r_lbl.get_width()) // 2, btn_y + 16))

    def run(self):
        running = True
        while running:
            mouse_pos = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False

                # Evento disparado automaticamente quando uma música termina
                elif event.type == self.MUSIC_END_EVENT:
                    if self.music_enabled:
                        self.avancar_musica()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_F11:      # press F11 to toggle
                        self.fullscreen = not getattr(self, "fullscreen", False)
                        flags = pygame.FULLSCREEN if self.fullscreen else 0
                        self.screen = pygame.display.set_mode(
                            (self.WIDTH, self.HEIGHT), flags
                        )

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    # 1. Clique na Tela de Escolha de Idioma
                    if self.game_state == "SELECT_LANG":
                        if hasattr(self, "btn_lang_pt") and self.btn_lang_pt.collidepoint(mouse_pos):
                            self.lang = "pt"
                            self.sim.evento_clima = self.sim.sortear_clima(self.lang)
                            self.game_state = "INTRO_DONKI"
                        elif hasattr(self, "btn_lang_en") and self.btn_lang_en.collidepoint(mouse_pos):
                            self.lang = "en"
                            self.sim.evento_clima = self.sim.sortear_clima(self.lang)
                            self.game_state = "INTRO_DONKI"

                    # Botão de alternar idioma no topo (ativo após a seleção inicial)
                    elif hasattr(self, "lang_btn_rect") and self.lang_btn_rect.collidepoint(mouse_pos):
                        self.lang = "en" if self.lang == "pt" else "pt"
                        self.sim.evento_clima = self.sim.sortear_clima(self.lang)

                    # Botão de alternar música ON/OFF
                    elif hasattr(self, "music_btn_rect") and self.music_btn_rect.collidepoint(mouse_pos):
                        self.alternar_musica()

                    # 2. Clique na tela de introdução do Luna-Bot
                    elif self.game_state == "INTRO_DONKI":
                        if hasattr(self, "intro_btn_rect") and self.intro_btn_rect.collidepoint(mouse_pos):
                            self.game_state = "PLAYING"

                    # 3. Decisões durante a partida
                    elif self.game_state == "PLAYING":
                        for opt_num, rect in self.btn_rects:
                            if rect.collidepoint(mouse_pos):
                                self.feedback_msg = self.sim.aplicar_turno(opt_num, self.lang)
                                if self.sim.oxigenio <= 0:
                                    self.game_state = "FAIL_O2"
                                elif self.sim.saude <= 0:
                                    self.game_state = "FAIL_RAD"
                                elif self.sim.ciencia >= self.sim.meta_ciencia:
                                    self.game_state = "VICTORY"
                                elif opt_num == 1:
                                    self.bg_current = self.bg_default
                                elif opt_num == 2:
                                    self.bg_current = self.bg_bunker
                                elif opt_num == 3:
                                    self.bg_current = self.bg_rover
                                break

                    # 4. Clique no modal de reinício
                    elif self.game_state in ["FAIL_O2", "FAIL_RAD", "VICTORY"]:
                        if hasattr(self, "restart_rect") and self.restart_rect.collidepoint(mouse_pos):
                            self.sim.reset()
                            self.bg_current = self.bg_default
                            self.game_state = "PLAYING"
                            self.feedback_msg = "[STATUS]: Missão reiniciada! Prepare a base, Comandante."

            # RENDERIZAÇÃO
            # 1. Limpa a tela inteira com cor preta/espaço profundo (evita qualquer rastro ou acúmulo de pixels transparentes)
            self.screen.fill((5, 10, 20))
            # 2. Desenha o fundo base lunar e, se ativo, o cenário temático
            self.screen.blit(self.bg_default, (0, 0))
            if self.bg_current != self.bg_default:
                self.screen.blit(self.bg_current, (0, 0))

            # Banner Superior
            self.screen.blit(self.banner, (25, 10))
            
            # Botão de Idioma (no canto superior direito)
            self.lang_btn_rect = pygame.Rect(self.WIDTH - 165, 18, 140, 42)
            is_lang_hover = self.lang_btn_rect.collidepoint(mouse_pos)
            l_bg = (40, 65, 100) if is_lang_hover else (25, 40, 65)
            pygame.draw.rect(self.screen, l_bg, self.lang_btn_rect, border_radius=6)
            pygame.draw.rect(self.screen, (100, 160, 230), self.lang_btn_rect, 1, border_radius=6)
            
            l_surf = self.font_btn.render(TEXTS[self.lang]["btn_lang"], True, (255, 255, 255))
            # Botão de alternar música (ao lado do botão de idioma)
            self.music_btn_rect = pygame.Rect(self.WIDTH - 325, 18, 140, 42)
            is_music_hover = self.music_btn_rect.collidepoint(mouse_pos)
            m_bg = (80, 50, 30) if is_music_hover else (60, 40, 20)
            pygame.draw.rect(self.screen, m_bg, self.music_btn_rect, border_radius=6)
            pygame.draw.rect(self.screen, (200, 150, 100), self.music_btn_rect, 1, border_radius=6)

            music_label = TEXTS[self.lang]["btn_music_on"] if self.music_enabled else TEXTS[self.lang]["btn_music_off"]
            m_surf = self.font_btn.render(music_label, True, (255, 255, 255))
            self.screen.blit(m_surf, (self.music_btn_rect.x + (self.music_btn_rect.w - m_surf.get_width()) // 2, self.music_btn_rect.y + 11))
            self.screen.blit(l_surf, (self.lang_btn_rect.x + (self.lang_btn_rect.w - l_surf.get_width()) // 2, self.lang_btn_rect.y + 11))

            # Componentes visuais da base
            self.draw_telemetry()
            self.draw_lunar_entities()
            self.draw_action_buttons(mouse_pos)
            self.draw_feedback_bar()

            # TELAS ESPECIAIS CONFORME O ESTADO DO JOGO:
            if self.game_state == "SELECT_LANG":
                self.draw_lang_select(mouse_pos)

            elif self.game_state == "INTRO_DONKI":
                self.draw_donki_intro(mouse_pos)

            elif self.game_state == "FAIL_O2":
                self.draw_modal(TEXTS[self.lang]["fail_o2_title"], TEXTS[self.lang]["fail_o2_desc"], False)
            elif self.game_state == "FAIL_RAD":
                self.draw_modal(TEXTS[self.lang]["fail_rad_title"], TEXTS[self.lang]["fail_rad_desc"], False)
            elif self.game_state == "VICTORY":
                self.draw_modal(TEXTS[self.lang]["win_title"], TEXTS[self.lang]["win_desc"], True)

            # Cursor
            self.screen.blit(self.cursor, (mouse_pos[0] - 4, mouse_pos[1] - 4))

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    app = ArtemisGameGUI()
    app.run()