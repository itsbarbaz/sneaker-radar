from advanced_consistency import run_advanced_consistency


# ============================================================
# HELPER
# ============================================================

def print_test_result(test_name, result):
    print("\n" + "=" * 70)
    print(test_name)
    print("=" * 70)

    print("\nCHECKS:")

    for name, value in result["checks"].items():
        print(f"  {name}: {value}")

    print("\nREVIEW REASONS:")
    print(f"  {result['review_reasons']}")

    print("\nDETAILS:")
    print(f"  {result['details']}")


# ============================================================
# TEST 1 — NORMAL JORDAN 1
# ============================================================

product_1 = {
    "id": "test-001",
    "brand": "Jordan",
    "model": "Jordan 1 Retro High",
    "title": "Air Jordan 1 Retro High",
    "primary_title": "Air Jordan 1 Retro High",
    "sku": "555088-161",
    "product_type": "sneakers",
    "category": "sneakers",
    "avg_price": 180,
}

result_1 = run_advanced_consistency(
    product_1,
    expected_gender="MEN",
    reference_price=180,
)

print_test_result(
    "TEST 1 — Normal Jordan 1",
    result_1,
)


# ============================================================
# TEST 2 — TRAVIS SCOTT
# ============================================================

product_2 = {
    "id": "test-002",
    "brand": "Jordan",
    "model": "Jordan 1 Retro High",
    "title": "Travis Scott x Air Jordan 1 Retro High",
    "primary_title": "Travis Scott Jordan 1",
    "sku": "555088-001",
    "product_type": "sneakers",
    "category": "sneakers",
    "avg_price": 900,
}

result_2 = run_advanced_consistency(
    product_2,
    expected_gender="MEN",
    reference_price=180,
)

print_test_result(
    "TEST 2 — Travis Scott Jordan 1",
    result_2,
)


# ============================================================
# TEST 3 — GS
# ============================================================

product_3 = {
    "id": "test-003",
    "brand": "Jordan",
    "model": "Jordan 1 Retro High",
    "title": "Air Jordan 1 Retro High GS",
    "primary_title": "Air Jordan 1 GS",
    "sku": "575441-161",
    "product_type": "sneakers",
    "category": "sneakers",
    "avg_price": 120,
}

result_3 = run_advanced_consistency(
    product_3,
    expected_gender="MEN",
    reference_price=180,
)

print_test_result(
    "TEST 3 — GS Jordan 1",
    result_3,
)


# ============================================================
# TEST 4 — EXTREME PRICE ANOMALY
# ============================================================

product_4 = {
    "id": "test-004",
    "brand": "Jordan",
    "model": "Jordan 1 Retro High",
    "title": "Air Jordan 1 Retro High",
    "primary_title": "Air Jordan 1 Retro High",
    "sku": "555088-161",
    "product_type": "sneakers",
    "category": "sneakers",
    "avg_price": 52000,
}

result_4 = run_advanced_consistency(
    product_4,
    expected_gender="MEN",
    reference_price=180,
)

print_test_result(
    "TEST 4 — Extreme price anomaly",
    result_4,
)


# ============================================================
# TEST 5 — IMPOSSIBLE RELEASE YEAR
# ============================================================

product_5 = {
    "id": "test-005",
    "brand": "Jordan",
    "model": "Jordan 4",
    "title": "Air Jordan 4 Retro",
    "primary_title": "Air Jordan 4 Retro",
    "sku": "555088-161",
    "product_type": "sneakers",
    "category": "sneakers",
    "release_year": 1975,
    "avg_price": 250,
}

result_5 = run_advanced_consistency(
    product_5,
    expected_gender="MEN",
    model_history={
        "first_known_year": 1989,
    },
    reference_price=250,
)

print_test_result(
    "TEST 5 — Impossible release year",
    result_5,
)


# ============================================================
# TEST 6 — MISSING SKU
# ============================================================

