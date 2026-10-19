/* Ebenezer Educational Centre - public site interactions */
(function () {
  "use strict";

  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var isMobile = window.matchMedia("(max-width: 991.98px)").matches;

  /* Expose device class so CSS can scope desktop-only animations. */
  if (isMobile) {
    document.documentElement.classList.add("ec-mobile");
  } else {
    document.documentElement.classList.remove("ec-mobile");
  }
  window.matchMedia("(max-width: 991.98px)").addEventListener("change", function (e) {
    isMobile = e.matches;
    if (isMobile) {
      document.documentElement.classList.add("ec-mobile");
    } else {
      document.documentElement.classList.remove("ec-mobile");
    }
  });

  /* Sticky navigation shadow */
  function initNav() {
    var nav = document.querySelector(".ec-nav");
    if (!nav) return;
    var onScroll = function () {
      nav.classList.toggle("scrolled", window.scrollY > 12);
    };
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
  }

  /* Hero slideshow */
  function initHero() {
    var hero = document.querySelector("[data-hero]");
    if (!hero) return;
    var slides = Array.prototype.slice.call(hero.querySelectorAll(".hero-slide"));
    var dots = Array.prototype.slice.call(hero.querySelectorAll(".hero-dots button"));
    var captions = Array.prototype.slice.call(
      hero.querySelectorAll(".hero-caption[data-slide-index]")
    );
    if (slides.length < 2) return;
    var index = slides.findIndex(function (s) { return s.classList.contains("active"); });
    if (index < 0) index = 0;
    var timer = null;
    var interval = parseInt(hero.dataset.interval || "6000", 10);

    function show(next) {
      slides.forEach(function (s, i) { s.classList.toggle("active", i === next); });
      dots.forEach(function (d, i) {
        d.classList.toggle("active", i === next);
        d.setAttribute("aria-selected", i === next ? "true" : "false");
      });
      captions.forEach(function (c, i) {
        if (i === next) {
          c.removeAttribute("hidden");
          var heading = c.querySelector("h1[data-typewriter]");
          if (heading) typewriter(heading);
        } else {
          c.setAttribute("hidden", "");
        }
      });
      index = next;
    }
    function next() { show((index + 1) % slides.length); }
    function prev() { show((index - 1 + slides.length) % slides.length); }
    function start() {
      if (reduceMotion) return;
      stop();
      timer = window.setInterval(next, interval);
    }
    function stop() { if (timer) window.clearInterval(timer); timer = null; }

    var nextBtn = hero.querySelector("[data-hero-next]");
    var prevBtn = hero.querySelector("[data-hero-prev]");
    if (nextBtn) nextBtn.addEventListener("click", function () { next(); start(); });
    if (prevBtn) prevBtn.addEventListener("click", function () { prev(); start(); });
    dots.forEach(function (d, i) {
      d.addEventListener("click", function () { show(i); start(); });
    });
    hero.addEventListener("mouseenter", stop);
    hero.addEventListener("mouseleave", start);
    document.addEventListener("visibilitychange", function () {
      if (document.hidden) stop(); else start();
    });
    show(index);
    start();
  }

  /* Reveal on scroll (auto-marks sections + staggered delays) */
  var AUTO_REVEAL =
    ".section .section-head, .section .ec-card, .section .field-card, " +
    ".section .stat-badge, .section .media-split > *, .section .teacher-card, " +
    ".section .gallery-item, .section .aspect-placeholder, .section .rounded-img, " +
    ".section .list-unstyled, .section .row > .col-md-4, .page-hero .container-ec > *";

  function initReveal() {
    Array.prototype.slice.call(document.querySelectorAll(AUTO_REVEAL)).forEach(function (el) {
      if (el.classList.contains("reveal") || el.closest(".reveal")) return;
      el.classList.add("reveal");
    });

    var els = Array.prototype.slice.call(document.querySelectorAll(".reveal"));
    if (!els.length) return;
    if (reduceMotion || isMobile || !("IntersectionObserver" in window)) {
      els.forEach(function (el) { el.classList.add("in"); });
      return;
    }

    /* stagger siblings that share a parent */
    var groups = {};
    els.forEach(function (el) {
      var key = el.parentElement ? (el.parentElement.className || "root") : "root";
      groups[key] = groups[key] || [];
      var i = groups[key].indexOf(el);
      if (i < 0) { groups[key].push(el); i = groups[key].length - 1; }
      el.style.transitionDelay = Math.min(i, 6) * 90 + "ms";
    });

    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add("in");
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12, rootMargin: "0px 0px -40px 0px" });
    els.forEach(function (el) { observer.observe(el); });
  }

  /* Hero particle field */
  function initHeroParticles() {
    var canvas = document.querySelector("[data-hero-particles]");
    var hero = canvas && canvas.closest("[data-hero]");
    if (!canvas || !hero || reduceMotion || isMobile) return;
    var ctx = canvas.getContext("2d");
    if (!ctx) return;

    var css = getComputedStyle(document.documentElement);
    var palette = [
      "rgba(255,255,255,",
      (css.getPropertyValue("--ec-accent") || "#d5720a").trim() + ","
    ];
    var particles = [];
    var raf = null;
    var running = false;
    var w = 0;
    var h = 0;

    function resize() {
      var rect = hero.getBoundingClientRect();
      var dpr = Math.min(window.devicePixelRatio || 1, 2);
      w = Math.max(1, Math.round(rect.width));
      h = Math.max(1, Math.round(rect.height));
      canvas.width = Math.round(w * dpr);
      canvas.height = Math.round(h * dpr);
      canvas.style.width = w + "px";
      canvas.style.height = h + "px";
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      seed();
    }

    function seed() {
      var count = Math.min(130, Math.max(60, Math.round((w * h) / 11000)));
      particles = [];
      for (var i = 0; i < count; i++) {
        particles.push({
          x: Math.random() * w,
          y: Math.random() * h,
          r: 1 + Math.random() * 2.6,
          vx: (Math.random() - 0.5) * 0.35,
          vy: -0.15 - Math.random() * 0.45,
          a: 0.15 + Math.random() * 0.45,
          phase: Math.random() * Math.PI * 2,
          speed: 0.6 + Math.random() * 1.4,
          color: palette[Math.random() < 0.65 ? 0 : 1]
        });
      }
    }

    function draw(t) {
      ctx.clearRect(0, 0, w, h);
      for (var i = 0; i < particles.length; i++) {
        var p = particles[i];
        p.x += p.vx;
        p.y += p.vy;
        if (p.y < -8) { p.y = h + 8; p.x = Math.random() * w; }
        if (p.x < -8) p.x = w + 8;
        if (p.x > w + 8) p.x = -8;
        var alpha = p.a * (0.6 + 0.4 * Math.sin(t / 1000 * p.speed + p.phase));
        ctx.beginPath();
        ctx.fillStyle = p.color + alpha.toFixed(3) + ")";
        ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
        ctx.fill();
      }
    }

    function loop(t) {
      if (!running) return;
      draw(t || 0);
      raf = window.requestAnimationFrame(loop);
    }
    function start() {
      if (running) return;
      running = true;
      raf = window.requestAnimationFrame(loop);
    }
    function stop() {
      running = false;
      if (raf) window.cancelAnimationFrame(raf);
      raf = null;
    }

    resize();
    start();
    window.addEventListener("resize", resize);
    document.addEventListener("visibilitychange", function () {
      if (document.hidden) stop(); else start();
    });
    if ("IntersectionObserver" in window) {
      new IntersectionObserver(function (entries) {
        entries.forEach(function (e) {
          if (e.isIntersecting) start(); else stop();
        });
      }, { threshold: 0 }).observe(hero);
    }
  }

  /* Typewriter effect for a single [data-typewriter] heading */
  function typewriter(el) {
    var text = (el.textContent || "").trim();
    if (!text) return;
    el.setAttribute("aria-label", text);
    if (reduceMotion) return;

    var previous = el.querySelector(".tw-caret");
    if (previous) previous.remove();
    var previousTimer = parseInt(el.getAttribute("data-tw-timer") || "0", 10);
    if (previousTimer) window.clearInterval(previousTimer);
    el.removeAttribute("data-tw-timer");

    el.textContent = "";
    var caret = document.createElement("span");
    caret.className = "tw-caret";
    caret.setAttribute("aria-hidden", "true");
    el.appendChild(caret);

    var i = 0;
    var timer = window.setInterval(function () {
      i++;
      if (!el.firstChild || el.firstChild.nodeType !== 3) {
        el.insertBefore(document.createTextNode(text.slice(0, i)), caret);
      } else {
        el.firstChild.textContent = text.slice(0, i);
      }
      if (i >= text.length) {
        window.clearInterval(timer);
        el.removeAttribute("data-tw-timer");
        window.setTimeout(function () { caret.remove(); }, 1600);
      }
    }, 55);
    el.setAttribute("data-tw-timer", timer);
  }

  function initTypewriter() {
    var els = Array.prototype.slice.call(document.querySelectorAll("[data-typewriter]"));
    els.forEach(function (el) {
      /* only type the caption that is visible on load */
      if (el.hasAttribute("hidden") || el.closest("[hidden]")) return;
      /* initHero().show() already started typing the initially active slide */
      if (el.querySelector(".tw-caret") || el.getAttribute("data-tw-timer")) return;
      typewriter(el);
    });
  }

  /* Gallery lightbox */
  function initLightbox() {
    var items = Array.prototype.slice.call(document.querySelectorAll("[data-lightbox] img, [data-lightbox] video"));
    if (!items.length) return;
    var overlay = document.createElement("div");
    overlay.className = "lightbox";
    overlay.setAttribute("role", "dialog");
    overlay.setAttribute("aria-modal", "true");
    overlay.setAttribute("aria-label", "Media viewer");
    overlay.innerHTML =
      '<button class="lb-close" aria-label="Close">&times;</button>' +
      '<button class="lb-prev" aria-label="Previous media">&#8249;</button>' +
      '<button class="lb-next" aria-label="Next media">&#8250;</button>' +
      '<figure class="m-0 text-center"><img alt=""><video controls alt="" style="display:none;"></video><figcaption class="lb-caption"></figcaption></figure>';
    document.body.appendChild(overlay);

    var mediaImg = overlay.querySelector("img");
    var mediaVideo = overlay.querySelector("video");
    var caption = overlay.querySelector(".lb-caption");
    var current = 0;

    function stopCurrentMedia() {
      if (mediaVideo) mediaVideo.pause();
      mediaImg.style.display = "none";
      mediaVideo.style.display = "none";
      mediaImg.src = "";
      mediaVideo.src = "";
      mediaImg.removeAttribute("poster");
      mediaVideo.removeAttribute("poster");
    }

    function render(i) {
      current = (i + items.length) % items.length;
      var source = items[current];
      stopCurrentMedia();
      caption.textContent = source.dataset.caption || source.alt || "";
      if (source.tagName.toLowerCase() === "video") {
        mediaVideo.src = source.src;
        mediaVideo.poster = source.poster || "";
        mediaVideo.style.display = "block";
        mediaVideo.load();
        mediaVideo.play().catch(function () { /* autoplay may be blocked by browser; user can press play */ });
      } else {
        mediaImg.src = source.src;
        mediaImg.alt = source.alt || "";
        mediaImg.style.display = "block";
      }
    }
    function open(i) {
      // Pause any background videos on the page to prevent echo
      document.querySelectorAll("video").forEach(function (v) { v.pause(); });
      render(i);
      overlay.classList.add("open");
      document.body.style.overflow = "hidden";
      overlay.querySelector(".lb-close").focus();
    }
    function close() { stopCurrentMedia(); overlay.classList.remove("open"); document.body.style.overflow = ""; }

    items.forEach(function (source, i) {
      source.parentElement.addEventListener("click", function () { open(i); });
      source.parentElement.setAttribute("tabindex", "0");
      source.parentElement.setAttribute("role", "button");
      source.parentElement.addEventListener("keydown", function (e) {
        if (e.key === "Enter" || e.key === " ") { e.preventDefault(); open(i); }
      });
    });
    overlay.querySelector(".lb-close").addEventListener("click", close);
    overlay.querySelector(".lb-next").addEventListener("click", function () { render(current + 1); });
    overlay.querySelector(".lb-prev").addEventListener("click", function () { render(current - 1); });
    overlay.addEventListener("click", function (e) { if (e.target === overlay) close(); });
    document.addEventListener("keydown", function (e) {
      if (!overlay.classList.contains("open")) return;
      if (e.key === "Escape") close();
      if (e.key === "ArrowRight") render(current + 1);
      if (e.key === "ArrowLeft") render(current - 1);
    });
  }

  /* Password visibility toggles */
  function initPasswordToggles() {
    Array.prototype.slice.call(document.querySelectorAll("[data-toggle-password]")).forEach(function (btn) {
      btn.addEventListener("click", function () {
        var target = document.getElementById(btn.dataset.togglePassword);
        if (!target) return;
        var showing = target.type === "text";
        target.type = showing ? "password" : "text";
        btn.setAttribute("aria-label", showing ? "Show password" : "Hide password");
        btn.innerHTML = showing ? '<i class="bi bi-eye"></i>' : '<i class="bi bi-eye-slash"></i>';
      });
    });
  }

  /* Auto-dismiss flash messages */
  function initAlerts() {
    Array.prototype.slice.call(document.querySelectorAll("[data-autodismiss]")).forEach(function (el) {
      window.setTimeout(function () {
        el.style.transition = "opacity .4s ease";
        el.style.opacity = "0";
        window.setTimeout(function () { el.remove(); }, 400);
      }, 6000);
    });
  }

  /* Run reveal immediately (script is loaded at the end of <body>) */
  initReveal();

  document.addEventListener("DOMContentLoaded", function () {
    initNav();
    initHero();
    initHeroParticles();
    initTypewriter();
    initLightbox();
    initPasswordToggles();
    initAlerts();

    /* Mobile navbar: close off-canvas menu on nav link or overlay click */
    var collapse = document.querySelector(".ec-nav .navbar-collapse");
    var overlay = document.querySelector(".ec-nav .navbar-overlay");
    var toggler = document.querySelector(".ec-nav .navbar-toggler");
    if (collapse && toggler) {
      var closeMenu = function () { collapse.classList.remove("show"); toggler.setAttribute("aria-expanded", "false"); };
      collapse.querySelectorAll(".nav-link").forEach(function (link) {
        link.addEventListener("click", closeMenu);
      });
      if (overlay) overlay.addEventListener("click", closeMenu);
    }
  });
})();
