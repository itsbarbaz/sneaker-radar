"""
Hypewise - generatore dell'immagine social "Le sneaker piu' mosse oggi".

Legge i prezzi dal database pubblico (sola lettura), calcola le variazioni piu' grandi
e crea un PNG 1600x900 (formato adatto a X) piu' un testo pronto da incollare.

Uso:
  python scripts/social_image.py                 dati veri da Supabase
  python scripts/social_image.py --demo          dati di esempio (per provare la grafica)
  python scripts/social_image.py --out cartella  dove salvare (default: social/)
"""
import argparse
import json
import os
import re
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone

from PIL import Image, ImageDraw, ImageFilter, ImageFont

SUPABASE_URL = "https://fbxvrrppskilblmszlvo.supabase.co"
ANON_KEY = "sb_publishable_D1afxXoieLW5ORTAuqoytQ_MLrr7Viz"  # chiave pubblica, sola lettura
SITE = "itsbarbaz.github.io/sneaker-radar"
FONTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")
W, H = 1600, 900
TOP_N = 5

# simboli: sigle e colori originali Hypewise (non i loghi ufficiali)
BRAND_COLORS = {
    "Jordan": ("#ff4d7d", "#7c4dff"), "Nike": ("#ff8a3d", "#ff3d7f"), "adidas": ("#3d8bff", "#7c4dff"),
    "New Balance": ("#7c8aa5", "#4d5b8a"), "ASICS": ("#22c1dc", "#3d6bff"), "Saucony": ("#3da5ff", "#6a3df0"),
    "Salomon": ("#ff7a45", "#ff3d5a"), "HOKA": ("#ffb43d", "#ff6a3d"), "On": ("#8b94e8", "#5b6bd6"),
    "Vans": ("#c06bff", "#ff5ca8"), "Converse": ("#ff7a59", "#ffb43d"),
}
BRAND_ABBR = {"New Balance": "NB", "ASICS": "AS", "Salomon": "SA", "Saucony": "SC", "Converse": "CV",
              "adidas": "A", "Jordan": "J", "Nike": "N", "HOKA": "H", "On": "ON", "Vans": "V"}
BRAND_MAP = {"jordan": "Jordan", "air jordan": "Jordan", "nike": "Nike", "adidas": "adidas", "new balance": "New Balance",
             "asics": "ASICS", "saucony": "Saucony", "salomon": "Salomon", "hoka": "HOKA", "hoka one one": "HOKA",
             "on": "On", "on running": "On", "vans": "Vans", "converse": "Converse"}


def font(name, size):
    return ImageFont.truetype(os.path.join(FONTS, "Inter-%s.otf" % name), size)


def hexrgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


# ---------------------------------------------------------------- dati
def api_all(path):
    rows, offset = [], 0
    while True:
        url = "%s/rest/v1/%s&limit=1000&offset=%d" % (SUPABASE_URL, path, offset)
        req = urllib.request.Request(url, headers={"apikey": ANON_KEY, "Authorization": "Bearer " + ANON_KEY})
        with urllib.request.urlopen(req, timeout=60) as r:
            chunk = json.loads(r.read().decode())
        rows += chunk
        if len(chunk) < 1000:
            return rows
        offset += 1000


