import streamlit as st
import requests
import time
import pandas as pd
# IMPORTANT: Run 'pip install streamlit-js-eval' in your command prompt
from streamlit_js_eval import get_geolocation

# Setup a clean mobile interface
st.set_page_config(page_title="Survive The Run", layout="centered")

st.title("🏃‍♂️Survive The Run")
st.write("Live updates from the course to help you pace yourself and stay hydrated")

# Your active Flask server laptop IP address
SERVER_API_URL = "http://172.20.10.4:5000/api/safety"
LIVE_API_URL = "http://172.20.10.4:5000/api/safety/live"

# Initialize local session state variables to hold status across web reruns
if "sos_triggered" not in st.session_state:
    st.session_state.sos_triggered = False

st.markdown("---")

# ==========================================
# PART 1: VIEW TEMPERATURE & HUMIDITY SYSTEM
# ==========================================
st.subheader("📊The Sweat & Sun Index")

current_temp = 31.5  # Fallback defaults
current_hum = 65.2

try:
    # Attempt to fetch live track data
    response = requests.get(LIVE_API_URL, timeout=3)
    if response.status_code == 200:
        logs = response.json()
        if logs:
            latest_record = logs[-1]
            telemetry = latest_record.get("telemetry", {})
            current_temp = telemetry.get('temperature_c', current_temp)
            current_hum = telemetry.get('humidity_pct', current_hum)
except Exception as e:
    st.warning("⚠️ Could not sync with Track Weather Station. Using fallback data.")

# Display Metrics
col1, col2 = st.columns(2)
col1.metric("Temperature", f"{current_temp} °C")
col2.metric("Humidity", f"{current_hum} %")

# ==========================================
# NEW: HYDRATION POP-UP NOTIFICATION
# ==========================================
# Set your danger levels here
TEMP_DANGER_LEVEL = 32.0
HUMIDITY_DANGER_LEVEL = 100.0

if current_temp >= TEMP_DANGER_LEVEL or current_hum >= HUMIDITY_DANGER_LEVEL:
    # st.toast creates the sliding pop-up notification
    st.toast("⚠️DRINK WATER and stay hydrated!", icon="💧")
    
    # We also add a permanent red box on the screen just in case they miss the pop-up
    st.error("🌡️High Humidity/Temperature Detected! Please DRINK WATER!")

# ==========================================
# PART 2: EMERGENCY SOS TOGGLE SYSTEM
# ==========================================
st.markdown("---")
st.subheader("🚨 Emergency Assistance")

st.write("Please ensure your phone's GPS/Location Services are turned ON.")

# --- LIVE MOBILE GEOLOCATION FETCH ---
# This continuously tracks the runner's phone GPS coordinates over the hotspot network
location = get_geolocation()

# Use Kolej Kediaman Pagoh coordinates strictly as a fallback safety net if GPS fails to fetch
runner_lat = 2.1501
runner_lon = 102.7297

if location and location.get('coords'):
    runner_lat = location['coords']['latitude']
    runner_lon = location['coords']['longitude']
    st.caption(f"🎯 GPS Signal Locked (Accuracy: {round(location['coords']['accuracy'], 1)}m)")
else:
    st.caption("📡 Syncing with phone GPS hardware... Please allow location access if prompted.")

# If SOS is currently ACTIVE:
if st.session_state.sos_triggered:
    st.error("⚠️ SOS ALARM ACTIVE! Broadcasting live location to Admin HQ...")
    
    # Show the map pointing to where the phone physically is!
    map_data = pd.DataFrame({'lat': [runner_lat], 'lon': [runner_lon]})
    st.map(map_data, zoom=15)
    
    # The CANCEL Button
    if st.button("✅ (I AM SAFE)", use_container_width=True, type="primary"):
        safe_payload = {
            "device_id": "USER_MOBILE_WEB",
            "runner_id": "RUNNER_JW",
            "telemetry": {
                "temperature_c": current_temp,
                "humidity_pct": current_hum,
                "latitude": runner_lat,
                "longitude": runner_lon
            },
            "emergency_sos": False,
            "timestamp": int(time.time())
        }
        
        try:
            requests.post(SERVER_API_URL, json=safe_payload, timeout=3)
            st.session_state.sos_triggered = False
            st.rerun()
        except Exception as e:
            st.error("Failed to connect to Admin Server to cancel.")

# If SOS is currently OFF (Safe State):
else:
    st.success("🟢 Status: Safe. Environmental monitoring active.")
    
    # The TRIGGER Button
    if st.button("🔥 SOS!!", use_container_width=True, type="primary"):
        # Build the high-priority payload with real-time dynamic GPS data
        sos_payload = {
            "device_id": "USER_MOBILE_WEB",
            "runner_id": "RUNNER_JW",
            "telemetry": {
                "temperature_c": current_temp,
                "humidity_pct": current_hum,
                "latitude": runner_lat,   # Real phone Latitude
                "longitude": runner_lon   # Real phone Longitude
            },
            "emergency_sos": True,
            "timestamp": int(time.time())
        }
        
        try:
            requests.post(SERVER_API_URL, json=sos_payload, timeout=3)
            st.session_state.sos_triggered = True
            st.rerun()
        except Exception as e:
            st.error("Failed to connect to Admin Server to send SOS.")
