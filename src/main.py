import os
import json
import urllib.request

def main():
    api_key = os.environ["KICKSDB_API_KEY"]

    url = "https://api.kicks.dev/v3/stockx/products?limit=3&category=sneakers"

    request = urllib.request.Request(
        url,
        headers={"Authorization": f"Bearer {api_key}"}
    )

    with urllib.request.urlopen(request) as response:
        data = json.loads(response.read().decode())

    print("🔥 KicksDB connected!")

    for product in data["data"]:
        print(f"👟 {product.get('title')}")
        print(f"SKU: {product.get('sku')}")
        print(f"Price: {product.get('avg_price')}")
        print("---")


if __name__ == "__main__":
    main()
