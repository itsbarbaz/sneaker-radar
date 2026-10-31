"""
Sneaker Radar - pipeline principale.

Per ogni modello della WATCHLIST (scripts/validate_watchlist.py):
  1. cerca su KicksDB
  2. controlla l'IDENTITA' (brand + sneaker + modello)  -> scarta il resto
  3. controlla la COERENZA (scripts/advanced_consistency.py)
  4. salva su Supabase: prodotto sempre, prezzo solo se approvato

Variabili d'ambiente:
  KICKSDB_API_KEY, SUPABASE_URL, SUPABASE_SECRET_KEY   obbligatorie
  DRY_RUN=1          non scrive su Supabase (solo log)
  MAX_QUERIES_PER_RUN  ricerche per run (default 30): la watchlist ruota ogni
                       giorno, cosi' il piano gratuito KicksDB (1000/mese) basta
  SEARCH_TERM        se presente, cerca solo questo termine (niente gate identita')
  EXPECTED_GENDER / EXPECTED_COLORWAY / EXPECTED_CONDITION   opzionali
"""

import json
import os
import re
import sys
import time
from datetime import date
import urllib.error
import urllib.parse
import urllib.request

sys.path.insert(
    0,
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"),
)

import validate_watchlist as vw  # noqa: E402
from advanced_consistency import run_advanced_consistency  # noqa: E402

try:
    sys.stdout.reconfigure(line_buffering=True)
except Exception:
    pass

PER_QUERY_LIMIT = 10
PAUSE_BETWEEN_QUERIES = 0.3


def log(*args):
    print(*args, flush=True)


# ------------------------------------------------------------
# KICKSDB
# ------------------------------------------------------------

def fetch_products(api_key, query):
    url = "https://api.kicks.dev/v3/stockx/products?" + urllib.parse.urlencode(
        {"query": query, "limit": PER_QUERY_LIMIT}
    )
    request = urllib.request.Request(url, headers={"Authorization": api_key})
    with urllib.request.urlopen(request, timeout=60) as response:
        data = json.loads(response.read().decode())
    if isinstance(data, dict):
        return data.get("data") or []
    return data if isinstance(data, list) else []


# ------------------------------------------------------------
# SUPABASE
# ------------------------------------------------------------

def reference_price_for(supabase, product_id):
    rows = (
        supabase.table("price_history")
        .select("price")
        .eq("product_id", product_id)
        .order("created_at", desc=True)
        .limit(10)
        .execute()
    ).data or []
    prices = []
    for row in rows:
        try:
            value = float(row.get("price"))
        except (TypeError, ValueError):
            continue
        if value > 0:
            prices.append(value)
    return sum(prices) / len(prices) if prices else None


EXTRAS_OK = False  # diventa True se la tabella products ha le colonne extra


def detect_extras(supabase):
    """Controlla se products ha image_url, stockx_url, gender, release_year."""
    global EXTRAS_OK
    try:
        supabase.table("products").select(
            "image_url,stockx_url,gender,release_year"
        ).limit(1).execute()
        EXTRAS_OK = True
    except Exception:
        EXTRAS_OK = False
    log("🖼️  Colonne foto/dettagli:", "presenti" if EXTRAS_OK else "assenti (si salvano solo i dati base)")


def product_extras(product):
    """Foto, link StockX semplice, genere e anno di uscita, se KicksDB li fornisce."""
    year = None
    for text in (product.get("secondary_title"), product.get("title")):
        found = re.search(r"\((19|20)\d\d\)", text or "")
        if found:
            year = int(found.group(0).strip("()"))
            break
    slug = product.get("slug")
    extras = {
        "image_url": product.get("image") or None,
        "stockx_url": ("https://stockx.com/" + slug) if slug else None,
        "gender": product.get("gender") or None,
        "release_year": year,
    }
    return {k: v for k, v in extras.items() if v is not None}


def get_or_create_product(supabase, product):
    sku = product.get("sku")
    columns = "id,image_url" if EXTRAS_OK else "id"
    existing = supabase.table("products").select(columns).eq("sku", sku).execute()
    if existing.data:
        row = existing.data[0]
        if EXTRAS_OK and not row.get("image_url"):
            extras = product_extras(product)
            if extras:
                supabase.table("products").update(extras).eq("id", row["id"]).execute()
        return row["id"], True
    new_row = {
        "title": product.get("title"),
        "brand": product.get("brand"),
        "sku": sku,
        "source": "kicksdb",
    }
    if EXTRAS_OK:
        new_row.update(product_extras(product))
    created = supabase.table("products").insert(new_row).execute()
    if not created.data:
        raise RuntimeError("Product insert failed for sku " + str(sku))
    return created.data[0]["id"], False


# ------------------------------------------------------------
# PROCESS ONE PRODUCT
# ------------------------------------------------------------

