var benchmarkChart = null;

function initBenchmarkPage() {
  loadSessions();
  document.getElementById('compare-btn').addEventListener('click', runComparison);
  document.getElementById('session-a').addEventListener('change', enableCompare);
  document.getElementById('session-b').addEventListener('change', enableCompare);
  document.getElementById('session-c').addEventListener('change', enableCompare);
}

function enableCompare() {
  var a = document.getElementById('session-a').value;
  var b = document.getElementById('session-b').value;
  document.getElementById('compare-btn').disabled = !(a && b);
}

function loadSessions() {
  fetch('/api/v1/sessions?page=0')
    .then(function(r) { return r.json(); })
    .then(function(sessions) {
      var selA = document.getElementById('session-a');
      var selB = document.getElementById('session-b');
      var selC = document.getElementById('session-c');
      selA.innerHTML = '<option value="">Select a finished session</option>';
      selB.innerHTML = '<option value="">Select a finished session</option>';
      selC.innerHTML = '<option value="">Select (optional)</option>';
      sessions.filter(function(s) { return s.status === 'finished'; }).forEach(function(s) {
        var label = s.name + ' (' + s.device_name + ')';
        var optA = document.createElement('option');
        optA.value = s.id;
        optA.textContent = label;
        selA.appendChild(optA);
        var optB = document.createElement('option');
        optB.value = s.id;
        optB.textContent = label;
        selB.appendChild(optB);
        var optC = document.createElement('option');
        optC.value = s.id;
        optC.textContent = label;
        selC.appendChild(optC);
      });
      if (sessions.filter(function(s) { return s.status === 'finished'; }).length === 0) {
        var statusEl = document.getElementById('compare-status');
        statusEl.textContent = 'No finished sessions available.';
      }
    });
}

function runComparison() {
  var a = document.getElementById('session-a').value;
  var b = document.getElementById('session-b').value;
  var c = document.getElementById('session-c').value;
  if (!a || !b) return;

  var ids = [a, b];
  if (c) ids.push(c);

  var btn = document.getElementById('compare-btn');
  var statusEl = document.getElementById('compare-status');
  btn.disabled = true;
  statusEl.textContent = 'Loading...';

  fetch('/api/v1/benchmark/compare?sessions=' + ids.join(','))
    .then(function(r) { return r.json(); })
    .then(function(data) {
      statusEl.textContent = '';
      btn.disabled = false;
      if (data.sessions && data.sessions.length >= 2) {
        renderComparison(data.sessions);
      }
    })
    .catch(function() {
      statusEl.textContent = 'Error loading comparison.';
      btn.disabled = false;
    });
}

function fmtDuration(secs) {
  if (!secs || secs <= 0) return '\u2014';
  var d = Math.floor(secs / 86400); secs %= 86400;
  var h = Math.floor(secs / 3600); secs %= 3600;
  var m = Math.floor(secs / 60);
  var s = Math.floor(secs % 60);
  var parts = [];
  if (d > 0) parts.push(d + 'd');
  if (h > 0) parts.push(h + 'h');
  if (m > 0) parts.push(m + 'm');
  parts.push(s + 's');
  return parts.join(' ');
}

