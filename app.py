import streamlit as st
import google.generativeai as genai
import os
import random
import time

# --- 1. SEITEN-KONFIGURATION ---
st.set_page_config(page_title="Tourismus-Trainer", page_icon="🎚️")

# --- 2. ZUGANGSDATEN ---
PW_KUNDE = "Start2025"     # Code für Kunden (begrenzt auf 3 Versuche)
PW_ADMIN = "GernotChef"    # Dein Code (unbegrenzt)
MAX_VERSUCHE = 3           # Anzahl der Versuche für Kunden

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
    st.stop()

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
        
        👉 **Kontakt:** Gernot Riedel
        📧 **E-Mail:** [kontakt@gernot-riedel.com](mailto:kontakt@gernot-riedel.com)
        """)
        
        if st.button("Zurück zum Login"):
            st.session_state.authenticated = False
            st.session_state.demo_versuche = 0
            st.rerun()
        st.stop()

# --- 5. SZENARIEN POOL ---
# (Die Texte bleiben gleich, aber das Level wird jetzt durch den Regler überschrieben)

VARIANTS_HOTEL = [
    """Deine Rolle: Herr Schuster, ein Gast.
    Situation: Es ist 14:30 Uhr, du bist nass vom Regen. Dein Zimmer (Junior Suite) ist noch nicht fertig.
    Verhalten: Du willst sofort duschen.""",
    
    """Deine Rolle: Herr Schuster, ein Gast.
    Situation: Du checkst aus. Rechnung: 35€ für Champagner aus der Minibar, den du nicht hattest.
    Verhalten: Du witterst einen Fehler oder Betrug.""",
    
    """Deine Rolle: Herr Schuster, ein Gast.
    Situation: 23:00 Uhr. Nachbarn schauen laut TV. Du kannst nicht schlafen.
    Verhalten: Du forderst Ruhe.""",

    """Deine Rolle: Frau Brandstätter, Geschäftsreisende.
    Situation: 7:00 Uhr. Weckruf für 6:30 Uhr kam nie. Meeting verpasst.
    Verhalten: Du verlangst Kompensation."""
]

VARIANTS_SKISCHULE = [
    """Deine Rolle: Eine Mutter.
    Situation: Kind (Leo, 6) hat nach dem Skikurs geweint.
    Verhalten: Du glaubst, der Lehrer hat nicht aufgepasst.""",
    
    """Deine Rolle: Ein Vater.
    Situation: Sohn ist in Gruppe 3, du denkst er gehört in Gruppe 1 (Profi).
    Verhalten: Du siehst das als Fehleinschätzung.""",
    
    """Deine Rolle: Ein Kunde.
    Situation: Kind nach 1 Stunde krank. Du willst Geld für 5 Tage zurück.
    Verhalten: Du pochst auf Rückerstattung.""",

    """Deine Rolle: Herr Lechner.
    Situation: Tochter (10) lernt im Kurs nichts Neues. Tag 3.
    Verhalten: Du bist enttäuscht."""
]

VARIANTS_SEILBAHN = [
    """Deine Rolle: Ein Skifahrer.
    Situation: Skipass geht nicht am Drehkreuz. 20 Min Wartezeit.
    Verhalten: Du hast es eilig und bist genervt.""",
    
    """Deine Rolle: Ein Gast.
    Situation: 11:00 Uhr, obere Lifte wegen Sturm zu.
    Verhalten: Du willst Geld für die Tageskarte zurück.""",

    """Deine Rolle: Frau Müller, Seniorin.
    Situation: 9:00 Uhr. Gondel schaukelt im Wind. Höhenangst.
    Verhalten: Du hast Angst und fühlst dich unsicher.""",

    """Deine Rolle: Familie Hofer.
    Situation: 14:00 Uhr, 35°C. 45 Min Warten auf Talfahrt in der Sonne.
    Verhalten: Kinder weinen, Eltern gestresst."""
]

VARIANTS_RESTAURANT = [
    """Deine Rolle: Frau Berger.
    Situation: 45 Min auf Essen gewartet. Andere bekamen es früher.
    Verhalten: Du zweifelst an der Organisation.""",
    
    """Deine Rolle: Herr Moser (Allergiker).
    Situation: Nüsse im Essen trotz Warnung.
    Verhalten: Du bist besorgt um deine Gesundheit.""",
    
    """Deine Rolle: Familie Huber.
    Situation: Tisch neben lauter Küchentür, Kinderstuhl fehlt.
    Verhalten: Gestresst, erwartest Lösung.""",

    """Deine Rolle: Herr Zeller.
    Situation: Geschäftsessen. Service langsam, Essen kalt.
    Verhalten: Peinlich berührt vor Kunden."""
]

VARIANTS_WELLNESS = [
    """Deine Rolle: Frau Dr. Schmidt.
    Situation: 90min Massage
