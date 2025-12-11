import streamlit as st
import google.generativeai as genai
import os
import random
import time

# --- 1. SEITEN-KONFIGURATION ---
st.set_page_config(page_title="Tourismus-Trainer", page_icon="🎓")

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
        
        # Stabile Text-Variable für Abschlussnachricht
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

# --- 5. SZENARIEN POOL (Praxisnah & Realistisch) ---

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
    Situation: Du hast reserviert ("Tisch mit Platz für Kinderwagen"). Man gibt dir einen Hochtisch mitten im Gang.
    Dein Ziel: Ein passender Tisch sofort, wie bestellt.""",

    """Deine Rolle: Herr Zeller, Geschäftsessen.
    Situation: Du hast Kunden eingeladen. Der Wein schmeckt nach Kork. Der Kellner meint: "Das gehört so."
    Dein Ziel: Du willst nicht blamiert werden. Der Wein muss weg, neue Flasche, ohne Diskussion."""
]

VARIANTS_WELLNESS = [
    """Deine Rolle: Frau Dr. Schmidt.
    Situation: Du hast 90 Min Massage bezahlt (180€). Nach 65 Min sagt die Masseurin "Fertig".
    Dein Ziel: Klärung. Du zahlst nicht für 90 Min, wenn du nur 65 bekommst.""",
    
    """Deine Rolle: Herr Wagner, Hygiene-Fanatiker.
    Situation: In der Sauna liegen benutzte Becher und Haare.
    Dein Ziel: Du beschwerst dich lautstark an der Spa-Rezeption. Das entspricht nicht dem 4-Sterne-Standard.""",
    
    """Deine Rolle: Frau Steiner, Stammgast.
    Situation: Du wolltest deine Lieblings-Therapeutin Lisa. Stattdessen kommt ein neuer Mitarbeiter ohne Vorwarnung.
    Dein Ziel: Du bist enttäuscht. Du willst Lisa oder den Termin stornieren.""",

    """Deine Rolle: Herr Fink.
    Situation: Der Ruheraum ist laut, Leute telefonieren. Personal unternimmt nichts.
    Dein Ziel: Du forderst, dass das Personal für Ruhe sorgt. Sofort."""
]

VARIANTS_EINZELHANDEL = [
    """Deine Rolle: Herr Bauer, Tourist.
    Situation: Du hast gestern eine teure Funktionsjacke (400€) gekauft. Heute geht der Reißverschluss auf.
    Dein Ziel: Umtausch oder Geld zurück. Keine Reparatur (dauert zu lange, du reist morgen ab).""",
    
    """Deine Rolle: Frau Novak.
    Situation: Du möchtest ein Souvenir zurückgeben, weil es dem Enkel nicht gefällt. Die Verkäuferin sagt "Reduzierte Ware vom Umtausch ausgeschlossen".
    Dein Ziel: Kulanz. Du hast extra gefragt!""",
    
    """Deine Rolle: Herr Gruber.
    Situation: Lange Schlange an der Kasse (10 Leute), nur eine Kasse offen. Zwei Mitarbeiter ratschen im Hintergrund.
    Dein Ziel: "Macht gefälligst eine zweite Kasse auf!".""",

    """Deine Rolle: Sammler.
    Situation: Du hast ein limitiertes Produkt reservieren lassen. Jetzt ist es weg ("verkauft").
    Dein Ziel: Du bist fassungslos. Du willst wissen, wer das verbockt hat."""
]

VARIANTS_TOURISTINFO = [
    """Deine Rolle: Familie Maier.
    Situation: Die Dame an der Info hat euch gestern auf eine Hütte geschickt. Die hatte Ruhetag. Ihr seid 2 Stunden umsonst gewandert mit Kindern.
    Dein Ziel: Ihr wollt euch beschweren über die schlechte Beratung.""",
    
    """Deine Rolle: Herr Kovac.
    Situation: Du willst ein Ticket für das Event heute Abend. Es ist ausverkauft. Auf der Website stand "Tickets an der Abendkasse".
    Dein Ziel: Du willst rein. Du hast dich auf die Website verlassen.""",
    
    """Deine Rolle: Frau Weber (Rollstuhlfahrerin).
    Situation: Der "barrierefreie Wanderweg" aus der Broschüre hat Stufen.
    Dein Ziel: Du bist wütend und enttäuscht. Du meldest das der Info.""",

    """Deine Rolle: Herr Wimmer.
    Situation: Du hast die "Gäste-Card" gekauft. Jetzt erfährst du, dass das Museum heute zu hat.
    Dein Ziel: Geld für die Karte zurück."""
]

# --- 6. SEITENLEISTE (Steuerung) ---
with st.sidebar:
    # Info-Anzeige
    if st.session_state.user_role == "kunde":
        st.write(f"Test-Modus: Runde {st.session_state.demo_versuche + 1} von {MAX_VERSUCHE}")
        st.progress((st.session_state.demo_versuche) / MAX_VERSUCHE)
    else:
        st.success(f"Angemeldet als: {PW_ADMIN} (Admin)")

    st.header("🎭 Einstellungen")
    
    # KATEGORIE
    kategorie = st.selectbox(
        "Bereich wählen:", 
        ("Hotel", "Skischule", "Seilbahn", "Restaurant", "Wellness/Spa", "Einzelhandel", "Touristeninformation")
    )

    # SCHWIERIGKEIT
    st.markdown("### 🎚️ Schwierigkeit")
    difficulty_selection = st.select_slider(
        "Wie hartnäckig ist der Gast?",
        options=["🟢 Einfach", "🟡 Mittel", "🔴 Schwer"],
        value="🔴 Schwer"
    )

    # DEFINITION DER HARTNÄCKIGKEIT (Das Gehirn der Simulation)
    DIFFICULTY_PROMPTS = {
        "🟢 Einfach": """
        LEVEL: KOOPERATIV (3/10).
        VERHALTEN: Du bist zwar kurz enttäuscht/genervt, aber du suchst Harmonie.
        HARTNÄCKIGKEIT: Sobald der Mitarbeiter eine freundliche Entschuldigung O
