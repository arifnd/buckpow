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
      if (mq.matches) { html.classList.add('dark'); }
      else { html.classList.remove('dark'); }
    }
  }

  function setTheme(mode) {
    localStorage.setItem('theme', mode);
    applyTheme(mode);
    updateChecks(mode);
    if (mode === 'system') {
      mq.addEventListener('change', function() { applyTheme('system'); });
    }
  }

  function updateChecks(mode) {
    document.querySelectorAll('.theme-option').forEach(function(el) {
      var check = el.querySelector('.theme-check');
      if (check) {
        check.classList.toggle('hidden', el.dataset.theme !== mode);
      }
    });
  }

  applyTheme(saved);

  document.addEventListener('DOMContentLoaded', function() { updateChecks(saved); });

  if (saved === 'system') {
    mq.addEventListener('change', function() { applyTheme('system'); });
  }

  document.addEventListener('click', function(e) {
    var item = e.target.closest('.theme-option');
    if (item) {
      setTheme(item.dataset.theme);
    }
  });

  document.addEventListener('htmx:afterSwap', function() {
    var mode = localStorage.getItem('theme') || 'system';
    applyTheme(mode);
    updateChecks(mode);
  });

  document.addEventListener('click', function(e) {
    var btn = e.target.closest('#nav-toggle');
    if (btn) {
      var menu = document.getElementById('nav-menu');
      if (menu) menu.classList.toggle('hidden');
    }
  });
})();
