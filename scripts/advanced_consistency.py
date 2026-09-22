import re


# ============================================================
# ADVANCED CONSISTENCY LAYER
# ============================================================

COLLAB_KEYWORDS = {
    "travis scott",
    "off-white",
    "dior",
    "fragment",
    "union",
    "sacai",
    "ambush",
    "supreme",
    "fear of god",
    "stussy",
    "kaws",
}

GENDER_KEYWORDS = {
    "women": "WOMEN",
    "woman": "WOMEN",
    "womens": "WOMEN",
    "women's": "WOMEN",
    "w": "WOMEN",

    "men": "MEN",
    "man": "MEN",
    "mens": "MEN",
    "men's": "MEN",

    "gs": "GS",
    "grade school": "GS",
    "junior": "GS",

    "toddler": "TODDLER",
    "td": "TODDLER",

    "infant": "INFANT",

    "unisex": "UNISEX",
}


def normalize_text(value):
    """
    Normalize text for consistency checks.
    """
    if not value:
        return ""

    return re.sub(
        r"\s+",
        " ",
        str(value).strip().lower()
    )


def extract_product_text(product):
    """
    Combine the most useful product fields into one searchable string.
    """
    fields = [
        product.get("title"),
        product.get("model"),
        product.get("primary_title"),
        product.get("secondary_title"),
        product.get("description"),
    ]

    return normalize_text(" ".join(
        str(field)
        for field in fields
        if field
    ))


def check_collaboration(product):
    """
    Detect known collaboration / special-edition keywords.

    Returns:
        {
            "passed": True/False,
            "detected": "..."/None
        }
    """
    text = extract_product_text(product)

    for keyword in COLLAB_KEYWORDS:
        if keyword in text:
            return {
                "passed": False,
                "detected": keyword,
            }

    return {
        "passed": True,
        "detected": None,
    }


def detect_gender(product):
    """
    Detect the likely target audience from product text.

    Returns:
        MEN / WOMEN / GS / TODDLER / INFANT / UNISEX / UNKNOWN
    """
    text = extract_product_text(product)

    # More specific multi-word expressions first.
    ordered_keywords = sorted(
        GENDER_KEYWORDS.items(),
        key=lambda item: len(item[0]),
        reverse=True,
    )

    for keyword, gender in ordered_keywords:
        pattern = rf"\b{re.escape(keyword)}\b"

        if re.search(pattern, text):
            return gender

    return "UNKNOWN"


def check_gender(product, expected_gender=None):
    """
    Compare detected product gender with the expected watchlist intent.

    If no expected gender is supplied, the check passes without
    imposing a restriction.
    """
    detected_gender = detect_gender(product)

    if not expected_gender:
        return {
            "passed": True,
            "detected": detected_gender,
            "expected": None,
        }

    expected_gender = expected_gender.upper()

    if detected_gender == "UNKNOWN":
        return {
            "passed": True,
            "detected": detected_gender,
            "expected": expected_gender,
        }

    return {
        "passed": detected_gender == expected_gender,
        "detected": detected_gender,
        "expected": expected_gender,
    }


def check_release_year(product, model_history=None):
    """
    Preliminary release-year consistency check.

    This first version is intentionally conservative.
    If no model history or release year is available,
    the check passes without making assumptions.
    """
    if not model_history:
        return {
            "passed": True,
            "year": None,
            "reason": None,
        }

    release_year = product.get("release_year")

    if release_year is None:
        return {
            "passed": True,
            "year": None,
            "reason": None,
        }

    try:
        release_year = int(release_year)
    except (TypeError, ValueError):
        return {
            "passed": False,
            "year": release_year,
            "reason": "invalid_release_year",
        }

    min_year = model_history.get("first_known_year")

    if min_year is not None and release_year < min_year:
        return {
            "passed": False,
            "year": release_year,
            "reason": "release_year_before_model_origin",
        }

    return {
        "passed": True,
        "year": release_year,
        "reason": None,
    }


def check_price_anomaly(product, reference_price=None):
    """
    Preliminary price anomaly check.

    This does NOT reject expensive products.
    It only flags a product when a reference price exists
    and the deviation is extreme.

    Threshold:
        > 500% of reference price
        OR
        < 1/5 of reference price
    """
    price = product.get("avg_price")

    if price is None or reference_price is None:
        return {
            "passed": True,
            "price": price,
            "reference_price": reference_price,
            "ratio": None,
        }

    try:
        price = float(price)
        reference_price = float(reference_price)
    except (TypeError, ValueError):
        return {
            "passed": True,
            "price": price,
            "reference_price": reference_price,
            "ratio": None,
        }

    if price <= 0 or reference_price <= 0:
        return {
            "passed": True,
            "price": price,
            "reference_price": reference_price,
            "ratio": None,
        }

    ratio = price / reference_price

    if ratio > 5 or ratio < 0.2:
        return {
            "passed": False,
            "price": price,
            "reference_price": reference_price,
            "ratio": ratio,
        }

    return {
        "passed": True,
        "price": price,
        "reference_price": reference_price,
        "ratio": ratio,
    }


def run_advanced_consistency(
    product,
    expected_gender=None,
    model_history=None,
    reference_price=None,
):
    """
    Run all Advanced Consistency checks.

    This function does not modify the existing validator status.
    It only returns additional information.
    """

    collaboration = check_collaboration(product)

    gender = check_gender(
        product,
        expected_gender=expected_gender,
    )

    release_year = check_release_year(
        product,
        model_history=model_history,
    )

    price_anomaly = check_price_anomaly(
        product,
        reference_price=reference_price,
    )

    checks = {
        "release_year": release_year["passed"],
        "collaboration": collaboration["passed"],
        "gender": gender["passed"],
        "price_anomaly": price_anomaly["passed"],
    }

    review_reasons = []

    if not collaboration["passed"]:
        review_reasons.append(
            "collaboration_detected"
        )

    if not gender["passed"]:
        review_reasons.append(
            "gender_mismatch"
        )

    if not release_year["passed"]:
        review_reasons.append(
            release_year["reason"]
        )

    if not price_anomaly["passed"]:
        review_reasons.append(
            "price_anomaly"
        )

    return {
        "checks": checks,
        "review_reasons": review_reasons,
        "details": {
            "collaboration": collaboration,
            "gender": gender,
            "release_year": release_year,
            "price_anomaly": price_anomaly,
        },
    }
