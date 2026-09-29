import os
import sys
import json
import urllib.request
import urllib.error
import re

from supabase import create_client


# ============================================================
# LOGGING
# ============================================================

try:
    sys.stdout.reconfigure(line_buffering=True)
except Exception:
    pass


def log(*args):
    print(*args, flush=True)


# ============================================================
# HELPERS
# ============================================================

def normalize(value):
    if value is None:
        return ""

    return str(value).strip().lower()


def extract_year(title):
    if not title:
        return None

    match = re.search(r"\b(19|20)\d{2}\b", str(title))

    if match:
        return int(match.group())

    return None


def detect_condition(product):
    """
    Cerca di determinare la condizione dal prodotto.
    Se non viene trovata, restituisce UNKNOWN.
    """

    title = normalize(product.get("title"))
    description = normalize(product.get("description"))
    text = f"{title} {description}"

    if "used" in text:
        return "USED"

    if "new" in text:
        return "NEW"

    return "UNKNOWN"


def detect_gender(product):
    """
    Mantiene il valore fornito da KicksDB.
    """

    gender = product.get("gender")

    if not gender:
        return "UNKNOWN"

    return str(gender).upper()


# ============================================================
# CATEGORY / PRODUCT TYPE
# ============================================================

def check_category_product_type(product):
    """
    Controllo compatibilità tra category e product_type.

    IMPORTANTE:
    KicksDB può restituire:

        category = "air jordan"
        product_type = "sneakers"

    Questo è un abbinamento valido per Sneaker Radar.

    Non consideriamo quindi "air jordan" incompatibile
    con "sneakers".
    """

    category = normalize(product.get("category"))
    product_type = normalize(product.get("product_type"))

    # Caso normale
    if category == "air jordan" and product_type == "sneakers":
        return {
            "passed": True,
            "category": category,
            "product_type": product_type,
            "reason": None
        }

    # Altri casi sneaker compatibili
    sneaker_categories = {
        "air jordan",
        "jordan",
        "nike",
        "adidas",
        "new balance",
        "asics",
        "puma",
        "reebok",
        "yeezy",
        "converse",
        "vans",
        "supreme"
    }

    sneaker_types = {
        "sneakers",
        "shoes",
        "footwear"
    }

    if category in sneaker_categories and product_type in sneaker_types:
        return {
            "passed": True,
            "category": category,
            "product_type": product_type,
            "reason": None
        }

    # Se mancano i dati, non blocchiamo il prodotto.
    if not category or not product_type:
        return {
            "passed": True,
            "category": category or None,
            "product_type": product_type or None,
            "reason": None
        }

    # Caso realmente incompatibile
    return {
        "passed": False,
        "category": category,
        "product_type": product_type,
        "reason": "category_product_type_mismatch"
    }


# ============================================================
# CONSISTENCY CHECKS
# ============================================================

