import os
import json
import urllib.request
import urllib.error

from supabase import create_client


def main():
    supabase_url = os.environ["SUPABASE_URL"]
    supabase_key = os.environ["SUPABASE_SECRET_KEY"]

    supabase = create_client(supabase_url, supabase_key)

    print("🔥 Supabase connected!")

    api_key = os.environ["KICKSDB_API_KEY"]

    url = "https://api.kicks.dev/v3/stockx/products?limit=1"

    request = urllib.request.Request(
        url,
        headers={"Authorization": f"Bearer {api_key}"}
    )

    try:
        with urllib.request.urlopen(request) as response:
            data = json.loads(response.read().decode())

    except urllib.error.HTTPError as e:
        print("KicksDB error:", e.code)
        print("Headers:", dict(e.headers))
        print("Body:", e.read().decode())
        raise

    print("🔥 KicksDB connected!")

    for product in data["data"]:
        title = product.get("title")
        sku = product.get("sku")
        price = product.get("avg_price")

        print(f"👟 {title}")
        print(f"SKU: {sku}")
        print(f"Price: {price}")

        existing = (
            supabase.table("products")
            .select("id")
            .eq("sku", sku)
            .execute()
        )
if not existing.data:
    result = (
        supabase.table("products")
        .insert({
            "title": title,
            "brand": product.get("brand"),
            "sku": sku,
            "source": "kicksdb"
        })
        .execute()
    )

    print("✅ Product saved to Supabase!")
        print(f"Found {len(existing.data)} products with this SKU")

        print("---")


if __name__ == "__main__":
    main()
