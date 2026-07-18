#ifndef SETUP_PAGE_H
#define SETUP_PAGE_H

#include <Arduino.h>

const char SETUP_PAGE_HTML[] PROGMEM = R"rawliteral(
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Reconfiguring...</title>
  <meta http-equiv="refresh" content="3;url=/">
</head>
<body style="font-family:sans-serif;background:#0f172a;color:#e2e8f0;display:flex;justify-content:center;align-items:center;height:100vh;">
  <p>Opening captive portal...</p>
</body>
</html>
)rawliteral";

#endif
