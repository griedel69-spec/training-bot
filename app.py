import streamlit as st
import google.generativeai as genai
import os
import random

# --- 1. SEITEN-KONFIGURATION ---
st.set_page_config(page_title="Tourismus-Trainer", page_icon="🎲")

# --- 2. PASSWORT-EINSTELLUNGEN ---
PW_KUNDE = "Start2025"     # Für Kunden (Max. 3 Versuche)
PW_ADMIN = "GernotChef"    # Für dich (Unendlich)
MAX_VERSUCHE = 3           # Anzahl der Demo-Versuche für Kunden

# --- 3. LOGIN LOGIK ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.user_role = None

if not st.session_state.authenticated:
    st.title("🔒 Login Tourismus-Training")
    st.write("Bitte geben Sie Ihren Zugangscode ein.")
    eingabe = st.text_input("Code:", type="password")
    
    if st.button("Anmelden"):
        if eingabe == PW_KUNDE:
            st.session_state.authenticated = True
            st.session_state.user_role = "kunde"
            st.rerun()
        elif eingabe == PW_ADMIN:
            st.session_state.authenticated = True
            st.session_state.user_role = "admin"
            st.rerun()
        else:
            st.error("Unbekannter Code.")
    st.stop() # Hier stoppt die App, solange man nicht eingeloggt ist

# --- 4. DEMO-ZÄHLER PRÜFEN (Nur für Kunden) ---
if "demo_versuche" not in st.session_state:
    st.session_state.demo_versuche = 0

if st.session_state.user_role == "kunde":
    if st.session_state.demo_versuche >= MAX_VERSUCHE:
        st.balloons()
        st.warning("🏁 Die kostenlose Demo-Phase ist beendet.")
        st.markdown(f"""
        ### Vielen Dank fürs Testen!
        Sie haben {MAX_VERSUCHE} Szenarien absolviert.
        
        **Möchten Sie dieses Tool für Ihr Unternehmen nutzen?**
        Diese KI kann exakt auf Ihre Region, Ihre Tonalität und Ihre Gäste angepasst werden.
        
        👉 **Kontakt:** Gernot Riedel | [Dein Link/Email hier]
        """)
        
        if st.button("Zurück zum Login"):
            st.session_state.authenticated = False
            st.session_state.demo_versuche = 0
            st.rerun()
        st.stop() # Hier ist Schluss für den Kunden

# --- 5. SZENARIEN POOL (Inhalt) ---
VARIANTS_HOTEL = [
    """Szenario: 'Der Regen'.
    Es ist 14:30 Uhr, Gast ist nass. Zimmer nicht fertig.
    Gast ist arrogant und ungeduldig (8/10).""",
    
    """Szenario: 'Die Minibar'.
    Gast checkt aus. Rechnung: 35€ für Champagner.
    Gast bestreitet das vehement und wittert Betrug. Misstrauisch.""",
    
    """Szenario: 'Der Lärm'.
    23:00 Uhr. Nachbarn schauen laut TV.
    Gast kann nicht schlafen und fordert sofortige Ruhe oder Zimmerwechsel."""
]

VARIANTS_SKISCHULE = [
    """Szenario: 'Helikopter-Mom'.
    Mutter holt Kind (Leo, 6) ab. Er hat geweint.
    Sie wirft dem Skilehrer vor, er hätte Leo vernachlässigt. Hysterisch.""",
    
    """Szenario: 'Falsche Gruppe'.
    Vater beschwert sich. Sein Sohn sei ein Profi, wurde aber in Gruppe 3 gesteckt.
    Er empfindet das als Beleidigung. Besserwisserisch.""",
    
    """Szenario: 'Geld zurück'.
    Kind ist nach 1 Stunde krank geworden.
    Eltern verlangen Geld für den 5-Tages-Kurs zurück. Stur."""
]

VARIANTS_SEILBAHN = [
    """Szenario: 'Das Drehkreuz'.
    Skipass geht nicht. Gast steht seit 20 Min an.
    Glaubt, das System ist schuld. Hat es eilig, aggressiv.""",
    
    """Szenario: 'Sturm'.
    Obere Lifte sind wegen Wind zu.
    Gast will Tageskarte stornieren, obwohl er schon gefahren ist. Uneinsichtig."""
]