def parse_ts(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()


def load_real():
    products = {p["id"]: p for p in api_all("products?select=id,title,brand,sku&order=id.asc")}
    hist = api_all("price_history?select=product_id,price,created_at&order=created_at.asc,id.asc")
    series = {}
    for h in hist:
        if h["product_id"] in products and h["price"]:
            series.setdefault(h["product_id"], []).append((parse_ts(h["created_at"]), float(h["price"])))
    out = []
    for pid, pts in series.items():
        p = products[pid]
        b = BRAND_MAP.get(str(p.get("brand") or "").strip().lower(), str(p.get("brand") or "").strip() or "Other")
        out.append({"title": p["title"], "brand": b, "sku": p["sku"], "pts": pts})
    return out


def load_demo():
    now = datetime.now(timezone.utc).timestamp()
    base = [("Jordan 4 Retro Black Cat", "Jordan", 283, 4.0), ("Converse Shai 001", "Converse", 117, 3.5),
            ("ASICS Gel-1130 Cream Silver (Women's)", "ASICS", 129, 3.2), ("Salomon XT-6 Black Phantom", "Salomon", 198, -3.1),
            ("Saucony ProGrid Omni 9 Grey", "Saucony", 153, 2.7), ("adidas Campus 00s Core Black", "adidas", 89, -1.1),
            ("New Balance 9060 Sea Salt", "New Balance", 151, -0.7)]
    return [{"title": t, "brand": b, "sku": "DEMO%d" % i, "pts": [(now - 86400 * 1.1, p / (1 + c / 100)), (now, float(p))]}
            for i, (t, b, p, c) in enumerate(base)]


# ---------------------------------------------------------------- calcolo
MODE = "daily"
HEAD = {"daily": ("Biggest sneaker", "price moves today"), "weekly": ("Wildest sneaker", "moves this week")}


def pick_mode(arg, when):
    """auto = alterna: giorni dispari = settimanale, pari = giornaliero."""
    if arg in ("daily", "weekly"):
        return arg
    return "weekly" if when.timetuple().tm_yday % 2 else "daily"


def movers(items, top=TOP_N, hours=12):
    res = []
    for it in items:
        pts = it["pts"]
        if len(pts) < 2:
            continue
        ps = [p for _, p in pts]
        if any(not (0.5 <= ps[i] / ps[i - 1] <= 1.5) for i in range(1, len(ps))):
            continue  # salto sospetto: non lo mostriamo
        t_last, last = pts[-1]
        if hours <= 12 and datetime.now(timezone.utc).timestamp() - t_last > 36 * 3600:
            continue  # nessuna lettura recente: non e' una mossa "di oggi"
        ref = None
        for t, p in reversed(pts[:-1]):          # lettura piu' vicina a 24 ore prima
            if t_last - t >= hours * 3600:
                ref = p
                break
        if ref is None:
            if hours > 12:
                continue  # storico troppo corto per la variazione settimanale
            ref = pts[-2][1]
        chg = (last - ref) / ref * 100
        if abs(chg) < 0.05:
            continue
        res.append({**it, "last": last, "chg": chg})
    res.sort(key=lambda r: abs(r["chg"]), reverse=True)
    return res[:top]


def clean_title(t):
    t = re.sub(r"\s*\([^)]*\)", "", t or "").strip()
    return re.sub(r"\s+", " ", t)


# ---------------------------------------------------------------- grafica
def fit(draw, text, fnt, maxw):
    if draw.textlength(text, font=fnt) <= maxw:
        return text
    while text and draw.textlength(text + "…", font=fnt) > maxw:
        text = text[:-1]
    return text.rstrip() + "…"


def gradient(w, h, c1, c2):
    base = Image.new("RGB", (w, h), c1)
    top = Image.new("RGB", (w, h), c2)
    mask = Image.linear_gradient("L").resize((w, h)).rotate(90, expand=False)
    mask = Image.linear_gradient("L").rotate(90).resize((w, h))
    return Image.composite(top, base, mask)


def background():
    bg = Image.new("RGB", (W, H), (10, 8, 22))
    glow = Image.new("RGB", (W, H), (0, 0, 0))
    d = ImageDraw.Draw(glow)
    d.ellipse((-300, -380, 800, 620), fill=(106, 61, 240))
    d.ellipse((1000, -250, 1900, 560), fill=(15, 169, 104))
    d.ellipse((500, 520, 1500, 1300), fill=(255, 90, 170))
    glow = glow.filter(ImageFilter.GaussianBlur(190))
    return Image.blend(bg, Image.eval(glow, lambda v: int(v * 0.55)), 0.6).convert("RGBA")


def badge(size, brand):
    c1, c2 = (hexrgb(x) for x in BRAND_COLORS.get(brand, ("#7c4dff", "#0fa968")))
    g = gradient(size, size, c1, c2).convert("RGBA")
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, size - 1, size - 1), radius=int(size * 0.3), fill=255)
    g.putalpha(mask)
    d = ImageDraw.Draw(g)
    ab = BRAND_ABBR.get(brand, re.sub(r"[^A-Za-z0-9]", "", brand)[:2].upper() or "?")
    f = font("ExtraBold", int(size * 0.42))
    d.text((size / 2, size / 2), ab, font=f, fill="white", anchor="mm")
    return g


