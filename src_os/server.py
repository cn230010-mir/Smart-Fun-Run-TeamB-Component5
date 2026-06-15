import socket
import threading
import json
from flask import Flask, render_template_string
from database_handler import save_safety_data, get_all_logs

# Initialize Flask app for the Website Dashboard
app = Flask(__name__)

HOST = '0.0.0.0'
PORT = 5000       # Port for IoT devices to send data

@app.route('/')
def dashboard():
    """ Renders the live web dashboard for the Fun Run organizers """
    logs = get_all_logs()
    
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Smart Fun Run - Safety Dashboard</title>
        <meta http-equiv="refresh" content="3">
        <style>
            body { font-family: Arial, sans-serif; margin: 30px; background-color: #f4f6f9; }
            h1 { color: #2c3e50; }
            .card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 20px; }
            table { width: 100%; border-collapse: collapse; margin-top: 10px; }
            th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
            th { background-color: #34495e; color: white; }
            .alert-true { background-color: #ffdddd; color: #d8000c; font-weight: bold; }
            .alert-false { background-color: #ddffdd; color: #4f8a10; }
        </style>
    </head>
    <body>
        <h1>🏃‍♂️ Smart Fun Run: Environmental & Safety Monitoring</h1>
        <div class="card">
            <h2>Live Safety Logs (Auto-refreshes)</h2>
            <table>
                <tr>
                    <th>Device ID</th>
                    <th>Runner ID</th>
                    <th>Temperature (°C)</th>
                    <th>Humidity (%)</th>
                    <th>SOS Emergency Status</th>
                </tr>
                {% for log in logs %}
                <tr class="alert-{{ log.emergency_sos | lower }}">
                    <td>{{ log.device_id }}</td>
                    <td>{{ log.runner_id }}</td>
                    <td>{{ log.telemetry.temperature_c }}</td>
                    <td>{{ log.telemetry.humidity_pct }}</td>
                    <td>{{ "🚨 CRITICAL SOS" if log.emergency_sos else "✅ SAFE" }}</td>
                </tr>
                {% endfor %}
            </table>
        </div>
    </body>
    </html>
    """
    return render_template_string(html_template, logs=reversed(logs))

def handle_iot_client(client_socket, client_address):
    try:
        data = client_socket.recv(1024).decode('utf-8')
        if data:
            payload = json.loads(data)
            print(f"[SOCKET] Data received from {client_address}")
            save_safety_data(payload)
            response = {"status": "SUCCESS"}
            client_socket.send(json.dumps(response).encode('utf-8'))
    except Exception as e:
        print(f"[SOCKET ERROR] {e}")
    finally:
        client_socket.close()

def run_socket_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    print(f"[BACKGROUND THREAD] Socket listener running on port {PORT}...")
    while True:
        client_socket, client_address = server.accept()
        threading.Thread(target=handle_iot_client, args=(client_socket, client_address)).start()

if __name__ == "__main__":
    # Start background network socket for IoT
    threading.Thread(target=run_socket_server, daemon=True).start()
    
    # Start Web Server Dashboard
    print("[MAIN THREAD] Launching Website on http://localhost:8080")
    app.run(host='0.0.0.0', port=8080, debug=False)
