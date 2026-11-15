"""Simulation logic extracted from the original Pygame game.
Only the non‑UI parts are kept: resource management, DONKI events,
and the apply‑turn method. This module can be imported by the Streamlit UI.
"""
import os, random

# Asset/search paths – used by UI to locate images/audio
POSSIBLE_ASSET_DIRS = [
    r"C:\\Users\\Pichau\\Desktop\\Clube Nicolinha\\space_outpost_game\\assets",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets"),
]
POSSIBLE_SONG_DIRS = [
    r"C:\\Users\\Pichau\\Desktop\\Clube Nicolinha\\space_outpost_game\\songs",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "songs"),
]

# ---------------------------------------------------------------------------
# Texts (same dictionary from the original game). Only a subset is needed for
# the Streamlit version, but we keep the full dict for completeness.
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
        "opt3_desc": "+35 Ciência | +15% Gelo | Pouco O2 (+4%)",
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
        "btn_lang": "IDIOMA: PT",
        "btn_music_on": "MÚSICA: ON",
        "btn_music_off": "MÚSICA: OFF",
        "intro_tag": "TRANSMISSÃO DE ENTRADA // NASA ARTEMIS",
        "intro_greeting": "Olá, Comandante! Sou o Luna-Bot, seu assistente na Lua!",
        "intro_p1": "Antes de começar a missão, preciso te explicar o que é o sistema DONKI da NASA.",
        "intro_p2": "DONKI significa 'Banco de Dados de Notificações de Clima Espacial'.",
        "intro_p3": "Ele vigia o Sol 24 horas por dia para detectar erupções e tempestades solares (CME).",
        "intro_p4": "Na Lua NÃO há atmosfera para nos proteger! Quando o DONKI acusar perigo vermelho,",
        "intro_p5": "você deve ordenar a tripulação para o Bunker de Regolito, evitando radiação letal!",
        "intro_btn": "ENTENDIDO, INICIAR MISSÃO!",
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
        "btn_lang": "LANG: EN",
        "btn_music_on": "MUSIC: ON",
        "btn_music_off": "MUSIC: OFF",
        "intro_tag": "INCOMING TRANSMISSION // NASA ARTEMIS",
        "intro_greeting": "Hello, Commander! I am Luna-Bot, your lunar assistant!",
        "intro_p1": "Before you take command, I must explain NASA's DONKI space weather system.",
        "intro_p2": "DONKI stands for 'Database Of Notifications, Knowledge, and Information'.",
        "intro_p3": "It monitors the Sun 24/7 to detect solar flares and proton storms (CMEs).",
        "intro_p4": "The Moon has NO atmosphere to shield us! Whenever DONKI shows high radiation,",
        "intro_p5": "you must shelter the crew in the Regolith Bunker to prevent acute injury!",
        "intro_btn": "UNDERSTOOD, START MISSION!",
    },
}

# ---------------------------------------------------------------------------
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
        self.evento_clima = self.sortear_clima("en")

    @staticmethod
    def sortear_clima(lang):
        if lang == "pt":
            eventos = [
                {"tipo": "Vento Solar Calmo", "classe": "Normal", "radiacao_uSv": 20, "is_cme": False},
                {"tipo": "Erupção Solar M", "classe": "M2.4", "radiacao_uSv": 75, "is_cme": False},
                {"tipo": "Ejeção de Massa Coronal X", "classe": "X3.1", "radiacao_uSv": 160, "is_cme": True},
            ]
        else:
            eventos = [
                {"tipo": "Calm Solar Wind", "classe": "Normal", "radiacao_uSv": 20, "is_cme": False},
                {"tipo": "Solar Flare M-Class", "classe": "M2.4", "radiacao_uSv": 75, "is_cme": False},
                {"tipo": "Coronal Mass Ejection X", "classe": "X3.1", "radiacao_uSv": 160, "is_cme": True},
            ]
        return random.choices(eventos, weights=[0.55, 0.30, 0.15], k=1)[0]

    def aplicar_turno(self, escolha, lang):
        # Base oxygen consumption each turn
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
            # Nerfed rover expedition (harder)
            self.oxigenio = max(0, self.oxigenio - 2)  # slight loss instead of gain
            self.gelo = min(100, self.gelo + 5)
            self.ciencia += 15
            feedback = TEXTS[lang]["feedback_opt3"]

        dose_uSv = self.evento_clima["radiacao_uSv"]
        classe = self.evento_clima["classe"]
        dose_real = dose_uSv * 0.10 if em_abrigo else dose_uSv
        self.radiacao += (dose_real / 10.0)

        # Acute damage
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
