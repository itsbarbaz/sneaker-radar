"""Hypewise - genera pagine statiche per modello (SEO/condivisione), sitemap.xml e robots.txt.
Gira nel workflow di deploy con i dati reali (sola lettura). Uso: python scripts/build_seo.py [--demo] [--site site]"""
import argparse, html, os, re, statistics, sys
from datetime import datetime, timezone
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import social_image as S

BASE = "https://itsbarbaz.github.io/sneaker-radar"
DAY = 86400

def slug(it):
    s = re.sub(r"[^a-z0-9]+", "-", it["title"].lower()).strip("-")[:70]
    k = re.sub(r"[^a-z0-9]+", "-", str(it["sku"]).lower()).strip("-")
    return (s + "-" + k).strip("-")

def clean_pts(pts):
    ps = [p for _, p in pts]
    if len(ps) < 2 or any(not (0.5 <= ps[i] / ps[i - 1] <= 1.5) for i in range(1, len(ps))):
        return None
    return pts

def chg_over(pts, days):
    t_last, last = pts[-1]
    for t, p in reversed(pts[:-1]):
        if t_last - t >= days * DAY:
            return (last - p) / p * 100
    return None

def fmt(v): return "—" if v is None else ("+" if v > 0 else "−" if v < 0 else "") + "{:.1f}%".format(abs(v))

NAVHTML = ('<div class="wrap"><nav><div class="nav-left"><button id="theme" class="theme" type="button"></button>'
           '<a class="mark" href="./">Hype<span>wise</span></a></div><div class="links"><a href="./" data-i18n="nav.home">Home</a>'
           '<a href="board.html" data-i18n="nav.prices">Prices</a><select id="lang" class="langsel" aria-label="Language"></select></div></nav>')
CSS = (".seo{max-width:780px;margin:0 auto;padding:28px 0 20px}.seo table{width:100%;border-collapse:collapse;margin:20px 0}"
       ".seo th,.seo td{padding:12px 6px;border-bottom:1px solid var(--line);text-align:left}.seo td.r,.seo th.r{text-align:right}.seo td.r{font-weight:600}"
       ".seo h1{font-size:clamp(28px,6vw,44px);line-height:1.05;margin:8px 0}.seo h2{margin:32px 0 6px}"
       ".seo .brand{color:var(--accent);font-family:var(--mono);text-transform:uppercase;letter-spacing:.08em;font-size:13px}"
       ".seo .note{color:var(--muted);font-size:14px}.seo .up{color:#0fa968}.seo .dn{color:#d1365c}.seo a{color:inherit}.seo td a{text-decoration:none;font-weight:600}")

def shell(depth, title, desc, path, body):
    """Pagina con la stessa barra e lo stesso footer del sito. depth=1 per le sottocartelle (usa <base>)."""
    e = html.escape; url = BASE + "/" + path
    return """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<base href="%(base)s">
<title>%(t)s</title>
<meta name="description" content="%(d)s">
<link rel="canonical" href="%(u)s">
<meta property="og:type" content="website"><meta property="og:site_name" content="Hypewise">
<meta property="og:title" content="%(t)s"><meta property="og:description" content="%(d)s">
<meta property="og:url" content="%(u)s"><meta property="og:image" content="%(b)s/og-image.png">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:image" content="%(b)s/og-image.png">
<link rel="icon" href="favicon.svg" type="image/svg+xml">
<script>try{var t=localStorage.getItem("hw-theme");if(t==="light"||t==="dark")document.documentElement.setAttribute("data-theme",t)}catch(e){}</script>
<link rel="stylesheet" href="style.css?v=22">
<style>%(css)s</style>
</head><body>
%(nav)s
<main class="seo">%(body)s</main>
<footer></footer></div>
<script src="i18n.js?v=22"></script><script src="strings.js?v=22"></script><script src="app.js?v=22"></script><script src="favs.js?v=22"></script><script src="ui.js?v=22"></script>
<script>HW.mount(); UI.initTheme(); UI.backdrop(); UI.banner(); UI.footer();</script>
</body></html>""" % {"base": "../" if depth else "./", "t": e(title), "d": e(desc), "u": url, "b": BASE, "css": CSS, "nav": NAVHTML, "body": body}

def stats(it, pts):
    t_last, last = pts[-1]
    recent = [p for t, p in pts if t_last - t <= 30 * DAY]
    return {"title": S.clean_title(it["title"]), "brand": it["brand"], "sku": it["sku"], "slug": slug(it), "last": last, "t_last": t_last,
            "lo": min(recent), "hi": max(recent), "avg": statistics.mean(recent), "c7": chg_over(pts, 7), "c30": chg_over(pts, 30), "n": len(pts)}

def cls(v): return "" if v is None else ("up" if v > 0 else "dn" if v < 0 else "")

