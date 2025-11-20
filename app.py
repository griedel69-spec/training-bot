import streamlit as st
import google.generativeai as genai

# --- SEITEN-KONFIGURATION ---
st.set_page_config(page_title="Hotel-Training", page_icon="🏨")
st.title("🏨 Der schwierige Gast")
st.caption("Trainings-Simulator mit Gemini 2.0")

# --- SIDEBAR: API KEY & RESET ---
with st.sidebar:
    api_key = st.text_input("Google API Key eingeben", type="password")
    st.markdown("---")
    if st.button("Neustart"):
        st.session_state.messages = []
        st.session_state.chat = None
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
            # HIER IST DIE ÄNDERUNG: Wir nutzen dein verfügbares Modell
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
        st.warning("Bitte erst den API Key links eingeben!")
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
            st.error(f"Ein Fehler ist aufgetreten: {e}")