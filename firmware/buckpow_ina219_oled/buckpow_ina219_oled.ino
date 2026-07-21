/*
 * BuckPow INA219 + OLED - Power Monitor Firmware
 * Supports ESP32 and ESP8266 with INA219 sensor and SSD1306 128x32 OLED.
 *
 * Wiring (I2C shared bus):
 *   INA219 (addr 0x40)         SSD1306 OLED (addr 0x3C)
 *   VCC  → 3.3V               VCC → 3.3V
 *   GND  → GND                GND → GND
 *   SCL  → GPIO 22 / D1       SCL → GPIO 22 / D1
 *   SDA  → GPIO 21 / D2       SDA → GPIO 21 / D2
 *
 * OLED display (128x32):
 *   Line 0: Voltage (V)
 *   Line 1: Current (mA)
 *   Line 2: Power (mW)
 *   Line 3: Energy (Wh) + Uptime (HH:MM)
 *
 * Sends bus_voltage (V), shunt_voltage (mV),
 * current (mA), power (mW) to BuckPow API.
 *
 * Required libraries (install via Arduino Library Manager):
 *   - Adafruit INA219 by Adafruit
 *   - Adafruit SSD1306 by Adafruit
 *   - Adafruit GFX Library by Adafruit
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
  #include <WiFiClientSecure.h>
#elif defined(ESP8266)
  #include <ESP8266WiFi.h>
  #include <ESP8266HTTPClient.h>
  #include <WiFiClient.h>
  #include <WiFiClientSecure.h>
#endif

#include <Wire.h>
#include <Adafruit_INA219.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <ArduinoJson.h>

// ── Firmware Version ──
#define FW_VERSION "1.1.0"

// ── WiFi Configuration ──
const char* WIFI_SSID     = "your-ssid";
const char* WIFI_PASSWORD = "your-password";

// ── BuckPow API Configuration ──
const char* API_BASE   = "http://192.168.100.16:8000";
const char* API_PATH   = "/api/v1/measurements";
const char* NODE_ID  = "esp32-ina219-oled";
const char* API_KEY    = "";
const bool  USE_HTTPS  = false;  // set true for HTTPS

// ── Timing ──
const unsigned long INTERVAL_MS  = 5000;
const unsigned long WIFI_TIMEOUT = 30000;
const unsigned long RETRY_MS     = 10000;

// ── OLED Configuration ──
#define SCREEN_WIDTH  128
#define SCREEN_HEIGHT 32
#define OLED_RESET    -1
#define OLED_ADDR     0x3C

// ── Globals ──
Adafruit_INA219 ina219;
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

unsigned long lastSend    = 0;
unsigned long lastWifiTry = 0;
unsigned long lastApiFail = 0;

float energyWh       = 0.0;
unsigned long startTime = 0;

String maskKey(const char* key) {
  int len = strlen(key);
  if (len <= 8) return String(key);
  String out = String(key).substring(0, 4) + "****" + String(key).substring(len - 4);
  return out;
}

void updateDisplay(float voltage, float current, float power) {
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(0, 0);

  char buf[24];

  // Line 0: Voltage
  snprintf(buf, sizeof(buf), "V : %6.2f V", voltage);
  display.println(buf);

  // Line 1: Current
  snprintf(buf, sizeof(buf), "I : %6.1f mA", current);
  display.println(buf);

  // Line 2: Power (auto mW / W)
  if (power >= 1000.0) {
    snprintf(buf, sizeof(buf), "P : %6.2f W", power / 1000.0);
  } else {
    snprintf(buf, sizeof(buf), "P : %6.1f mW", power);
  }
  display.println(buf);

  // Line 3: Energy + Uptime (auto mWh / Wh)
  unsigned long elapsed = (millis() - startTime) / 1000;
  unsigned long hours   = elapsed / 3600;
  unsigned long minutes = (elapsed % 3600) / 60;

  if (energyWh >= 1.0) {
    snprintf(buf, sizeof(buf), "E : %6.2f Wh %02lu:%02lu", energyWh, hours, minutes);
  } else {
    snprintf(buf, sizeof(buf), "E : %6.1f mWh %02lu:%02lu", energyWh * 1000.0, hours, minutes);
  }
  display.println(buf);

  display.display();
}

bool connectWiFi() {
  if (WiFi.status() == WL_CONNECTED) return true;
  Serial.print("Connecting to WiFi");
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(0, 0);
  display.println("WiFi connecting...");
  display.display();

  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  unsigned long start = millis();
  while (WiFi.status() != WL_CONNECTED) {
    if (millis() - start > WIFI_TIMEOUT) {
      Serial.println(" timeout");
      display.clearDisplay();
      display.setTextSize(1);
      display.setTextColor(SSD1306_WHITE);
      display.setCursor(0, 0);
      display.println("WiFi timeout!");
      display.println("Running offline.");
      display.display();
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
  doc["device_id"]       = NODE_ID;
  doc["firmware_version"] = FW_VERSION;
  doc["bus_voltage"]     = busVoltage;
  doc["shunt_voltage"]   = shuntVoltage;
  doc["current"]         = current;
  doc["power"]           = power;

  // Build the full API endpoint URL
  String url = String(API_BASE) + API_PATH;

  // Serialize the JSON document into a String payload
  String payload;
  serializeJson(doc, payload);

  // Select client based on protocol
  HTTPClient http;

  if (USE_HTTPS) {
    WiFiClientSecure secureClient;
    secureClient.setInsecure();  // skip certificate verification
    if (!http.begin(secureClient, url)) {
      Serial.println("HTTP begin failed");
      lastApiFail = millis();
      return false;
    }
  } else {
    WiFiClient plainClient;
    if (!http.begin(plainClient, url)) {
      Serial.println("HTTP begin failed");
      lastApiFail = millis();
      return false;
    }
  }

  // Set request headers: JSON content type and optional Bearer token auth
  http.addHeader("Content-Type", "application/json");
  if (API_KEY[0] != '\0') {
    http.addHeader("Authorization", "Bearer " + String(API_KEY));
  }

  // Send the POST request with the serialized JSON payload
  int code = http.POST(payload);

  // Free HTTP resources immediately after request completes
  http.end();

  // 201 Created = success
  if (code == 201) {
    Serial.print("OK id=");
    Serial.println(NODE_ID);
    return true;
  }

  // Log non-201 responses (e.g. 400, 401, 500) or connection errors
  if (code > 0) {
    Serial.print("HTTP ");
    Serial.println(code);
  } else {
    Serial.println("API unreachable");
  }

  // Back off before retrying to avoid spamming a down server
  lastApiFail = millis();
  return false;
}

void setup() {
  Serial.begin(115200);
  Serial.println("\n\nBuckPow INA219 + OLED Firmware v" FW_VERSION);
  Serial.print("Host: ");
  Serial.println(API_BASE);
  Serial.print("Proto: ");
  Serial.println(USE_HTTPS ? "HTTPS" : "HTTP");
  Serial.print("Key:   ");
  Serial.println(maskKey(API_KEY));

  Wire.begin();

  // INA219
  if (!ina219.begin()) {
    Serial.println("ERROR: INA219 not found. Check wiring.");
    while (1) delay(100);
  }
  ina219.setCalibration_32V_2A();
  Serial.println("INA219 detected");

  // OLED
  if (!display.begin(SSD1306_SWITCHCAPVCC, OLED_ADDR)) {
    Serial.println("ERROR: SSD1306 OLED not found. Check wiring.");
    while (1) delay(100);
  }
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(0, 0);
  display.println("BuckPow v" FW_VERSION);
  display.println("INA219 + OLED");
  display.println("Initializing...");
  display.display();
  Serial.println("SSD1306 OLED detected");

  startTime = millis();
  connectWiFi();
}

void loop() {
  unsigned long now = millis();

  if (WiFi.status() != WL_CONNECTED && now - lastWifiTry >= WIFI_TIMEOUT) {
    lastWifiTry = now;
    connectWiFi();
  }
  if (WiFi.status() != WL_CONNECTED) {
    // Still update display with last readings while offline
    return;
  }

  if (now - lastSend < INTERVAL_MS) return;
  lastSend = now;

  float busV       = ina219.getBusVoltage_V();
  float shuntV     = ina219.getShuntVoltage_mV();
  float current_mA = ina219.getCurrent_mA();
  float power_mW   = ina219.getPower_mW();

  // Accumulate energy: Wh = mW * ms / 3600000000
  energyWh += power_mW * INTERVAL_MS / 3600000000.0;

  updateDisplay(busV, current_mA, power_mW);
  sendReading(busV, shuntV, current_mA, power_mW);
}
