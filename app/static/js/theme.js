(function() {
  var html = document.documentElement;
  var saved = localStorage.getItem('theme') || 'system';
  var mq = window.matchMedia('(prefers-color-scheme: dark)');

  function applyTheme(mode) {
    if (mode === 'dark') {
      html.classList.add('dark');
    } else if (mode === 'light') {
      html.classList.remove('dark');
    } else {
      if (mq.matches) {
        html.classList.add('dark');
      } else {
        html.classList.remove('dark');
      }
    }
  }

  applyTheme(saved);

  if (saved === 'system') {
    mq.addEventListener('change', function() { applyTheme('system'); });
  }

  var toggle = document.getElementById('theme-toggle');
  var path = document.getElementById('theme-path');

  var moon = 'M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z';
  var sun = 'M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z';
  var monitor = 'M8 21h8m-4-4v4m-7-6a2 2 0 01-2-2V5a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2H5z';

  function updateIcon(mode) {
    if (!path) return;
    if (mode === 'dark') { path.setAttribute('d', moon); }
    else if (mode === 'light') { path.setAttribute('d', sun); }
    else { path.setAttribute('d', monitor); }
  }

  updateIcon(saved);

  function nextMode(mode) {
    var modes = ['system', 'dark', 'light'];
    var idx = modes.indexOf(mode);
    return modes[(idx + 1) % modes.length];
  }

  if (toggle) {
    toggle.addEventListener('click', function() {
      var current = localStorage.getItem('theme') || 'system';
      var next = nextMode(current);
      localStorage.setItem('theme', next);
      applyTheme(next);
      updateIcon(next);
    });
  }

  var navToggle = document.getElementById('nav-toggle');
  var navMenu = document.getElementById('nav-menu');
  if (navToggle && navMenu) {
    navToggle.addEventListener('click', function() {
      navMenu.classList.toggle('hidden');
    });
  }
})();
