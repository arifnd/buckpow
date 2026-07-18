function fmtSig(val, digits) {
  if (val === 0) return '0';
  digits = digits || 3;
  var magnitude = Math.floor(Math.log10(Math.abs(val))) + 1;
  var decimals = Math.max(0, digits - magnitude);
  return val.toFixed(decimals);
}

function fmtCurrent(a) {
  if (a == null) return '-';
  var abs = Math.abs(a);
  if (abs < 0.001) return fmtSig(a * 1000000) + ' µA';
  if (abs < 1) return fmtSig(a * 1000) + ' mA';
  return fmtSig(a) + ' A';
}

function fmtPower(w) {
  if (w == null) return '-';
  var abs = Math.abs(w);
  if (abs < 0.001) return fmtSig(w * 1000000) + ' µW';
  if (abs < 1) return fmtSig(w * 1000) + ' mW';
  if (abs < 1000) return fmtSig(w) + ' W';
  return fmtSig(w / 1000) + ' kW';
}

function fmtEnergy(wh) {
  if (wh == null) return '-';
  if (Math.abs(wh) >= 1000) return fmtSig(wh / 1000) + ' kWh';
  return fmtSig(wh) + ' Wh';
}
