function formatTimestamp(isoString) {
  if (!isoString) return '';
  var d = new Date(isoString.replace(/[+-]\d{2}:\d{2}Z$/, 'Z'));
  if (isNaN(d.getTime())) return '';
  var fmt = window.__userTimestampFormat || '24h';
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
  if (fmt === '12h') {
    var ampm = hours >= 12 ? 'PM' : 'AM';
    var h12 = hours % 12 || 12;
    return year + '-' + month + '-' + day + ' ' + h12 + ':' + minutes + ':' + seconds + ' ' + ampm;
  }
  return year + '-' + month + '-' + day + ' ' + pad(hours) + ':' + minutes + ':' + seconds;
}