def render(rows, when, out_png):
    img = background()
    d = ImageDraw.Draw(img)
    # intestazione
    f_logo = font("ExtraBold", 46)
    d.text((80, 62), "Hype", font=f_logo, fill=(154, 124, 255))
    d.text((80 + d.textlength("Hype", font=f_logo), 62), "wise", font=f_logo, fill=(59, 232, 160))
    d.text((W - 80, 74), when.strftime("%B %d, %Y").replace(" 0", " "), font=font("Medium", 30), fill=(205, 199, 236), anchor="ra")
    # titolo
    d.text((80, 128), HEAD[MODE][0], font=font("ExtraBold", 74), fill="white")
    d.text((80, 208), HEAD[MODE][1], font=font("ExtraBold", 74), fill=(59, 232, 160))
    d.text((80, 300), ("US resale market · 7-day change" if MODE == "weekly" else "US resale market · average price in USD"), font=font("Medium", 28), fill=(205, 199, 236))
    # righe
    y0, rh, gap = 362, 72, 12
    f_name, f_price, f_chg = font("SemiBold", 34), font("Bold", 38), font("Bold", 30)
    for i, r in enumerate(rows):
        y = y0 + i * (rh + gap)
        card = Image.new("RGBA", (W - 160, rh), (255, 255, 255, 0))
        cd = ImageDraw.Draw(card)
        cd.rounded_rectangle((0, 0, W - 161, rh - 1), radius=22, fill=(255, 255, 255, 22), outline=(255, 255, 255, 40), width=2)
        img.alpha_composite(card, (80, y))
        b = badge(54, r["brand"])
        img.alpha_composite(b, (96, y + 10))
        d.text((170, y + rh / 2), fit(d, clean_title(r["title"]), f_name, 760), font=f_name, fill="white", anchor="lm")
        d.text((1150, y + rh / 2), "${:,.0f}".format(r["last"]), font=f_price, fill="white", anchor="rm")
        up = r["chg"] > 0
        col = (59, 232, 160) if up else (255, 107, 146)
        txt = ("+" if up else "−") + "{:.1f}%".format(abs(r["chg"]))
        pw = d.textlength(txt, font=f_chg) + 70
        px0, px1 = W - 96 - pw, W - 96
        d.rounded_rectangle((px0, y + 12, px1, y + rh - 12), radius=26, fill=(col[0], col[1], col[2], 45) if False else tuple(int(c * 0.22 + 10 * 0.78) for c in col))
        tri = [(px0 + 22, y + rh / 2 + 8), (px0 + 42, y + rh / 2 + 8), (px0 + 32, y + rh / 2 - 9)] if up else \
              [(px0 + 22, y + rh / 2 - 8), (px0 + 42, y + rh / 2 - 8), (px0 + 32, y + rh / 2 + 9)]
        d.polygon(tri, fill=col)
        d.text((px1 - 22, y + rh / 2), txt, font=f_chg, fill=col, anchor="rm")
    # piede
    d.text((80, H - 44), SITE, font=font("Bold", 28), fill=(154, 124, 255), anchor="lm")
    d.text((W - 80, H - 44), "Estimates from market data · not financial advice", font=font("Medium", 24), fill=(163, 157, 194), anchor="rm")
    img.convert("RGB").save(out_png, "PNG", optimize=True)


