import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request


WATCHLIST = [
    ("Jordan", "Air Jordan 1", "Jordan 1"),
    ("Jordan", "Air Jordan 3", "Jordan 3"),
    ("Jordan", "Air Jordan 4", "Jordan 4"),
    ("Jordan", "Air Jordan 5", "Jordan 5"),
    ("Jordan", "Air Jordan 11", "Jordan 11"),
    ("Jordan", "Air Jordan 12", "Jordan 12"),
    ("Nike", "Air Force 1", "Nike Air Force 1"),
    ("Nike", "Dunk", "Nike Dunk"),
    ("Nike", "SB Dunk", "Nike SB Dunk"),
    ("Nike", "Vomero 5", "Nike Vomero 5"),
    ("Nike", "P-6000", "Nike P-6000"),
    ("Nike", "Kobe", "Nike Kobe"),
    ("Nike", "Air Max", "Nike Air Max"),
    ("adidas", "Samba", "adidas Samba"),
    ("adidas", "Gazelle", "adidas Gazelle"),
    ("adidas", "Bad Bunny", "adidas Bad Bunny"),
    ("adidas", "Taekwondo", "adidas Taekwondo"),
    ("adidas", "Yeezy", "adidas Yeezy"),
    ("adidas", "Adizero", "adidas Adizero"),
    ("New Balance", "1906R", "New Balance 1906R"),
    ("New Balance", "2002R", "New Balance 2002R"),
    ("New Balance", "9060", "New Balance 9060"),
    ("New Balance", "530", "New Balance 530"),
    ("New Balance", "990", "New Balance 990"),
    ("New Balance", "993", "New Balance 993"),
    ("New Balance", "204L", "New Balance 204L"),
    ("ASICS", "Gel-1130", "ASICS Gel 1130"),
    ("ASICS", "Gel-Kayano 14", "ASICS Gel Kayano 14"),
    ("ASICS", "Gel-NYC", "ASICS Gel NYC"),
    ("ASICS", "GT-2160", "ASICS GT-2160"),
    ("ASICS", "Novablast", "ASICS Novablast"),
    ("Vans", "Old Skool", "Vans Old Skool"),
    ("Vans", "Knu Skool", "Vans Knu Skool"),
    ("Vans", "Slip-On", "Vans Slip On"),
    ("Vans", "Sk8-Hi", "Vans Sk8 Hi"),
    ("Saucony", "ProGrid Omni 9", "Saucony ProGrid Omni 9"),
    ("Saucony", "ProGrid Triumph 4", "Saucony ProGrid Triumph 4"),
    ("Saucony", "Guide 7", "Saucony Guide 7"),
    ("Saucony", "Ride Millennium", "Saucony Ride Millennium"),
    ("Salomon", "XT-6", "Salomon XT-6"),
    ("Salomon", "XT-4", "Salomon XT-4"),
    ("Salomon", "ACS Pro", "Salomon ACS Pro"),
    ("Salomon", "Speedcross", "Salomon Speedcross"),
    ("Mizuno", "MXR", "Mizuno MXR"),
    ("Mizuno", "Wave Prophecy Moc", "Mizuno Wave Prophecy Moc"),
    ("Mizuno", "Wave Rider", "Mizuno Wave Rider"),
    ("HOKA", "Clifton", "HOKA Clifton"),
    ("HOKA", "Bondi", "HOKA Bondi"),
    ("HOKA", "Speedgoat", "HOKA Speedgoat"),
    ("On", "Cloud", "On Cloud"),
    ("On", "Cloudmonster", "On Cloudmonster"),
    ("On", "Cloudtilt", "On Cloudtilt"),
]


def normalize(text):
    text = str(text or "").lower()
    text = text.replace("-", " ")
    text = text.replace("_", " ")
    text = re.sub(r"[^a-z0-9 ]+", " ", text)
    return " ".join(text.split())


def tokenize(text):
    return normalize(text).split()


def exact_brand_match(expected_brand, product_brand):
    expected = normalize(expected_brand)
    actual = normalize(product_brand)

    return expected == actual


def sequence_match(expected_model, text):
    expected_tokens = tokenize(expected_model)
    actual_tokens = tokenize(text)

    if not expected_tokens:
        return False

    if len(expected_tokens) > len(actual_tokens):
        return False

    for index in range(
        len(actual_tokens) - len(expected_tokens) + 1
    ):
        window = actual_tokens[
            index:index + len(expected_tokens)
        ]

        if window == expected_tokens:
            return True

    return False


def model_matches(model, product):
    fields = [
        product.get("model"),
        product.get("primary_title"),
        product.get("title"),
    ]

    for field in fields:
        if sequence_match(model, field):
            return True

    return False


