/* Hypewise Signal v2: modello multi-fattore, puro (funziona nel browser e in Node).
   Ogni fattore va da -1 (vendi) a +1 (compra). Il punteggio finale è la somma pesata.
   L'affidabilità dipende da quanti dati ci sono, quanto sono regolari e quanti fattori concordano. */
(function (root) {
  var DAY = 864e5;
  var W = { range: 0.30, z: 0.20, mom: 0.20, slope: 0.15, dd: 0.15 };
  var clamp = function (v, a, b) { return Math.max(a, Math.min(b, v)); };
  var mean = function (a) { return a.reduce(function (s, v) { return s + v; }, 0) / a.length; };
  var std = function (a) { var m = mean(a); return Math.sqrt(mean(a.map(function (v) { return (v - m) * (v - m); }))); };
  var median = function (a) { var s = a.slice().sort(function (x, y) { return x - y; }), k = s.length >> 1; return s.length % 2 ? s[k] : (s[k - 1] + s[k]) / 2; };

  /* toglie i valori anomali (salti oltre ~35% rispetto alla mediana dei vicini) */
  function clean(p, t) {
    var P = [], T = [];
    for (var i = 0; i < p.length; i++) {
      var nb = []; for (var j = Math.max(0, i - 2); j <= Math.min(p.length - 1, i + 2); j++) if (j !== i) nb.push(p[j]);
      var m = nb.length ? median(nb) : p[i];
      if (p[i] / m > 1.35 || p[i] / m < 0.74) continue;
      P.push(p[i]); T.push(t[i]);
    }
    return { p: P, t: T };
  }
  /* media mobile esponenziale che tiene conto del tempo reale tra una lettura e l'altra */
  function ema(p, t, halfDays) {
    var e = p[0];
    for (var i = 1; i < p.length; i++) { var a = 1 - Math.pow(0.5, (t[i] - t[i - 1]) / DAY / halfDays); e = e + a * (p[i] - e); }
    return e;
  }
  function regression(p, t, days) {
    var from = t[t.length - 1] - days * DAY, xs = [], ys = [];
    for (var i = 0; i < p.length; i++) if (t[i] >= from) { xs.push((t[i] - from) / DAY); ys.push(p[i]); }
    if (xs.length < 4) return null;
    var mx = mean(xs), my = mean(ys), sxy = 0, sxx = 0, syy = 0;
    for (var k = 0; k < xs.length; k++) { sxy += (xs[k] - mx) * (ys[k] - my); sxx += (xs[k] - mx) * (xs[k] - mx); syy += (ys[k] - my) * (ys[k] - my); }
    if (!sxx || !syy) return { slopePct: 0, r2: 0 };
    return { slopePct: sxy / sxx / my * 100, r2: (sxy * sxy) / (sxx * syy), n: xs.length };
  }

  function signal(x) {
    var rawP = x.prices || [], rawT = x.times || [];
    if (rawP.length < 8 || rawT[rawT.length - 1] - rawT[0] < 7 * DAY) return { verdict: "none", n: rawP.length };
    var c = clean(rawP, rawT), p = c.p, t = c.t, n = p.length;
    if (n < 8 || t[n - 1] - t[0] < 7 * DAY) return { verdict: "none", n: n };
    var last = p[n - 1], span = (t[n - 1] - t[0]) / DAY;
    var min = Math.min.apply(null, p), max = Math.max.apply(null, p), avg = mean(p), sd = std(p);

    /* 1. posizione nell'intervallo (percentile del prezzo attuale) */
    var rank = p.filter(function (v) { return v <= last; }).length / n;
    var fRange = clamp((0.5 - rank) * 2, -1, 1);
    /* 2. distanza dalla media, misurata in deviazioni standard */
    var zs = sd > 0 ? (last - avg) / sd : 0, fZ = clamp(-zs / 2, -1, 1);
    /* 3. slancio: media veloce contro media lenta; conta in modo diverso se il prezzo è basso o alto */
    var r = ema(p, t, 3) / ema(p, t, 10) - 1, m = clamp(r / 0.05, -1, 1);
    var fMom = rank <= 0.5 ? m : -Math.abs(m) * (rank - 0.5) * 2;
    /* 4. trend a 21 giorni con regressione, pesato dalla sua qualità (R²) */
    var rg = regression(p, t, 21), sl = rg ? clamp(rg.slopePct / 0.8, -1, 1) * Math.sqrt(rg.r2) : 0;
    var fSlope = rank <= 0.5 ? sl : -Math.abs(sl) * (rank - 0.5) * 2;
    /* 5. distanza dal massimo: forte sconto = compra, vicino al massimo = vendi */
    var dd = (last - max) / max * 100, fDd = clamp((-dd - 6) / 14, -1, 1);

    var raw = W.range * fRange + W.z * fZ + W.mom * fMom + W.slope * fSlope + W.dd * fDd;

    /* volatilità giornaliera: più è alta, più il segnale viene smorzato */
    var rets = []; for (var i = 1; i < n; i++) { var dt = Math.max(0.5, (t[i] - t[i - 1]) / DAY); rets.push((p[i] - p[i - 1]) / p[i - 1] * 100 / Math.sqrt(dt)); }
    var vol = std(rets), flat = (max - min) / avg * 100 < 4;
    var score = raw / (1 + Math.max(0, vol - 2) / 6); if (flat) score *= 0.6;
    /* coltello che cade: se il prezzo sta ancora scendendo in fretta non si dice mai Compra */
    var knife = fMom <= -0.6 && sl <= -0.3; if (knife) score = Math.min(score, 0.2);
    score = clamp(score, -1, 1);
    var verdict = score >= 0.3 ? "cop" : score <= -0.3 ? "sell" : "wait";
    var strength = Math.abs(score) >= 0.55 ? "strong" : Math.abs(score) >= 0.3 ? "mod" : "neutral";

    var f = [
      { k: "range", v: fRange, txt: Math.round(rank * 100) + "%" },
      { k: "z", v: fZ, txt: (last >= avg ? "+" : "") + ((last - avg) / avg * 100).toFixed(1) + "%" },
      { k: "mom", v: fMom, txt: (r >= 0 ? "+" : "") + (r * 100).toFixed(1) + "%" },
      { k: "slope", v: fSlope, txt: rg ? (rg.slopePct >= 0 ? "+" : "") + rg.slopePct.toFixed(2) + "%/d" : "–" },
      { k: "dd", v: fDd, txt: dd.toFixed(1) + "%" }
    ];
    /* affidabilità: dati (fino a 60) + regolarità + accordo tra i fattori; mai oltre 85 */
    var sgn = verdict === "cop" ? 1 : verdict === "sell" ? -1 : 0;
    var agree = sgn === 0 ? 0.5 : f.filter(function (q) { return q.v * sgn > 0.05; }).length / f.length;
    var conf = Math.min(30, n / 60 * 30) + Math.min(30, span / 60 * 30) + agree * 15 + (vol < 3 ? 10 : vol < 6 ? 4 : 0) + (rg ? rg.r2 * 5 : 0);
    conf = Math.round(clamp(conf, 10, 85));
    var level = conf >= 65 ? "high" : conf >= 40 ? "med" : "low";

    var why = [];
    why.push(rank <= 0.25 ? "r.low" : rank <= 0.45 ? "r.lowmid" : rank >= 0.9 ? "r.high" : rank >= 0.7 ? "r.highmid" : "r.mid");
    var devp = (last - avg) / avg * 100; if (devp <= -4) why.push("r.below"); else if (devp >= 4) why.push("r.above");
    var t7 = null; if (r !== null) { if (knife || (rg && rg.slopePct * 7 <= -4)) why.push("r.fall"); else if (rg && rg.slopePct * 7 >= 4) why.push("r.rise"); else why.push("r.flat"); }
    if (vol >= 6) why.push("r.vol");
    return { verdict: verdict, strength: strength, score: Math.round(score * 100), conf: conf, level: level, factors: f, why: why, n: n, span: Math.round(span), vol: vol, rank: rank };
  }
  var api = { signal: signal, WEIGHTS: W };
  if (typeof module !== "undefined" && module.exports) module.exports = api; else root.HWSignal = api;
})(typeof window !== "undefined" ? window : globalThis);
