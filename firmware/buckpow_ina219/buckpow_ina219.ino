/*
 * BuckPow INA219 - Power Monitor Firmware
 * Supports ESP32 and ESP8266 with INA219 sensor.
 *
 * Wiring (INA219 → ESP32/ESP8266):
 *   VCC  → 3.3V
 *   GND  → GND
 *   SCL  → GPIO 22 (ESP32) / D1 (ESP8266, GPIO 5)
 *   SDA  → GPIO 21 (ESP32) / D2 (ESP8266, GPIO 4)
 *
 * Sends bus_voltage (V), shunt_voltage (mV),
 * current (mA), power (mW) to BuckPow API.
 *
 * Required libraries (install via Arduino Library Manager):
 *   - Adafruit INA219 by Adafruit
 *   - ArduinoJson by Benoit Blanchon
 *
 * MIT License
 *
 * Copyright (c) 2026 Ari Effendi
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

#include <Arduino.h>

#if defined(ESP32)
  #include <WiFi.h>
  #include <HTTPClient.h>
#elif defined(ESP8266)
  #include <ESP8266WiFi.h>
  #include <ESP8266HTTPClient.h>
  #include <WiFiClient.h>
#endif

#include <Adafruit_INA219.h>
#include <ArduinoJson.h>

// ── Firmware Version ──
#define FW_VERSION "1.0.0"

// ── WiFi Configuration ──
const char* WIFI_SSID     = "your-ssid";
const char* WIFI_PASSWORD = "your-password";

// ── BuckPow API Configuration ──
const char* API_BASE   = "http://192.168.100.16:8000";
const char* API_PATH   = "/api/v1/measurements";
const char* DEVICE_ID  = "esp32-ina219-01";
const char* API_KEY    = "";

// ── Timing ──
const unsigned long INTERVAL_MS  = 1000;
const unsigned long WIFI_TIMEOUT = 30000;
const unsigned long RETRY_MS     = 10000;

// ── Globals ──
Adafruit_INA219 ina219;
unsigned long lastSend    = 0;
unsigned long lastWifiTry = 0;
unsigned long lastApiFail = 0;

bool connectWiFi() {
  if (WiFi.status() == WL_CONNECTED) return true;
  Serial.print("Connecting to WiFi");
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  unsigned long start = millis();
  while (WiFi.status() != WL_CONNECTED) {
    if (millis() - start > WIFI_TIMEOUT) {
      Serial.println(" timeout");
      return false;
    }
    delay(500);
    Serial.print(".");
  }
  Serial.println(" connected");
  Serial.print("IP: ");
  Serial.println(WiFi.localIP().toString());
  return true;
}

bool sendReading(float busVoltage, float shuntVoltage, float current, float power) {
  if (WiFi.status() != WL_CONNECTED) return false;
  if (millis() - lastApiFail < RETRY_MS) return false;

  StaticJsonDocument<256> doc;
  doc["device_id"]       = DEVICE_ID;
  doc["firmware_version"] = FW_VERSION;
  doc["bus_voltage"]     = busVoltage;
  doc["shunt_voltage"]   = shuntVoltage;
  doc["current"]         = current;
  doc["power"]           = power;

  String url = String(API_BASE) + API_PATH;
  String payload;
  serializeJson(doc, payload);

  WiFiClient client;
  HTTPClient http;
  if (!http.begin(client, url)) {
    Serial.println("HTTP begin failed");
    lastApiFail = millis();
    return false;
  }
  http.addHeader("Content-Type", "application/json");
  if (API_KEY[0] != '\0') {
    http.addHeader("Authorization", "Bearer " + String(API_KEY));
  }
  int code = http.POST(payload);
  http.end();

  if (code == 201) {
    Serial.print("OK id=");
    Serial.println(DEVICE_ID);
    return true;
  }

  if (code > 0) {
    Serial.print("HTTP ");
    Serial.println(code);
  } else {
    Serial.println("API unreachable");
  }
  lastApiFail = millis();
  return false;
}

void setup() {
  Serial.begin(115200);
  Serial.println("\n\nBuckPow INA219 Firmware");

  Wire.begin();
  if (!ina219.begin()) {
    Serial.println("ERROR: INA219 not found. Check wiring.");
    while (1) delay(100);
  }
  ina219.setCalibration_32V_2A();
  Serial.println("INA219 detected");

  connectWiFi();
}

void loop() {
  unsigned long now = millis();

  if (WiFi.status() != WL_CONNECTED && now - lastWifiTry >= WIFI_TIMEOUT) {
    lastWifiTry = now;
    connectWiFi();
  }
  if (WiFi.status() != WL_CONNECTED) return;

  if (now - lastSend < INTERVAL_MS) return;
  lastSend = now;

  float busV       = ina219.getBusVoltage_V();
  float shuntV     = ina219.getShuntVoltage_mV();
  float current_mA = ina219.getCurrent_mA();
  float power_mW   = ina219.getPower_mW();

  sendReading(busV, shuntV, current_mA, power_mW);
}
