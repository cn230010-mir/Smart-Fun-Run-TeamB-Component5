import socket
import threading
import json
from database_handler import save_environmental_data

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
        data = client_socket.recv(1024).decode('utf-8')
        if data:
            payload = json.loads(data)
            print(f"[DATA RECEIVED] From {client_address}: {payload}")
            
            # Pass data to the database handler to be safely stored
            save_environmental_data(payload)
            
            response = {"status": "SUCCESS", "message": "Data logged safely."}
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
    print(f"[SERVER STARTED] Listening for Environmental & Safety IoT data on port 5000...")

    while True:
        client_socket, client_address = server.accept()
        thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
        thread.start()

if __name__ == "__main__":
    main()
