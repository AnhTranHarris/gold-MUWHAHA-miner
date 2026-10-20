# R00-054 F15 — additive causal matured-quote opportunity veto

Verified existing-lineage research, October 19, 2026 user local. **No original R00-054, source tape, model, replay engine, or MT5 order logic changed.** Descends from F10 source branch commit `d7c8fdb9418468d2e5362fcfa350c885284a5136`; preserves research F11–F14 as separate continuing studies.

## Successful measured candidate mechanism

Within each broker's original R00-054 five-second event stream, original event `i` is considered executable only if its latest two previously emitted events whose **full native midpoint +30..32-second markouts are mature by event_i time** both had non-neutral directional displacement. An earlier event is eligible only at `event_time_j + 33,000 ms <= decision_time_i`. The current signal's own future label is never read. The code in `f15_matured_nonneutral_veto.py` implements this exact rule.

This is an **entry-only permit/veto on the original BUY/SELL side and original event timestamp**. It uses original event-time aligned fully matured quote feedback, not exchange-traded volume or hold/exit/P&L.

### Source-matched four-month cumulative results (two separately evaluated brokers)

| Measure | Baseline R00-054 | New fixed F15 rule |
|---|---:|---:|
| Emitted source-native research signals | 2,574,251 | 2,048,235 |
| Correct initial directions | 1,208,071 | 978,629 |
| Correctness | 46.9290% | **47.7791%** |
| Originally bad events vetoed | — | **296,574** |
| Additional missed R9 SYNTH reference hours or days | — | **0 in all eight broker-month studies** |

All eight individual broker-month correctness percentages increased using this same rule, including the June/July historically exposed months. **Critical classification:** The fixed two-event rule was retrospectively selected after comparing original January, February, June, July outcomes, so this is promising *teacher-free causal mechanism discovery*, NOT prospective frozen/blind model selection. No claim of 70% transferable precision or executable MT5 positions is made.

The full original 3200-row condition grid (400 experiments × eight source broker-months) and exact eight original signal-array receipts were preserved in local package `R00_054_FILTER15_CAUSAL_MECHANISM_CONTINUATION_20261019.zip`: 115,051 bytes; SHA-256 `bcc5138558af8b685d0cdf57931dc3d1cf3a0eb376d624c0e01bddd37eae2a3f`; ZIP CRC PASS. Its files: `R00_054_FILTER15_MATURED_RESPONSE_VOTING.py`, `test_filter15_causality.py`, all eight original monthly candidate CSV panels, shared-rule cross-month analysis, JuneJuly specialist cooperation panel, `F15_VERIFIED_DISCOVERY_RECEIPT.json`, `SOURCE_FILE_SHA256_MANIFEST.json`, and research-only F14 student scripts/receipts. Existing approved native raw tick archives are source registry pinned and NOT duplicated in package.

### Scientific continuation

Protect elected R00-054; retain the historically fitted F08/F10 70–84% as an overfit feature-extraction teacher **only**. F15 is a truly causal mature-prior-feedback input for an independent NEUTRAL/no-opportunity hazard specialist. Couple with separate opposite-direction hazard from actual source bid/ask updates and published M15/H1 sweep/reclaim lifecycle, session volatility/structure and independent resets. Choose thresholds with time-ordered JAN/FEB training/calibration and source independence, freeze on June/July (historically exposed) then require a genuinely unexposed approved month for blind verification. Per eligible UTC hour/day R9 SYNTH correct-entry-count >=90% still governs throughput; no profit/exits/account claims.

### Public mechanism-research sources, not performance evidence

- MetaQuotes [secondary meta-labeling architecture](https://www.mql5.com/en/articles/22274).
- MetaQuotes [entry filter permutation evaluation](https://www.mql5.com/en/articles/23665).
- MetaQuotes Chinese [asymmetric gold directional modeling](https://www.mql5.com/zh/articles/17654).
- [Regime-filter discussion](https://www.reddit.com/r/algotrading/comments/1v42762/regime_filters_matter_more_than_your_entry_rule/) and [meta-labeling field discussion](https://www.reddit.com/r/algotrading/comments/1lnm48w/meta_labeling_for_algorithmic_trading_how_to/).
- [QuantConnect false-positive meta-model research](https://www.quantconnect.com/forum/discussion/14706/why-meta-labeling-is-not-a-silver-bullet/).

User archive preference: use Google Drive and GitHub; do NOT spend remaining ChatGPT personal Library space. A new Google Drive archive is **not claimed** until the upload completes and its hashes are read back. This receipt is evidence, not a substitute for the full original governing reports or versioned governor laws.
