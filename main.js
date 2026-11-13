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
})();
