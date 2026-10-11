"""
Misura la QUALITA' DEI DATI di KicksDB per ogni modello (watchlist attuale
+ candidati emersi dalla ricerca di mercato USA).

Per ogni modello: prende i primi N risultati, tiene solo quelli che
passano l'identita' (brand + sneaker + modello, stessa logica del
validatore) e misura quanti hanno SKU, prezzo medio > 0, weekly_orders > 0
e aggiornamento recente.  Output: score 0-100 + JSON.

Variabili: KICKSDB_API_KEY (obbligatoria), OUTPUT_PATH (opzionale).
"""
import json
import os
import statistics
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import validate_watchlist as vw  # noqa: E402

LIMIT = 20

# (brand, nome, modello_per_validazione, query, origine)
CANDIDATES = [
    ("Jordan", "Air Jordan 6", "Jordan 6", "Jordan 6"),
    ("Jordan", "Air Jordan 13", "Jordan 13", "Jordan 13"),
    ("Nike", "Total 90", "Total 90", "Nike Total 90"),
    ("Nike", "Kobe 6 Protro", "Kobe 6", "Nike Kobe 6"),
    ("Nike", "Ja 3", "Ja 3", "Nike Ja 3"),
    ("Nike", "Mind 001", "Mind 001", "Nike Mind 001"),
    ("Nike", "Air Max 95", "Air Max 95", "Nike Air Max 95"),
    ("Nike", "Air Max 90", "Air Max 90", "Nike Air Max 90"),
    ("Nike", "Air Max 1", "Air Max 1", "Nike Air Max 1"),
    ("Converse", "Shai 001", "Shai 001", "Converse Shai 001"),
    ("Puma", "Speedcat", "Speedcat", "Puma Speedcat"),
    ("adidas", "Handball Spezial", "Handball Spezial", "adidas Handball Spezial"),
    ("adidas", "Campus 00s", "Campus 00s", "adidas Campus 00s"),
    ("adidas", "Superstar", "Superstar", "adidas Superstar"),
    ("adidas", "Tokyo", "Tokyo", "adidas Tokyo"),
    ("New Balance", "550", "550", "New Balance 550"),
    ("New Balance", "740", "740", "New Balance 740"),
    ("New Balance", "1000", "1000", "New Balance 1000"),
    ("Saucony", "ProGrid Omni 9", "Omni 9", "Saucony Omni 9"),
    ("Saucony", "Triumph 4", "Triumph 4", "Saucony Triumph 4"),
    ("Saucony", "Jazz", "Jazz", "Saucony Jazz"),
    ("ASICS", "Gel-Kayano 14", "Kayano 14", "ASICS Kayano 14"),
    ("ASICS", "Gel-Nimbus 10.1", "Nimbus 10.1", "ASICS Gel Nimbus 10.1"),
    ("ASICS", "Gel-Quantum 360", "Quantum 360", "ASICS Gel Quantum 360"),
    ("Vans", "Authentic", "Authentic", "Vans Authentic"),
    ("Vans", "Knu Skool", "Knu", "Vans Knu"),
    ("Mizuno", "Wave Prophecy", "Wave Prophecy", "Mizuno Wave Prophecy"),
    ("Salomon", "XT-Whisper", "XT Whisper", "Salomon XT Whisper"),
    ("Salomon", "XT-Slate", "XT Slate", "Salomon XT Slate"),
    ("HOKA", "Mafate", "Mafate", "HOKA Mafate"),
    ("Crocs", "Classic Clog", "Classic Clog", "Crocs Classic Clog"),
]


def fetch(api_key, query):
    url = "https://api.kicks.dev/v3/stockx/products?" + urllib.parse.urlencode(
        {"query": query, "limit": LIMIT}
    )
    req = urllib.request.Request(url, headers={"Authorization": api_key})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read().decode()).get("data", [])
    except Exception as e:  # noqa: BLE001
        print(f"  errore {query}: {e}")
        return None


def age_days(value):
    try:
        text = str(value).replace("Z", "+00:00")
        if "." in text:
            head, rest = text.split(".", 1)
            digits = "".join(c for c in rest if c.isdigit())[:6]
            tail = rest[len("".join(c for c in rest if c.isdigit())):]
            text = f"{head}.{digits}{tail}"
        dt = datetime.fromisoformat(text)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return (datetime.now(timezone.utc) - dt).days
    except Exception:  # noqa: BLE001
        return None


def score_entry(brand, name, vmodel, query, products):
    if products is None:
        return {"brand": brand, "name": name, "query": query, "error": True, "score": 0}
    matched = []
    for p in products:
        ev = vw.evaluate_candidate(brand, vmodel, p)
        if ev["identity_match"]:
            matched.append(p)
    n = len(matched)
    if n == 0:
        return {"brand": brand, "name": name, "query": query, "returned": len(products),
                "identity_matched": 0, "score": 0}

    def frac(pred):
        return sum(1 for p in matched if pred(p)) / n

    full = frac(lambda p: vw.has_valid_sku(p) and vw.has_valid_price(p))
    orders = [p.get("weekly_orders") for p in matched
              if isinstance(p.get("weekly_orders"), (int, float))]
    active = frac(lambda p: isinstance(p.get("weekly_orders"), (int, float))
                  and p["weekly_orders"] > 0)
    fresh = frac(lambda p: (age_days(p.get("updated_at")) is not None
                            and age_days(p.get("updated_at")) <= 90))
    volume = min(n, 10) / 10
    score = round(100 * (0.30 * full + 0.30 * active + 0.15 * fresh + 0.25 * volume))
    return {
        "brand": brand, "name": name, "query": query,
        "returned": len(products), "identity_matched": n,
        "full_data_pct": round(full * 100), "active_pct": round(active * 100),
        "fresh_pct": round(fresh * 100),
        "median_weekly_orders": statistics.median(orders) if orders else 0,
        "max_weekly_orders": max(orders) if orders else 0,
        "sample_titles": [p.get("title") for p in matched[:3]],
        "score": score,
    }


def main():
    api_key = os.environ["KICKSDB_API_KEY"]
    out = os.environ.get("OUTPUT_PATH", "candidate_scores.json")
    rows = []
    for source, items in (("watchlist", [(b, d, v, q) for b, d, v, q in vw.WATCHLIST]),
                          ("candidate", CANDIDATES)):
        for brand, name, vmodel, query in items:
            print(f"[{source}] {query}")
            row = score_entry(brand, name, vmodel, query, fetch(api_key, query))
            row["source"] = source
            rows.append(row)
            print(f"   score={row['score']} match={row.get('identity_matched')}")
    rows.sort(key=lambda r: -r["score"])
    with open(out, "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2, ensure_ascii=False)
    print("salvato", out)


if __name__ == "__main__":
    main()
