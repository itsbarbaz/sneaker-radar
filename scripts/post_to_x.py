"""Hypewise - pubblica su X l'immagine del giorno (API ufficiale). Sicuro per default:
 - senza chiavi o senza X_AUTOPOST=true non fa nulla
 - non pubblica due volte lo stesso giorno (segna la data in social/x_last.txt)
Variabili: X_API_KEY, X_API_SECRET, X_ACCESS_TOKEN, X_ACCESS_SECRET, X_POST_KIND (spotlight|movers), DRY_RUN=1"""
import os, re, sys
from datetime import datetime, timezone

DIR = sys.argv[1] if len(sys.argv) > 1 else "social"
KIND = os.environ.get("X_POST_KIND", "spotlight")
DRY = os.environ.get("DRY_RUN") == "1"

def weighted_len(t):
    t = re.sub(r"https?://\S+", "x" * 23, t)
    return sum(2 if ord(c) > 0x2000 else 1 for c in t)

def fit(text):
    """Tiene il testo entro 280 caratteri (i link contano 23): prima toglie gli hashtag, poi accorcia."""
    if weighted_len(text) <= 280: return text
    lines = [l for l in text.split("\n") if not l.startswith("#")]
    text = "\n".join(lines).strip()
    while weighted_len(text) > 280 and len(lines) > 3:
        lines.pop(2); text = "\n".join(lines).strip()
    return text if weighted_len(text) <= 280 else text[:270].rstrip() + "…"

def main():
    img, txt = (("spotlight.png", "spotlight.txt") if KIND == "spotlight" else ("today.png", "caption.txt"))
    ip, tp = os.path.join(DIR, img), os.path.join(DIR, txt)
    if not (os.path.exists(ip) and os.path.exists(tp)):
        print("Nessun contenuto da pubblicare (%s)." % KIND); return
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    last = os.path.join(DIR, "x_last.txt")
    if os.path.exists(last) and open(last).read().strip() == today:
        print("Gia' pubblicato oggi."); return
    text = fit(open(tp, encoding="utf-8").read().strip())
    print("Testo (%d):\n%s" % (weighted_len(text), text))
    keys = [os.environ.get(k, "") for k in ("X_API_KEY", "X_API_SECRET", "X_ACCESS_TOKEN", "X_ACCESS_SECRET")]
    if DRY or not all(keys):
        print("Simulazione: nessuna pubblicazione (%s)." % ("DRY_RUN" if DRY else "chiavi mancanti")); return
    import tweepy
    api = tweepy.API(tweepy.OAuth1UserHandler(*keys))
    media = api.media_upload(filename=ip)
    client = tweepy.Client(consumer_key=keys[0], consumer_secret=keys[1], access_token=keys[2], access_token_secret=keys[3])
    r = client.create_tweet(text=text, media_ids=[media.media_id])
    open(last, "w").write(today)
    print("Pubblicato, id:", r.data.get("id"))

if __name__ == "__main__":
    main()
