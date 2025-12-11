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
        
        # Hier war der Fehler. Jetzt stabilisiert durch Variable:
        msg = f"""
        ### Vielen Dank fürs Testen!
        Sie haben {MAX_VERSUCHE} Szenarien absolviert.
        
        **Möchten Sie dieses Tool für Ihr Unternehmen nutzen?**
        Diese KI kann exakt auf Ihre Region, Ihre Tonalität und Ihre Gäste angepasst werden.
        
        👉 **Kontakt:** Gernot Riedel
        📧 **E-Mail:** [kontakt@gernot-riedel.com](mailto:kontakt@gernot-riedel.com)
        """
        st.markdown(msg)
        
        if st.button("Zurück zum Login"):
            st.session_state.authenticated = False
            st.session_state.demo_versuche = 0
            st.rerun()
        st.stop()

# --- 5. SZENARIEN POOL ---

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
    Situation: 90min Massage gebucht, nach 60min fertig.
    Verhalten: Fühlst dich um Leistung betrogen.""",
    
    """Deine Rolle: Herr Wagner.
    Situation: Haare und nasse Handtücher in der Sauna.
    Verhalten: Du findest es unhygienisch.""",
    
    """Deine Rolle: Frau Steiner.
    Situation: Lieblings-Therapeutin krank, Aushilfe übernimmt ohne Info.
    Verhalten: Enttäuscht.""",

    """Deine Rolle: Herr Fink.
    Situation: Ruheraum war laut, Sauna voll. Entspannungspaket gescheitert.
    Verhalten: Willst Geld zurück."""
]

VARIANTS_EINZELHANDEL = [
    """Deine Rolle: Herr Bauer.
    Situation: Gestern Jacke gekauft, heute Riss entdeckt.
    Verhalten: Du denkst, das war schon vorher so.""",
    
    """Deine Rolle: Frau Novak (Sprachbarriere).
    Situation: Will Souvenir umtauschen. Versteht Bon nicht.
    Verhalten: Unsicher und frustriert.""",
    
    """Deine Rolle: Herr Gruber.
    Situation: Lange Schlange, nur eine Kasse offen.
    Verhalten: Ungeduldig.""",

    """Deine Rolle: Herr Steiner.
    Situation: Reserviertes Sammlerstück ist "ausverkauft" trotz Reservierung.
    Verhalten: Fühlt sich getäuscht."""
]

VARIANTS_TOURISTINFO = [
    """Deine Rolle: Familie Maier.
    Situation: Ausflug gebucht, wegen Regen abgesagt. Keine Rückerstattung laut AGB.
    Verhalten: Fühlt sich falsch beraten.""",
    
    """Deine Rolle: Herr Kovac.
    Situation: Wanderweg war gesperrt, stand nicht im Prospekt.
    Verhalten: Verärgert über veraltete Infos.""",
    
    """Deine Rolle: Frau Weber.
    Situation: Sucht barrierefreie Infos. Personal hat keine Zeit.
    Verhalten: Überfordert.""",

    """Deine Rolle: Herr Wimmer.
    Situation: Erlebnis-Card gekauft, Attraktionen geschlossen.
    Verhalten: Fühlt sich abgezockt."""
]

# --- 6. SEITENLEISTE (Steuerung) ---
with st.sidebar:
    if st.session_state.user_role == "kunde":
        st.write(f"Test-Modus: Runde {st.session_state.demo_versuche + 1} von {MAX_VERSUCHE}")
        st.progress((st.session_state.demo_versuche) / MAX_VERSUCHE)
    else:
        st.success(f"Angemeldet als: {PW_ADMIN} (Admin)")

    st.header("🎭 Einstellungen")
    
    kategorie = st.selectbox(
        "Bereich wählen:", 
        ("Hotel", "Skischule", "Seilbahn", "Restaurant", "Wellness/Spa", "Einzelhandel", "Touristeninformation")
    )

    st.markdown("### 🎚️ Schwierigkeit")
    difficulty_selection = st.select_slider(
        "Wie schwierig soll der Gast sein?",
        options=["🟢 Einfach", "🟡 Mittel", "🔴 Schwer"],
        value="🔴 Schwer"
    )

    DIFFICULTY_PROMPTS = {
        "🟢 Einfach": "LEVEL: NIEDRIG (3/10). Der Gast ist höflich und nur leicht enttäuscht. Er ist kooperativ.",
        "🟡 Mittel": "LEVEL: MITTEL (6/10). Der Gast ist genervt und bestimmt. Er diskutiert, bleibt aber sachlich.",
        "🔴 Schwer": "LEVEL: EXTREM HOCH (10/10). Der Gast ist emotional, wütend, aggressiv oder arrogant. Schwer zu beruhigen."
    }

    selected_difficulty_prompt = DIFFICULTY_PROMPTS[difficulty_selection]
    
    st.markdown("---")
    st.write("👇 Nächstes Training:")
    
    if st.button("🎲 Neue Situation würfeln"):
        if st.session_state.user_role == "kunde":
            st.session_state.demo_versuche += 1
            
        st.session_state.messages = []
        st.session_state.chat = None
        
        if kategorie == "Hotel":
            st.session_state.current_scenario = random.choice(VARIANTS_HOTEL)
        elif kategorie == "Skischule":
            st.session_state.current_scenario = random.choice(VARIANTS_SKISCHULE)
        elif kategorie == "Seilbahn":
            st.session_state.current_scenario = random.choice(VARIANTS_SEILBAHN)
        elif kategorie == "Restaurant":
            st.session_state.current_scenario = random.choice(VARIANTS_RESTAURANT)
        elif kategorie == "Wellness/Spa":
            st.session_state.current_scenario = random.choice(VARIANTS_WELLNESS)
        elif kategorie == "Einzelhandel":
            st.session_state.current_scenario = random.choice(VARIANTS_EINZELHANDEL)
        elif kategorie == "Touristeninformation":
            st.session_state.current_scenario = random.choice(VARIANTS_TOURISTINFO)
            
        st.session_state.current_difficulty = selected_difficulty_prompt
        st.rerun() 

    st.markdown("---")
    if st.button("Logout"):
        st.session_state.authenticated = False
        st.rerun()

# --- 7. INITIALISIERUNG ---
if "current_scenario" not in st.session_state:
    st.session_state.current_scenario = random.choice(VARIANTS_HOTEL)
if "current_difficulty" not in st.session_state:
    st.session_state.current_difficulty = DIFFICULTY_PROMPTS["🔴 Schwer"]

# --- 8. HAUPTBEREICH ANZEIGE ---
st.title(f"Training: {kategorie}")

with st.expander("ℹ️ Aktuelles Szenario (Bitte lesen)", expanded=True):
    st.info(st.session_state.current_scenario)
    if "NIEDRIG" in st.session_state.current_difficulty:
        st.success("Modus: 🟢 Einfach")
    elif "MITTEL" in st.session_state.current_difficulty:
        st.warning("Modus: 🟡 Mittel")
    else:
        st.error("Modus: 🔴 Schwer")

# --- 9. KI KONFIGURATION ---
SYSTEM_INSTRUCTION = f"""
Du bist ein professioneller Rollenspiel-Bot für Tourismus-Training.
Deine Aufgabe ist es, die Rolle eines Gastes zu spielen.

SZENARIO:
{st.session_state.current_scenario}

ANWEISUNG ZUM VERHALTEN:
{st.session_state.current_difficulty}
Nutze NUR das oben genannte Level.

ANWEISUNGEN:
1. Bleib strikt in der Rolle.
2. Reagiere dynamisch auf den User.
3. WICHTIG: Wenn der User das Codewort "FEEDBACK" schreibt (oder das Problem perfekt gelöst hat),
   wechsle die Persona. Du bist dann ein erfahrener Business-Coach.
   Gib eine professionelle Analyse: Was war gut? Was war schlecht? Gib 3 konkrete Formulierungstipps.
"""

try:
    api_key = st.secrets["GOOGLE_API_KEY"]
except:
    with st.sidebar:
        st.warning("⚠️ API Key nicht in Secrets gefunden.")
        api_key = st.text_input("API Key manuell eingeben", type="password")

if not api_key:
    st.error("Bitte API Key hinterlegen, um zu starten.")
    st.stop()

# --- 10. CHAT ENGINE ---
if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat" not in st.session_state or st.session_state.chat is None:
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.0-flash", system_instruction=SYSTEM_INSTRUCTION)
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
