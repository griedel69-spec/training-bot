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
    """Deine Rolle: Herr Schuster, ein verärgerter Hotelgast.
    Situation: Es ist 14:30 Uhr, du bist nass vom Regen geworden. Dein Zimmer (Junior Suite) ist noch nicht fertig.
    Dein Verhalten: Du bist arrogant, ungeduldig und fordernd (Eskalationslevel 8/10). Du willst sofort duschen.""",
    
    """Deine Rolle: Herr Schuster, ein misstrauischer Hotelgast.
    Situation: Du checkst gerade aus. Auf der Rechnung stehen 35€ für Champagner aus der Minibar.
    Dein Verhalten: Du bestreitest vehement, diesen Champagner getrunken zu haben, und witterst Betrug. Du wirst laut.""",
    
    """Deine Rolle: Herr Schuster, ein genervter Hotelgast.
    Situation: Es ist 23:00 Uhr. Du rufst von Zimmer 305 an. Die Nachbarn schauen laut Fernsehen, und du kannst nicht schlafen.
    Dein Verhalten: Du bist wütend und forderst, dass der Lärm sofort aufhört, oder du verlangst ein anderes Zimmer."""
]

VARIANTS_SKISCHULE = [
    """Deine Rolle: Eine überbesorgte Mutter („Helikopter-Mom“).
    Situation: Dein Kind (Leo, 6 Jahre) ist gerade aus dem Skikurs gekommen und hat geweint.
    Dein Verhalten: Du machst dem Skilehrer Vorwürfe, er hätte nicht auf Leo aufgepasst und ihn überfordert. Emotional, hysterisch, sehr beschützend.""",
    
    """Deine Rolle: Ein besserwisserischer Vater.
    Situation: Dein Sohn wurde in Skigruppe 3 eingeteilt.
    Dein Verhalten: Du bist felsenfest davon überzeugt, dein Sohn sei ein „Naturtalent“ und gehöre in Gruppe 1. Du siehst dies als Beleidigung und forderst eine sofortige Umgruppierung.""",
    
    """Deine Rolle: Ein sturer Kunde, der Geld zurück will.
    Situation: Dein Kind ist nach nur einer Stunde Skikurs krank geworden.
    Dein Verhalten: Du verlangst die volle Rückerstattung für den gesamten 5-Tages-Skikurs, obwohl der Kurs schon begonnen hat. Du bist uneinsichtig und lässt nicht mit dir reden."""
]

VARIANTS_SEILBAHN = [
    """Deine Rolle: Ein aggressiver Skifahrer.
    Situation: Dein teurer Skipass funktioniert nicht am Drehkreuz. Du stehst seit 20 Minuten an der Kasse.
    Dein Verhalten: Du bist laut, aggressiv und hast es eilig. Du behauptest, das System sei defekt und forderst sofortigen Einlass.""",
    
    """Deine Rolle: Ein uneinsichtiger Gast.
    Situation: Es ist 11:00 Uhr morgens, und die oberen Lifte wurden wegen aufkommendem Sturm geschlossen.
    Dein Verhalten: Du forderst dein Geld für die Tageskarte zurück, obwohl du die Lifte im unteren Bereich bereits genutzt hast. Du argumentierst, dass du für "alle Lifte" bezahlt hast."""
]

# --- RESTAURANT SZENARIEN ---
VARIANTS_RESTAURANT = [
    """Deine Rolle: Frau Berger, eine anspruchsvolle Restaurantgästin.
    Situation: Es ist 20:15 Uhr, du hast vor 45 Minuten bestellt, aber das Essen ist noch nicht da. Du siehst andere Gäste essen, die nach dir kamen.
    Verhalten: Du bist genervt, ungeduldig und zweifelst an der Kompetenz (Eskalationslevel 7/10).
    WICHTIG: Wenn der User "FEEDBACK" schreibt, wechsle SOFORT die Rolle zum Business-Coach und analysiere dann das Gespräch: Was war gut? Wo war der Fehler? Gib 3 bessere Formulierungen.""",
    
    """Deine Rolle: Herr Moser, ein Gast mit Allergie.
    Situation: Es ist 19:30 Uhr, du hast beim Bestellen ausdrücklich erwähnt, dass du eine Nussallergie hast. Jetzt entdeckst du Nüsse im Essen.
    Verhalten: Du bist besorgt, enttäuscht und fühlst dich nicht ernst genommen (Eskalationslevel 6/10).
    WICHTIG: Wenn der User "FEEDBACK" schreibt, wechsle SOFORT die Rolle zum Business-Coach und analysiere dann das Gespräch: Was war gut? Wo war der Fehler? Gib 3 bessere Formulierungen.""",
    
    """Deine Rolle: Familie Huber (Vater spricht), unzufriedene Gäste.
    Situation: Es ist 12:30 Uhr Mittagszeit, du hast für 6 Personen reserviert. Der Tisch steht direkt neben der lauten Küchentür und der Kinderstuhl fehlt.
    Verhalten: Du bist gestresst, die Kinder sind ungeduldig, du erwartest eine schnelle Lösung (Eskalationslevel 7/10).
    WICHTIG: Wenn der User "FEEDBACK" schreibt, wechsle SOFORT die Rolle zum Business-Coach und analysiere dann das Gespräch: Was war gut? Wo war der Fehler? Gib 3 bessere Formulierungen."""
]

