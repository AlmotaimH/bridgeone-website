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
      var label = btn.textContent; btn.classList.add("busy"); btn.textContent = box.getAttribute("data-sending") || "Sending…";
      var fp = document.querySelector(".form-fail"); if (fp) fp.hidden = true;
      fetch(FORM_ENDPOINT, { method: "POST", body: data, headers: { Accept: "application/json" } })
        .then(function (r) { if (!r.ok) throw new Error(); return r.json(); }).then(function (j) { if (!j || String(j.success) !== "true") throw new Error(); box.classList.add("sent"); box.scrollIntoView({ block: "center", behavior: reduce ? "auto" : "smooth" }); })
        .catch(function () {
          btn.disabled = false; btn.classList.remove("busy"); btn.textContent = label;
          var body = "Name: " + data.get("name") + "\nEmail: " + data.get("email") + "\nCompany: " + (data.get("company") || "") + "\nService: " + (data.get("service") || "") + "\n\n" + data.get("message");
          var href = "mailto:" + CONTACT_EMAIL + "?subject=" + encodeURIComponent("Website enquiry: " + data.get("name")) + "&body=" + encodeURIComponent(body);
          if (fp) {
            fp.innerHTML = "";
            var t = document.createElement("span"); t.textContent = (box.getAttribute("data-fail") || "We couldn't send your message from the website. Please email us at ") + CONTACT_EMAIL + ".";
            var a = document.createElement("a"); a.className = "btn btn-gold"; a.href = href; a.textContent = box.getAttribute("data-mailbtn") || "Email us instead";
            var c = document.createElement("a"); c.className = "btn btn-glass"; c.href = "tel:+16473355647"; c.textContent = "+1 (647) 335-5647"; c.setAttribute("dir", "ltr");
            var row = document.createElement("span"); row.className = "ff-row"; row.appendChild(a); row.appendChild(c);
            fp.appendChild(t); fp.appendChild(row); fp.hidden = false;
            btn.closest(".full").appendChild(fp);
            fp.scrollIntoView({ block: "nearest", behavior: reduce ? "auto" : "smooth" });
          }
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
    h1.setAttribute("aria-label", h1.textContent.replace(/\s+/g, " ").trim());
    var wi = 0, parts = h1.querySelectorAll(".ln").length ? h1.querySelectorAll(".ln") : [h1];
    [].forEach.call(parts, function (p) {
      var ht = p.textContent.trim(); p.innerHTML = ""; p.setAttribute("aria-hidden", "true");
      ht.split(/\s+/).forEach(function (w) {
        var s = document.createElement("span"); s.className = "w"; s.textContent = w;
        s.style.animationDelay = (0.15 + wi++ * 0.07) + "s"; p.appendChild(s); p.appendChild(document.createTextNode(" "));
      });
    });
  }

  /* Toronto time + open / closed, live */
  var clock = document.querySelector("[data-clock]");
  if (clock && !clock.hidden && window.Intl) {
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
    if (false) {
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
      var t = now / 1000, gx = Math.sin(t * 0.5) * 5, gy = Math.sin(t * 0.7) * 3;
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
  var ba = document.querySelector(".end.a b"), bb = document.querySelector(".end.b b"), PAIRS = null;
  try { PAIRS = JSON.parse((clock && clock.getAttribute("data-pairs")) || "null"); } catch (e) {}
  if (PAIRS && ba && bb) {
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
    /* A small gold growth arrow follows the pointer */
    var cur = document.createElement("div"); cur.className = "cur"; cur.innerHTML = '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M3 17l6-6 4 4 8-8"/><path d="M15 7h6v6"/></svg>'; cur.setAttribute("aria-hidden", "true"); document.body.appendChild(cur);
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

  (function () {
  /* ===== Icons draw themselves in, and redraw on hover ===== */
  var icoTiles = document.querySelectorAll(".tile .ico");
  icoTiles.forEach(function (ic) {
    ic.querySelectorAll("path,rect,circle,line,polyline").forEach(function (s) { s.setAttribute("pathLength", "1"); });
  });
  if ("IntersectionObserver" in window && !reduce) {
    var iio = new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (e.isIntersecting) { e.target.querySelector(".ico").classList.add("drawn"); e.target.classList.add("in"); iio.unobserve(e.target); } });
    }, { threshold: 0.35 });
    icoTiles.forEach(function (ic) { ic.classList.add("draw"); iio.observe(ic.closest(".tile")); });
  }

  /* ===== Business health check: sliders drive a live radar chart ===== */
  var chk = document.querySelector(".check");
  if (chk) {
    var NS = "http://www.w3.org/2000/svg";
    var svg = chk.querySelector(".radar");
    var ranges = [].slice.call(chk.querySelectorAll("input[type=range]"));
    var src = chk.querySelector(".radar-src");
    var shortL = [].slice.call(src.querySelectorAll("span")).slice(0, 6).map(function (s) { return s.textContent; });
    var svcNames = [].slice.call(document.querySelectorAll(".svc-bento .tile h3")).map(function (h) { return h.textContent; });
    var areaNames = ranges.map(function (r) { return r.closest(".rng").querySelector(".rl span").textContent; });
    var N = 6, R = 112, rv = [0, 0, 0, 0, 0, 0], tgt = ranges.map(function (r) { return +r.value; });
    function pt(i, v) { var a = -Math.PI / 2 + i * 2 * Math.PI / N; return [Math.cos(a) * R * v / 5, Math.sin(a) * R * v / 5]; }
    function el(n, at, p) { var e = document.createElementNS(NS, n); for (var k in at) e.setAttribute(k, at[k]); (p || svg).appendChild(e); return e; }
    var defs = el("defs", {});
    var lg = el("linearGradient", { id: "rg", x1: "0", y1: "0", x2: "1", y2: "1" }, defs);
    el("stop", { offset: "0", "stop-color": "#F2B45A", "stop-opacity": ".55" }, lg); el("stop", { offset: "1", "stop-color": "#5B6CFF", "stop-opacity": ".45" }, lg);
    var grid = el("g", { "class": "rgrid" });
    for (var lv = 1; lv <= 5; lv++) {
      var ps = []; for (var i = 0; i < N; i++) ps.push(pt(i, lv).join(","));
      el("polygon", { points: ps.join(" "), "class": lv === 5 ? "outer" : "" }, grid);
    }
    for (var j = 0; j < N; j++) {
      var e5 = pt(j, 5); el("line", { x1: 0, y1: 0, x2: e5[0], y2: e5[1] }, grid);
      var lp = pt(j, 6.15), tx = el("text", { x: lp[0].toFixed(1), y: (lp[1] + 4).toFixed(1), "text-anchor": Math.abs(lp[0]) < 8 ? "middle" : (lp[0] > 0 ? "start" : "end"), "class": "rlab" });
      tx.textContent = shortL[j] + " ";
      var tv = document.createElementNS(NS, "tspan"); tv.setAttribute("class", "rval"); tx.appendChild(tv);
    }
    var tp = []; for (var ti = 0; ti < N; ti++) tp.push(pt(ti, 4).map(function (n) { return n.toFixed(1); }).join(","));
    el("polygon", { points: tp.join(" "), "class": "rtarget" });
    for (var sl = 1; sl <= 5; sl++) { var sp = pt(0, sl), st = el("text", { x: (sp[0] + 6).toFixed(1), y: (sp[1] + 4).toFixed(1), "class": "rscale" }); st.textContent = sl; }
    var shape = el("polygon", { "class": "rshape", fill: "url(#rg)" });
    var dots = []; for (var d = 0; d < N; d++) dots.push(el("circle", { r: 5, "class": "rdot" }));
    var vs = chk.querySelector(".vs"), va = chk.querySelector(".va"), cta = chk.querySelector(".verdict .btn");
    var whyT = src.querySelector(".why").textContent, pick = -1;
    function draw() {
      shape.setAttribute("points", rv.map(function (v, i) { return pt(i, v).map(function (n) { return n.toFixed(1); }).join(","); }).join(" "));
      dots.forEach(function (c, i) { var p = pt(i, rv[i]); c.setAttribute("cx", p[0].toFixed(1)); c.setAttribute("cy", p[1].toFixed(1)); });
    }
    var raf = 0;
    function animate() {
      var done = true;
      rv = rv.map(function (v, i) { var nv = v + (tgt[i] - v) * 0.18; if (Math.abs(tgt[i] - nv) > 0.01) done = false; else nv = tgt[i]; return nv; });
      draw(); raf = done ? 0 : requestAnimationFrame(animate);
    }
    var ovn = chk.querySelector(".ovn"), ovt = chk.querySelector(".ovt"), ovb = chk.querySelector(".ovbar i"), lvls = [].slice.call(src.querySelectorAll(".lv")).map(function (s) { return s.textContent; });
    function overall() {
      var avg = tgt.reduce(function (a, b) { return a + b; }, 0) / N;
      ovn.textContent = avg.toFixed(1); ovb.style.width = ((avg - 1) / 4 * 100) + "%";
      ovt.textContent = lvls[avg < 2.75 ? 0 : avg < 3.75 ? 1 : 2] || "";
      chk.setAttribute("data-level", avg < 2.75 ? "0" : avg < 3.75 ? "1" : "2");
    }
    function verdict() {
      overall();
      var min = Math.min.apply(null, tgt);
      pick = min >= 4 ? -1 : tgt.indexOf(min);
      dots.forEach(function (c, i) { c.classList.toggle("low", i === pick); });
      grid.querySelectorAll(".rlab").forEach(function (t, i) { t.classList.toggle("low", i === pick); });
      if (pick < 0) { vs.textContent = src.querySelector(".st").textContent; va.textContent = src.querySelector(".sb").textContent; }
      else { vs.textContent = svcNames[pick] || ""; va.textContent = whyT.replace("{a}", areaNames[pick]); }
      chk.classList.remove("pop"); void chk.offsetWidth; chk.classList.add("pop");
    }
    function update() {
      ranges.forEach(function (r, i) {
        tgt[i] = +r.value; r.closest(".rng").querySelector("output").textContent = r.value;
        r.style.setProperty("--p", ((r.value - 1) / 4 * 100) + "%");
      });
      grid.querySelectorAll(".rval").forEach(function (v, i) { v.textContent = tgt[i]; });
      verdict();
      if (reduce) { rv = tgt.slice(); draw(); } else if (!raf) raf = requestAnimationFrame(animate);
    }
    ranges.forEach(function (r) { r.addEventListener("input", update); });
    if (cta) cta.addEventListener("click", function () {
      var sel = document.querySelector("form.cf select[name=service]");
      if (sel && pick >= 0) [].forEach.call(sel.options, function (o, i) { if (o.textContent === svcNames[pick]) sel.selectedIndex = i; });
    });
    ranges.forEach(function (r) { r.style.setProperty("--p", ((r.value - 1) / 4 * 100) + "%"); });
    grid.querySelectorAll(".rval").forEach(function (v, i) { v.textContent = tgt[i]; });
    verdict();
    if (reduce || !("IntersectionObserver" in window)) { rv = tgt.slice(); draw(); }
    else {
      draw();
      var rio = new IntersectionObserver(function (es) { if (es[0].isIntersecting) { rio.disconnect(); raf = requestAnimationFrame(animate); } }, { threshold: 0.4 });
      rio.observe(svg);
    }
  }

  /* ===== How an engagement runs: a cycle; the active card comes forward ===== */
  var cyc = document.querySelector(".cycle");
  if (cyc) {
    var cards = [].slice.call(cyc.querySelectorAll(".cc")), nds = [].slice.call(cyc.querySelectorAll(".nd"));
    var arm = cyc.querySelector(".arm"), rp = cyc.querySelector(".rp"), n = cards.length, cur = 0, turns = 0, paused = false;
    var show = function (i, jump) {
      var prev = cur;
      if (!jump && i === 0 && prev === n - 1) turns++;
      if (jump) turns = Math.floor(turns);
      cur = i;
      cards.forEach(function (c, k) { var pos = (k - i + n) % n; c.setAttribute("data-pos", pos); c.setAttribute("aria-current", pos === 0 ? "step" : "false"); });
      nds.forEach(function (d, k) { d.classList.toggle("on", k === i); d.classList.toggle("done", k < i); });
      arm.style.transform = "rotate(" + ((document.documentElement.dir === "rtl" ? -1 : 1) * (turns * n + i) * 360 / n) + "deg)";
      if (i === 0) { rp.style.transition = "none"; rp.style.strokeDasharray = "0 100"; void rp.getBoundingClientRect(); rp.style.transition = ""; }
      else rp.style.strokeDasharray = (i * 100 / n) + " 100";
    };
    nds.forEach(function (d, k) {
      d.addEventListener("click", function () { show(k, true); });
      d.addEventListener("mouseenter", function () { paused = true; });
      d.addEventListener("mouseleave", function () { paused = false; });
    });
    cyc.querySelector(".deck").addEventListener("mouseenter", function () { paused = true; });
    cyc.querySelector(".deck").addEventListener("mouseleave", function () { paused = false; });
    show(0, true);
    var go = function () { setInterval(function () { if (!paused && !document.hidden) show((cur + 1) % n); }, 3600); };
    if ("IntersectionObserver" in window) {
      var cio2 = new IntersectionObserver(function (es) { if (es[0].isIntersecting) { cio2.disconnect(); go(); } }, { threshold: 0.35 });
      cio2.observe(cyc);
    } else go();
  }
  })();
})();
