import streamlit as st
import time
import pandas as pd
from sklearn.linear_model import LinearRegression
import requests  # For OpenWeather API
import random  # For simulation (NEW)

# Config: Replace with your OpenWeather API key
API_KEY = 'your_openweather_api_key_here'  # From openweathermap.org
CITY = 'Coimbatore'  # Or 'Chennai'

# Retro-futuristic CSS
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

# Tabs for Timeline
tab1, tab2, tab3 = st.tabs(["Past", "Present", "Future"])

# Historical Data (simulate or load CSV)
historical_data = pd.DataFrame({
    'Date': pd.date_range(start='2025-01-01', periods=30),
    'Level': [20, 18, 15, 22, 19, 16, 23, 20, 17, 24, 21, 18, 25, 22, 19, 26, 23, 20, 27, 24, 21, 28, 25, 22, 29, 26, 23, 30, 27, 24]
})  # Replace with real data

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

# Impact Metrics
st.sidebar.header("Impact Metrics")
savings = 42  # Example; make dynamic below
st.sidebar.metric("Projected Water Savings", f"{savings}%", "Based on predictions")
st.sidebar.write("Reduces wastage by blending AI with cultural methods.")

# ML Prediction Function
def predict_future(current_levels):
    X = pd.to_numeric(historical_data['Date'].dt.strftime('%s')).values.reshape(-1, 1)
    y = historical_data['Level']
    model = LinearRegression().fit(X, y)
    future_X = [[int(time.time()) + 86400]]  # Tomorrow
    pred = model.predict(future_X)[0]
    
    # OpenWeather Integration
    try:
        weather_url = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}"
        response = requests.get(weather_url).json()
        rain = response['rain']['1h'] if 'rain' in response else 0
        pred += rain * 2  # Adjust for rain
        st.sidebar.metric("Today's Rain Forecast", f"{rain} mm")
    except:
        st.sidebar.error("Weather API error—using base prediction.")
    
    return pred

# Serial Setup with Fallback to Simulation (KEY FIX)
ser = None
try:
    import serial
    ser = serial.Serial('COM3', 9600, timeout=1)  # Try local serial
    st.info("Hardware connected—running live mode.")
except Exception as e:
    st.warning("No hardware detected (cloud mode)—simulating data for demo.")
    # Simulation function
    def simulate_data():
        distance = random.uniform(5, 25)  # Random between full and empty
        pump_status = "ON" if distance > 20 else "OFF"
        return distance, pump_status

# Live Update Loop
while True:
    try:
        if ser:  # Live hardware mode
            line = ser.readline().decode('utf-8').strip()
            if line:
                parts = line.split(',')
                distance = float(parts[0].split(':')[1].strip().replace(' cm', ''))
                pump_status = parts[1].split(':')[1].strip()
        else:  # Simulation mode (cloud)
            distance, pump_status = simulate_data()
        
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
        
        # Update Future Tab & Savings (Dynamic)
        with tab3:
            future_level = predict_future(historical_data['Level'])
            st.metric("Predicted Tomorrow Level", f"{future_level:.1f}%")
            if future_level < 20:
                st.warning("Low prediction—Activate eri revival + auto-pump!")
        
        # Dynamic Savings (Imp. 4 refinement)
        savings = max(0, (100 - future_level) * 0.42)  # Example formula
        st.sidebar.metric("Projected Water Savings", f"{savings:.1f}%")
    
        time.sleep(1)
    except Exception as e:
        st.error(f"Update error: {e}")
        time.sleep(5)  # Retry
