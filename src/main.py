import os
import sys
import json
import urllib.parse
import urllib.request
import urllib.error
from pathlib import Path

from supabase import create_client


# ============================================================
# IMPORT ADVANCED CONSISTENCY
# ============================================================

# Permette a src/main.py di importare scripts/advanced_consistency.py
ROOT_DIR = Path(__file__).resolve().parents[1]

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from scripts.advanced_consistency import run_advanced_consistency


# ============================================================
# OUTPUT GITHUB ACTIONS
# ============================================================

try:
    sys.stdout.reconfigure(line_buffering=True)
except Exception:
    pass


def log(*args):
    print(*args, flush=True)


# ============================================================
# UTILITY
# ============================================================

def first_value(product, *fields):
    """
    Restituisce il primo campo presente e non vuoto.
    """
    for field in fields:
        value = product.get(field)

        if value is not None and str(value).strip() != "":
            return value

    return None


def safe_float(value):
    """
    Converte un valore in float quando possibile.
    """
    if value is None:
        return None

    try:
        return float(value)
    except (TypeError, ValueError):
        return None


# ============================================================
# COSTRUZIONE PRODOTTO NORMALIZZATO
# ============================================================

def normalize_kicksdb_product(product):
    """
    Trasforma il prodotto KicksDB nel formato utilizzato
    dall'Advanced Consistency Layer.

    Non inventa valori mancanti.
    """

    normalized = {
        # Identificazione principale
        "title": first_value(
            product,
            "title",
            "name",
        ),

        "brand": first_value(
            product,
            "brand",
        ),

        "model": first_value(
            product,
            "model",
        ),

        "sku": first_value(
            product,
            "sku",
            "style_id",
            "styleId",
        ),

        # Prezzo
        "avg_price": first_value(
            product,
            "avg_price",
            "price",
        ),

        # Categoria
        "category": first_value(
            product,
            "category",
        ),

        "product_type": first_value(
            product,
            "product_type",
            "productType",
        ),

        # Colorway
        "colorway": first_value(
            product,
            "colorway",
            "color",
        ),

        # Condizione
        "condition": first_value(
            product,
            "condition",
        ),

        # Titoli/descriptions aggiuntivi
        "primary_title": first_value(
            product,
            "primary_title",
        ),

        "secondary_title": first_value(
            product,
            "secondary_title",
        ),

        "description": first_value(
            product,
            "description",
        ),

        # Anno
        "release_year": first_value(
            product,
            "release_year",
            "releaseYear",
        ),
    }

    # Manteniamo anche tutti i dati originali KicksDB.
    # In questo modo non perdiamo informazioni eventualmente
    # utili in futuro.
    normalized["_raw_kicksdb"] = product

    return normalized


# ============================================================
# REFERENCE PRICE
# ============================================================

def get_reference_price(supabase, product_id):
    """
    Calcola il prezzo medio storico del prodotto.

    Se non esiste uno storico sufficiente, restituisce None.
    In quel caso il controllo price_anomaly passa senza
    inventare una reference price.
    """

    if not product_id:
        return None

    try:
        history = (
            supabase
            .table("price_history")
            .select("price")
            .eq("product_id", product_id)
            .execute()
        )

        rows = history.data or []

        prices = []

        for row in rows:
            price = safe_float(row.get("price"))

            if price is not None and price > 0:
                prices.append(price)

        if not prices:
            return None

        return sum(prices) / len(prices)

    except Exception as e:
        log("⚠️ Impossibile recuperare il prezzo storico:", e)
        return None


# ============================================================
# ADVANCED CONSISTENCY CONFIG
# ============================================================

EXPECTED_GENDER = os.environ.get(
    "EXPECTED_GENDER"
)

EXPECTED_COLORWAY = os.environ.get(
    "EXPECTED_COLORWAY"
)

EXPECTED_CONDITION = os.environ.get(
    "EXPECTED_CONDITION"
)


def get_model_history():
    """
    Recupera opzionalmente la storia del modello.

    Per ora non inventiamo anni di origine.
    Se in futuro vorremo usare il controllo release_year
    in modo automatico, possiamo alimentarlo con un database
    dedicato.
    """

    return None


# ============================================================
# KICKSDB
# ============================================================

