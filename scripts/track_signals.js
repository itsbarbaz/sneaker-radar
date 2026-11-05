/* Hypewise signal record.
   Runs after the daily bot. 1) logs every new Cop/Sell signal with date and price,
   2) checks old signals 7 and 30 days later and stores what the price did.
   Uses the same signal model as the site (site/signal.js), so what we log is what visitors see.
   Env: SUPABASE_URL, SUPABASE_SECRET_KEY. Set DRY_RUN=1 to print without writing. */
const S = require("../site/signal.js");
const URL_ = (process.env.SUPABASE_URL || "").replace(/\/$/, ""), KEY = process.env.SUPABASE_SECRET_KEY || "";
const DRY = /^(1|true|yes)$/i.test(process.env.DRY_RUN || "");
const DAY = 864e5, REPEAT_DAYS = 14, TOL = 3 * DAY;
if (!URL_ || !KEY) { console.log("Missing SUPABASE_URL / SUPABASE_SECRET_KEY: nothing to do."); process.exit(0); }
const H = { apikey: KEY, Authorization: "Bearer " + KEY, "Content-Type": "application/json" };

async function all(path) {
  const out = [];
  for (let from = 0; ; from += 1000) {
    const r = await fetch(`${URL_}/rest/v1/${path}&limit=1000&offset=${from}`, { headers: H });
    if (!r.ok) throw new Error(path + " -> HTTP " + r.status + " " + (await r.text()).slice(0, 200));
    const rows = await r.json(); out.push(...rows); if (rows.length < 1000) break;
  }
  return out;
}
async function send(method, path, body) {
  const r = await fetch(`${URL_}/rest/v1/${path}`, { method, headers: { ...H, Prefer: "return=minimal,resolution=ignore-duplicates" }, body: JSON.stringify(body) });
  if (!r.ok) throw new Error(method + " " + path + " -> HTTP " + r.status + " " + (await r.text()).slice(0, 200));
}

(async () => {
  const hist = await all("price_history?select=product_id,price,created_at&order=created_at.asc,id.asc");
  const by = {};
  for (const h of hist) { const v = Number(h.price); if (!(v > 0)) continue; (by[h.product_id] = by[h.product_id] || { prices: [], times: [] }); by[h.product_id].prices.push(v); by[h.product_id].times.push(Date.parse(h.created_at)); }
  const log = await all("signal_log?select=id,product_id,signal,signal_date,price_at_signal,price_7d,price_30d,checked_7d_at,checked_30d_at&order=signal_date.desc");
  const lastByProduct = {};
  for (const l of log) if (!lastByProduct[l.product_id]) lastByProduct[l.product_id] = l; // newest first
  const now = Date.now(), today = new Date().toISOString().slice(0, 10);

  /* 1) log new signals */
  const fresh = [];
  for (const id of Object.keys(by)) {
    const x = by[id], newest = x.times[x.times.length - 1];
    if (now - newest > 2 * DAY) continue;                      // only if we have a reading from the last 2 days
    const s = S.signal(x);
    if (s.verdict !== "cop" && s.verdict !== "sell") continue;
    const prev = lastByProduct[id];
    if (prev && prev.signal === s.verdict && now - Date.parse(prev.signal_date) < REPEAT_DAYS * DAY) continue; // same ongoing signal: don't count it twice
    fresh.push({ product_id: Number(id), signal: s.verdict, score: s.score, confidence: s.conf, price_at_signal: x.prices[x.prices.length - 1], signal_date: today });
  }
  console.log(`New signals to log: ${fresh.length} (cop ${fresh.filter(f => f.signal === "cop").length}, sell ${fresh.filter(f => f.signal === "sell").length})`);
  if (fresh.length && !DRY) for (let i = 0; i < fresh.length; i += 200) await send("POST", "signal_log?on_conflict=product_id,signal_date", fresh.slice(i, i + 200));

  /* 2) check old signals */
  function priceNear(x, target) {
    let best = -1, d = Infinity;
    for (let i = 0; i < x.times.length; i++) { const dd = Math.abs(x.times[i] - target); if (dd < d) { d = dd; best = i; } }
    return best >= 0 && d <= TOL ? x.prices[best] : null;
  }
  let upd = 0;
  for (const l of log) {
    const x = by[l.product_id]; if (!x) continue;
    const t0 = Date.parse(l.signal_date), patch = {};
    for (const [days, pk, ck] of [[7, "price_7d", "checked_7d_at"], [30, "price_30d", "checked_30d_at"]]) {
      if (l[ck]) continue;
      const target = t0 + days * DAY;
      if (now < target + TOL) continue;                          // too early, wait until the window has passed
      patch[pk] = priceNear(x, target); patch[ck] = new Date().toISOString();  // null price = no reading near that date
    }
    if (Object.keys(patch).length) { upd++; if (!DRY) await send("PATCH", `signal_log?id=eq.${l.id}`, patch); }
  }
  console.log(`Signals checked/updated: ${upd}`);
})().catch(e => { console.error(e); process.exit(1); });