product_6 = {
    "id": "test-006",
    "brand": "Jordan",
    "model": "Jordan 4",
    "title": "Air Jordan 4 Retro",
    "primary_title": "Air Jordan 4 Retro",
    "sku": "",
    "product_type": "sneakers",
    "category": "sneakers",
    "avg_price": 200,
}

result_6 = run_advanced_consistency(
    product_6,
    expected_gender="MEN",
    reference_price=200,
)

print_test_result(
    "TEST 6 — Missing SKU",
    result_6,
)


# ============================================================
# TEST 7 — BRAND / MODEL INCONSISTENCY
# ============================================================

product_7 = {
    "id": "test-007",
    "brand": "Adidas",
    "model": "Jordan 4",
    "title": "Air Jordan 4 Retro",
    "primary_title": "Air Jordan 4 Retro",
    "sku": "123456",
    "product_type": "sneakers",
    "category": "sneakers",
    "avg_price": 200,
}

result_7 = run_advanced_consistency(
    product_7,
    expected_gender="MEN",
    reference_price=200,
)

print_test_result(
    "TEST 7 — Brand / Model inconsistency",
    result_7,
)


# ============================================================
# TEST 8 — CATEGORY / PRODUCT TYPE MISMATCH
# ============================================================

product_8 = {
    "id": "test-008",
    "brand": "Nike",
    "model": "Air Jordan 1",
    "title": "Air Jordan 1 Retro",
    "primary_title": "Air Jordan 1 Retro",
    "sku": "555088-161",
    "product_type": "socks",
    "category": "sneakers",
    "avg_price": 30,
}

result_8 = run_advanced_consistency(
    product_8,
    expected_gender="MEN",
    reference_price=30,
)

print_test_result(
    "TEST 8 — Category / Product type mismatch",
    result_8,
)


# ============================================================
# TEST 9 — DUPLICATE
# ============================================================

product_9 = {
    "id": "test-009",
    "brand": "Jordan",
    "model": "Jordan 4",
    "title": "Air Jordan 4 Retro",
    "primary_title": "Air Jordan 4 Retro",
    "sku": "555088-161",
    "product_type": "sneakers",
    "category": "sneakers",
    "avg_price": 200,
}

seen_identities_9 = {
    "sku:555088-161"
}

result_9 = run_advanced_consistency(
    product_9,
    expected_gender="MEN",
    reference_price=200,
    seen_identities=seen_identities_9,
)

print_test_result(
    "TEST 9 — Duplicate product",
    result_9,
)


# ============================================================
# TEST 10 — INVALID PRICE
# ============================================================

product_10 = {
    "id": "test-010",
    "brand": "Jordan",
    "model": "Jordan 4",
    "title": "Air Jordan 4 Retro",
    "primary_title": "Air Jordan 4 Retro",
    "sku": "555088-161",
    "product_type": "sneakers",
    "category": "sneakers",
    "avg_price": 0,
}

result_10 = run_advanced_consistency(
    product_10,
    expected_gender="MEN",
    reference_price=200,
)

print_test_result(
    "TEST 10 — Invalid price",
    result_10,
)


# ============================================================
# TEST 11 — INCOMPLETE DATA
# ============================================================

product_11 = {
    "id": "test-011",
    "brand": "Jordan",
    "title": "Air Jordan 4 Retro",
    "avg_price": 200,
}

result_11 = run_advanced_consistency(
    product_11,
    expected_gender="MEN",
    reference_price=200,
)

print_test_result(
    "TEST 11 — Incomplete data",
    result_11,
)


# ============================================================
# TEST 12 — TITLE / MODEL INCONSISTENCY
# ============================================================

product_12 = {
    "id": "test-012",
    "brand": "Nike",
    "model": "Jordan 4",
    "title": "Nike Air Max 97",
    "primary_title": "Nike Air Max 97",
    "sku": "123456",
    "product_type": "sneakers",
    "category": "sneakers",
    "avg_price": 180,
}

result_12 = run_advanced_consistency(
    product_12,
    expected_gender="MEN",
    reference_price=180,
)

print_test_result(
    "TEST 12 — Title / Model inconsistency",
    result_12,
)


