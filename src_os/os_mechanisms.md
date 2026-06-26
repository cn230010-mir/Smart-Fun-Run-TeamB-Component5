# 🧠 Operating System (OS) Mechanisms Documentation
**Component 5: Environmental and Safety Monitoring (Group B-5)**

This document mapping technical implementation pathways across all files in the `src_os/` workspace directly to kernel-level resource handling concepts.



## 🧵 1. Process Management & Multi-threading (`server.py`)

The backend coordination unit (`server.py`) works closely with the Host OS scheduler to handle simultaneous network requests asynchronously.

### Code Mapping Details:
```python
# From src_os/server.py
while True:
    try:
        client_sock, addr = iot_server.accept()
        # Dynamic Multi-threaded Concurrency Processing
        worker = threading.Thread(target=process_iot_client, args=(client_sock, addr))
        worker.start()
    except:
        break

```

* **Dynamic Worker Allocation:** Instead of serializing incoming execution queues, `server.py` forces the parent process to spawn independent execution threads dynamically for every hardware client connection.
* **Daemon Subsystem Management:** The primary background network interface is bound explicitly as a **Daemon Thread** (`daemon=True`). This ties its resource lifetime directly to the Flask web instance, allowing the OS kernel to instantly sweep and reclaim open port bindings upon program termination.



## 🔒 2. Concurrency Synchronization & Shared Memory (`server.py`)

When multiple background execution workers try to modify volatile application states concurrently inside the system RAM, a mechanism is needed to resolve the **Critical Section Problem**.

### Code Mapping Details:

```python
# From src_os/server.py
with data_lock:
    if bib_id in REGISTERED_RUNNERS:
        packet["runner_name"] = REGISTERED_RUNNERS[bib_id]["name"]
        
with data_lock:
    LIVE_LOGS.append(packet)

```

* **Mutual Exclusion Enforcement:** The `data_lock = threading.Lock()` primitive provides strict serialization wrapper around the global tracking lists (`LIVE_LOGS` & `REGISTERED_RUNNERS`).
* **Prevention of Race Conditions:** Threads attempting to push tracking info must acquire the lock. If another thread holds the lock, the OS blocks the incoming thread until the current operation exits the critical section safely.



## 📥 3. Inter-Process Communication (IPC): Producer-Consumer Model (`server.py` & `admin.html`)

Data pipeline flow between backend computing loops and presentation layouts mirrors the classic OS **Bounded-Buffer Pattern**.

### Code Mapping Details:

```python
# From src_os/server.py
class ThreadSafeQueue:
    def put(self, item):
        with self.lock: self.items.append(item)
    def get(self):
        while True:
            with self.lock:
                if self.items: return self.items.pop(0)
            time.sleep(0.1) # Yields CPU execution slices back to OS scheduler

```

* **Shared Buffer Pipeline:** Telemetry packets captured via sockets act as *Producers*, pushing items into a centralized `ThreadSafeQueue`.
* **Asynchronous Consumption:** The presentation template (`admin.html`) acts as the *Consumer*. It links directly to the `/stream` endpoint via an EventSource gateway, fetching items sequentially from the queue to render safe or critical updates dynamically without blocking the main browser execution context.



## 🚨 4. Software Interrupts & Preemptive Notification (`server.py` & `sos.html`)

High-severity status anomalies within our event network require quick processing, bypassing standard sequential I/O lanes.

### Code Mapping Details:

```python
# From src_os/server.py
@app.route('/trigger_web_sos', methods=['POST'])
def trigger_web_sos():
    # ... forces high-priority injection ...
    sos_payload["emergency_sos"] = True
    broadcast_to_admin(sos_payload)

```

* **Virtual Traps Handling:** When an emergency alert originates from an active terminal, it interacts with the system like a **Software Interrupt (Trap)**.
* **Preemptive Interception:** The payload jumps ahead of passive background processing loops. Upon receiving this message packet, the web portal instantly preempts the standard layout view, calling up the emergency interface (`sos.html` window overlay) to notify event handlers immediately.



## 📂 5. File System & Persistent Data Management (`database_handler.py` & `safety_logs.json`)

To prevent data volatility from erasing system records, our infrastructure coordinates directly with the OS Storage Architecture subsystem.

### System Mapping Architecture:

```text
  ┌──────────────────────┐                   ┌──────────────────────┐
  │ Volatile System RAM      │  System Call      │ Non-Volatile Storage     │
  │   (LIVE_LOGS Array)      ├───────────────►│  (safety_logs.json)      │
  └──────────────────────┘  (Disk Write)     └──────────────────────┘

```

* **File Storage Operations:** The component uses `database_handler.py` to write volatile tracking histories down to solid-state disks into `safety_logs.json`.
* **Buffer Syncing & Block Commitment:** When writing records, the code invokes underlying kernel File System APIs (`open()`, `json.dump()`). The OS converts memory structures into raw byte vectors, locks the target file blocks to block simultaneous access corruptions, and ensures data is saved securely even during power failures.


## 📊 6. Core OS Integration Metrics

| Workspace Resource (`src_os/`) | Core Operating System Concept      | Technical Role in System Runtime                                  |
| `server.py`                    | Thread Scheduling & IPC Buffering  | Spawns parallel worker processes and manages the main Event Loop. |
| `database_handler.py`          | File System Abstract Layer (I/O)   | Coordinates disk transactions and ensures atomic file updates.    |
| `safety_logs.json`             | Persistent Storage Matrix          | Acts as the solid-state data sink for telemetry metrics.          |
| `admin.html` / `sos.html`      | Asynchronous Event Consuming       | Translates streamed socket information into user alert overlays.  |
