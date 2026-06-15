import socket
import threading
import json
import time
from datetime import datetime
from flask import Flask, render_template_string, Response, request, jsonify

app = Flask(__name__)

# Memori perkongsian global (Thread-safe)
LIVE_LOGS = []
EVENT_LISTENERS = []
REGISTERED_RUNNERS = {}  # Menyimpan data pelari yang mendaftar sendiri via telefon

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
    # Menghasilkan QR Code am (Generic QR) untuk diletakkan di kaunter pendaftaran
    host_base = request.host
    generic_qr_url = f"http://{host_base}/"
    
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>HQ Command Center - Admin Panel</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 30px; background-color: #0f172a; color: #f8fafc; }
            h1 { color: #38bdf8; margin-bottom: 5px; }
            .grid { display: grid; grid-template-columns: 1fr 2fr; gap: 20px; margin-top: 20px; }
            .card { background: #1e293b; padding: 20px; border-radius: 12px; }
            .qr-zone { background: white; color: black; padding: 20px; border-radius: 8px; text-align: center; margin-top: 15px; }
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
            <p id="alertMessage" style="font-size:20px; font-weight:bold; color: black;"></p>
            <div style="font-size:14px; color:#64748b; margin-bottom:15px;">Sila hubungi pasukan perubatan zon terdekat dengan segera.</div>
            <button onclick="document.getElementById('emergencyOverlay').style.display='none'" style="padding:10px 20px; cursor:pointer; font-weight:bold;">SAHKAN AMARAN</button>
        </div></div>

        <h1>🛸 HQ Command Center: Panel Urus Setia</h1>
        <p style="color:#94a3b8; margin:0;">Sistem Pengurusan Keselamatan Acara Larian Pintar</p>
        
        <div class="grid">
            <div class="card">
                <h3>QR Code Pendaftaran Pelari</h3>
                <p style="font-size:13px; color:#94a3b8;">Letakkan QR Code ini di papan tanda atau meja urus setia. Pelari perlu mengimbas QR ini untuk mendaftar profil peranti mereka sebelum larian bermula.</p>
                <div class="qr-zone">
                    <img src="https://chart.googleapis.com/chart?chs=200x200&cht=qr&chl={{ qr_link }}&choe=UTF-8"><br>
                    <a href="{{ qr_link }}" target="_blank" style="font-size:13px; color:#0284c7; text-decoration:none; font-weight:bold; display:block; margin-top:10px;">Simulasi Imbas Telefon Pelari 🔗</a>
                </div>
            </div>
            
            <div class="card">
                <h3>Log Isyarat Kecemasan Semasa (Auto-Refreshes)</h3>
                <table>
                    <thead><tr><th>Masa</th><th>ID Bib</th><th>Nama Pelari</th><th>Suhu (°C)</th><th>Status</th></tr></thead>
                    <tbody id="logTableBody"><tr><td colspan="5" style="text-align:center; color:#64748b;">Menunggu pendaftaran atau isyarat SOS pelari...</td></tr></tbody>
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
                row.innerHTML = `
                    <td>${log.timestamp}</td>
                    <td><b style="color:#38bdf8;">${log.runner_id}</b></td>
                    <td>${log.runner_name}</td>
                    <td>${log.telemetry.temperature_c} °C</td>
                    <td><span class="status-tag ${log.emergency_sos ? 'tag-sos' : 'tag-safe'}">${log.emergency_sos ? '🚨 CRITICAL SOS' : '✅ REGISTERED / SAFE'}</span></td>
                `;
                
                if (log.emergency_sos === true) {
                    document.getElementById('alertMessage').innerText = `PELARI: ${log.runner_name} (BIB: ${log.runner_id}) MEMERLUKAN BANTUAN!`;
                    document.getElementById('emergencyOverlay').style.display = 'flex';
                    bleep();
                }
            };
        </script>
    </body>
    </html>
    """
    return render_template_string(html_template, qr_link=generic_qr_url)

# =====================================================================
# 2. HALAMAN HALAMAN UNTUK USER (ALIRAN DAFTAR -> PORTAL SOS)
# =====================================================================
@app.route('/')
def runner_portal():
    # Semak jika peranti ini sudah mempunyai ID pendaftaran dalam sesi parameter
    runner_id = request.args.get('runner_id')
    
    # JIKALAU BELUM DAFTAR: Paparkan Halaman Borang Pendaftaran
    if not runner_id or runner_id not in REGISTERED_RUNNERS:
        html_register = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Pendaftaran Peranti Pelari</title>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f4f6f9; text-align: center; }
                .box { max-width: 400px; margin: 40px auto; background: white; padding: 30px; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
                h2 { color: #2c3e50; }
                input[type="text"] { width: 90%; padding: 12px; margin: 10px 0; border: 1px solid #ccc; border-radius: 8px; font-size: 15px; }
                button { background-color: #3498db; color: white; border: none; width: 96%; padding: 14px; font-size: 16px; font-weight: bold; border-radius: 8px; cursor: pointer; margin-top: 15px; }
                button:hover { background-color: #2980b9; }
            </style>
        </head>
        <body>
            <div class="box">
                <h2>🏃‍♂️ Daftar Peranti Keselamatan</h2>
                <p style="color:#7f8c8d; font-size:14px;">Sila masukkan maklumat anda sebelum memulakan larian acara Fun Run.</p>
                <form action="/register_process" method="POST">
                    <input type="text" name="runner_name" placeholder="Nama Penuh Anda" required>
                    <input type="text" name="runner_id" placeholder="Nombor Bib Larian (Contoh: BIB999)" required>
                    <button type="submit">DAFTAR PERANTI SAYA</button>
                </form>
            </div>
        </body>
        </html>
        """
        return render_template_string(html_register)
    
    # JIKALAU SUDAH BERJAYA DAFTAR: Paparkan Halaman Utama Portal SOS Keselamatan
    runner_info = REGISTERED_RUNNERS[runner_id]
    html_sos_dashboard = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>My Safety Badge</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body { font-family: Arial, sans-serif; margin: 0; padding: 15px; background-color: #f4f6f9; text-align: center; }
            .profile-container { max-width: 400px; margin: 20px auto; background: white; padding: 25px; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
            h1 { color: #2c3e50; font-size: 22px; margin-bottom: 5px; }
            .status-ok { color: #27ae60; font-weight: bold; background: #e8f8f0; display: inline-block; padding: 5px 15px; border-radius: 20px; font-size: 13px; }
            .sos-button { background-color: #e74c3c; color: white; border: none; width: 100%; padding: 25px; font-size: 20px; font-weight: bold; border-radius: 12px; cursor: pointer; box-shadow: 0 5px 10px rgba(231, 76, 60, 0.4); margin-top: 20px; }
            .sos-button:active { transform: scale(0.97); background-color: #c0392b; }
        </style>
        <script>
            function sendSos() {
                if(confirm("🚨 AMARAN: Adakah anda pasti mahu menghantar isyarat kecemasan ke HQ Urus Setia?")) {
                    fetch('/trigger_web_sos', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({ runner_id: "{{ runner_id }}", runner_name: "{{ runner_name }}" })
                    }).then(() => alert("✅ SOS Berjaya Dihantar! Pasukan perubatan kini sedang digerakkan ke lokasi anda."));
                }
            }
        </script>
    </head>
    <body>
        <div class="profile-container">
            <h1>🏃‍♂️ Portal Keselamatan Aktif</h1>
            <div class="status-ok">Sistem Memantau Aktiviti</div>
            
            <div style="text-align: left; background: #f8f9fa; padding: 15px; border-radius: 8px; margin-top: 15px;">
                <p style="margin: 5px 0;"><b>Nama Pelari:</b> {{ runner_name }}</p>
                <p style="margin: 5px 0;"><b>No. Bib:</b> {{ runner_id }}</p>
            </div>
            
            <button class="sos-button" onclick="sendSos()">🚨 TEKAN JIKA KECEMASAN (SOS)</button>
            <p style="font-size:11px; color:#95a5a6; margin-top:15px;">Isyarat kecemasan ini akan dikesan oleh sistem operasi HQ secara langsung.</p>
        </div>
    </body>
    </html>
    """
    return render_template_string(html_sos_dashboard, runner_id=runner_id, runner_name=runner_info['name'])

@app.route('/register_process', methods=['POST'])
def register_process():
    """ Memproses maklumat pendaftaran borang """
    runner_name = request.form.get('runner_name')
    runner_id = request.form.get('runner_id').strip().upper()
    
    # Daftarkan maklumat ke dalam kamus (Dictionary) server global
    REGISTERED_RUNNERS[runner_id] = {
        "name": runner_name,
        "registration_time": datetime.now().strftime("%H:%M:%S")
    }
    
    # Hantar maklumat log pendaftaran am awal ke pelayar urus setia admin (SOS = False)
    payload = {
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "device_id": "REGISTRATION_DESK",
        "runner_id": runner_id,
        "runner_name": runner_name,
        "telemetry": {"temperature_c": 36.5},  # Suhu normal semasa mendaftar
        "emergency_sos": False
    }
    
    # Hantar ke socket dalaman (Port 5000) supaya admin dapat melihat pendaftaran secara real-time
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(('127.0.0.1', 5000))
        s.send(json.dumps(payload).encode('utf-8'))
        s.close()
    except: pass

    # Selepas mendaftar, bawa pengguna terus ke portal SOS mereka menggunakan parameter ?runner_id=
    return f"<script>window.location.href='/?runner_id={runner_id}';</script>"

@app.route('/trigger_web_sos', methods=['POST'])
def trigger_web_sos():
    data = request.json
    runner_id = data.get('runner_id')
    runner_name = data.get('runner_name')
    
    emergency_payload = {
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "device_id": "RUNNER_MOBILE_WEB",
        "runner_id": runner_id,
        "runner_name": runner_name,
        "telemetry": {"temperature_c": 39.2},  # Simulasi suhu tinggi semasa kecemasan
        "emergency_sos": True
    }
    
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(('127.0.0.1', 5000))
        s.send(json.dumps(emergency_payload).encode('utf-8'))
        s.close()
    except: pass
    
    return jsonify({"status": "SUCCESS"})

# =====================================================================
# 3. BACKGROUND SOCKET SERVER (Port 5000 - Mendengar Isyarat ESP32 / Web)
# =====================================================================
def handle_iot_client(client_socket, client_address):
    try:
        data = client_socket.recv(1024).decode('utf-8')
        if data:
            payload = json.loads(data)
            payload["timestamp"] = datetime.now().strftime("%H:%M:%S")
            
            # Jika isyarat datang daripada ESP32 yang tiada "runner_name", carinya daripada memori pendaftaran
            if "runner_name" not in payload or not payload["runner_name"]:
                r_id = payload.get("runner_id", "").upper()
                if r_id in REGISTERED_RUNNERS:
                    payload["runner_name"] = REGISTERED_RUNNERS[r_id]["name"]
                else:
                    payload["runner_name"] = "Pelari Perkakasan (Bukan Web)"
            
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
    print("[SERVER STARTED] Listening on port 8080 (Flask) and port 5000 (Socket).")
    app.run(host='0.0.0.0', port=8080, debug=False)