# ============================================================
# TEST 13 — CORRECT COLORWAY
# ============================================================

product_13 = {
    "id": "test-013",
    "brand": "Jordan",
    "model": "Jordan 1 Retro High",
    "title": "Air Jordan 1 Retro High Chicago",
    "primary_title": "Air Jordan 1 Chicago",
    "sku": "555088-161",
    "colorway": "Chicago",
    "product_type": "sneakers",
    "category": "sneakers",
    "avg_price": 300,
}

result_13 = run_advanced_consistency(
    product_13,
    expected_gender="MEN",
    expected_colorway="Chicago",
    reference_price=300,
)

print_test_result(
    "TEST 13 — Correct colorway",
    result_13,
)


# ============================================================
# TEST 14 — COLORWAY MISMATCH
# ============================================================

product_14 = {
    "id": "test-014",
    "brand": "Jordan",
    "model": "Jordan 1 Retro High",
    "title": "Air Jordan 1 Retro High Bred",
    "primary_title": "Air Jordan 1 Bred",
    "sku": "555088-001",
    "colorway": "Bred",
    "product_type": "sneakers",
    "category": "sneakers",
    "avg_price": 300,
}

result_14 = run_advanced_consistency(
    product_14,
    expected_gender="MEN",
    expected_colorway="Chicago",
    reference_price=300,
)

print_test_result(
    "TEST 14 — Colorway mismatch",
    result_14,
)


# ============================================================
# TEST 15 — MISSING COLORWAY
# ============================================================

product_15 = {
    "id": "test-015",
    "brand": "Jordan",
    "model": "Jordan 1 Retro High",
    "title": "Air Jordan 1 Retro High",
    "primary_title": "Air Jordan 1 Retro High",
    "sku": "555088-161",
    "product_type": "sneakers",
    "category": "sneakers",
    "avg_price": 250,
}

result_15 = run_advanced_consistency(
    product_15,
    expected_gender="MEN",
    expected_colorway="Chicago",
    reference_price=250,
)

print_test_result(
    "TEST 15 — Missing colorway",
    result_15,
)


# ============================================================
# TEST 16 — NEW / DEADSTOCK
# ============================================================

product_16 = {
    "id": "test-016",
    "brand": "Jordan",
    "model": "Jordan 1 Retro High",
    "title": "Air Jordan 1 Chicago",
    "primary_title": "Air Jordan 1 Chicago",
    "sku": "555088-161",
    "colorway": "Chicago",
    "condition": "Deadstock",
    "product_type": "sneakers",
    "category": "sneakers",
    "avg_price": 400,
}

result_16 = run_advanced_consistency(
    product_16,
    expected_gender="MEN",
    expected_colorway="Chicago",
    expected_condition="NEW",
    reference_price=400,
)

print_test_result(
    "TEST 16 — Deadstock / New",
    result_16,
)


# ============================================================
# TEST 17 — USED
# ============================================================

product_17 = {
    "id": "test-017",
    "brand": "Jordan",
    "model": "Jordan 1 Retro High",
    "title": "Air Jordan 1 Chicago Used",
    "primary_title": "Air Jordan 1 Chicago",
    "sku": "555088-161",
    "colorway": "Chicago",
    "condition": "Used",
    "product_type": "sneakers",
    "category": "sneakers",
    "avg_price": 220,
}

result_17 = run_advanced_consistency(
    product_17,
    expected_gender="MEN",
    expected_colorway="Chicago",
    expected_condition="USED",
    reference_price=220,
)

print_test_result(
    "TEST 17 — Used",
    result_17,
)


# ============================================================
# TEST 18 — CONDITION MISMATCH
# ============================================================

product_18 = {
    "id": "test-018",
    "brand": "Jordan",
    "model": "Jordan 1 Retro High",
    "title": "Air Jordan 1 Chicago Used",
    "primary_title": "Air Jordan 1 Chicago",
    "sku": "555088-161",
    "colorway": "Chicago",
    "condition": "Used",
    "product_type": "sneakers",
    "category": "sneakers",
    "avg_price": 220,
}

