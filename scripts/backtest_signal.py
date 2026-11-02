"""Scarica lo storico (sola lettura) e lo salva per il backtest. Uso: python scripts/backtest_signal.py dati.json && node scripts/backtest_signal.js dati.json"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import social_image as S
items = S.load_real()
out = [{"sku": i["sku"], "times": [int(t * 1000) for t, _ in i["pts"]], "prices": [p for _, p in i["pts"]]} for i in items if len(i["pts"]) >= 9]
json.dump(out, open(sys.argv[1] if len(sys.argv) > 1 else "dati.json", "w"))
print("Serie salvate:", len(out))
