import socket
import threading
import json
import time
from datetime import datetime
from flask import Flask, render_template_string, Response, request

app = Flask(__name__)
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
    q = SimpleQueue()
    EVENT_LISTENERS.append(q)
    def event_generator():
        try:
            while True: yield q.get()
        finally: EVENT_LISTENERS.remove(q)
    return Response(event_generator(), mimetype="text/event-stream")

def broadcast_to_admin(data):
    message = f"data: {json.dumps(data)}\n\n"
    for listener in EVENT_LISTENERS:
        try: listener.put(message)
        except: pass

@app.route('/')
def admin_dashboard():
    # Port 9090 digunakan khusus untuk diimbas oleh telefon pelari
    host_base = request.host.split(':')[0] + ":9090"
    runner_list = ["RUNNER_001", "RUNNER_034", "RUNNER_102", "RUNNER_555"]
    
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Urus Setia Command Center</title>
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
            <button onclick="document.getElementById('emergencyOverlay').style.display='none'" style="padding:10px 20px; margin-top:15px; cursor:pointer;">SAHKAN & TUTUP</button>
        </div></div>

        <h1>🛸 HQ Command Center: Papan Pemantauan Keselamatan</h1>
        <div class="grid">
            <div class="card">
                <h3>Cetak Kod QR Pelari</h3>
                {% for runner in runners %}
                <div class="qr-card">
                    <b>{{ runner }}</b><br>
                    <img src="https://chart.googleapis.com/chart?chs=130x130&cht=qr&chl=http://{{ host }}/?runner_id={{ runner }}&choe=UTF-8">
                </div>
                {% endfor %}
            </div>
            <div class="card">
                <h3>Log Telementri Sensor & Amaran Real-Time</h3>
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
    threading.Thread(target=run_socket_server, daemon=True).start()
    app.run(host='0.0.0.0', port=8080, debug=False)
