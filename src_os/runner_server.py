import socket
import json
from datetime import datetime
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

@app.route('/trigger_sos', methods=['POST'])
def trigger_sos():
    data = request.json
    runner_id = data.get('runner_id')
    
    emergency_payload = {
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "device_id": "MOBILE_WEB_PORTAL",
        "runner_id": runner_id,
        "telemetry": {"temperature_c": 38.5, "humidity_pct": 80.0},
        "emergency_sos": True
    }
    
    # Menghantar maklumat SOS terus ke Socket Server Admin (Port 5000)
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(('127.0.0.1', 5000))
        s.send(json.dumps(emergency_payload).encode('utf-8'))
        s.close()
    except: pass
    
    return jsonify({"status": "SUCCESS"})

@app.route('/')
def runner_profile():
    target_runner = request.args.get('runner_id')
    if not target_runner:
        return '<body style="font-family:Arial;text-align:center;margin-top:50px;"><h2>🏃‍♂️ Portal Keselamatan Larian</h2><p>Akses disekat. Sila imbas kod QR rasmi pada bib anda.</p></body>'

    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Runner Safety Portal</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body { font-family: Arial, sans-serif; margin: 0; padding: 15px; background-color: #f4f6f9; text-align: center; }
            .profile-container { max-width: 400px; margin: 30px auto; background: white; padding: 25px; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
            .sos-button { background-color: #e74c3c; color: white; border: none; width: 100%; padding: 20px; font-size: 18px; font-weight: bold; border-radius: 12px; cursor: pointer; }
            .sos-button:active { transform: scale(0.98); background-color: #c0392b; }
        </style>
        <script>
            function sendSos() {
                if(confirm("🚨 Amaran: Hantar isyarat kecemasan kepada Urus Setia?")) {
                    fetch('/trigger_sos', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({ runner_id: "{{ runner_id }}" })
                    }).then(() => alert("✅ Isyarat SOS Berjaya Dihantar!"));
                }
            }
        </script>
    </head>
    <body>
        <div class="profile-container">
            <h2>🏃‍♂️ Profil Pemantauan Aktif</h2>
            <p style="font-size:18px; color:#7f8c8d;"><b>ID Pelari:</b> {{ runner_id }}</p>
            <br>
            <button class="sos-button" onclick="sendSos()">🚨 BUTTON SOS KECEMASAN</button>
        </div>
    </body>
    </html>
    """
    return render_template_string(html_template, runner_id=target_runner)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=9090, debug=False)
