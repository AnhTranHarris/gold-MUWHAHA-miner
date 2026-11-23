# R9 HybridGate V9 — exact-source recovery index (2026-11-23)

**Status: heavily-fitted nine-month in-sample RESEARCH, FAILED approval criteria, no native MQL5 compile or production trade authorization.** This page is only an index. **DO NOT use it in place of the original C++ and Python source files.**

## Full, original, directly executable source — primary recovery asset

**[Download V9 source package from MT5_EXPAND](https://drive.google.com/file/d/1kJgKHP9jVBDevvm6gga-_oyp4N6eemOz/view)**

Archive: `R9_HYBRIDGATE_V9_SOURCE_ONLY_20261123.zip` (418,921 bytes), exact SHA256 `c40100ed16cec1d83238faaff3a4fed786e1fd69611eb1dc98c5a34f1b6402d7`. Includes 25 ZIP entries; 24 internal file SHA checks and ZIP CRC pass. Zero original raw ticks duplicated.

The **full executable** source is `R9_V9_SOURCE_ONLY_20261123/source/r9_hybridgate_v9.cpp`; compilation dependencies `r9_v7_value_model.hpp`, `r9_v8_value_model.hpp`, `r9_v8b_value_model.hpp`, and exact original source parent `r9_hybridgate_v8b.cpp` are present in `source/`.

**Do not reconstruct code from prose.** Included full files:
- `research/build_v9.py`: guarded, literal source modifications of pinned V8B
- `research/screen_v9.py`, `research/v9_fullnine_p6.py`: tested original-source runner
- `research/portable_replay_v9.py` and `REPRODUCE_V9.sh`: source hash verification, compile, full nine-month C++ chronological replay, exact P&L receipt validation
- `research/causal_prefix_test_v9.py`: strict quote-suffix truncation check
- `receipts/v9_p6_fullnine_scorecard.csv`, `V9_COMPARISON.csv`, `V9_QA.json`, `v9_causal_prefix_receipt.json`
- `receipts/v8b_reference_jan.csv` and `v9_default_jan.csv` to independently verify V9 default-mode **byte-exact** 1,365-trade replay parity
- `receipts/source_sha256_v8b_independent.json`: original nine Coinexx compressed raw-source SHA256s, 72,129,347 actual ticks
- `RESEARCH_CONTINUATION_V9_SOURCE.md` and `MANIFEST_SHA256.json`.

## Source precedence (read these actual sources)

1. Original R9 v1.90 EA `Experts/GoldMuwahahaMiner_R9_HybridGate.mq5` on branch `carson/mt5-r9-hybrid-gate-certification`; immutable blob `7eecb5f1947017a01ce85b2520725de54749e523`.
2. True January merged R9/Coinexx archive: https://drive.google.com/file/d/1BUUQV_enLHz-OaswCrTfoTF7ibf7YCuY/view .
3. True Feb-Sep merged archive: https://drive.google.com/file/d/11hdLG-OI7OsG4uH75_0mNvFadBF6Szvx/view .
4. Nine original real Coinexx TickLogger monthly gzip files on PRIMARY Drive: https://drive.google.com/drive/folders/1XzHug6HYQdSKIbKuGhBTOUHawAXynIb4 .
5. V8B full, exact source/model archive: https://drive.google.com/file/d/1_pr73FIpJuBC6hk-AS92QeTtXkx7mLtn/view , SHA `f2f96709b7f69324a6b70814f3e376a706226d329d0ab06c10b98dd04bf16bda`.

Merged matched Coinexx outcomes are hindsight/target conditioned, not causal replay fills. **Freeze original R9 net $360,693.05 across 272,352 Jan-Sep synthetic R9 trades as a nine-month in-sample performance benchmark.** Do not train runtime inference from future Coinexx matching endpoints.

## Actual independent Coinexx replay results

Full V9 P6 heuristic lifecycle after original V8B 43-feature entry admission gate:
- 72,129,347 source quote ticks, 17,294 completed trades, **−$694.40** after fixed $0.02/closed-trade fee and genuine bid/ask execution marks. Original V8B: 16,209 trades, −$393.36.
- 0 of 9 monthly frozen 90% profit floors met.
- January: 1,456 trades +$106.24 vs V8B 1,365 +$100.64.
- July: 331 trades +$2.25 vs V8B 322 +$3.83.
- March/April independent monthly hypothetical $100 cash goes <=0, so complete nine-month trades beyond that boundary are research-only unbounded diagnostics, NOT fundable account performance.
- Entire nine-month P6 engine tested on original tick source, not retrospectively matched oracle trade schedules.
- Prefix causality: 3,000,000 January source ticks vs 7,699,274 full, **149** identical closed positions before prefix cutoff.
- V9 with new action/risk switches disabled: original frozen V8B January ledger byte-for-byte identical.
- Source-only archive extracted and recompiled cleanly; independent January replay reproduced 1,456 completed and +$106.24 after fees.

V9 attempted source-causal quote-age abort, low-persistence harvest, volatility-sensitive stop and conditional opposite/same-side rearm. Most action changes lost economic edge in different regimes. None accepted.

**Next researched design is conditional on-policy lifecycle value**: distinct original R9 first-entry / successful continuation / after-loss opposite rearm states; event-specific first-passage survival and liquidation value, not a universal short-horizon exit threshold. Use all nine months for intensive source-exact in-sample training; evaluate **whole original R9 minute-state machine** on the actual real-tick tape with $100/$500 cash and every monthly 90% benchmark. Preserve complete executable source and incremental receipts.

The original R9, all approved MICRO180/S100/account-risk policies, and native production EA are unchanged. This branch carries a source pin; **the complete V9 C++ source is inside the linked MT5_EXPAND ZIP**, not committed as native MQL5 code.