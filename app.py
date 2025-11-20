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
    23:00
