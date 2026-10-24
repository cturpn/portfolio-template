'use strict';

// Shared behaviour for every theme. Each block only runs when its markup is on the page.
(function () {
  var root = document.documentElement;
  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // Light / dark toggle (themes that offer one)
  var themeBtn = document.getElementById('themeToggle');
  if (themeBtn) {
    themeBtn.addEventListener('click', function () {
      var next = root.getAttribute('data-theme') === 'light' ? 'dark' : 'light';
      root.setAttribute('data-theme', next);
      try { localStorage.setItem('theme', next); } catch (e) {}
    });
  }

  // Mobile menu
  var menuBtn = document.getElementById('menuBtn');
  var links = document.getElementById('navLinks');
  if (menuBtn && links) {
    menuBtn.addEventListener('click', function () {
      var open = links.classList.toggle('open');
      menuBtn.setAttribute('aria-expanded', String(open));
      menuBtn.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
    });
  }

  // Nav border + back-to-top
  var nav = document.getElementById('nav');
  var toTop = document.getElementById('toTop');
  function onScroll() {
    var y = window.scrollY;
    if (nav) nav.classList.toggle('scrolled', y > 8);
    if (toTop) toTop.classList.toggle('show', y > 600);
  }
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();
  if (toTop) toTop.addEventListener('click', function () { window.scrollTo({ top: 0, behavior: reduced ? 'auto' : 'smooth' }); });

  // Flash messages
  document.querySelectorAll('.flash').forEach(function (el) {
    function close() { el.classList.add('closing'); setTimeout(function () { el.remove(); }, 300); }
    var t = setTimeout(close, 6000);
    el.querySelector('button').addEventListener('click', function () { clearTimeout(t); close(); });
  });

  // Count-up numbers: <span data-count="54" data-suffix="+">54</span>
  function countUp(el) {
    var target = +el.getAttribute('data-count');
    var suffix = el.getAttribute('data-suffix') || '';
    if (reduced || !target) { el.textContent = target + suffix; return; }
    var start = null, dur = 1200;
    function step(t) {
      if (!start) start = t;
      var p = Math.min((t - start) / dur, 1);
      el.textContent = Math.round(target * (1 - Math.pow(1 - p, 3))) + (p === 1 ? suffix : '');
      if (p < 1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
  }

  // Reveal on scroll (+ start count-ups when they come into view)
  var watched = document.querySelectorAll('.reveal, [data-count]');
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (!e.isIntersecting) return;
        if (e.target.hasAttribute('data-count')) countUp(e.target);
        e.target.classList.add('in');
        io.unobserve(e.target);
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });
    watched.forEach(function (el) { io.observe(el); });
  } else {
    watched.forEach(function (el) { el.classList.add('in'); });
  }

  // Screenshot carousels
  if (!reduced) {
    document.querySelectorAll('[data-slides]').forEach(function (wrap) {
      var slides = wrap.querySelectorAll('img');
      var dots = wrap.querySelectorAll('.slide-dots span');
      if (slides.length < 2) return;
      var i = 0;
      setInterval(function () {
        slides[i].classList.remove('is-active');
        if (dots[i]) dots[i].classList.remove('is-active');
        i = (i + 1) % slides.length;
        slides[i].classList.add('is-active');
        if (dots[i]) dots[i].classList.add('is-active');
      }, 3800);
    });
  }

  // Project filters: buttons [data-filter], items [data-group]
  var filterBtns = document.querySelectorAll('.filter-btn[data-filter]');
  filterBtns.forEach(function (btn) {
    btn.addEventListener('click', function () {
      var f = btn.getAttribute('data-filter');
      filterBtns.forEach(function (b) { b.setAttribute('aria-pressed', String(b === btn)); });
      document.querySelectorAll('[data-group]').forEach(function (item) {
        item.hidden = !(f === 'all' || item.getAttribute('data-group') === f);
      });
    });
  });

  // Contact form character counter
  var msg = document.getElementById('message');
  var count = document.getElementById('charCount');
  if (msg && count) {
    msg.addEventListener('input', function () {
      count.textContent = msg.value.length;
      count.parentNode.classList.toggle('near-limit', msg.value.length > 1900);
    });
  }

  // Site assistant
  var form = document.getElementById('chatForm');
  if (form) {
    var input = document.getElementById('chatInput');
    var log = document.getElementById('chatLog');
    var suggest = document.getElementById('chatSuggest');
    var tokenMeta = document.querySelector('meta[name="csrf-token"]');
    var fallback = 'Sorry, I could not answer that. Please use the contact page.';

    var add = function (text, cls) {
      var el = document.createElement('div');
      el.className = 'msg ' + cls;
      el.textContent = text;
      log.appendChild(el);
      log.scrollTop = log.scrollHeight;
      return el;
    };

    var ask = async function (q) {
      add(q, 'user');
      if (suggest) { suggest.remove(); suggest = null; }
      var pending = add('Typing…', 'bot typing');
      try {
        var res = await fetch('/api/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'X-CSRFToken': tokenMeta ? tokenMeta.content : '' },
          body: JSON.stringify({ message: q })
        });
        var data = await res.json();
        pending.remove();
        add(data.reply || data.error || fallback, 'bot');
      } catch (e) {
        pending.remove();
        add('Connection problem. Please try again.', 'bot error');
      }
    };

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var q = input.value.trim();
      if (!q) return;
      input.value = '';
      ask(q);
    });
    if (suggest) {
      suggest.querySelectorAll('button').forEach(function (b) {
        b.addEventListener('click', function () { ask(b.textContent); });
      });
    }
  }
})();
