import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request


WATCHLIST = [
    ("Jordan", "Air Jordan 1", "Jordan 1", "Jordan 1"),
    ("Jordan", "Air Jordan 3", "Jordan 3", "Jordan 3"),
    ("Jordan", "Air Jordan 4", "Jordan 4", "Jordan 4"),
    ("Jordan", "Air Jordan 5", "Jordan 5", "Jordan 5"),
    ("Jordan", "Air Jordan 11", "Jordan 11", "Jordan 11"),
    ("Jordan", "Air Jordan 12", "Jordan 12", "Jordan 12"),
    ("Nike", "Air Force 1", "Air Force 1", "Nike Air Force 1"),
    ("Nike", "Dunk", "Dunk", "Nike Dunk"),
    ("Nike", "SB Dunk", "SB Dunk", "Nike SB Dunk"),
    ("Nike", "Vomero 5", "Vomero 5", "Nike Vomero 5"),
    ("Nike", "P-6000", "P-6000", "Nike P-6000"),
    ("Nike", "Kobe", "Kobe", "Nike Kobe"),
    ("Nike", "Air Max", "Air Max", "Nike Air Max"),
    ("adidas", "Samba", "Samba", "adidas Samba"),
    ("adidas", "Gazelle", "Gazelle", "adidas Gazelle"),
    ("adidas", "Bad Bunny", "Bad Bunny", "adidas Bad Bunny"),
    ("adidas", "Taekwondo", "Taekwondo", "adidas Taekwondo"),
    ("adidas", "Yeezy", "Yeezy", "adidas Yeezy"),
    ("adidas", "Adizero", "Adizero", "adidas Adizero"),
    ("New Balance", "1906R", "1906R", "New Balance 1906R"),
    ("New Balance", "2002R", "2002R", "New Balance 2002R"),
    ("New Balance", "9060", "9060", "New Balance 9060"),
    ("New Balance", "530", "530", "New Balance 530"),
    ("New Balance", "990", "990", "New Balance 990"),
    ("New Balance", "993", "993", "New Balance 993"),
    ("New Balance", "204L", "204L", "New Balance 204L"),
    ("ASICS", "Gel-1130", "Gel 1130", "ASICS Gel 1130"),
    ("ASICS", "Gel-Kayano 14", "Gel Kayano 14", "ASICS Gel Kayano 14"),
    ("ASICS", "Gel-NYC", "Gel NYC", "ASICS Gel NYC"),
    ("ASICS", "GT-2160", "GT 2160", "ASICS GT-2160"),
    ("ASICS", "Novablast", "Novablast", "ASICS Novablast"),
    ("Vans", "Old Skool", "Old Skool", "Vans Old Skool"),
    ("Vans", "Knu Skool", "Knu Skool", "Vans Knu Skool"),
    ("Vans", "Slip-On", "Slip On", "Vans Slip On"),
    ("Vans", "Sk8-Hi", "Sk8 Hi", "Vans Sk8 Hi"),
    ("Saucony", "ProGrid Omni 9", "ProGrid Omni 9", "Saucony ProGrid Omni 9"),
    ("Saucony", "ProGrid Triumph 4", "ProGrid Triumph 4", "Saucony ProGrid Triumph 4"),
    ("Saucony", "Guide 7", "Guide 7", "Saucony Guide 7"),
    ("Saucony", "Ride Millennium", "Ride Millennium", "Saucony Ride Millennium"),
    ("Salomon", "XT-6", "XT 6", "Salomon XT-6"),
    ("Salomon", "XT-4", "XT 4", "Salomon XT-4"),
    ("Salomon", "ACS Pro", "ACS Pro", "Salomon ACS Pro"),
    ("Salomon", "Speedcross", "Speedcross", "Salomon Speedcross"),
    ("Mizuno", "MXR", "MXR", "Mizuno MXR"),
    ("Mizuno", "Wave Prophecy Moc", "Wave Prophecy Moc", "Mizuno Wave Prophecy Moc"),
    ("Mizuno", "Wave Rider", "Wave Rider", "Mizuno Wave Rider"),
    ("HOKA", "Clifton", "Clifton", "HOKA Clifton"),
    ("HOKA", "Bondi", "Bondi", "HOKA Bondi"),
    ("HOKA", "Speedgoat", "Speedgoat", "HOKA Speedgoat"),
    ("On", "Cloud", "Cloud", "On Cloud"),
    ("On", "Cloudmonster", "Cloudmonster", "On Cloudmonster"),
    ("On", "Cloudtilt", "Cloudtilt", "On Cloudtilt"),
]