def model_page(st):
    e = html.escape; title = st["title"]
    upd = datetime.fromtimestamp(st["t_last"], timezone.utc).strftime("%B %d, %Y").replace(" 0", " ")
    desc = "%s resale price history: about $%s now, 30-day range $%s-$%s. Daily US market data, estimates only." % (
        title, "{:,.0f}".format(st["last"]), "{:,.0f}".format(st["lo"]), "{:,.0f}".format(st["hi"]))
    rows = [("Latest average price", "$" + "{:,.0f}".format(st["last"])), ("30-day low / high", "$%s / $%s" % ("{:,.0f}".format(st["lo"]), "{:,.0f}".format(st["hi"]))),
            ("30-day average", "$" + "{:,.0f}".format(st["avg"])), ("Change, 7 days", fmt(st["c7"])), ("Change, 30 days", fmt(st["c30"])),
            ("Readings", str(st["n"])), ("Last updated", upd)]
    tr = "".join('<tr><th>%s</th><td class="r">%s</td></tr>' % (e(k), e(v)) for k, v in rows)
    body = ('<p class="brand">%s · US resale</p><h1>%s price history</h1>'
            '<p>Average US resale price tracked daily by Hypewise. Latest reading: <strong>$%s</strong> (%s).</p><table>%s</table>'
            '<p><a class="btn" href="shoe.html?sku=%s">See the full chart, Cop/Wait/Sell signal and story →</a></p>'
            '<p class="note">More: <a href="b/%s.html">all %s sneakers</a> · <a href="movers.html">biggest movers</a> · <a href="method.html">how the signal works</a>.</p>'
            '<p class="note">Estimates based on market data. Not financial advice. Hypewise is not affiliated with any brand or marketplace.</p>') % (
        e(st["brand"]), e(title), "{:,.0f}".format(st["last"]), upd, tr, html.escape(str(st["sku"]), quote=True), bslug(st["brand"]), e(st["brand"]))
    return shell(1, title + " price history | Hypewise", desc, "m/%s.html" % st["slug"], body)

def bslug(b): return re.sub(r"[^a-z0-9]+", "-", b.lower()).strip("-") or "other"

def table(sts, cols=("c7", "c30")):
    e = html.escape
    if not sts:
        return '<p class="note">Not enough price history yet.</p>'
    h = '<table><tr><th>Sneaker</th><th class="r">Price</th>' + "".join('<th class="r">%s</th>' % ("7 days" if c == "c7" else "30 days") for c in cols) + "</tr>"
    for x in sts:
        h += '<tr><td><a href="m/%s.html">%s</a></td><td class="r">$%s</td>' % (x["slug"], e(x["title"]), "{:,.0f}".format(x["last"]))
        h += "".join('<td class="r %s">%s</td>' % (cls(x[c]), fmt(x[c])) for c in cols) + "</tr>"
    return h + "</table>"

DISC = '<p class="note">Estimates based on daily US resale market data. Not financial advice. Hypewise is not affiliated with any brand or marketplace.</p>'

def movers_page(all_st):
    key = "c7" if sum(1 for x in all_st if x["c7"] is not None) >= 10 else "c30"
    pool = [x for x in all_st if x[key] is not None]
    label = "7 days" if key == "c7" else "30 days"
    up = sorted([x for x in pool if x[key] > 0], key=lambda x: -x[key])[:10]
    dn = sorted([x for x in pool if x[key] < 0], key=lambda x: x[key])[:10]
    body = ('<p class="brand">Updated daily</p><h1>Sneaker price movers</h1><p>The biggest US resale price changes over the last %s, from Hypewise daily tracking. '
            'Large moves on cheap or rarely traded pairs can be noise, so always check the chart.</p><h2>Biggest rises</h2>%s<h2>Biggest drops</h2>%s%s') % (
        label, table(up, (key,)), table(dn, (key,)), DISC)
    return shell(0, "Sneaker price movers: biggest rises and drops | Hypewise", "The biggest US sneaker resale price rises and drops over the last %s, updated daily." % label, "movers.html", body)

def brand_page(brand, sts):
    sts = sorted(sts, key=lambda x: -x["last"])
    body = ('<p class="brand">US resale</p><h1>%s sneaker prices</h1><p>Average US resale prices for %d %s models tracked daily by Hypewise.</p>%s%s') % (
        html.escape(brand), len(sts), html.escape(brand), table(sts), DISC)
    return shell(1, "%s sneaker prices and history | Hypewise" % brand, "Resale price history for %d %s sneakers, tracked daily on the US market. Estimates only." % (len(sts), brand), "b/%s.html" % bslug(brand), body)

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--demo", action="store_true"); ap.add_argument("--site", default="site")
    a = ap.parse_args()
    items = S.load_demo() if a.demo else S.load_real()
    out = os.path.join(a.site, "m"); bout = os.path.join(a.site, "b"); os.makedirs(out, exist_ok=True); os.makedirs(bout, exist_ok=True)
    urls = [BASE + "/", BASE + "/board.html", BASE + "/method.html", BASE + "/movers.html", BASE + "/compare.html", BASE + "/track.html", BASE + "/legal.html"]
    all_st = []
    for it in items:
        pts = clean_pts(it["pts"])
        if not pts or (len(pts) < 3 and not a.demo):
            continue
        all_st.append(stats(it, pts))
    for st in all_st:
        with open(os.path.join(out, st["slug"] + ".html"), "w", encoding="utf-8") as f: f.write(model_page(st))
        urls.append("%s/m/%s.html" % (BASE, st["slug"]))
    with open(os.path.join(a.site, "movers.html"), "w", encoding="utf-8") as f: f.write(movers_page(all_st))
    byb = {}
    for st in all_st: byb.setdefault(st["brand"], []).append(st)
    nb = 0
    for b, sts in byb.items():
        if len(sts) < 3 and not a.demo: continue
        with open(os.path.join(bout, bslug(b) + ".html"), "w", encoding="utf-8") as f: f.write(brand_page(b, sts))
        urls.append("%s/b/%s.html" % (BASE, bslug(b))); nb += 1
    n = len(all_st)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    with open(os.path.join(a.site, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
                "".join("<url><loc>%s</loc><lastmod>%s</lastmod></url>\n" % (u, today) for u in urls) + "</urlset>\n")
    with open(os.path.join(a.site, "robots.txt"), "w") as f:
        f.write("User-agent: *\nAllow: /\nSitemap: %s/sitemap.xml\n" % BASE)
    print("Pagine modello:", n, "· pagine marca:", nb)

if __name__ == "__main__":
    main()
