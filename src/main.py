import os
import sys
import json
import urllib.request
import urllib.error

from supabase import create_client

# Forza l'output a comparire subito nei log di GitHub Actions
try:
    sys.stdout.reconfigure(line_buffering=True)
except Exception:
    pass


def log(*args):
    print(*args, flush=True)


def main():
    # =========================
    # SUPABASE
    # =========================

    supabase_url = os.environ["SUPABASE_URL"]
    supabase_key = os.environ["SUPABASE_SECRET_KEY"]

    supabase = create_client(supabase_url, supabase_key)

    log("🔥 Supabase connected!")

    # =========================
    # KICKSDB
    # =========================

    api_key = os.environ["KICKSDB_API_KEY"]

    # TEST: chiediamo semplicemente 1 prodotto
    url = "https://api.kicks.dev/v3/stockx/products?limit=1"

    request = urllib.request.Request(
        url,
        headers={"Authorization": api_key}
    )

    try:
        with urllib.request.urlopen(request) as response:
            data = json.loads(response.read().decode())

    except urllib.error.HTTPError as e:
        log("❌ KicksDB error:", e.code)
        log("Headers:", dict(e.headers))
        log("Body:", e.read().decode())
        raise

    log("🔥 KicksDB connected!")

    # =========================
    # STRUTTURA RISPOSTA (log corto)
    # =========================

    log("📡 Response type:", type(data).__name__)

    if isinstance(data, dict):
        log("🔑 Top-level keys:", list(data.keys()))
        products = data.get("data", [])
    elif isinstance(data, list):
        products = data
    else:
        products = []

    log(f"📦 Products returned: {len(products)}")

    if products:
        log("👟 First product keys:", list(products[0].keys()))

    # =========================
    # PROCESS PRODUCTS
    # =========================

    for product in products:
        title = product.get("title")
        sku = product.get("sku")
        price = product.get("avg_price")
        brand = product.get("brand")

        log(f"👟 {title}")
        log(f"SKU: {sku}")
        log(f"Price: {price}")

        if not sku:
            log("⚠️ Product has no SKU, skipping.")
            log("---")
            continue

        # =========================
        # CHECK PRODUCT
        # =========================

        existing = (
            supabase
            .table("products")
            .select("id")
            .eq("sku", sku)
            .execute()
        )

        if existing.data:
            product_id = existing.data[0]["id"]
            log(f"🔎 Found existing product with id {product_id}")

        else:
            log("🆕 Product not found in database.")
            log("💾 Saving product...")

            (
                supabase
                .table("products")
                .insert({
                    "title": title,
                    "brand": brand,
                    "sku": sku,
                    "source": "kicksdb"
                })
                .execute()
            )

            inserted = (
                supabase
                .table("products")
                .select("id")
                .eq("sku", sku)
                .execute()
            )

            if not inserted.data:
                raise RuntimeError(
                    "❌ Product was inserted but its ID could not be found."
                )

            product_id = inserted.data[0]["id"]
            log(f"✅ Product saved to Supabase with id {product_id}")

        # =========================
        # PRICE HISTORY
        # =========================

        if price is not None and price > 0:
            (
                supabase
                .table("price_history")
                .insert({
                    "product_id": product_id,
                    "price": price,
                    "currency": "USD"
                })
                .execute()
            )

            log("💰 Price saved to price_history!")

        else:
            log("⚠️ Price is 0 or missing, so it was not saved.")

        log("---")

    log("✅ Done.")


if __name__ == "__main__":
    main()
