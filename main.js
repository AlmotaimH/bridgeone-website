/* BridgeOne site script — animations, language switch, forms */
(function () {
  "use strict";

  /* ===== SETTINGS: edit these before launch ===== */
  var FORM_ENDPOINT = "https://formspree.io/f/YOUR_FORM_ID"; // free at formspree.io — paste your form URL here
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
  function onScroll() {
    var y = window.scrollY;
    if (hdr) hdr.classList.toggle("scrolled", y > 20);
    if (toTop) toTop.classList.toggle("show", y > 700);
    if (bar) {
      var h = document.body.scrollHeight - window.innerHeight;
      bar.style.width = (h > 0 ? Math.min(100, (y / h) * 100) : 0) + "%";
    }
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
    text.split(/\s+/).forEach(function (w, i) {
      var s = document.createElement("span");
      s.className = "w";
      s.setAttribute("aria-hidden", "true");
      s.textContent = w;
      s.style.animationDelay = (0.25 + i * 0.07) + "s";
      el.appendChild(s);
      el.appendChild(document.createTextNode(" "));
    });
  }
  var heroH1 = document.querySelector("[data-split]");

  /* Scroll reveal */
  var io = "IntersectionObserver" in window ? new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      if (e.isIntersecting) { e.target.classList.add("on"); io.unobserve(e.target); }
    });
  }, { threshold: 0.14, rootMargin: "0px 0px -40px 0px" }) : null;
  document.querySelectorAll(".rv, .steps li, .rule").forEach(function (el) {
    var d = el.getAttribute("data-d");
    if (d) el.style.transitionDelay = d + "s";
    if (io && !reduce) io.observe(el); else el.classList.add("on");
  });

  /* Card spotlight follows the cursor */
  document.querySelectorAll(".card").forEach(function (c) {
    c.addEventListener("pointermove", function (e) {
      var r = c.getBoundingClientRect();
      c.style.setProperty("--mx", (e.clientX - r.left) + "px");
      c.style.setProperty("--my", (e.clientY - r.top) + "px");
    });
  });

  /* Hero logo tilt */
  var art = document.querySelector(".hero-art img");
  var hero = document.querySelector(".hero");
  if (art && hero && !reduce && window.matchMedia("(pointer: fine)").matches) {
    hero.addEventListener("pointermove", function (e) {
      var r = hero.getBoundingClientRect();
      var x = (e.clientX - r.left) / r.width - 0.5, y = (e.clientY - r.top) / r.height - 0.5;
      art.style.transform = "rotateY(" + (x * 10) + "deg) rotateX(" + (-y * 10) + "deg)";
    });
    hero.addEventListener("pointerleave", function () { art.style.transform = ""; });
  }

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
        .then(function (r) { if (!r.ok) throw new Error(); box.classList.add("sent"); })
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
})();
