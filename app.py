import streamlit as st
import google.generativeai as genai
import os
import random
import time

# --- 1. SEITEN-KONFIGURATION ---
st.set_page_config(page_title="Service-Training KI", page_icon="🎓")

# --- 2. ZUGANGSDATEN ---
PW_KUNDE = "Start2025"     # Code für Kunden
PW_ADMIN = "GernotChef"    # Dein Code
MAX_VERSUCHE = 3           # Anzahl der Versuche für Kunden

# --- 3. SESSION STATE INITIALISIERUNG ---
if "intro_complete" not in st.session_state:
    st.session_state.intro_complete = False
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.user_role = None

# --- 4. STARTSEITE (LANDING PAGE) ---
if not st.session_state.intro_complete:
    st.title("🎓 Willkommen beim KI-Training")
    st.subheader("Souveränität im Umgang mit Gästen & Kunden")
    
    st.markdown("""
    Egal ob an der **Rezeption**, im **Einzelhandel** oder in der **Dienstleistung**: 
    Der richtige Ton macht die Musik. 
    
    In diesem Simulator trainieren Sie völlig risikofrei den Umgang mit:
    * 😤 Fordernden **Gästen** (Tourismus)
    * 🛍️ Kritischen **Kunden** (Handel)
    * ⚡ Komplexen **Beschwerden** & Reklamationen
    
    ---
    ### 📱 Tipp für Smartphone-Nutzer
    Machen Sie das Training noch realistischer! 
    Klicken Sie in das Antwortfeld und nutzen Sie die **Diktierfunktion (Mikrofon-Symbol)** Ihrer Tastatur. 
    So sprechen Sie direkt mit dem Kunden, statt zu tippen.
    ---
    """)
    
    if st.button("🚀 Training jetzt starten"):
        st.session_state.intro_complete = True
        st.rerun()
        
    st.stop() # Hier stoppt das Skript, solange man nicht geklickt hat

# --- 5. LOGIN LOGIK ---
if not st.session_state.authenticated:
    st.title("🔒 Login")
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

# --- 6. DEMO-ZÄHLER PRÜFEN (Nur für Kunden) ---
if "demo_versuche" not in st.session_state:
    st.session_state.demo_versuche = 0

if st.session_state.user_role == "kunde":
    if st.session_state.demo_versuche >= MAX_VERSUCHE:
        st.balloons()
        st.warning("🏁 Die kostenlose Demo-Phase ist beendet.")
        
        msg = f"""
        ### Vielen Dank fürs Testen!
        Sie haben {MAX_VERSUCHE} Szenarien absolviert.
        
        **Möchten Sie dieses Tool für Ihr Unternehmen nutzen?**
        Diese KI kann exakt auf Ihre Region, Ihre Tonalität und Ihre Gäste/Kunden angepasst werden.
        
        👉 **Kontakt:** Gernot Riedel
        📧 **E-Mail:** [kontakt@gernot-riedel.com](mailto:kontakt@gernot-riedel.com)
        """
        st.markdown(msg)
        
        if st.button("Zurück zum Login"):
            st.session_state.authenticated = False
            st.session_state.demo_versuche = 0
            st.session_state.intro_complete = False # Zurück zur Startseite
            st.rerun()
        st.stop()

# --- 7. SZENARIEN POOL ---

VARIANTS_HOTEL = [
    """Deine Rolle: Herr Schuster, Gast.
    Situation: Es ist 14:30 Uhr, starker Regen. Du kommst nass an die Rezeption. Dein Zimmer (Junior Suite) ist laut System erst ab 15:00 Uhr fertig.
    Dein Ziel: Du willst SOFORT ins Zimmer oder zumindest eine trockene Alternative.""",
    
    """Deine Rolle: Frau Mitterer, Gast.
    Situation: Check-out. Auf der Rechnung stehen 35€ für Champagner aus der Minibar. Du trinkst aber gar keinen Alkohol.
    Dein Ziel: Die Position muss sofort storniert werden. Du fühlst dich abgezockt.""",
    
    """Deine Rolle: Herr Huber, Gast in Zimmer 305.
    Situation: 23:15 Uhr. Die Gäste im Nebenzimmer schauen extrem laut Fernsehen. Du hast morgen eine Wanderung vor dir.
    Dein Ziel: Du rufst an der Rezeption an. Du willst, dass JETZT Ruhe ist, keine Ausreden.""",

    """Deine Rolle: Frau Brandstätter, Business-Gast.
    Situation: 7:15 Uhr. Du hattest einen Weckruf für 6:30 Uhr bestellt, der nie kam. Du hast den Zug zum Meeting verpasst.
    Dein Ziel: Du willst Dampf ablassen und eine Kompensation. Eine Entschuldigung reicht dir nicht."""
]

