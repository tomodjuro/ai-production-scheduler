import pandas as pd
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

def ucitaj_sve_podatke():
    """Učitava radne naloge, kapacitete strojeva i zalihe sirovina."""
    nalozi_path = "data/radni_nalozi.csv"
    strojevi_path = "data/strojevi_kapaciteti.csv"
    zalihe_path = "data/zalihe_sirovina.csv"
    
    if not os.path.exists("data"):
        os.makedirs("data")
        
    df_nalozi = pd.read_csv(nalozi_path) if os.path.exists(nalozi_path) else pd.DataFrame()
    df_strojevi = pd.read_csv(strojevi_path) if os.path.exists(strojevi_path) else pd.DataFrame()
    df_zalihe = pd.read_csv(zalihe_path) if os.path.exists(zalihe_path) else pd.DataFrame()
    
    return df_nalozi, df_strojevi, df_zalihe

def analiziraj_proizvodnju():
    """Dinamički analizira opterećenje, kapacitete linija i dostupnost zaliha."""
    df_nalozi, df_strojevi, df_zalihe = ucitaj_sve_podatke()
    
    if df_nalozi.empty:
        return df_nalozi, df_strojevi, df_zalihe

    # Dinamička provjera sirovina na temelju zaliha
    # (Mapiramo proizvode na potrebne materijale ili provjeravamo stupac ako postoji)
    def provjeri_rizik(row):
        # Ako u tablici zaliha imamo zapis za materijal, provjeri dostupnost
        dostupno = row.get("Dostupna_sirovina", True)
        rok = row["Rok_isporuke_dani"]
        sati = row["Potrebno_sati"]
        
        # Pretpostavka: dvosmjenski rad (16h dnevno)
        potrebno_dana = sati / 16.0
        
        if not dostupno:
            return "ČEKANJE SIROVINE"
        elif potrebno_dana > rok:
            return "RIZIK KAŠNJENJA (OTD ugrožen)"
        else:
            return "U ROKU"

    df_nalozi["Status_Planiranja"] = df_nalozi.apply(provjeri_rizik, axis=1)
    return df_nalozi, df_strojevi, df_zalihe

def dodaj_radni_nalog(nalog_id, proizvod, kolicina, linija, potrebno_sati, rok_dani, dostupna_sirovina):
    nalozi_path = "data/radni_nalogi_test.csv" if os.path.exists("data/radni_nalogi_test.csv") else "data/radni_nalogi.csv"
    df_nalozi, _, _ = ucitaj_sve_podatke()
    
    if not df_nalozi.empty and nalog_id in df_nalozi["Nalog_ID"].values:
        return False, f"Nalog s ID-jem '{nalog_id}' već postoji!"
    
    novi_red = {
        "Nalog_ID": nalog_id,
        "Proizvod": proizvod,
        "Kolicina": int(kolicina),
        "Linija": linija,
        "Potrebno_sati": float(potrebno_sati),
        "Rok_isporuke_dani": int(rok_dani),
        "Dostupna_sirovina": bool(dostupna_sirovina)
    }
    
    df_nalozi = pd.concat([df_nalozi, pd.DataFrame([novi_red])], ignore_index=True)
    df_nalozi.to_csv(nalozi_path, index=False)
    
    return True, "Radni nalog je uspješno dodan!"

def pitaj_groq_ai(user_query, df_nalozi, df_strojevi, df_zalihe):
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        return "⚠️ **Greška:** Nije pronađen GROQ_API_KEY u .env datoteci."

    client = Groq(api_key=api_key)
    ugrozeni = df_nalozi[df_nalozi["Status_Planiranja"].str.contains("RIZIK|ČEKANJE")]
    
    system_prompt = f"""
    Ti si stručni AI asistent u planiranju proizvodnje i optimizaciji radnih naloga.
    Trenutno stanje ugroženih radnih naloga:
    {ugrozeni.to_string()}
    
    Kapaciteti strojeva i linija:
    {df_strojevi.to_string()}
    
    Stanje zaliha sirovina:
    {df_zalihe.to_string()}
    
    Tvoj zadatak je dati planeru 3 konkretna koraka kako reorganizirati proizvodnju, riješiti uska grla i osigurati OTD. Odgovaraj profesionalno, ali toplo, na hrvatskom jeziku.
    """
    
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_query}
            ],
            model="openai/gpt-oss-120b",
            temperature=0.3,
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"⚠️ Došlo je do greške prilikom poziva Groq API-ja: {str(e)}"