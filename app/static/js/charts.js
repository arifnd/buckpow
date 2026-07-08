const CHART_COLORS = {
  voltage: { border: '#58a6ff', bg: 'rgba(88, 166, 255, 0.1)' },
  current: { border: '#3fb950', bg: 'rgba(63, 185, 80, 0.1)' },
  power: { border: '#d29922', bg: 'rgba(210, 153, 34, 0.1)' },
  energy: { border: '#d2a8ff', bg: 'rgba(210, 168, 255, 0.1)' },
};

const CHART_OPTS = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false },
  },
  scales: {
    x: {
      ticks: { color: '#8b949e', maxTicksLimit: 8, font: { size: 13 } },
      grid: { color: '#21262d' },
    },
    y: {
      ticks: { color: '#8b949e', font: { size: 13 } },
      grid: { color: '#21262d' },
      beginAtZero: true,
    },
  },
};

function createChart(canvasId, label, colorKey) {
  const ctx = document.getElementById(canvasId).getContext('2d');
  const c = CHART_COLORS[colorKey];
  return new Chart(ctx, {
    type: 'line',
    data: {
      labels: [],
      datasets: [{
        label,
        data: [],
        borderColor: c.border,
        backgroundColor: c.bg,
        tension: 0.2,
        fill: true,
        pointRadius: 1,
        borderWidth: 2,
      }],
    },
    options: CHART_OPTS,
  });
}