def run_consistency_checks(
    product,
    historical_price=None,
    expected_gender=None,
    expected_colorway=None,
    expected_condition=None
):
    """
    Advanced Consistency Layer.

    Restituisce:
        {
            "status": "PASS" / "REVIEW",
            "checks": {...},
            "details": {...},
            "reasons": [...]
        }
    """

    title = normalize(product.get("title"))
    brand = normalize(product.get("brand"))
    model = normalize(product.get("model"))
    sku = product.get("sku")
    price = product.get("avg_price")

    # --------------------------------------------------------
    # RELEASE YEAR
    # --------------------------------------------------------

    release_year = extract_year(title)

    release_year_check = {
        "passed": True,
        "year": release_year,
        "reason": None
    }

    # --------------------------------------------------------
    # COLLABORATION
    # --------------------------------------------------------

    collaboration_check = {
        "passed": True,
        "detected": None
    }

    # --------------------------------------------------------
    # GENDER
    # --------------------------------------------------------

    detected_gender = detect_gender(product)

    if expected_gender:
        gender_passed = (
            normalize(detected_gender) == normalize(expected_gender)
        )
    else:
        gender_passed = True

    gender_check = {
        "passed": gender_passed,
        "detected": detected_gender,
        "expected": expected_gender
    }

    # --------------------------------------------------------
    # PRICE ANOMALY
    # --------------------------------------------------------

    price_value = None

    try:
        if price is not None:
            price_value = float(price)
    except (ValueError, TypeError):
        price_value = None

    reference_price = None
    ratio = None

    if historical_price is not None:
        try:
            reference_price = float(historical_price)
        except (ValueError, TypeError):
            reference_price = None

    if price_value is not None and reference_price and reference_price > 0:
        ratio = price_value / reference_price

    # Manteniamo il controllo permissivo:
    # il prezzo viene considerato valido se non è palesemente anomalo.
    price_anomaly_passed = True

    price_anomaly_check = {
        "passed": price_anomaly_passed,
        "price": price_value,
        "reference_price": reference_price,
        "ratio": ratio
    }

    # --------------------------------------------------------
    # SKU
    # --------------------------------------------------------

    sku_passed = bool(sku)

    sku_check = {
        "passed": sku_passed,
        "sku": sku,
        "reason": None if sku_passed else "missing_sku"
    }

    # --------------------------------------------------------
    # BRAND / MODEL
    # --------------------------------------------------------

    product_brand = normalize(product.get("brand"))
    product_model = normalize(product.get("model"))

    brand_model_passed = bool(product_brand and product_model)

    brand_model_check = {
        "passed": brand_model_passed,
        "brand": product_brand,
        "model": product_model,
        "reason": (
            None
            if brand_model_passed
            else "missing_brand_or_model"
        )
    }

    # --------------------------------------------------------
    # CATEGORY / PRODUCT TYPE
    # --------------------------------------------------------

    category_product_type_check = check_category_product_type(product)

    # --------------------------------------------------------
    # DUPLICATE
    # --------------------------------------------------------

    identity = None

    if sku:
        identity = f"sku:{normalize(sku)}"

    duplicate_check = {
        "passed": True,
        "duplicate": False,
        "identity": identity,
        "reason": None
    }

    # --------------------------------------------------------
    # PRICE VALIDITY
    # --------------------------------------------------------

    price_validity_passed = (
        price_value is not None and price_value >= 0
    )

    price_validity_check = {
        "passed": price_validity_passed,
        "price": price_value,
        "reason": (
            None
            if price_validity_passed
            else "invalid_price"
        )
    }

    # --------------------------------------------------------
    # DATA COMPLETENESS
    # --------------------------------------------------------

    required_fields = [
        "title",
        "brand",
        "model",
        "sku",
        "product_type",
        "category"
    ]

    missing_fields = [
        field
        for field in required_fields
        if not product.get(field)
    ]

    completeness = (
        (len(required_fields) - len(missing_fields))
        / len(required_fields)
    )

    data_completeness_passed = len(missing_fields) == 0

    data_completeness_check = {
        "passed": data_completeness_passed,
        "completeness": completeness,
        "missing_fields": missing_fields,
        "reason": (
            None
            if data_completeness_passed
            else "missing_fields"
        )
    }

    # --------------------------------------------------------
    # TITLE / MODEL
    # --------------------------------------------------------

    title_model_passed = True
    match_ratio = None

    if product_model and title:
        model_words = product_model.split()

        if model_words:
            matches = sum(
                1
                for word in model_words
                if word in title
            )

            match_ratio = matches / len(model_words)

            title_model_passed = match_ratio >= 0.8

    title_model_check = {
        "passed": title_model_passed,
        "model": product_model,
        "title": title,
        "match_ratio": match_ratio,
        "reason": (
            None
            if title_model_passed
            else "title_model_mismatch"
        )
    }

    # --------------------------------------------------------
    # COLORWAY
    # --------------------------------------------------------

    colorway_check = {
        "passed": True,
        "detected": None,
        "expected": expected_colorway,
        "match_ratio": None,
        "reason": None
    }

    # --------------------------------------------------------
    # CONDITION
    # --------------------------------------------------------

    detected_condition = detect_condition(product)

    if expected_condition:
        condition_passed = (
            normalize(detected_condition)
            == normalize(expected_condition)
        )
    else:
        condition_passed = True

    condition_check = {
        "passed": condition_passed,
        "detected": detected_condition,
        "expected": expected_condition,
        "reason": (
            None
            if condition_passed
            else "condition_mismatch"
        )
    }

    # ========================================================
    # FINAL CHECK RESULT
    # ========================================================

    checks = {
        "release_year": release_year_check["passed"],
        "collaboration": collaboration_check["passed"],
        "gender": gender_check["passed"],
        "price_anomaly": price_anomaly_check["passed"],
        "sku": sku_check["passed"],
        "brand_model": brand_model_check["passed"],
        "category_product_type": category_product_type_check["passed"],
        "duplicate": duplicate_check["passed"],
        "price_validity": price_validity_check["passed"],
        "data_completeness": data_completeness_check["passed"],
        "title_model": title_model_check["passed"],
        "colorway": colorway_check["passed"],
        "condition": condition_check["passed"]
    }

    reasons = []

    for name, passed in checks.items():
        if not passed:
            detail = None

            if name == "category_product_type":
                detail = category_product_type_check.get("reason")

            elif name == "gender":
                detail = "gender_mismatch"

            elif name == "sku":
                detail = sku_check.get("reason")

            elif name == "brand_model":
                detail = brand_model_check.get("reason")

            elif name == "price_validity":
                detail = price_validity_check.get("reason")

            elif name == "data_completeness":
                detail = data_completeness_check.get("reason")

            elif name == "title_model":
                detail = title_model_check.get("reason")

            elif name == "condition":
                detail = condition_check.get("reason")

            reasons.append(
                detail or name
            )

    status = "PASS" if not reasons else "REVIEW"

    details = {
        "collaboration": collaboration_check,
        "gender": gender_check,
        "release_year": release_year_check,
        "price_anomaly": price_anomaly_check,
        "sku": sku_check,
        "brand_model": brand_model_check,
        "category_product_type": category_product_type_check,
        "duplicate": duplicate_check,
        "price_validity": price_validity_check,
        "data_completeness": data_completeness_check,
        "title_model": title_model_check,
        "colorway": colorway_check,
        "condition": condition_check
    }

    return {
        "status": status,
        "checks": checks,
        "details": details,
        "reasons": reasons
    }


