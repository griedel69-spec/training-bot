import streamlit as st
import google.generativeai as genai
import os

# --- SEITEN-KONFIGURATION ---
st.set_page_config(page_title="Hotel-Training", page_icon="🏨")
st.title("🏨 Der schwierige Gast")
st.caption("Trainings-Simulator mit Gemini 2.0")

# --- API KEY MANAGEMENT (Der Profi-Teil) ---
# Die App schaut zuerst in den Tresor (Secrets). Wenn da nichts ist, fragt sie den User.
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
except:
    with st.sidebar:
        api_key = st.text_input("Google API Key eingeben", type="password")

# --- BUTTONS (Neustart) ---
with st.sidebar:
    st.markdown("---")
    if st.button("Gespräch neu starten"):
        st.session_state.messages = []
        st.session_state.chat = None
        st.rerun()
    st.info("Tipp: Schreibe 'FEEDBACK' für eine Analyse.")

# --- SYSTEM PROMPT ---
SYSTEM_INSTRUCTION = """
Du bist "Herr Schuster", ein verärgerter Hotelgast.Szenario: 14:30 Uhr, Regen, nass. Zimmer (Junior Suite) nicht fertig. Check-in offiziell ab 15:00.
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
            st.error(f"Fehler: {e}")

# --- CHAT VERLAUF ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- EINGABE ---
if prompt := st.chat_input("Deine Antwort..."):
    if not api_key:
        st.warning("Bitte API Key eingeben (oder in Secrets hinterlegen).")
    else:
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
