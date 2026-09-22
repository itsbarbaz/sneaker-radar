import json
import os
import urllib.error
import urllib.parse
import urllib.request


WATCHLIST = [
    # =========================
    # JORDAN
    # =========================
    ("Jordan", "Air Jordan 1", "Jordan 1", "core", 100),
    ("Jordan", "Air Jordan 3", "Jordan 3", "core", 100),
    ("Jordan", "Air Jordan 4", "Jordan 4", "core", 100),
    ("Jordan", "Air Jordan 5", "Jordan 5", "core", 100),
    ("Jordan", "Air Jordan 11", "Jordan 11", "core", 100),
    ("Jordan", "Air Jordan 12", "Jordan 12", "core", 95),

    # =========================
    # NIKE
    # =========================
    ("Nike", "Air Force 1", "Nike Air Force 1", "core", 100),
    ("Nike", "Dunk", "Nike Dunk", "core", 100),
    ("Nike", "SB Dunk", "Nike SB Dunk", "core", 95),
    ("Nike", "Vomero 5", "Nike Vomero 5", "core", 90),
    ("Nike", "P-6000", "Nike P-6000", "core", 90),
    ("Nike", "Kobe", "Nike Kobe", "core", 90),
    ("Nike", "Air Max", "Nike Air Max", "core", 85),

    # =========================
    # ADIDAS
    # =========================
    ("adidas", "Samba", "adidas Samba", "core", 100),
    ("adidas", "Gazelle", "adidas Gazelle", "core", 90),
    ("adidas", "Bad Bunny", "adidas Bad Bunny", "core", 90),
    ("adidas", "Taekwondo", "adidas Taekwondo", "emerging", 75),
    ("adidas", "Yeezy", "adidas Yeezy", "core", 80),
    ("adidas", "Adizero", "adidas Adizero", "emerging", 70),

    # =========================
    # NEW BALANCE
    # =========================
    ("New Balance", "1906R", "New Balance 1906R", "core", 95),
    ("New Balance", "2002R", "New Balance 2002R", "core", 95),
    ("New Balance", "9060", "New Balance 9060", "core", 95),
    ("New Balance", "530", "New Balance 530", "core", 85),
    ("New Balance", "990", "New Balance 990", "core", 90),
    ("New Balance", "993", "New Balance 993", "core", 85),
    ("New Balance", "204L", "New Balance 204L", "emerging", 75),

    # =========================
    # ASICS
    # =========================
    ("ASICS", "Gel-1130", "ASICS Gel 1130", "core", 95),
    ("ASICS", "Gel-Kayano 14", "ASICS Gel Kayano 14", "core", 95),
    ("ASICS", "Gel-NYC", "ASICS Gel NYC", "core", 90),
    ("ASICS", "GT-2160", "ASICS GT-2160", "core", 85),
    ("ASICS", "Novablast", "ASICS Novablast", "emerging", 70),

    # =========================
    # VANS
    # =========================
    ("Vans", "Old Skool", "Vans Old Skool", "core", 90),
    ("Vans", "Knu Skool", "Vans Knu Skool", "core", 85),
    ("Vans", "Slip-On", "Vans Slip On", "core", 80),
    ("Vans", "Sk8-Hi", "Vans Sk8 Hi", "emerging", 70),

    # =========================
    # SAUCONY
    # =========================
    ("Saucony", "ProGrid Omni 9", "Saucony ProGrid Omni 9", "emerging", 85),
    ("Saucony", "ProGrid Triumph 4", "Saucony ProGrid Triumph 4", "emerging", 80),
    ("Saucony", "Guide 7", "Saucony Guide 7", "emerging", 65),
    ("Saucony", "Ride Millennium", "Saucony Ride Millennium", "discovery", 55),

    # =========================
    # SALOMON
    # =========================
    ("Salomon", "XT-6", "Salomon XT-6", "core", 90),
    ("Salomon", "XT-4", "Salomon XT-4", "emerging", 75),
    ("Salomon", "ACS Pro", "Salomon ACS Pro", "emerging", 70),
    ("Salomon", "Speedcross", "Salomon Speedcross", "discovery", 55),

    # =========================
    # MIZUNO
    # =========================
    ("Mizuno", "MXR", "Mizuno MXR", "emerging", 80),
    ("Mizuno", "Wave Prophecy Moc", "Mizuno Wave Prophecy Moc", "emerging", 75),
    ("Mizuno", "Wave Rider", "Mizuno Wave Rider", "discovery", 55),

    # =========================
    # HOKA
    # =========================
    ("HOKA", "Clifton", "HOKA Clifton", "core", 80),
    ("HOKA", "Bondi", "HOKA Bondi", "core", 80),
    ("HOKA", "Speedgoat", "HOKA Speedgoat", "emerging", 65),

    # =========================
    # ON
    # =========================
    ("On", "Cloud", "On Cloud", "core", 75),
    ("On", "Cloudmonster", "On Cloudmonster", "core", 75),
    ("On", "Cloudtilt", "On Cloudtilt", "emerging", 65),
]


def test_query(api_key, search_query):
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

        if products:
            product = products[0]

            return {
                "status": "OK",
                "query": search_query,
                "title": product.get("title"),
                "sku": product.get("sku"),
                "price": product.get("avg_price"),
            }

        return {
            "status": "EMPTY",
            "query": search_query,
        }

    except urllib.error.HTTPError as e:
        return {
            "status": f"HTTP_{e.code}",
            "query": search_query,
            "error": e.read().decode(),
        }

    except Exception as e:
        return {
            "status": f"ERROR_{type(e).__name__}",
            "query": search_query,
            "error": str(e),
        }


def main():
    api_key = os.environ["KICKSDB_API_KEY"]

    print("🔥 Starting Sneaker Radar watchlist test")
    print(f"📦 Queries to test: {len(WATCHLIST)}")
    print()

    results = []

    for brand, model, search_query, tier, priority in WATCHLIST:
        print(f"🔎 Testing: {search_query}")

        result = test_query(
            api_key,
            search_query
        )

        result.update({
            "brand": brand,
            "model": model,
            "tier": tier,
            "priority": priority,
        })

        results.append(result)

        if result["status"] == "OK":
            print(
                f"   ✅ OK — {result.get('title')} "
                f"| SKU: {result.get('sku')} "
                f"| Price: {result.get('price')}"
            )

        elif result["status"] == "EMPTY":
            print("   ⚠️ EMPTY — no product returned")

        else:
            print(
                f"   ❌ {result['status']} — "
                f"{result.get('error', '')}"
            )

        print()

    with open(
        "watchlist_test_results.json",
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            results,
            file,
            indent=2,
            ensure_ascii=False
        )

    ok_count = sum(
        1 for result in results
        if result["status"] == "OK"
    )

    empty_count = sum(
        1 for result in results
        if result["status"] == "EMPTY"
    )

    error_count = len(results) - ok_count - empty_count

    print("===================================")
    print("📊 WATCHLIST TEST SUMMARY")
    print("===================================")
    print(f"Total:  {len(results)}")
    print(f"OK:     {ok_count}")
    print(f"EMPTY:  {empty_count}")
    print(f"ERROR:  {error_count}")
    print("===================================")
    print("📄 Results saved to watchlist_test_results.json")


if __name__ == "__main__":
    main()
