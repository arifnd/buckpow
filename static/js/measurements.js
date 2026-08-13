var currentPage = 1;

function getFilterParams() {
  const p = new URLSearchParams();
  const d = document.getElementById('filter-device').value;
  const s = document.getElementById('filter-session').value;
  const f = document.getElementById('filter-from').value;
  const t = document.getElementById('filter-to').value;
  if (d) p.set('device_id', d);
  if (s) p.set('session_id', s);
  if (f) p.set('start_date', f);
  if (t) p.set('end_date', t);
  if (f || t) p.set('tz', window.__userTimezone || '+0');
  return p;
}

async function loadMeasurements(page) {
  page = page || 1;
  const params = getFilterParams();
  params.set('page', page);
  params.set('per_page', 10);
  const res = await fetch(`/api/v1/measurements?${params}`);
  const data = await res.json();

  const tbody = document.getElementById('measurements-body');
  tbody.innerHTML = data.measurements.map(m => `<tr class="border-b border-gray-200 dark:border-gray-800 hover:bg-gray-100 dark:hover:bg-gray-800">
    <td class="py-2 px-2">${m.device_name || m.device_id}</td>
    <td class="py-2 px-2">${m.session_name || '\u2014'}</td>
    <td class="py-2 px-2 text-right">${m.bus_voltage.toFixed(3)} V</td>
    <td class="py-2 px-2 text-right">${fmtCurrent(m.current)}</td>
    <td class="py-2 px-2 text-right">${fmtPower(m.power)}</td>
    <td class="py-2 px-2 text-right">${fmtEnergy(m.energy)}</td>
    <td class="py-2 px-2">${formatTimestamp(m.created_at)}</td>
  </tr>`).join('');

  const pagination = document.getElementById('pagination');
  const p = data.page, total = data.pages;
  pagination.parentElement.style.display = total <= 1 ? 'none' : '';
  let html = `<li><a class="flex items-center justify-center w-7 h-7 rounded text-xs ${p <= 1 ? 'text-gray-500 pointer-events-none' : 'text-gray-900 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800'} border border-gray-300 dark:border-gray-700 transition-colors" href="#" onclick="loadMeasurements(${p - 1}); return false;">&laquo;</a></li>`;
  let pages = new Set([1, total]);
  for (let i = Math.max(2, p - 2); i <= Math.min(total - 1, p + 2); i++) pages.add(i);
  [...pages].sort((a, b) => a - b).forEach((n, i, arr) => {
    if (i > 0 && n - arr[i - 1] > 1) html += '<li><span class="flex items-center justify-center w-7 h-7 text-xs text-gray-500">&hellip;</span></li>';
    html += `<li><a class="flex items-center justify-center w-7 h-7 rounded text-xs border border-gray-300 dark:border-gray-700 transition-colors ${n === p ? 'bg-blue-600 border-blue-600 text-white' : 'text-gray-900 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800'}" href="#" onclick="loadMeasurements(${n}); return false;">${n}</a></li>`;
  });
  html += `<li><a class="flex items-center justify-center w-7 h-7 rounded text-xs ${p >= total ? 'text-gray-500 pointer-events-none' : 'text-gray-900 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800'} border border-gray-300 dark:border-gray-700 transition-colors" href="#" onclick="loadMeasurements(${p + 1}); return false;">&raquo;</a></li>`;
  pagination.innerHTML = html;
  currentPage = p;
}

async function loadFilterOptions() {
  const [devices, sessions] = await Promise.all([
    fetch('/api/v1/devices?page=0').then(r => r.json()),
    fetch('/api/v1/sessions?page=0').then(r => r.json()),
  ]);
  const deviceSel = document.getElementById('filter-device');
  deviceSel.innerHTML = '<option value="">All</option>';
  devices.forEach(d => {
    const opt = document.createElement('option');
    opt.value = d.id;
    opt.textContent = d.alias || d.device_id;
    deviceSel.appendChild(opt);
  });
  const sessionSel = document.getElementById('filter-session');
  sessionSel.innerHTML = '<option value="">All</option>';
  sessions.forEach(s => {
    const opt = document.createElement('option');
    opt.value = s.id;
    opt.textContent = s.name;
    sessionSel.appendChild(opt);
  });
}

function initMeasurements() {
  var fromEl = document.getElementById('filter-from');
  var toEl = document.getElementById('filter-to');
  if (!fromEl || !toEl) return;

  loadFilterOptions();
  loadMeasurements(1);

  document.getElementById('filter-form').addEventListener('submit', function(e) {
    e.preventDefault();
    loadMeasurements(1);
  });
  document.getElementById('reset-filters').addEventListener('click', function() {
    document.getElementById('filter-device').value = '';
    document.getElementById('filter-session').value = '';
    fromEl.value = '';
    toEl.value = '';
    loadMeasurements(1);
  });
  document.getElementById('download-csv').addEventListener('click', function() {
    window.location.href = '/api/v1/measurements/export/csv?' + getFilterParams().toString();
  });
  document.getElementById('download-xlsx').addEventListener('click', function() {
    window.location.href = '/api/v1/measurements/export/xlsx?' + getFilterParams().toString();
  });
}

if (document.getElementById('measurements-body')) initMeasurements();
document.addEventListener('htmx:afterSettle', function() {
  if (document.getElementById('filter-from') && !document.getElementById('measurements-body')) {
    initMeasurements();
  }
});
