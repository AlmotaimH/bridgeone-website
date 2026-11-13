/* BridgeOne site script — animations, language switch, forms */
(function () {
  "use strict";

  /* ===== SETTINGS: edit these before launch ===== */
  var FORM_ENDPOINT = "https://formsubmit.co/ajax/info@bridge-one.ca"; // free at formspree.io — paste your form URL here
  var CONTACT_EMAIL = "info@bridge-one.ca";                  // fallback if the form endpoint isn't set yet
  /* ============================================== */

  var T = window.BO_I18N || null;
  var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var doc = document.documentElement;

  /* Loader */
  window.addEventListener("load", function () { setTimeout(function () { document.body.classList.add("loaded"); }, 350); });
  setTimeout(function () { document.body.classList.add("loaded"); }, 2500);

  /* Footer year */
  document.querySelectorAll("[data-year]").forEach(function (el) { el.textContent = new Date().getFullYear(); });

  /* Header shrink + back to top + reading progress */
  var hdr = document.querySelector(".hdr");
  var toTop = document.querySelector(".to-top");
  var bar = document.querySelector(".progress");
  if (!bar) { bar = document.createElement("div"); bar.className = "progress"; bar.setAttribute("aria-hidden", "true"); document.body.appendChild(bar); }
  function onScroll() {
    var y = window.scrollY;
    if (hdr) hdr.classList.toggle("scrolled", y > 20);
    if (toTop) toTop.classList.toggle("show", y > 700);
    if (bar) {
      var h = document.body.scrollHeight - window.innerHeight;
      bar.style.width = (h > 0 ? Math.min(100, (y / h) * 100) : 0) + "%";
    }
    if (bqWords && bqWords.length) {
      var qr = bq.getBoundingClientRect(), vh = window.innerHeight;
      var qn = Math.round(Math.max(0, Math.min(1, (vh * 0.92 - qr.top) / (vh * 0.5))) * bqWords.length);
      for (var qi = 0; qi < bqWords.length; qi++) bqWords[qi].classList.toggle("lit", qi < qn);
    }
    if (wm) { var wr = wm.getBoundingClientRect(); if (wr.top < window.innerHeight + 50) wm.style.transform = "translateX(" + ((wr.top / window.innerHeight) * 7 - 2).toFixed(2) + "vw)"; }
  }
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();
  if (toTop) toTop.addEventListener("click", function () { window.scrollTo({ top: 0, behavior: reduce ? "auto" : "smooth" }); });

  /* Mobile menu */
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

  /* Hero headline: word-by-word reveal */
  function splitWords(el) {
    if (!el) return;
    var text = el.textContent.trim();
    el.setAttribute("aria-label", text);
    el.innerHTML = "";
    var second = false;
    text.split(/\s+/).forEach(function (w, i) {
      var s = document.createElement("span");
      s.className = second ? "w em" : "w";
      s.setAttribute("aria-hidden", "true");
      s.textContent = w;
      s.style.animationDelay = (0.25 + i * 0.07) + "s";
      el.appendChild(s);
      el.appendChild(document.createTextNode(" "));
      /* the second sentence is the promise: set it apart */
      if (!second && /[.،]$/.test(w)) {
        second = true;
        var b = document.createElement("span"); b.className = "brk"; el.appendChild(b);
      }
    });
  }
  var heroH1 = document.querySelector("[data-split]");

  /* Scroll reveal */
  var io = "IntersectionObserver" in window ? new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      if (e.isIntersecting) { e.target.classList.add("on"); io.unobserve(e.target); }
    });
  }, { threshold: 0.14, rootMargin: "0px 0px -40px 0px" }) : null;
  document.querySelectorAll(".rv, .steps li, .lbl").forEach(function (el) {
    var d = el.getAttribute("data-d");
    if (d) el.style.transitionDelay = d + "s";
    if (io && !reduce) io.observe(el); else el.classList.add("on");
  });

  /* Languages are separate pages (/, /fr/, /ar/); nothing to switch here */
  splitWords(heroH1);
  function msg(key, fallback) {
    var b = document.querySelector("[data-fail]");
    return (b && b.getAttribute("data-fail")) || fallback;
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
      if (form.querySelector(".hp").value) return; // spam trap
      if (!form.querySelector("[name=_subject]")) { var hs = document.createElement("input"); hs.type = "hidden"; hs.name = "_subject"; hs.value = "New enquiry from bridge-one.ca"; form.appendChild(hs); var ht = document.createElement("input"); ht.type = "hidden"; ht.name = "_template"; ht.value = "table"; form.appendChild(ht); }
      var data = new FormData(form);
      var btn = form.querySelector("button[type=submit]");
      if (FORM_ENDPOINT.indexOf("YOUR_FORM_ID") !== -1) {
        var body = "Name: " + data.get("name") + "\nEmail: " + data.get("email") + "\nCompany: " + (data.get("company") || "") +
          "\nService: " + (data.get("service") || "") + "\n\n" + data.get("message");
        window.location.href = "mailto:" + CONTACT_EMAIL + "?subject=" + encodeURIComponent("Website enquiry — " + data.get("name")) + "&body=" + encodeURIComponent(body);
        return;
      }
      btn.disabled = true;
      fetch(FORM_ENDPOINT, { method: "POST", body: data, headers: { Accept: "application/json" } })
        .then(function (r) { if (!r.ok) throw new Error(); box.classList.add("sent"); box.scrollIntoView({ block: "center", behavior: reduce ? "auto" : "smooth" }); })
        .catch(function () { btn.disabled = false; alertBox(msg("contact.fail", "Sorry, something went wrong. Please email us at ") + CONTACT_EMAIL); });
    });
  }
  function alertBox(text) {
    var p = document.querySelector(".form-fail");
    if (p) { p.textContent = text; p.hidden = false; }
  }

  /* Newsletter */
  document.querySelectorAll("form.news").forEach(function (nf) {
    nf.addEventListener("submit", function (e) {
      e.preventDefault();
      var inp = nf.querySelector("input[type=email]");
      if (!emailRe.test(inp.value.trim())) { inp.focus(); return; }
      var holder = nf.parentElement;
      if (FORM_ENDPOINT.indexOf("YOUR_FORM_ID") !== -1) {
        window.location.href = "mailto:" + CONTACT_EMAIL + "?subject=" + encodeURIComponent("Newsletter signup") + "&body=" + encodeURIComponent("Please add " + inp.value.trim() + " to the BridgeOne newsletter.");
        return;
      }
      var d = new FormData(); d.append("email", inp.value.trim()); d.append("_subject", "Newsletter signup");
      fetch(FORM_ENDPOINT, { method: "POST", body: d, headers: { Accept: "application/json" } })
        .then(function () { holder.classList.add("subbed"); }).catch(function () { holder.classList.add("subbed"); });
    });
  });

  /* Insights filter */
  var filters = document.querySelectorAll(".filters button");
  filters.forEach(function (b) {
    b.addEventListener("click", function () {
      var cat = b.getAttribute("data-cat");
      filters.forEach(function (x) { x.setAttribute("aria-pressed", x === b ? "true" : "false"); });
      document.querySelectorAll("[data-post]").forEach(function (p) {
        var show = cat === "all" || p.getAttribute("data-post") === cat;
        p.classList.toggle("hide", !show);
        if (show) { p.classList.remove("on"); void p.offsetWidth; p.classList.add("on"); }
      });
    });
  });

  /* Copy link */
  var copyBtn = document.querySelector("[data-copy]");
  if (copyBtn) copyBtn.addEventListener("click", function () {
    try { navigator.clipboard.writeText(window.location.href); } catch (e) {}
    copyBtn.textContent = copyBtn.getAttribute("data-copied") || "Link copied";
  });

  /* ================= Live layer ================= */
  var lang = (doc.getAttribute("lang") || "en").slice(0, 2);
  var fine = !!(window.matchMedia && window.matchMedia("(hover: hover) and (pointer: fine)").matches);
  var wm = reduce ? null : document.querySelector(".wordmark");

  /* Toronto time + open / closed, live */
  var clock = document.querySelector("[data-clock]");
  if (clock && window.Intl) {
    var OPEN = { en: ["Open now", "Closed now"], fr: ["Ouvert", "Fermé"], ar: ["مفتوح الآن", "مغلق الآن"] }[lang] || ["Open now", "Closed now"];
    var CITY = lang === "ar" ? "تورنتو" : "Toronto";
    var tick = function () {
      try {
        var o = {};
        new Intl.DateTimeFormat("en-CA", { timeZone: "America/Toronto", weekday: "short", hour: "2-digit", minute: "2-digit", hour12: false })
          .formatToParts(new Date()).forEach(function (p) { o[p.type] = p.value; });
        var h = parseInt(o.hour, 10) % 24;
        var open = ["Mon", "Tue", "Wed", "Thu"].indexOf(o.weekday) !== -1 && h >= 10 && h < 19;
        clock.className = "coord live" + (open ? " open" : "");
        clock.innerHTML = "<i></i><span>" + CITY + " <span dir=\"ltr\">" + (h < 10 ? "0" + h : h) + ":" + o.minute + "</span></span><span>" + OPEN[open ? 0 : 1] + "</span>";
      } catch (e) {}
    };
    tick(); setInterval(tick, 20000);
  }

  /* "Who we work with" becomes a running ribbon */
  var strip = document.querySelector(".strip .wrap");
  if (strip && !reduce) {
    var chips = [].slice.call(strip.querySelectorAll(".chip"));
    if (chips.length) {
      var mq = document.createElement("div"); mq.className = "mq";
      var tr = document.createElement("div"); tr.className = "mq-t";
      for (var k = 0; k < 4; k++) chips.forEach(function (c) { var n = c.cloneNode(true); if (k) n.setAttribute("aria-hidden", "true"); tr.appendChild(n); });
      chips.forEach(function (c) { c.parentNode.removeChild(c); });
      mq.appendChild(tr); strip.appendChild(mq); strip.classList.add("has-mq");
    }
  }

  /* Numbers count up when they come into view */
  if ("IntersectionObserver" in window && !reduce) {
    var cio = new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        if (!e.isIntersecting) return;
        cio.unobserve(e.target);
        var el = e.target, to = +el.getAttribute("data-count"), pre = el.getAttribute("data-pre") || "", suf = el.getAttribute("data-suf") || "", t0 = performance.now();
        (function step(now) {
          var p = Math.min(1, (now - t0) / 1700);
          el.textContent = pre + Math.round(to * (1 - Math.pow(1 - p, 3))) + suf;
          if (p < 1) requestAnimationFrame(step);
        })(t0);
      });
    }, { threshold: 0.5 });
    document.querySelectorAll("[data-count]").forEach(function (el) { cio.observe(el); });
  }

  /* The bridge is alive: the main cable sways, and follows the pointer like a plucked string */
  var svg = document.querySelector(".bridge"), heroEl = document.querySelector(".hero");
  if (svg && heroEl && !reduce) {
    var mainCable = svg.querySelector(".cable.main"), hm = [].slice.call(svg.querySelectorAll(".hm line"));
    var cx = 0, cy = 0, vx = 0, vy = 0, tx = 0, ty = 0, inside = false, visible = true;
    if (fine) {
      heroEl.addEventListener("pointermove", function (e) {
        var r = svg.getBoundingClientRect();
        var px = (e.clientX - r.left) / r.width * 1440, py = (e.clientY - r.top) / r.height * 320;
        inside = true;
        tx = Math.max(-170, Math.min(170, (px - 720) * 0.34));
        ty = Math.max(-190, Math.min(14, (py - 300) * 0.6));
      });
      heroEl.addEventListener("pointerleave", function () { inside = false; });
    }
    if ("IntersectionObserver" in window) new IntersectionObserver(function (es) { visible = es[0].isIntersecting; }).observe(svg);
    var frame = function (now) {
      requestAnimationFrame(frame);
      if (!visible || !mainCable) return;
      var t = now / 1000, gx = inside ? tx : Math.sin(t * 0.55) * 18, gy = inside ? ty : Math.sin(t * 0.8) * 6 - 3;
      vx += (gx - cx) * 0.05; vy += (gy - cy) * 0.05; vx *= 0.9; vy *= 0.9; cx += vx; cy += vy;
      var qx = 720 + cx, qy = 388 + cy;
      mainCable.setAttribute("d", "M400 52Q" + qx.toFixed(1) + " " + qy.toFixed(1) + " 1040 52");
      for (var i = 0; i < hm.length; i++) {
        var u = (i + 1) / (hm.length + 1), a = (1 - u) * (1 - u), b = 2 * u * (1 - u), c = u * u;
        hm[i].setAttribute("x1", (400 * a + qx * b + 1040 * c).toFixed(1));
        hm[i].setAttribute("y1", Math.min(234, 52 * a + qy * b + 52 * c).toFixed(1));
      }
    };
    requestAnimationFrame(frame);
  }

  /* What the bridge connects keeps changing */
  var PAIRS = {
    en: [["Vision", "Execution"], ["Strategy", "Results"], ["Plans", "Action"], ["Canada", "The world"]],
    fr: [["Vision", "Exécution"], ["Stratégie", "Résultats"], ["Plans", "Action"], ["Canada", "Le monde"]],
    ar: [["الرؤية", "التنفيذ"], ["الاستراتيجية", "النتائج"], ["الخطط", "الإنجاز"], ["كندا", "العالم"]]
  }[lang];
  var ba = document.querySelector(".bank.a b"), bb = document.querySelector(".bank.b b");
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
  var bq = document.querySelector(".why-lead blockquote"), bqWords = [];
  if (bq && !reduce) {
    var qt = bq.textContent.trim(); bq.setAttribute("aria-label", qt); bq.innerHTML = "";
    qt.split(/\s+/).forEach(function (w) {
      var sp = document.createElement("span"); sp.className = "qw"; sp.setAttribute("aria-hidden", "true"); sp.textContent = w;
      bq.appendChild(sp); bq.appendChild(document.createTextNode(" ")); bqWords.push(sp);
    });
  }

  if (fine && !reduce) {
    /* A quiet gold ring follows the pointer */
    var cur = document.createElement("div"); cur.className = "cur"; cur.setAttribute("aria-hidden", "true"); document.body.appendChild(cur);
    var mx = 0, my = 0, rx = 0, ry = 0, curOn = false;
    window.addEventListener("pointermove", function (e) {
      mx = e.clientX; my = e.clientY;
      if (!curOn) { curOn = true; rx = mx; ry = my; cur.classList.add("on"); }
      var hit = e.target && e.target.closest ? e.target.closest("a,button,.card,input,select,textarea") : null;
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
    var fig = document.querySelector(".about-img.founder");
    if (fig) {
      fig.addEventListener("pointermove", function (e) {
        var r = fig.getBoundingClientRect(), x = (e.clientX - r.left) / r.width - 0.5, y = (e.clientY - r.top) / r.height - 0.5;
        fig.style.transition = "transform .2s ease-out";
        fig.style.transform = "perspective(900px) rotateY(" + (x * 7).toFixed(2) + "deg) rotateX(" + (-y * 7).toFixed(2) + "deg)";
      });
      fig.addEventListener("pointerleave", function () { fig.style.transition = "transform .7s cubic-bezier(.16,1,.3,1)"; fig.style.transform = ""; });
    }
  }
  onScroll();
})();