# --- 6. SEITENLEISTE (Steuerung) ---
with st.sidebar:
    # Info-Anzeige für den User
    if st.session_state.user_role == "kunde":
        st.write(f"Test-Modus: Runde {st.session_state.demo_versuche + 1} von {MAX_VERSUCHE}")
        st.progress((st.session_state.demo_versuche) / MAX_VERSUCHE)
    else:
        st.success(f"Angemeldet als: {PW_ADMIN} (Admin)")

    st.header("🎭 Einstellung")
    kategorie = st.selectbox("Bereich wählen:", ("Hotel", "Skischule", "Seilbahn"))
    
    st.markdown("---")
    st.write("👇 Nächstes Training:")
    
    # Der "Würfel"-Button
    if st.button("🎲 Neue Situation würfeln"):
        # Zähler nur erhöhen, wenn es ein Kunde ist
        if st.session_state.user_role == "kunde":
            st.session_state.demo_versuche += 1
            
        # Chat resetten
        st.session_state.messages = []
        st.session_state.chat = None
        
        # Würfeln
        if kategorie == "Hotel":
            st.session_state.current_scenario = random.choice(VARIANTS_HOTEL)
        elif kategorie == "Skischule":
            st.session_state.current_scenario = random.choice(VARIANTS_SKISCHULE)
        elif kategorie == "Seilbahn":
            st.session_state.current_scenario = random.choice(VARIANTS_SEILBAHN)
        st.rerun() # <--- HIER WAR DER FEHLER, JETZT KORRIGIERT

    st.markdown("---")
    if st.button("Logout"):
        st.session_state.authenticated = False
        st.rerun()

# --- 7. INITIALISIERUNG (Erster Start) ---
if "current_scenario" not in st.session_state:
    # Standard-Start, damit Variable nicht leer ist
    st.session_state.current_scenario = random.choice(VARIANTS_HOTEL)

# --- 8. HAUPTBEREICH ANZEIGE ---
st.title(f"Training: {kategorie}")

# Schöne Box für das Szenario
with st.expander("ℹ️ Aktuelles Szenario (Bitte lesen)", expanded=True):
    st.info(st.session_state.current_scenario)

# --- 9. KI KONFIGURATION ---
# Prompt zusammenbauen
SYSTEM_INSTRUCTION = f"""
Du bist ein professioneller Rollenspiel-Bot für Tourismus-Training.
DEINE ROLLE & SITUATION:
{st.session_state.current_scenario}

ANWEISUNGEN:
1. Bleib strikt in der Rolle.
2. Reagiere auf die Antworten des Users (wütend, beruhigt, sarkastisch).
3. WICHTIG: Wenn der User das Wort "FEEDBACK" schreibt (oder das Problem perfekt gelöst hat),
   wechsle die Persona. Du bist dann ein Business-Coach.
   Gib eine professionelle Analyse: Was war gut? Was war schlecht? Gib 3 konkrete Formulierungstipps.
"""

# API Key holen (aus Secrets oder Eingabe)
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
except:
    # Fallback, falls Secrets noch nicht eingerichtet sind
    with st.sidebar:
        st.warning("⚠️ API Key nicht in Secrets gefunden.")
        api_key = st.text_input("API Key manuell eingeben", type="password")

if not api_key:
    st.error("Bitte API Key hinterlegen, um zu starten.")
    st.stop()

# --- 10. CHAT ENGINE ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Chat starten, falls noch nicht aktiv
if "chat" not in st.session_state or st.session_state.chat is None:
    try:
        genai.configure(api_key=api_key)
        # Wir nutzen das modernste Modell
        model = genai.GenerativeModel("gemini-2.0-flash", system_instruction=SYSTEM_INSTRUCTION)
        st.session_state.chat = model.start_chat(history=[])
        
        # Erster Satz der KI triggern
        response = st.session_state.chat.send_message("Start")
        st.session_state.messages.append({"role": "assistant", "content": response.text})
    except Exception as e:
        st.error(f"Verbindungsfehler: {e}")

# Chat-Historie anzeigen
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Eingabe verarbeiten
if prompt := st.chat_input("Deine Antwort..."):
    # 1. User Nachricht anzeigen
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. KI Antwort holen
    try:
        response = st.session_state.chat.send_message(prompt)
        st.session_state.messages.append({"role": "assistant", "content": response.text})
        with st.chat_message("assistant"):
            st.markdown(response.text)
    except Exception as e:
        st.error(f"Fehler bei der Antwort: {e}")
