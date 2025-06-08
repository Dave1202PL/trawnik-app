
import streamlit as st
import requests
import json
from datetime import datetime, timedelta

API_KEY = "9517e36e5cc8a496ddcb4673a4b78c5c"
MIASTO = "Pruszcz Gdański"
HISTORIA_PLIKU = "koszenia.json"

def pobierz_pogode():
    url = f"https://api.openweathermap.org/data/2.5/weather?q={MIASTO}&appid={API_KEY}&units=metric&lang=pl"
    res = requests.get(url)
    return res.json()

def zapisz_koszenie(data, poziom):
    try:
        with open(HISTORIA_PLIKU, "r") as f:
            historia = json.load(f)
    except FileNotFoundError:
        historia = []
    historia.append({"data": data, "poziom": poziom})
    with open(HISTORIA_PLIKU, "w") as f:
        json.dump(historia, f)

def ostatnie_koszenie():
    try:
        with open(HISTORIA_PLIKU, "r") as f:
            historia = json.load(f)
        return historia[-1]
    except:
        return None

def ile_dni_od_koszenia(data):
    data_k = datetime.strptime(data, "%Y-%m-%d").date()
    return (datetime.now().date() - data_k).days

def dni_do_koszenia(poziom):
    return {1: 5, 2: 6, 3: 8, 4: 10, 5: 12}.get(poziom, 7)

st.title("🌱 Kiedy kosić trawnik?")
st.caption("Pogodowy doradca trawnika – wersja Panicza")

st.header("1. Zapisz nowe koszenie")
data_koszenia = st.date_input("Data koszenia", value=datetime.today())
poziom = st.slider("Poziom wysokości kosiarki (1 = najkrótsze)", 1, 5, 3)
if st.button("Zapisz koszenie"):
    zapisz_koszenie(data_koszenia.strftime("%Y-%m-%d"), poziom)
    st.success("Zapisano ostatnie koszenie.")

st.header("2. Czy to już czas?")
ostatnie = ostatnie_koszenie()
if ostatnie:
    dni_od = ile_dni_od_koszenia(ostatnie['data'])
    sugerowane_dni = dni_do_koszenia(ostatnie['poziom'])

    st.write(f"🗓 Ostatnie koszenie: **{ostatnie['data']}** (poziom {ostatnie['poziom']})")
    st.write(f"⏳ Minęło: **{dni_od} dni** – rekomendowana przerwa: **{sugerowane_dni} dni**")

    pogoda = pobierz_pogode()
    temp = pogoda['main']['temp']
    opady = pogoda.get('rain', {}).get('1h', 0)
    stan_nieba = pogoda['weather'][0]['description']

    st.write(f"🌡 Temperatura: **{temp}°C**, 🌧 Opady (1h): **{opady} mm**, 🌤 Niebo: {stan_nieba}")

    if dni_od >= sugerowane_dni:
        if opady > 0 or temp < 10:
            st.warning("🛑 To czas na koszenie, ale pogoda jest niesprzyjająca.")
        else:
            st.success("✅ To idealny dzień na koszenie trawnika!")
    else:
        st.info("⏳ Jeszcze trochę – trawa nie zdążyła odrosnąć wystarczająco.")
else:
    st.info("Nie zapisano jeszcze żadnego koszenia.")

st.header("3. Historia koszeń")
try:
    with open(HISTORIA_PLIKU, "r") as f:
        historia = json.load(f)
    for wpis in reversed(historia[-5:]):
        st.text(f"{wpis['data']} – Poziom {wpis['poziom']}")
except:
    st.write("Brak danych.")
