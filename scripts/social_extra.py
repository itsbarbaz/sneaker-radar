"""Hypewise - immagini extra: avatar, banner X e post a tema (sneaker generica originale)."""
import os, sys
from PIL import Image, ImageDraw, ImageFilter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import social_image as S

SITE = S.SITE
def bg(w, h):
    old = (S.W, S.H); S.W, S.H = w, h
    im = S.background(); S.W, S.H = old
    return im

def shoe(w, tilt=0, color=(255, 255, 255)):
    """Sneaker generica (forma originale) disegnata su 240x120 e scalata."""
    sc = 4; im = Image.new("RGBA", (240 * sc, 130 * sc), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    def P(pts): return [(x * sc, y * sc) for x, y in pts]
    upper = [(8,84),(10,74),(20,70),(52,60),(66,44),(74,26),(86,22),(104,31),(124,40),(160,45),(196,52),(222,70),(232,88),(226,92),(14,92)]
    d.polygon(P(upper), fill=color + (245,))
    d.polygon(P([(6,90),(230,90),(236,104),(230,116),(20,116),(8,108)]), fill=(245, 245, 255, 255))
    d.line(P([(8,100),(234,100)]), fill=(120, 80, 255, 255), width=3 * sc)
    for a, b in [((96,38),(106,54)),((110,44),(120,59)),((124,49),(133,63))]:
        d.line(P([a, b]), fill=(40, 20, 90, 150), width=4 * sc)
    d.line(P([(150,78),(190,70)]), fill=(15, 169, 104, 255), width=5 * sc)
    im = im.resize((w, int(w * 130 / 240)), Image.LANCZOS)
    return im.rotate(tilt, expand=True, resample=Image.BICUBIC)

def glow_shoe(base, cx, cy, w, tilt=-8):
    g = Image.new("RGBA", base.size, (0, 0, 0, 0))
    ImageDraw.Draw(g).ellipse((cx - w * .55, cy - w * .25, cx + w * .55, cy + w * .35), fill=(124, 77, 255, 150))
    base.alpha_composite(g.filter(ImageFilter.GaussianBlur(70)))
    s = shoe(w, tilt); base.alpha_composite(s, (int(cx - s.width / 2), int(cy - s.height / 2)))

def txt(d, xy, t, f, fill="white", anchor="la"): d.text(xy, t, font=f, fill=fill, anchor=anchor)

def logo(d, x, y, size):
    f = S.font("ExtraBold", size); a, b = "Hype", "wise"
    d.text((x, y), a, font=f, fill=(150, 120, 255)); d.text((x + d.textlength(a, font=f), y), b, font=f, fill=(52, 235, 160))

def avatar(out):
    im = bg(500, 500); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, 499, 499), 120, outline=(255, 255, 255, 30), width=2)
    glow_shoe(im, 250, 250, 360, -10)
    im.convert("RGB").save(out)

def banner(out):
    im = bg(1500, 500); d = ImageDraw.Draw(im)
    logo(d, 80, 120, 110)
    txt(d, (84, 260), "Sneaker prices, signals & history.", S.font("SemiBold", 44))
    txt(d, (84, 330), "Cop / Wait / Sell - built in public on GitHub", S.font("Medium", 32), (190, 185, 230))
    glow_shoe(im, 1160, 270, 520, -8)
    im.convert("RGB").save(out)

def card(out, kicker, l1, l2, sub, foot="Estimates only, not financial advice"):
    im = bg(1600, 900); d = ImageDraw.Draw(im)
    logo(d, 80, 60, 56)
    txt(d, (80, 200), kicker, S.font("Bold", 34), (52, 235, 160))
    txt(d, (80, 262), l1, S.font("ExtraBold", 96)); txt(d, (80, 370), l2, S.font("ExtraBold", 96), (52, 235, 160))
    y = 520
    for line in sub:
        txt(d, (84, y), line, S.font("Medium", 36), (205, 200, 235)); y += 56
    glow_shoe(im, 1210, 560, 600, -9)
    txt(d, (80, 842), SITE, S.font("Bold", 30), (150, 120, 255)); txt(d, (1520, 842), foot, S.font("Medium", 24), (160, 155, 195), "ra")
    im.convert("RGB").save(out)

def signal(out):
    im = bg(1600, 900); d = ImageDraw.Draw(im)
    logo(d, 80, 60, 56)
    txt(d, (80, 190), "One glance, three answers", S.font("ExtraBold", 80))
    items = [("COP", "price low in its range", (52, 235, 160)), ("WAIT", "no clear edge", (255, 196, 61)), ("SELL", "price high in its range", (255, 92, 130))]
    for i, (k, s, c) in enumerate(items):
        x = 80 + i * 500
        ov = Image.new("RGBA", im.size, (0, 0, 0, 0)); ImageDraw.Draw(ov).rounded_rectangle((x, 340, x + 450, 640), 36, fill=(255, 255, 255, 22), outline=c, width=4)
        im.alpha_composite(ov); d = ImageDraw.Draw(im)
        txt(d, (x + 225, 450), k, S.font("ExtraBold", 110), c, "mm"); txt(d, (x + 225, 560), s, S.font("Medium", 30), (225, 222, 245), "mm")
    txt(d, (80, 700), "5 factors: range, z-score, momentum, trend, drawdown. Beta.", S.font("Medium", 34), (205, 200, 235))
    txt(d, (80, 842), SITE, S.font("Bold", 30), (150, 120, 255)); txt(d, (1520, 842), "Estimates only, not financial advice", S.font("Medium", 24), (160, 155, 195), "ra")
    im.convert("RGB").save(out)

def og(out):
    im = bg(1200, 630); d = ImageDraw.Draw(im)
    logo(d, 70, 110, 96)
    txt(d, (74, 250), "Sneaker prices, history", S.font("ExtraBold", 54)); txt(d, (74, 316), "& Cop / Wait / Sell signals", S.font("ExtraBold", 54), (52, 235, 160))
    txt(d, (76, 410), "Daily US resale data. Estimates, not financial advice.", S.font("Medium", 28), (205, 200, 235))
    glow_shoe(im, 930, 330, 420, -8)
    txt(d, (76, 560), SITE, S.font("Bold", 28), (150, 120, 255))
    im.convert("RGB").save(out)


if __name__ == "__main__":
    o = sys.argv[1] if len(sys.argv) > 1 else "."; os.makedirs(o, exist_ok=True)
    avatar(o + "/x-avatar.png"); banner(o + "/x-banner.png")
    card(o + "/post-intro.png", "BUILDING IN PUBLIC", "Sneaker prices,", "tracked daily.", ["Open project on GitHub.", "Charts, history and a Cop/Wait/Sell signal.", "Feedback welcome."])
    card(o + "/post-github.png", "OPEN PROJECT", "Follow the build", "on GitHub.", ["github.com/itsbarbaz/sneaker-radar", "Also on Reddit - come say hi.", "Investors & partners: get in touch."])
    signal(o + "/post-signal.png"); og(o + "/og-image.png")
