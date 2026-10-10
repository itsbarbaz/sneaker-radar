import datetime
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

# Parole/frasi tipiche del mercato delle repliche (UA, PK,
# batch, ecc.). A differenza di COLLAB_KEYWORDS, qui usiamo un
# match a PAROLA INTERA (non sottostringa), perche' molte di
# queste parole sono corte e ambigue (es. "ua", "pk", "aaa") e
# un match a sottostringa darebbe troppi falsi positivi su
# parole che le contengono per caso.
#
# Aggiungi qui altre parole se ne trovi di nuove nei dati.
REPLICA_KEYWORDS = {
    "replica",
    "replicas",
    "rep",
    "reps",
    "fake",
    "fakes",
    "counterfeit",
    "bootleg",
    "knockoff",
    "knock-off",
    "unauthorized",
    "ua batch",
    "pk batch",
    "pk god",
    "god batch",
    "aaa quality",
    "1:1",
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
# UTILS & NORMALIZATION
# ============================================================

def normalize_text(value):
    if not value:
        return ""
    return re.sub(r"\s+", " ", str(value).strip().lower())


def extract_product_text(product):
    fields = [
        product.get("title"),
        product.get("model"),
        product.get("primary_title"),
        product.get("secondary_title"),
        product.get("description"),
        product.get("colorway"),
    ]
    return normalize_text(" ".join(str(field) for field in fields if field))


# ============================================================
# COLORWAY
# ============================================================

def tokenize_colorway(value):
    """
    Trasforma una colorway in token confrontabili.
    """
    text = normalize_text(value)
    if not text:
        return set()

    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return {token for token in text.split() if len(token) >= 2}


def check_colorway(product, expected_colorway=None):
    """
    Controlla che la colorway richiesta sia compatibile
    con quella dichiarata nel prodotto.

    Soglia abbassata a 0.4: i nomi delle colorway nei vari
    marketplace sono scritti in modi molto diversi tra loro
    (es. "Black Cement" vs "Cement Grey Black Fire Red"), quindi
    una soglia troppo alta (0.6) scartava colorway che in realtà
    erano la stessa, solo descritta con parole diverse.
    """
    detected = product.get("colorway")
    if detected is None:
        detected = ""
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
        # Nessuna colorway dichiarata dal prodotto: non è un
        # motivo sufficiente per scartarlo, lo segnaliamo solo
        # per revisione manuale invece di rigettarlo.
        return {
            "passed": True,
            "detected": None,
            "expected": expected,
            "match_ratio": 0.0,
            "reason": "missing_colorway",
        }

    matched = expected_tokens.intersection(detected_tokens)
    match_ratio = len(matched) / len(expected_tokens)

    # Soglia abbassata a 0.4 (era 0.6).
    if match_ratio >= 0.4:
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
    explicit_condition = normalize_text(product.get("condition"))

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
    """
    detected = detect_condition(product)

    if not expected_condition:
        return {
            "passed": True,
            "detected": detected,
            "expected": None,
            "reason": None,
        }

    expected = normalize_text(expected_condition).upper()

    passed = (detected == expected or detected == "UNKNOWN")
    return {
        "passed": passed,
        "detected": detected,
        "expected": expected,
        "reason": None if passed else "condition_mismatch",
    }


# ============================================================
# COLLABORATION
# ============================================================
#
# IMPORTANTE: una collaborazione (Travis Scott, Off-White, Dior,
# ecc.) è un prodotto valido a tutti gli effetti, NON un errore.
# In precedenza questa funzione ritornava "passed": False quando
# rilevava una collab, e quel False veniva sommato ai motivi di
# scarto in run_advanced_consistency, facendo rigettare OGNI
# singola collab a prescindere da SKU, prezzo o qualità dei dati.
#
# Ora "passed" è sempre True: rilevare una collaborazione non
# blocca più l'approvazione. "is_collaboration" resta disponibile
# come informazione (serve anche a check_price_anomaly per
# allargare la tolleranza di prezzo sulle collab, che hanno
# naturalmente un mercato più caro e più volatile).

def check_collaboration(product):
    text = extract_product_text(product)

    for keyword in COLLAB_KEYWORDS:
        if keyword in text:
            return {
                "passed": True,
                "is_collaboration": True,
                "detected": keyword,
            }

    return {
        "passed": True,
        "is_collaboration": False,
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
# PRICE ANOMALY (DINAMICA CON COLLABORATIVE TOLERANCE)
# ============================================================

def check_price_anomaly(product, reference_price=None):
    """
    Segnala un prezzo fuori range rispetto a un prezzo di
    riferimento (es. prezzo medio storico del modello).

    Range allargato rispetto a prima:
      - prodotti normali: 0.2x - 4.0x (era 0.25x - 3.0x)
      - collaborazioni:   0.2x - 8.0x (era 0.25x - 6.0x)

    Le collab hanno mercati molto più nervosi (possono valere
    2-10 volte il prezzo di retail), quindi una soglia stretta
    le faceva scartare come "anomale" anche quando il prezzo era
    del tutto normale per quel tipo di prodotto.
    """
    price = product.get("avg_price")

    if price is None or reference_price is None:
        return {
            "passed": True,
            "price": price,
            "reference_price": reference_price,
            "ratio": None,
            "reason": None,
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
            "reason": None,
        }

    if price <= 0 or reference_price <= 0:
        return {
            "passed": True,
            "price": price,
            "reference_price": reference_price,
            "ratio": None,
            "reason": None,
        }

    ratio = price / reference_price

    is_collab = check_collaboration(product)["is_collaboration"]
    max_ratio = 8.0 if is_collab else 4.0
    min_ratio = 0.2

    if ratio > max_ratio or ratio < min_ratio:
        return {
            "passed": False,
            "price": price,
            "reference_price": reference_price,
            "ratio": ratio,
            "reason": "price_anomaly",
        }

    return {
        "passed": True,
        "price": price,
        "reference_price": reference_price,
        "ratio": ratio,
        "reason": None,
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
    """
    Controlla che il brand dichiarato sia compatibile con il
    modello/titolo del prodotto, usando un elenco di parole
    chiave note per brand.

    FIX: prima, una collaborazione (es. "Travis Scott x Air
    Jordan 1") su un brand NON presente in known_brand_tokens
    passava comunque (nessuna regola = ok), ma se il brand era
    "Jordan"/"Nike" il controllo si basava solo sui token noti:
    questo restava corretto, il problema vero della collab era
    altrove (check_collaboration). Qui aggiungiamo solo i token
    mancanti più comuni (es. "jordan" sotto "nike" già c'era,
    aggiungiamo "sb" per Nike, "ultraboost"/"stan smith" per
    adidas, "990v" per New Balance) per ridurre i falsi scarti.
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
            "sb",
            "kobe",
            "vomero",
            "p-6000",
            "p 6000",
        },
        "adidas": {
            "adidas",
            "yeezy",
            "samba",
            "gazelle",
            "campus",
            "taekwondo",
            "adizero",
            "ultraboost",
            "stan smith",
        },
        "new balance": {
            "new balance",
            "nb",
            "990",
            "550",
            "1906r",
            "2002r",
            "9060",
            "530",
            "993",
            "204l",
        },
        "asics": {
            "asics",
            "gel",
            "gt-2160",
            "gt 2160",
            "novablast",
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
            "xt-4",
            "xt 6",
            "xt 4",
            "acs",
            "speedcross",
        },
        "on": {
            "on",
            "cloud",
            "cloudmonster",
            "cloudtilt",
            "cloudsurfer",
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

    category_is_footwear = any(term in category for term in footwear_terms)
    type_is_footwear = any(term in product_type for term in footwear_terms)

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
# CURRENCY
# ============================================================
#
# Il progetto lavora in USD in via prioritaria. KicksDB, nei
# dati osservati finora, non espone mai un campo valuta
# esplicito nella risposta: assumiamo quindi che il prezzo sia
# gia' in USD quando nessuno dei campi noti e' presente, per
# non rompere nulla di quello che funziona oggi.
#
# Se in futuro KicksDB (o un'altra fonte, se mai se ne
# aggiungeranno) iniziasse a restituire un campo valuta e
# questo non fosse USD, il prodotto viene segnalato per
# revisione (non scartato), cosi' il dato resta visibile ma
# marcato come da verificare prima di trattarlo come se fosse
# in USD.
#
# Si controllano piu' nomi di campo possibili perche' non
# conosciamo con certezza quale userebbe una fonte diversa da
# KicksDB: se scopri il nome esatto che usa KicksDB (o altre
# fonti), aggiungilo qui.

CURRENCY_FIELD_CANDIDATES = (
    "currency",
    "currency_code",
    "price_currency",
    "avg_price_currency",
)


def detect_currency(product):
    """
    Cerca un campo valuta esplicito nel prodotto. Ritorna None
    se nessun campo e' presente (caso osservato finora con
    KicksDB), altrimenti la valuta normalizzata in maiuscolo.
    """
    for field in CURRENCY_FIELD_CANDIDATES:
        value = product.get(field)

        if value is not None and str(value).strip() != "":
            return str(value).strip().upper()

    return None


def check_currency(product, expected_currency="USD"):
    """
    Verifica che la valuta del prezzo sia quella attesa
    (USD di default).

    Nessun campo valuta trovato -> passa (si assume USD,
    coerente con tutti i dati KicksDB visti finora).

    Campo valuta trovato e combacia -> passa.

    Campo valuta trovato e NON combacia -> non passa, ma solo
    per revisione manuale: il dato potrebbe comunque essere
    utile (es. se in futuro si decide di supportare anche EUR),
    quindi non va scartato a priori come fosse un errore.
    """
    detected = detect_currency(product)

    if not expected_currency:
        return {
            "passed": True,
            "detected": detected,
            "expected": None,
            "reason": None,
        }

    expected = str(expected_currency).strip().upper()

    if detected is None:
        return {
            "passed": True,
            "detected": None,
            "expected": expected,
            "reason": None,
        }

    if detected == expected:
        return {
            "passed": True,
            "detected": detected,
            "expected": expected,
            "reason": None,
        }

    return {
        "passed": False,
        "detected": detected,
        "expected": expected,
        "reason": "currency_mismatch",
    }


# ============================================================
# COUNTERFEIT / REPLICA RISK
# ============================================================

def check_counterfeit_risk(product):
    """
    Cerca nel testo del prodotto (titolo, modello, descrizione,
    colorway) parole tipiche del mercato delle repliche (UA, PK,
    batch, AAA, ecc. - vedi REPLICA_KEYWORDS).

    Match a PAROLA INTERA, non a sottostringa: "ua" deve
    comparire come parola separata, non dentro un'altra parola
    (es. non si attiva per sbaglio su un ipotetico testo che
    contenga "...ua..." come parte di un'altra parola).

    Se trova una corrispondenza, segnala per revisione manuale
    (non scarta in automatico): un match su parola chiave non e'
    prova certa di contraffazione, puo' anche essere un falso
    positivo (es. una descrizione che dice esplicitamente "NOT a
    replica"), quindi serve sempre un occhio umano prima di
    scartare il prodotto.
    """
    text = extract_product_text(product)

    if not text:
        return {
            "passed": True,
            "detected": None,
            "reason": None,
        }

    for keyword in REPLICA_KEYWORDS:
        pattern = r"\b" + re.escape(keyword) + r"\b"

        if re.search(pattern, text):
            return {
                "passed": False,
                "detected": keyword,
                "reason": "counterfeit_risk_keyword_detected",
            }

    return {
        "passed": True,
        "detected": None,
        "reason": None,
    }


# ============================================================
# DATA FRESHNESS
# ============================================================
#
# KicksDB non ha mai esposto, nei dati osservati finora, un
# campo data/timestamp esplicito tra quelli che leggiamo oggi.
# Questo controllo e' quindi scritto in modo completamente
# difensivo: se non trova nessuno dei campi noti, PASSA sempre
# (comportamento identico a oggi, nessuna rottura). Si attiva
# solo se trova un campo data/timestamp e riesce a interpretarlo.
#
# Se scopri il nome esatto del campo che usa KicksDB per la
# data dell'ultima vendita/aggiornamento, aggiungilo qui.

DATE_FIELD_CANDIDATES = (
    "updated_at",
    "last_updated",
    "last_sale_date",
    "last_sale_at",
    "price_updated_at",
)


def _parse_date_value(value):
    """
    Prova a interpretare un valore data in diversi formati
    plausibili (timestamp unix in secondi o millisecondi,
    stringa ISO 8601). Ritorna un datetime (UTC) o None se il
    formato non e' riconosciuto.
    """
    if value is None or value == "":
        return None

    # Timestamp numerico (secondi o millisecondi dall'epoch).
    if isinstance(value, (int, float)):
        try:
            # Se il numero e' troppo grande per essere in
            # secondi (es. > anno ~5138), assumiamo millisecondi.
            if value > 10**11:
                value = value / 1000.0

            return datetime.datetime.fromtimestamp(
                value, tz=datetime.timezone.utc
            )
        except (ValueError, OverflowError, OSError):
            return None

    # Stringa ISO 8601 (es. "2026-10-01" o
    # "2026-10-01T12:00:00Z").
    if isinstance(value, str):
        text = value.strip()

        if text.endswith("Z"):
            text = text[:-1] + "+00:00"

        try:
            parsed = datetime.datetime.fromisoformat(text)

            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=datetime.timezone.utc)

            return parsed
        except ValueError:
            return None

    return None


def check_data_freshness(product, max_age_days=90):
    """
    Se trova un campo data/timestamp riconoscibile e questo e'
    piu' vecchio di max_age_days, segnala per revisione (non
    scarta): un prezzo calcolato su un dato vecchio puo' essere
    fuorviante ma non e' automaticamente sbagliato.

    Nessun campo trovato, o max_age_days=None -> passa sempre.
    """
    if max_age_days is None:
        return {
            "passed": True,
            "detected_date": None,
            "age_days": None,
            "reason": None,
        }

    raw_value = None

    for field in DATE_FIELD_CANDIDATES:
        value = product.get(field)

        if value is not None and value != "":
            raw_value = value
            break

    if raw_value is None:
        return {
            "passed": True,
            "detected_date": None,
            "age_days": None,
            "reason": None,
        }

    parsed = _parse_date_value(raw_value)

    if parsed is None:
        # Campo presente ma formato non riconosciuto: non
        # penalizziamo il prodotto per un problema nostro di
        # parsing, passa comunque.
        return {
            "passed": True,
            "detected_date": raw_value,
            "age_days": None,
            "reason": None,
        }

    now = datetime.datetime.now(tz=datetime.timezone.utc)
    age_days = (now - parsed).total_seconds() / 86400.0

    if age_days > max_age_days:
        return {
            "passed": False,
            "detected_date": parsed.isoformat(),
            "age_days": round(age_days, 1),
            "reason": "stale_data",
        }

    return {
        "passed": True,
        "detected_date": parsed.isoformat(),
        "age_days": round(age_days, 1),
        "reason": None,
    }


# ============================================================
# LIQUIDITY (VOLUME DI MERCATO)
# ============================================================
#
# Stesso approccio difensivo del controllo data: se KicksDB non
# espone un campo volume/numero vendite tra quelli noti, il
# controllo passa sempre (nessuna rottura rispetto a oggi).

SALES_COUNT_FIELD_CANDIDATES = (
    "sales_count",
    "sale_count",
    "number_of_sales",
    "trade_count",
    "volume",
)


def check_liquidity(product, min_sales=1):
    """
    Se trova un campo numero-vendite/volume riconoscibile e il
    valore e' sotto min_sales, segnala per revisione: un prezzo
    medio calcolato su pochissime vendite e' meno affidabile.

    Nessun campo trovato, o min_sales=None -> passa sempre.
    """
    if min_sales is None:
        return {
            "passed": True,
            "sales_count": None,
            "reason": None,
        }

    raw_value = None

    for field in SALES_COUNT_FIELD_CANDIDATES:
        value = product.get(field)

        if value is not None and value != "":
            raw_value = value
            break

    if raw_value is None:
        return {
            "passed": True,
            "sales_count": None,
            "reason": None,
        }

    try:
        sales_count = float(raw_value)
    except (TypeError, ValueError):
        # Valore non numerico: non penalizziamo per un
        # problema di formato, passa comunque.
        return {
            "passed": True,
            "sales_count": raw_value,
            "reason": None,
        }

    if sales_count < min_sales:
        return {
            "passed": False,
            "sales_count": sales_count,
            "reason": "low_liquidity",
        }

    return {
        "passed": True,
        "sales_count": sales_count,
        "reason": None,
    }


# ============================================================
# SIZE PLAUSIBILITY
# ============================================================
#
# Controllo volutamente permissivo: non verifichiamo che la
# taglia sia in un range "giusto" per US/UK/EU (non sappiamo
# con certezza quale sistema usi KicksDB), solo che sia un
# numero plausibile per UNA scarpa in un senso generico (copre
# bambino/adulto in qualunque sistema di taglie comune).
# Serve solo a intercettare errori di parsing a monte
# (es. "3XL" finito per sbaglio nel campo size, o un valore
# chiaramente impazzito tipo 999).

SIZE_FIELD_CANDIDATES = (
    "size",
    "us_size",
    "eu_size",
    "uk_size",
)


def check_size_plausibility(product, min_size=0, max_size=60):
    """
    Se trova un campo taglia riconoscibile e il valore numerico
    e' fuori da [min_size, max_size], segnala per revisione.

    Nessun campo trovato, valore non numerico (es. "M", "One
    Size"), o min_size/max_size=None -> passa sempre: non e'
    compito di questo controllo capire la taglia, solo
    intercettare numeri palesemente impazziti.
    """
    if min_size is None or max_size is None:
        return {
            "passed": True,
            "size": None,
            "reason": None,
        }

    raw_value = None

    for field in SIZE_FIELD_CANDIDATES:
        value = product.get(field)

        if value is not None and value != "":
            raw_value = value
            break

    if raw_value is None:
        return {
            "passed": True,
            "size": None,
            "reason": None,
        }

    try:
        size_value = float(raw_value)
    except (TypeError, ValueError):
        # Non numerico (es. "M", "One Size"): non e' compito
        # di questo controllo, passa comunque.
        return {
            "passed": True,
            "size": raw_value,
            "reason": None,
        }

    if size_value < min_size or size_value > max_size:
        return {
            "passed": False,
            "size": size_value,
            "reason": "implausible_size",
        }

    return {
        "passed": True,
        "size": size_value,
        "reason": None,
    }


# ============================================================
# DATA COMPLETENESS
# ============================================================

def check_data_completeness(product, strict_mode=False):
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

    # In strict_mode richiediamo una completezza dell'80%, altrimenti
    # basta il 50% (invariato: era già una soglia ragionevole).
    required_threshold = 0.8 if strict_mode else 0.5
    passed = completeness >= required_threshold

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
    """
    Soglia di match abbassata a 0.35 (era 0.5): i titoli dei
    marketplace spesso riordinano o abbreviano le parole del
    modello (es. modello "Gel-Kayano 14" / titolo "ASICS Gel
    Kayano 14 Cream Black"), quindi una soglia troppo alta
    scartava prodotti identici solo per differenze di formato.
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

    OPTIONAL_MODEL_TERMS = {
        "retro",
        "high",
        "low",
        "mid",
        "og",
        "se",
        "ls",
        "pe",
        "pf",
        "flyease",
        "premium",
        "remastered",
        "classic",
        "original",
        "edition",
        "men",
        "mens",
        "women",
        "womens",
        "gs",
        "grade",
        "school",
        "junior",
        "toddler",
        "infant",
    }

    model_tokens = [
        token
        for token in model.split()
        if len(token) >= 2 and token not in OPTIONAL_MODEL_TERMS
    ]

    if not model_tokens:
        return {
            "passed": True,
            "model": model,
            "title": title,
            "match_ratio": None,
            "reason": None,
        }

    if model.startswith("jordan "):
        jordan_number_match = re.search(r"\bjordan\s+(\d+)\b", model)
        if jordan_number_match:
            jordan_number = jordan_number_match.group(1)
            jordan_family_present = (
                re.search(rf"\bjordan\s+{re.escape(jordan_number)}\b", title)
                is not None
            )
            if jordan_family_present:
                return {
                    "passed": True,
                    "model": model,
                    "title": title,
                    "match_ratio": 1.0,
                    "reason": None,
                }

    matched_tokens = sum(1 for token in model_tokens if token in title)
    match_ratio = matched_tokens / len(model_tokens)

    # Soglia abbassata a 0.35 (era 0.5).
    if match_ratio >= 0.35:
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
    expected_currency="USD",
    max_age_days=90,
    min_sales=None,
    min_size=0,
    max_size=60,
    strict_mode=False,
):

    collaboration = check_collaboration(product)
    gender = check_gender(product, expected_gender=expected_gender)
    release_year = check_release_year(product, model_history=model_history)
    price_anomaly = check_price_anomaly(product, reference_price=reference_price)
    sku = check_sku(product)
    brand_model = check_brand_model_consistency(product)
    category_product_type = check_category_product_type(product)
    duplicate = check_duplicate(product, seen_identities=seen_identities)
    price_validity = check_price_validity(product)
    currency = check_currency(product, expected_currency=expected_currency)
    counterfeit_risk = check_counterfeit_risk(product)
    data_freshness = check_data_freshness(product, max_age_days=max_age_days)
    liquidity = check_liquidity(product, min_sales=min_sales)
    size_plausibility = check_size_plausibility(
        product, min_size=min_size, max_size=max_size
    )
    completeness = check_data_completeness(product, strict_mode=strict_mode)
    title_model = check_title_model_consistency(product)
    colorway = check_colorway(product, expected_colorway=expected_colorway)
    condition = check_condition(product, expected_condition=expected_condition)

    # ========================================================
    # CHECKS MAP
    # ========================================================
    #
    # "collaboration" resta nella mappa come informazione (true/
    # false sul fatto che sia una collab nota), ma non è più un
    # check che può bloccare l'approvazione: per quello guarda
    # "is_collaboration" nei dettagli, non questo valore.

    checks = {
        "release_year": release_year["passed"],
        "is_collaboration": collaboration["is_collaboration"],
        "gender": gender["passed"],
        "price_anomaly": price_anomaly["passed"],
        "sku": sku["passed"],
        "brand_model": brand_model["passed"],
        "category_product_type": category_product_type["passed"],
        "duplicate": duplicate["passed"],
        "price_validity": price_validity["passed"],
        "currency": currency["passed"],
        "counterfeit_risk": counterfeit_risk["passed"],
        "data_freshness": data_freshness["passed"],
        "liquidity": liquidity["passed"],
        "size_plausibility": size_plausibility["passed"],
        "data_completeness": completeness["passed"],
        "title_model": title_model["passed"],
        "colorway": colorway["passed"],
        "condition": condition["passed"],
    }

    # ========================================================
    # REVIEW REASONS
    # ========================================================
    #
    # FIX PRINCIPALE: "collaboration_detected" è stato RIMOSSO da
    # qui. Prima, ogni prodotto riconosciuto come collaborazione
    # (Travis Scott, Off-White, Dior, ecc.) veniva scartato a
    # prescindere da quanto fossero buoni gli altri dati, perché
    # questo motivo veniva sempre aggiunto quando una collab era
    # rilevata. Una collab è un prodotto legittimo: ora viene solo
    # segnalata come informazione (vedi "is_collaboration" sopra
    # e in "details"), non più usata per rigettare.

    review_reasons = []

    if not gender["passed"]:
        review_reasons.append("gender_mismatch")

    if not release_year["passed"]:
        review_reasons.append(release_year["reason"])

    if not price_anomaly["passed"]:
        review_reasons.append(price_anomaly["reason"])

    if not sku["passed"]:
        review_reasons.append(sku["reason"])

    if not brand_model["passed"]:
        review_reasons.append(brand_model["reason"])

    if not category_product_type["passed"]:
        review_reasons.append(category_product_type["reason"])

    if not duplicate["passed"]:
        review_reasons.append(duplicate["reason"])

    if not price_validity["passed"]:
        review_reasons.append(price_validity["reason"])

    if not currency["passed"]:
        review_reasons.append(currency["reason"])

    if not counterfeit_risk["passed"]:
        review_reasons.append(counterfeit_risk["reason"])

    if not data_freshness["passed"]:
        review_reasons.append(data_freshness["reason"])

    if not liquidity["passed"]:
        review_reasons.append(liquidity["reason"])

    if not size_plausibility["passed"]:
        review_reasons.append(size_plausibility["reason"])

    if not completeness["passed"]:
        review_reasons.append(completeness["reason"])

    if not title_model["passed"]:
        review_reasons.append(title_model["reason"])

    if not colorway["passed"]:
        review_reasons.append(colorway["reason"])

    if not condition["passed"]:
        review_reasons.append(condition["reason"])

    clean_reasons = [reason for reason in review_reasons if reason]
    approved = len(clean_reasons) == 0

    # ========================================================
    # RESULT
    # ========================================================

    return {
        "approved": approved,
        "strict_mode": strict_mode,
        "checks": checks,
        "review_reasons": clean_reasons,
        "details": {
            "collaboration": collaboration,
            "gender": gender,
            "release_year": release_year,
            "price_anomaly": price_anomaly,
            "sku": sku,
            "brand_model": brand_model,
            "category_product_type": category_product_type,
            "duplicate": duplicate,
            "price_validity": price_validity,
            "currency": currency,
            "counterfeit_risk": counterfeit_risk,
            "data_freshness": data_freshness,
            "liquidity": liquidity,
            "size_plausibility": size_plausibility,
            "data_completeness": completeness,
            "title_model": title_model,
            "colorway": colorway,
            "condition": condition,
        },
    }
