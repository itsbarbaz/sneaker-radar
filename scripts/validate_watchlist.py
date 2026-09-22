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
    """
    Normalizza il testo per rendere il confronto più semplice.
    """
    text = str(text or "").lower()

    text = text.replace("-", " ")
    text = text.replace("_", " ")
    text = re.sub(r"[^a-z0-9 ]+", " ", text)

    return " ".join(text.split())


def validate_product(brand, model, search_query, product):
    """
    Controlla se il prodotto restituito da KicksDB
    sembra coerente con la nostra ricerca.
    """

    title = product.get("title", "")
    product_brand = product.get("brand", "")
    sku = product.get("sku", "")
    price = product.get("avg_price")

    normalized_title = normalize(title)
    normalized_brand = normalize(product_brand)
    normalized_expected_brand = normalize(brand)
    normalized_model = normalize(model)

    reasons = []
    score = 0

    # =========================
    # BRAND
    # =========================

    if normalized_expected_brand in normalized_brand:
        score += 30
    elif normalized_expected_brand in normalized_title:
        score += 20
    else:
        reasons.append("brand mismatch")

    # =========================
    # MODEL
    # =========================

    model_words = normalized_model.split()

    matched_words = 0

    for word in model_words:
        if word in normalized_title:
            matched_words += 1

    if model_words and matched_words == len(model_words):
        score += 40

    elif matched_words > 0:
        score += 20

    else:
        reasons.append("model mismatch")

    # =========================
    # SKU
    # =========================

    if sku:
        score += 15
    else:
        reasons.append("missing SKU")

    # =========================
    # PRICE
    # =========================

    if isinstance(price, (int, float)) and price > 0:
        score += 15
    else:
        reasons.append("invalid price")

    # =========================
    # FINAL DECISION
    # =========================

    if score >= 85:
        status = "VALID"

    elif score >= 60:
        status = "REVIEW"

    else:
        status = "REJECT"

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

    url = "https://api.kicks.dev/v3/stockx/products?" + params

    request = urllib.request.Request(
        url,
        headers={
            "Authorization": api_key
        }
    )

    try:
        with urllib.request.urlopen(request) as response:
            data = json.loads(response.read().decode())

        products = data.get("data", [])

        if not products:
            return None

        return products[0]

    except urllib.error.HTTPError as e:
        print(f"❌ HTTP {e.code} for {search_query}")
        return None

    except Exception as e:
        print(f"❌ Error for {search_query}: {e}")
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
                f"   ⚠️ {', '.join(result['reasons'])}"
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
        1 for result in results
        if result["status"] == "VALID"
    )

    review = sum(
        1 for result in results
        if result["status"] == "REVIEW"
    )

    reject = sum(
        1 for result in results
        if result["status"] == "REJECT"
    )

    empty = sum(
        1 for result in results
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
    print("📄 Saved to watchlist_validation_results.json")


if __name__ == "__main__":
    main()