result_18 = run_advanced_consistency(
    product_18,
    expected_gender="MEN",
    expected_colorway="Chicago",
    expected_condition="NEW",
    reference_price=400,
)

print_test_result(
    "TEST 18 — Condition mismatch",
    result_18,
)


# ============================================================
# TEST 19 — COLORWAY + CONDITION COMBINED
# ============================================================

product_19 = {
    "id": "test-019",
    "brand": "Jordan",
    "model": "Jordan 1 Retro High",
    "title": "Air Jordan 1 Chicago",
    "primary_title": "Air Jordan 1 Chicago",
    "sku": "555088-161",
    "colorway": "Chicago",
    "condition": "New",
    "product_type": "sneakers",
    "category": "sneakers",
    "avg_price": 350,
}

result_19 = run_advanced_consistency(
    product_19,
    expected_gender="MEN",
    expected_colorway="Chicago",
    expected_condition="NEW",
    reference_price=350,
)

print_test_result(
    "TEST 19 — Colorway + Condition combined",
    result_19,
)


# ============================================================
# TEST 20 — WRONG COLORWAY + WRONG CONDITION
# ============================================================

product_20 = {
    "id": "test-020",
    "brand": "Jordan",
    "model": "Jordan 1 Retro High",
    "title": "Air Jordan 1 Bred Used",
    "primary_title": "Air Jordan 1 Bred",
    "sku": "555088-001",
    "colorway": "Bred",
    "condition": "Used",
    "product_type": "sneakers",
    "category": "sneakers",
    "avg_price": 180,
}

result_20 = run_advanced_consistency(
    product_20,
    expected_gender="MEN",
    expected_colorway="Chicago",
    expected_condition="NEW",
    reference_price=350,
)

print_test_result(
    "TEST 20 — Wrong colorway + wrong condition",
    result_20,
)


# ============================================================
# TEST 21 — COUNTERFEIT KEYWORD (UA BATCH)
# ============================================================

product_21 = {
    "id": "test-021",
    "brand": "Jordan",
    "model": "Jordan 1 Retro High",
    "title": "Air Jordan 1 Retro High UA Batch",
    "sku": "555088-161",
    "product_type": "sneakers",
    "category": "sneakers",
    "avg_price": 120,
}

result_21 = run_advanced_consistency(
    product_21,
    reference_price=180,
)

print_test_result(
    "TEST 21 — Counterfeit keyword (UA Batch)",
    result_21,
)


# ============================================================
# TEST 22 — CLEAN PRODUCT, NO COUNTERFEIT RISK
# ============================================================

product_22 = {
    "id": "test-022",
    "brand": "Jordan",
    "model": "Jordan 1 Retro High",
    "title": "Air Jordan 1 Retro High Guava Ice",
    "sku": "555088-161",
    "product_type": "sneakers",
    "category": "sneakers",
    "avg_price": 180,
}

result_22 = run_advanced_consistency(
    product_22,
    reference_price=180,
)

print_test_result(
    "TEST 22 — Clean product, no counterfeit risk "
    "(regression: 'Guava' must not false-positive on 'UA')",
    result_22,
)


# ============================================================
# TEST 23 — STALE DATA (OLD UPDATED_AT)
# ============================================================

product_23 = {
    "id": "test-023",
    "brand": "Jordan",
    "model": "Jordan 4",
    "title": "Air Jordan 4 Retro",
    "sku": "555088-161",
    "product_type": "sneakers",
    "category": "sneakers",
    "avg_price": 250,
    "updated_at": "2025-01-01T00:00:00Z",
}

result_23 = run_advanced_consistency(
    product_23,
    reference_price=250,
)

print_test_result(
    "TEST 23 — Stale data (old updated_at)",
    result_23,
)


# ============================================================
# TEST 24 — FRESH DATA (RECENT UPDATED_AT)
# ============================================================