VARIANTS_SKISCHULE = [
    """Deine Rolle: Mutter von Leo (6 Jahre).
    Situation: Leo kommt weinend aus dem Kurs, seine Handschuhe sind weg und er sagt, der Lehrer hat "nie gewartet".
    Dein Ziel: Du willst den Skischulleiter sprechen. Du zweifelst an der Kompetenz des Lehrers.""",
    
    """Deine Rolle: Ein ehrgeiziger Vater.
    Situation: Dein Sohn wurde in Gruppe 3 (Mittel) eingeteilt. Du bist überzeugt, er ist ein "Rennläufer" (Gruppe 1).
    Dein Ziel: Sofortige Umgruppierung. Du fühlst dich in deiner Ehre gekränkt.""",
    
    """Deine Rolle: Urlauber aus Norddeutschland.
    Situation: Dein Kind ist nach 1 Stunde Kurs krank geworden (Magen-Darm). Du willst das Geld für die restlichen 4 Tage zurück (lt. AGB eigentlich nicht möglich ohne Attest).
    Dein Ziel: Kulanz erzwingen.""",

    """Deine Rolle: Herr Lechner, Stammgast.
    Situation: Du hast einen Privatlehrer gebucht (300€/Tag), aber der Lehrer spricht kaum Deutsch und versteht deine Wünsche nicht.
    Dein Ziel: Lehrerwechsel sofort oder Geld zurück."""
]

VARIANTS_SEILBAHN = [
    """Deine Rolle: Hektischer Skifahrer.
    Situation: Dein Skipass (gestern gekauft) piept rot am Drehkreuz. Eine lange Schlange bildet sich hinter dir.
    Dein Ziel: Du willst durchgelassen werden. "Das Ding muss kaputt sein!".""",
    
    """Deine Rolle: Ein Tagesgast.
    Situation: 11:30 Uhr. Die Gondel zum Gipfel schließt wegen Sturm. Du hast 65€ für die Tageskarte gezahlt und bist erst einmal gefahren.
    Dein Ziel: Du willst dein Geld zurück, zumindest anteilig.""",

    """Deine Rolle: Ängstliche Dame (60+).
    Situation: Die Gondel bleibt kurz stehen und schaukelt. Du hast Panik. Du rufst über die Sprechanlage (Notruf) an.
    Dein Ziel: Du willst beruhigt werden und wissen, was los ist.""",

    """Deine Rolle: Familienvater Hofer.
    Situation: Hochsommer, 30 Grad. Ihr wartet seit 45 Minuten auf die Talfahrt. Keine Infos, keine Getränke. Kinder weinen.
    Dein Ziel: Du beschwerst dich beim Personal, dass die Organisation katastrophal ist."""
]

VARIANTS_RESTAURANT = [
    """Deine Rolle: Hungriger Gast.
    Situation: Du sitzt seit 20 Minuten und hast noch nicht mal Getränke bekommen. Der Kellner läuft ständig vorbei.
    Dein Ziel: Du willst sofort bedient werden oder du gehst.""",
    
    """Deine Rolle: Herr Moser (Nuss-Allergie).
    Situation: Du hast explizit "ohne Nüsse" bestellt. Im Salat sind Walnüsse.
    Dein Ziel: Du hast Angst und bist wütend. Das ist lebensgefährlich! Du verlangst den Chef.""",
    
    """Deine Rolle: Mutter mit Kinderwagen.
    Situation: Du hast reserviert ("Tisch mit
