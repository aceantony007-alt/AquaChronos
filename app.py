import streamlit as st
import time
import pandas as pd
from sklearn.linear_model import LinearRegression
import requests
import random  # For simulation fallback
from streamlit.components.v1 import html  # For JS embedding (NEW)

# Config
API_KEY = 'your_openweather_api_key_here'  # OpenWeather key
CITY = 'Coimbatore'
BAUD_RATE = 9600  # Your Arduino baud

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

# Tabs
tab1, tab2, tab3 = st.tabs(["Past", "Present", "Future"])

# Historical Data
historical_data = pd.DataFrame({
    'Date': pd.date_range(start='2025-01-01', periods=30),
    'Level': [20, 18, 15, 22, 19, 16, 23, 20, 17, 24, 21, 18, 25, 22, 19, 26, 23, 20, 27, 24, 21, 28, 25, 22, 29, 26, 23, 30, 27, 24]
})

with tab1:
    st.header("Past: Historical Analysis")
    st.line_chart(historical_data.set_index('Date'))
    st.write("Analyzes patterns like droughts; suggests traditional eri systems.")

with tab2:
    st.header("Present: Real-Time Monitoring")
    level_placeholder = st.empty()
    pump_placeholder = st.empty()
    chart_placeholder = st.line_chart(pd.DataFrame({'Level %': [0]}))
    data_history = []

    # Embed WebSerial JS (NEW: Client-side hardware access)
    st.subheader("Connect Hardware")
    html("""
        <button onclick="connectToSerial()">Connect Arduino</button>
        <div id="output" style="color: white; background-color: #172a46; padding: 10px; height: 200px; overflow-y: scroll;"></div>
        <script>
        async function connectToSerial() {
            try {
                const port = await navigator.serial.requestPort();
                await port.open({ baudRate: """ + str(BAUD_RATE) + """ });
                appendOutput('Connected to Arduino!');
                const reader = port.readable.getReader();
                let receivedData = '';
                while (true) {
                    const { value, done } = await reader.read();
                    if (done) {
                        appendOutput('Connection closed.');
                        reader.releaseLock();
                        break;
                    }
                    receivedData += new TextDecoder().decode(value);
                    if (receivedData.includes('\\n')) {  // Assume lines end with \n
                        appendOutput(receivedData.trim());
                        // Parse for Streamlit (optional: alert or console for now)
                        console.log(receivedData.trim());  // For debugging
                        receivedData = '';
                    }
                }
            } catch (error) {
                appendOutput('Error: ' + error.message);
            }
        }
        function appendOutput(message) {
            const outputDiv = document.getElementById('output');
            outputDiv.innerHTML += '<p>' + message + '</p>';
            outputDiv.scrollTop = outputDiv.scrollHeight;
        }
        </script>
    """, height=300)

with tab3:
    st.header("Future: Predictions & Interventions")

# Impact Metrics
st.sidebar.header("Impact Metrics")
savings = 42
st.sidebar.metric("Projected Water Savings", f"{savings}%")
st.sidebar.write("Reduces wastage by blending AI with cultural methods.")

# ML Function (unchanged)
def predict_future(current_levels):
    X = pd.to_numeric(historical_data['Date'].dt.strftime('%s')).values.reshape(-1, 1)
    y = historical_data['Level']
    model = LinearRegression().fit(X, y)
    future_X = [[int(time.time()) + 86400]]
    pred = model.predict(future_X)[0]
    
    try:
        weather_url = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}"
        response = requests.get(weather_url).json()
        rain = response['rain']['1h'] if 'rain' in response else 0
        pred += rain * 2
        st.sidebar.metric("Today's Rain Forecast", f"{rain} mm")
    except:
        st.sidebar.error("Weather API error—using base prediction.")
    
    return pred

# Live Loop (simulation if no hardware; JS handles real)
while True:
    # For web demo, use simulation (JS output is separate)
    distance = random.uniform(5, 25)
    pump_status = "ON" if distance > 20 else "OFF"
    level_percent = max(0, (25 - distance) / 25 * 100)
    
    with tab2:
        level_placeholder.metric("Water Level", f"{level_percent:.1f}%", delta=level_percent - 50)
        pump_placeholder.metric("Motor Status", pump_status)
        
        data_history.append(level_percent)
        if len(data_history) > 20: data_history.pop(0)
        chart_placeholder.line_chart(pd.DataFrame({'Level %': data_history}))
    
    with tab3:
        future_level = predict_future(historical_data['Level'])
        st.metric("Predicted Tomorrow Level", f"{future_level:.1f}%")
        if future_level < 20:
            st.warning("Low prediction—Activate eri revival + auto-pump!")
    
    savings = max(0, (100 - future_level) * 0.42)
    st.sidebar.metric("Projected Water Savings", f"{savings:.1f}%")
    
    time.sleep(1)
