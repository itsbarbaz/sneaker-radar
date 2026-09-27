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


# ============================================================
# COLORWAY
# ============================================================

def normalize_text(value):
    if not value:
        return ""

    return re.sub(
        r"\s+",
        " ",
        str(value).strip().lower()
    )


def extract_product_text(product):
    fields = [
        product.get("title"),
        product.get("model"),
        product.get("primary_title"),
        product.get("secondary_title"),
        product.get("description"),
        product.get("colorway"),
    ]

    return normalize_text(
        " ".join(
            str(field)
            for field in fields
            if field
        )
    )


def tokenize_colorway(value):
    """
    Trasforma una colorway in token confrontabili.
    """
    text = normalize_text(value)

    if not text:
        return set()

    text = re.sub(r"[^a-z0-9\s]", " ", text)

    return {
        token
        for token in text.split()
        if len(token) >= 2
    }


def check_colorway(product, expected_colorway=None):
    """
    Controlla che la colorway richiesta sia compatibile
    con quella dichiarata/rilevata nel prodotto.

    Se expected_colorway non viene fornita, il controllo
    passa senza inventare informazioni.
    """

    detected = product.get("colorway")

    if detected is None:
        text = extract_product_text(product)

        # Se non abbiamo un campo colorway separato,
        # non facciamo un'inferenza aggressiva.
        detected = ""

        if text:
            detected = product.get("colorway") or ""

    detected = normalize_text(detected)

    if not expected_colorway:
        return {
            "passed": True,
            "detected": detected or None,
            "expected": None,
            "match_ratio": None,
            "reason": None,
        }

    expected = normalize_text(expected_colorway)

    expected_tokens = tokenize_colorway(expected)
    detected_tokens = tokenize_colorway(detected)

    if not expected_tokens:
        return {
            "passed": True,
            "detected": detected or None,
            "expected": expected,
            "match_ratio": None,
            "reason": None,
        }

    if not detected_tokens:
        return {
            "passed": False,
            "detected": None,
            "expected": expected,
            "match_ratio": 0.0,
            "reason": "missing_colorway",
        }

    matched = expected_tokens.intersection(detected_tokens)

    match_ratio = len(matched) / len(expected_tokens)

    if match_ratio >= 0.5:
        return {
            "passed": True,
            "detected": detected,
            "expected": expected,
            "match_ratio": match_ratio,
            "reason": None,
        }

    return {
        "passed": False,
        "detected": detected,
        "expected": expected,
        "match_ratio": match_ratio,
        "reason": "colorway_mismatch",
    }


# ============================================================
# CONDITION
# ============================================================

CONDITION_KEYWORDS = {
    "deadstock": "NEW",
    "ds": "NEW",
    "brand new": "NEW",
    "new": "NEW",
    "unworn": "NEW",
    "unused": "NEW",

    "used": "USED",
    "pre-owned": "USED",
    "preowned": "USED",
    "worn": "USED",

    "very good": "USED",
    "good condition": "USED",

    "damaged": "DAMAGED",
    "damage": "DAMAGED",
    "defect": "DAMAGED",
    "defective": "DAMAGED",
}


def detect_condition(product):
    """
    Determina la condizione dichiarata del prodotto.
    """

    explicit_condition = normalize_text(
        product.get("condition")
    )

    if explicit_condition:
        for keyword, condition in sorted(
            CONDITION_KEYWORDS.items(),
            key=lambda item: len(item[0]),
            reverse=True,
        ):
            if keyword in explicit_condition:
                return condition

        return "UNKNOWN"

    text = normalize_text(
        " ".join(
            str(product.get(field))
            for field in [
                "title",
                "primary_title",
                "secondary_title",
                "description",
            ]
            if product.get(field)
        )
    )

    for keyword, condition in sorted(
        CONDITION_KEYWORDS.items(),
        key=lambda item: len(item[0]),
        reverse=True,
    ):
        pattern = rf"\b{re.escape(keyword)}\b"

        if re.search(pattern, text):
            return condition

    return "UNKNOWN"


def check_condition(product, expected_condition=None):
    """
    Confronta la condizione rilevata con quella richiesta.

    Se la condizione non è specificata, non viene inventata.
    """

    detected = detect_condition(product)

    if not expected_condition:
        return {
            "passed": True,
            "detected": detected,
            "expected": None,
            "reason": None,
        }

    expected = normalize_text(
        expected_condition
    ).upper()

    return {
        "passed": (
            detected == expected
            or detected == "UNKNOWN"
        ),
        "detected": detected,
        "expected": expected,
        "reason": (
            None
            if (
                detected == expected
                or detected == "UNKNOWN"
            )
            else "condition_mismatch"
        ),
    }


