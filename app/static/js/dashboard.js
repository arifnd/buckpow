var MAX_POINTS = 50;
var voltageChart, currentChart, powerChart, energyChart;
var currentTimeRange = '1h';
var currentSessionId = '';
var sessionStartedAts = {};


function initCharts() {
  voltageChart = createChart('voltageChart', 'Voltage (V)', 'voltage');
  currentChart = createChart('currentChart', 'Current (A)', 'current');
  powerChart = createChart('powerChart', 'Power (W)', 'power');
  energyChart = createChart('energyChart', 'Energy (Wh)', 'energy');
}

function formatTime(isoString) {
  if (!isoString) return '';
  const d = new Date(isoString);
  if (isNaN(d.getTime())) return '';
  return d.getHours().toString().padStart(2, '0') + ':' +
         d.getMinutes().toString().padStart(2, '0') + ':' +
         d.getSeconds().toString().padStart(2, '0');
}

function toFixedSafe(val, digits) {
  return (val != null ? Number(val) : 0).toFixed(digits);
}

function formatDuration(startedAt) {
  if (!startedAt) return '\u2014';
  var diff = Math.floor((Date.now() - new Date(startedAt).getTime()) / 1000);
  if (diff < 0) return '\u2014';
  var d = Math.floor(diff / 86400); diff %= 86400;
  var h = Math.floor(diff / 3600); diff %= 3600;
  var m = Math.floor(diff / 60);
  var s = diff % 60;
  var parts = [];
  if (d > 0) parts.push(d + 'd');
  if (h > 0) parts.push(h + 'h');
  if (m > 0) parts.push(m + 'm');
  parts.push(s + 's');
  return parts.join(' ');
}

function updateSummaryCards(data) {
  if (!data) return;
  var online = 0, total = 0;
  if (data.devices) {
    total = data.devices.length;
    data.devices.forEach(function(d) { if (d.status === 'online') online++; });
  }
  document.getElementById('val-device').textContent = online + '/' + total;

  if (data.latest) {
    var r = data.latest;
    document.getElementById('val-current').textContent = toFixedSafe(r.current, 3);
    document.getElementById('val-power').textContent = toFixedSafe(r.power, 3);
  }
}

function updateSummaryFromSummary(summary) {
  if (!summary) return;
  document.getElementById('val-load-voltage').textContent = summary.total_projects;
  document.getElementById('val-voltage').textContent = summary.active_sessions;
  document.getElementById('val-energy').textContent = toFixedSafe(summary.today_energy, 6);
}

const CARD_COLORS = {
  info: 'text-[#58a6ff]',
  success: 'text-[#3fb950]',
  warning: 'text-[#d29922]',
  purple: 'text-[#d2a8ff]',
};

function statCard(title, unit, color, fields) {
  return '<div class="bg-[var(--surface)] border border-[var(--border)] rounded-lg p-3">\n    <small class="text-[var(--muted)] uppercase tracking-wide text-xs">' + title + '</small>\n    ' + fields.map(function(f) {
    return '\n      <div class="flex justify-between items-center py-1.5 border-b border-[var(--border)] last:border-0">\n        <small class="text-[var(--muted)]">' + f.label + '</small>\n        <span class="' + (CARD_COLORS[color] || 'text-[#c9d1d9]') + ' font-semibold">' + f.val + ' <small class="text-[var(--muted)] font-normal">' + unit + '</small></span>\n      </div>';
  }).join('') + '\n  </div>';
}

function updateStats(dashboard) {
  var stats = dashboard.stats;
  if (!stats || !stats.voltage) return;
  var container = document.getElementById('stats-cards');
  var totalFields = [];
  if (dashboard.latest && dashboard.latest.energy != null) {
    totalFields.push({ label: 'Energy', val: toFixedSafe(dashboard.latest.energy, 6) });
  }
  var started = sessionStartedAts[currentSessionId];
  if (started) {
    totalFields.push({ label: 'Running', val: formatDuration(started) });
  }
  container.innerHTML =
    statCard('Voltage', 'V', 'info', [
      { label: 'Min', val: toFixedSafe(stats.voltage.min, 3) },
      { label: 'Max', val: toFixedSafe(stats.voltage.max, 3) },
      { label: 'Avg', val: toFixedSafe(stats.voltage.avg, 3) },
    ]) +
    statCard('Current', 'A', 'success', [
      { label: 'Min', val: toFixedSafe(stats.current.min, 3) },
      { label: 'Max', val: toFixedSafe(stats.current.max, 3) },
      { label: 'Avg', val: toFixedSafe(stats.current.avg, 3) },
    ]) +
    statCard('Power', 'W', 'warning', [
      { label: 'Min', val: toFixedSafe(stats.power.min, 3) },
      { label: 'Max', val: toFixedSafe(stats.power.max, 3) },
      { label: 'Avg', val: toFixedSafe(stats.power.avg, 3) },
      { label: 'Peak', val: toFixedSafe(stats.power.peak, 3) },
    ]) +
    (totalFields.length ? statCard('TOTAL', '', 'purple', totalFields) : '');
}

