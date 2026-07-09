(function() {
  var form = document.getElementById('settings-form');
  var status = document.getElementById('settings-status');

  function load() {
    fetch('/api/v1/settings').then(function(r) { return r.json(); }).then(function(s) {
      if (s.high_power_threshold != null) document.getElementById('field-high-power').value = s.high_power_threshold;
      if (s.high_current_threshold != null) document.getElementById('field-high-current').value = s.high_current_threshold;
      if (s.low_voltage_threshold != null) document.getElementById('field-low-voltage').value = s.low_voltage_threshold;
      if (s.brand) document.getElementById('field-brand').value = s.brand;
    });
  }

  form.addEventListener('submit', function(e) {
    e.preventDefault();
    var data = {};
    ['high_power_threshold', 'high_current_threshold', 'low_voltage_threshold', 'brand'].forEach(function(key) {
      var el = document.getElementById('field-' + key.replace(/_/g, '-'));
      var val = el ? el.value.trim() : '';
      data[key] = val || null;
    });

    status.textContent = 'Saving…';
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

  load();
})();