# ============================================================
# COLLABORATION
# ============================================================

def check_collaboration(product):
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


# ============================================================
# GENDER / SIZING
# ============================================================

def detect_gender(product):
    text = extract_product_text(product)

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


# ============================================================
# RELEASE YEAR
# ============================================================

def check_release_year(product, model_history=None):
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


# ============================================================
# PRICE ANOMALY
# ============================================================

def check_price_anomaly(product, reference_price=None):
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


# ============================================================
# SKU
# ============================================================

def check_sku(product):
    sku = product.get("sku")

    if sku is None or str(sku).strip() == "":
        return {
            "passed": False,
            "sku": None,
            "reason": "missing_sku",
        }

    sku = str(sku).strip()

    if len(sku) < 3:
        return {
            "passed": False,
            "sku": sku,
            "reason": "invalid_sku",
        }

    return {
        "passed": True,
        "sku": sku,
        "reason": None,
    }


# ============================================================
# BRAND ↔ MODEL
# ============================================================

def check_brand_model_consistency(product):
    brand = normalize_text(product.get("brand"))
    model = normalize_text(product.get("model"))
    title = normalize_text(product.get("title"))

    if not brand or not model:
        return {
            "passed": True,
            "brand": brand or None,
            "model": model or None,
            "reason": None,
        }

    combined = f"{model} {title}"

    known_brand_tokens = {
        "nike": {
            "nike",
            "jordan",
            "air force",
            "air max",
            "dunk",
        },

        "adidas": {
            "adidas",
            "yeezy",
            "samba",
            "gazelle",
            "campus",
        },

        "new balance": {
            "new balance",
            "nb",
            "990",
            "550",
        },

        "asics": {
            "asics",
            "gel",
        },

        "puma": {
            "puma",
            "suede",
            "palermo",
        },

        "reebok": {
            "reebok",
            "club c",
        },

        "hoka": {
            "hoka",
            "clifton",
            "bondi",
            "speedgoat",
        },

        "salomon": {
            "salomon",
            "xt-6",
            "acs",
        },
    }

    expected_tokens = known_brand_tokens.get(brand)

    if expected_tokens is None:
        return {
            "passed": True,
            "brand": brand,
            "model": model,
            "reason": None,
        }

    if any(token in combined for token in expected_tokens):
        return {
            "passed": True,
            "brand": brand,
            "model": model,
            "reason": None,
        }

    return {
        "passed": False,
        "brand": brand,
        "model": model,
        "reason": "brand_model_inconsistency",
    }


# ============================================================
# CATEGORY ↔ PRODUCT TYPE
# ============================================================

def check_category_product_type(product):
    category = normalize_text(product.get("category"))
    product_type = normalize_text(product.get("product_type"))

    if not category or not product_type:
        return {
            "passed": True,
            "category": category or None,
            "product_type": product_type or None,
            "reason": None,
        }

    footwear_terms = {
        "sneaker",
        "sneakers",
        "shoe",
        "shoes",
        "footwear",
    }

    category_is_footwear = any(
        term in category
        for term in footwear_terms
    )

    type_is_footwear = any(
        term in product_type
        for term in footwear_terms
    )

    if category_is_footwear == type_is_footwear:
        return {
            "passed": True,
            "category": category,
            "product_type": product_type,
            "reason": None,
        }

    return {
        "passed": False,
        "category": category,
        "product_type": product_type,
        "reason": "category_product_type_mismatch",
    }


# ============================================================
# DUPLICATE
# ============================================================

def build_product_identity(product):
    sku = normalize_text(product.get("sku"))

    if sku:
        return f"sku:{sku}"

    brand = normalize_text(product.get("brand"))
    model = normalize_text(product.get("model"))
    title = normalize_text(product.get("title"))

    return f"{brand}|{model}|{title}"


def check_duplicate(product, seen_identities=None):
    if seen_identities is None:
        return {
            "passed": True,
            "duplicate": False,
            "identity": None,
            "reason": None,
        }

    identity = build_product_identity(product)

    if identity in seen_identities:
        return {
            "passed": False,
            "duplicate": True,
            "identity": identity,
            "reason": "possible_duplicate",
        }

    return {
        "passed": True,
        "duplicate": False,
        "identity": identity,
        "reason": None,
    }


# ============================================================
# PRICE VALIDITY
# ============================================================

def check_price_validity(product):
    price = product.get("avg_price")

    if price is None:
        return {
            "passed": False,
            "price": None,
            "reason": "missing_price",
        }

    try:
        price = float(price)

    except (TypeError, ValueError):
        return {
            "passed": False,
            "price": price,
            "reason": "invalid_price",
        }

    if price <= 0:
        return {
            "passed": False,
            "price": price,
            "reason": "non_positive_price",
        }

    return {
        "passed": True,
        "price": price,
        "reason": None,
    }


