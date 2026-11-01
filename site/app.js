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


  /* ---------- Segnale Compra / Aspetta / Vendi (regole semplici, spiegabili) ---------- */
  function signal(x) {
    var p = x.prices || [], t = x.times || [], n = p.length;
    if (n < 8 || t[n - 1] - t[0] < 7 * DAY) return { verdict: "none", n: n };
    var st = stats(x), rng = st.max - st.min, last = st.last;
    var pos = rng > 0 ? (last - st.min) / rng : 0.5;
    var dev = (last - st.avg) / st.avg * 100, t7 = change(x, 7);
    var rets = []; for (var i = 1; i < n; i++) rets.push((p[i] - p[i - 1]) / p[i - 1] * 100);
    var m = rets.reduce(function (s, v) { return s + v; }, 0) / rets.length;
    var vol = Math.sqrt(rets.reduce(function (s, v) { return s + (v - m) * (v - m); }, 0) / rets.length);
    var score = 0, why = [];
    if (pos <= 0.25) { score += 2; why.push("r.low"); } else if (pos <= 0.4) { score += 1; why.push("r.lowmid"); }
    else if (pos >= 0.9) { score -= 2; why.push("r.high"); } else if (pos >= 0.75) { score -= 1; why.push("r.highmid"); }
    else why.push("r.mid");
    if (dev <= -5) { score += 1.5; why.push("r.below"); } else if (dev <= -2) { score += 0.5; }
    else if (dev >= 5) { score -= 1.5; why.push("r.above"); } else if (dev >= 2) { score -= 0.5; }
    if (t7 !== null) {
      if (t7 <= -5) { score -= 1; why.push("r.fall"); }
      else if (t7 >= 5) { why.push("r.rise"); if (pos >= 0.75) score -= 0.5; }
      else why.push("r.flat");
    }
    if (vol >= 6) why.push("r.vol");
    var verdict = score >= 2 ? "cop" : score <= -2 ? "sell" : "wait";
    var conf = n >= 40 && vol < 6 ? "high" : n >= 20 ? "med" : "low";
    if (vol >= 6 && conf === "high") conf = "med";
    return { verdict: verdict, score: score, pos: pos, dev: dev, t7: t7, vol: vol, n: n, conf: conf, why: why };
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

  /* ---------- Marchi come badge (sigla colorata, NON i loghi ufficiali) ---------- */
  var BRAND_COLORS = { "Jordan": ["#ff4d7d", "#7c4dff"], "Nike": ["#ff8a3d", "#ff3d7f"], "adidas": ["#3d8bff", "#7c4dff"], "New Balance": ["#7c8aa5", "#4d5b8a"],
    "ASICS": ["#12c2b5", "#3d8bff"], "Saucony": ["#5b6bff", "#12c2b5"], "Salomon": ["#ff5d5d", "#ff9d3d"], "HOKA": ["#ffc93d", "#ff6b3d"],
    "On": ["#8d99b3", "#5b6bff"], "Vans": ["#9a7cff", "#ff4d7d"], "Converse": ["#ff4d7d", "#ffc93d"] };
  var BRAND_ABBR = { "New Balance": "NB", "ASICS": "AS", "Salomon": "SA", "Saucony": "SC", "Converse": "CV", "adidas": "A", "Jordan": "J", "Nike": "N", "HOKA": "H", "On": "ON", "Vans": "V" };
  function hash(s) { var h = 0; for (var i = 0; i < s.length; i++) h = (h * 31 + s.charCodeAt(i)) >>> 0; return h; }
  function brandColors(b) {
    if (BRAND_COLORS[b]) return BRAND_COLORS[b];
    var hues = Object.keys(BRAND_COLORS), pick = BRAND_COLORS[hues[hash(String(b)) % hues.length]];
    return pick;
  }
  function abbr(b) { return BRAND_ABBR[b] || String(b || "?").replace(/[^A-Za-z0-9]/g, "").slice(0, 2).toUpperCase(); }
  var GLYPH = {"Jordan": "<circle cx=\"12\" cy=\"12\" r=\"9\"/><path d=\"M12 17V7M7.5 11.5L12 7l4.5 4.5\"/>", "Nike": "<path d=\"M3 16l7-7 3 3 8-6\"/><path d=\"M3 20l5-5M9 20l3-3\"/>", "adidas": "<circle cx=\"12\" cy=\"12\" r=\"3\"/><circle cx=\"12\" cy=\"12\" r=\"7\"/><path d=\"M12 2v3M12 19v3\"/>", "New Balance": "<path d=\"M4 8h12a3 3 0 0 1 0 6H8M20 16H8a3 3 0 0 0 0 6\"/>", "ASICS": "<path d=\"M4 12c3-6 6 6 8 0s5 6 8 0\"/><path d=\"M4 18c3-6 6 6 8 0s5 6 8 0\" opacity=\".5\"/>", "Saucony": "<path d=\"M13 2L5 14h6l-1 8 9-13h-6z\"/>", "Salomon": "<path d=\"M2 20L9 7l4 7 3-5 6 11z\"/>", "HOKA": "<path d=\"M3 8l9-4 9 4-9 4zM3 13l9 4 9-4M3 18l9 4 9-4\"/>", "On": "<circle cx=\"12\" cy=\"12\" r=\"8\"/><circle cx=\"12\" cy=\"12\" r=\"2.2\" fill=\"currentColor\"/>", "Vans": "<rect x=\"2\" y=\"9\" width=\"20\" height=\"6\" rx=\"3\"/><circle cx=\"7\" cy=\"19\" r=\"1.7\"/><circle cx=\"17\" cy=\"19\" r=\"1.7\"/>", "Converse": "<path d=\"M12 3l2.7 5.8 6.3.8-4.6 4.4 1.2 6.3L12 17.2 6.4 20.3l1.2-6.3L3 9.6l6.3-.8z\"/>"};
  function glyph(b) { return GLYPH[b] ? '<svg class="gl" viewBox="0 0 24 24" aria-hidden="true">' + GLYPH[b] + "</svg>" : ""; }
  function bmark(b, size) {
    var c = brandColors(b);
    return '<span class="bmark" style="--c1:' + c[0] + ";--c2:" + c[1] + ";--s:" + (size || 40) + 'px" aria-hidden="true">' + (glyph(b) || esc(abbr(b))) + "</span>";
  }
  function bchip(b, i) { return '<span class="bchip" style="--d:' + ((i || 0) * -0.35) + 's">' + bmark(b, 30) + esc(b) + "</span>"; }

  /* "Verificato": almeno 2 letture e nessun salto sospetto (oltre il 50%) tra una lettura e la successiva. */
  function verified(x) {
    var p = x.prices; if (!p || p.length < 2) return false;
    for (var i = 1; i < p.length; i++) { var r = p[i] / p[i - 1]; if (r > 1.5 || r < 0.5) return false; }
    return true;
  }
  var CHECK = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 3l7 3v5c0 4.5-3 8.3-7 10-4-1.7-7-5.5-7-10V6z"/><path d="M8.5 12.2l2.5 2.5 4.5-5"/></svg>';
  function vbadge(x, label, tip) { return verified(x) ? '<span class="verified" title="' + esc(tip) + '">' + CHECK + esc(label) + "</span>" : ""; }

  /* Copertina: foto ufficiale se c'è, altrimenti sfumatura generata nei colori del marchio. */
  var SHOE = '<svg class="shoe" viewBox="0 0 240 120" aria-hidden="true"><defs><linearGradient id="sg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".95"/><stop offset="1" stop-color="#fff" stop-opacity=".55"/></linearGradient></defs><path d="M8 84c0-6 3-10 9-12l34-12c10-4 16-12 20-22 3-8 10-12 18-8l18 9c10 5 22 8 34 9l40 4c18 2 32 12 36 26 1 4 0 8-3 10H14c-4 0-6-3-6-8z" fill="url(#sg)"/><path d="M6 88h224c4 0 6 6 4 12-2 6-8 10-14 10H20c-8 0-14-8-14-22z" fill="#fff" fill-opacity=".92"/><path d="M96 38l10 16M110 44l9 15M124 49l8 14" stroke="rgba(20,10,60,.45)" stroke-width="3.5" stroke-linecap="round"/><path d="M158 76c12 0 24-2 34-6" stroke="rgba(20,10,60,.25)" stroke-width="4" stroke-linecap="round" fill="none"/></svg>';
  function cover(x, size, badge) {
    var c = brandColors(x.brand), img = "";
    if (x.image) {
      var url = String(x.image).replace(/w=\d+/, "w=" + (size === "l" ? 900 : 480)).replace(/h=\d+/, "h=" + (size === "l" ? 640 : 340));
      img = '<img src="' + esc(url) + '" alt="' + esc(x.title) + '" loading="lazy" referrerpolicy="no-referrer" onerror="this.remove()">';
    }
    return '<div class="cover" style="--c1:' + c[0] + ";--c2:" + c[1] + '"><span class="big" aria-hidden="true">' + esc(abbr(x.brand)) + "</span>" + SHOE + img + (badge ? '<div class="tag">' + badge + "</div>" : "") + "</div>";
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

  window.HWD = { esc: esc, normBrand: normBrand, brandRank: brandRank, BRAND_ORDER: BRAND_ORDER, parseTitle: parseTitle, money: money, pct: pct, change: change, stats: stats, signal: signal,
    loadAll: loadAll, loadOne: loadOne, demoData: demoData, bmark: bmark, bchip: bchip, verified: verified, vbadge: vbadge, cover: cover, brandColors: brandColors, spark: spark, DAY: DAY };
})();