function updateEnergyBreakdown(stats) {
  if (!stats || !stats.energy) return;
  var tables = {
    hourly: document.getElementById('energy-hourly').querySelector('tbody'),
    daily: document.getElementById('energy-daily').querySelector('tbody'),
    weekly: document.getElementById('energy-weekly').querySelector('tbody'),
    monthly: document.getElementById('energy-monthly').querySelector('tbody'),
  };
  Object.keys(tables).forEach(function(key) {
    var rows = stats.energy[key] || [];
    tables[key].innerHTML = rows.slice(-20).map(function(r) {
      return '<tr class="border-b border-[var(--border)]"><td class="py-0.5 pr-2">' + r.period + '</td><td class="py-0.5 text-right">' + r.energy.toFixed(6) + '</td></tr>';
    }).join('') || '<tr><td class="py-1 text-[var(--muted)]" colspan="2">No data</td></tr>';
  });
}

function updateTable(measurements) {
  const tbody = document.getElementById('readings-body');
  tbody.innerHTML = measurements.slice(0, 10).map(function(r) {
    return '<tr class="border-b border-[var(--border)] hover:bg-[var(--hover)]">\n    <td class="py-2 px-2 text-left">' + (r.created_at ? new Date(r.created_at).toLocaleString() : '') + '</td>\n    <td class="py-2 px-2 text-left">' + (r.session_name || '\u2014') + '</td>\n    <td class="py-2 px-2 text-right">' + toFixedSafe(r.bus_voltage, 3) + '</td>\n    <td class="py-2 px-2 text-right">' + toFixedSafe(r.shunt_voltage, 3) + '</td>\n    <td class="py-2 px-2 text-right">' + toFixedSafe(r.load_voltage, 3) + '</td>\n    <td class="py-2 px-2 text-right">' + (toFixedSafe(r.current, 3) * 1000).toFixed(2) + ' mA</td>\n    <td class="py-2 px-2 text-right">' + (toFixedSafe(r.power, 3) * 1000).toFixed(2) + ' mW</td>\n    <td class="py-2 px-2 text-right">' + toFixedSafe(r.energy, 6) + '</td>\n  </tr>';
  }).join('');
}

function updateCharts(chartData) {
  if (!chartData || !chartData.labels || chartData.labels.length === 0) {
    return;
  }

  var lastIdx = chartData.labels.length - 1;
  var el;

  el = document.getElementById('chart-val-voltage');
  if (el && chartData.voltage && chartData.voltage[lastIdx] != null) el.textContent = toFixedSafe(chartData.voltage[lastIdx], 3);

  el = document.getElementById('chart-val-current');
  if (el && chartData.current && chartData.current[lastIdx] != null) el.textContent = toFixedSafe(chartData.current[lastIdx], 3);

  el = document.getElementById('chart-val-power');
  if (el && chartData.power && chartData.power[lastIdx] != null) el.textContent = toFixedSafe(chartData.power[lastIdx], 3);

  el = document.getElementById('chart-val-energy');
  if (el && chartData.energy && chartData.energy[lastIdx] != null) el.textContent = toFixedSafe(chartData.energy[lastIdx], 6);

  const slice = function(arr) { return arr.slice(-MAX_POINTS); };
  const labels = slice(chartData.labels).map(formatTime);

  voltageChart.data.labels = labels;
  voltageChart.data.datasets[0].data = slice(chartData.voltage);
  voltageChart.update();

  currentChart.data.labels = labels;
  currentChart.data.datasets[0].data = slice(chartData.current);
  currentChart.update();

  powerChart.data.labels = labels;
  powerChart.data.datasets[0].data = slice(chartData.power);
  powerChart.update();

  var energyData = slice(chartData.energy);
  if (energyData.length > 0) {
    var base = energyData[0];
    energyData = energyData.map(function(v) { return v - base; });
  }
  energyChart.data.labels = labels;
  energyChart.data.datasets[0].data = energyData;
  energyChart.update();
}

async function fetchJSON(url) {
  try {
    const res = await fetch(url);
    if (!res.ok) {
      console.warn('Fetch failed:', url, res.status);
      return null;
    }
    return await res.json();
  } catch (err) {
    console.warn('Fetch error:', url, err.message);
    return null;
  }
}

function loadSessionSelector() {
  fetch('/api/v1/sessions?page=0').then(function(r) { return r.json(); }).then(function(sessions) {
    var sel = document.getElementById('session-selector');
    var currentVal = sel.value;
    var running = sessions.filter(function(s) { return s.status === 'running'; });
    sel.innerHTML = '<option value=""' + (running.length > 0 ? ' disabled' : '') + '>Select a running session</option>';
    sessionStartedAts = {};
    running.forEach(function(s) {
      sessionStartedAts[s.id] = s.started_at;
      var opt = document.createElement('option');
      opt.value = s.id;
      opt.textContent = s.name + ' (' + s.device_name + ')';
      sel.appendChild(opt);
    });
    if (currentVal && [...sel.options].some(function(o) { return o.value === currentVal; })) {
      sel.value = currentVal;
    } else if (running.length > 0) {
      sel.value = running[0].id;
    }
    currentSessionId = sel.value;
    if (currentSessionId) {
      fetchDashboardData();
      fetchStatistics();
    }
  });
}

