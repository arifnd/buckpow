const MAX_POINTS = 50;
let voltageChart, currentChart, powerChart, energyChart;
let intervalId;
let currentGranularity = '';

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

function updateSummaryCards(data) {
  if (!data || !data.latest) return;
  const r = data.latest;
  const dev = data.devices && data.devices.find(d => d.id === r.device_id);
  document.getElementById('val-device').textContent = dev ? dev.device_id : r.device_id;
  document.getElementById('val-voltage').textContent = toFixedSafe(r.bus_voltage, 3);
  document.getElementById('val-load-voltage').textContent = toFixedSafe(r.load_voltage, 3);
  document.getElementById('val-current').textContent = toFixedSafe(r.current, 3);
  document.getElementById('val-power').textContent = toFixedSafe(r.power, 3);
  document.getElementById('val-energy').textContent = toFixedSafe(r.energy, 3);
  document.getElementById('last-updated').textContent = new Date().toLocaleTimeString();

  const statusEl = document.getElementById('val-status');
  if (dev) {
    statusEl.textContent = dev.status;
    statusEl.className = 'inline-flex items-center px-2 py-0.5 rounded-full text-sm font-medium ' + (dev.status === 'online' ? 'bg-[#3fb950] text-white' : 'bg-[#8b949e] text-white');
  }
}

const CARD_COLORS = {
  info: 'text-[#58a6ff]',
  success: 'text-[#3fb950]',
  warning: 'text-[#d29922]',
  purple: 'text-[#d2a8ff]',
};

function statCard(title, unit, color, fields) {
  return `<div class="bg-[var(--surface)] border border-[var(--border)] rounded-lg p-3">
    <small class="text-[var(--muted)] uppercase tracking-wide text-xs">${title}</small>
    ${fields.map(f => `
      <div class="flex justify-between items-center py-1.5 border-b border-[var(--border)] last:border-0">
        <small class="text-[var(--muted)]">${f.label}</small>
        <span class="${CARD_COLORS[color] || 'text-[#c9d1d9]'} font-semibold">${f.val} <small class="text-[var(--muted)] font-normal">${unit}</small></span>
      </div>`).join('')}
  </div>`;
}

function updateStats(stats) {
  if (!stats || !stats.voltage) return;
  const container = document.getElementById('stats-cards');
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
    statCard('Energy', 'Wh', 'purple', [
      { label: 'Total', val: toFixedSafe(stats.energy.total, 6) },
    ]);
}

function updateTable(measurements) {
  const tbody = document.getElementById('readings-body');
  tbody.innerHTML = measurements.slice(0, 20).map(r => `<tr class="border-b border-[var(--border)] hover:bg-[var(--hover)]">
    <td class="py-2 px-2 text-left">${r.created_at ? new Date(r.created_at).toLocaleString() : ''}</td>
    <td class="py-2 px-2 text-left">${r.session_name || '—'}</td>
    <td class="py-2 px-2 text-right">${toFixedSafe(r.bus_voltage, 3)}</td>
    <td class="py-2 px-2 text-right">${toFixedSafe(r.shunt_voltage, 3)}</td>
    <td class="py-2 px-2 text-right">${toFixedSafe(r.load_voltage, 3)}</td>
    <td class="py-2 px-2 text-right">${(toFixedSafe(r.current, 3) * 1000).toFixed(2)} mA</td>
    <td class="py-2 px-2 text-right">${(toFixedSafe(r.power, 3) * 1000).toFixed(2)} mW</td>
    <td class="py-2 px-2 text-right">${toFixedSafe(r.energy, 6)}</td>
  </tr>`).join('');
}

function updateCharts(chartData) {
  if (!chartData || !chartData.labels || chartData.labels.length === 0) {
    return;
  }

  const slice = (arr) => arr.slice(-MAX_POINTS);
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

  energyChart.data.labels = labels;
  energyChart.data.datasets[0].data = slice(chartData.energy);
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

async function fetchDashboardData() {
  const dashboard = await fetchJSON('/api/v1/dashboard');

  var sessionEl = document.getElementById('session-indicator');
  if (!dashboard || !dashboard.active_session) {
    if (sessionEl) {
      sessionEl.innerHTML = '<span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-[#8b949e] text-white">No active session</span>';
    }
    updateCharts({labels: [], voltage: [], current: [], power: [], energy: []});
    return;
  }

  if (sessionEl) {
    var s = dashboard.active_session;
    sessionEl.innerHTML = '<span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-[#3fb950] text-white">Session: ' + s.name + '</span>';
  }

  var sessionFilter = 'session_id=' + dashboard.active_session.id + '&';
  var params = currentGranularity ? 'granularity=' + currentGranularity + '&' : '';
  var [chart, recent] = await Promise.all([
    fetchJSON('/api/v1/chart?' + sessionFilter + params + 'limit=100'),
    fetchJSON('/api/v1/measurements?' + sessionFilter + 'per_page=20'),
  ]);

  if (dashboard) {
    updateSummaryCards(dashboard);
    updateStats(dashboard.stats || {});
  }
  if (chart) {
    updateCharts(chart);
  }
  if (recent) {
    updateTable(recent.measurements || []);
  }
}

document.addEventListener('DOMContentLoaded', () => {
  initCharts();
  fetchDashboardData();
  intervalId = setInterval(fetchDashboardData, 5000);

  document.getElementById('granularity-group').addEventListener('click', (e) => {
    const btn = e.target.closest('button');
    if (!btn) return;
    const g = btn.dataset.granularity;
    if (g === currentGranularity) return;
    currentGranularity = g;
    document.querySelectorAll('#granularity-group button').forEach(b => {
      if (b.dataset.granularity === g) {
        b.classList.remove('text-[var(--muted)]', 'bg-transparent');
        b.classList.add('text-[var(--body-text)]', 'bg-[var(--surface)]');
      } else {
        b.classList.remove('text-[var(--body-text)]', 'bg-[var(--surface)]');
        b.classList.add('text-[var(--muted)]', 'bg-transparent');
      }
    });
    fetchDashboardData();
  });
});
