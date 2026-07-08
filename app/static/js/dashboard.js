const MAX_POINTS = 50;
let voltageChart, currentChart, powerChart, energyChart;
let intervalId;

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
    statusEl.className = 'badge ' + (dev.status === 'online' ? 'bg-success' : 'bg-secondary');
  }
}

function statCard(title, unit, color, fields) {
  return `<div class="col-md-3 mb-3">
    <div class="card border-0 bg-dark h-100">
      <div class="card-body">
        <small class="text-muted text-uppercase">${title}</small>
        ${fields.map(f => `
          <div class="d-flex justify-content-between align-items-center py-1 border-bottom border-secondary border-opacity-25">
            <small class="text-secondary">${f.label}</small>
            <span class="text-${color} fw-semibold">${f.val} <small class="text-secondary fw-normal">${unit}</small></span>
          </div>`).join('')}
      </div>
    </div>
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
  tbody.innerHTML = measurements.slice(0, 50).map(r => `<tr>
    <td>${r.created_at ? new Date(r.created_at).toLocaleString() : ''}</td>
    <td>${toFixedSafe(r.bus_voltage, 3)}</td>
    <td>${toFixedSafe(r.shunt_voltage, 3)}</td>
    <td>${toFixedSafe(r.load_voltage, 3)}</td>
    <td>${(toFixedSafe(r.current, 3) * 1000).toFixed(2)} mA</td>
    <td>${(toFixedSafe(r.power, 3) * 1000).toFixed(2)} mW</td>
    <td>${toFixedSafe(r.energy, 6)}</td>
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
  const [dashboard, chart, recent] = await Promise.all([
    fetchJSON('/api/v1/dashboard'),
    fetchJSON('/api/v1/chart?limit=100'),
    fetchJSON('/api/v1/measurements?per_page=50'),
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
});
