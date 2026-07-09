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

  function updateIcon(mode) {
    var el = document.getElementById('theme-icon');
    if (!el) return;
    if (mode === 'dark') { el.setAttribute('icon', 'heroicons-outline:moon'); }
    else if (mode === 'light') { el.setAttribute('icon', 'heroicons-outline:sun'); }
    else { el.setAttribute('icon', 'heroicons-outline:computer-desktop'); }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() { updateIcon(saved); });
  } else {
    updateIcon(saved);
  }

  if (saved === 'system') {
    mq.addEventListener('change', function() { applyTheme('system'); });
  }

  function nextMode(mode) {
    var modes = ['system', 'dark', 'light'];
    var idx = modes.indexOf(mode);
    return modes[(idx + 1) % modes.length];
  }

  document.addEventListener('click', function(e) {
    var btn = e.target.closest('#theme-toggle');
    if (btn) {
      var current = localStorage.getItem('theme') || 'system';
      var next = nextMode(current);
      localStorage.setItem('theme', next);
      applyTheme(next);
      updateIcon(next);
    }
  });

  document.addEventListener('click', function(e) {
    var btn = e.target.closest('#nav-toggle');
    if (btn) {
      var menu = document.getElementById('nav-menu');
      if (menu) menu.classList.toggle('hidden');
    }
  });

  document.addEventListener('htmx:afterSwap', function() {
    var mode = localStorage.getItem('theme') || 'system';
    applyTheme(mode);
    updateIcon(mode);
  });
})();
