function formatTimestamp(isoString) {
  if (!isoString) return '';
  var d = new Date(isoString);
  if (isNaN(d.getTime())) return '';
  var tFmt = window.__userTimestampFormat || '24h';
  var dFmt = window.__userDateFormat || 'YYYY-MM-DD';
  var tzOffset = parseInt(window.__userTimezone || '0', 10) || 0;
  var targetMs = d.getTime() + tzOffset * 3600000;
  function pad(n) { return String(n).padStart(2, '0'); }
  var dt = new Date(targetMs);
  var year = dt.getUTCFullYear();
  var month = pad(dt.getUTCMonth() + 1);
  var day = pad(dt.getUTCDate());
  var hours = dt.getUTCHours();
  var minutes = pad(dt.getUTCMinutes());
  var seconds = pad(dt.getUTCSeconds());
  var dateStr;
  if (dFmt === 'DD/MM/YYYY') {
    dateStr = day + '/' + month + '/' + year;
  } else if (dFmt === 'MM/DD/YYYY') {
    dateStr = month + '/' + day + '/' + year;
  } else {
    dateStr = year + '-' + month + '-' + day;
  }
  if (tFmt === '12h') {
    var ampm = hours >= 12 ? 'PM' : 'AM';
    var h12 = hours % 12 || 12;
    return dateStr + ' ' + h12 + ':' + minutes + ':' + seconds + ' ' + ampm;
  }
  return dateStr + ' ' + pad(hours) + ':' + minutes + ':' + seconds;
}
