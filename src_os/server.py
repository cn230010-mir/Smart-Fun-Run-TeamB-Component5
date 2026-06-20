from flask import Flask, request, jsonify, render_template  # <-- ADDED render_template HERE
import threading
import database_handler  # Imports YOUR database_handler.py file seamlessly!

app = Flask(__name__)

# OS Mechanism: Track active threads for monitoring/Expo justification purposes
active_connections_counter = 0
counter_lock = threading.Lock()

# ==================================================
# MOBILE: Serves the Mobile SOS UI to the Phone
# ==================================================
@app.route('/sos', methods=['GET'])
def serve_sos_page():
    return render_template('sos.html')

# ==================================================
# NEW COMMAND CENTER: Serves the Admin Dashboard
# ==================================================
@app.route('/admin', methods=['GET'])
def serve_admin_page():
    """
    Opens the HQ Command Center in the browser.
    """
    return render_template('admin.html')

# ==================================================
# API ROUTES (Handles the IoT Data and Map Data)
# ==================================================
@app.route('/api/safety', methods=['POST'])
def handle_safety_payload():
    """
    This route intercepts incoming JSON payloads from the Phone/ESP32.
    """
    global active_connections_counter
    
    # OS Concept: Simulate spawning/tracking a unique concurrent task process
    with counter_lock:
        active_connections_counter += 1
        current_thread_id = threading.get_ident()
        print(f"\n[SERVER] New Client Request incoming! Assigned to OS Thread ID: {current_thread_id}")
        print(f"[SERVER] Concurrent connections handled by system: {active_connections_counter}")

    try:
        # Extract the raw JSON structure sent by the device
        payload = request.get_json()
        
        if not payload:
            return jsonify({"status": "error", "message": "Malformed or empty JSON data"}), 400

        # CRITICAL COUPLING: Safely pass the data into YOUR database thread-safe file
        database_handler.save_safety_data(payload)

        # OS Feature: Prioritized background log notifications
        if payload.get("emergency_sos") is True:
            telemetry = payload.get("telemetry", {})
            lat = telemetry.get("latitude", "UNKNOWN")
            lon = telemetry.get("longitude", "UNKNOWN")
            acc = telemetry.get("accuracy_meters", "UNKNOWN")
            
            print(f"\n!!! [CRITICAL INTERRUPT] EMERGENCY SOS RECEIVED !!!")
            print(f" -> RUNNER ID : {payload.get('runner_id')}")
            print(f" -> LOCATION  : Latitude: {lat}, Longitude: {lon}")
            print(f" -> ACCURACY  : Within {acc} meters")
            print(f"==================================================\n")

        # Reduce the active connection count once processing finishes
        with counter_lock:
            active_connections_counter -= 1
            
        return jsonify({"status": "success", "message": "Telemetry logged safely"}), 200

    except Exception as e:
        print(f"[SERVER ERROR] Exception thrown during execution: {str(e)}")
        with counter_lock:
            active_connections_counter -= 1
        return jsonify({"status": "internal_error", "message": str(e)}), 500


@app.route('/api/safety/live', methods=['GET'])
def expose_live_dashboard_feed():
    """
    API Integration Window for Component 5 (Central Dashboard).
    When they run a request here, it pulls data directly via your data locks.
    """
    logs = database_handler.get_all_logs()
    return jsonify(logs), 200


# ==================================================
# SERVER STARTUP
# ==================================================
if __name__ == "__main__":
    print("==================================================")
    print("      SMART FUN RUN MULTITHREADED OS SERVER       ")
    print("==================================================")
    print("[OS SETUP] Exposing server across all local interfaces...")
    print("[OS SETUP] Listening on Port: 5000")
    print("[OS SETUP] Target Endpoint URL: http://localhost:5000/api/safety")
    print("==================================================")
    
    # 'threaded=True' commands the OS to automatically spin up individual processing
    # threads for parallel execution, ensuring requests don't queue or bottleneck.
    # 'host="0.0.0.0"' opens the network gateway so external devices can connect.
    app.run(host="0.0.0.0", port=5000, threaded=True)
