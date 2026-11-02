// Hypewise - backtest del segnale Cop/Wait/Sell sui prezzi storici.
// Per ogni serie e ogni giorno: calcola il segnale con i dati disponibili fino a quel momento
// e confronta con la variazione reale dei 7 giorni successivi.
// Uso: node scripts/backtest_signal.js dati.json   (dati.json prodotto da scripts/backtest_signal.py)
const fs = require("fs");
const { signal } = require("../site/signal.js");
const data = JSON.parse(fs.readFileSync(process.argv[2], "utf8"));
const H = Number(process.argv[3] || 7), DAY = 86400000;
const agg = { cop: [], wait: [], sell: [], none: [] };
for (const s of data) {
  const t = s.times, p = s.prices;
  for (let i = 7; i < t.length; i++) {
    const fut = t.findIndex((v, j) => j > i && v - t[i] >= H * DAY);
    if (fut < 0) continue;
    const r = signal({ prices: p.slice(0, i + 1), times: t.slice(0, i + 1) });
    const fwd = (p[fut] - p[i]) / p[i] * 100;
    if (Math.abs(fwd) > 80) continue;
    (agg[r.verdict] || agg.none).push(fwd);
  }
}
const mean = a => a.reduce((x, y) => x + y, 0) / a.length;
console.log("Variazione reale a " + H + " giorni dopo il segnale\n");
let all = [].concat(agg.cop, agg.wait, agg.sell, agg.none);
console.log("tutti i punti: n=" + all.length + (all.length ? "  media " + mean(all).toFixed(2) + "%" : ""));
for (const k of ["cop", "wait", "sell"]) {
  const a = agg[k]; if (!a.length) { console.log(k + ": nessun dato"); continue; }
  const up = a.filter(v => v > 0).length / a.length * 100;
  console.log(k.padEnd(5) + " n=" + String(a.length).padEnd(5) + " media " + mean(a).toFixed(2) + "%   saliti dopo: " + up.toFixed(0) + "%");
}
console.log("\nSe il segnale funziona: COP deve avere media sopra 'tutti', SELL sotto. Servono n alti (centinaia) per fidarsi.");
