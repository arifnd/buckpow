#ifndef CAPTIVE_PORTAL_H
#define CAPTIVE_PORTAL_H

#include <Arduino.h>

const char CAPTIVE_PAGE_TOP[] PROGMEM = R"rawliteral(
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>BuckPow Setup</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0f172a; color: #e2e8f0; min-height: 100vh; display: flex; justify-content: center; padding: 24px; }
    .container { max-width: 400px; width: 100%; }
    .header { text-align: center; margin-bottom: 32px; }
    .header h1 { font-size: 24px; font-weight: 700; color: #f8fafc; }
    .header p { font-size: 14px; color: #94a3b8; margin-top: 4px; }
    .card { background: #1e293b; border-radius: 12px; padding: 20px; margin-bottom: 16px; }
    .card h3 { font-size: 14px; font-weight: 600; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 12px; }
    .field { margin-bottom: 12px; }
    .field:last-child { margin-bottom: 0; }
    .field label { display: block; font-size: 14px; color: #94a3b8; margin-bottom: 4px; }
    .field input, .field select { width: 100%; padding: 10px 12px; background: #0f172a; border: 1px solid #334155; border-radius: 8px; color: #f8fafc; font-size: 14px; }
    .field input:focus, .field select:focus { outline: none; border-color: #2563eb; }
    .field select { appearance: none; cursor: pointer; }
    .field .hint { font-size: 12px; color: #64748b; margin-top: 4px; }
    .wifi-list { list-style: none; max-height: 240px; overflow-y: auto; }
    .wifi-item { display: flex; align-items: center; padding: 10px 12px; border-bottom: 1px solid #334155; cursor: pointer; border-radius: 8px; margin-bottom: 2px; }
    .wifi-item:last-child { border-bottom: none; }
    .wifi-item:hover { background: #334155; }
    .wifi-item.selected { background: #1e3a5f; border-color: #2563eb; }
    .wifi-item .wifi-name { flex: 1; font-size: 14px; color: #f8fafc; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
    .wifi-item .wifi-signal { font-size: 12px; color: #94a3b8; margin-right: 8px; white-space: nowrap; }
    .wifi-item .wifi-lock { font-size: 12px; color: #64748b; margin-left: 4px; }
    .wifi-item .wifi-top { background: #065f46; border-radius: 4px; padding: 1px 6px; font-size: 10px; font-weight: 600; color: #6ee7b7; margin-left: 8px; white-space: nowrap; }
    .wifi-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
    .wifi-header h3 { margin-bottom: 0; }
    .wifi-rescan { background: none; border: 1px solid #334155; color: #94a3b8; font-size: 12px; padding: 4px 10px; border-radius: 6px; cursor: pointer; }
    .wifi-rescan:hover { border-color: #2563eb; color: #f8fafc; }
    .wifi-empty { text-align: center; padding: 20px; color: #64748b; font-size: 13px; }
    #ssid-display { cursor: default; color: #94a3b8; }
    .btn { display: block; width: 100%; padding: 12px; background: #2563eb; color: white; border: none; border-radius: 8px; font-size: 14px; font-weight: 500; cursor: pointer; text-align: center; margin-top: 8px; }
    .btn:hover { background: #1d4ed8; }
    .btn:disabled { background: #334155; cursor: not-allowed; }
    .msg { text-align: center; padding: 48px 0; }
    .msg h1 { font-size: 24px; font-weight: 700; color: #f8fafc; margin-bottom: 8px; }
    .msg p { font-size: 14px; color: #94a3b8; }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>BuckPow Setup</h1>
      <p>Configure your device</p>
    </div>

    <form id="setup-form">
      <div class="card">
        <div class="wifi-header">
          <h3>WiFi Network</h3>
          <button type="button" class="wifi-rescan" id="rescan-btn">Rescan</button>
        </div>
        <input type="hidden" id="ssid" name="ssid" value="">
        <ul class="wifi-list" id="wifi-list">
          <li class="wifi-empty">Scanning...</li>
        </ul>
        <div class="field" style="margin-top:12px">
          <label for="ssid-display">Network</label>
          <input type="text" id="ssid-display" placeholder="Tap a network above" readonly>
        </div>
        <div class="field">
          <label for="password">Password</label>
          <input type="password" id="password" name="password" placeholder="Leave blank for open networks">
          <label style="display:flex;align-items:center;gap:6px;font-size:13px;color:#94a3b8;cursor:pointer;margin-top:8px;margin-bottom:0"><input type="checkbox" id="show-pw" style="width:18px;height:18px;accent-color:#2563eb"> Show password</label>
        </div>
      </div>

      <div class="card">
        <h3>Device</h3>
        <div class="field">
          <label for="deviceName">Device Name</label>
          <input type="text" id="deviceName" name="deviceName" value="esp32-ina219" required>
        </div>
        <div class="field">
          <label for="location">Location</label>
          <input type="text" id="location" name="location" placeholder="Optional">
        </div>
      </div>

      <div class="card">
        <h3>Server</h3>
        <div class="field">
          <label for="serverUrl">BuckPow URL</label>
          <input type="url" id="serverUrl" name="serverUrl" value="http://192.168.1.10:8000" required>
        </div>
        <div class="field">
          <label for="apiKey">API Key</label>
          <input type="text" id="apiKey" name="apiKey" placeholder="Optional">
        </div>
      </div>

      <div class="card">
        <h3>Measurement</h3>
        <div class="field">
          <label for="sampleInterval">Sample Interval (seconds)</label>
          <input type="number" id="sampleInterval" name="sampleInterval" value="1" min="0.1" step="0.1" required>
          <p class="hint">How often to send readings to the server</p>
        </div>
      </div>

      <button type="submit" class="btn" id="save-btn">Save &amp; Connect</button>
    </form>
  </div>

  <script>
    var selectedSsid = '';

    function scanWifi() {
      var list = document.getElementById('wifi-list');
      list.innerHTML = '<li class="wifi-empty">Scanning...</li>';
      document.getElementById('rescan-btn').disabled = true;
      fetch('/scan').then(function(r) { return r.json(); }).then(function(data) {
        list.innerHTML = '';
        document.getElementById('rescan-btn').disabled = false;
        if (!data.length) { list.innerHTML = '<li class="wifi-empty">No networks found</li>'; return; }
        data.sort(function(a, b) { return b.rssi - a.rssi; });
        for (var i = 0; i < data.length; i++) {
          var li = document.createElement('li');
          li.className = 'wifi-item';
          if (data[i].ssid === selectedSsid) li.className += ' selected';
          var html = '<span class="wifi-name">' + data[i].ssid + '</span>';
          html += '<span class="wifi-signal">' + data[i].rssi + ' dBm</span>';
          if (data[i].enc) html += '<span class="wifi-lock">&#128274;</span>';
          if (i < 3) html += '<span class="wifi-top">Strong</span>';
          li.innerHTML = html;
          li.setAttribute('data-ssid', data[i].ssid);
          li.addEventListener('click', function() {
            selectedSsid = this.getAttribute('data-ssid');
            document.getElementById('ssid').value = selectedSsid;
            var display = document.getElementById('ssid-display');
            display.value = selectedSsid;
            display.style.color = '#f8fafc';
            var items = document.querySelectorAll('.wifi-item');
            for (var j = 0; j < items.length; j++) items[j].className = 'wifi-item';
            this.className = 'wifi-item selected';
          });
          list.appendChild(li);
        }
      }).catch(function() {
        list.innerHTML = '<li class="wifi-empty">Scan failed</li>';
        document.getElementById('rescan-btn').disabled = false;
      });
    }
    document.getElementById('rescan-btn').addEventListener('click', scanWifi);
    scanWifi();

    document.getElementById('show-pw').addEventListener('change', function() {
      document.getElementById('password').type = this.checked ? 'text' : 'password';
    });

    document.getElementById('setup-form').addEventListener('submit', function(e) {
      e.preventDefault();
      if (!document.getElementById('ssid').value) { alert('Please select a WiFi network'); return; }
      var btn = document.getElementById('save-btn');
      btn.textContent = 'Saving...';
      btn.disabled = true;
      var data = new URLSearchParams(new FormData(this));
      fetch('/save', { method: 'POST', body: data }).then(function() {
        document.querySelector('.container').innerHTML =
          '<div class="msg"><h1>Restarting...</h1><p>Device will connect to WiFi automatically</p></div>';
      });
    });
  </script>
</body>
</html>
)rawliteral";

#endif
