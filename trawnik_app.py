import streamlit as st
import requests
import json
from datetime import datetime, timedelta

# Ustawienia API
API_KEY = "304fdfaedad346adb5f202319250806"
CITY = "Pruszcz Gdański"
API_URL = f"http://api.weatherapi.com/v1/current.json?key={API_KEY}&q={CITY}&aqi=no"

# Funkcja pobierania pogody
def get_weather():
    try:
        response = requests.get(API_URL)
        data = response.json()
        condition = data["current"]["condition"]["text"]
        temp_c = data["current"]["temp_c"]
        is_rain = "rain" in condition.lower()
        humidity = data["current"]["humidity"]
        return {
            "condition": condition,
            "temp_c": temp_c,
            "is_rain": is_rain,
            "humidity": humidity
        }
    except Exception as e:
        return None

# Funkcje do obsługi pliku z koszeniami
DATA_FILE = "koszenia.json"

def load_data():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

def add_entry(date, height_level):
    data = load_data()
    data.append({"date": date, "height_level": height_level})
    save_data(data)

def delete_entry(index):
    data = load_data()
    if 0 <= index < len(data):
        del data[index]
        save_data(data)

# Streamlit UI
st.set_page_config(page_title="Trawnik App", layout="centered")
st.title("🌿 Aplikacja do koszenia trawnika")

menu = st.sidebar.radio("Menu", ["📅 Planowanie koszenia", "📖 Historia koszeń"])

if menu == "📅 Planowanie koszenia":
    st.subheader("Dzisiejsza pogoda w Pruszczu Gdańskim")
    weather = get_weather()

    if weather:
        st.write(f"🌡️ Temperatura: {weather['temp_c']}°C")
        st.write(f"🌧️ Warunki: {weather['condition']}")
        st.write(f"💧 Wilgotność: {weather['humidity']}%")
    else:
        st.warning("Nie udało się pobrać danych pogodowych.")

    st.divider()

    st.subheader("📌 Zapisz nowe koszenie")

    height = st.slider("Poziom wysokości kosiarki (1 - nisko, 5 - wysoko)", 1, 5, 3)
    force_save = st.checkbox("Ignoruj pogodę przy zapisie koszenia")

    today = datetime.now().strftime("%Y-%m-%d")

    if weather and (weather["is_rain"] or weather["humidity"] > 85) and not force_save:
        st.warning("⚠️ Pogoda nie sprzyja koszeniu (deszcz lub zbyt wysoka wilgotność).")
        confirm_bad_weather = st.checkbox("Mimo to potwierdzam koszenie", key="confirm_bad_weather")
        if confirm_bad_weather:
            if st.button("Zapisz koszenie mimo pogody"):
                add_entry(today, height)
                st.success("Zapisano koszenie mimo niekorzystnej pogody.")
    else:
        if st.button("Zapisz nowe koszenie"):
            add_entry(today, height)
            st.success("Koszenie zapisane!")

    st.divider()
    st.subheader("📅 Kiedy znów kosić?")

    data = load_data()
    if data:
        last = data[-1]
        days_passed = (datetime.now() - datetime.strptime(last["date"], "%Y-%m-%d")).days
        suggested_wait = 4 + (5 - int(last["height_level"])) * 1
        next_mow = int(suggested_wait - days_passed)

        if next_mow <= 0:
            st.success("✅ Możesz już kosić! Trawa prawdopodobnie dojrzała.")
        else:
            st.info(f"🕒 Zalecane koszenie za {next_mow} dni.")
    else:
        st.write("Brak danych o poprzednich koszeniach.")

elif menu == "📖 Historia koszeń":
    st.subheader("📖 Historia koszeń")
    data = load_data()
    if data:
        for i, entry in enumerate(data):
            col1, col2, col3 = st.columns([3, 2, 1])
            with col1:
                st.write(f"📅 {entry['date']}")
            with col2:
                st.write(f"🔧 Poziom: {entry['height_level']}")
            with col3:
                if st.button("❌ Usuń", key=f"del_{i}"):
                    delete_entry(i)
                    st.experimental_rerun()
    else:
        st.info("Brak zapisanych koszeń.")