product_24 = {
    "id": "test-024",
    "brand": "Jordan",
    "model": "Jordan 4",
    "title": "Air Jordan 4 Retro",
    "sku": "555088-161",
    "product_type": "sneakers",
    "category": "sneakers",
    "avg_price": 250,
    "updated_at": "2026-10-09T00:00:00Z",
}

result_24 = run_advanced_consistency(
    product_24,
    reference_price=250,
)

print_test_result(
    "TEST 24 — Fresh data (recent updated_at)",
    result_24,
)


# ============================================================
# TEST 25 — LOW LIQUIDITY (min_sales ENABLED EXPLICITLY)
# ============================================================

product_25 = {
    "id": "test-025",
    "brand": "Jordan",
    "model": "Jordan 4",
    "title": "Air Jordan 4 Retro",
    "sku": "555088-161",
    "product_type": "sneakers",
    "category": "sneakers",
    "avg_price": 250,
    "sales_count": 0,
}

result_25 = run_advanced_consistency(
    product_25,
    reference_price=250,
    min_sales=1,
)

print_test_result(
    "TEST 25 — Low liquidity (min_sales=1 enabled explicitly)",
    result_25,
)


# ============================================================
# TEST 26 — LIQUIDITY FIELD ABSENT (DEFAULT: DISABLED)
# ============================================================

product_26 = {
    "id": "test-026",
    "brand": "Jordan",
    "model": "Jordan 4",
    "title": "Air Jordan 4 Retro",
    "sku": "555088-161",
    "product_type": "sneakers",
    "category": "sneakers",
    "avg_price": 250,
}

result_26 = run_advanced_consistency(
    product_26,
    reference_price=250,
)

print_test_result(
    "TEST 26 — No sales_count field "
    "(liquidity check disabled by default: must pass)",
    result_26,
)


# ============================================================
# TEST 27 — IMPLAUSIBLE SIZE
# ============================================================

product_27 = {
    "id": "test-027",
    "brand": "Jordan",
    "model": "Jordan 4",
    "title": "Air Jordan 4 Retro",
    "sku": "555088-161",
    "product_type": "sneakers",
    "category": "sneakers",
    "avg_price": 250,
    "size": 999,
}

result_27 = run_advanced_consistency(
    product_27,
    reference_price=250,
)

print_test_result(
    "TEST 27 — Implausible size (999)",
    result_27,
)


# ============================================================
# TEST 28 — PLAUSIBLE SIZE
# ============================================================

product_28 = {
    "id": "test-028",
    "brand": "Jordan",
    "model": "Jordan 4",
    "title": "Air Jordan 4 Retro",
    "sku": "555088-161",
    "product_type": "sneakers",
    "category": "sneakers",
    "avg_price": 250,
    "size": 9.5,
}

result_28 = run_advanced_consistency(
    product_28,
    reference_price=250,
)

print_test_result(
    "TEST 28 — Plausible size (9.5)",
    result_28,
)


# ============================================================
# ASSERTIONS (FANNO FALLIRE LA CI SE UN RISULTATO E' SBAGLIATO)
# ============================================================
#
# I test sopra stampano soltanto: la CI risultava verde anche con
# un risultato sbagliato, purche' lo script non andasse in errore.
# Qui ogni controllo confronta il risultato con quello atteso e,
# se anche uno solo non combacia, lo script termina con codice 1.

import sys

from advanced_consistency import (
    check_brand_model_consistency,
    check_collaboration,
)

assertion_failures = []
assertion_count = 0


def expect(label, actual, expected):
    global assertion_count
    assertion_count += 1

    if actual != expected:
        assertion_failures.append(
            f"{label}: ottenuto {actual!r}, atteso {expected!r}"
        )


def brand_ok(brand, model, title=""):
    return check_brand_model_consistency(
        {"brand": brand, "model": model, "title": title}
    )["passed"]


def is_collab(title):
    return check_collaboration({"title": title})["is_collaboration"]


