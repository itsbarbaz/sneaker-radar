"""
Salva la risposta GREZZA di KicksDB per poche query rappresentative,
con un riepilogo dei campi presenti.

Serve a scoprire i nomi veri dei campi (valuta, data di
aggiornamento, numero di vendite, taglia...) invece di indovinarli.
Non scrive mai la chiave API nell'output.

Variabili d'ambiente:
    KICKSDB_API_KEY   obbligatoria
    OUTPUT_PATH       opzionale, default kicksdb_raw_sample.json
"""

import json
import os
import urllib.error
import urllib.parse
import urllib.request

QUERIES = [
    "Jordan 4",
    "Nike Dunk",
    "adidas Samba",
    "New Balance 990",
    "HOKA Clifton",
    "On Cloudmonster",
    "Travis Scott Jordan 1",
    "ASICS Gel Kayano 14",
]

PRODUCTS_PER_QUERY = 3


def fetch(api_key, query):
    params = urllib.parse.urlencode(
        {"query": query, "limit": PRODUCTS_PER_QUERY}
    )
    url = "https://api.kicks.dev/v3/stockx/products?" + params

    request = urllib.request.Request(
        url, headers={"Authorization": api_key}
    )

    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            return {
                "http_status": response.status,
                "body": json.loads(response.read().decode()),
            }
    except urllib.error.HTTPError as error:
        return {"http_status": error.code, "error": str(error)}
    except Exception as error:  # rete, JSON non valido, timeout
        return {"http_status": None, "error": repr(error)}


def type_name(value):
    if value is None:
        return "null"
    return type(value).__name__


def summarize_fields(products):
    """Per ogni campo: in quanti prodotti c'e', tipi visti, un esempio."""
    summary = {}

    for product in products:
        if not isinstance(product, dict):
            continue

        for key, value in product.items():
            entry = summary.setdefault(
                key, {"present_in": 0, "types": set(), "example": None}
            )
            entry["present_in"] += 1
            entry["types"].add(type_name(value))

            if entry["example"] is None and value not in (None, "", [], {}):
                text = json.dumps(value, ensure_ascii=False, default=str)
                entry["example"] = text[:160]

    return {
        key: {
            "present_in": entry["present_in"],
            "types": sorted(entry["types"]),
            "example": entry["example"],
        }
        for key, entry in sorted(summary.items())
    }


def main():
    api_key = os.environ["KICKSDB_API_KEY"]
    output_path = os.environ.get("OUTPUT_PATH", "kicksdb_raw_sample.json")

    raw_by_query = {}
    all_products = []

    for query in QUERIES:
        print(f"query: {query}")
        result = fetch(api_key, query)
        raw_by_query[query] = result

        body = result.get("body")
        products = body.get("data", []) if isinstance(body, dict) else []
        all_products.extend(products)

        print(f"  http={result.get('http_status')} prodotti={len(products)}")

    output = {
        "queries": QUERIES,
        "products_total": len(all_products),
        "field_summary": summarize_fields(all_products),
        "top_level_keys_per_query": {
            query: sorted(result["body"].keys())
            for query, result in raw_by_query.items()
            if isinstance(result.get("body"), dict)
        },
        "raw": raw_by_query,
    }

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(output, file, indent=2, ensure_ascii=False, default=str)

    print(f"salvato: {output_path}")
    print(f"campi distinti: {len(output['field_summary'])}")


if __name__ == "__main__":
    main()
