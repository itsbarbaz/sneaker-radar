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

def page(it, pts):
    e = html.escape
    title = S.clean_title(it["title"]); brand = it["brand"]
    last = pts[-1][1]; t_last = pts[-1][0]
    recent = [p for t, p in pts if t_last - t <= 30 * DAY]
    lo, hi, avg = min(recent), max(recent), statistics.mean(recent)
    c7, c30 = chg_over(pts, 7), chg_over(pts, 30)
    upd = datetime.fromtimestamp(t_last, timezone.utc).strftime("%B %d, %Y").replace(" 0", " ")
    sl = slug(it)
    desc = "%s resale price history: about $%s now, 30-day range $%s-$%s. Daily US market data, estimates only." % (
        title, "{:,.0f}".format(last), "{:,.0f}".format(lo), "{:,.0f}".format(hi))
    url = "%s/m/%s.html" % (BASE, sl)
    full = "../shoe.html?sku=" + html.escape(str(it["sku"]), quote=True)
    rows = [("Latest average price", "$" + "{:,.0f}".format(last)), ("30-day low / high", "$%s / $%s" % ("{:,.0f}".format(lo), "{:,.0f}".format(hi))),
            ("30-day average", "$" + "{:,.0f}".format(avg)), ("Change, 7 days", fmt(c7)), ("Change, 30 days", fmt(c30)),
            ("Readings", str(len(pts))), ("Last updated", upd)]
    tr = "".join("<tr><th>%s</th><td>%s</td></tr>" % (e(k), e(v)) for k, v in rows)
    return sl, """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>%(t)s price history | Hypewise</title>
<meta name="description" content="%(d)s">
<link rel="canonical" href="%(u)s">
<meta property="og:type" content="website"><meta property="og:site_name" content="Hypewise">
<meta property="og:title" content="%(t)s price history | Hypewise"><meta property="og:description" content="%(d)s">
<meta property="og:url" content="%(u)s"><meta property="og:image" content="%(b)s/og-image.png">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:image" content="%(b)s/og-image.png">
<link rel="icon" href="../favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="../style.css?v=14">
<style>.seo{max-width:760px;margin:0 auto;padding:40px 20px 60px}.seo table{width:100%%;border-collapse:collapse;margin:24px 0}
.seo th,.seo td{padding:12px 4px;border-bottom:1px solid var(--line);text-align:left}.seo td{text-align:right;font-weight:600}.seo h1{font-size:clamp(28px,6vw,44px);line-height:1.05;margin:8px 0}
.seo .brand{color:var(--accent);font-family:var(--mono);text-transform:uppercase;letter-spacing:.08em;font-size:13px}.seo .note{color:var(--muted);font-size:14px}</style>
</head><body><main class="seo">
<p class="brand">%(br)s · US resale</p><h1>%(t)s price history</h1>
<p>Average US resale price tracked daily by Hypewise. Latest reading: <strong>$%(l)s</strong> (%(upd)s).</p>
<table>%(tr)s</table>
<p><a class="btn" href="%(full)s">See the full chart, Cop/Wait/Sell signal and story →</a></p>
<p class="note">Estimates based on market data. Not financial advice. Hypewise is not affiliated with any brand or marketplace.</p>
<p class="note"><a href="../index.html">Hypewise</a> · <a href="../board.html">All sneakers</a> · <a href="../legal.html">Legal</a></p>
</main></body></html>""" % {"t": e(title), "d": e(desc), "u": url, "b": BASE, "br": e(brand), "l": "{:,.0f}".format(last), "upd": upd, "tr": tr, "full": full}

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--demo", action="store_true"); ap.add_argument("--site", default="site")
    a = ap.parse_args()
    items = S.load_demo() if a.demo else S.load_real()
    out = os.path.join(a.site, "m"); os.makedirs(out, exist_ok=True)
    urls = [BASE + "/", BASE + "/board.html", BASE + "/legal.html"]; n = 0
    for it in items:
        pts = clean_pts(it["pts"])
        if not pts or len(pts) < 3 and not a.demo:
            continue
        sl, doc = page(it, pts)
        with open(os.path.join(out, sl + ".html"), "w", encoding="utf-8") as f: f.write(doc)
        urls.append("%s/m/%s.html" % (BASE, sl)); n += 1
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    with open(os.path.join(a.site, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
                "".join("<url><loc>%s</loc><lastmod>%s</lastmod></url>\n" % (u, today) for u in urls) + "</urlset>\n")
    with open(os.path.join(a.site, "robots.txt"), "w") as f:
        f.write("User-agent: *\nAllow: /\nSitemap: %s/sitemap.xml\n" % BASE)
    print("Pagine modello create:", n)

if __name__ == "__main__":
    main()
