#ifndef STATUS_PAGE_H
#define STATUS_PAGE_H

#include <Arduino.h>

const char STATUS_PAGE_HEAD[] PROGMEM = R"rawliteral(
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>BuckPow Node Status</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0f172a; color: #e2e8f0; min-height: 100vh; display: flex; justify-content: center; padding: 24px; }
    .container { max-width: 400px; width: 100%; }
    .header { text-align: center; margin-bottom: 32px; }
    .header h1 { font-size: 24px; font-weight: 700; color: #f8fafc; }
    .header p { font-size: 14px; color: #94a3b8; margin-top: 4px; }
    .status-card { background: #1e293b; border-radius: 12px; padding: 20px; margin-bottom: 16px; }
    .status-card h3 { font-size: 14px; font-weight: 600; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 12px; }
    .row { display: flex; justify-content: space-between; align-items: center; padding: 8px 0; border-bottom: 1px solid #334155; }
    .row:last-child { border-bottom: none; }
    .label { font-size: 14px; color: #94a3b8; }
    .value { font-size: 14px; font-weight: 500; color: #f8fafc; }
    .badge { display: inline-block; padding: 2px 8px; border-radius: 9999px; font-size: 12px; font-weight: 500; }
    .badge-green { background: #065f46; color: #6ee7b7; }
    .badge-red { background: #7f1d1d; color: #fca5a5; }
    .badge-blue { background: #1e3a5f; color: #93c5fd; }
    .btn { display: block; width: 100%; padding: 12px; background: #2563eb; color: white; border: none; border-radius: 8px; font-size: 14px; font-weight: 500; cursor: pointer; text-align: center; text-decoration: none; margin-top: 8px; }
    .btn:hover { background: #1d4ed8; }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>BuckPow Node</h1>
      <p id="node-id">
)rawliteral";

const char STATUS_PAGE_BODY[] PROGMEM = R"rawliteral(</p>
    </div>

    <div class="status-card">
      <h3>Network</h3>
      <div class="row">
        <span class="label">WiFi</span>
        <span class="badge" id="wifi-badge">Connecting...</span>
      </div>
      <div class="row">
        <span class="label">IP</span>
        <span class="value" id="ip">...</span>
      </div>
      <div class="row">
        <span class="label">RSSI</span>
        <span class="value" id="rssi">...</span>
      </div>
      <div class="row">
        <span class="label">Server</span>
        <span class="badge" id="server-badge">Connecting...</span>
      </div>
    </div>

    <div class="status-card">
      <h3>Sensor</h3>
      <div class="row">
        <span class="label">Type</span>
        <span class="badge badge-blue">INA219</span>
      </div>
      <div class="row">
        <span class="label">Voltage</span>
        <span class="value" id="voltage">--</span>
      </div>
      <div class="row">
        <span class="label">Current</span>
        <span class="value" id="current">--</span>
      </div>
    </div>

    <div class="status-card">
      <h3>Upload</h3>
      <div class="row">
        <span class="label">Last Upload</span>
        <span class="value" id="last-upload">never</span>
      </div>
      <div class="row">
        <span class="label">Uptime</span>
        <span class="value" id="uptime">...</span>
      </div>
      <div class="row">
        <span class="label">Firmware</span>
        <span class="value">v)rawliteral";

const char STATUS_PAGE_SCRIPT[] PROGMEM = R"rawliteral(</span>
      </div>
    </div>

    <a class="btn" href="/setup">Reconfigure</a>
  </div>

  <script>
    function update() {
      fetch('/api/status')
        .then(r => r.json())
        .then(d => {
          document.getElementById('node-id').textContent = d.node_id || 'BuckPow Node';
          document.getElementById('ip').textContent = d.ip || '--';
          document.getElementById('rssi').textContent = d.rssi ? d.rssi + ' dBm' : '--';

          var wb = document.getElementById('wifi-badge');
          if (d.wifi === 'Connected') {
            wb.textContent = 'Connected';
            wb.className = 'badge badge-green';
          } else {
            wb.textContent = 'Disconnected';
            wb.className = 'badge badge-red';
          }

          var sb = document.getElementById('server-badge');
          if (d.server === 'Connected') {
            sb.textContent = 'Connected';
            sb.className = 'badge badge-green';
          } else {
            sb.textContent = 'Disconnected';
            sb.className = 'badge badge-red';
          }

          document.getElementById('last-upload').textContent = d.last_upload || 'never';
          document.getElementById('voltage').textContent = d.voltage != null ? d.voltage.toFixed(2) + ' V' : '--';
          document.getElementById('current').textContent = d.current != null ? d.current.toFixed(1) + ' mA' : '--';

          var uptime = d.uptime || 0;
          var h = Math.floor(uptime / 3600);
          var m = Math.floor((uptime % 3600) / 60);
          var s = uptime % 60;
          document.getElementById('uptime').textContent =
            (h > 0 ? h + 'h ' : '') + m + 'm ' + s + 's';
        })
        .catch(e => console.error('Status fetch error:', e));
    }
    update();
    setInterval(update, 3000);
  </script>
</body>
</html>
)rawliteral";

#endif
