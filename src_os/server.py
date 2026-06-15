import socket
import threading
import json
# Diubah: Import fungsi baru yang kawan anda buat
from database_handler import save_safety_data 

# Server Configuration
HOST = '0.0.0.0'  # Listens on all available network interfaces
PORT = 5000       # Port used for IoT data transmission

def handle_client(client_socket, client_address):
    """
    OS Concept: Multithreading (Concurrency)
    Each connected IoT device/sensor is handled in its own separate thread.
    """
    print(f"[NEW CONNECTION] Thread active for device at {client_address}")
    
    try:
        # Receive the JSON payload from the IoT device
        data = client_socket.recv(1024).decode('utf-8')
        if data:
            # Parse the incoming string into a JSON object
            payload = json.loads(data)
            print(f"[DATA RECEIVED] From {client_address}: {payload}")
            
            # Diubah: Menggunakan fungsi save_safety_data yang baru
            save_safety_data(payload)
            
            # Send acknowledgement back to the IoT device
            response = {"status": "SUCCESS", "message": "Safety telemetry logged safely."}
            client_socket.send(json.dumps(response).encode('utf-8'))
            
    except Exception as e:
        print(f"[ERROR] Failed to handle data from {client_address}: {e}")
    finally:
        client_socket.close()
        print(f"[DISCONNECTED] Connection with {client_address} closed.")

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    print(f"[SERVER STARTED] Listening for Environmental & Safety IoT data on port {PORT}...")

    while True:
        # Accept incoming connections from IoT microcontrollers
        client_socket, client_address = server.accept()
        
        # Create a new thread for the connection to prevent blocking other devices
        thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
        thread.start()
        print(f"[ACTIVE THREADS] Total active connections: {threading.active_count() - 1}")

if __name__ == "__main__":
    main()
