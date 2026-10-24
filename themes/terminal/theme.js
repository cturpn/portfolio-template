'use strict';

// Terminal theme: matrix rain behind the page.
// Throttled to ~20 fps, paused while the tab is hidden, skipped for reduced motion.
(function () {
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

  var canvas = document.createElement('canvas');
  canvas.className = 'matrix';
  canvas.setAttribute('aria-hidden', 'true');
  document.body.prepend(canvas);

  var ctx = canvas.getContext('2d');
  var chars = '01アイウエオカキクケコABCDEF{}[];></>';
  var size = 18, drops = [], last = 0, frame = null;

  var resize = function () {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    drops = Array.from({ length: Math.floor(canvas.width / size) }, function () { return Math.random() * -100; });
  };

  var draw = function (t) {
    frame = requestAnimationFrame(draw);
    if (t - last < 50) return;
    last = t;
    ctx.fillStyle = 'rgba(3,7,18,0.05)';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = '#00ff88';
    ctx.font = '14px "Share Tech Mono", monospace';
    for (var i = 0; i < drops.length; i++) {
      ctx.fillText(chars[Math.floor(Math.random() * chars.length)], i * size, drops[i] * size);
      if (drops[i] * size > canvas.height && Math.random() > 0.975) drops[i] = 0;
      drops[i] += 0.5;
    }
  };

  resize();
  window.addEventListener('resize', resize);
  document.addEventListener('visibilitychange', function () {
    if (document.hidden) { cancelAnimationFrame(frame); frame = null; }
    else if (!frame) frame = requestAnimationFrame(draw);
  });
  frame = requestAnimationFrame(draw);
})();
