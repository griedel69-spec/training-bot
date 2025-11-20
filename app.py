import streamlit as st
import google.generativeai as genai
import os
import random

# --- SEITEN-KONFIGURATION ---
st.set_page_config(page_title="Tourismus-Trainer", page_icon="🎲")

# --- PASSWORT ---
PASSWORT = "Start2025"

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔒 Login Tourismus-Training")
    eingabe = st.text_input("Code:", type="password")
    if st.button("Anmelden"):
        if eingabe == PASSWORT:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Falsch.")
    st.stop()

# --- SZENARIEN DEFINITIONEN (Der Pool an Möglichkeiten) ---
# Hier liegen die verschiedenen Varianten pro Kategorie

VARIANTS_HOTEL = [
    """Szenario A: 'Der Regen'.
    Du bist Herr Grander. Es ist 14:30 Uhr, du bist nass geworden. Zimmer nicht fertig.
    Du willst sofort duschen. Du bist arrogant und ungeduldig.""",
    
    """Szenario B: 'Die Minibar'.
    Du bist Herr Grander. Du checkst gerade aus. Auf der Rechnung stehen 35€ für Champagner aus der Minibar.
    Du hast den aber nie getrunken! Du witterst Betrug. Du bist misstrauisch und laut.""",
    
    """Szenario C: 'Der Lärm'.
    Du bist Herr Grander. Es ist 23:00 Uhr. Du rufst von Zimmer 305 an.
    Die Nachbarn schauen laut Fernsehen. Du kannst nicht schlafen. Du forderst, dass das sofort aufhört oder du willst ein anderes Zimmer."""
]

VARIANTS_SKISCHULE = [
    """Szenario A: 'Helikopter-Mom'.
    Du bist eine Mutter. Dein Kind Leo (6) hat im Kurs geweint.
    Du wirfst dem Skilehrer vor, er hätte Leo vernachlässigt. Du bist hysterisch.""",
    
    """Szenario B: 'Falsche Gruppe'.
    Du bist ein Vater. Dein Sohn ist in Gruppe 3 eingeteilt worden.
    Du bist überzeugt, er ist ein Profi und gehört in Gruppe 1. Das ist eine Beleidigung!
    Du bist besserwisserisch und arrogant.""",
]

VARIANTS_SEILBAHN = [
    """Szenario A: 'Das Drehkreuz'.
    Dein Skipass geht nicht. Du stehst seit 20 Min an. Du glaubst, das System ist schuld.
    Du hast es eilig und wirst aggressiv.""",
    
    """Szenario B: 'Die Rückerstattung'.
    Es ist 11:00 Uhr. Der Wind hat aufgefrischt, obere Lifte stehen.
    Du willst dein Geld für die Tageskarte zurück. Sofort.
    Du bist stur und lässt nicht mit dir reden."""
]

# --- SIDEBAR ---
with st.sidebar:
    st.header("🎭 Kategorie wählen")
    kategorie = st.selectbox("Bereich:", ("Hotel", "Skischule", "Seilbahn"))
    
    st.markdown("---")
    st.write("👇 Klicke hier für eine neue Situation:")
    
    # Der "Würfel"-Button
    if st.button("🎲 Neue Situation würfeln"):
        st.session_state.messages = []
        st.session_state.chat = None
        # Hier wird gewürfelt!
        if kategorie == "Hotel":
            st.session_state.current_scenario = random.choice(VARIANTS_HOTEL)
        elif kategorie == "Skischule":
            st.session_state.current_scenario = random.choice(VARIANTS_SKISCHULE)
        elif kategorie == "Seilbahn":
            st.session_state.current_scenario = random.choice(VARIANTS_SEILBAHN)
        st.rerun()

    if st.button("Logout"):
        st.session_state.authenticated = False
        st.rerun()

# --- INITIALISIERUNG (Beim ersten Laden auch würfeln) ---
if "current_scenario" not in st.session_state:
    st.session_state.current_scenario = random.choice(VARIANTS_HOTEL)


# --- HAUPTBEREICH ---
st.title("Training: " + kategorie)

# Anzeige für den Trainer (damit du weißt, was los ist)
with st.expander("ℹ️ Aktuelles Szenario (Nur für Trainer sichtbar)", expanded=True):
    st.info(st.session_state.current_scenario)

# --- PROMPT ZUSAMMENBAUEN ---
# Wir nehmen das gewürfelte Szenario und packen die "Coach"-Anweisung immer dazu
SYSTEM_INSTRUCTION = f"""
Du bist ein Rollenspiel-Bot.
{st.session_state.current_scenario}
Verhalte dich extrem realistisch entsprechend der Rolle (Level 8/10).
WICHTIG: Wenn der User "FEEDBACK" schreibt, wechsle SOFORT die Rolle zum Business-Coach.
Analysiere dann das Gespräch: Was war gut? Wo war der Fehler? Gib 3 bessere Formulierungsvorschläge.
"""

# --- API KEY ---
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
except:
    with st.sidebar:
        api_key = st.text_input("API Key", type="password")

# --- CHAT LOGIK ---
if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat" not in st.session_state or st.session_state.chat is None:
    if api_key:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-2.0-flash", system_instruction=SYSTEM_INSTRUCTION)
            st.session_state.chat = model.start_chat(history=[])
            response = st.session_state.chat.send_message("Start")
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"Fehler: {e}")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Deine Antwort..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    try:
        response = st.session_state.chat.send_message(prompt)
        st.session_state.messages.append({"role": "assistant", "content": response.text})
        with st.chat_message("assistant"):
            st.markdown(response.text)
    except Exception as e:
        st.error(f"Fehler: {e}")