def render_portrait(rows, when, out_png):
    """Formato verticale 1080x1350 per Instagram."""
    global W, H
    ow, oh = W, H
    W, H = 1080, 1350
    try:
        img = background()
    finally:
        W, H = ow, oh
    pw_, ph_ = 1080, 1350
    d = ImageDraw.Draw(img)
    f_logo = font("ExtraBold", 54)
    d.text((70, 70), "Hype", font=f_logo, fill=(154, 124, 255))
    d.text((70 + d.textlength("Hype", font=f_logo), 70), "wise", font=f_logo, fill=(59, 232, 160))
    d.text((pw_ - 70, 84), when.strftime("%b %d, %Y").replace(" 0", " "), font=font("Medium", 30), fill=(205, 199, 236), anchor="ra")
    d.text((70, 170), HEAD[MODE][0], font=font("ExtraBold", 84), fill="white")
    d.text((70, 262), HEAD[MODE][1], font=font("ExtraBold", 84), fill=(59, 232, 160))
    d.text((70, 372), ("US resale market · 7-day change" if MODE == "weekly" else "US resale market · average price in USD"), font=font("Medium", 30), fill=(205, 199, 236))
    y0, rh, gap = 424, 150, 8
    f_name, f_price, f_chg = font("SemiBold", 34), font("Bold", 44), font("Bold", 34)
    for i, r in enumerate(rows):
        y = y0 + i * (rh + gap)
        card = Image.new("RGBA", (pw_ - 140, rh), (255, 255, 255, 0))
        ImageDraw.Draw(card).rounded_rectangle((0, 0, pw_ - 141, rh - 1), radius=28, fill=(255, 255, 255, 22), outline=(255, 255, 255, 40), width=2)
        img.alpha_composite(card, (70, y))
        img.alpha_composite(badge(86, r["brand"]), (92, y + 32))
        d.text((204, y + 44), fit(d, clean_title(r["title"]), f_name, 780), font=f_name, fill="white", anchor="lm")
        d.text((204, y + 100), "${:,.0f}".format(r["last"]), font=f_price, fill=(205, 199, 236), anchor="lm")
        up = r["chg"] > 0
        col = (59, 232, 160) if up else (255, 107, 146)
        txt = ("+" if up else "−") + "{:.1f}%".format(abs(r["chg"]))
        tw = d.textlength(txt, font=f_chg) + 72
        x1 = pw_ - 92; x0 = x1 - tw
        d.rounded_rectangle((x0, y + 82, x1, y + 126), radius=22, fill=tuple(int(c * 0.22 + 10 * 0.78) for c in col))
        d.polygon([(x0 + 18, y + 112), (x0 + 38, y + 112), (x0 + 28, y + 94)] if up else [(x0 + 18, y + 96), (x0 + 38, y + 96), (x0 + 28, y + 114)], fill=col)
        d.text((x1 - 18, y + 104), txt, font=f_chg, fill=col, anchor="rm")
    d.text((70, ph_ - 80), SITE, font=font("Bold", 30), fill=(154, 124, 255), anchor="lm")
    d.text((70, ph_ - 40), "Estimates from market data · not financial advice", font=font("Medium", 24), fill=(163, 157, 194), anchor="lm")
    img.convert("RGB").save(out_png, "PNG", optimize=True)


def caption(rows, when):
    lines = [("Wildest sneaker price moves this week (US resale):" if MODE == "weekly" else "Biggest sneaker price moves today (US resale):"), ""]
    for r in rows:
        arrow = "▲" if r["chg"] > 0 else "▼"
        lines.append("%s %s  $%s  %s%.1f%%" % (arrow, clean_title(r["title"]), "{:,.0f}".format(r["last"]),
                                               "+" if r["chg"] > 0 else "−", abs(r["chg"])))
    lines += ["", "Full charts and price history: https://%s" % SITE, "Estimates only, not financial advice.",
              "#sneakers #sneakerhead #resale"]
    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--demo", action="store_true")
    ap.add_argument("--out", default="social")
    ap.add_argument("--mode", choices=["auto", "daily", "weekly"], default="auto")
    a = ap.parse_args()
    items = load_demo() if a.demo else load_real()
    global MODE
    when = datetime.now(timezone.utc)
    MODE = pick_mode(a.mode, when)
    rows = movers(items, hours=7 * 24 - 12) if MODE == "weekly" else movers(items)
    if MODE == "weekly" and len(rows) < 3:
        MODE = "daily"; rows = movers(items)   # poco storico: ripiega sul giornaliero
    if len(rows) < 3:
        print("Pochi movimenti da mostrare (%d): nessuna immagine creata." % len(rows))
        sys.exit(0)
    os.makedirs(a.out, exist_ok=True)
    render(rows, when, os.path.join(a.out, "today.png"))
    render_portrait(rows, when, os.path.join(a.out, "today-ig.png"))
    with open(os.path.join(a.out, "caption.txt"), "w", encoding="utf-8") as f:
        f.write(caption(rows, when))
    print("Creata immagine con %d scarpe" % len(rows))


if __name__ == "__main__":
    main()
