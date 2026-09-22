from advanced_consistency import run_advanced_consistency


def run_test(name, product, **kwargs):
    result = run_advanced_consistency(
        product,
        **kwargs
    )

    print("=" * 60)
    print(name)
    print("=" * 60)

    print("CHECKS:")
    for key, value in result["checks"].items():
        print(f"  {key}: {value}")

    print("REVIEW REASONS:")
    print(f"  {result['review_reasons']}")

    print("DETAILS:")
    print(f"  {result['details']}")
    print()


def main():

    # --------------------------------------------------------
    # TEST 1 — Normal Jordan 1
    # --------------------------------------------------------

    normal_jordan = {
        "title": "Jordan 1 Retro High OG Black White",
        "model": "Jordan 1",
        "primary_title": "Jordan 1",
        "avg_price": 180,
    }

    run_test(
        "TEST 1 — Normal Jordan 1",
        normal_jordan,
        expected_gender="MEN",
        reference_price=180,
    )


    # --------------------------------------------------------
    # TEST 2 — Travis Scott collaboration
    # --------------------------------------------------------

    travis_jordan = {
        "title": "Jordan 1 Retro High OG Travis Scott",
        "model": "Jordan 1",
        "primary_title": "Jordan 1",
        "avg_price": 900,
    }

    run_test(
        "TEST 2 — Travis Scott Jordan 1",
        travis_jordan,
        expected_gender="MEN",
        reference_price=180,
    )


    # --------------------------------------------------------
    # TEST 3 — GS mismatch
    # --------------------------------------------------------

    gs_jordan = {
        "title": "Jordan 1 Retro High OG Chicago (GS)",
        "model": "Jordan 1",
        "primary_title": "Jordan 1",
        "avg_price": 120,
    }

    run_test(
        "TEST 3 — GS Jordan 1",
        gs_jordan,
        expected_gender="MEN",
        reference_price=180,
    )


    # --------------------------------------------------------
    # TEST 4 — Extreme price anomaly
    # --------------------------------------------------------

    expensive_jordan = {
        "title": "Jordan 1 Retro High OG Black White",
        "model": "Jordan 1",
        "primary_title": "Jordan 1",
        "avg_price": 52000,
    }

    run_test(
        "TEST 4 — Extreme price anomaly",
        expensive_jordan,
        expected_gender="MEN",
        reference_price=180,
    )


    # --------------------------------------------------------
    # TEST 5 — Impossible release year
    # --------------------------------------------------------

    impossible_year = {
        "title": "Jordan 4 Retro Black Cement",
        "model": "Jordan 4",
        "primary_title": "Jordan 4",
        "release_year": 1975,
        "avg_price": 250,
    }

    run_test(
        "TEST 5 — Impossible release year",
        impossible_year,
        expected_gender="MEN",
        reference_price=250,
        model_history={
            "first_known_year": 1989,
        },
    )


if __name__ == "__main__":
    main()
