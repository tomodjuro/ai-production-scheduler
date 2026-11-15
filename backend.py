
import pandas as pd
import os
from groq import Groq
from dotenv import load_dotenv

# Učitavanje .env datoteke iz mape projekta
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

# Putanje do podataka
DATA_DIR = os.path.join(BASE_DIR, "data")

NALOZI_PATH = os.path.join(DATA_DIR, "radni_nalozi.csv")
STROJEVI_PATH = os.path.join(DATA_DIR, "strojevi_kapaciteti.csv")
ZALIHE_PATH = os.path.join(DATA_DIR, "zalihe_sirovina.csv")


def ucitaj_sve_podatke():
    """Učitava radne naloge, kapacitete strojeva i zalihe sirovina."""

    os.makedirs(DATA_DIR, exist_ok=True)

    try:
        df_nalozi = (
            pd.read_csv(NALOZI_PATH)
            if os.path.exists(NALOZI_PATH)
            else pd.DataFrame()
        )

        df_strojevi = (
            pd.read_csv(STROJEVI_PATH)
            if os.path.exists(STROJEVI_PATH)
            else pd.DataFrame()
        )

        df_zalihe = (
            pd.read_csv(ZALIHE_PATH)
            if os.path.exists(ZALIHE_PATH)
            else pd.DataFrame()
        )

        return df_nalozi, df_strojevi, df_zalihe

    except Exception as e:
        raise RuntimeError(
            f"Greška prilikom učitavanja podataka: {e}"
        )


def analiziraj_proizvodnju():
    """Dinamički analizira opterećenje, kapacitete linija i dostupnost zaliha."""

    df_nalozi, df_strojevi, df_zalihe = ucitaj_sve_podatke()

    if df_nalozi.empty:
        return df_nalozi, df_strojevi, df_zalihe

    # Provjera potrebnih stupaca
    potrebni_stupci = [
        "Dostupna_sirovina",
        "Rok_isporuke_dani",
        "Potrebno_sati"
    ]

    for stupac in potrebni_stupci:
        if stupac not in df_nalozi.columns:
            raise ValueError(
                f"Nedostaje stupac '{stupac}' u radni_nalozi.csv"
            )

    def provjeri_rizik(row):

        dostupno = row["Dostupna_sirovina"]
        rok = row["Rok_isporuke_dani"]
        sati = row["Potrebno_sati"]

        # Pretvaranje vrijednosti u logički tip
        if isinstance(dostupno, str):
            dostupno = dostupno.strip().lower() in [
                "true", "1", "da", "yes"
            ]

        # Dvosmjenski rad - 16 sati dnevno
        potrebno_dana = float(sati) / 16.0

        if not dostupno:
            return "ČEKANJE SIROVINE"

        elif potrebno_dana > float(rok):
            return "RIZIK KAŠNJENJA (OTD ugrožen)"

        else:
            return "U ROKU"

    df_nalozi["Status_Planiranja"] = df_nalozi.apply(
        provjeri_rizik,
        axis=1
    )

    return df_nalozi, df_strojevi, df_zalihe


def dodaj_radni_nalog(
    nalog_id,
    proizvod,
    kolicina,
    linija,
    potrebno_sati,
    rok_dani,
    dostupna_sirovina
):
    """Dodaje novi radni nalog u CSV datoteku."""

    try:
        os.makedirs(DATA_DIR, exist_ok=True)

        # Učitavanje postojeće datoteke
        if os.path.exists(NALOZI_PATH):
            df_nalozi = pd.read_csv(NALOZI_PATH)
        else:
            df_nalozi = pd.DataFrame()

        # Provjera duplikata
        if (
            not df_nalozi.empty
            and "Nalog_ID" in df_nalozi.columns
            and nalog_id in df_nalozi["Nalog_ID"].astype(str).values
        ):
            return False, f"Nalog s ID-jem '{nalog_id}' već postoji!"

        # Novi radni nalog
        novi_red = {
            "Nalog_ID": nalog_id,
            "Proizvod": proizvod,
            "Kolicina": int(kolicina),
            "Linija": linija,
            "Potrebno_sati": float(potrebno_sati),
            "Rok_isporuke_dani": int(rok_dani),
            "Dostupna_sirovina": bool(dostupna_sirovina)
        }

        # Dodavanje u DataFrame
        df_nalozi = pd.concat(
            [df_nalozi, pd.DataFrame([novi_red])],
            ignore_index=True
        )

        # Spremanje CSV datoteke
        df_nalozi.to_csv(
            NALOZI_PATH,
            index=False,
            encoding="utf-8-sig"
        )

        return True, "Radni nalog je uspješno dodan!"

    except PermissionError:
        return False, (
            "Datoteka je zaključana ili nemaš dozvolu "
            "za spremanje. Zatvori CSV datoteku u Excelu."
        )

    except Exception as e:
        return False, f"Greška prilikom spremanja naloga: {e}"


def pitaj_groq_ai(user_query, df_nalozi, df_strojevi, df_zalihe):
    """AI asistent za planiranje proizvodnje putem Groq API-ja."""

    api_key = os.environ.get("GROQ_API_KEY")

    if not api_key:
        return (
            "⚠️ Greška: Nije pronađen GROQ_API_KEY "
            "u .env datoteci."
        )

    try:
        client = Groq(
            api_key=api_key,
            timeout=30.0,
            max_retries=2
        )

        # Provjera ugroženih naloga
        if (
            not df_nalozi.empty
            and "Status_Planiranja" in df_nalozi.columns
        ):
            ugrozeni = df_nalozi[
                df_nalozi["Status_Planiranja"].astype(str).str.contains(
                    "RIZIK|ČEKANJE",
                    case=False,
                    na=False
                )
            ]
        else:
            ugrozeni = pd.DataFrame()

        system_prompt = f"""
Ti si stručni AI asistent u planiranju proizvodnje
i optimizaciji radnih naloga.

Tvoj zadatak je pomoći planeru u optimizaciji proizvodnje.

TRENUTNO STANJE UGROŽENIH RADNIH NALOGA:
{ugrozeni.to_string(index=False)}

KAPACITETI STROJEVA I PROIZVODNIH LINIJA:
{df_strojevi.to_string(index=False)}

STANJE ZALIHA SIROVINA:
{df_zalihe.to_string(index=False)}

Na temelju dostupnih podataka:

1. Analiziraj ugrožene radne naloge.
2. Identificiraj uska grla u proizvodnji.
3. Predloži 3 konkretna koraka za reorganizaciju proizvodnje.
4. Predloži kako poboljšati OTD (On-Time Delivery).
5. Upozori na nedostatak sirovina i kapaciteta.

Odgovaraj profesionalno, jasno i konkretno,
na hrvatskom jeziku.

Nemoj izmišljati podatke koji nisu navedeni.
"""

        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_query
                }
            ],
            model="openai/gpt-oss-120b",
            temperature=0.3,
        )

        return chat_completion.choices[0].message.content

    except Exception as e:
        return (
            "⚠️ Došlo je do greške prilikom poziva Groq API-ja: "
            f"{type(e).__name__}: {str(e)}"
        )
