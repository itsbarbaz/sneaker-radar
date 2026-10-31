/* Hypewise: interruttore chiaro/scuro, conteggi animati, nastro prezzi. */
(function () {
  var root = document.documentElement;
  function saved() { try { return localStorage.getItem("hw-theme"); } catch (e) { return null; } }
  function effective() { var t = root.getAttribute("data-theme"); return t || (matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light"); }
  function sync() { var b = document.getElementById("theme"); if (b) { var d = effective() === "dark"; b.setAttribute("aria-pressed", String(d)); if (window.HW) b.setAttribute("aria-label", HW.t(d ? "theme.to.light" : "theme.to.dark")); } }
  function initTheme() {
    var t = saved(); if (t === "light" || t === "dark") root.setAttribute("data-theme", t);
    var b = document.getElementById("theme");
    if (b) b.addEventListener("click", function () {
      var next = effective() === "dark" ? "light" : "dark"; root.setAttribute("data-theme", next);
      try { localStorage.setItem("hw-theme", next); } catch (e) {}
      sync(); document.dispatchEvent(new CustomEvent("hw-theme"));
    });
    sync(); document.addEventListener("hw-lang", sync);
  }
  var reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
  function countUp(el, to, fmt, ms) {
    fmt = fmt || function (v) { return Math.round(v).toLocaleString(); };
    if (reduce || !isFinite(to)) { el.textContent = fmt(to); return; }
    var t0 = performance.now(); ms = ms || 900;
    (function f(now) { var k = Math.min(1, (now - t0) / ms), e = 1 - Math.pow(1 - k, 3); el.textContent = fmt(to * e); if (k < 1) requestAnimationFrame(f); })(t0);
  }
  /* items: [{label, value, chg}] */
  function ticker(el, items, fmtPct) {
    if (!items.length) { el.hidden = true; return; }
    var one = items.map(function (it) {
      var cls = it.chg > 0.05 ? "up" : it.chg < -0.05 ? "down" : "flat";
      return '<span class="it"><span>' + HWD.esc(it.label) + "</span><b>" + HWD.money(it.value) + '</b><span class="' + cls + '">' + (it.chg > 0 ? "▲ " : it.chg < 0 ? "▼ " : "") + fmtPct(it.chg) + "</span></span>";
    }).join("");
    el.innerHTML = '<div class="track">' + one + one + "</div>";
    el.hidden = false;
  }
  window.UI = { initTheme: initTheme, countUp: countUp, ticker: ticker, sync: sync };
})();
