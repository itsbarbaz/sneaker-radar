import json
import os
import urllib.error
import urllib.parse
import urllib.request


SEARCH_QUERY = "Jordan 1"


def search_product(api_key, search_query):
    params = urllib.parse.urlencode({
        "query": search_query,
        "limit": 1,
    })

    url = (
        "https://api.kicks.dev/v3/stockx/products?"
        + params
    )

    request = urllib.request.Request(
        url,
        headers={
            "Authorization": api_key
        }
    )

    try:
        with urllib.request.urlopen(
            request
        ) as response:

            data = json.loads(
                response.read().decode()
            )

        products = data.get(
            "data",
            []
        )

        if not products:
            return None

        return products[0]

    except urllib.error.HTTPError as e:
        print(
            f"❌ HTTP {e.code}"
        )

        try:
            print(
                e.read().decode()
            )
        except Exception:
            pass

        return None

    except Exception as e:
        print(
            f"❌ Error: {e}"
        )

        return None


def main():
    api_key = os.environ[
        "KICKSDB_API_KEY"
    ]

    print(
        "==================================="
    )
    print(
        "🔎 JORDAN 1 DIAGNOSTIC TEST"
    )
    print(
        "==================================="
    )
    print()

    print(
        f"Query: {SEARCH_QUERY}"
    )
    print()

    product = search_product(
        api_key,
        SEARCH_QUERY
    )

    if product is None:
        print(
            "❌ No product returned."
        )
        return

    print(
        "✅ Product returned!"
    )
    print()

    print(
        "==================================="
    )
    print(
        "📦 COMPLETE PRODUCT"
    )
    print(
        "==================================="
    )
    print()

    print(
        json.dumps(
            product,
            indent=2,
            ensure_ascii=False
        )
    )

    print()

    print(
        "==================================="
    )
    print(
        "🔑 IMPORTANT FIELDS"
    )
    print(
        "==================================="
    )
    print()

    important_fields = [
        "id",
        "title",
        "brand",
        "model",
        "gender",
        "sku",
        "product_type",
        "category",
        "secondary_category",
        "categories",
        "breadcrumbs",
        "primary_title",
        "secondary_title",
        "description",
        "slug",
        "avg_price",
        "min_price",
        "max_price",
        "weekly_orders",
        "rank",
    ]

    for field in important_fields:

        print(
            f"{field}:"
        )

        print(
            product.get(field)
        )

        print()

    print(
        "==================================="
    )
    print(
        "🏁 TEST COMPLETE"
    )
    print(
        "==================================="
    )


if __name__ == "__main__":
    main()