def fetch_kicksdb_products():
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
        with urllib.request.urlopen(
            request,
            timeout=30
        ) as response:

            data = json.loads(
                response.read().decode()
            )

    except urllib.error.HTTPError as e:
        log("❌ KicksDB error:", e.code)
        log("Headers:", dict(e.headers))

        try:
            body = e.read().decode()
            log("Body:", body)
        except Exception:
            pass

        raise

    except urllib.error.URLError as e:
        log("❌ KicksDB connection error:", e)
        raise

    log("🔥 KicksDB connected!")

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

    return products


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
    # CONFIGURAZIONE
    # ========================================================

    log("")
    log("============================================================")
    log("🛡️ ADVANCED CONSISTENCY LAYER")
    log("============================================================")

    log(
        "Expected gender:",
        EXPECTED_GENDER or "NONE"
    )

    log(
        "Expected colorway:",
        EXPECTED_COLORWAY or "NONE"
    )

    log(
        "Expected condition:",
        EXPECTED_CONDITION or "NONE"
    )

    log("============================================================")
    log("")

    # ========================================================
    # FETCH KICKSDB
    # ========================================================

    products = fetch_kicksdb_products()

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
    # DUPLICATE TRACKING
    # ========================================================

    seen_identities = set()

    # ========================================================
    # PROCESS PRODUCTS
    # ========================================================

    for index, raw_product in enumerate(
        products,
        start=1
    ):

        log("")
        log(
            "============================================================"
        )
        log(
            f"👟 PRODUCT {index}/{len(products)}"
        )
        log(
            "============================================================"
        )

        # ----------------------------------------------------
        # NORMALIZE
        # ----------------------------------------------------

        product = normalize_kicksdb_product(
            raw_product
        )

        title = product.get("title")
        sku = product.get("sku")
        price = product.get("avg_price")
        brand = product.get("brand")

        log("Title:", title)
        log("Brand:", brand)
        log("SKU:", sku)
        log("Price:", price)

        # ----------------------------------------------------
        # BASIC VALIDATION
        # ----------------------------------------------------

        if not sku:

            log(
                "⚠️ Product has no SKU."
            )

        # ----------------------------------------------------
        # FIND EXISTING PRODUCT
        # ----------------------------------------------------

        product_id = None

        if sku:

            existing = (
                supabase
                .table("products")
                .select("id")
                .eq("sku", sku)
                .execute()
            )

            if existing.data:

                product_id = (
                    existing.data[0]["id"]
                )

                log(
                    f"🔎 Found existing product "
                    f"with id {product_id}"
                )

            else:

                log(
                    "🆕 Product not found in database."
                )

        # ----------------------------------------------------
        # REFERENCE PRICE
        # ----------------------------------------------------

        reference_price = None

        if product_id:

            reference_price = (
                get_reference_price(
                    supabase,
                    product_id
                )
            )

        if reference_price is not None:

            log(
                "📊 Historical reference price:",
                round(reference_price, 2)
            )

        else:

            log(
                "📊 Historical reference price: NONE"
            )

        # ----------------------------------------------------
        # MODEL HISTORY
        # ----------------------------------------------------

        model_history = get_model_history()

        # ----------------------------------------------------
        # ADVANCED CONSISTENCY
        # ----------------------------------------------------

        log("")
        log(
            "🛡️ Running Advanced Consistency..."
        )

        consistency = run_advanced_consistency(
            product,

            expected_gender=EXPECTED_GENDER,

            model_history=model_history,

            reference_price=reference_price,

            seen_identities=seen_identities,

            expected_colorway=EXPECTED_COLORWAY,

            expected_condition=EXPECTED_CONDITION,
        )

        checks = consistency.get(
            "checks",
            {}
        )

        review_reasons = consistency.get(
            "review_reasons",
            []
        )

        details = consistency.get(
            "details",
            {}
        )

        # ----------------------------------------------------
        # STATUS
        # ----------------------------------------------------

        all_checks_passed = all(
            checks.values()
        )

        if all_checks_passed:

            consistency_status = "VALID"

        else:

            consistency_status = "REVIEW"

        log("")
        log(
            "🧠 CONSISTENCY RESULT:",
            consistency_status
        )

        log("")
        log("CHECKS:")

        for check_name, passed in checks.items():

            icon = "✅" if passed else "❌"

            log(
                f"  {icon} {check_name}: {passed}"
            )

        log("")

        if review_reasons:

            log(
                "⚠️ REVIEW REASONS:"
            )

            for reason in review_reasons:

                log(
                    f"  - {reason}"
                )

        else:

            log(
                "✅ REVIEW REASONS: []"
            )

        log("")

        log("DETAILS:")

        log(
            json.dumps(
                details,
                indent=2,
                ensure_ascii=False
            )
        )

        # ----------------------------------------------------
        # REGISTER IDENTITY FOR DUPLICATE CHECK
        # ----------------------------------------------------

        identity_details = details.get(
            "duplicate",
            {}
        )

        identity = identity_details.get(
            "identity"
        )

        if identity:

            seen_identities.add(
                identity
            )

        # ----------------------------------------------------
        # SAVE PRODUCT
        # ----------------------------------------------------

        if product_id:

            log(
                "💾 Product already exists."
            )

        else:

            if not sku:

                log(
                    "⚠️ No SKU available."
                )

                log(
                    "⏭️ Product will NOT be inserted "
                    "because the current database "
                    "logic requires SKU."
                )

                log("---")

                continue

            log(
                "💾 Saving product..."
            )

            insert_payload = {
                "title": title,
                "brand": brand,
                "sku": sku,
                "source": "kicksdb",
            }

            inserted_product = (
                supabase
                .table("products")
                .insert(insert_payload)
                .execute()
            )

            if not inserted_product.data:

                raise RuntimeError(
                    "❌ Product insertion failed."
                )

            product_id = (
                inserted_product
                .data[0]
                .get("id")
            )

            if not product_id:

                # Fallback: recupera ID tramite SKU
                inserted = (
                    supabase
                    .table("products")
                    .select("id")
                    .eq("sku", sku)
                    .execute()
                )

                if not inserted.data:

                    raise RuntimeError(
                        "❌ Product was inserted "
                        "but its ID could not be found."
                    )

                product_id = (
                    inserted.data[0]["id"]
                )

            log(
                "✅ Product saved to Supabase "
                f"with id {product_id}"
            )

        # ----------------------------------------------------
        # PRICE HISTORY
        # ----------------------------------------------------

        numeric_price = safe_float(
            price
        )

        if (
            product_id
            and numeric_price is not None
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
                "⚠️ Price is 0 or missing, "
                "so it was not saved."
            )

        # ----------------------------------------------------
        # FINAL PRODUCT STATUS
        # ----------------------------------------------------

        log("")
        log(
            "🏁 FINAL STATUS:",
            consistency_status
        )

        if consistency_status == "REVIEW":

            log(
                "⚠️ Product requires review."
            )

        else:

            log(
                "✅ Product passed "
                "Advanced Consistency."
            )

        log("---")

    # ========================================================
    # END
    # ========================================================

    log("")
    log(
        "============================================================"
    )
    log(
        "✅ PIPELINE COMPLETED"
    )
    log(
        "============================================================"
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()