def process_product(product, target, supabase, dry_run, seen_skus, expected, stats):
    title = product.get("title")
    sku = product.get("sku")

    if target is not None:
        brand, validation_model = target
        identity = vw.evaluate_candidate(brand, validation_model, product)
        if not identity["identity_match"]:
            stats["identity_rejected"] += 1
            log(f"   ⏭️  identita' non valida, scartato: {title} ({', '.join(identity['reasons'])})")
            return

    if not vw.has_valid_sku(product):
        stats["no_sku"] += 1
        log(f"   ⏭️  senza SKU, scartato: {title}")
        return

    if sku in seen_skus:
        stats["duplicates"] += 1
        return
    seen_skus.add(sku)

    product_id = None
    reference = None
    if not dry_run:
        product_id, existed = get_or_create_product(supabase, product)
        stats["existing" if existed else "created"] += 1
        if existed:
            reference = reference_price_for(supabase, product_id)

    consistency = run_advanced_consistency(
        product,
        reference_price=reference,
        expected_gender=expected["gender"],
        expected_colorway=expected["colorway"],
        expected_condition=expected["condition"],
    )

    approved = consistency["approved"]
    reasons = consistency["review_reasons"]
    price = product.get("avg_price")

    if approved:
        stats["approved"] += 1
        log(f"   ✅ {title} | {sku} | ${price}")
    else:
        stats["review"] += 1
        log(f"   ⚠️  REVIEW {title} | {sku} | motivi: {', '.join(reasons)}")

    if approved and vw.has_valid_price(product):
        if dry_run:
            stats["prices_saved"] += 1
        else:
            supabase.table("price_history").insert({
                "product_id": product_id,
                "price": float(price),
                "currency": "USD",
            }).execute()
            stats["prices_saved"] += 1
    else:
        stats["prices_skipped"] += 1


# ------------------------------------------------------------
# MAIN
# ------------------------------------------------------------

def main():
    api_key = os.environ["KICKSDB_API_KEY"]
    dry_run = os.environ.get("DRY_RUN", "").lower() in ("1", "true", "yes")

    supabase = None
    if not dry_run:
        from supabase import create_client
        supabase = create_client(
            os.environ["SUPABASE_URL"], os.environ["SUPABASE_SECRET_KEY"]
        )
        log("🔥 Supabase connected!")
        detect_extras(supabase)
    else:
        log("🧪 DRY_RUN: nessuna scrittura su Supabase")

    expected = {
        "gender": os.environ.get("EXPECTED_GENDER"),
        "colorway": os.environ.get("EXPECTED_COLORWAY"),
        "condition": os.environ.get("EXPECTED_CONDITION"),
    }

    search_term = os.environ.get("SEARCH_TERM")
    if search_term:
        targets = [(search_term, None)]
    else:
        targets = [
            (query, (brand, validation_model))
            for brand, _display, validation_model, query in vw.WATCHLIST
        ]

    if not search_term:
        batch = int(os.environ.get("MAX_QUERIES_PER_RUN", "30"))
        if 0 < batch < len(targets):
            start = (date.today().toordinal() * batch) % len(targets)
            targets = [targets[(start + i) % len(targets)] for i in range(batch)]

    log(f"📋 Ricerche da eseguire: {len(targets)}")

    stats = {k: 0 for k in (
        "created", "existing", "approved", "review", "identity_rejected",
        "no_sku", "duplicates", "prices_saved", "prices_skipped",
        "queries_ok", "queries_failed",
    )}
    seen_skus = set()

    for query, target in targets:
        log("")
        log(f"🔎 {query}")
        try:
            products = fetch_products(api_key, query)
        except urllib.error.HTTPError as error:
            stats["queries_failed"] += 1
            log(f"   ❌ errore KicksDB: {error}")
            if error.code in (401, 403, 429):
                log("   🛑 chiave non valida o quota esaurita: mi fermo per non sprecare richieste")
                break
            continue
        except (urllib.error.URLError, TimeoutError, ValueError) as error:
            stats["queries_failed"] += 1
            log(f"   ❌ errore KicksDB: {error}")
            continue

        stats["queries_ok"] += 1
        log(f"   📦 {len(products)} risultati")

        for product in products:
            try:
                process_product(
                    product, target, supabase, dry_run, seen_skus, expected, stats
                )
            except Exception as error:  # un prodotto rotto non ferma la run
                stats["review"] += 1
                log(f"   ❌ errore su {product.get('title')}: {error!r}")

        time.sleep(PAUSE_BETWEEN_QUERIES)

    log("")
    log("=" * 60)
    log("📊 RIEPILOGO")
    for key, value in stats.items():
        log(f"  {key}: {value}")
    log("=" * 60)

    if stats["queries_ok"] == 0:
        log("❌ Nessuna query riuscita")
        sys.exit(1)


if __name__ == "__main__":
    main()