function buildSessionFilter() {
  return currentSessionId ? 'session_id=' + currentSessionId : '';
}

async function fetchSummary() {
  var data = await fetchJSON('/api/v1/dashboard/summary');
  if (data) updateSummaryFromSummary(data);
}

async function fetchDashboardData() {
  const dashboard = await fetchJSON('/api/v1/dashboard');

  var sessionFilter = buildSessionFilter();
  if (!sessionFilter) {
    updateCharts({labels: [], voltage: [], current: [], power: [], energy: []});
    clearStatistics();
    return;
  }

  if (dashboard) {
    updateSummaryCards(dashboard);
    updateStats(dashboard);
  }

  var granularityMap = {'1h': 'm', '24h': 'h', '7d': 'd', '30d': 'd'};
  var limitMap = {'1h': 60, '24h': 24, '7d': 7, '30d': 30};
  var params = sessionFilter + '&limit=' + (limitMap[currentTimeRange] || 100) + '&range=' + currentTimeRange + '&granularity=' + (granularityMap[currentTimeRange] || '');
  var [chart, recent, summary] = await Promise.all([
    fetchJSON('/api/v1/chart?' + params),
    fetchJSON('/api/v1/measurements?' + sessionFilter + '&per_page=10'),
    fetchJSON('/api/v1/dashboard/summary'),
  ]);

  if (chart) updateCharts(chart);
  if (recent) updateTable(recent.measurements || []);
  if (summary) updateSummaryFromSummary(summary);
}

function clearStatistics() {
  document.getElementById('stats-cards').innerHTML = '';
  ['hourly', 'daily', 'weekly', 'monthly'].forEach(function(key) {
    var table = document.getElementById('energy-' + key);
    if (table) table.querySelector('tbody').innerHTML = '';
  });
}

async function fetchStatistics() {
  if (!currentSessionId) {
    clearStatistics();
    return;
  }
  var params = 'session_id=' + currentSessionId;
  if (currentTimeRange) {
    var now = Date.now();
    if (currentTimeRange === '1h') params += '&start_date=' + new Date(now - 3600000).toISOString();
    else if (currentTimeRange === '24h') params += '&start_date=' + new Date(now - 86400000).toISOString();
    else if (currentTimeRange === '7d') params += '&start_date=' + new Date(now - 604800000).toISOString();
    else if (currentTimeRange === '30d') params += '&start_date=' + new Date(now - 2592000000).toISOString();
  }
  var stats = await fetchJSON('/api/v1/dashboard/statistics?' + params);
  if (stats) updateEnergyBreakdown(stats);
}

function startDashboard() {
  if (window.__dashboardIntervalId) clearInterval(window.__dashboardIntervalId);
  if (window.__statIntervalId) clearInterval(window.__statIntervalId);
  if (window.__summaryIntervalId) clearInterval(window.__summaryIntervalId);
  initCharts();
  fetchSummary();
  loadSessionSelector();
  window.__dashboardIntervalId = setInterval(fetchDashboardData, 5000);
  window.__statIntervalId = setInterval(fetchStatistics, 30000);
  window.__summaryIntervalId = setInterval(fetchSummary, 30000);
}

function isDashboardPage() {
  return !!document.getElementById('voltageChart');
}

function initOnDashboard() {
  if (isDashboardPage()) {
    startDashboard();
  }
}

document.addEventListener('DOMContentLoaded', initOnDashboard);
document.addEventListener('htmx:afterSettle', initOnDashboard);

document.addEventListener('change', function(e) {
  if (e.target.id === 'session-selector') {
    currentSessionId = e.target.value;
    if (currentSessionId) {
      fetchDashboardData();
      fetchStatistics();
    } else {
      updateCharts({labels: [], voltage: [], current: [], power: [], energy: []});
      clearStatistics();
    }
  }
});

document.addEventListener('click', function(e) {
  var rangeBtn = e.target.closest('#time-range-group button');
  if (!rangeBtn) return;
  var r = rangeBtn.dataset.range;
  if (r === currentTimeRange) return;
  currentTimeRange = r;
  document.querySelectorAll('#time-range-group button').forEach(function(b) {
    if (b.dataset.range === r) {
      b.classList.remove('text-[var(--muted)]', 'bg-transparent');
      b.classList.add('text-[var(--body-text)]', 'bg-[var(--surface)]');
    } else {
      b.classList.remove('text-[var(--body-text)]', 'bg-[var(--surface)]');
      b.classList.add('text-[var(--muted)]', 'bg-transparent');
    }
  });
  if (currentSessionId) {
    fetchDashboardData();
    fetchStatistics();
  }
});