def full_run(**overrides):
    product = {
        "brand": "Jordan",
        "model": "Jordan 1 Retro High",
        "title": "Air Jordan 1 Retro High",
        "sku": "555088-161",
        "product_type": "sneakers",
        "category": "sneakers",
        "avg_price": 180,
    }
    product.update(overrides)
    return run_advanced_consistency(product, reference_price=180)


# --- brand / modello: Jordan non e' piu' un caso senza regole ---
expect("Jordan + adidas Samba", brand_ok("Jordan", "adidas Samba"), False)
expect("Jordan + Jordan 1", brand_ok("Jordan", "Jordan 1 Retro High"), True)
expect("Nike + Jordan 4", brand_ok("Nike", "Jordan 4 Retro"), True)
expect("Nike + adidas Samba", brand_ok("Nike", "adidas Samba"), False)

# --- brand "On": il token "on" non deve combaciare dentro altre parole ---
expect("On + Hoka Clifton", brand_ok("On", "Hoka Clifton 9"), False)
expect("On + Vans Slip On", brand_ok("On", "Vans Slip On"), False)
expect("On + On Running Cloud X", brand_ok("On", "On Running Cloud X 4"), True)
expect("On + Cloudmonster", brand_ok("On", "On Cloudmonster 2"), True)

# --- altri brand: nessun falso scarto introdotto ---
expect("Hoka One One alias", brand_ok("Hoka One One", "Hoka One One Clifton 9"), True)
expect("Hoka senza brand nel modello", brand_ok("Hoka", "Bondi B3LS"), True)
expect("NB 990v5", brand_ok("New Balance", "990v5"), True)
expect("ASICS Gel-Kayano", brand_ok("ASICS", "Gel-Kayano 14"), True)
expect("ASICS vs Gelato", brand_ok("ASICS", "Gelato Runner"), False)
expect("Salomon XT-6", brand_ok("Salomon", "Salomon XT-6"), True)
expect("Salomon vs Nike", brand_ok("Salomon", "Nike Dunk Low"), False)

# --- collab: "union" solo come parola intera ---
expect("Reunion non e' collab", is_collab("Nike Dunk Low Reunion Pack"), False)
expect("Communion non e' collab", is_collab("Air Jordan 1 Communion Edition"), False)
expect("Union LA e' collab", is_collab("Nike Union LA Dunk"), True)
expect("Travis Scott e' collab", is_collab("Travis Scott x Air Jordan 1"), True)
expect("Off-White e' collab", is_collab("Off-White x Nike Dunk"), True)
expect("Panda non e' collab", is_collab("Nike Dunk Low Panda"), False)

# --- comportamento complessivo che non deve regredire ---
clean = full_run()
expect("prodotto pulito approvato", clean["approved"], True)

travis = full_run(
    title="Travis Scott x Air Jordan 1 Retro High",
    avg_price=900,
)
expect("Travis Scott approvato", travis["approved"], True)
expect("Travis Scott riconosciuto come collab", travis["checks"]["is_collaboration"], True)

expect("SKU mancante segnalato",
       "missing_sku" in full_run(sku="")["review_reasons"], True)
expect("prezzo anomalo segnalato",
       "price_anomaly" in full_run(avg_price=52000)["review_reasons"], True)
expect("prezzo zero segnalato",
       "non_positive_price" in full_run(avg_price=0)["review_reasons"], True)
expect("replica UA batch segnalata",
       "counterfeit_risk_keyword_detected"
       in full_run(title="Air Jordan 1 Retro High UA Batch")["review_reasons"], True)
expect("Guava non e' replica",
       "counterfeit_risk_keyword_detected"
       in full_run(title="Air Jordan 1 Retro High Guava Ice")["review_reasons"], False)
expect("Jordan con modello adidas segnalato",
       "brand_model_inconsistency"
       in full_run(model="adidas Samba", title="adidas Samba OG")["review_reasons"], True)

