import os
import json
import urllib.request
import urllib.error

from supabase import create_client


def main():
    # =========================
    # SUPABASE
    # =========================

    supabase_url = os.environ["SUPABASE_URL"]
    supabase_key = os.environ["SUPABASE_SECRET_KEY"]

    supabase = create_client(
        supabase_url,
        supabase_key
    )

    print("🔥 Supabase connected!")

    # =========================
    # KICKSDB
    # =========================

    api_key = os.environ["KICKSDB_API_KEY"]

    url = (
        "https://api.kicks.dev/v3/stockx/products"
        "?query=Nike%20Air%20Force%201%20Low&limit=1"
    )

    request = urllib.request.Request(
        url,
        headers={
            "Authorization": api_key
        }
    )

    try:
        with urllib.request.urlopen(request) as response:
            data = json.loads(
                response.read().decode()
            )

    except urllib.error.HTTPError as e:
        print("❌ KicksDB error:", e.code)
        print("Headers:", dict(e.headers))
        print("Body:", e.read().decode())
        raise

    print("🔥 KicksDB connected!")

    print("📡 KicksDB response:")
    print(json.dumps(data, indent=2))

    # =========================
    # GET PRODUCTS
    # =========================

    products = data.get("data", [])

    print(f"📦 Products returned: {len(products)}")

    # =========================
    # PROCESS PRODUCTS
    # =========================

    for product in products:
        title = product.get("title")
        sku = product.get("sku")
        price = product.get("avg_price")
        brand = product.get("brand")

        print(f"👟 {title}")
        print(f"SKU: {sku}")
        print(f"Price: {price}")

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

        # =========================
        # PRODUCT ALREADY EXISTS
        # =========================

        if existing.data:
            product_id = existing.data[0]["id"]

            print(
                f"🔎 Found existing product with id {product_id}"
            )

        # =========================
        # NEW PRODUCT
        # =========================

        else:
            print("🆕 Product not found in database.")
            print("💾 Saving product...")

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

            # Get the ID of the product we just inserted
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

            print(
                f"✅ Product saved to Supabase with id {product_id}"
            )

        # =========================
        # SAVE PRICE HISTORY
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

            print("💰 Price saved to price_history!")

        else:
            print(
                "⚠️ Price is 0 or missing, so it was not saved."
            )

        print("---")


if __name__ == "__main__":
    main()
