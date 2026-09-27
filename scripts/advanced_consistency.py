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
# NORMALIZZAZIONE
# ============================================================

def normalize_text(value):
    """
    Normalizza il testo per i controlli di coerenza.
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
    Unisce i principali campi testuali del prodotto.
    """
    fields = [
        product.get("title"),
        product.get("model"),
        product.get("primary_title"),
        product.get("secondary_title"),
        product.get("description"),
    ]

    return normalize_text(
        " ".join(
            str(field)
            for field in fields
            if field
        )
    )


# ============================================================
# 1. COLLABORATION
# ============================================================

def check_collaboration(product):
    """
    Cerca collaborazioni note nel prodotto.
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


# ============================================================
# 2. GENDER / SIZING
# ============================================================

def detect_gender(product):
    """
    Determina il target più probabile del prodotto.
    """

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
    """
    Confronta il target rilevato con quello atteso.
    """

    detected_gender = detect_gender(product)

    if not expected_gender:
        return {
            "passed": True,
            "detected": detected_gender,
            "expected": None,
        }

    expected_gender = expected_gender.upper()

    # UNKNOWN non viene considerato automaticamente un errore.
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
# 3. RELEASE YEAR
# ============================================================

def check_release_year(product, model_history=None):
    """
    Controlla che l'anno di release non sia precedente
    all'origine conosciuta del modello.
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


# ============================================================
# 4. PRICE ANOMALY
# ============================================================

def check_price_anomaly(product, reference_price=None):
    """
    Controlla deviazioni estreme rispetto al prezzo di riferimento.

    Soglie:
        > 5x reference = anomalia
        < 0.2x reference = anomalia
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


# ============================================================
# 5. SKU CONSISTENCY
# ============================================================

def check_sku(product):
    """
    Controlla che lo SKU esista e abbia una struttura minima plausibile.

    Non tenta di verificare se lo SKU sia quello ufficiale.
    """

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
# 6. BRAND ↔ MODEL
# ============================================================

def check_brand_model_consistency(product):
    """
    Controllo conservativo tra brand e modello.

    Se non ci sono abbastanza informazioni, non genera
    artificialmente un errore.
    """

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

    # Brand non presente nella nostra knowledge base:
    # non giudichiamo.
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
# 7. CATEGORY ↔ PRODUCT TYPE
# ============================================================

def check_category_product_type(product):
    """
    Controlla la coerenza generale tra categoria e product type.
    """

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
# 8. DUPLICATE / QUASI-DUPLICATE
# ============================================================

def build_product_identity(product):
    """
    Costruisce un'identità semplice del prodotto.

    Priorità:
        1. SKU
        2. brand + model + title
    """

    sku = normalize_text(product.get("sku"))

    if sku:
        return f"sku:{sku}"

    brand = normalize_text(product.get("brand"))
    model = normalize_text(product.get("model"))
    title = normalize_text(product.get("title"))

    return f"{brand}|{model}|{title}"


def check_duplicate(product, seen_identities=None):
    """
    Controlla se l'identità del prodotto è già stata vista.
    """

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
# 9. PRICE VALIDITY
# ============================================================

def check_price_validity(product):
    """
    Controlla che il prezzo sia numericamente utilizzabile.

    Questo è diverso da price_anomaly.
    """

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
# 10. DATA COMPLETENESS
# ============================================================

def check_data_completeness(product):
    """
    Misura la completezza dei principali campi.

    Non richiede necessariamente che tutti siano presenti.
    """

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

    # Soglia conservativa.
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
# 11. TITLE ↔ MODEL
# ============================================================

def check_title_model_consistency(product):
    """
    Controlla se il modello strutturato è ragionevolmente
    rappresentato nel titolo.
    """

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
# MAIN ADVANCED CONSISTENCY ENGINE
# ============================================================

def run_advanced_consistency(
    product,
    expected_gender=None,
    model_history=None,
    reference_price=None,
    seen_identities=None,
):
    """
    Esegue tutti gli 11 controlli Advanced Consistency.

    IMPORTANTE:
    questa funzione NON modifica direttamente lo status
    del validator principale.

    Restituisce:
        checks
        review_reasons
        details
    """

    # --------------------------------------------------------
    # ESECUZIONE CONTROLLI
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # CHECKS SINTETICI
    # --------------------------------------------------------

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
    }

    # --------------------------------------------------------
    # REVIEW REASONS
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # RISULTATO FINALE
    # --------------------------------------------------------

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
        },
    }
