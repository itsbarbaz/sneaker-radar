"""Hypewise - video verticale 9:16 (Reel/Short/X) "Biggest sneaker price moves today".
Uso: python scripts/social_video.py [--demo] [--out cartella]   (richiede ffmpeg e Pillow)"""
import argparse, os, subprocess, sys, tempfile
from datetime import datetime, timezone
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import social_image as S

VW, VH, FPS = 1080, 1920, 30
INTRO, STEP, T_ROWS, END = 1.6, 1.15, 1.6, 11.0
GREEN, VIOLET, MUTED = (59, 232, 160), (154, 124, 255), (205, 199, 236)

def ease(x):
    x = max(0.0, min(1.0, x)); return 1 - (1 - x) ** 3

def make_bg():
    ow, oh = S.W, S.H; S.W, S.H = VW, VH
    try: return S.background()
    finally: S.W, S.H = ow, oh

def row_layer(r, pct_shown):
    w, h = VW - 120, 190
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w - 1, h - 1), radius=34, fill=(255, 255, 255, 26), outline=(255, 255, 255, 50), width=2)
    im.alpha_composite(S.badge(108, r["brand"]), (28, 41))
    fn, fp, fc = S.font("SemiBold", 38), S.font("Bold", 54), S.font("Bold", 42)
    d.text((166, 62), S.fit(d, S.clean_title(r["title"]), fn, 640), font=fn, fill="white", anchor="lm")
    d.text((166, 128), "${:,.0f}".format(r["last"]), font=fp, fill=MUTED, anchor="lm")
    up = r["chg"] > 0; col = GREEN if up else (255, 107, 146)
    txt = ("+" if up else "−") + "{:.1f}%".format(abs(pct_shown))
    tw = d.textlength(txt, font=fc) + 76; x1 = w - 28; x0 = x1 - tw
    d.rounded_rectangle((x0, 92, x1, 152), radius=30, fill=tuple(int(c * .22 + 8) for c in col))
    d.polygon([(x0 + 20, 132), (x0 + 44, 132), (x0 + 32, 110)] if up else [(x0 + 20, 112), (x0 + 44, 112), (x0 + 32, 134)], fill=col)
    d.text((x1 - 22, 124), txt, font=fc, fill=col, anchor="rm")
    return im

def with_alpha(im, a):
    im = im.copy(); im.putalpha(im.getchannel("A").point(lambda v: int(v * a))); return im

def frame(bg, rows, when, t):
    img = bg.copy(); d = ImageDraw.Draw(img)
    a_in = ease(t / 0.8)
    off = int((1 - a_in) * 40)
    fl = S.font("ExtraBold", 64)
    lay = Image.new("RGBA", (VW, 520), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
    ld.text((60, 20), "Hype", font=fl, fill=VIOLET); ld.text((60 + ld.textlength("Hype", font=fl), 20), "wise", font=fl, fill=GREEN)
    ld.text((VW - 60, 36), when.strftime("%b %d, %Y").replace(" 0", " "), font=S.font("Medium", 32), fill=MUTED, anchor="ra")
    ld.text((60, 150), S.HEAD[S.MODE][0], font=S.font("ExtraBold", 96), fill="white")
    ld.text((60, 262), S.HEAD[S.MODE][1], font=S.font("ExtraBold", 96), fill=GREEN)
    ld.text((60, 392), ("US resale market · 7-day change" if S.MODE == "weekly" else "US resale · average price in USD"), font=S.font("Medium", 34), fill=MUTED)
    img.alpha_composite(with_alpha(lay, a_in), (0, 150 + off))
    y0 = 640
    for i, r in enumerate(rows):
        ts = T_ROWS + i * STEP
        if t < ts: continue
        p = ease((t - ts) / 0.55)
        shown = r["chg"] * ease((t - ts) / 0.9)
        layer = with_alpha(row_layer(r, shown), p)
        img.alpha_composite(layer, (60 + int((1 - p) * 120), y0 + i * 206))
    te = T_ROWS + len(rows) * STEP + 0.6
    if t >= te:
        p = ease((t - te) / 0.6)
        cta = Image.new("RGBA", (VW, 220), (0, 0, 0, 0)); cd = ImageDraw.Draw(cta)
        cd.text((VW / 2, 50), "Charts & price history", font=S.font("ExtraBold", 54), fill="white", anchor="mm")
        cd.text((VW / 2, 126), S.SITE, font=S.font("Bold", 38), fill=VIOLET, anchor="mm")
        cd.text((VW / 2, 190), "Estimates from market data · not financial advice", font=S.font("Medium", 26), fill=(163, 157, 194), anchor="mm")
        img.alpha_composite(with_alpha(cta, p), (0, 1700 - int((1 - p) * 20)))
    return img.convert("RGB")

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--demo", action="store_true"); ap.add_argument("--out", default="social")
    ap.add_argument("--mode", choices=["auto", "daily", "weekly"], default="auto")
    ap.add_argument("--still", type=float, help="salva solo un fotogramma a t secondi (test)")
    a = ap.parse_args()
    items = S.load_demo() if a.demo else S.load_real()
    when = datetime.now(timezone.utc)
    S.MODE = S.pick_mode(a.mode, when)
    rows = S.movers(items, hours=7 * 24 - 12) if S.MODE == "weekly" else S.movers(items)
    if S.MODE == "weekly" and len(rows) < 3:
        S.MODE = "daily"; rows = S.movers(items)
    if len(rows) < 3:
        print("Pochi movimenti: nessun video."); return
    os.makedirs(a.out, exist_ok=True); bg = make_bg()
    if a.still is not None:
        frame(bg, rows, when, a.still).save(os.path.join(a.out, "still.png")); return
    out = os.path.join(a.out, "today.mp4"); tmp = os.path.join(a.out, "tmp-render.mp4")
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "%dx%d" % (VW, VH),
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "medium", "-crf", "20",
                          "-movflags", "+faststart", tmp], stdin=subprocess.PIPE)
    for n in range(int(END * FPS)):
        t = n / FPS
        p.stdin.write(frame(bg, rows, when, t).tobytes())
    p.stdin.close()
    if p.wait() != 0: sys.exit("ffmpeg ha fallito")
    os.replace(tmp, out); print("Creato", out)

if __name__ == "__main__":
    main()
