var benchmarkChart = null;

function initBenchmarkPage() {
  loadSessions();
  document.getElementById('compare-btn').addEventListener('click', runComparison);
  document.getElementById('session-a').addEventListener('change', enableCompare);
  document.getElementById('session-b').addEventListener('change', enableCompare);
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
      selA.innerHTML = '<option value="">Select a finished session</option>';
      selB.innerHTML = '<option value="">Select a finished session</option>';
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
  if (!a || !b) return;

  var btn = document.getElementById('compare-btn');
  var statusEl = document.getElementById('compare-status');
  btn.disabled = true;
  statusEl.textContent = 'Loading...';

  fetch('/api/v1/benchmark/compare?sessions=' + a + ',' + b)
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
  document.getElementById('header-b').textContent = sessions[1].session_name;

  var tbody = document.getElementById('comparison-tbody');
  var rows = [
    { label: 'Device', a: sessions[0].device_name || '\u2014', b: sessions[1].device_name || '\u2014' },
    { label: 'Avg Power (W)', a: sessions[0].avg_power, b: sessions[1].avg_power },
    { label: 'Peak Power (W)', a: sessions[0].peak_power, b: sessions[1].peak_power },
    { label: 'Total Energy (Wh)', a: sessions[0].total_energy, b: sessions[1].total_energy },
    { label: 'Avg Current (A)', a: sessions[0].avg_current, b: sessions[1].avg_current },
    { label: 'Voltage Std Dev', a: sessions[0].voltage_stddev, b: sessions[1].voltage_stddev },
    { label: 'Duration', a: fmtDuration(sessions[0].duration), b: fmtDuration(sessions[1].duration) },
    { label: 'Measurements', a: sessions[0].measurement_count, b: sessions[1].measurement_count },
    { label: 'Started', a: sessions[0].started_at ? new Date(sessions[0].started_at).toLocaleString() : '\u2014', b: sessions[1].started_at ? new Date(sessions[1].started_at).toLocaleString() : '\u2014' },
    { label: 'Ended', a: sessions[0].ended_at ? new Date(sessions[0].ended_at).toLocaleString() : '\u2014', b: sessions[1].ended_at ? new Date(sessions[1].ended_at).toLocaleString() : '\u2014' },
  ];
  tbody.innerHTML = rows.map(function(r, i) {
    var cls = i % 2 === 0 ? 'bg-[var(--surface)]' : '';
    return '<tr class="border-b border-[var(--border)] hover:bg-[var(--hover)] ' + cls + '">'
      + '<td class="py-2 px-3 font-medium">' + r.label + '</td>'
      + '<td class="py-2 px-3">' + r.a + '</td>'
      + '<td class="py-2 px-3">' + r.b + '</td>'
      + '</tr>';
  }).join('');

  renderOverlayChart(sessions);
}

function formatBenchTime(isoString) {
  if (!isoString) return '';
  var d = new Date(isoString);
  if (isNaN(d.getTime())) return '';
  return d.getHours().toString().padStart(2, '0') + ':' +
         d.getMinutes().toString().padStart(2, '0') + ':' +
         d.getSeconds().toString().padStart(2, '0');
}

function renderOverlayChart(sessions) {
  var ctx = document.getElementById('benchmarkChart').getContext('2d');
  if (benchmarkChart) {
    benchmarkChart.destroy();
  }

  var labels = sessions[0].chart_data.labels.map(formatBenchTime);
  var colors = ['#58a6ff', '#f85149'];
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