function renderComparison(sessions) {
  document.getElementById('results-section').classList.remove('hidden');
  document.getElementById('header-a').textContent = sessions[0].session_name;
  document.getElementById('header-b').textContent = sessions.length >= 2 ? sessions[1].session_name : '';
  var headerC = document.getElementById('header-c');
  if (sessions.length >= 3) {
    headerC.textContent = sessions[2].session_name;
    headerC.classList.remove('hidden');
  } else {
    headerC.textContent = 'Session 3';
    headerC.classList.add('hidden');
  }

  var tbody = document.getElementById('comparison-tbody');
  var rows = [
    { label: 'Device', fn: function(s) { return s.device_name || '\u2014'; } },
    { label: 'Avg Power (W)', fn: function(s) { return s.avg_power; } },
    { label: 'Peak Power (W)', fn: function(s) { return s.peak_power; } },
    { label: 'Total Energy (Wh)', fn: function(s) { return s.total_energy; } },
    { label: 'Avg Current (A)', fn: function(s) { return s.avg_current; } },
    { label: 'Voltage Std Dev', fn: function(s) { return s.voltage_stddev; } },
    { label: 'Duration', fn: function(s) { return fmtDuration(s.duration); } },
    { label: 'Measurements', fn: function(s) { return s.measurement_count; } },
    { label: 'Started', fn: function(s) { return formatTimestamp(s.started_at); } },
    { label: 'Ended', fn: function(s) { return formatTimestamp(s.ended_at); } },
  ];
  tbody.innerHTML = rows.map(function(r, i) {
    var cls = i % 2 === 0 ? 'bg-white dark:bg-gray-900' : '';
    var hiddenCol = sessions.length < 3 ? ' hidden' : '';
    return '<tr class="border-b border-gray-200 dark:border-gray-800 hover:bg-gray-100 dark:hover:bg-gray-800 ' + cls + '">'
      + '<td class="py-2 px-3 font-medium">' + r.label + '</td>'
      + '<td class="py-2 px-3">' + r.fn(sessions[0]) + '</td>'
      + '<td class="py-2 px-3">' + (sessions[1] ? r.fn(sessions[1]) : '') + '</td>'
      + '<td class="py-2 px-3' + hiddenCol + '">' + (sessions[2] ? r.fn(sessions[2]) : '') + '</td>'
      + '</tr>';
  }).join('');

  renderOverlayChart(sessions);
}

function formatBenchTime(isoString) {
  if (!isoString) return '';
  var d = new Date(isoString);
  if (isNaN(d.getTime())) return '';
  var tzOffset = parseInt(window.__userTimezone || '0', 10) || 0;
  var dt = new Date(d.getTime() + tzOffset * 3600000);
  function pad(n) { return String(n).padStart(2, '0'); }
  return pad(dt.getUTCHours()) + ':' + pad(dt.getUTCMinutes()) + ':' + pad(dt.getUTCSeconds());
}

function renderOverlayChart(sessions) {
  var ctx = document.getElementById('benchmarkChart').getContext('2d');
  if (benchmarkChart) {
    benchmarkChart.destroy();
  }

  var labels = sessions[0].chart_data.labels.map(formatBenchTime);
  var colors = ['#58a6ff', '#f85149', '#3fb950'];
  var datasets = sessions.map(function(s, i) {
    return {
      label: s.session_name,
      data: s.chart_data.power,
      borderColor: colors[i],
      backgroundColor: colors[i] + '20',
      tension: 0.2,
      fill: false,
      pointRadius: 0,
      pointHitRadius: 5,
      borderWidth: 2,
    };
  });

  benchmarkChart = new Chart(ctx, {
    type: 'line',
    data: { labels: labels, datasets: datasets },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: 'nearest', intersect: false },
      plugins: {
        legend: {
          display: true,
          labels: { color: '#c9d1d9', font: { size: 12 } },
        },
      },
      scales: {
        x: {
          ticks: { color: '#8b949e', maxTicksLimit: 10, font: { size: 12 } },
          grid: { display: false },
        },
        y: {
          ticks: { color: '#8b949e', font: { size: 12 } },
          grid: { color: '#21262d' },
          beginAtZero: true,
          title: {
            display: true,
            text: 'Power (W)',
            color: '#8b949e',
          },
        },
      },
    },
  });
}

function isBenchmarkPage() {
  return !!document.getElementById('session-a');
}

function initOnBenchmark() {
  if (isBenchmarkPage()) {
    initBenchmarkPage();
  }
}

document.addEventListener('DOMContentLoaded', initOnBenchmark);
document.addEventListener('htmx:afterSettle', initOnBenchmark);
