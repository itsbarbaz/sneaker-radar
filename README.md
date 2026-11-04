# Hypewise — sneaker resale price radar

**Live site: https://itsbarbaz.github.io/sneaker-radar/**  ·  X: [@gethypewise](https://x.com/gethypewise)  ·  hypewise.team@gmail.com

Hypewise tracks US resale prices of sneakers every day and turns the history into a simple, explainable signal: **Cop, Wait or Sell?**

## What it does

- Collects daily resale prices for hundreds of sneakers (rotating batch per day).
- Stores the full price history in a database and shows charts for every model.
- Computes a transparent signal from 5 factors (trend, momentum, position in range, volatility, data quality), with a confidence score. It refuses to give a verdict when there is not enough data (fewer than 8 readings over 7 days).
- Publishes daily "biggest movers" and a single-sneaker spotlight for social media, generated automatically.
- Static site in English, Spanish, French, Italian and Russian. No frameworks, no cookies, anonymous first-party visit counter only.

How the signal works: [/method.html](https://itsbarbaz.github.io/sneaker-radar/method.html)

## How it works

```
GitHub Actions (daily)  ->  Python bot (src/main.py)  ->  Supabase (Postgres)
                                                              |
                         static site on GitHub Pages  <-------+   (read-only public key)
                         social images / video (Pillow, ffmpeg) -> `social` branch
```

| Part | Where |
|---|---|
| Daily price collector | `src/main.py`, workflow *Sneaker Radar* |
| Site (HTML/CSS/JS, i18n) | `site/` |
| Signal logic | `site/signal.js`, backtest in `scripts/backtest_signal.py` |
| SEO pages (models, brands, movers, sitemap) | `scripts/build_seo.py` (generated at deploy) |
| Social images and video | `scripts/social_*.py` |

## Honest limitations

- Price history is young (about a month), so signals are early and **not validated**: a first backtest on 10 series is too small to prove anything and will be repeated as data grows.
- A single price source; no size-level data yet.
- Estimates only. **Not financial advice.** Not affiliated with any brand or marketplace; all trademarks belong to their owners.

## Roadmap

- Watchlist and price alerts
- More history, then a re-run of the backtest
- Size-level prices and a second data source
- Weekly per-model reports

## Development

Built by a solo founder together with Claude (Anthropic's AI assistant), which wrote much of the code and tooling under human direction and review. Feedback and issues are welcome.

Run the site locally: `python3 -m http.server -d site` then open http://localhost:8000.