def product_type_is_sneaker(product):
    product_type = normalize(
        product.get("product_type")
    )

    categories = product.get("categories") or []

    normalized_categories = {
        normalize(category)
        for category in categories
    }

    breadcrumbs = product.get("breadcrumbs") or []

    breadcrumb_values = set()

    for breadcrumb in breadcrumbs:
        if isinstance(breadcrumb, dict):
            breadcrumb_values.add(
                normalize(breadcrumb.get("value"))
            )

            breadcrumb_values.add(
                normalize(breadcrumb.get("alias"))
            )

    has_sneaker_category = (
        "sneakers" in normalized_categories
        or "sneakers" in breadcrumb_values
    )

    return (
        product_type == "sneakers"
        and has_sneaker_category
    )


def has_valid_price(product):
    price = product.get("avg_price")

    return (
        isinstance(price, (int, float))
        and price > 0
    )


def has_valid_sku(product):
    sku = str(
        product.get("sku") or ""
    ).strip()

    return bool(sku)


def validate_product(
    brand,
    model,
    search_query,
    product
):
    title = str(
        product.get("title") or ""
    )

    product_brand = str(
        product.get("brand") or ""
    )

    product_model = str(
        product.get("model") or ""
    )

    sku = str(
        product.get("sku") or ""
    )

    product_type = str(
        product.get("product_type") or ""
    )

    category = str(
        product.get("category") or ""
    )

    price = product.get("avg_price")

    reasons = []

    brand_match = exact_brand_match(
        brand,
        product_brand
    )

    sneaker_match = product_type_is_sneaker(
        product
    )

    model_match = model_matches(
        model,
        product
    )

    sku_match = has_valid_sku(
        product
    )

    price_match = has_valid_price(
        product
    )

    if not brand_match:
        reasons.append(
            "brand mismatch"
        )

    if not sneaker_match:
        reasons.append(
            "product is not confirmed as a sneaker"
        )

    if not model_match:
        reasons.append(
            "model mismatch"
        )

    if not sku_match:
        reasons.append(
            "missing SKU"
        )

    if not price_match:
        reasons.append(
            "invalid price"
        )

    if not brand_match:
        status = "REJECT"
        score = 0

    elif not sneaker_match:
        status = "REJECT"
        score = 0

    elif not model_match:
        status = "REJECT"
        score = 0

    else:
        score = 70

        if sku_match:
            score += 15

        if price_match:
            score += 15

        if score == 100:
            status = "VALID"
        else:
            status = "REVIEW"

    return {
        "status": status,
        "score": score,
        "query": search_query,
        "brand": brand,
        "model": model,
        "title": title,
        "product_brand": product_brand,
        "product_model": product_model,
        "product_type": product_type,
        "category": category,
        "sku": sku,
        "price": price,
        "reasons": reasons,
    }


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
            f"❌ HTTP {e.code} for "
            f"{search_query}"
        )

        return None

    except Exception as e:
        print(
            f"❌ Error for "
            f"{search_query}: {e}"
        )

        return None


def main():
    api_key = os.environ[
        "KICKSDB_API_KEY"
    ]

    print(
        "🔥 Starting watchlist validation"
    )

    print(
        f"📦 Queries: {len(WATCHLIST)}"
    )

    print()

    results = []

    for (
        brand,
        model,
        search_query
    ) in WATCHLIST:

        print(
            f"🔎 {search_query}"
        )

        product = search_product(
            api_key,
            search_query
        )

        if product is None:

            result = {
                "status": "EMPTY",
                "score": 0,
                "query": search_query,
                "brand": brand,
                "model": model,
                "reasons": [
                    "no product returned"
                ],
            }

        else:

            result = validate_product(
                brand,
                model,
                search_query,
                product
            )

        results.append(
            result
        )

        print(
            f"   {result['status']} "
            f"| score={result['score']} "
            f"| {result.get('title', '')}"
        )

        if result.get("reasons"):

            print(
                "   ⚠️ "
                + ", ".join(
                    result["reasons"]
                )
            )

        print()

    with open(
        "watchlist_validation_results.json",
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            results,
            file,
            indent=2,
            ensure_ascii=False
        )

    valid = sum(
        1
        for result in results
        if result["status"] == "VALID"
    )

    review = sum(
        1
        for result in results
        if result["status"] == "REVIEW"
    )

    reject = sum(
        1
        for result in results
        if result["status"] == "REJECT"
    )

    empty = sum(
        1
        for result in results
        if result["status"] == "EMPTY"
    )

    print(
        "==================================="
    )

    print(
        "📊 VALIDATION SUMMARY"
    )

    print(
        "==================================="
    )

    print(
        f"Total:   {len(results)}"
    )

    print(
        f"VALID:   {valid}"
    )

    print(
        f"REVIEW:  {review}"
    )

    print(
        f"REJECT:  {reject}"
    )

    print(
        f"EMPTY:   {empty}"
    )

    print(
        "==================================="
    )

    print(
        "📄 Saved to "
        "watchlist_validation_results.json"
    )


if __name__ == "__main__":
    main()
