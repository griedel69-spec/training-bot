import streamlit as st
import google.generativeai as genai
import os

# --- SEITEN-KONFIGURATION ---
st.set_page_config(page_title="Hotel-Training", page_icon="🏨")

# --- DER TÜRSTEHER (Passwort-Schutz) ---
# Ändere "Start2025" in dein Wunsch-Passwort
PASSWORT = "Start2025"

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔒 Geschützter Bereich")
    eingabe = st.text_input("Bitte Zugangscode eingeben:", type="password")
    if st.button("Anmelden"):
        if eingabe == PASSWORT:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Falscher Code. Zugriff verweigert.")
    st.stop()  # HIER STOPPT DIE APP, wenn das Passwort fehlt!

# --- AB HIER BEGINNT DIE EIGENTLICHE APP (nur sichtbar nach Login) ---

st.title("🏨 Der schwierige Gast")
st.caption("Trainings-Simulator mit Gemini 2.0")

# --- API KEY MANAGEMENT ---
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
except:
    with st.sidebar:
        st.warning("API Key nicht im Tresor gefunden.")
        api_key = st.text_input("Google API Key eingeben", type="password")

# --- BUTTONS ---
with st.sidebar:
    st.markdown("---")
    if st.button("Gespräch neu starten"):
        st.session_state.messages = []
        st.session_state.chat = None
        st.rerun()
    
    # Logout Button
    if st.button("Logout"):
        st.session_state.authenticated = False
        st.rerun()
        
    st.info("Tipp: Schreibe 'FEEDBACK' für eine Analyse.")

# --- SYSTEM PROMPT ---
SYSTEM_INSTRUCTION = """
Du bist „Herr Grander“, ein verärgerter Hotelgast.
Szenario: 14:30 Uhr, Regen, nass. Zimmer (Junior Suite) nicht fertig. Check-in offiziell ab 15:00.
Verhalten: Ungeduldig, fordernd, sarkastisch (Level 8/10).
WICHTIG: Wenn der User "FEEDBACK" schreibt, wechsle SOFORT die Rolle zum Business-Coach.
Analysiere dann das Gespräch: Was war gut? Wo war der Fehler? Gib 3 bessere Formulierungsvorschläge.
"""

# --- SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- CHAT INITIALISIEREN ---
if "chat" not in st.session_state or st.session_state.chat is None:
    if api_key:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-2.0-flash", system_instruction=SYSTEM_INSTRUCTION)
            st.session_state.chat = model.start_chat(history=[])
            response = st.session_state.chat.send_message("Start")
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"Fehler beim Verbinden: {e}")

# --- CHAT VERLAUF ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- EINGABE ---
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
