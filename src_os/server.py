import socket
import threading
import json
import time
from datetime import datetime
from flask import Flask, render_template_string, Response, request, jsonify

app = Flask(__name__)

# Memori perkongsian log global (Thread-safe queue)
LIVE_LOGS = []
EVENT_LISTENERS = []

class SimpleQueue:
    def __init__(self):
        self.items = []
        self.lock = threading.Lock()
    def put(self, item):
        with self.lock: self.items.append(item)
    def get(self):
        while True:
            with self.lock:
                if self.items: return self.items.pop(0)
            time.sleep(0.1)

@app.route('/stream')
def stream():
    """ Laluan Server-Sent Events (SSE) untuk kemas kini skrin admin secara real-time """
    q = SimpleQueue()
    EVENT_LISTENERS.append(q)
    def event_generator():
        try:
            while True: yield q.get()
        finally: EVENT_LISTENERS.remove(q)
    return Response(event_generator(), mimetype="text/event-stream")

def broadcast_to_admin(data):
    """ Menghantar data telemeteri secara terus ke paparan pelayar web admin """
    message = f"data: {json.dumps(data)}\n\n"
    for listener in EVENT_LISTENERS:
        try: listener.put(message)
        except: pass

# =====================================================================
# 1. HALAMAN UNTUK ADMIN/URUS SETIA (http://localhost:8080/admin)
# =====================================================================
@app.route('/admin')
def admin_dashboard():
    host_base = request.host
    runner_list = ["RUNNER_001", "RUNNER_034", "RUNNER_102", "RUNNER_555"]
    
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>HQ Command Center - Admin Only</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 30px; background-color: #0f172a; color: #f8fafc; }
            h1 { color: #38bdf8; }
            .grid { display: grid; grid-template-columns: 1fr 2fr; gap: 20px; margin-top: 20px; }
            .card { background: #1e293b; padding: 20px; border-radius: 12px; }
            .qr-card { background: white; color: black; padding: 10px; margin: 10px 0; border-radius: 8px; text-align: center; }
            table { width: 100%; border-collapse: collapse; margin-top: 15px; background: #0f172a; }
            th, td { padding: 12px; text-align: left; border-bottom: 1px solid #1e293b; }
            th { background-color: #334155; color: #38bdf8; }
            .status-tag { padding: 4px 8px; border-radius: 4px; font-weight: bold; }
            .tag-safe { background: #16a34a; color: white; }
            .tag-sos { background: #dc2626; color: white; animation: blink 1s infinite; }
            @keyframes blink { 50% { opacity: 0.4; } }
            #emergencyOverlay { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(220, 38, 38, 0.95); z-index: 9999; justify-content: center; align-items: center; flex-direction: column; }
            .alert-box { background: white; color: black; padding: 40px; border-radius: 20px; text-align: center; }
        </style>
    </head>
    <body>
        <div id="emergencyOverlay"><div class="alert-box">
            <h2 style="color:#dc2626; font-size:36px;">🚨 SOS KECEMASAN DIKESAN 🚨</h2>
            <p id="alertMessage" style="font-size:20px; font-weight:bold;"></p>
            <button onclick="document.getElementById('emergencyOverlay').style.display='none'" style="padding:10px 20px; margin-top:15px; cursor:pointer;">SAHKAN AMARAN</button>
        </div></div>

        <h1>🛸 HQ Command Center: Panel Urus Setia</h1>
        <div class="grid">
            <div class="card">
                <h3>Cetak QR Kod Pelari</h3>
                {% for runner in runners %}
                <div class="qr-card">
                    <b>{{ runner }}</b><br>
                    <img src="https://chart.googleapis.com/chart?chs=130x130&cht=qr&chl=http://{{ host }}/?runner_id={{ runner }}&choe=UTF-8"><br>
                    <a href="http://{{ host }}/?runner_id={{ runner }}" target="_blank" style="font-size:11px; color:#0284c7; text-decoration:none; font-weight:bold;">Buka Profil Pelari 🔗</a>
                </div>
                {% endfor %}
            </div>
            <div class="card">
                <h3>Log Isyarat Kecemasan Semasa (Auto-Refreshes)</h3>
                <table>
                    <thead><tr><th>Masa</th><th>ID Pelari</th><th>Suhu (°C)</th><th>Kelembapan (%)</th><th>Status</th></tr></thead>
                    <tbody id="logTableBody"><tr><td colspan="5" style="text-align:center; color:#64748b;">Menunggu isyarat rangkaian...</td></tr></tbody>
                </table>
            </div>
        </div>
        <script>
            const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            function bleep() {
                let osc = audioCtx.createOscillator(); let gain = audioCtx.createGain();
                osc.type = 'sawtooth'; osc.frequency.setValueAtTime(880, audioCtx.currentTime);
                osc.connect(gain); gain.connect(audioCtx.destination); osc.start(); osc.stop(audioCtx.currentTime + 0.4);
            }
            const eventSource = new EventSource('/stream');
            eventSource.onmessage = function(event) {
                const log = JSON.parse(event.data);
                const tbody = document.getElementById('logTableBody');
                if (tbody.rows.length == 1 && tbody.rows[0].cells.length == 1) tbody.innerHTML = '';
                const row = tbody.insertRow(0);
                row.innerHTML = `<td>${log.timestamp}</td><td><b style="color:#38bdf8;">${log.runner_id}</b></td><td>${log.telemetry.temperature_c} °C</td><td>${log.telemetry.humidity_pct} %</td><td><span class="status-tag ${log.emergency_sos ? 'tag-sos' : 'tag-safe'}">${log.emergency_sos ? '🚨 CRITICAL SOS' : '✅ SAFE'}</span></td>`;
                
                if (log.emergency_sos === true) {
                    document.getElementById('alertMessage').innerText = `PELARI ${log.runner_id} MEMERLUKAN BANTUAN SEGERA!`;
                    document.getElementById('emergencyOverlay').style.display = 'flex';
                    bleep();
                }
            };
        </script>
    </body>
    </html>
    """
    return render_template_string(html_template, runners=runner_list, host=host_base)

# =====================================================================
# 2. HALAMAN UNTUK USER/PELARI (http://localhost:8080/?runner_id=...)
# =====================================================================
@app.route('/')
def runner_profile():
    target_runner = request.args.get('runner_id')
    if not target_runner:
        return '<body style="font-family:Arial;text-align:center;margin-top:50px;"><h2>🏃‍♂️ Smart Fun Run Portal</h2><p>Sila scan QR Code rasmi pada bib anda untuk melihat profile.</p></body>'

    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>My Safety Badge</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body { font-family: Arial, sans-serif; margin: 0; padding: 15px; background-color: #f4f6f9; text-align: center; }
            .profile-container { max-width: 400px; margin: 20px auto; background: white; padding: 25px; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
            h1 { color: #2c3e50; font-size: 22px; }
            .sos-button { background-color: #e74c3c; color: white; border: none; width: 100%; padding: 22px; font-size: 18px; font-weight: bold; border-radius: 12px; cursor: pointer; box-shadow: 0 5px 10px rgba(231, 76, 60, 0.4); }
            .sos-button:active { transform: scale(0.97); }
        </style>
        <script>
            function sendSos() {
                if(confirm("🚨 Kirim amaran kecemasan sekarang kepada Urus Setia HQ?")) {
                    fetch('/trigger_web_sos', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({ runner_id: "{{ runner_id }}" })
                    }).then(() => alert("✅ Isyarat dihantar! Bantuan perubatan sedang menuju ke lokasi anda."));
                }
            }
        </script>
    </head>
    <body>
        <div class="profile-container">
            <h1>🏃‍♂️ My Active Safety Portal</h1>
            <p style="font-size:18px; color:#7f8c8d; font-weight:bold;">ID Pelari: {{ runner_id }}</p>
            <br>
            <button class="sos-button" onclick="sendSos()">🚨 TEKAN JIKA KECEMASAN (SOS)</button>
        </div>
    </body>
    </html>
    """
    return render_template_string(html_template, runner_id=target_runner)

@app.route('/trigger_web_sos', methods=['POST'])
def trigger_web_sos():
    data = request.json
    runner_id = data.get('runner_id')
    
    emergency_payload = {
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "device_id": "RUNNER_MOBILE_WEB",
        "runner_id": runner_id,
        "telemetry": {"temperature_c": 38.5, "humidity_pct": 79.0},
        "emergency_sos": True
    }
    
    # Hantar isyarat melalui dalaman (internal socket loopback) ke Port 5000
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(('127.0.0.1', 5000))
        s.send(json.dumps(emergency_payload).encode('utf-8'))
        s.close()
    except: pass
    
    return jsonify({"status": "SUCCESS"})

# =====================================================================
# 3. BACKGROUND SOCKET SERVER (Port 5000 - Untuk ESP32 & Web SOS)
# =====================================================================
def handle_iot_client(client_socket, client_address):
    try:
        data = client_socket.recv(1024).decode('utf-8')
        if data:
            payload = json.loads(data)
            payload["timestamp"] = datetime.now().strftime("%H:%M:%S")
            LIVE_LOGS.append(payload)
            broadcast_to_admin(payload)
    except: pass
    finally: client_socket.close()

def run_socket_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', 5000))
    server.listen()
    while True:
        client_socket, client_address = server.accept()
        threading.Thread(target=handle_iot_client, args=(client_socket, client_address)).start()

if __name__ == "__main__":
    # Jalankan socket listener (Port 5000) di latar belakang (Background Thread)
    threading.Thread(target=run_socket_server, daemon=True).start()
    
    # Jalankan Flask Web Server utama pada Port 8080
    print("[SERVER STARTED] Listening for Environmental & Safety IoT data on port 5000.")
    app.run(host='0.0.0.0', port=8080, debug=False)