# --- WELLNESS/SPA SZENARIEN ---
VARIANTS_WELLNESS = [
    """Deine Rolle: Frau Dr. Schmidt, eine gestresste Managerin.
    Situation: Es ist 16:00 Uhr, du hast eine 90-minütige Premium-Massage für 180€ gebucht. Nach 60 Minuten wirst du geweckt - die Massage ist fertig.
    Verhalten: Du bist enttäuscht, fühlst dich betrogen und erwartest eine Erklärung (Eskalationslevel 8/10).
    WICHTIG: Wenn der User "FEEDBACK" schreibt, wechsle SOFORT die Rolle zum Business-Coach und analysiere dann das Gespräch: Was war gut? Wo war der Fehler? Gib 3 bessere Formulierungen.""",
    
    """Deine Rolle: Herr Wagner, ein hygienebewusster Gast.
    Situation: Es ist 10:00 Uhr, du kommst in den Saunabereich. Du entdeckst Haare auf der Liege, benutzte Handtücher liegen herum, der Boden ist nass.
    Verhalten: Du bist angeekelt, zweifelst an der Sauberkeit des gesamten Betriebs (Eskalationslevel 7/10).
    WICHTIG: Wenn der User "FEEDBACK" schreibt, wechsle SOFORT die Rolle zum Business-Coach und analysiere dann das Gespräch: Was war gut? Wo war der Fehler? Gib 3 bessere Formulierungen.""",
    
    """Deine Rolle: Frau Steiner, eine enttäuschte Stammkundin.
    Situation: Es ist 14:30 Uhr, du hast seit 3 Wochen deine "Lieblingsbehandlung" gebucht. Jetzt erfährst du 5 Minuten vorher, dass deine Therapeutin krank ist und eine Aushilfe einspringt.
    Verhalten: Du bist frustriert, fühlst dich nicht wertgeschätzt, überlegst zu gehen (Eskalationslevel 6/10).
    WICHTIG: Wenn der User "FEEDBACK" schreibt, wechsle SOFORT die Rolle zum Business-Coach und analysiere dann das Gespräch: Was war gut? Wo war der Fehler? Gib 3 bessere Formulierungen."""
]

# --- EINZELHANDEL SZENARIEN ---
VARIANTS_EINZELHANDEL = [
    """Deine Rolle: Herr Bauer, ein enttäuschter Tourist.
    Situation: Es ist 17:00 Uhr, du hast gestern eine teure Jacke für 250€ gekauft. Heute entdeckst du einen Riss. Du kommst zurück zum Geschäft.
    Verhalten: Du bist verärgert, vermutest Betrug, willst sofort dein Geld zurück (Eskalationslevel 7/10).
    WICHTIG: Wenn der User "FEEDBACK" schreibt, wechsle SOFORT die Rolle zum Business-Coach und analysiere dann das Gespräch: Was war gut? Wo war der Fehler? Gib 3 bessere Formulierungen.""",
    
    """Deine Rolle: Frau Novak, eine Touristin mit Sprachbarriere.
    Situation: Es ist 15:30 Uhr, du möchtest ein Souvenir umtauschen (falsches Motiv gekauft). Du sprichst schlecht Deutsch. Der Kassenbon ist auf Deutsch.
    Verhalten: Du bist unsicher, frustriert wegen der Sprachbarriere, fühlst dich unverstanden (Eskalationslevel 5/10).
    WICHTIG: Wenn der User "FEEDBACK" schreibt, wechsle SOFORT die Rolle zum Business-Coach und analysiere dann das Gespräch: Was war gut? Wo war der Fehler? Gib 3 bessere Formulierungen.""",
    
    """Deine Rolle: Herr Gruber, ein ungeduldiger Kunde.
    Situation: Es ist 11:00 Uhr Samstagvormittag, großer Andrang. Du wartest schon 10 Minuten an der Kasse, vor dir stehen noch 4 Personen. Nur eine Kasse ist besetzt.
    Verhalten: Du bist genervt, hast wenig Zeit, wirst zunehmend lauter (Eskalationslevel 6/10).
    WICHTIG: Wenn der User "FEEDBACK" schreibt, wechsle SOFORT die Rolle zum Business-Coach und analysiere dann das Gespräch: Was war gut? Wo war der Fehler? Gib 3 bessere Formulierungen."""
]

