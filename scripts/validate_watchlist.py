import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request


WATCHLIST = [
    # =========================
    # JORDAN
    # =========================
    ("Jordan", "Air Jordan 1", "Jordan 1"),
    ("Jordan", "Air Jordan 3", "Jordan 3"),
    ("Jordan", "Air Jordan 4", "Jordan 4"),
    ("Jordan", "Air Jordan 5", "Jordan 5"),
    ("Jordan", "Air Jordan 11", "Jordan 11"),
    ("Jordan", "Air Jordan 12", "Jordan 12"),

    # =========================
    # NIKE
    # =========================
    ("Nike", "Air Force 1", "Nike Air Force 1"),
    ("Nike", "Dunk", "Nike Dunk"),
    ("Nike", "SB Dunk", "Nike SB Dunk"),
    ("Nike", "Vomero 5", "Nike Vomero 5"),
    ("Nike", "P-6000", "Nike P-6000"),
    ("Nike", "Kobe", "Nike Kobe"),
    ("Nike", "Air Max", "Nike Air Max"),

    # =========================
    # ADIDAS
    # =========================
    ("adidas", "Samba", "adidas Samba"),
    ("adidas", "Gazelle", "adidas Gazelle"),
    ("adidas", "Bad Bunny", "adidas Bad Bunny"),
    ("adidas", "Taekwondo", "adidas Taekwondo"),
    ("adidas", "Yeezy", "adidas Yeezy"),
    ("adidas", "Adizero", "adidas Adizero"),

    # =========================
    # NEW BALANCE
    # =========================
    ("New Balance", "1906R", "New Balance 1906R"),
    ("New Balance", "2002R", "New Balance 2002R"),
    ("New Balance", "9060", "New Balance 9060"),
    ("New Balance", "530", "New Balance 530"),
    ("New Balance", "990", "New Balance 990"),
    ("New Balance", "993", "New Balance 993"),
    ("New Balance", "204L", "New Balance 204L"),

    # =========================
    # ASICS
    # =========================
    ("ASICS", "Gel-1130", "ASICS Gel 1130"),
    ("ASICS", "Gel-Kayano 14", "ASICS Gel Kayano 14"),
    ("ASICS", "Gel-NYC", "ASICS Gel NYC"),
    ("ASICS", "GT-2160", "ASICS GT-2160"),
    ("ASICS", "Novablast", "ASICS Novablast"),

    # =========================
    # VANS
    # =========================
    ("Vans", "Old Skool", "Vans Old Skool"),
    ("Vans", "Knu Skool", "Vans Knu Skool"),
    ("Vans", "Slip-On", "Vans Slip On"),
    ("Vans", "Sk8-Hi", "Vans Sk8 Hi"),

    # =========================
    # SAUCONY
    # =========================
    ("Saucony", "ProGrid Omni 9", "Saucony ProGrid Omni 9"),
    ("Saucony", "ProGrid Triumph 4", "Saucony ProGrid Triumph 4"),
    ("Saucony", "Guide 7", "Saucony Guide 7"),
    ("Saucony", "Ride Millennium", "Saucony Ride Millennium"),

    # =========================
    # SALOMON
    # =========================
    ("Salomon", "XT-6", "Salomon XT-6"),
    ("Salomon", "XT-4", "Salomon XT-4"),
    ("Salomon", "ACS Pro", "Salomon ACS Pro"),
    ("Salomon", "Speedcross", "Salomon Speedcross"),

    # =========================
    # MIZUNO
    # =========================
    ("Mizuno", "MXR", "Mizuno MXR"),
    ("Mizuno", "Wave Prophecy Moc", "Mizuno Wave Prophecy Moc"),
    ("Mizuno", "Wave Rider", "Mizuno Wave Rider"),

    # =========================
    # HOKA
    # =========================
    ("HOKA", "Clifton", "HOKA Clifton"),
    ("HOKA", "Bondi", "HOKA Bondi"),
    ("HOKA", "Speedgoat", "HOKA Speedgoat"),

    # =========================
    # ON
    # =========================
    ("On", "Cloud", "On Cloud"),
    ("On", "Cloudmonster", "On Cloudmonster"),
    ("On", "Cloudtilt", "On Cloudtilt"),
]


def normalize(text):
    """
    Normalizza il testo per rendere il confronto più semplice.
    """

    text = str(text or "").lower()

    text = text.replace("-", " ")
    text = text.replace("_", " ")

    text = re.sub(
        r"[^a-z0-9 ]+",
        " ",
        text
    )

    return " ".join(text.split())