# --- DATI REALI KicksDB (scripts/fixtures/kicksdb_real_sample.json) ---
# I test sopra usano prodotti inventati: avevano category="sneakers",
# ma nei dati veri `category` e' un'etichetta di brand ("Air Jordan",
# "Other Brands") e 22 sneaker su 24 venivano segnalate per errore.
# Qui l'atteso e' calcolato da regole semplici e indipendenti dal
# modulo: e' una scarpa, ha SKU e prezzo > 0 -> deve essere approvata.

import json
import os

fixture_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "fixtures",
    "kicksdb_real_sample.json",
)

with open(fixture_path, encoding="utf-8") as fixture_file:
    real_products = json.load(fixture_file)["products"]

expect("campione reale: numero prodotti", len(real_products), 24)

for real in real_products:
    # max_age_days=None: le date del campione invecchiano, il
    # controllo freschezza e' provato a parte qui sotto.
    outcome = run_advanced_consistency(real, max_age_days=None)
    reasons = outcome["review_reasons"]
    name = real["title"][:45]

    is_shoe = real["product_type"] == "sneakers"
    has_sku = bool(str(real.get("sku") or "").strip())
    has_price = (real.get("avg_price") or 0) > 0

    expect(f"reale/{name}: category mismatch falso",
           "category_product_type_mismatch" in reasons, False)
    expect(f"reale/{name}: not_footwear",
           "not_footwear" in reasons, not is_shoe)
    expect(f"reale/{name}: approvato",
           outcome["approved"], is_shoe and has_sku and has_price)

expect("reale: gender dal campo (kids -> GS)",
       run_advanced_consistency(real_products[0])["details"]["gender"]["detected"],
       "GS")

from advanced_consistency import check_data_freshness

real_date = check_data_freshness({"updated_at": "2026-10-05T00:42:37.72832134Z"})
expect("data reale con 8 cifre frazionarie interpretata",
       real_date["age_days"] is not None, True)

expect("weekly_orders letto come campo liquidita",
       run_advanced_consistency(
           {"weekly_orders": 0, "sku": "X-1", "avg_price": 100,
            "product_type": "sneakers", "categories": ["sneakers"],
            "title": "t", "brand": "b", "model": "m"},
           min_sales=1,
       )["checks"]["liquidity"],
       False)

print("\n" + "=" * 70)
print("ASSERTIONS")
print("=" * 70)

if assertion_failures:
    print(f"\nFALLITE {len(assertion_failures)} su {assertion_count}:")
    for failure in assertion_failures:
        print(f"  - {failure}")
    sys.exit(1)

print(f"\nTutte le {assertion_count} assertion sono passate.")


# ============================================================
# SUMMARY
# ============================================================

print("\n")
print("=" * 70)
print("ADVANCED CONSISTENCY TEST SUITE COMPLETED")
print("=" * 70)

print("\n28 test case eseguiti, piu' le assertion.")

print("\nCONTROLLI VERIFICATI:")

print("  1.  Release year")
print("  2.  Collaboration")
print("  3.  Gender / sizing")
print("  4.  Price anomaly")
print("  5.  SKU")
print("  6.  Brand / Model")
print("  7.  Category / Product type")
print("  8.  Duplicate")
print("  9.  Price validity")
print(" 10.  Data completeness")
print(" 11.  Title / Model")
print(" 12.  Colorway")
print(" 13.  Condition")

print("\nNUOVI TEST:")

print("  13. Correct colorway")
print("  14. Colorway mismatch")
print("  15. Missing colorway")
print("  16. Deadstock / New")
print("  17. Used")
print("  18. Condition mismatch")
print("  19. Colorway + Condition combined")
print("  20. Wrong colorway + wrong condition")

print("\nFILTRI AGGIUNTIVI (currency, counterfeit, freshness, "
      "liquidity, size):")

print("  21. Counterfeit keyword (UA Batch)")
print("  22. Clean product, no counterfeit risk")
print("  23. Stale data")
print("  24. Fresh data")
print("  25. Low liquidity (enabled explicitly)")
print("  26. No sales_count field (liquidity disabled by default)")
print("  27. Implausible size")
print("  28. Plausible size")

print("\n")
