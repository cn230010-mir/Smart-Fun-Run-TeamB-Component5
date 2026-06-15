import threading
import json
import csv
from datetime import datetime

# OS Concept: Mutual Exclusion (Mutex Lock)
data_lock = threading.Lock()
LOG_FILE = "environmental_logs.csv"

def save_environmental_data(payload):
    """
    Safely appends safety and environmental sensor logs to a CSV file using Mutex.
    """
    # Acquire the lock before accessing the file (OS Synchronization)
    data_lock.acquire()
    
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sensor_id = payload.get("sensor_id", "UNKNOWN")
        temperature = payload.get("temperature", 0.0)
        air_quality = payload.get("air_quality", "NORMAL")
        emergency_status = payload.get("emergency_button", False)
        
        with open(LOG_FILE, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([timestamp, sensor_id, temperature, air_quality, emergency_status])
            
        print(f"[FILE SYSTEM] Successfully logged data for Sensor {sensor_id}.")
        
    except Exception as e:
        print(f"[CRITICAL ERROR] File write failed: {e}")
        
    finally:
        # ALWAYS release the lock so other waiting threads can write
        data_lock.release()
