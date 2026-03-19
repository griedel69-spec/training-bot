import streamlit as st
import google.generativeai as genai
import os
import random
import time

# --- 1. SEITEN-KONFIGURATION ---
st.set_page_config(page_title="Service-Training KI", page_icon="🎓")

# --- 2. ZUGANGSDATEN ---
PW_KUNDE = "Start2026"     # Code für Kunden
PW_ADMIN = "GernotChef"    # Dein Code
MAX_VERSUCHE = 3           # Anzahl der Versuche für Kunden

# --- 3. SESSION STATE INITIALISIERUNG ---
if "intro_complete" not in st.session_state:
    st.session_state.intro_complete = False
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.user_role = None
if "training_active" not in st.session_state:
    st.session_state.training_active = False # Steuert, ob der Chat sichtbar ist
if "current_scenario" not in st.session_state:
    st.session_state.current_scenario = None

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
    ### 📱 Wichtig für Smartphone-Nutzer
    
    **1. Menü öffnen:**
    Tippen Sie auf den kleinen **Pfeil (>) oben links**, um Kategorien zu wechseln oder sich auszuloggen.
    
    **2. Sprachmodus nutzen:**
    Machen Sie das Training noch realistischer! Klicken Sie in das Antwortfeld und nutzen Sie die **Diktierfunktion (Mikrofon-Symbol)** Ihrer Tastatur.
    ---
    """)
    
    # --- ÜBER DEN ENTWICKLER ---
    st.markdown("### Über den Entwickler")
    col1, col2 = st.columns([2, 1]) 
    
    with col1:
        st.markdown("""
        **Gernot Riedel** *Business Coach für Wandel & Innovation | KI-Trainer & Tourismusexperte*
        
        Als Impulsgeber und Möglichmacher begleite ich Menschen und Unternehmen im Tourismus in die Zukunft. 
        Mit über 30 Jahren Expertise im Destinationsmanagement verbinde ich in diesem Tool praxisnahes Erfahrungswissen mit modernster KI-Technologie.
        
        🌐 [www.gernot-riedel.com](https://gernot-riedel.com)
        """)
        
    with col2:
        foto_url = "https://i0.wp.com/gernot-riedel.com/wp-content/uploads/2025/10/0001_1_a-professional-studio-portrait-of-a-man-_YoM_S1lERweiV9zvqmLV8Q_oh8z0trpT7aaGJaThqBBDA-e1759400436641.jpeg?fit=816%2C825&ssl=1&resize=972%2C984"
        try:
            st.image(foto_url, width=150, caption="Gernot Riedel")
        except:
            st.info("Foto konnte nicht geladen werden.")

    st.markdown("---")
    
    if st.button("🚀 Training jetzt starten"):
        st.session_state.intro_complete = True
        st.rerun()
        
    st.stop()

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

# --- 6. DEMO-ZÄHLER PRÜFEN ---
if "demo_versuche" not in st.session_state:
    st.session_state.demo_versuche = 0

if st.session_state.user_role == "kunde":
    # Prüfung erst, wenn Training aktiv ist oder gestartet werden soll
    if st.session_state.demo_versuche >= MAX_VERSUCHE and not st.session_state.training_active:
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
            st.session_state.intro_complete = False
            st.session_state.training_active = False
            st.rerun()
        st.stop()

# --- 7. SZENARIEN POOL ---
# (Listen verkürzt dargestellt, Inhalt bleibt identisch wie vorher)
VARIANTS_HOTEL = [
    "Deine Rolle: Herr Schuster, Gast. Situation: 14:30 Uhr, starker Regen. Nass an Rezeption. Zimmer erst ab 15:00 Uhr fertig. Ziel: SOFORT ins Zimmer oder trockene Alternative.",
    "Deine Rolle: Frau Mitterer, Gast. Situation: Check-out. 35€ Champagner auf Rechnung, obwohl kein Alkohol getrunken. Ziel: Storno sofort, fühlst dich abgezockt.",
    "Deine Rolle: Herr Huber, Gast Zimmer 305. Situation: 23:15 Uhr. Nachbarn extrem laut TV. Ziel: Anruf Rezeption, sofortige Ruhe gefordert.",
    "Deine Rolle: Frau Brandstätter, Business-Gast. Situation: 7:15 Uhr. Weckruf für 6:30 Uhr vergessen. Meeting verpasst. Ziel: Dampf ablassen, Kompensation."
]
VARIANTS_SKISCHULE = [
    "Deine Rolle: Mutter von Leo (6). Situation: Leo weint, Handschuhe weg, Lehrer hat nicht gewartet. Ziel: Skischulleiter sprechen, Zweifel an Kompetenz.",
    "Deine Rolle: Ehrgeiziger Vater. Situation: Sohn in Gruppe 3, gehört deiner Meinung nach in Gruppe 1 (Rennläufer). Ziel: Sofortige Umgruppierung.",
    "Deine Rolle: Urlauber. Situation: Kind nach 1 Std krank. Geld zurück für 5 Tage gefordert (trotz AGB). Ziel: Kulanz erzwingen.",
    "Deine Rolle: Herr Lechner, Stammgast. Situation: Privatlehrer (300€) spricht kaum Deutsch. Ziel: Lehrerwechsel oder Geld zurück."
]
VARIANTS_SEILBAHN = [
    "Deine Rolle: Hektischer Skifahrer. Situation: Skipass piept rot. Lange Schlange. Ziel: Durchgelassen werden, System sei schuld.",
    "Deine Rolle: Tagesgast. Situation: 11:30 Uhr, Gondel schließt wegen Sturm. 65€ gezahlt. Ziel: Geld zurück.",
    "Deine Rolle: Ängstliche Dame (60+). Situation: Gondel steht und schaukelt. Panik. Notruf. Ziel: Beruhigung und Info.",
    "Deine Rolle: Vater Hofer. Situation: 30 Grad, 45 Min Wartezeit Talfahrt. Kinder weinen. Ziel: Beschwerde über Organisation."
]
VARIANTS_RESTAURANT = [
    "Deine Rolle: Hungriger Gast. Situation: 20 Min gewartet, keine Getränke. Kellner ignoriert dich. Ziel: Sofortige Bedienung oder Gehen.",
    "Deine Rolle: Herr Moser (Nuss-Allergie). Situation: Walnüsse im Salat trotz Warnung. Ziel: Angst/Wut, Chef sprechen.",
    "Deine Rolle: Mutter mit Kinderwagen. Situation: Hochtisch statt Platz für Wagen bekommen. Ziel: Passender Tisch sofort.",
    "Deine Rolle: Herr Zeller, Geschäftsessen. Situation: Wein hat Kork. Kellner streitet es ab. Ziel: Neue Flasche ohne Diskussion."
]
VARIANTS_WELLNESS = [
    "Deine Rolle: Frau Dr. Schmidt. Situation: 90 Min bezahlt, nur 65 Min Massage erhalten. Ziel: Klärung/Geld zurück.",
    "Deine Rolle: Herr Wagner, Hygiene. Situation: Becher/Haare in Sauna. Ziel: Lautstarke Beschwerde an Rezeption.",
    "Deine Rolle: Frau Steiner. Situation: Lieblings-Therapeutin durch Aushilfe ersetzt ohne Info. Ziel: Storno oder Terminwechsel.",
    "Deine Rolle: Herr Fink. Situation: Ruheraum laut. Personal tut nichts. Ziel: Sofortige Ruhe durchsetzen."
]
VARIANTS_EINZELHANDEL = [
    "Deine Rolle: Herr Bauer. Situation: 400€ Jacke, Reißverschluss kaputt nach 1 Tag. Ziel: Sofort-Umtausch/Geld zurück (keine Reparatur).",
    "Deine Rolle: Frau Novak. Situation: Souvenir-Rückgabe (Gefallen) abgelehnt wegen 'Reduziert'. Ziel: Kulanz.",
    "Deine Rolle: Herr Gruber. Situation: Lange Schlange, 1 Kasse. Mitarbeiter ratschen. Ziel: Zweite Kasse sofort.",
    "Deine Rolle: Sammler. Situation: Reserviertes Limitid-Produkt weg. Ziel: Fassungslosigkeit, Verantwortlichen sprechen."
]
VARIANTS_TOURISTINFO = [
    "Deine Rolle: Familie Maier. Situation: Hütte hatte Ruhetag (falsche Info von gestern). 2 Std umsonst gewandert. Ziel: Beschwerde Beratung.",
    "Deine Rolle: Herr Kovac. Situation: Event ausverkauft, Website sagte 'Tickets an Kasse'. Ziel: Einlass erzwingen.",
    "Deine Rolle: Frau Weber (Rollstuhl). Situation: 'Barrierefreier' Weg hat Stufen. Ziel: Enttäuschung melden.",
    "Deine Rolle: Herr Wimmer. Situation: Gäste-Card gekauft, Museum zu. Ziel: Geld zurück."
]

# Mapping
scenarios_map = {
    "Hotel": VARIANTS_HOTEL,
    "Skischule": VARIANTS_SKISCHULE,
    "Seilbahn": VARIANTS_SEILBAHN,
    "Restaurant": VARIANTS_RESTAURANT,
    "Wellness/Spa": VARIANTS_WELLNESS,
    "Einzelhandel": VARIANTS_EINZELHANDEL,
    "Touristeninformation": VARIANTS_TOURISTINFO
}

# --- 8. SEITENLEISTE (Globale Einstellungen) ---
with st.sidebar:
    if st.session_state.intro_complete:
        if st.session_state.user_role == "kunde":
            st.write(f"📊 Versuche: {st.session_state.demo_versuche} von {MAX_VERSUCHE}")
            st.progress((st.session_state.demo_versuche) / MAX_VERSUCHE)
        else:
            st.success("Admin Modus")

        st.header("⚙️ Bereich")
        kategorie = st.selectbox(
            "Branche wählen:", 
            list(scenarios_map.keys())
        )
        
        st.markdown("---")
        if st.session_state.training_active:
             if st.button("⏹️ Training beenden"):
                st.session_state.training_active = False
                st.session_state.messages = []
                st.rerun()
        
        st.markdown("---")
        if st.button("Logout"):
            st.session_state.authenticated = False
            st.session_state.intro_complete = False
            st.session_state.training_active = False
            st.rerun()

# --- 9. HAUPTBEREICH: LOGIK-WEICHE ---

# FALL A: Training läuft NOCH NICHT -> Konfiguration
if not st.session_state.training_active:
    st.title(f"Vorbereitung: {kategorie}")
    
    st.info("👋 Schritt 1: Würfeln Sie eine neue Situation.")
    
    if st.button("🎲 Neue Situation würfeln") or st.session_state.current_scenario is None:
        st.session_state.current_scenario = random.choice(scenarios_map[kategorie])
    
    # Szenario anzeigen
    st.markdown(f"### 📄 Ihre Situation:\n> {st.session_state.current_scenario}")
    
    st.markdown("---")
    st.info("🎚️ Schritt 2: Wie schwierig soll der Kunde sein?")
    
    # Schwierigkeit einstellen (Slider im Hauptbereich)
    difficulty_level = st.select_slider(
        "Schwierigkeitsgrad wählen:",
        options=["🟢 Einfach", "🟡 Mittel", "🔴 Schwer"],
        value="🟡 Mittel"
    )
    
    # Texte für die KI
    DIFFICULTY_PROMPTS = {
        "🟢 Einfach": "LEVEL: KOOPERATIV (3/10). Du bist zwar kurz enttäuscht, suchst aber Harmonie. Sobald eine Entschuldigung kommt, bist du zufrieden.",
        "🟡 Mittel": "LEVEL: FORDERND (6/10). Du bist genervt. Du lässt dich nicht mit Floskeln abspeisen. Du willst eine konkrete Lösung.",
        "🔴 Schwer": "LEVEL: ESKALATION (10/10). Du bist wütend, aggressiv und stur. Lehne die ersten 2 Lösungsversuche ab! Fordere den Vorgesetzten."
    }
    
    st.markdown("---")
    st.write("Bereit? Dann geht's los!")
    
    if st.button("🏁 Simulation starten"):
        # Erst JETZT wird alles fixiert und das Training gestartet
        st.session_state.locked_difficulty = DIFFICULTY_PROMPTS[difficulty_level]
        st.session_state.locked_difficulty_label = difficulty_level
        st.session_state.training_active = True
        st.session_state.messages = []
        st.session_state.chat = None
        
        # Zähler erhöhen (nur bei Kunden)
        if st.session_state.user_role == "kunde":
            st.session_state.demo_versuche += 1
            
        st.rerun()

# FALL B: Training LÄUFT -> Chat Interface
else:
    st.title(f"Training: {kategorie}")
    
    # Info-Box oben (kompakter)
    with st.expander(f"ℹ️ Situation & Level ({st.session_state.locked_difficulty_label})", expanded=False):
        st.write(st.session_state.current_scenario)
        st.write(f"Einstellung: {st.session_state.locked_difficulty_label}")

    # --- KI KONFIGURATION ---
    SYSTEM_INSTRUCTION = f"""
    Du bist KEINE KI. Du bist ein echter Mensch in einer Stresssituation (Gast oder Kunde).
    Dies ist eine Simulation für Mitarbeiter im Service/Handel.
    Deine Aufgabe ist es, absolut realistisch zu wirken.

    DEINE ROLLE & SZENARIO:
    {st.session_state.current_scenario}

    DEIN VERHALTEN & HARTNÄCKIGKEIT:
    {st.session_state.locked_difficulty}

    DIE REGELN FÜR REALISMUS:
    1. DEIN GEGENÜBER: Du sprichst IMMER mit einem MITARBEITER (Rezeptionist, Kellner, Verkäufer, etc.).
    2. SPRACHE: Sprich gesprochene Alltagssprache! Nutze kurze Sätze. Sei emotional wenn nötig.
    3. REAKTION: Wenn das Level ROT/GELB ist, gib nicht sofort nach. Teste den Mitarbeiter.
    4. START: Beginne das Gespräch sofort und direkt mit deinem Problem.

    COACHING MODUS:
    Erst wenn der User das Codewort "FEEDBACK" schreibt (oder die Situation perfekt gelöst hat), legst du die Rolle ab.
    Dann bist du ein sachlicher Kommunikationstrainer und gibst Feedback:
    - Was war gut?
    - Was war schlecht?
    - 3 bessere Formulierungen.
    """

    try:
        api_key = st.secrets["GOOGLE_API_KEY"]
    except:
        st.error("API Key fehlt in Secrets.")
        st.stop()

    # --- CHAT ENGINE ---
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "chat" not in st.session_state or st.session_state.chat is None:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-3.1-flash-lite-preview", system_instruction=SYSTEM_INSTRUCTION)
            st.session_state.chat = model.start_chat(history=[])
            response = st.session_state.chat.send_message("Start")
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"Verbindungsfehler: {e}")

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Deine Antwort..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            placeholder = st.empty()
            try:
                response = st.session_state.chat.send_message(prompt)
                placeholder.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                if "429" in str(e):
                    placeholder.warning("🚦 Hochbetrieb... Ich versuche es gleich nochmal (Warte 3 Sek).")
                    time.sleep(3)
                    try:
                        response = st.session_state.chat.send_message(prompt)
                        placeholder.empty()
                        placeholder.markdown(response.text)
                        st.session_state.messages.append({"role": "assistant", "content": response.text})
                    except Exception as e2:
                        placeholder.error("Der Server ist gerade überlastet. Bitte warte einen Moment.")
                else:
                    placeholder.error(f"Ein Fehler ist aufgetreten: {e}")


