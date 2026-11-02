"""Hypewise - "Sneaker spotlight": un'immagine con il grafico a 30 giorni di UNA scarpa interessante (dati veri).
Uso: python scripts/social_spotlight.py [--demo] [--out cartella]"""
import argparse, os, statistics, sys
from datetime import datetime, timezone
from PIL import Image, ImageDraw, ImageFilter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import social_image as S

DAY = 86400
VIO, GRN, RED, MUT = (154, 124, 255), (59, 232, 160), (255, 107, 146), (205, 199, 236)
POPULAR = ("Jordan", "Nike", "adidas", "New Balance", "ASICS", "Salomon", "Saucony", "HOKA", "On")

def chg(pts, days):
    t_last, last = pts[-1]
    for t, p in reversed(pts[:-1]):
        if t_last - t >= days * DAY:
            return (last - p) / p * 100
    return None

def swing(pts):
    """Misura quanto il grafico sale E scende: ampiezza 30 giorni e numero di inversioni nette."""
    ps = [p for _, p in pts[-30:]] if False else [p for t, p in pts if pts[-1][0] - t <= 30 * DAY]
    if len(ps) < 6: return 0, 0, 0
    avg = statistics.mean(ps); rng = (max(ps) - min(ps)) / avg * 100
    thr = (max(ps) - min(ps)) * 0.18; turns, direction, ext = 0, 0, ps[0]
    for v in ps[1:]:
        if direction == 0:
            if abs(v - ext) >= thr: direction = 1 if v > ext else -1; ext = v
        elif direction == 1:
            if v > ext: ext = v
            elif ext - v >= thr: turns += 1; direction = -1; ext = v
        else:
            if v < ext: ext = v
            elif v - ext >= thr: turns += 1; direction = 1; ext = v
    return rng, turns, avg

def candidates(items, now):
    out = []
    for it in items:
        pts = it["pts"]
        if len(pts) < 8 or now - pts[-1][0] > 36 * 3600 or pts[-1][0] - pts[0][0] < 10 * DAY:
            continue
        ps = [p for _, p in pts]
        if any(not (0.6 <= ps[i] / ps[i - 1] <= 1.4) for i in range(1, len(ps))):
            continue
        c7 = chg(pts, 7)
        if c7 is None or not (4 <= abs(c7) <= 30) or pts[-1][1] < 90:
            continue
        rng, turns, _ = swing(pts)
        if rng < 8 or turns < 2:
            continue
        score = (rng + 3 * abs(c7) + 6 * min(turns, 4)) * (1.3 if it["brand"] in POPULAR else 1.0)
        out.append((score, it, rng, turns, c7))
    out.sort(key=lambda r: -r[0])
    return out

def pick(items, now, sku=None):
    cands = candidates(items, now)
    for sc, it, rng, turns, c7 in cands[:10]:
        print("  candidato: %-55s sku=%s  range30=%.0f%%  inversioni=%d  7g=%+.1f%%  score=%.0f" % (it["title"][:55], it["sku"], rng, turns, c7, sc))
    if sku:
        for sc, it, *_ in cands:
            if str(it["sku"]).lower() == sku.lower(): return it
    return cands[0][1] if cands else None

