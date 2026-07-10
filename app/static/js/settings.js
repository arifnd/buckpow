(function() {
  var FIELD_MAP = {
    high_power_threshold: 'field-high-power',
    high_current_threshold: 'field-high-current',
    low_voltage_threshold: 'field-low-voltage',
    brand: 'field-brand',
    timestamp_format: 'field-timestamp-format',
    timezone: 'field-timezone',
    device_watchdog_timeout: 'field-device-watchdog-timeout',
  };

  var FORMS = [
    { id: 'form-alerts', fields: ['high_power_threshold', 'high_current_threshold', 'low_voltage_threshold'], status: 'status-alerts' },
    { id: 'form-general', fields: ['brand', 'timestamp_format', 'timezone', 'device_watchdog_timeout'], status: 'status-general' },
  ];

  function load() {
    fetch('/api/v1/settings').then(function(r) { return r.json(); }).then(function(s) {
      Object.keys(FIELD_MAP).forEach(function(key) {
        var el = document.getElementById(FIELD_MAP[key]);
        if (!el) return;
        if (s[key] != null) {
          if (el.tagName === 'SELECT') el.value = s[key];
          else el.value = s[key];
        }
      });
    });
  }

  FORMS.forEach(function(f) {
    var form = document.getElementById(f.id);
    if (!form) return;
    form.addEventListener('submit', function(e) {
      e.preventDefault();
      var status = document.getElementById(f.status);
      var data = {};
      f.fields.forEach(function(key) {
        var el = document.getElementById(FIELD_MAP[key]);
        var val = el ? el.value.trim() : '';
        data[key] = val || null;
      });

      status.textContent = 'Saving\u2026';
      fetch('/api/v1/settings', {
        method: 'PUT',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(data),
      }).then(function(r) {
        if (r.ok) {
          status.textContent = 'Saved';
          setTimeout(function() { status.textContent = ''; }, 2000);
        } else {
          r.json().then(function(err) { status.textContent = 'Error: ' + (err.error || 'Unknown'); });
        }
      });
    });
  });

  load();
})();