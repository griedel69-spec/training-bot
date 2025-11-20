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
        st.rerun
