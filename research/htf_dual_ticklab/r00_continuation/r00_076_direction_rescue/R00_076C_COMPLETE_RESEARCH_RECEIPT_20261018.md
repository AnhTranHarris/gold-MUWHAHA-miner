# R00-076C continuation — source-native interstitial direction correction

**Additive research only. No new generator, event filters, exits, executed trades, P&L, or forward-blind claims.**
Parent GitHub HEAD independently read before starting experiment: `7b77c146dae946288856a2e2d2d54d42e557b16e`.
Original Coinexx/Dukascopy source readers, R00-068 protected event timestamps/indices and R9 interval definitions were not modified.

## Frozen pre-test research artifacts
- Frozen plan JSON SHA-256: `58c68af41a5468970ccdc5bf05568b0819858efda8497a7a2eb6f5fabccc7f66`.
- Native interstitial feature implementation `interstitial_076c.py` SHA-256: `8c1e42498618debeb1a582d8386cac6e334d1dc211ba2fe078d6ab4ff7de9287`.
- Experiment runner `experiment_076c.py` SHA-256: `528b338d1b881dbf509a35b16fce492f087749001a09cfbc5e36b494c3923b7d`.
- Source-native prefix invariance and duplicate source quote index tests passed (2/2).
- All eight exact original SHA-pinned broker 2026 Jan/Feb/June/July quote tapes accessed through unmodified original `R00-067` reader. Raw event alignment checked against R00-076A and R00-070 for each month.
- Features: 31 live bid/ask quote-interstitial episode and published-pivot-history fields sampled at existing source quote index; three Jan-only independently fitted direction oracles N(31), S(85) and F(188). Full 4-specialist original R00-076 design remains INCOMPLETE; new impulse/exhaustion live states and M15/H1 sweep/reclaim observations are an additive subcycle.

## February freeze and exposed June/July transfer

Policy was frozen on February: `S_flip_005`, original 373,756 event opportunities.
- February protected reference: 175,397 correct.
- February chosen correction: 175,514 correct (+117).
- June/July historical exposed transfer: original 814,244 events preserved in both independent broker reports.
- Original protected side: 367,207 correct / 814,244 = 45.0979%.
- February-frozen S_flip_005: 366,555 correct / 814,244 = 45.0178%, **-652 correct directions**.
- Frozen policy flips 51,779 events: 22,830 rescued, 23,482 damaged, 5,467 neutral/missing flips.
- All alternatives and paired event arrays preserved. The separately scored N_flip_010 made +9 correct on transfer, but it was **not February-selected**. It cannot be promoted or retrospectively substituted.
- R9 matched volume+correct-count 90% floor: 1998/2006 UTC hours and 108/110 UTC days pass; original failed/missing intervals remain counted. ISO weeks 19/20 and UTC months 5/6 by exact two-broker R9 ledger.
- Accuracy goal >=80% **NOT MET**. No model promoted. R9 SYNTH completed profitable trade rate is NOT equal to the +30-second quote-midpoint direction label.

## Portable exact archive and verification

`XAUUSD_R00_076C_COMPLETE_INTERSTITIAL_DIRECTION_RESEARCH_20261018.zip`:
- **105,818,222 bytes**, SHA-256 `95100ec9166b8fb0f71426644e5cbc870d75539851bc9b8e1069356844609599`.
- **72 members**, independent ZIP CRC and **every member SHA-256 PASS**.
- Includes original reports and governance documents verbatim, original helper-code dependencies, frozen plans, new source .py and tests, all model joblibs, eight tick-history event caches, February selected policy, complete same-event transfer arrays, every scored candidate, R9 all hourly/daily/weekly/monthly ledgers, validation receipts and R00-076D precise continuation design.
- Original large raw source tapes and other earlier full project ZIP archives remain at their separately authorized and SHA-pinned locations. The full latest ZIP is currently a **verified local conversation artifact ONLY**. **No verified Google Drive upload has occurred in this turn.** Do not state cloud backup or allow future agents to substitute this GitHub note for the original ZIP.
- Google Drive connector cannot directly ingest an unregistered local file path; attempted personal Library preservation hit quota. This is an **archival gap**, not research result invalidation. Preserve exact ZIP and download link before ending session.

## Next research continuation, not restart

R00-076D DESIGN ONLY: quote-arrival conditional-duration hazard and persistent tick-time HTF sweep/reclaim lifecycles, fully independent impulse/exhaustion/reclaim/pullback chains, January chronological/purged OOF counterfactual flip-benefit training, February freeze, historically exposed June/July. NO unapproved extra data. Every original signal and its source timestamp remains.

Sources (public mechanism descriptions; not authorized historical price data):
- https://www.mql5.com/en/articles/24742
- https://www.mql5.com/en/articles/22063
- https://www.tradingview.com/script/Y6gO4MHi-Liquidity-Sweep-Levels-Pro/
