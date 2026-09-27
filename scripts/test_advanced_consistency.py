from advanced_consistency import run_advanced_consistency


# ============================================================
# HELPER
# ============================================================

def print_test_result(test_name, result):
    print("\n" + "=" * 60)
    print(test_name)
    print("=" * 60)

    print("\nCHECKS:")

    for name, value in result["checks"].items():
        print(f"  {name}: {value}")

    print("\nREVIEW REASONS:")

    print(f"  {result['review_reasons']}")

    print("\nDETAILS:")

    print(f"  {result['details']}")


# ============================================================
# TEST 1 — NORMAL JORDAN
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
# SUMMARY
# ============================================================

print("\n")
print("=" * 60)
print("ADVANCED CONSISTENCY TEST SUITE COMPLETED")
print("=" * 60)

print("\n12 test case eseguiti.")
print("Controlli verificati:")
print("  1. Release year")
print("  2. Collaboration")
print("  3. Gender / sizing")
print("  4. Price anomaly")
print("  5. SKU consistency")
print("  6. Brand / Model")
print("  7. Category / Product type")
print("  8. Duplicate detection")
print("  9. Price validity")
print(" 10. Data completeness")
print(" 11. Title / Model")
print("\n")
