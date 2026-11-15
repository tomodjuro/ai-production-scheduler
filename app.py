
import streamlit as st
import pandas as pd

from backend import (
    analiziraj_proizvodnju,
    pitaj_groq_ai,
    dodaj_radni_nalog
)

# --------------------------------------------------
# 1. KONFIGURACIJA STRANICE
# --------------------------------------------------

st.set_page_config(
    page_title="AI Production Scheduler & Bottleneck Predictor",
    page_icon="⚙️",
    layout="wide"
)

st.title("⚙️ AI Production Scheduler & Bottleneck Predictor")

st.markdown(
    "**Modul:** Optimizacija radnih naloga, "
    "kapaciteta strojeva i zaliha sirovina"
)

# --------------------------------------------------
# 2. UČITAVANJE PODATAKA
# --------------------------------------------------

try:
    df_analiza, df_strojevi, df_zalihe = analiziraj_proizvodnju()

except Exception as e:
    st.error(f"Greška prilikom učitavanja podataka: {e}")
    st.stop()


# Osiguranje da DataFrame ima očekivane stupce
if "Status_Planiranja" not in df_analiza.columns:
    df_analiza["Status_Planiranja"] = pd.Series(
        dtype="object"
    )

# --------------------------------------------------
# 3. SIDEBAR - UNOS NOVOG RADNOG NALOGA
# --------------------------------------------------

st.sidebar.header("➕ Novi radni nalog")

proizvodi = [
    "Cijevni grijač A1",
    "Kapilarni termostat T2",
    "Rotacijski prekidač P3",
    "Grijača ploča HP4",
    "Regulator temperature R5"
]

if not df_strojevi.empty and "Linija_ID" in df_strojevi.columns:
    linije = df_strojevi["Linija_ID"].dropna().astype(str).tolist()
else:
    linije = ["Linija-1"]

with st.sidebar.form("form_novi_nalog"):

    novi_id = st.text_input(
        "Nalog ID",
        value="RN-307"
    )

    novi_proizvod = st.selectbox(
        "Proizvod",
        proizvodi
    )

    nova_kolicina = st.number_input(
        "Količina (kom)",
        min_value=1,
        value=500,
        step=50
    )

    nova_linija = st.selectbox(
        "Proizvodna linija",
        linije
    )

    potrebno_sati = st.number_input(
        "Potrebno sati rada",
        min_value=1.0,
        value=16.0,
        step=1.0
    )

    rok_dani = st.number_input(
        "Rok isporuke (dani od danas)",
        min_value=1,
        value=2,
        step=1
    )

    dostupna_sirovina = st.checkbox(
        "Dostupna sirovina na skladištu",
        value=True
    )

    submit_button = st.form_submit_button(
        label="Spremi nalog",
        use_container_width=True
    )

if submit_button:

    if not novi_id.strip():
        st.sidebar.error("Unesi ID radnog naloga.")

    else:
        uspjeh, poruka = dodaj_radni_nalog(
            novi_id.strip(),
            novi_proizvod,
            nova_kolicina,
            nova_linija,
            potrebno_sati,
            rok_dani,
            dostupna_sirovina
        )

        if uspjeh:
            st.sidebar.success(poruka)
            st.rerun()

        else:
            st.sidebar.error(poruka)


# --------------------------------------------------
# 4. KPI KARTICE
# --------------------------------------------------

ukupno_naloga = len(df_analiza)

ugrozeni_nalozi = len(
    df_analiza[
        df_analiza["Status_Planiranja"]
        .astype(str)
        .str.contains(
            "RIZIK|ČEKANJE",
            case=False,
            na=False
        )
    ]
)

uredni_nalozi = ukupno_naloga - ugrozeni_nalozi

st.subheader("📊 Pregled proizvodnje")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label="Ukupno radnih naloga",
        value=ukupno_naloga
    )

with col2:
    st.metric(
        label="Ugroženi nalozi (OTD rizik)",
        value=ugrozeni_nalozi,
        delta=f"-{ugrozeni_nalozi}",
        delta_color="inverse"
    )

