/* BridgeOne site script: menu, header, reading progress, contact form, copy link */
(function () {
  "use strict";

  /* ===== SETTINGS ===== */
  var FORM_ENDPOINT = "https://formsubmit.co/ajax/info@bridge-one.ca"; // FormSubmit: delivers enquiries to this inbox
  var CONTACT_EMAIL = "info@bridge-one.ca";                  // used until the form endpoint is set
  /* ==================== */

  var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  document.querySelectorAll("[data-year]").forEach(function (el) { el.textContent = new Date().getFullYear(); });

  var hdr = document.querySelector(".hdr");
  var toTop = document.querySelector(".to-top");
  var bar = document.querySelector(".progress");
  function onScroll() {
    var y = window.scrollY;
    if (toTop) toTop.classList.toggle("show", y > 900);
    if (bar) {
      var h = document.body.scrollHeight - window.innerHeight;
      bar.style.width = (h > 0 ? Math.min(100, (y / h) * 100) : 0) + "%";
    }
  }
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();
  if (toTop) toTop.addEventListener("click", function () { window.scrollTo({ top: 0, behavior: reduce ? "auto" : "smooth" }); });

  var burger = document.querySelector(".burger");
  if (burger && hdr) {
    burger.addEventListener("click", function () {
      var open = hdr.classList.toggle("open");
      burger.setAttribute("aria-expanded", open ? "true" : "false");
    });
    document.querySelectorAll(".mnav a").forEach(function (a) {
      a.addEventListener("click", function () { hdr.classList.remove("open"); burger.setAttribute("aria-expanded", "false"); });
    });
  }

  /* Contact form */
  var box = document.querySelector(".form-box");
  var form = document.querySelector("form.cf");
  var emailRe = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (form) {
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var ok = true;
      form.querySelectorAll("[data-req]").forEach(function (inp) {
        var f = inp.closest(".f");
        var bad = inp.type === "email" ? !emailRe.test(inp.value.trim()) : inp.value.trim().length < 2;
        f.classList.toggle("bad", bad);
        if (bad) inp.setAttribute("aria-invalid", "true"); else inp.removeAttribute("aria-invalid");
        if (bad && ok) { inp.focus(); ok = false; }
      });
      if (!ok) return;
      if (form.querySelector(".hp").value) return;
      if (!form.querySelector("[name=_subject]")) { var s = document.createElement("input"); s.type = "hidden"; s.name = "_subject"; s.value = "New enquiry from bridge-one.ca"; form.appendChild(s); var tpl = document.createElement("input"); tpl.type = "hidden"; tpl.name = "_template"; tpl.value = "table"; form.appendChild(tpl); }
      var data = new FormData(form);
      var btn = form.querySelector("button[type=submit]");
      if (FORM_ENDPOINT.indexOf("YOUR_FORM_ID") !== -1) {
        var body = "Name: " + data.get("name") + "\nEmail: " + data.get("email") + "\nCompany: " + (data.get("company") || "") +
          "\nService: " + (data.get("service") || "") + "\n\n" + data.get("message");
        window.location.href = "mailto:" + CONTACT_EMAIL + "?subject=" + encodeURIComponent("Website enquiry: " + data.get("name")) + "&body=" + encodeURIComponent(body);
        return;
      }
      btn.disabled = true;
      fetch(FORM_ENDPOINT, { method: "POST", body: data, headers: { Accept: "application/json" } })
        .then(function (r) { if (!r.ok) throw new Error(); box.classList.add("sent"); box.scrollIntoView({ block: "center", behavior: reduce ? "auto" : "smooth" }); })
        .catch(function () {
          btn.disabled = false;
          var p = document.querySelector(".form-fail");
          if (p) { p.textContent = (box.getAttribute("data-fail") || "Something went wrong. Email us at ") + CONTACT_EMAIL; p.hidden = false; }
        });
    });
  }

  var copyBtn = document.querySelector("[data-copy]");
  if (copyBtn) copyBtn.addEventListener("click", function () {
    try { navigator.clipboard.writeText(window.location.href); } catch (e) {}
    copyBtn.textContent = copyBtn.getAttribute("data-copied") || "Link copied";
  });
  /* ================= Live layer ================= */
  var fine = !!(window.matchMedia && window.matchMedia("(hover: hover) and (pointer: fine)").matches);

  /* Headline: word-by-word reveal */
  var h1 = document.querySelector("[data-split]");
  if (h1 && !reduce) {
    var ht = h1.textContent.trim(); h1.setAttribute("aria-label", ht); h1.innerHTML = "";
    ht.split(/\s+/).forEach(function (w, i) {
      var s = document.createElement("span"); s.className = "w"; s.setAttribute("aria-hidden", "true"); s.textContent = w;
      s.style.animationDelay = (0.15 + i * 0.07) + "s"; h1.appendChild(s); h1.appendChild(document.createTextNode(" "));
    });
  }

  /* Toronto time + open / closed, live */
  var clock = document.querySelector("[data-clock]");
  if (clock && window.Intl) {
    var tick = function () {
      try {
        var o = {};
        new Intl.DateTimeFormat("en-CA", { timeZone: "America/Toronto", weekday: "short", hour: "2-digit", minute: "2-digit", hour12: false })
          .formatToParts(new Date()).forEach(function (p) { o[p.type] = p.value; });
        var h = parseInt(o.hour, 10) % 24;
        var open = ["Mon", "Tue", "Wed", "Thu"].indexOf(o.weekday) !== -1 && h >= 10 && h < 19;
        clock.classList.toggle("open", open);
        clock.innerHTML = '<span class="dot" aria-hidden="true"></span><span>' + clock.getAttribute("data-city") + ' <span dir="ltr">' + (h < 10 ? "0" + h : h) + ":" + o.minute + '</span></span><span class="st">' + clock.getAttribute(open ? "data-open" : "data-closed") + "</span>";
      } catch (e) {}
    };
    tick(); setInterval(tick, 20000);
  }

  /* "We work with" becomes a running ribbon */
  var wl = document.querySelector(".who ul");
  if (wl && !reduce) {
    var items = [].slice.call(wl.children), mq = document.createElement("div"), tr = document.createElement("ul");
    mq.className = "mq"; tr.className = "mq-t";
    for (var k = 0; k < 4; k++) items.forEach(function (c) { var n = c.cloneNode(true); if (k) n.setAttribute("aria-hidden", "true"); tr.appendChild(n); });
    mq.appendChild(tr); wl.parentNode.replaceChild(mq, wl); mq.parentNode.classList.add("has-mq");
  }

  /* Numbers count up when they come into view */
  if ("IntersectionObserver" in window && !reduce) {
    var cio = new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        if (!e.isIntersecting) return;
        cio.unobserve(e.target);
        var el = e.target, m = el.textContent.trim().match(/^(\D*?)(\d[\d,\s\u202f\u00a0]*\d|\d)(\D*)$/);
        if (!m) return;
        var pre = m[1], raw = m[2], suf = m[3], to = +raw.replace(/\D/g, ""), t0 = performance.now();
        var sep = /,/.test(raw) ? "," : (/[\s\u202f\u00a0]/.test(raw) ? "\u202f" : "");
        var fmt = function (n) { var s = String(n); return sep ? s.replace(/\B(?=(\d{3})+(?!\d))/g, sep) : s; };
        (function step(now) {
          var p = Math.min(1, (now - t0) / 1700);
          el.textContent = pre + fmt(Math.round(to * (1 - Math.pow(1 - p, 3)))) + suf;
          if (p < 1) requestAnimationFrame(step);
        })(t0);
      });
    }, { threshold: 0.5 });
    document.querySelectorAll(".stat b").forEach(function (el) { cio.observe(el); });
  }

  /* The bridge is alive: the main cable sways, and follows the pointer like a plucked string */
  var span = document.querySelector(".span"), heroEl = document.querySelector(".hero");
  if (span && heroEl && !reduce) {
    var mainCable = span.querySelector(".cable.main"), hm = [].slice.call(span.querySelectorAll(".hm line"));
    var L = 300, R = 1140, TOP = 46, QY = 396, DECK = 286;
    var cx = 0, cy = 0, vx = 0, vy = 0, tx = 0, ty = 0, inside = false, visible = true, started = false;
    setTimeout(function () { started = true; }, 2700);
    if (fine) {
      heroEl.addEventListener("pointermove", function (e) {
        var r = span.getBoundingClientRect();
        var px = (e.clientX - r.left) / r.width * 1440, py = (e.clientY - r.top) / r.height * 380;
        inside = true;
        tx = Math.max(-170, Math.min(170, (px - 720) * 0.34));
        ty = Math.max(-200, Math.min(14, (py - 340) * 0.6));
      });
      heroEl.addEventListener("pointerleave", function () { inside = false; });
    }
    if ("IntersectionObserver" in window) new IntersectionObserver(function (es) { visible = es[0].isIntersecting; }).observe(span);
    var frame = function (now) {
      requestAnimationFrame(frame);
      if (!visible || !started || !mainCable) return;
      var t = now / 1000, gx = inside ? tx : Math.sin(t * 0.55) * 18, gy = inside ? ty : Math.sin(t * 0.8) * 6 - 3;
      vx += (gx - cx) * 0.05; vy += (gy - cy) * 0.05; vx *= 0.9; vy *= 0.9; cx += vx; cy += vy;
      var qx = 720 + cx, qy = QY + cy;
      mainCable.setAttribute("d", "M" + L + " " + TOP + "Q" + qx.toFixed(1) + " " + qy.toFixed(1) + " " + R + " " + TOP);
      for (var i = 0; i < hm.length; i++) {
        var u = (i + 1) / (hm.length + 1), a = (1 - u) * (1 - u), b = 2 * u * (1 - u), c = u * u;
        hm[i].setAttribute("x1", (L * a + qx * b + R * c).toFixed(1));
        hm[i].setAttribute("y1", Math.min(DECK - 8, TOP * a + qy * b + TOP * c).toFixed(1));
      }
    };
    requestAnimationFrame(frame);
  }

  /* What the bridge connects keeps changing */
  var ba = document.querySelector(".bank.a b"), bb = document.querySelector(".bank.b b"), PAIRS = null;
  try { PAIRS = JSON.parse((clock && clock.getAttribute("data-pairs")) || "null"); } catch (e) {}
  if (PAIRS && ba && bb && !reduce) {
    var pi = 0;
    setInterval(function () {
      pi = (pi + 1) % PAIRS.length;
      [ba, bb].forEach(function (el, j) {
        setTimeout(function () {
          el.classList.add("swap");
          setTimeout(function () { el.textContent = PAIRS[pi][j]; el.classList.remove("swap"); }, 360);
        }, j * 280);
      });
    }, 3600);
  }

  /* The promise lights up word by word as you scroll */
  var bq = document.querySelector(".statement"), bqWords = [];
  if (bq && !reduce) {
    var qt = bq.textContent.trim(); bq.setAttribute("aria-label", qt); bq.innerHTML = "";
    qt.split(/\s+/).forEach(function (w) {
      var sp = document.createElement("span"); sp.className = "qw"; sp.setAttribute("aria-hidden", "true"); sp.textContent = w;
      bq.appendChild(sp); bq.appendChild(document.createTextNode(" ")); bqWords.push(sp);
    });
  }
  var wm = reduce ? null : document.querySelector(".wordmark");
  function live() {
    if (bqWords.length) {
      var qr = bq.getBoundingClientRect(), vh = window.innerHeight;
      var qn = Math.round(Math.max(0, Math.min(1, (vh * 0.92 - qr.top) / (vh * 0.5))) * bqWords.length);
      for (var qi = 0; qi < bqWords.length; qi++) bqWords[qi].classList.toggle("lit", qi < qn);
    }
    if (wm) { var wr = wm.getBoundingClientRect(); if (wr.top < window.innerHeight + 50) wm.style.transform = "translateX(" + Math.max(-1.5, Math.min(1.5, (wr.top / window.innerHeight) * 3 - 1.5)).toFixed(2) + "vw)"; }
  }
  window.addEventListener("scroll", live, { passive: true }); live();

  if (fine && !reduce) {
    /* A soft gold ring follows the pointer */
    var cur = document.createElement("div"); cur.className = "cur"; cur.setAttribute("aria-hidden", "true"); document.body.appendChild(cur);
    var mx = 0, my = 0, rx = 0, ry = 0, curOn = false;
    window.addEventListener("pointermove", function (e) {
      mx = e.clientX; my = e.clientY;
      if (!curOn) { curOn = true; rx = mx; ry = my; cur.classList.add("on"); }
      var hit = e.target && e.target.closest ? e.target.closest("a,button,.tile,input,select,textarea") : null;
      cur.classList.toggle("big", !!hit);
    }, { passive: true });
    document.documentElement.addEventListener("pointerleave", function () { curOn = false; cur.classList.remove("on"); });
    (function loop() { rx += (mx - rx) * 0.2; ry += (my - ry) * 0.2; cur.style.transform = "translate(" + rx.toFixed(1) + "px," + ry.toFixed(1) + "px)"; requestAnimationFrame(loop); })();

    /* Main buttons lean toward the pointer */
    document.querySelectorAll(".btn-lg").forEach(function (b) {
      b.addEventListener("pointermove", function (e) {
        var r = b.getBoundingClientRect();
        b.style.translate = ((e.clientX - r.left - r.width / 2) * 0.16).toFixed(1) + "px " + ((e.clientY - r.top - r.height / 2) * 0.28).toFixed(1) + "px";
      });
      b.addEventListener("pointerleave", function () { b.style.translate = ""; });
    });

    /* Founder photo tilts with the pointer */
    var fig = document.querySelector(".portrait .ph");
    if (fig) {
      fig.addEventListener("pointermove", function (e) {
        var r = fig.getBoundingClientRect(), x = (e.clientX - r.left) / r.width - 0.5, y = (e.clientY - r.top) / r.height - 0.5;
        fig.style.transition = "transform .2s ease-out";
        fig.style.transform = "perspective(900px) rotateY(" + (x * 7).toFixed(2) + "deg) rotateX(" + (-y * 7).toFixed(2) + "deg)";
      });
      fig.addEventListener("pointerleave", function () { fig.style.transition = "transform .7s cubic-bezier(.16,1,.3,1)"; fig.style.transform = ""; });
    }
  }
})();