def validate_product(brand, model, search_query, product):
    """
    Valuta quanto il prodotto restituito da KicksDB
    corrisponde alla ricerca.

    Il sistema è volutamente conservativo:
    se ci sono dubbi, il prodotto viene mandato in REVIEW
    invece di essere considerato automaticamente valido.
    """

    title = str(product.get("title") or "")
    product_brand = str(product.get("brand") or "")
    sku = str(product.get("sku") or "")
    price = product.get("avg_price")

    normalized_title = normalize(title)
    normalized_brand = normalize(product_brand)
    normalized_expected_brand = normalize(brand)
    normalized_model = normalize(model)

    reasons = []

    # =========================
    # PRODOTTI NON DESIDERATI
    # =========================

    excluded_terms = [
        "sock",
        "socks",
        "shirt",
        "t shirt",
        "tee",
        "jacket",
        "pants",
        "shorts",
        "hat",
        "cap",
        "bag",
        "backpack",
        "wallet",
        "accessory",
        "accessories",
        "slides",
        "sandal",
    ]

    for term in excluded_terms:
        if term in normalized_title:
            reasons.append(
                f"excluded product type: {term}"
            )

    # =========================
    # BRAND
    # =========================

    brand_match = (
        normalized_expected_brand == normalized_brand
        or normalized_expected_brand in normalized_brand
        or normalized_expected_brand in normalized_title
    )

    if not brand_match:
        reasons.append("brand mismatch")

    # =========================
    # MODEL
    # =========================

    model_words = normalized_model.split()

    matched_words = 0

    for word in model_words:
        if word in normalized_title:
            matched_words += 1

    if not model_words:
        reasons.append("missing model")

    elif matched_words == len(model_words):
        pass

    elif matched_words > 0:
        reasons.append("partial model match")

    else:
        reasons.append("model mismatch")

    # =========================
    # SKU
    # =========================

    if not sku:
        reasons.append("missing SKU")

    # =========================
    # PRICE
    # =========================

    valid_price = (
        isinstance(price, (int, float))
        and price > 0
    )

    if not valid_price:
        reasons.append("invalid price")

    # =========================
    # HARD REJECT
    # =========================

    has_excluded_product_type = any(
        reason.startswith("excluded product type")
        for reason in reasons
    )

    has_model_mismatch = (
        "model mismatch" in reasons
    )

    if has_excluded_product_type:
        status = "REJECT"
        score = 0

    elif not brand_match:
        status = "REJECT"
        score = 0

    elif has_model_mismatch:
        status = "REJECT"
        score = 0

    # =========================
    # SCORE
    # =========================

    else:
        score = 0

        if brand_match:
            score += 35

        if matched_words == len(model_words):
            score += 35

        if sku:
            score += 15

        if valid_price:
            score += 15

        if score >= 90:
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
        with urllib.request.urlopen(request) as response:
            data = json.loads(
                response.read().decode()
            )

        products = data.get("data", [])

        if not products:
            return None

        return products[0]

    except urllib.error.HTTPError as e:
        print(
            f"❌ HTTP {e.code} for {search_query}"
        )
        return None

    except Exception as e:
        print(
            f"❌ Error for {search_query}: {e}"
        )
        return None


def main():
    api_key = os.environ["KICKSDB_API_KEY"]

    print("🔥 Starting watchlist validation")
    print(f"📦 Queries: {len(WATCHLIST)}")
    print()

    results = []

    for brand, model, search_query in WATCHLIST:

        print(f"🔎 {search_query}")

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
            }

        else:

            result = validate_product(
                brand,
                model,
                search_query,
                product
            )

        results.append(result)

        print(
            f"   {result['status']} "
            f"| score={result['score']} "
            f"| {result.get('title', '')}"
        )

        if result.get("reasons"):
            print(
                "   ⚠️ "
                + ", ".join(result["reasons"])
            )

        print()

    # =========================
    # SAVE RESULTS
    # =========================

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

    # =========================
    # SUMMARY
    # =========================

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

    print("===================================")
    print("📊 VALIDATION SUMMARY")
    print("===================================")
    print(f"Total:   {len(results)}")
    print(f"VALID:   {valid}")
    print(f"REVIEW:  {review}")
    print(f"REJECT:  {reject}")
    print(f"EMPTY:   {empty}")
    print("===================================")
    print(
        "📄 Saved to "
        "watchlist_validation_results.json"
    )


if __name__ == "__main__":
    main()
