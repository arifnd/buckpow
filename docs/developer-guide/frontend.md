# Frontend

Frontend architecture, templates, and JavaScript modules.

---

## Overview

BuckPow uses a server-rendered frontend with:

- **Jinja2** templates for HTML rendering
- **HTMX** for SPA-like page transitions
- **Tailwind CSS** for styling with dark mode
- **Chart.js** for real-time charts
- **Iconify** for icons

<!-- TODO: Replace with frontend architecture diagram -->

## Technology Stack

| Technology | Version | Purpose |
|-----------|---------|---------|
| **Jinja2** | 3.1+ | Server-side template engine |
| **HTMX** | 2.0.4 | SPA-like navigation |
| **Tailwind CSS** | CDN | Utility-first CSS |
| **Chart.js** | CDN | Interactive charts |
| **Iconify** | 2.1.0 | Icon library |
| **Flowbite Datepicker** | 1.3.1 | Date range picker |

## Directory Structure

```
app/
├── templates/
│   ├── base.html                    # Base layout
│   ├── _partials/
│   │   └── confirm_modal.html       # Reusable modal
│   ├── auth/
│   │   ├── login.html               # Login page
│   │   └── profile.html             # Profile editing
│   ├── dashboard/
│   │   └── index.html               # Main dashboard
│   ├── devices/
│   │   ├── index.html               # Device list
│   │   └── form.html                # Create/edit form
│   ├── sessions/
│   │   ├── index.html               # Session list
│   │   ├── form.html                # Create/edit form
│   │   └── detail.html              # Session details
│   ├── projects/
│   │   └── index.html               # Project list
│   ├── measurements/
│   │   └── index.html               # Measurements + export
│   ├── benchmark/
│   │   └── index.html               # Benchmark comparison
│   ├── alerts/
│   │   └── index.html               # Alert management
│   ├── settings/
│   │   └── index.html               # User settings
│   └── audit/
│       └── index.html               # Audit log viewer
└── static/
    ├── css/
    │   └── style.css                # Custom styles
    └── js/
        ├── format.js               # Unit formatting (fmtCurrent, fmtPower, fmtEnergy)
        ├── dashboard.js             # Dashboard logic
        ├── benchmark.js             # Benchmark logic
        ├── charts.js                # Chart.js factory
        ├── theme.js                 # Theme toggle
        └── timestamp.js             # Time formatting
```

## Base Template

All pages extend `base.html` which provides:

### Head Section

```html
<!-- CDN dependencies -->
<script src="https://cdn.tailwindcss.com"></script>
<script src="https://unpkg.com/htmx.org@2.0.4"></script>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script src="https://cdn.jsdelivr.net/npm/iconify-icon@2.1.0"></script>
<script src="https://cdn.jsdelivr.net/npm/flowbite-datepicker@1.3.1"></script>

<!-- User settings for JS -->
<script>
  window.__userTimestampFormat = '24h';
  window.__userDateFormat = 'YYYY-MM-DD';
  window.__userTimezone = '+0';
</script>
```

### Layout

```html
<body class="flex h-screen bg-gray-50 dark:bg-gray-950">
  <!-- Sidebar (authenticated only) -->
  <aside id="sidebar">...</aside>

  <!-- Main content -->
  <div class="flex-1 flex flex-col">
    <header>...</header>
    <main>
      {% block content %}{% endblock %}
      {% block extra_scripts %}{% endblock %}
    </main>
    <footer>...</footer>
  </div>
</body>
```

### Template Blocks

| Block | Purpose |
|-------|---------|
| `content` | Main page content |
| `extra_scripts` | Page-specific JavaScript |
| `extra_head` | Page-specific head elements |

## HTMX Integration

### SPA-Like Navigation

The `<body>` tag uses `hx-boost="true"` for automatic page transitions:

```html
<body hx-boost="true">
  <!-- All links load pages without full refresh -->
  <a href="/devices">Devices</a>
</body>
```

### API Polling

Dashboard uses `hx-trigger` for real-time updates:

```html
<div hx-get="/api/v1/dashboard" hx-trigger="every 5s">
  <!-- Auto-refreshes every 5 seconds -->
</div>
```

### JavaScript Re-evaluation

After HTMX swaps content, JavaScript re-initializes:

```javascript
document.addEventListener('htmx:afterSettle', function() {
  // Re-initialize page-specific JS
  initDashboard();
});
```

## Dark Mode

### Theme Toggle

Three modes available:

| Mode | Behavior |
|------|----------|
| **System** | Follows OS preference |
| **Light** | Always light theme |
| **Dark** | Always dark theme |

### Implementation

```javascript
// theme.js
function setTheme(theme) {
  if (theme === 'dark' || (theme === 'system' && isDark())) {
    document.documentElement.classList.add('dark');
  } else {
    document.documentElement.classList.remove('dark');
  }
  localStorage.setItem('theme', theme);
}
```

### Tailwind Configuration

```html
<script>
  window.tailwind.config = { darkMode: 'class' };
</script>
```

Dark mode uses the `dark` class on `<html>`:

```css
/* Tailwind utilities */
bg-white dark:bg-gray-900
text-gray-900 dark:text-gray-300
border-gray-200 dark:border-gray-800
```

## Chart.js

### Chart Factory

```javascript
// charts.js
function createChart(canvasId, label, colorKey, beginAtZero = true) {
  return new Chart(ctx, {
    type: 'line',
    data: { labels: [], datasets: [{ ... }] },
    options: { responsive: true, ... }
  });
}
```