# ============================================================
# DATA COMPLETENESS
# ============================================================

def check_data_completeness(product):
    required_fields = [
        "title",
        "brand",
        "model",
        "sku",
        "product_type",
        "avg_price",
    ]

    present = 0
    missing = []

    for field in required_fields:
        value = product.get(field)

        if value is not None and str(value).strip() != "":
            present += 1
        else:
            missing.append(field)

    completeness = present / len(required_fields)

    passed = completeness >= 0.5

    return {
        "passed": passed,
        "completeness": round(completeness, 4),
        "missing_fields": missing,
        "reason": (
            None
            if passed
            else "insufficient_data_completeness"
        ),
    }


# ============================================================
# TITLE ↔ MODEL
# ============================================================

def check_title_model_consistency(product):
    model = normalize_text(product.get("model"))
    title = normalize_text(product.get("title"))

    if not model or not title:
        return {
            "passed": True,
            "model": model or None,
            "title": title or None,
            "match_ratio": None,
            "reason": None,
        }

    model_tokens = [
        token
        for token in model.split()
        if len(token) >= 2
    ]

    if not model_tokens:
        return {
            "passed": True,
            "model": model,
            "title": title,
            "match_ratio": None,
            "reason": None,
        }

    matched_tokens = sum(
        1
        for token in model_tokens
        if token in title
    )

    match_ratio = matched_tokens / len(model_tokens)

    if match_ratio >= 0.5:
        return {
            "passed": True,
            "model": model,
            "title": title,
            "match_ratio": match_ratio,
            "reason": None,
        }

    return {
        "passed": False,
        "model": model,
        "title": title,
        "match_ratio": match_ratio,
        "reason": "title_model_inconsistency",
    }


# ============================================================
# MAIN ENGINE
# ============================================================

def run_advanced_consistency(
    product,
    expected_gender=None,
    model_history=None,
    reference_price=None,
    seen_identities=None,
    expected_colorway=None,
    expected_condition=None,
):

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

    sku = check_sku(product)

    brand_model = check_brand_model_consistency(product)

    category_product_type = check_category_product_type(
        product
    )

    duplicate = check_duplicate(
        product,
        seen_identities=seen_identities,
    )

    price_validity = check_price_validity(product)

    completeness = check_data_completeness(product)

    title_model = check_title_model_consistency(product)

    colorway = check_colorway(
        product,
        expected_colorway=expected_colorway,
    )

    condition = check_condition(
        product,
        expected_condition=expected_condition,
    )

    # ========================================================
    # CHECKS
    # ========================================================

    checks = {
        "release_year": release_year["passed"],
        "collaboration": collaboration["passed"],
        "gender": gender["passed"],
        "price_anomaly": price_anomaly["passed"],
        "sku": sku["passed"],
        "brand_model": brand_model["passed"],
        "category_product_type": (
            category_product_type["passed"]
        ),
        "duplicate": duplicate["passed"],
        "price_validity": price_validity["passed"],
        "data_completeness": completeness["passed"],
        "title_model": title_model["passed"],
        "colorway": colorway["passed"],
        "condition": condition["passed"],
    }

    # ========================================================
    # REVIEW REASONS
    # ========================================================

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

    if not sku["passed"]:
        review_reasons.append(
            sku["reason"]
        )

    if not brand_model["passed"]:
        review_reasons.append(
            brand_model["reason"]
        )

    if not category_product_type["passed"]:
        review_reasons.append(
            category_product_type["reason"]
        )

    if not duplicate["passed"]:
        review_reasons.append(
            duplicate["reason"]
        )

    if not price_validity["passed"]:
        review_reasons.append(
            price_validity["reason"]
        )

    if not completeness["passed"]:
        review_reasons.append(
            completeness["reason"]
        )

    if not title_model["passed"]:
        review_reasons.append(
            title_model["reason"]
        )

    if not colorway["passed"]:
        review_reasons.append(
            colorway["reason"]
        )

    if not condition["passed"]:
        review_reasons.append(
            condition["reason"]
        )

    # ========================================================
    # RESULT
    # ========================================================

    return {
        "checks": checks,

        "review_reasons": [
            reason
            for reason in review_reasons
            if reason
        ],

        "details": {
            "collaboration": collaboration,
            "gender": gender,
            "release_year": release_year,
            "price_anomaly": price_anomaly,
            "sku": sku,
            "brand_model": brand_model,
            "category_product_type": (
                category_product_type
            ),
            "duplicate": duplicate,
            "price_validity": price_validity,
            "data_completeness": completeness,
            "title_model": title_model,
            "colorway": colorway,
            "condition": condition,
        },
    }