with col3:
    st.metric(
        label="Nalozi u roku",
        value=uredni_nalozi,
        delta="Stabilno"
    )

st.divider()


# --------------------------------------------------
# 5. TABOVI - PREGLED PODATAKA
# --------------------------------------------------

tab1, tab2, tab3 = st.tabs([
    "📋 Radni nalozi i OTD",
    "🏭 Kapaciteti strojeva",
    "📦 Zalihe sirovina"
])


# TAB 1 - RADNI NALOZI

with tab1:

    st.subheader("Pregled radnih naloga i statusa planiranja")

    if df_analiza.empty:

        st.info("Trenutno nema evidentiranih radnih naloga.")

    else:

        def oboji_status(val):

            val = str(val)

            if "RIZIK" in val:
                return (
                    "background-color: #ffcccc; "
                    "color: #990000; font-weight: bold;"
                )

            elif "ČEKANJE" in val:
                return (
                    "background-color: #fff2cc; "
                    "color: #b26b00; font-weight: bold;"
                )

            else:
                return (
                    "background-color: #d9ead3; "
                    "color: #274e13; font-weight: bold;"
                )

        if "Status_Planiranja" in df_analiza.columns:

            stil = df_analiza.style.map(
                oboji_status,
                subset=["Status_Planiranja"]
            )

            st.dataframe(
                stil,
                width="stretch"
            )

        else:

            st.dataframe(
                df_analiza,
                width="stretch"
            )


# TAB 2 - STROJEVI

with tab2:

    st.subheader("Stanje proizvodnih linija i kapaciteta")

    if df_strojevi.empty:

        st.warning("Nema dostupnih podataka o kapacitetima strojeva.")

    else:

        st.dataframe(
            df_strojevi,
            width="stretch"
        )


# TAB 3 - ZALIHE

with tab3:

    st.subheader("Stanje skladišta sirovina i očekivane isporuke")

    if df_zalihe.empty:

        st.warning("Nema dostupnih podataka o zalihama sirovina.")

    else:

        st.dataframe(
            df_zalihe,
            width="stretch"
        )


# --------------------------------------------------
# 6. AI ASISTENT - GROQ API
# --------------------------------------------------

st.divider()

st.subheader("💬 AI Asistent za planiranje (Groq LLM)")

st.markdown(
    "Postavi pitanje o proizvodnji, kapacitetima, "
    "uskim grlima ili dostupnosti sirovina."
)

# Inicijalizacija povijesti razgovora
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


# Prikaz prethodnih poruka
for poruka in st.session_state.chat_history:

    with st.chat_message(poruka["role"]):
        st.markdown(poruka["content"])


# Unos novog pitanja
user_query = st.chat_input(
    "Pitaj asistenta npr.: Koje linije imaju uska grla?"
)


if user_query:

    # Spremanje korisničkog pitanja
    st.session_state.chat_history.append({
        "role": "user",
        "content": user_query
    })

    with st.chat_message("user"):
        st.markdown(user_query)

    # Poziv AI asistenta
    with st.chat_message("assistant"):

        with st.spinner(
            "AI analizira naloge, kapacitete strojeva i zalihe..."
        ):

            ai_odgovor = pitaj_groq_ai(
                user_query,
                df_analiza,
                df_strojevi,
                df_zalihe
            )

        st.markdown(ai_odgovor)

    # Spremanje AI odgovora
    st.session_state.chat_history.append({
        "role": "assistant",
        "content": ai_odgovor
    })


# --------------------------------------------------
# 7. BRISANJE POVIJESTI RAZGOVORA
# --------------------------------------------------

if st.session_state.chat_history:

    if st.button("🗑️ Obriši povijest razgovora"):

        st.session_state.chat_history = []
        st.rerun()


# --------------------------------------------------
# 8. PODNOŽJE
# --------------------------------------------------

st.divider()

st.caption(
    "AI Production Scheduler | "
    "Production Planning & Bottleneck Prediction"
)
