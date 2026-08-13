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
templates/
├── base.html                    # Base layout
├── _partials/
│   └── confirm_modal.html       # Reusable modal
├── auth/
│   ├── login.html               # Login page
│   └── profile.html             # Profile editing
├── dashboard/
│   └── index.html               # Main dashboard
├── devices/
│   ├── index.html               # Device list
│   └── form.html                # Create/edit form
├── sessions/
│   ├── index.html               # Session list
│   ├── form.html                # Create/edit form
│   └── detail.html              # Session details
├── projects/
│   └── index.html               # Project list
├── measurements/
│   └── index.html               # Measurements + export
├── benchmark/
│   └── index.html               # Benchmark comparison
├── alerts/
│   └── index.html               # Alert management
├── settings/
│   └── index.html               # User settings
└── audit/
    └── index.html               # Audit log viewer

static/
├── css/
│   └── app.css                   # Compiled Tailwind + custom styles
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
<!-- Compiled stylesheet -->
<link rel="stylesheet" href="{{ url_for('static', filename='css/app.css') }}">

<!-- CDN dependencies -->
<script src="https://unpkg.com/htmx.org@2.0.4"></script>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script defer src="https://unpkg.com/alpinejs@3.14.1/dist/cdn.min.js"></script>

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

### CSRF Handling

HTMX is wired up once in `base.html` to attach the CSRF token to every request:

```html
<script>
  htmx.on('htmx:configRequest', function(evt) {
    evt.detail.headers['X-CSRF-Token'] = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
  });
</script>
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

## Inline SVG Icons

Icons use inline SVG with heroicons v2 outline paths (24×24, `stroke-width="1.5"`), sized with Tailwind `w-*`/`h-*` classes:

```html
<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-5 h-5">
  <path stroke-linecap="round" stroke-linejoin="round" d="M2.25 12l8.954-8.955c.44-.439 1.152-.439 1.591 0L21.75 12M4.5 9.75v10.125c0 .621.504 1.125 1.125 1.125H9.75v-4.875c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125V21h4.125c.621 0 1.125-.504 1.125-1.125V9.75M8.25 21h8.25"></path>
</svg>
```

Brand icons that need a filled appearance (e.g. the GitHub footer icon) use `fill="currentColor"` with no `stroke`.

### Navigation Icons

Sidebar navigation icons are defined in the `nav_icons` map in `base.html`, keyed by name:

| Page | Icon key | Heroicon |
|------|----------|----------|
| Dashboard | `home` | home |
| Devices | `cpu-chip` | cpu-chip |
| Sessions | `clock` | clock |
| Projects | `folder-open` | folder-open |
| Measurements | `chart-pie` | chart-pie |
| Benchmark | `scale` | scale |
| Alerts | `bell` | bell |
| Audit | `clipboard-list` | clipboard-list |

## Responsive Design

### Breakpoints

| Breakpoint | Behavior |
|------------|----------|
| `< 768px` | Mobile: hamburger menu, stacked layout |
| `≥ 768px` | Desktop: sidebar visible, multi-column |

### Mobile Sidebar

The off-canvas sidebar is toggled with Alpine.js state on the `<body>`:

```html
<body x-data="{ sidebarOpen: false }">
  <aside
    x-cloak
    x-bind:class="sidebarOpen ? 'translate-x-0' : '-translate-x-full'"
    class="fixed ... w-72 md:!translate-x-0">
    ...
  </aside>
  <button @click="sidebarOpen = !sidebarOpen">...</button>
</body>
```

The `md:!translate-x-0` important variant keeps the sidebar visible on desktop; `x-cloak` prevents a flash before Alpine initializes.

### Responsive Utilities

```html
<!-- Hide on mobile, show on desktop -->
<div class="hidden md:block">Desktop only</div>

<!-- Show on mobile, hide on desktop -->
<button class="md:hidden">Mobile only</button>
```

## Custom CSS

Add custom styles to the Tailwind source at `resources/css/app.css`, then rebuild with `npm run build:css` (or `npm run watch:css` during development). The compiled output is served at `static/css/app.css`:

```css
/* resources/css/app.css */
@tailwind base;
@tailwind components;
@tailwind utilities;

/* Custom components/overrides go here */
```

Chart canvases are sized with utility classes directly on the wrapper — no custom CSS class needed:

```html
<div class="relative h-[220px]"><canvas id="voltageChart"></canvas></div>
```

> The compiled `static/css/app.css` must be committed — it is generated by Tailwind's JIT from the classes found in `templates/**/*.html` and `static/js/**/*.js`.

## Adding a New Page

### 1. Create Template

```html
<!-- templates/my-page/index.html -->
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
# src/dashboard/ (page route file per domain)
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
# templates/base.html
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

- The CSRF token is injected on every request via `htmx:configRequest`
- Interactive UI (sidebar, dropdowns, theme submenu) is handled by Alpine.js
- JavaScript re-initializes via `htmx:afterSwap`/`htmx:afterSettle` events

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
