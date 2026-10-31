/* Hypewise: dati, formattazione e illustrazione condivisi dalle pagine Prezzi e Scheda. */
(function () {
  var SUPABASE_URL = "https://fbxvrrppskilblmszlvo.supabase.co";
  var SUPABASE_ANON_KEY = "sb_publishable_D1afxXoieLW5ORTAuqoytQ_MLrr7Viz"; // chiave pubblica, sola lettura
  var DAY = 864e5;

  function esc(s) { return String(s == null ? "" : s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }

  /* ---------- Marchi ---------- */
  var BRAND_ORDER = ["Jordan", "Nike", "adidas", "New Balance", "ASICS", "Saucony", "Salomon", "HOKA", "On", "Vans", "Converse"];
  function normBrand(b) {
    var k = String(b || "").trim().toLowerCase();
    var map = { "jordan": "Jordan", "air jordan": "Jordan", "nike": "Nike", "adidas": "adidas", "new balance": "New Balance", "asics": "ASICS",
      "saucony": "Saucony", "salomon": "Salomon", "hoka": "HOKA", "hoka one one": "HOKA", "on": "On", "on running": "On", "vans": "Vans", "converse": "Converse" };
    return map[k] || (b ? String(b).trim() : "Other");
  }
  function brandRank(b) { var i = BRAND_ORDER.indexOf(b); return i < 0 ? 99 : i; }

  /* ---------- Dettagli ricavati dal titolo ---------- */
  function parseTitle(title, brand) {
    var t = String(title || ""), tags = (t.match(/\(([^)]*)\)/g) || []).map(function (x) { return x.slice(1, -1); });
    var year = null, fit = null;
    tags.forEach(function (g) {
      if (/^(19|20)\d\d$/.test(g)) year = Number(g);
      else if (/^women'?s$/i.test(g) || g === "W") fit = "women";
      else if (/^(gs)$/i.test(g)) fit = "gs";
      else if (/^(ps)$/i.test(g)) fit = "ps";
      else if (/^(td)$/i.test(g)) fit = "td";
    });
    var name = t.replace(/\s*\([^)]*\)/g, "").trim();
    return { name: name, year: year, fit: fit };
  }

  /* ---------- Numeri ---------- */
  var usd = new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 });
  function money(v) { return usd.format(v); }
  function pct(v, loc) { return (v > 0 ? "+" : "") + v.toLocaleString(loc, { minimumFractionDigits: 1, maximumFractionDigits: 1 }) + "%"; }

  /* Variazione su "days" giorni. Restituisce null se mancano due letture abbastanza distanti. */
  function change(x, days) {
    var p = x.prices, t = x.times; if (!p || p.length < 2) return null;
    var last = p.length - 1, target = t[last] - days * DAY, ref = 0;
    for (var i = 0; i < last; i++) { if (Math.abs(t[i] - target) < Math.abs(t[ref] - target)) ref = i; }
    if (t[last] - t[ref] < 5 * 36e5 || !p[ref]) return null;
    return (p[last] - p[ref]) / p[ref] * 100;
  }
  function stats(x) {
    var p = x.prices, t = x.times, lo = 0, hi = 0, sum = 0;
    p.forEach(function (v, i) { if (v < p[lo]) lo = i; if (v > p[hi]) hi = i; sum += v; });
    return { n: p.length, last: p[p.length - 1], first: p[0], min: p[lo], max: p[hi], tmin: t[lo], tmax: t[hi], avg: sum / p.length, tfirst: t[0], tlast: t[t.length - 1] };
  }

  /* ---------- Supabase ---------- */
  async function api(path) {
    var r = await fetch(SUPABASE_URL + "/rest/v1/" + path, { headers: { apikey: SUPABASE_ANON_KEY, Authorization: "Bearer " + SUPABASE_ANON_KEY } });
    if (!r.ok) throw new Error("HTTP " + r.status);
    return r.json();
  }
  async function apiAll(path) { // Supabase manda al massimo 1000 righe: leggo a pagine
    var out = [], step = 1000;
    for (var from = 0; from < 200000; from += step) {
      var rows = await api(path + "&limit=" + step + "&offset=" + from);
      out = out.concat(rows);
      if (rows.length < step) break;
    }
    return out;
  }
  var EXTRA_COLS = "image_url,stockx_url,gender,release_year";
  async function productRows(filter) {
    var base = "products?select=id,title,brand,sku", f = filter || "";
    try { return await apiAll(base + "," + EXTRA_COLS + "&order=id.asc" + f); }  // colonne extra presenti
    catch (e) { return await apiAll(base + "&order=id.asc" + f); }                // ancora non create
  }
  function shape(p, byId, extras) {
    var h = byId[p.id], ex = (extras && extras[p.sku]) || {};
    return {
      id: p.id, title: p.title, brand: normBrand(p.brand), sku: p.sku,
      image: p.image_url || ex.image || null, link: p.stockx_url || ex.link || null,
      gender: p.gender || null, year: p.release_year || null,
      prices: h.prices, times: h.times
    };
  }
  async function loadExtras() { try { var r = await fetch("images.json"); return r.ok ? r.json() : {}; } catch (e) { return {}; } }
  function groupHistory(rows) {
    var byId = {};
    rows.forEach(function (h) {
      var v = Number(h.price); if (!(v > 0)) return;
      var e = byId[h.product_id] = byId[h.product_id] || { prices: [], times: [] };
      e.prices.push(v); e.times.push(Date.parse(h.created_at));
    });
    return byId;
  }
  async function loadAll() {
    var results = await Promise.all([productRows(""), apiAll("price_history?select=product_id,price,created_at&order=created_at.asc,id.asc"), loadExtras()]);
    var byId = groupHistory(results[1]);
    return results[0].filter(function (p) { return byId[p.id]; }).map(function (p) { return shape(p, byId, results[2]); });
  }
  async function loadOne(sku) {
    var rows = await productRows("&sku=eq." + encodeURIComponent(sku));
    if (!rows.length) return null;
    var hist = await apiAll("price_history?select=product_id,price,created_at&product_id=eq." + rows[0].id + "&order=created_at.asc,id.asc");
    var byId = groupHistory(hist), extras = await loadExtras();
    return byId[rows[0].id] ? shape(rows[0], byId, extras) : null;
  }

  /* ---------- Dati di esempio (se Supabase non risponde) ---------- */
  function demoData() {
    var base = [["Jordan 4 Retro Black Cat", "Jordan", "CU1110-010", 285], ["Jordan 11 Retro Gamma Blue (2024)", "Jordan", "378037-006", 268], ["Jordan 5 Retro Wolf Grey", "Jordan", "DD0587-100", 205],
      ["Nike Dunk Low Panda", "Nike", "DD1391-100", 118], ["Nike Air Max 95 Neon", "Nike", "CT1689-001", 172], ["adidas Samba OG Cloud White", "adidas", "B75806", 142],
      ["adidas Campus 00s Core Black", "adidas", "HQ8708", 98], ["New Balance 9060 Sea Salt", "New Balance", "U9060ECA", 156], ["ASICS Gel-1130 Cream Silver (Women's)", "ASICS", "1201A256-107", 131],
      ["Salomon XT-6 Black Phantom", "Salomon", "L41086000", 196], ["Saucony ProGrid Omni 9 Grey", "Saucony", "S70785-1", 149], ["Converse Shai 001", "Converse", "A09123C", 121]];
    var now = Date.now();
    return base.map(function (b, i) {
      var pts = [], p = b[3] * 0.93, s = i * 7 + 3;
      for (var d = 0; d < 14; d++) { s = (s * 9301 + 49297) % 233280; p += (s / 233280 - 0.44) * b[3] * 0.04; pts.push(Math.round(p)); }
      return { id: i, title: b[0], brand: b[1], sku: b[2], image: null, link: null, gender: null, year: null,
        prices: pts, times: pts.map(function (_, k) { return now - (pts.length - 1 - k) * 2 * DAY; }) };
    });
  }

  /* ---------- Illustrazione di una sneaker (se manca la foto ufficiale) ---------- */
  var PALETTES = [["#6a3df0", "#12a867"], ["#1a1530", "#8f72ff"], ["#12a867", "#1a1530"], ["#d1365c", "#1a1530"], ["#2f6df0", "#e9e6f7"], ["#a76a00", "#1a1530"], ["#8f72ff", "#12a867"]];
  function hash(s) { var h = 0; for (var i = 0; i < s.length; i++) h = (h * 31 + s.charCodeAt(i)) >>> 0; return h; }
  function sneakerSVG(seed, label) {
    var pal = PALETTES[hash(String(seed)) % PALETTES.length], a = pal[0], b = pal[1];
    return '<svg class="shoe-ill" viewBox="0 0 320 180" role="img" aria-label="' + esc(label || "Sneaker illustration") + '">' +
      '<ellipse cx="164" cy="160" rx="132" ry="7" fill="currentColor" opacity=".12"/>' +
      '<path d="M34 128 L38 74 Q40 58 58 56 L98 52 Q112 50 122 60 L136 78 Q156 90 186 92 L252 100 Q296 108 304 128 Z" fill="' + a + '"/>' +
      '<path d="M236 98 Q292 106 304 128 L256 128 Q252 110 236 98 Z" fill="' + b + '"/>' +
      '<path d="M34 128 L38 84 Q58 78 80 88 L84 128 Z" fill="' + b + '" opacity=".9"/>' +
      '<path d="M102 54 Q118 40 136 48 L142 70 Q124 70 112 64 Z" fill="#fff" opacity=".85"/>' +
      '<g stroke="#fff" stroke-width="3" stroke-linecap="round" opacity=".95"><path d="M144 80 L160 70"/><path d="M158 86 L174 76"/><path d="M172 91 L188 81"/><path d="M188 94 L204 85"/></g>' +
      '<path d="M96 112 Q160 92 232 104" fill="none" stroke="#fff" stroke-width="3" opacity=".55" stroke-linecap="round"/>' +
      '<rect x="20" y="126" width="290" height="22" rx="11" fill="#f4f2ec" stroke="#cfcbe0"/>' +
      '<rect x="22" y="142" width="286" height="8" rx="4" fill="#1a1530" opacity=".85"/>' +
      '</svg>';
  }

  /* Foto ufficiale (se c'è) con ripiego sull'illustrazione. size: "s" per le card, "l" per la scheda. */
  function shoeImage(x, size) {
    var ill = sneakerSVG(x.sku || x.title, x.title);
    if (!x.image) return '<div class="shoe-img ill">' + ill + "</div>";
    var url = String(x.image).replace(/w=\d+/, "w=" + (size === "l" ? 900 : 480)).replace(/h=\d+/, "h=" + (size === "l" ? 640 : 340));
    return '<div class="shoe-img photo"><img src="' + esc(url) + '" alt="' + esc(x.title) + '" loading="lazy" referrerpolicy="no-referrer" onerror="this.parentNode.className=\'shoe-img ill\';this.parentNode.innerHTML=this.parentNode.dataset.ill" ></div>'
      .replace('<div class="shoe-img photo">', '<div class="shoe-img photo" data-ill="' + esc(ill) + '">');
  }

  function spark(p, t) {
    var w = 120, h = 34;
    if (p.length < 2) return '<svg class="spark" viewBox="0 0 ' + w + " " + h + '"><line x1="3" y1="17" x2="117" y2="17" stroke="var(--line)" stroke-width="2" stroke-dasharray="3 4"/></svg>';
    var mn = Math.min.apply(null, p), mx = Math.max.apply(null, p), rg = (mx - mn) || 1;
    var t0 = t[0], tr = (t[t.length - 1] - t0) || 1;
    var pts = p.map(function (v, i) { return [((t[i] - t0) / tr) * (w - 8) + 4, h - 5 - ((v - mn) / rg) * (h - 10)]; });
    var d = pts.map(function (q, i) { return (i ? "L" : "M") + q[0].toFixed(1) + " " + q[1].toFixed(1); }).join(" ");
    var last = pts[pts.length - 1], c = p[p.length - 1] >= p[0] ? "var(--up)" : "var(--down)";
    return '<svg class="spark" viewBox="0 0 ' + w + " " + h + '" aria-hidden="true"><path d="' + d + '" fill="none" stroke="' + c + '" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/><circle cx="' + last[0].toFixed(1) + '" cy="' + last[1].toFixed(1) + '" r="2.8" fill="' + c + '"/></svg>';
  }

  window.HWD = { esc: esc, normBrand: normBrand, brandRank: brandRank, BRAND_ORDER: BRAND_ORDER, parseTitle: parseTitle, money: money, pct: pct, change: change, stats: stats,
    loadAll: loadAll, loadOne: loadOne, demoData: demoData, sneakerSVG: sneakerSVG, shoeImage: shoeImage, spark: spark, DAY: DAY };
})();
