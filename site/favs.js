/* Hypewise: saved sneakers (kept only in this browser) and the Compare link in the nav. */
(function () {
  var K = "hw-favs", mem = [];
  function read() { try { var a = JSON.parse(localStorage.getItem(K) || "[]"); return Array.isArray(a) ? a : []; } catch (e) { return mem; } }
  function write(a) { mem = a; try { localStorage.setItem(K, JSON.stringify(a)); } catch (e) {} }
  function has(sku) { return read().indexOf(sku) > -1; }
  function list() { return read(); }
  function toggle(sku) {
    var a = read(), i = a.indexOf(sku);
    if (i > -1) a.splice(i, 1); else a.push(sku);
    write(a); sync(); document.dispatchEvent(new CustomEvent("hw-favs", { detail: { sku: sku } }));
    return i < 0;
  }
  var HEART = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 21s-7-4.6-9.3-9A5.3 5.3 0 0 1 12 6.6 5.3 5.3 0 0 1 21.3 12C19 16.4 12 21 12 21z"/></svg>';
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }
  function t(k, d) { return (window.HW && HW.t) ? HW.t(k) : d; }
  /* Small heart for cards (icon only) */
  function heart(sku) { var on = has(sku); return '<button type="button" class="heart" data-fav="' + esc(sku) + '" aria-pressed="' + on + '" aria-label="' + esc(t(on ? "fav.saved" : "fav.add", "Save")) + '">' + HEART + "</button>"; }
  /* Labelled button for the sneaker page */
  function button(sku) { var on = has(sku); return '<button type="button" class="btn ghost favbtn" data-fav="' + esc(sku) + '" aria-pressed="' + on + '">' + HEART + "<span>" + esc(t(on ? "fav.saved" : "fav.add", "Save")) + "</span></button>"; }
  function sync() {
    Array.prototype.forEach.call(document.querySelectorAll("[data-fav]"), function (b) {
      var on = has(b.getAttribute("data-fav"));
      b.setAttribute("aria-pressed", String(on));
      if (b.classList.contains("favbtn")) { var s = b.querySelector("span"); if (s) s.textContent = t(on ? "fav.saved" : "fav.add", "Save"); }
      else b.setAttribute("aria-label", t(on ? "fav.saved" : "fav.add", "Save"));
    });
  }
  document.addEventListener("click", function (e) {
    var b = e.target.closest && e.target.closest("[data-fav]"); if (!b) return;
    e.preventDefault(); e.stopPropagation(); toggle(b.getAttribute("data-fav"));
  }, true);
  document.addEventListener("hw-lang", sync);

  /* Compare link in the nav */
  var nav = document.querySelector("nav .links");
  if (nav && !nav.querySelector('[href="compare.html"]')) {
    var a = document.createElement("a"); a.href = "compare.html"; a.setAttribute("data-i18n", "nav.compare"); a.textContent = "Compare";
    if (/compare\.html$/.test(location.pathname)) a.setAttribute("aria-current", "page");
    var sel = nav.querySelector("select"); nav.insertBefore(a, sel || null);
  }
  window.HWF = { has: has, list: list, toggle: toggle, heart: heart, button: button, sync: sync };
})();
