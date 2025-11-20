import streamlit as st
import google.generativeai as genai
import os

# --- SEITEN-KONFIGURATION ---
st.set_page_config(page_title="Tourismus-Trainer", page_icon="🏔️")

# --- PASSWORT-SCHUTZ ---
PASSWORT = "Start2025" # Hier dein Passwort ändern

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔒 Login Tourismus-Training")
    eingabe = st.text_input("Bitte Zugangscode eingeben:", type="password")
    if st.button("Anmelden"):
        if eingabe == PASSWORT:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Falscher Code.")
    st.stop()

# --- SZENARIO-AUSWAHL (Das Herzstück) ---
with st.sidebar:
    st.header("🎭 Szenario wählen")
    szenario_typ = st.selectbox(
        "Trainings-Situation:",
        ("Hotel / Rezeption (Herr Grander)", 
         "Skischule (Helikopter-Eltern)", 
         "Seilbahn (Ticket-Problem)")
    )

    # Hier definieren wir die Persönlichkeiten
    if "Hotel" in szenario_typ:
        SYSTEM_INSTRUCTION = """
        Du bist „Herr Grander“, ein verärgerter Hotelgast.
        Szenario: 14:30 Uhr, Regen. Zimmer (Junior Suite) nicht fertig.
        Verhalten: Arrogant, ungeduldig, fordernd (Level 8/10).
        WICHTIG: Bei Codewort "FEEDBACK" wechsle zum Coach und analysiere das Gespräch.
        """
    elif "Skischule" in szenario_typ:
        SYSTEM_INSTRUCTION = """
        Du bist eine überbesorgte Mutter („Helikopter-Mom“).
        Szenario: Dein Kind (Leo, 6 Jahre) ist im Skikurs angeblich überfordert und hat geweint.
        Du machst dem Skilehrer Vorwürfe, dass er nicht aufpasst.
        Verhalten: Emotional, hysterisch, beschützend.
        WICHTIG: Bei Codewort "FEEDBACK" wechsle zum Coach und analysiere das Gespräch.
        """
    elif "Seilbahn" in szenario_typ:
        SYSTEM_INSTRUCTION = """
        Du bist ein aggressiver Skifahrer am Drehkreuz.
        Szenario: Dein teurer Skipass geht nicht, das Drehkreuz sperrt.
        Du stehst seit 20 Minuten an. Du behauptest, das System ist schuld.
        Verhalten: Laut, aggressiv, du hast es eilig.
        WICHTIG: Bei Codewort "FEEDBACK" wechsle zum Coach und analysiere das Gespräch.
        """

    st.markdown("---")
    
    # Automatische Löschung bei Szenario-Wechsel
    if "last_scenario" not in st.session_state:
        st.session_state.last_scenario = szenario_typ
    
    if st.session_state.last_scenario != szenario_typ:
        st.session_state.messages = []
        st.session_state.chat = None
        st.session_state.last_scenario = szenario_typ
        st.rerun()

    # Manueller Neustart Button
    if st.button("Gespräch neu starten"):
        st.session_state.messages = []
        st.session_state.chat = None
        st.rerun()
        
    if st.button("Logout"):
        st.session_state.authenticated = False
        st.rerun()

# --- HAUPTBEREICH ---
st.title(f"Training: {szenario_typ}")
st.caption("KI-gestützter Simulator für schwierige Gespräche")

# --- API KEY CHECK ---
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
except:
    with st.sidebar:
        st.warning("API Key fehlt.")
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
