Smart Fun Run - Environmental & Safety Monitoring System
IoT x OS Joint Project |
Team B
1. Project Title & Component Name
Project Title: Smart Fun Run - Environmental & Safety Monitoring System
Component Name: Team B: Fixed Safety Checkpoint & Guardian Interrupt

2. Team Members & Roles
This unified repository is maintained by the following 7 sub-group members across the IoT and Operating System tracks:
IoT Track (BNF44403)

TAN JING HAN (Matric No: AN230137) - IoT Lead: Edge firmware architecture, hardware integration, and ISR configuration.

CHIN JING WEN (Matric No: AN230122) - IoT Developer: Sensor calibration (DHT22), circuit prototyping, and payload schema formulation.

DEIVAMALAR (Matric No: AN230118) - IoT Developer: Hardware housing/ruggedization, power management, and hardware testing.
OS Track (BNF32303)

ALYA KHAIRINA NABIHAH BINTI AHMAD JAWAHER (Matric No: CN230123) - OS Lead: Multi-threaded Flask core, synchronization locks, and overall backend architecture.

FARINA BINTI FATHOL JAWAD (Matric No: CN230165) - OS Developer: Concurrency engineering (Thread management for Runner SOS and Telemetry streams).

ARMIRA AINI BINTI ASMI (Matric No: CN230010) - OS Developer: Thread-safe storage engine, file I/O operations, and log routing (safety_logs.json).

NUR ASHIKIN BINTI MOHD RIZAL (Matric No: CN230378) - OS Developer: API Gateway routing, deployment configuration, and command center telemetry ingestion.

3. Component Overview
The "Survive The Run" system is an active, real-time participant protection platform designed to bridge the gap between localized edge telemetry and centralized administrative oversight during high-stakes endurance runs. During the live run, stationary monitoring nodes ("Guardian Interrupts") powered by ESP32 microcontrollers continuously capture ambient environmental data (temperature and humidity) via DHT22 sensors while supporting an instantaneous, hardware-interrupt-driven Emergency SOS button.
This dual-stream data is packaged into standardized JSON payloads and transmitted via Wi-Fi to a multi-threaded Flask backend server. The server isolates telemetry streams and high-priority emergency alerts using thread synchronization (Mutex locks) to prevent file corruption, immediately broadcasting precise geolocation coordinates and environmental hazard alerts directly to the HQ Command Center UI to accelerate rescue response times.

4. Quick Start Guide
Follow these sequential steps to boot up and run the entire monitoring system:
Step 1: Hardware Setup & Power
Wire the physical components to your ESP32 DevKit V1 according to the predefined pin map provided in docs/hardware_setup.pdf (DHT22 Data to GPIO 4, Tactile Button to GPIO 15).
Ensure an active Wi-Fi Access Point with the SSID JW is available within range.
Power the ESP32 board via USB. The firmware will execute its non-blocking boot cycle and automatically connect to the local gateway.
Step 2: Initialize the Backend Server
Open a terminal on your host machine (ensure your local machine IP matches or is routed to the static target IP: 172.20.10.4).
Navigate to the OS source directory: cd src_os


Run the multi-threaded Flask application core: python server.py

The server will spin up the isolated ingestion threads and begin listening on Port 5000.
Step 3: Access the Interface & Ingestion
HQ Command Center Dashboard: Open your browser and navigate to http://172.20.10.4:5000/admin to monitor incoming live feeds.
Mobile SOS Interface: Access http://172.20.10.4:5000/sos on runner handsets to simulate live tracking and manual triggers.
Telemetry Verification: Check http://172.20.10.4:5000/api/safety/live to verify thread-safe readings stream error-free into safety_logs.json.

