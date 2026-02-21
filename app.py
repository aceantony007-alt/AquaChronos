import streamlit as st
import serial
import time
import pandas as pd
from sklearn.linear_model import LinearRegression
import requests  # For OpenWeather API (Improvement 2)

# Config: Replace with your COM port, baud, and OpenWeather API key (free from openweathermap.org)
ser = serial.Serial('COM3', 9600, timeout=1)  # Arduino port
API_KEY = 'your_openweather_api_key_here'  # Sign up and get free key
CITY = 'Coimbatore'  # For local weather

# Retro-futuristic CSS (Improvement 3: UI/UX Polish)
st.markdown("""
    <style>
    .stApp { background-color: #0a192f; color: #ccd6f6; }
    .stMetric { background-color: #172a46; border: 1px solid #64ffda; border-radius: 5px; padding: 10px; }
    h1, h2, h3 { color: #64ffda; font-family: 'Courier New', monospace; }
    .css-1aumxhk { background-color: #172a46; }  /* Tabs */
    </style>
""", unsafe_allow_html=True)

st.title("🕰️ AquaChronos: Water Time Machine")
st.subheader("Global Water Management Dashboard")

# Tabs for Timeline (Past, Present, Future)
tab1, tab2, tab3 = st.tabs(["Past", "Present", "Future"])

# Historical Data (simulate or load CSV)
historical_data = pd.DataFrame({
    'Date': pd.date_range(start='2025-01-01', periods=30),
    'Level': [20, 18, 15, 22, 19, 16, 23, 20, 17, 24, 21, 18, 25, 22, 19, 26, 23, 20, 27, 24, 21, 28, 25, 22, 29, 26, 23, 30, 27, 24]
})  # Replace with real IMD/Kaggle CSV

with tab1:
    st.header("Past: Historical Analysis")
    st.line_chart(historical_data.set_index('Date'))
    st.write("Analyzes patterns like droughts; suggests traditional eri systems.")

with tab2:
    st.header("Present: Real-Time Monitoring")
    level_placeholder = st.empty()
    pump_placeholder = st.empty()
    chart_placeholder = st.line_chart(pd.DataFrame({'Level %': [0]}))  # Live chart
    data_history = []  # For chart

with tab3:
    st.header("Future: Predictions & Interventions")

# Impact Metrics Section (Improvement 4)
st.sidebar.header("Impact Metrics")
savings = 42  # Calculated example (Imp. 4: Quantify based on ML)
st.sidebar.metric("Projected Water Savings", f"{savings}%", "Based on predictions")
st.sidebar.write("Reduces wastage by blending AI with cultural methods.")

# ML Prediction Function
def predict_future(current_levels):
    X = pd.to_numeric(historical_data['Date'].dt.strftime('%s')).values.reshape(-1, 1)
    y = historical_data['Level']
    model = LinearRegression().fit(X, y)
    future_X = [[int(time.time()) + 86400]]  # Tomorrow
    pred = model.predict(future_X)[0]
    
    # Integrate OpenWeather (Improvement 2: Advanced Software)
    try:
        weather_url = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}"
        response = requests.get(weather_url).json()
        rain = response['rain']['1h'] if 'rain' in response else 0  # mm/hour
        pred += rain * 2  # Adjust prediction (e.g., rain increases level)
        st.sidebar.metric("Today's Rain Forecast", f"{rain} mm")
    except:
        st.sidebar.error("Weather API error—using base prediction.")
    
    return pred

# Live Update Loop
while True:
    try:
        line = ser.readline().decode('utf-8').strip()
        if line:
            parts = line.split(',')
            distance = float(parts[0].split(':')[1].strip().replace(' cm', ''))
            pump_status = parts[1].split(':')[1].strip()
            
            # Level % (assume 25 cm max empty)
            level_percent = max(0, (25 - distance) / 25 * 100)
            
            # Update Present Tab
            with tab2:
                level_placeholder.metric("Water Level", f"{level_percent:.1f}%", delta=level_percent - 50)
                pump_placeholder.metric("Motor Status", pump_status, delta_color="inverse" if pump_status == "ON" else "normal")
                
                # Chart
                data_history.append(level_percent)
                if len(data_history) > 20: data_history.pop(0)
                chart_placeholder.line_chart(pd.DataFrame({'Level %': data_history}))
            
            # Update Future Tab
            with tab3:
                future_level = predict_future(historical_data['Level'])
                st.metric("Predicted Tomorrow Level", f"{future_level:.1f}%")
                if future_level < 20:
                    st.warning("Low prediction—Activate eri revival + auto-pump!")
    
        time.sleep(1)
    except Exception as e:
        st.error(f"Error: {e}")
        break
