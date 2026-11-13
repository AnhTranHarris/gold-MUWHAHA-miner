# Gold MUWHAHAHA R9 — quote-only pressure proxy pilot

**Research-only result: no reliable improvement to 155-feature AUC.** The three implemented feature families are fixed-kernel marked quote-event excitation (12), a causal two-timescale latent quote-pressure state filter (7), and quoted-spread resilience (8). They use only the existing Coinexx Bid/Ask/time_msc, including source ordinal and same-ms ordering.

See `RESULTS.md` for frozen baseline/five-fold AUC, original R9 direction, day-block uncertainty, and the limitations of inferring liquidity from price-only data. The existing QRB/QAF-enabled R9 EA is unchanged; no thresholds were deployed.

## Reproduction inputs

The historical quotes and prior frozen derived caches are referenced, not duplicated:
- Original broker raw Jan–Sep 2026 `XAUUSD_MT5_BROKER_2026_MM_ticks_ALL.csv.gz` in the primary data archive.
- Frozen 145-column original R9 features: `R9_M60_FullUniverse_DerivedCache_Part1/2/3_*zip`.
- Original event-time competing-hazard labels/features: `R9_M60_Hazard_ExactEvent_Derived_2026_Part1/2/3_*zip`.
- Frozen CUSUM/intensity features: `R9_M60_Coinexx_CUSUM_QuoteIntensity_Cache_JanSep_20261113.zip`.
- Original 155-feature baseline model: `R9_M60_JanSep_FullTraining_155Features_20261113.zip`.

The report's files can be reconstituted in `/mnt/data/r9_m60_proxy_20261113/deps`; local source scripts use pinned archive paths. The `derived` zip in this handoff contains only new proxy features and the nine SHA receipts, not historical raw data. For tests, `PYTHONPATH=src python -m unittest discover -s tests -v`.

## Scientific restrictions

- The fixed kernels are *Hawkes-inspired*, **not** fitted multivariate Hawkes maximum-likelihood parameters.
- The latent pressure filter predicts quote-price behavior, **not** latent executed order imbalance.
- Spread resilience measures **quoted spreads**, not L2 displayed-size replenishment.
- AUC reflects fixed five-second labels at original R9 timestamps; it does not demonstrate an actual profitable or high-volume trading strategy.
- May–September are previously researched development months, not fresh or independent test data.
