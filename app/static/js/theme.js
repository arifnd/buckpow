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
  var icon = document.getElementById('theme-icon');

  function updateIcon(mode) {
    if (!icon) return;
    if (mode === 'dark') { icon.setAttribute('icon', 'heroicons-outline:moon'); }
    else if (mode === 'light') { icon.setAttribute('icon', 'heroicons-outline:sun'); }
    else { icon.setAttribute('icon', 'heroicons-outline:computer-desktop'); }
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