### Color Scheme

| Chart | Border Color | Background |
|-------|-------------|------------|
| Voltage | `#58a6ff` (blue) | `rgba(88, 166, 255, 0.1)` |
| Current | `#3fb950` (green) | `rgba(63, 185, 80, 0.1)` |
| Power | `#d29922` (yellow) | `rgba(210, 153, 34, 0.1)` |
| Energy | `#d2a8ff` (purple) | `rgba(210, 168, 255, 0.1)` |

### Dashboard Charts

Four charts update every 5 seconds:

```javascript
// dashboard.js
function initCharts() {
  voltageChart = createChart('voltageChart', 'Voltage (V)', 'voltage');
  currentChart = createChart('currentChart', 'Current (A)', 'current');
  powerChart = createChart('powerChart', 'Power (W)', 'power');
  energyChart = createChart('energyChart', 'Energy (Wh)', 'energy', false);
}
```

### Benchmark Overlay Chart

Compares multiple sessions on the same axis:

```javascript
// benchmark.js
function renderOverlayChart(sessions) {
  const colors = ['#58a6ff', '#f85149', '#3fb950'];
  const datasets = sessions.map((s, i) => ({
    label: s.session_name,
    data: s.chart_data.power,
    borderColor: colors[i],
  }));
}
```

## Timestamps

### User Settings

Timezone and format are injected from user settings:

```javascript
window.__userTimestampFormat = '24h';  // or '12h'
window.__userDateFormat = 'YYYY-MM-DD';  // or 'DD/MM/YYYY', 'MM/DD/YYYY'
window.__userTimezone = '+0';  // offset in hours
```

### Formatting

```javascript
// timestamp.js
function formatTimestamp(isoString) {
  // Applies timezone offset and format preference
  // Returns formatted string like "10:30:00" or "10:30 PM"
}

function formatRelativeTime(isoString) {
  // Returns "5s ago", "2m ago", "1h ago"
}
```

## Iconify Icons

Icons use the `<iconify-icon>` web component:

```html
<iconify-icon icon="heroicons-outline:home" width="20" height="20"></iconify-icon>
```

### Navigation Icons

| Page | Icon |
|------|------|
| Dashboard | `heroicons-outline:home` |
| Devices | `heroicons-outline:cpu-chip` |
| Sessions | `heroicons-outline:clock` |
| Projects | `heroicons-outline:folder-open` |
| Measurements | `heroicons-outline:chart-pie` |
| Benchmark | `heroicons-outline:scale` |
| Alerts | `heroicons-outline:bell` |
| Audit | `heroicons-outline:clipboard-list` |

## Responsive Design

### Breakpoints

| Breakpoint | Behavior |
|------------|----------|
| `< 768px` | Mobile: hamburger menu, stacked layout |
| `≥ 768px` | Desktop: sidebar visible, multi-column |

### Mobile Sidebar

```javascript
function toggleSidebar() {
  const sidebar = document.getElementById('sidebar');
  sidebar.classList.toggle('-translate-x-full');
}
```

### Responsive Utilities

```html
<!-- Hide on mobile, show on desktop -->
<div class="hidden md:block">Desktop only</div>

<!-- Show on mobile, hide on desktop -->
<button class="md:hidden">Mobile only</button>
```

## Custom CSS

Minimal custom styles in `app/static/css/style.css`:

```css
html {
  font-size: 17px;
}

.chart-container {
  position: relative;
  height: 220px;
}

/* Custom scrollbar */
::-webkit-scrollbar {
  width: 8px;
}
::-webkit-scrollbar-thumb {
  background: #30363d;
  border-radius: 4px;
}
```

## Adding a New Page

### 1. Create Template

```html
<!-- app/templates/my-page/index.html -->
{% extends "base.html" %}

{% block content %}
<h2 class="text-xl font-semibold mb-4">My Page</h2>
<!-- Page content -->
{% endblock %}

{% block extra_scripts %}
<script>
// Page-specific JavaScript
</script>
{% endblock %}
```

### 2. Add Route

```python
# app/dashboard/routes.py
@dashboard_router.get('/my-page')
def my_page(current_user: User | None = Depends(get_current_user)):
    redir = _require_dashboard_user(current_user)
    if isinstance(redir, RedirectResponse):
        return redir
    return HTMLResponse(
        _render('my-page/index.html', current_user=current_user, active_page='my-page')
    )
```

### 3. Add Navigation

```python
# app/templates/base.html
{% set nav_items = [
  ...
  ('/my-page', 'my-page', 'heroicons-outline:icon-name', 'My Page'),
] %}
```

## Performance

### CDN Dependencies

All frontend libraries are loaded from CDN:

- No local bundling required
- Automatic version pinning
- Browser caching across pages

### HTMX Optimization

- `hx-boost="true"` enables SPA-like transitions
- Only the `<main>` content is swapped (not the full page)
- JavaScript re-initializes via `htmx:afterSettle` event

### Chart Updates

- Charts update every 5 seconds (dashboard)
- Statistics update every 30 seconds
- Summary updates every 30 seconds
- Maximum 50 data points per chart (`MAX_POINTS`)

## Browser Support

| Browser | Version |
|---------|---------|
| Chrome | 90+ |
| Firefox | 88+ |
| Safari | 14+ |
| Edge | 90+ |

!!! note "IE11 not supported"
    HTMX and modern CSS features require a modern browser.
