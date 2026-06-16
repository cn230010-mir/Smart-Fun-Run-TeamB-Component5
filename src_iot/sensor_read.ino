#include <WiFi.h>
#include <HTTPClient.h>
#include <DHT.h>

// Wi-Fi Credentials
const char* ssid = "JW";
const char* password = "stay0801";
const char* serverUrl = "http://172.20.10.4:5000/api/safety";

// Pin Configurations
#define DHTPIN 4
#define DHTTYPE DHT22
#define SOS_BUTTON_PIN 15

DHT dht(DHTPIN, DHTTYPE);

// Non-blocking Timer Variables
unsigned long lastDHTRead = 0;
const unsigned long dhtInterval = 5000; // Poll telemetry every 5 seconds

unsigned long lastWiFiCheck = 0;
const unsigned long wiFiCheckInterval = 10000; // Check Wi-Fi every 10 seconds

// Debouncing Variables for SOS Button
volatile bool sosTriggered = false;
unsigned long lastDebounceTime = 0;
const unsigned long debounceDelay = 250; // 250ms noise filter window

// Interrupt Service Routine (ISR) for instant SOS detection
void IRAM_ATTR handleSOSInterrupt() {
  unsigned long currentTime = millis();
  // Filter out rapid mechanical switch bounces
  if ((currentTime - lastDebounceTime) > debounceDelay) {
    sosTriggered = true;
    lastDebounceTime = currentTime;
  }
}

void setup() {
  Serial.begin(115200);
  dht.begin();
  
  pinMode(SOS_BUTTON_PIN, INPUT_PULLUP);
  // Attach interrupt to intercept edge signals instantly
  attachInterrupt(digitalPinToInterrupt(SOS_BUTTON_PIN), handleSOSInterrupt, FALLING);

  // Initial connection attempt
  WiFi.begin(ssid, password);
  Serial.print("Connecting to Wi-Fi");
}

void loop() {
  unsigned long currentMillis = millis();

  // 1. NON-BLOCKING WI-FI RECONNECTION LOGIC
  if (currentMillis - lastWiFiCheck >= wiFiCheckInterval) {
    lastWiFiCheck = currentMillis;
    if (WiFi.status() != WL_CONNECTED) {
      Serial.println("[Warning] Wi-Fi lost. Attempting background reconnect...");
      WiFi.disconnect();
      WiFi.begin(ssid, password); 
      // Loop keeps running! SOS button remains functional.
    }
  }

  // 2. IMMEDIATE SOS PAYLOAD TRANSMISSION
  if (sosTriggered) {
    sosTriggered = false; // Reset flag immediately
    Serial.println("[ALERT] SOS Button Pressed! Transmitting high-priority payload...");
    sendPayload(dht.readTemperature(), dht.readHumidity(), true);
  }

  // 3. PERIODIC ENVIRONMENTAL POLLING (Every 5 Seconds)
  if (currentMillis - lastDHTRead >= dhtInterval) {
    lastDHTRead = currentMillis;
    
    float temp = dht.readTemperature();
    float hum = dht.readHumidity();

    if (!isnan(temp) && !isnan(hum)) {
      Serial.println("[Data] Sending normal environmental telemetry.");
      sendPayload(temp, hum, false);
    } else {
      Serial.println("[Error] Failed to read from DHT22 sensor.");
    }
  }
}

// Function to handle clean HTTP JSON payloads
void sendPayload(float temp, float humidity, bool isEmergency) {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(serverUrl);
    http.addHeader("Content-Type", "application/json");

    // String construction matching the agreed JSON contract
    String jsonOutput = "{\"device_id\":\"ENV_SAFE_01\",\"runner_id\":\"RUNNER_034\",";
    jsonOutput += "\"telemetry\":{\"temperature_c\":" + String(temp, 1) + ",\"humidity_pct\":" + String(humidity, 1) + "},";
    jsonOutput += "\"emergency_sos\":" + String(isEmergency ? "true" : "false") + ",";
    jsonOutput += "\"timestamp\":" + String(millis() / 1000) + "}"; // Simulated runtime timestamp

    int httpResponseCode = http.POST(jsonOutput);
    
    if (httpResponseCode > 0) {
      Serial.printf("[HTTP] Success, Response Code: %d\n", httpResponseCode);
    } else {
      Serial.printf("[HTTP] Error sending payload, Code: %s\n", http.errorToString(httpResponseCode).c_str());
    }
    http.end();
  } else {
    Serial.println("[HTTP] Transmit failed: Wi-Fi network currently unavailable.");
  }
}