def render(it, out_png, when):
    pts = [(t, p) for t, p in it["pts"] if it["pts"][-1][0] - t <= 30 * DAY]
    last = pts[-1][1]; c7 = chg(it["pts"], 7); c30 = chg(it["pts"], 30)
    ps = [p for _, p in pts]; lo, hi, avg = min(ps), max(ps), statistics.mean(ps)
    W, H, SS = 1600, 900, 2
    img = S.background(); d = ImageDraw.Draw(img)
    f = lambda n, s: S.font(n, s)
    d.text((80, 62), "Hype", font=f("ExtraBold", 46), fill=VIO); d.text((80 + d.textlength("Hype", font=f("ExtraBold", 46)), 62), "wise", font=f("ExtraBold", 46), fill=GRN)
    d.text((W - 80, 74), "SNEAKER SPOTLIGHT", font=f("Bold", 28), fill=GRN, anchor="ra")
    img.alpha_composite(S.badge(84, it["brand"]), (80, 150))
    title = S.clean_title(it["title"]); fn = f("ExtraBold", 46)
    lines, cur = [], ""
    for w_ in title.split():
        if d.textlength((cur + " " + w_).strip(), font=fn) <= 560: cur = (cur + " " + w_).strip()
        else: lines.append(cur); cur = w_
    lines.append(cur); lines = lines[:3]
    for k, ln in enumerate(lines): d.text((190, 148 + k * 56), S.fit(d, ln, fn, 560), font=fn, fill="white")
    d.text((80, 340), "${:,.0f}".format(last), font=f("ExtraBold", 150), fill="white")
    up = (c7 or 0) > 0; col = GRN if up else RED
    txt = ("+" if up else "−") + "{:.1f}%  in 7 days".format(abs(c7))
    tw = d.textlength(txt, font=f("Bold", 40)) + 70
    d.rounded_rectangle((80, 520, 80 + tw, 590), 35, fill=tuple(int(c * .22 + 8) for c in col))
    d.polygon([(104, 563), (130, 563), (117, 541)] if up else [(104, 545), (130, 545), (117, 567)], fill=col)
    d.text((146, 555), txt, font=f("Bold", 40), fill=col, anchor="lm")
    y = 650
    for k, v in [("30-day low", "${:,.0f}".format(lo)), ("30-day high", "${:,.0f}".format(hi)), ("30-day avg", "${:,.0f}".format(avg))]:
        d.text((80, y), k, font=f("Medium", 26), fill=MUT); d.text((300, y), v, font=f("Bold", 30), fill="white"); y += 48
    # grafico (a destra)
    cx0, cy0, cx1, cy1 = 840, 160, 1500, 700
    panel = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(panel).rounded_rectangle((cx0 - 30, cy0 - 30, cx1 + 30, cy1 + 30), 36, fill=(255, 255, 255, 18), outline=(255, 255, 255, 40), width=2)
    img.alpha_composite(panel); d = ImageDraw.Draw(img)
    pad = (hi - lo) * 0.18 or 1; mn, mx = lo - pad, hi + pad
    t0, t1 = pts[0][0], pts[-1][0]
    xy = [(cx0 + (t - t0) / ((t1 - t0) or 1) * (cx1 - cx0), cy1 - (p - mn) / (mx - mn) * (cy1 - cy0)) for t, p in pts]
    for k in range(4):
        gy = cy0 + k * (cy1 - cy0) / 3; d.line((cx0, gy, cx1, gy), fill=(70, 62, 98), width=2)
        d.text((cx1, gy - 6), "${:,.0f}".format(mx - k * (mx - mn) / 3), font=f("Medium", 20), fill=(150, 144, 185), anchor="rb")
    area = Image.new("RGBA", img.size, (0, 0, 0, 0)); ad = ImageDraw.Draw(area)
    ad.polygon(xy + [(xy[-1][0], cy1), (xy[0][0], cy1)], fill=col + (46,)); img.alpha_composite(area); d = ImageDraw.Draw(img)
    glow = Image.new("RGBA", img.size, (0, 0, 0, 0)); gd = ImageDraw.Draw(glow); gd.line(xy, fill=col + (255,), width=10, joint="curve")
    img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(14))); d = ImageDraw.Draw(img)
    d.line(xy, fill=col + (255,), width=7, joint="curve")
    for p_ in xy: d.ellipse((p_[0] - 3.5, p_[1] - 3.5, p_[0] + 3.5, p_[1] + 3.5), fill=col)
    lx, ly = xy[-1]; d.ellipse((lx - 14, ly - 14, lx + 14, ly + 14), fill=(255, 255, 255)); d.ellipse((lx - 9, ly - 9, lx + 9, ly + 9), fill=col)
    d.text((cx0 - 10, cy1 + 56), "Last 30 days · average US resale price", font=f("Medium", 24), fill=MUT)
    d.text((80, H - 44), S.SITE, font=f("Bold", 28), fill=VIO, anchor="lm")
    d.text((W - 80, H - 44), "Cop, Wait or Sell? Estimates · not financial advice", font=f("Medium", 24), fill=(163, 157, 194), anchor="rm")
    img.convert("RGB").save(out_png, "PNG", optimize=True)
    return {"title": title, "last": last, "c7": c7, "c30": c30, "lo": lo, "hi": hi}

def caption(r):
    return ("Sneaker spotlight 🔎 %s\n\n$%s now, %s%.1f%% in 7 days. 30-day range: $%s-$%s.\n\nCop, Wait or Sell? Full chart + signal:\nhttps://%s\n\nEstimates only, not financial advice.\n#sneakers #sneakerhead #resale\n") % (
        r["title"], "{:,.0f}".format(r["last"]), "+" if r["c7"] > 0 else "−", abs(r["c7"]), "{:,.0f}".format(r["lo"]), "{:,.0f}".format(r["hi"]), S.SITE)

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--demo", action="store_true"); ap.add_argument("--out", default="social"); ap.add_argument("--sku", default=""); a = ap.parse_args()
    now = datetime.now(timezone.utc).timestamp()
    if a.demo:
        import random; random.seed(2); pts = []; v = 245
        for k in range(30, -1, -1): v *= 1 + random.uniform(-.012, .012) + (0.018 if k < 8 else 0); pts.append((now - k * DAY, v))
        items = [{"title": "Jordan 4 Retro Black Cat", "brand": "Jordan", "sku": "CU1110-010", "pts": pts}]
    else:
        items = S.load_real()
    it = pick(items, now, a.sku or None)
    if not it:
        print("Nessuna scarpa adatta per lo spotlight oggi."); return
    os.makedirs(a.out, exist_ok=True)
    r = render(it, os.path.join(a.out, "spotlight.png"), datetime.now(timezone.utc))
    open(os.path.join(a.out, "spotlight.txt"), "w", encoding="utf-8").write(caption(r))
    print("Spotlight:", r["title"], "%+.1f%%" % r["c7"])

if __name__ == "__main__":
    main()
