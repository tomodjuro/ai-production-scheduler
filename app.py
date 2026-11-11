import streamlit as st
import pandas as pd
from backend import analiziraj_proizvodnju, pitaj_groq_ai, dodaj_radni_nalog

# Konfiguracija stranice
st.set_page_config(
    page_title="AI Production Scheduler & Bottleneck Predictor",
    page_icon="⚙️",
    layout="wide"
)

st.title("⚙️ AI Production Scheduler & Bottleneck Predictor")
st.markdown("**Modul:** Optimizacija radnih naloga, kapaciteta strojeva i zaliha sirovina")

# Učitavanje svih podataka iz backenda
df_analiza, df_strojevi, df_zalihe = analiziraj_proizvodnju()

# --- SIDEBAR: Forma za unos novog radnog naloga ---
st.sidebar.header("➕ Novi radni nalog")

with st.sidebar.form("form_novi_nalog"):
    novi_id = st.text_input("Nalog ID", value="RN-307")
    novi_proizvod = st.selectbox("Proizvod", ["Cijevni grijač A1", "Kapilarni termostat T2", "Rotacijski prekidač P3", "Grijača ploča HP4", "Regulator temperature R5"])
    nova_kolicina = st.number_input("Količina (kom)", min_value=1, value=500, step=50)
    nova_linija = st.selectbox("Proizvodna linija", df_strojevi["Linija_ID"].tolist() if not df_strojevi.empty else ["Linija-1"])
    potrebno_sati = st.number_input("Potrebno sati rada", min_value=1.0, value=16.0, step=1.0)
    rok_dani = st.number_input("Rok isporuke (dani od danas)", min_value=1, value=2, step=1)
    dostupna_sirovina = st.checkbox("Dostupna sirovina na skladištu", value=True)
    
    submit_button = st.form_submit_button(label="Spremi nalog")

if submit_button:
    uspjeh, poruka = dodaj_radni_nalog(novi_id, novi_proizvod, nova_kolicina, nova_linija, potrebno_sati, rok_dani, dostupna_sirovina)
    if uspjeh:
        st.sidebar.success(poruka)
        st.rerun()
    else:
        st.sidebar.error(poruka)

# --- SEKCIJA 1: KPI Kartice ---
col1, col2, col3 = st.columns(3)
ukupno_naloga = len(df_analiza)
ugrozeni_nalozi = len(df_analiza[df_analiza["Status_Planiranja"].str.contains("RIZIK|ČEKANJE")])
uredni_nalozi = ukupno_naloga - ugrozeni_nalozi

with col1:
    st.metric(label="Ukupno radnih naloga", value=ukupno_naloga)
with col2:
    st.metric(label="Ugroženi nalozi (OTD rizik)", value=ugrozeni_nalozi, delta=f"-{ugrozeni_nalozi}", delta_color="inverse")
with col3:
    st.metric(label="Nalozi u roku", value=uredni_nalozi, delta="Stabilno")

st.divider()

# --- SEKCIJA 2: Tabovi za detaljan pregled (Radni nalozi, Strojevi, Zalihe) ---
tab1, tab2, tab3 = st.tabs(["📋 Radni nalozi i OTD", "🏭 Kapaciteti strojeva", "📦 Zalihe sirovina"])

with tab1:
    st.subheader("Pregled radnih naloga i statusa planiranja")
    def oboji_status(val):
        if "RIZIK" in val:
            return 'background-color: #ffcccc; color: #990000; font-weight: bold;'
        elif "ČEKANJE" in val:
            return 'background-color: #fff2cc; color: #b26b00; font-weight: bold;'
        else:
            return 'background-color: #d9ead3; color: #274e13; font-weight: bold;'

    st.dataframe(df_analiza.style.map(oboji_status, subset=["Status_Planiranja"]), use_container_width=True)

with tab2:
    st.subheader("Stanje proizvodnih linija i kapaciteta")
    st.dataframe(df_strojevi, use_container_width=True)

with tab3:
    st.subheader("Stanje skladišta sirovina i očekivane isporuke")
    st.dataframe(df_zalihe, use_container_width=True)

# --- SEKCIJA 3: AI Asistent (Groq API Integracija s punim kontekstom) ---
st.divider()
st.subheader("💬 AI Asistent za planiranje (Groq LLM)")

user_query = st.chat_input("Pitaj asistenta npr.: 'Koje linije imaju uska grla i kako da riješimo nedostatak materijala?'")

if user_query:
    st.chat_message("user").write(user_query)
    
    with st.spinner("AI analizira naloge, kapacitete strojeva i zalihe..."):
        ai_odgovor = pitaj_groq_ai(user_query, df_analiza, df_strojevi, df_zalihe)
        
    st.chat_message("assistant").write(ai_odgovor)