/*
 * BuckPow INA219 - Captive Portal Firmware
 * Supports ESP32 and ESP8266 with INA219 sensor.
 *
 * Custom captive portal for WiFi and node configuration.
 * No external WiFi manager library required.
 * EEPROM stores WiFi credentials and node config.
 *
 * Wiring (INA219 → ESP32/ESP8266):
 *   VCC  → 3.3V
 *   GND  → GND
 *   SCL  → GPIO 22 (ESP32) / D1 (ESP8266, GPIO 5)
 *   SDA  → GPIO 21 (ESP32) / D2 (ESP8266, GPIO 4)
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
  #include <WiFiClientSecure.h>
  #include <WebServer.h>
  #include <DNSServer.h>
#elif defined(ESP8266)
  #include <ESP8266WiFi.h>
  #include <ESP8266HTTPClient.h>
  #include <WiFiClient.h>
  #include <WiFiClientSecure.h>
  #include <ESP8266WebServer.h>
  #include <DNSServer.h>
#endif

#include <Adafruit_INA219.h>
#include <ArduinoJson.h>
#include <EEPROM.h>
#include "captive_portal.h"
#include "status_page.h"
#include "setup_page.h"

// ── Firmware Version ──
#define FW_VERSION "1.2.0"

// ── EEPROM Layout ──
#define EEPROM_SIZE 512
#define EEPROM_MAGIC 0x4250  // "BP"

// ── Timing ──
const unsigned long WIFI_TIMEOUT     = 30000;
const unsigned long RETRY_MS         = 10000;
const unsigned long STATUS_PAGE_MS   = 5000;

// ── Globals ──
Adafruit_INA219 ina219;
DNSServer dnsServer;
unsigned long lastSend    = 0;
unsigned long lastWifiTry = 0;
unsigned long lastApiFail = 0;
unsigned long lastUpload  = 0;
bool serverConnected      = false;
bool captivePortalActive  = false;
bool ipReported           = false;
float lastVoltage         = 0;
float lastCurrent         = 0;

// ── Config struct (saved to EEPROM) ──
struct Config {
  uint16_t magic;
  char wifiSsid[33];
  char wifiPassword[65];
  char nodeId[33];
  char location[65];
  char serverUrl[129];
  char apiKey[65];
  uint16_t sampleInterval;
};

Config config;

// ── Web server ──
#if defined(ESP32)
  WebServer statusServer(80);
#elif defined(ESP8266)
  ESP8266WebServer statusServer(80);
#endif

// ── Forward declarations ──
void loadConfig();
void saveConfig();
bool connectWiFi();
void startCaptivePortal();
void startStatusPage();
void handleStatusPage();
void handleStatusApi();
void handleConfigPage();
void handleWifiScan();
void handleSaveConfig();
String maskKey(const char* key);
String timeSince(unsigned long ms);

// ─────────────────────────────────────────────
//  EEPROM Config
// ─────────────────────────────────────────────

void loadConfig() {
  EEPROM.begin(EEPROM_SIZE);
  EEPROM.get(0, config);

  if (config.magic != EEPROM_MAGIC) {
    Serial.println("No saved config, using defaults");
    memset(&config, 0, sizeof(config));
    config.magic = EEPROM_MAGIC;
    strlcpy(config.wifiSsid, "", sizeof(config.wifiSsid));
    strlcpy(config.wifiPassword, "", sizeof(config.wifiPassword));
    strlcpy(config.nodeId, "esp32-ina219", sizeof(config.nodeId));
    strlcpy(config.location, "", sizeof(config.location));
    strlcpy(config.serverUrl, "http://192.168.1.10:8000", sizeof(config.serverUrl));
    strlcpy(config.apiKey, "", sizeof(config.apiKey));
    config.sampleInterval = 1000;
  } else {
    Serial.println("Config loaded from EEPROM");
  }
}

void saveConfig() {
  config.magic = EEPROM_MAGIC;
  EEPROM.put(0, config);
  EEPROM.commit();
  Serial.println("Config saved to EEPROM");
}

// ─────────────────────────────────────────────
//  WiFi Connection
// ─────────────────────────────────────────────

bool connectWiFi() {
  if (WiFi.status() == WL_CONNECTED) return true;
  if (strlen(config.wifiSsid) == 0) return false;

  Serial.print("Connecting to ");
  Serial.println(config.wifiSsid);

  WiFi.begin(config.wifiSsid, config.wifiPassword);

  unsigned long start = millis();
  while (WiFi.status() != WL_CONNECTED) {
    if (millis() - start > WIFI_TIMEOUT) {
      Serial.println(" timeout");
      return false;
    }
    delay(500);
    Serial.print(".");
  }

  Serial.println();
  Serial.print("Connected! IP: ");
  Serial.println(WiFi.localIP().toString());
  return true;
}

// ─────────────────────────────────────────────
//  Captive Portal
// ─────────────────────────────────────────────

void startCaptivePortal() {
  captivePortalActive = true;
  WiFi.mode(WIFI_AP_STA);

  String apName = "BuckPow-" + String(WiFi.macAddress().substring(12));
  apName.replace(":", "");

  WiFi.softAP(apName.c_str());
  delay(500);

  dnsServer.start(53, "*", WiFi.softAPIP());

  statusServer.on("/scan", handleWifiScan);
  statusServer.on("/save", handleSaveConfig);
  statusServer.onNotFound(handleConfigPage);
  statusServer.begin();

  Serial.println("Captive portal: http://" + WiFi.softAPIP().toString());
  Serial.println("AP: " + apName);
}

void handleConfigPage() {
  statusServer.send(200, "text/html", FPSTR(CAPTIVE_PAGE_TOP));
}

void handleWifiScan() {
  int n = WiFi.scanNetworks();
  String json = "[";
  for (int i = 0; i < n; i++) {
    if (i > 0) json += ",";
    json += "{\"ssid\":\"" + WiFi.SSID(i) + "\",\"rssi\":" + String(WiFi.RSSI(i));
#if defined(ESP32)
    json += ",\"enc\":" + String(WiFi.encryptionType(i) != WIFI_AUTH_OPEN ? 1 : 0) + "}";
#elif defined(ESP8266)
    json += ",\"enc\":" + String(WiFi.encryptionType(i) != ENC_TYPE_NONE ? 1 : 0) + "}";
#endif
  }
  json += "]";
  WiFi.scanDelete();
  statusServer.send(200, "application/json", json);
}

void handleSaveConfig() {
  strlcpy(config.wifiSsid, statusServer.arg("ssid").c_str(), sizeof(config.wifiSsid));
  strlcpy(config.wifiPassword, statusServer.arg("password").c_str(), sizeof(config.wifiPassword));
  strlcpy(config.nodeId, statusServer.arg("nodeId").c_str(), sizeof(config.nodeId));
  strlcpy(config.location, statusServer.arg("location").c_str(), sizeof(config.location));
  strlcpy(config.serverUrl, statusServer.arg("serverUrl").c_str(), sizeof(config.serverUrl));
  strlcpy(config.apiKey, statusServer.arg("apiKey").c_str(), sizeof(config.apiKey));

  int intervalMs = atoi(statusServer.arg("sampleInterval").c_str()) * 1000;
  config.sampleInterval = intervalMs;
  if (config.sampleInterval < 100) config.sampleInterval = 100;

  saveConfig();
  statusServer.send(200, "text/plain", "OK");
  delay(1000);
  ESP.restart();
}

// ─────────────────────────────────────────────
//  Status Page
// ─────────────────────────────────────────────

String timeSince(unsigned long ms) {
  if (ms == 0) return "never";
  unsigned long diff = (millis() - ms) / 1000;
  if (diff < 60) return String(diff) + "s ago";
  if (diff < 3600) return String(diff / 60) + "m ago";
  return String(diff / 3600) + "h ago";
}

String maskKey(const char* key) {
  int len = strlen(key);
  if (len <= 8) return String(key);
  return String(key).substring(0, 4) + "****" + String(key).substring(len - 4);
}

void handleStatusApi() {
  StaticJsonDocument<1024> doc;
  doc["node_id"]      = config.nodeId;
  doc["location"]      = config.location;
  doc["firmware"]      = FW_VERSION;
  doc["ip"]            = WiFi.localIP().toString();
  doc["wifi"]          = WiFi.status() == WL_CONNECTED ? "Connected" : "Disconnected";
  doc["rssi"]          = WiFi.RSSI();
  doc["server_url"]    = config.serverUrl;
  doc["server"]        = serverConnected ? "Connected" : "Disconnected";
  doc["sensor"]        = "INA219";
  doc["sample_interval"] = config.sampleInterval;
  doc["api_key_masked"]  = maskKey(config.apiKey);
  doc["last_upload"]   = timeSince(lastUpload);
  doc["uptime"]        = millis() / 1000;
  doc["voltage"]       = lastVoltage;
  doc["current"]       = lastCurrent;

  String payload;
  serializeJson(doc, payload);
  statusServer.send(200, "application/json", payload);
}

void handleStatusPage() {
  String html = FPSTR(STATUS_PAGE_HEAD);
  html += config.nodeId;
  html += FPSTR(STATUS_PAGE_BODY);
  html += FW_VERSION;
  html += FPSTR(STATUS_PAGE_SCRIPT);
  statusServer.send(200, "text/html", html);
}

void startStatusPage() {
  statusServer.on("/", handleStatusPage);
  statusServer.on("/api/status", handleStatusApi);
  statusServer.on("/setup", []() {
    statusServer.send(200, "text/html", FPSTR(SETUP_PAGE_HTML));
    delay(1000);
    memset(config.wifiSsid, 0, sizeof(config.wifiSsid));
    memset(config.wifiPassword, 0, sizeof(config.wifiPassword));
    saveConfig();
    WiFi.disconnect();
    delay(500);
    ESP.restart();
  });
  statusServer.begin();
  Serial.println("Status page: http://" + WiFi.localIP().toString());
}

// ─────────────────────────────────────────────
//  Send Data to BuckPow
// ─────────────────────────────────────────────

void sendLocalIp() {
  if (WiFi.status() != WL_CONNECTED || ipReported) return;

  StaticJsonDocument<96> doc;
  doc["local_ip"] = WiFi.localIP().toString();

  String url = String(config.serverUrl) + "/api/v1/devices/local-ip";
  String payload;
  serializeJson(doc, payload);

  HTTPClient http;
  if (url.startsWith("https")) {
    WiFiClientSecure secureClient;
    secureClient.setInsecure();
    if (!http.begin(secureClient, url)) return;
  } else {
    WiFiClient plainClient;
    if (!http.begin(plainClient, url)) return;
  }
  http.addHeader("Content-Type", "application/json");
  if (config.apiKey[0] != '\0') {
    http.addHeader("Authorization", "Bearer " + String(config.apiKey));
  }
  int code = http.sendRequest("PATCH", payload);
  http.end();

  if (code == 200) {
    Serial.print("Local IP reported: ");
    Serial.println(WiFi.localIP().toString());
    ipReported = true;
  }
}

bool sendReading(float busVoltage, float shuntVoltage, float current, float power) {
  if (WiFi.status() != WL_CONNECTED) return false;
  if (millis() - lastApiFail < RETRY_MS) return false;

  StaticJsonDocument<128> doc;
  doc["device_id"]        = config.nodeId;
  doc["firmware_version"] = FW_VERSION;
  doc["bus_voltage"]      = busVoltage;
  doc["shunt_voltage"]    = shuntVoltage;
  doc["current"]          = current;
  doc["power"]            = power;

  String url = String(config.serverUrl) + "/api/v1/measurements";
  String payload;
  serializeJson(doc, payload);

  HTTPClient http;

  if (url.startsWith("https")) {
    WiFiClientSecure secureClient;
    secureClient.setInsecure();
    if (!http.begin(secureClient, url)) {
      Serial.println("HTTP begin failed");
      lastApiFail = millis();
      serverConnected = false;
      return false;
    }
  } else {
    WiFiClient plainClient;
    if (!http.begin(plainClient, url)) {
      Serial.println("HTTP begin failed");
      lastApiFail = millis();
      serverConnected = false;
      return false;
    }
  }

  http.addHeader("Content-Type", "application/json");
  if (config.apiKey[0] != '\0') {
    http.addHeader("Authorization", "Bearer " + String(config.apiKey));
  }

  int code = http.POST(payload);
  http.end();

  if (code == 201) {
    Serial.print("OK id=");
    Serial.println(config.nodeId);
    serverConnected = true;
    ipReported = true;
    lastUpload = millis();
    return true;
  }

  if (code > 0) {
    Serial.print("HTTP ");
    Serial.println(code);
    serverConnected = false;
  } else {
    Serial.println("API unreachable");
    serverConnected = false;
  }
  lastApiFail = millis();
  return false;
}

// ─────────────────────────────────────────────
//  Setup
// ─────────────────────────────────────────────

void setup() {
  Serial.begin(115200);
  Serial.println("\n\nBuckPow INA219 Captive Portal v" FW_VERSION);

  loadConfig();

  Wire.begin();
  if (!ina219.begin()) {
    Serial.println("ERROR: INA219 not found. Check wiring.");
  } else {
    ina219.setCalibration_32V_2A();
    Serial.println("INA219 detected");
  }

  if (strlen(config.wifiSsid) == 0) {
    Serial.println("No WiFi configured, starting captive portal");
    startCaptivePortal();
  } else {
    WiFi.mode(WIFI_STA);
    if (connectWiFi()) {
      startStatusPage();
    } else {
      Serial.println("WiFi failed, starting captive portal");
      startCaptivePortal();
    }
  }
}

// ─────────────────────────────────────────────
//  Loop
// ─────────────────────────────────────────────

void loop() {
  dnsServer.processNextRequest();
  statusServer.handleClient();

  unsigned long now = millis();

  if (WiFi.status() != WL_CONNECTED && !captivePortalActive && now - lastWifiTry >= WIFI_TIMEOUT) {
    lastWifiTry = now;
    connectWiFi();
  }
  if (WiFi.status() != WL_CONNECTED) return;

  if (now - lastSend < config.sampleInterval) return;
  lastSend = now;

  float busV       = ina219.getBusVoltage_V();
  float shuntV     = ina219.getShuntVoltage_mV();
  float current_mA = ina219.getCurrent_mA();
  float power_mW   = ina219.getPower_mW();

  lastVoltage = busV;
  lastCurrent = current_mA;

  sendLocalIp();
  sendReading(busV, shuntV, current_mA, power_mW);
}