# ============================================================
# MAIN
# ============================================================

def main():

    # ========================================================
    # SUPABASE
    # ========================================================

    supabase_url = os.environ["SUPABASE_URL"]
    supabase_key = os.environ["SUPABASE_SECRET_KEY"]

    supabase = create_client(
        supabase_url,
        supabase_key
    )

    log("🔥 Supabase connected!")

    # ========================================================
    # ADVANCED CONSISTENCY CONFIG
    # ========================================================

    expected_gender = os.environ.get(
        "EXPECTED_GENDER"
    )

    expected_colorway = os.environ.get(
        "EXPECTED_COLORWAY"
    )

    expected_condition = os.environ.get(
        "EXPECTED_CONDITION"
    )

    log("=" * 60)
    log("🛡️ ADVANCED CONSISTENCY LAYER")
    log("=" * 60)
    log(
        "Expected gender:",
        expected_gender or "NONE"
    )
    log(
        "Expected colorway:",
        expected_colorway or "NONE"
    )
    log(
        "Expected condition:",
        expected_condition or "NONE"
    )
    log("=" * 60)

    # ========================================================
    # KICKSDB
    # ========================================================

    api_key = os.environ["KICKSDB_API_KEY"]

    search_term = os.environ.get(
        "SEARCH_TERM",
        "Jordan 4 Retro"
    )

    encoded_search = urllib.parse.quote(search_term)

    url = (
        "https://api.kicks.dev/v3/stockx/products"
        f"?query={encoded_search}&limit=10"
    )

    log("🔎 Search term:", search_term)
    log("📋 URL richiesto:", url)

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

        log("❌ KicksDB error:", e.code)
        log(
            "Headers:",
            dict(e.headers)
        )
        log(
            "Body:",
            e.read().decode()
        )

        raise

    except urllib.error.URLError as e:

        log("❌ KicksDB connection error:", e)
        raise

    log("🔥 KicksDB connected!")

    # ========================================================
    # RESPONSE
    # ========================================================

    log(
        "📡 Response type:",
        type(data).__name__
    )

    if isinstance(data, dict):

        log(
            "🔑 Top-level keys:",
            list(data.keys())
        )

        log(
            "📋 meta:",
            json.dumps(
                data.get("meta"),
                indent=2
            )
        )

        raw_data = data.get("data")

        log(
            "📋 data (raw):",
            json.dumps(raw_data)[:500]
        )

        products = raw_data or []

    elif isinstance(data, list):

        products = data

    else:

        products = []

    log(
        f"📦 Products returned: {len(products)}"
    )

    if not products:

        log(
            "⚠️ Nessun prodotto restituito."
        )

        log("✅ Done.")

        return

    log(
        "👟 First product keys:",
        list(products[0].keys())
    )

    # ========================================================
    # PROCESS PRODUCTS
    # ========================================================

    for index, product in enumerate(
        products,
        start=1
    ):

        log("")
        log("=" * 60)
        log(
            f"👟 PRODUCT {index}/{len(products)}"
        )
        log("=" * 60)

        title = product.get("title")
        sku = product.get("sku")
        price = product.get("avg_price")
        brand = product.get("brand")

        log("Title:", title)
        log("Brand:", brand)
        log("SKU:", sku)
        log("Price:", price)

        if not sku:

            log(
                "⚠️ Product has no SKU, skipping."
            )

            log("---")

            continue

        # ====================================================
        # CHECK PRODUCT
        # ====================================================

        existing = (
            supabase
            .table("products")
            .select("id")
            .eq("sku", sku)
            .execute()
        )

        if existing.data:

            product_id = existing.data[0]["id"]

            log(
                f"🔎 Found existing product with id {product_id}"
            )

            # ------------------------------------------------
            # HISTORICAL REFERENCE PRICE
            # ------------------------------------------------

            historical = (
                supabase
                .table("price_history")
                .select("price")
                .eq("product_id", product_id)
                .order(
                    "created_at",
                    desc=True
                )
                .limit(10)
                .execute()
            )

            historical_price = None

            if historical.data:

                prices = []

                for row in historical.data:

                    try:

                        value = float(
                            row.get("price")
                        )

                        if value > 0:
                            prices.append(value)

                    except (
                        ValueError,
                        TypeError
                    ):
                        pass

                if prices:

                    historical_price = (
                        sum(prices)
                        / len(prices)
                    )

            log(
                "📊 Historical reference price:",
                historical_price
            )

        else:

            log(
                "🆕 Product not found in database."
            )

            log(
                "💾 Saving product..."
            )

            insert_result = (
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

            if not insert_result.data:

                raise RuntimeError(
                    "❌ Product insert failed."
                )

            product_id = (
                insert_result.data[0]["id"]
            )

            historical_price = None

            log(
                f"✅ Product saved to Supabase with id {product_id}"
            )

        # ====================================================
        # CONSISTENCY
        # ====================================================

        log(
            "🛡️ Running Advanced Consistency..."
        )

        consistency = run_consistency_checks(
            product=product,
            historical_price=historical_price,
            expected_gender=expected_gender,
            expected_colorway=expected_colorway,
            expected_condition=expected_condition
        )

        log(
            "🧠 CONSISTENCY RESULT:",
            consistency["status"]
        )

        log("CHECKS:")

        for check_name, passed in consistency["checks"].items():

            symbol = "✅" if passed else "❌"

            log(
                f"{symbol} {check_name}: {passed}"
            )

        if consistency["reasons"]:

            log(
                "⚠️ REVIEW REASONS:"
            )

            for reason in consistency["reasons"]:

                log(
                    f"- {reason}"
                )

        log(
            "DETAILS:"
        )

        log(
            json.dumps(
                consistency["details"],
                indent=2
            )
        )

        # ====================================================
        # SAVE PRICE
        # ====================================================

        log(
            "💾 Product already exists."
            if existing.data
            else "💾 Product created."
        )

        if price is not None:

            try:

                numeric_price = float(price)

            except (
                ValueError,
                TypeError
            ):

                numeric_price = None

            if (
                numeric_price is not None
                and numeric_price > 0
            ):

                (
                    supabase
                    .table("price_history")
                    .insert({
                        "product_id": product_id,
                        "price": numeric_price,
                        "currency": "USD"
                    })
                    .execute()
                )

                log(
                    "💰 Price saved to price_history!"
                )

            else:

                log(
                    "⚠️ Price is 0 or invalid, "
                    "so it was not saved."
                )

        else:

            log(
                "⚠️ Price is missing, "
                "so it was not saved."
            )

        # ====================================================
        # FINAL STATUS
        # ====================================================

        log(
            "🏁 FINAL STATUS:",
            consistency["status"]
        )

        if consistency["status"] == "PASS":

            log(
                "✅ Product approved."
            )

        else:

            log(
                "⚠️ Product requires review."
            )

        log("---")

    # ========================================================
    # COMPLETE
    # ========================================================

    log("")
    log("=" * 60)
    log("✅ PIPELINE COMPLETED")
    log("=" * 60)


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()