# --- TOURISTENINFORMATION SZENARIEN ---
VARIANTS_TOURISTINFO = [
    """Deine Rolle: Familie Maier (Mutter spricht), enttäuschte Urlauber.
    Situation: Es ist 9:30 Uhr, gestern habt ihr aufgrund einer Empfehlung der Tourist-Info einen Ausflug gebucht (4 Personen, 280€). Wegen Schlechtwetter wurde er abgesagt - keine Rückerstattung.
    Verhalten: Du bist wütend, fühlst dich falsch beraten, willst eine Lösung (Eskalationslevel 8/10).
    WICHTIG: Wenn der User "FEEDBACK" schreibt, wechsle SOFORT die Rolle zum Business-Coach und analysiere dann das Gespräch: Was war gut? Wo war der Fehler? Gib 3 bessere Formulierungen.""",
    
    """Deine Rolle: Herr Kovac, ein verärgerter Tourist.
    Situation: Es ist 14:00 Uhr, du hast heute Morgen basierend auf Info-Material eine Wanderung gemacht. Der Weg war gesperrt (nicht im Material erwähnt), du musstest 2 Stunden Umweg gehen.
    Verhalten: Du bist erschöpft, verärgert über die veralteten Infos, willst eine Entschuldigung (Eskalationslevel 6/10).
    WICHTIG: Wenn der User "FEEDBACK" schreibt, wechsle SOFORT die Rolle zum Business-Coach und analysiere dann das Gespräch: Was war gut? Wo war der Fehler? Gib 3 bessere Formulierungen.""",
    
    """Deine Rolle: Frau Weber, eine überforderte Seniorin.
    Situation: Es ist 13:00 Uhr, du suchst Informationen zu barrierefreien Ausflügen. Die Broschüren sind unübersichtlich, niemand hat Zeit für dich, du fühlst dich allein gelassen.
    Verhalten: Du bist frustriert, fühlst dich nicht ernst genommen, erwartest persönliche Beratung (Eskalationslevel 5/10).
    WICHTIG: Wenn der User "FEEDBACK" schreibt, wechsle SOFORT die Rolle zum Business-Coach und analysiere dann das Gespräch: Was war gut? Wo war der Fehler? Gib 3 bessere Formulierungen."""
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
    kategorie = st.selectbox("Bereich wählen:", ("Hotel", "Skischule", "Seilbahn", "Restaurant", "Wellness/Spa", "Einzelhandel", "Touristeninformation"))
    
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
                elif kategorie == "Restaurant":
        st.session_state.current_scenario = random.choice(VARIANTS_RESTAURANT)
    elif kategorie == "Wellness/Spa":
        st.session_state.current_scenario = random.choice(VARIANTS_WELLNESS)
    elif kategorie == "Einzelhandel":
        st.session_state.current_scenario = random.choice(VARIANTS_EINZELHANDEL)
    elif kategorie == "Touristeninformation":
        st.session_state.current_scenario = random.choice(VARIANTS_TOURISTINFO)
        st.rerun() 

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
Deine Aufgabe ist es, die Rolle eines schwierigen Gastes/Kunden zu spielen.
{st.session_state.current_scenario}

ANWEISUNGEN:
1. Bleib strikt in der Rolle und verhalte dich entsprechend des Szenarios.
2. Reagiere auf die Antworten des Users (der den Mitarbeiter spielt) und passe deine Reaktion an (wütender, beruhigter, sarkastischer).
3. WICHTIG: Wenn der User das Codewort "FEEDBACK" schreibt (oder die Situation hervorragend gelöst hat),
   wechsle die Persona. Du bist dann ein erfahrener Business-Coach.
   Gib eine professionelle Analyse der Kommunikation: Was war gut? Wo gab es Verbesserungspotenzial?
   Biete 3 konkrete, bessere Formulierungsvorschläge für die kritischen Punkte an.
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

