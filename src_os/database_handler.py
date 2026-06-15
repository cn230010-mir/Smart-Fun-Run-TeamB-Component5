import json
import os
import threading

# OS Mechanism: Initialize a Mutex Lock to synchronize file access
file_lock = threading.Lock()

# Define where your JSON database file will be saved in the src_os directory
DB_FILE_PATH = os.path.join(os.path.dirname(__file__), "safety_logs.json")

def save_safety_data(payload):
    """
    Receives an incoming JSON payload from server.py, handles thread synchronization, 
    and writes the telemetry safely to a JSON file log.
    """
    # OS Mechanism: Acquire the Mutex lock before touching the file to prevent race conditions
    with file_lock:
        print(f"\n[DB_HANDLER] Thread locked. Safely processing payload...")
        
        existing_data = []
        
        # 1. Read existing data if the file exists and isn't empty
        if os.path.exists(DB_FILE_PATH) and os.path.getsize(DB_FILE_PATH) > 0:
            try:
                with open(DB_FILE_PATH, "r") as file:
                    existing_data = json.load(file)
            except json.JSONDecodeError:
                print("[DB_HANDLER] Warning: File was corrupted or empty. Resetting log array.")
                existing_data = []

        # 2. Append the new payload sent by the IoT team
        existing_data.append(payload)

        # 3. Write back the updated data cleanly
        with open(DB_FILE_PATH, "w") as file:
            json.dump(existing_data, file, indent=4)
            
        print(f"[DB_HANDLER] Data written successfully! Thread unlocked.")


def get_all_logs():
    """
    Reads and returns the complete safety log history securely.
    """
    with file_lock: # Protect the file from being read while another thread is writing to it
        if os.path.exists(DB_FILE_PATH) and os.path.getsize(DB_FILE_PATH) > 0:
            with open(DB_FILE_PATH, "r") as file:
                return json.load(file)
        return []


# ==========================================
# LOCAL TESTING BLOCK
# ==========================================
if __name__ == "__main__":
    import time
    print("=== Starting Independent Database Handler Test ===")

    # Mocking the exact JSON structure provided by your IoT Team's ESP32 code
    mock_payload_1 = {
        "device_id": "ENV_SAFE_01",
        "runner_id": "RUNNER_034",
        "telemetry": {"temperature_c": 31.5, "humidity_pct": 65.2},
        "emergency_sos": False,
        "timestamp": int(time.time())
    }

    mock_payload_2 = {
        "device_id": "ENV_SAFE_01",
        "runner_id": "RUNNER_034",
        "telemetry": {"temperature_c": 35.8, "humidity_pct": 70.1},
        "emergency_sos": True,  # High-priority alert simulation!
        "timestamp": int(time.time()) + 1
    }

    # Test saving data sequentially 
    print("\n--- Testing Input 1 (Normal Telemetry) ---")
    save_safety_data(mock_payload_1)
    
    print("\n--- Testing Input 2 (SOS Emergency Alert) ---")
    save_safety_data(mock_payload_2)

    # Test reading back data
    print("\n--- Testing Data Retrieval Verification ---")
    saved_records = get_all_logs()
    print(f"Total records found in database file: {len(saved_records)}")
    print(json.dumps(saved_records, indent=2))
