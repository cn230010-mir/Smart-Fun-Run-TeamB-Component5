# 🏃‍♂️ Smart Fun Run — Environmental & Safety Monitoring System
### 🌐 IoT x OS Joint Project | Team B

---

## 📝 1. Project Title & Component Name
* **Project Title:** Smart Fun Run - Environmental & Safety Monitoring System
* **Component Name:** Team B: Fixed Safety Checkpoint & Guardian Interrupt

---

## 👥 2. Team Members & Roles
This unified repository is maintained by the following 7 sub-group members across the **Internet of Things (IoT)** and **Operating System (OS)** tracks:

### 🔌 IoT Track (BNF44403)
| Name | Matric Number | Core Responsibilities |
| :--- | :--- | :--- |
| **TAN JING HAN** | AN230137 | **IoT Lead**: Edge firmware architecture, hardware integration, and ISR configuration. |
| **CHIN JING WEN** | AN230122 | **IoT Developer**: Sensor calibration (DHT22), circuit prototyping, and payload schema formulation. |
| **DEIVAMALAR** | AN230118 | **IoT Developer**: Hardware housing/ruggedization, power management, and hardware testing. |

### 💻 OS Track (BNF32303)
| Name | Matric Number | Core Responsibilities |
| :--- | :--- | :--- |
| **ALYA KHAIRINA NABIHAH BINTI AHMAD JAWAHER** | CN230123 | **OS Lead**: Multi-threaded Flask core, synchronization locks, and overall backend architecture. |
| **FARINA BINTI FATHOL JAWAD** | CN230165 | **OS Developer**: Concurrency engineering (Thread management for Runner SOS and Telemetry streams). |
| **ARMIRA AINI BINTI ASMI** | CN230010 | **OS Developer**: Thread-safe storage engine, file I/O operations, and log routing. |
| **NUR ASHIKIN BINTI MOHD RIZAL** | CN230378 | **OS Developer**: API Gateway routing, deployment configuration, and command center telemetry ingestion. |

---

## 🔍 3. Component Overview
The **"Survive The Run"** system is an active, real-time participant protection platform designed to bridge the gap between localized edge telemetry and centralized administrative oversight during high-stakes endurance runs. 


```

[ESP32 Edge Node]                       [Flask Backend Server]                 [HQ Command Center]
(DHT22 + SOS Button)  ───( Wi-Fi )───>  (Multi-threaded Ingestion)  ───(HTTP)───>   (Admin UI Dashboard)
└─> Mutex Lock ──> [safety_logs.json]

```

During the live run, stationary monitoring nodes (**"Guardian Interrupts"**) powered by ESP32 microcontrollers continuously capture ambient environmental data (temperature and humidity) via DHT22 sensors while supporting an instantaneous, hardware-interrupt-driven Emergency SOS button. 

This dual-stream data is packaged into standardized JSON payloads and transmitted via Wi-Fi to a multi-threaded Flask backend server. The server isolates telemetry streams and high-priority emergency alerts using thread synchronization (**Mutex locks**) to prevent file corruption, immediately broadcasting precise geolocation coordinates and environmental hazard alerts directly to the HQ Command Center UI to accelerate rescue response times.

---

## 🚀 4. Quick Start Guide
Follow these sequential steps to boot up and deploy the complete monitoring system:

### 🔌 Step 1: Hardware Setup & Power
1. Wire the physical components to your **ESP32 DevKit V1** according to the pinout guide provided in `docs/hardware_setup.pdf`:
   * **DHT22 Data Pin:** Connect to `GPIO 4`
   * **Tactile SOS Button:** Connect to `GPIO 15`
2. Ensure an active Wi-Fi Access Point with the SSID `JW` is live and within range.
3. Power the ESP32 board via USB. The firmware will execute its non-blocking boot cycle and automatically connect to the local gateway.

### 💻 Step 2: Initialize the Backend Server
1. Open a terminal on your host machine (ensure your local machine IP matches or is routed to the static target IP: `172.20.10.4`).
2. Navigate to the OS source directory:
   ```bash
   cd src_os

```

3. Run the multi-threaded Flask application core:
```bash
python server.py

```



> 💡 **System Note:** The server will spin up the isolated ingestion threads instantly and begin listening for client incoming packets on **Port 5000**.

### 📊 Step 3: Access the Interface & Ingestion

* **HQ Command Center Dashboard:** Open your browser and navigate to `http://172.20.10.4:5000/admin` to monitor incoming live feeds.
* **Mobile SOS Interface:** Access `http://172.20.10.4:5000/sos` on runner handsets to simulate live tracking and manual triggers.
* **Telemetry Verification:** Check `http://172.20.10.4:5000/api/safety/live` to verify thread-safe readings stream error-free into `safety_logs.json`.

---

## 📂 5. Standardized Repository Structure

To ensure easy code navigation and compliance with course rubrics, please ensure all file modifications adhere strictly to the following directory layout:

```text
Smart-Fun-Run-TeamB-Component4/
├── docs/                       # Technical documentation and schematics
│   ├── architecture.pdf        # System architecture & data flow diagrams
│   ├── hardware_setup.pdf      # Wiring diagrams, Fritzing sketches, and parts lists
│   └── os_mechanisms.md        # Detailed explanation of OS concepts applied (Mutex/Locks)
├── media/                      # Physical prototype verification
│   └── [photos/videos]         # High-quality photos and videos of lab demo testing
├── src_iot/                    # Source code for microcontrollers/edge devices
│   ├── sensor_read.ino         # ESP32 FreeRTOS/ISR firmware source code
│   └── payload_format.json     # Pre-defined JSON payload standard sent to backend
├── src_os/                     # Source code for the backend server
│   ├── safety_logs.json        # Thread-safe persistent file database
│   └── server.py               # Multi-threaded Flask application core logic
└── README.md                   # This project master landing page

```

---

## 📜 6. Core OS & IoT Engineering Implementations

* **Concurrency Handling:** The Flask backend natively orchestrates a pool of worker threads, capable of digesting incoming data frames from dozens of runner checkpoints concurrently without blocking.
* **Resource Synchronization:** Implements a robust mutual exclusion (`threading.Lock()`) boundary protecting `safety_logs.json`. This completely mitigates data race conditions when high-frequency telemetry logs and urgent SOS alerts target the file system at the exact same millisecond.
* **Hardware Interrupt Execution:** The edge firmware leverages ESP32 hardware timers to hook a dedicated ISR (`IRAM_ATTR`) to `GPIO 15`. This forces immediate alert dispatching on a falling edge signal, bypassing any processing delays in the main loop.

```

```
