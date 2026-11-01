/* Hypewise: menu tema, banner viola, sfondo con i marchi, conteggi animati, nastro prezzi. */
(function () {
  var root = document.documentElement, BRANDS = ["Jordan", "Nike", "adidas", "New Balance", "ASICS", "Saucony", "Salomon", "HOKA", "On", "Vans", "Converse"];
  var reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
  function saved() { try { var t = localStorage.getItem("hw-theme"); return t === "light" || t === "dark" ? t : "auto"; } catch (e) { return "auto"; } }
  function effective() { var t = root.getAttribute("data-theme"); return t || (matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light"); }
  var ICON = {
    light: '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>',
    dark: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M21 13a9 9 0 1 1-10-10 7 7 0 0 0 10 10z"/></svg>',
    auto: '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="4" width="18" height="12" rx="2"/><path d="M8 20h8M12 16v4"/></svg>'
  };
  function setMode(m) {
    if (m === "auto") { root.removeAttribute("data-theme"); try { localStorage.removeItem("hw-theme"); } catch (e) {} }
    else { root.setAttribute("data-theme", m); try { localStorage.setItem("hw-theme", m); } catch (e) {} }
    sync(); document.dispatchEvent(new CustomEvent("hw-theme"));
  }
  function sync() {
    var m = saved(), b = document.getElementById("theme"); if (!b) return;
    b.innerHTML = ICON[m === "auto" ? effective() : m] + '<span>' + HWD.esc(HW.t("theme." + m)) + '</span><i aria-hidden="true">▾</i>';
    b.setAttribute("aria-label", HW.t("theme.label") + ": " + HW.t("theme." + m));
    Array.prototype.forEach.call(document.querySelectorAll(".tmenu li button"), function (o) { o.setAttribute("aria-checked", String(o.dataset.m === m)); o.lastChild.textContent = HW.t("theme." + o.dataset.m); });
  }
  function initTheme() {
    var old = document.getElementById("theme"), t = saved();
    if (t !== "auto") root.setAttribute("data-theme", t);
    if (old) {
      var wrap = document.createElement("div"); wrap.className = "tmenu";
      wrap.innerHTML = '<button id="theme" class="theme" type="button" aria-haspopup="menu" aria-expanded="false"></button><ul role="menu" hidden>' +
        ["light", "dark", "auto"].map(function (m) { return '<li role="none"><button type="button" role="menuitemradio" data-m="' + m + '">' + ICON[m] + '<span></span></button></li>'; }).join("") + "</ul>";
      old.replaceWith(wrap);
      var btn = wrap.querySelector("#theme"), ul = wrap.querySelector("ul");
      function close() { ul.hidden = true; btn.setAttribute("aria-expanded", "false"); }
      btn.addEventListener("click", function (e) { e.stopPropagation(); ul.hidden = !ul.hidden; btn.setAttribute("aria-expanded", String(!ul.hidden)); });
      ul.addEventListener("click", function (e) { var o = e.target.closest("button"); if (o) { setMode(o.dataset.m); close(); btn.focus(); } });
      document.addEventListener("click", close); document.addEventListener("keydown", function (e) { if (e.key === "Escape") close(); });
    }
    sync(); document.addEventListener("hw-lang", function () { sync(); banner(true); });
  }
  /* Banner viola con messaggi che cambiano */
  var bi = 0, btimer = null;
  function banner(refresh) {
    var el = document.getElementById("hw-banner");
    try { if (sessionStorage.getItem("hw-bn") === "1") return; } catch (e) {}
    if (!el) {
      el = document.createElement("div"); el.id = "hw-banner"; el.className = "banner";
      el.innerHTML = '<span class="dot" aria-hidden="true"></span><p id="bn-text" aria-live="polite"></p><button type="button" aria-label="">×</button>';
      (document.querySelector(".wrap") || document.body).prepend(el);
      el.querySelector("button").addEventListener("click", function () { el.remove(); clearInterval(btimer); try { sessionStorage.setItem("hw-bn", "1"); } catch (e) {} });
      if (!reduce) btimer = setInterval(function () { bi = (bi + 1) % 3; swap(); }, 5200);
    }
    el.querySelector("button").setAttribute("aria-label", HW.t("bn.close"));
    if (refresh || true) swap(true);
  }
  function swap(now) {
    var p = document.getElementById("bn-text"); if (!p) return;
    function set() { p.textContent = HW.t("bn." + (bi + 1)); p.classList.remove("out"); }
    if (now || reduce) return set();
    p.classList.add("out"); setTimeout(set, 280);
  }
  /* Sfondo: righe di marchi che scorrono e una parola gigante che cambia */
  function backdrop() {
    if (document.getElementById("hw-bg")) return;
    var d = document.createElement("div"); d.id = "hw-bg"; d.setAttribute("aria-hidden", "true");
    var row = function (shift) { var r = BRANDS.slice(shift).concat(BRANDS.slice(0, shift)); var s = r.join("<i>✦</i>"); return '<div class="row">' + s + "<i>✦</i>" + s + "<i>✦</i></div>"; };
    d.innerHTML = row(0) + row(4) + row(8) + '<div class="bigword" id="bigword">' + BRANDS[0] + "</div>";
    document.body.prepend(d);
    var w = document.getElementById("bigword"), k = 0;
    if (!reduce) setInterval(function () { w.classList.add("off"); setTimeout(function () { k = (k + 1) % BRANDS.length; w.textContent = BRANDS[k]; w.classList.remove("off"); }, 600); }, 3600);
  }

  /* Footer classico: colonne di link, social (in arrivo), note legali */
  var SOCIAL = {
    X: '<path d="M4 4l16 16M20 4L4 20"/>',
    Instagram: '<rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.2" cy="6.8" r=".8" fill="currentColor"/>',
    TikTok: '<path d="M14 3v11a4 4 0 1 1-4-4"/><path d="M14 3c.5 2.6 2.2 4 5 4"/>',
    YouTube: '<rect x="2.5" y="5.5" width="19" height="13" rx="4"/><path d="M10 9.5l5 2.5-5 2.5z" fill="currentColor"/>'
  };
  function footer() {
    var old = document.querySelector(".wrap > footer"); if (!old || document.getElementById("hw-footer")) return;
    var notes = old.innerHTML, t = function (k) { return HWD.esc(HW.t(k)); }, L = function (k) { return '<span data-i18n="' + k + '">' + t(k) + "</span>"; };
    var f = document.createElement("footer"); f.id = "hw-footer"; f.className = "bigfoot";
    var brands = BRANDS.map(function (b) { return '<li><a href="board.html?brand=' + encodeURIComponent(b) + '">' + HWD.esc(b) + "</a></li>"; }).join("");
    var soc = Object.keys(SOCIAL).map(function (n) {
      return '<span class="s" title="' + HWD.esc(n) + ' · ' + t("ft.soon") + '" aria-label="' + HWD.esc(n) + '" role="img"><svg viewBox="0 0 24 24" aria-hidden="true">' + SOCIAL[n] + "</svg></span>";
    }).join("");
    function col(title, links) {
      return '<nav aria-label="' + t(title) + '"><h4>' + L(title) + "</h4><ul>" + links + "</ul></nav>";
    }
    function li(href, key) { return '<li><a href="' + href + '">' + L(key) + "</a></li>"; }
    f.innerHTML = '<div class="fgrid"><div class="fabout"><a class="mark" href="./">Hype<span>wise</span></a><p>' + L("ft.tag") + '</p><div class="soc" aria-label="' + t("ft.follow") + '">' + soc + "</div></div>" +
      col("ft.brands", brands) +
      col("ft.product", li("board.html", "ft.prices") + li("./#come", "ft.how") + li("./#segnale", "ft.signal")) +
      col("ft.company", li("legal.html#about", "ft.about") + li("legal.html#contact", "ft.contact")) +
      col("ft.legal", li("legal.html#privacy", "ft.privacy") + li("legal.html#terms", "ft.terms") + li("legal.html#disclaimer", "ft.disc") + li("legal.html#cookies", "ft.cookies")) + "</div>" +
      '<div class="fnotes">' + notes + '</div><div class="fbar"><span>' + L("ft.rights") + '</span><span class="reg">' + L("ft.region") + '</span><a href="#" class="top">↑ ' + L("ft.top") + "</a></div>";
    old.replaceWith(f);
    f.querySelector(".top").addEventListener("click", function (e) { e.preventDefault(); scrollTo({ top: 0, behavior: "smooth" }); });
  }
  function countUp(el, to, fmt, ms) {
    fmt = fmt || function (v) { return Math.round(v).toLocaleString(); };
    if (reduce || !isFinite(to)) { el.textContent = fmt(to); return; }
    var t0 = performance.now(); ms = ms || 900;
    (function f(now) { var k = Math.min(1, (now - t0) / ms), e = 1 - Math.pow(1 - k, 3); el.textContent = fmt(to * e); if (k < 1) requestAnimationFrame(f); })(t0);
  }
  function ticker(el, items, fmtPct) {
    if (!items.length) { el.hidden = true; return; }
    var one = items.map(function (it) {
      var cls = it.chg > 0.05 ? "up" : it.chg < -0.05 ? "down" : "flat";
      return '<span class="it"><span class="nm">' + HWD.esc(it.label) + '</span><b>' + HWD.money(it.value) + '</b><span class="pc ' + cls + '">' + (it.chg > 0.05 ? "↗ " : it.chg < -0.05 ? "↘ " : "") + fmtPct(it.chg) + "</span></span>";
    }).join("");
    el.innerHTML = '<div class="track">' + one + one + "</div>"; el.hidden = false;
  }
  window.UI = { initTheme: initTheme, countUp: countUp, ticker: ticker, sync: sync, banner: banner, backdrop: backdrop, footer: footer };
})();