CANDIDATE_LIMIT = 10


def normalize(text):
    text = str(text or "").lower()
    text = text.replace("-", " ")
    text = text.replace("_", " ")
    text = re.sub(r"[^a-z0-9 ]+", " ", text)
    return " ".join(text.split())


def tokenize(text):
    return normalize(text).split()


def exact_brand_match(expected_brand, product_brand):
    return normalize(expected_brand) == normalize(product_brand)


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
    expected_tokens = tokenize(model)

    product_model = product.get("model")
    product_model_tokens = tokenize(product_model)

    if product_model:
        # Il campo "model" strutturato di KicksDB
        # è la fonte principale per identificare il modello.
        #
        # Questo impedisce casi come:
        #
        # Jordan 5
        #      vs
        # Jordan Luka 5
        #
        # dove il titolo contiene "Jordan 5" ma
        # il vero modello è "Jordan Luka 5".

        expected_has_number = any(
            token.isdigit()
            for token in expected_tokens
        )

        product_model_has_number = any(
            token.isdigit()
            for token in product_model_tokens
        )

        # Match diretto sul campo model.
        if sequence_match(
            model,
            product_model
        ):
            return True

        # Se entrambi hanno numeri di modello ma
        # non c'è un match diretto, NON permettiamo
        # al titolo di creare un falso positivo.
        if (
            expected_has_number
            and product_model_has_number
        ):
            return False

        # Per query di collaborazione/collezione
        # come "Bad Bunny", il termine potrebbe
        # non essere presente nel campo model.
        #
        # In quel caso titolo e primary_title
        # possono essere usati come fallback.
        for field in [
            product.get("primary_title"),
            product.get("title"),
        ]:
            if sequence_match(
                model,
                field
            ):
                return True

        return False

    # Se KicksDB non fornisce il campo model,
    # utilizziamo titolo e primary_title come fallback.
    for field in [
        product.get("primary_title"),
        product.get("title"),
    ]:
        if sequence_match(
            model,
            field
        ):
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
                normalize(
                    breadcrumb.get("value")
                )
            )

            breadcrumb_values.add(
                normalize(
                    breadcrumb.get("alias")
                )
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


def evaluate_candidate(
    brand,
    validation_model,
    product
):
    brand_match = exact_brand_match(
        brand,
        product.get("brand")
    )

    sneaker_match = product_type_is_sneaker(
        product
    )

    model_match = model_matches(
        validation_model,
        product
    )

    sku_match = has_valid_sku(
        product
    )

    price_match = has_valid_price(
        product
    )

    identity_match = (
        brand_match
        and sneaker_match
        and model_match
    )

    data_quality_score = 0

    if sku_match:
        data_quality_score += 15

    if price_match:
        data_quality_score += 15

    if identity_match:
        identity_score = 70
    else:
        identity_score = 0

    total_score = (
        identity_score
        + data_quality_score
    )

    if not identity_match:
        status = "REJECT"

    elif sku_match and price_match:
        status = "VALID"

    else:
        status = "REVIEW"

    reasons = []

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

    return {
        "status": status,
        "identity_match": identity_match,
        "identity_score": identity_score,
        "data_quality_score": data_quality_score,
        "score": total_score,
        "checks": {
            "brand_match": brand_match,
            "sneaker_match": sneaker_match,
            "model_match": model_match,
            "sku_match": sku_match,
            "price_match": price_match,
        },
        "title": product.get("title"),
        "brand": product.get("brand"),
        "model": product.get("model"),
        "product_type": product.get("product_type"),
        "category": product.get("category"),
        "sku": product.get("sku"),
        "price": product.get("avg_price"),
        "reasons": reasons,
    }


def search_products(api_key, search_query):
    params = urllib.parse.urlencode({
        "query": search_query,
        "limit": CANDIDATE_LIMIT,
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

        return data.get(
            "data",
            []
        )

    except urllib.error.HTTPError as e:
        print(
            f"❌ HTTP {e.code} for "
            f"{search_query}"
        )

        return []

    except Exception as e:
        print(
            f"❌ Error for "
            f"{search_query}: {e}"
        )

        return []


def build_result(
    brand,
    display_model,
    validation_model,
    search_query,
    products
):
    evaluated = []

    for product in products:
        evaluation = evaluate_candidate(
            brand,
            validation_model,
            product
        )

        evaluated.append(
            evaluation
        )

    identity_matches = [
        item
        for item in evaluated
        if item["identity_match"]
    ]

    valid_matches = [
        item
        for item in identity_matches
        if item["status"] == "VALID"
    ]

    review_matches = [
        item
        for item in identity_matches
        if item["status"] == "REVIEW"
    ]

    if valid_matches:
        status = "VALID"

    elif review_matches:
        status = "REVIEW"

    elif identity_matches:
        status = "REVIEW"

    elif products:
        status = "REJECT"

    else:
        status = "EMPTY"

    identity_matches.sort(
        key=lambda item: (
            item["data_quality_score"],
            normalize(item["title"]),
        ),
        reverse=True
    )

    evaluated.sort(
        key=lambda item: (
            item["identity_match"],
            item["data_quality_score"],
            normalize(item["title"]),
        ),
        reverse=True
    )

    reasons = []

    if not products:
        reasons.append(
            "no products returned"
        )

    elif not identity_matches:
        reasons.append(
            "no candidate passed identity filters"
        )

    elif not valid_matches:
        reasons.append(
            "identity match found, but no candidate has complete data"
        )

    return {
        "status": status,
        "query": search_query,
        "brand": brand,
        "display_model": display_model,
        "validation_model": validation_model,

        "products_returned": len(products),

        "identity_matches": len(
            identity_matches
        ),

        "valid_matches": len(
            valid_matches
        ),

        "review_matches": len(
            review_matches
        ),

        "reasons": reasons,

        "matched_candidates": identity_matches,

        "all_candidates": evaluated,
    }


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

    print(
        f"🔎 Candidates per query: "
        f"{CANDIDATE_LIMIT}"
    )

    print()

    results = []

    for (
        brand,
        display_model,
        validation_model,
        search_query
    ) in WATCHLIST:

        print(
            f"🔎 {search_query}"
        )

        products = search_products(
            api_key,
            search_query
        )

        result = build_result(
            brand,
            display_model,
            validation_model,
            search_query,
            products
        )

        results.append(
            result
        )

        print(
            f"   {result['status']}"
        )

        print(
            f"   📦 Products returned: "
            f"{result['products_returned']}"
        )

        print(
            f"   🎯 Identity matches: "
            f"{result['identity_matches']}"
        )

        print(
            f"   ✅ Complete matches: "
            f"{result['valid_matches']}"
        )

        print(
            f"   ⚠️ Review matches: "
            f"{result['review_matches']}"
        )

        if result["matched_candidates"]:
            print(
                "   👟 Matching products:"
            )

            for candidate in result[
                "matched_candidates"
            ]:

                print(
                    "      - "
                    + str(
                        candidate["title"]
                    )
                    + " | "
                    + candidate["status"]
                    + " | data="
                    + str(
                        candidate[
                            "data_quality_score"
                        ]
                    )
                )

        if result["reasons"]:
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

    total_identity_matches = sum(
        result["identity_matches"]
        for result in results
    )

    total_valid_matches = sum(
        result["valid_matches"]
        for result in results
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
        f"Total queries:        {len(results)}"
    )

    print(
        f"VALID queries:        {valid}"
    )

    print(
        f"REVIEW queries:       {review}"
    )

    print(
        f"REJECT queries:       {reject}"
    )

    print(
        f"EMPTY queries:        {empty}"
    )

    print(
        f"Identity matches:     {total_identity_matches}"
    )

    print(
        f"Complete matches:     {total_valid_matches}"
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
