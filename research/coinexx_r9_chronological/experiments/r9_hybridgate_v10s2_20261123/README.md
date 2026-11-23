# R9 HybridGate V8B–V10S2: Nine-month in-sample source-exact continuation (2026-11-23)

**IMPORTANT:** Existing R9 research; not a new strategy. **NOT APPROVED** for live MT5, broker deployment, or a real-tick Strategy Tester performance claim. Original R9 v1.90 and its source branch are unchanged.

## Exact source recovery (not a summary substitute)

**READ AND EXECUTE THE COMPLETE ARCHIVE, NOT THIS HANDOFF ALONE**:

- Full **74-file C++17/Python/source-model/forensic and quality-control archive**: [MT5_EXPAND original package](https://drive.google.com/file/d/1HWEpL38QuS5ft_urIBiLZGuJRpDWJ_Mm/view). Package sha256 `e0f284849aea3956ecf4218677e05f65349022ba4171e5e3c7be70767d01e73d`; 1,299,452 bytes; all 74 payload SHA256 hashes independently verified. **No raw tick copies.**
- Original immutable R9 EA `Experts/GoldMuwahahaMiner_R9_HybridGate.mq5`, parent source Git blob SHA `7eecb5f1947017a01ce85b2520725de54749e523`; original branch `carson/mt5-r9-hybrid-gate-certification`.
- Frozen merged R9 book: January ZIP [archive](https://drive.google.com/file/d/1BUUQV_enLHz-OaswCrTfoTF7ibf7YCuY/view); Feb–Sep [archive](https://drive.google.com/file/d/11hdLG-OI7OsG4uH75_0mNvFadBF6Szvx/view). These contain 272,352 historical legs / +$360,693.05, **retrospectively matched**, not causal executable fills. The original 9 months have **nine separate monthly 90% acceptance floors** totaling $324,623.78 rounded up per-month to cent.
- Original Coinexx TickLogger monthly gzip files under PRIMARY Drive, `XAUUSD_MT5_BROKER_2026_MM_ticks_ALL.csv.gz` for January–September: 72,129,347 source quote rows; 9/9 source SHA256 verified. Original tick files NEVER rebuilt or uploaded here.

## Executable C++ on-policy research (exact package source)

Read `R9_SOURCE/r9_hybridgate_v8b.cpp` and `r9_hybridgate_v9.cpp`, `v9r.cpp`, `v10.cpp`, `v10s.cpp`, `v10s2.cpp` from the package. Read corresponding build scripts, frozen LightGBM exported C++ headers and training scripts, source-forensic Python, 9/9 V10S2 execution log files, regression tests, model inference parity receipts and SHA manifest. All decisions derive from completed tick-built MTF candles and pre-event quote information; the matched merged endpoints are never inputs to the trading simulator.

Source-verified economic outcomes:
- Original V8B R9 source-real replay 16,209 trades, −$393.36, 0/9 passes.
- V9 lifecycle risk P6 17,294 trades, −$694.40. Rejected.
- R9 regenerated rearm population 551,091 rearm trades; mean fee-net −$0.2142 per trade, negative expected return tail. Rejected as direct extension.
- Source-tick completed 5-second sweep/reclaim family 96,175 unfiltered trades; average fee-net −$0.2155. Rejected as standalone admission.
- V10S online fitted sweep model: retrospectively selected candidate subset +$667.05, but independent **on-policy** Jan −$18.43, July −$100.82.
- V10S2 full-nine-month on-policy after feedback refit: **30,567 trades, −$2,540.81**, 7,768 sweep-family trades −$690.82, **0/9** monthly 90%-R9 financial passes, month-reset hypothetical $100 capital exhausted in 7/9 months.

All simulation results include original bid/ask source-side fills and 0.01 lot=one-ounce original research convention with one $0.02 per completed trade roundtrip fee. No real MT5 broker execution, queue/slippage/rejection, broker stopout or margin is modeled; unfunded post-cash-exhaustion trades are diagnostic.

## Verification and future executable goal

Fresh C++17/zlib rebuild from exact frozen sources succeeds when the two V8B model headers are included. Python/C++ dedicated recovery model **30/30** and V10S2 feedback model **36/36** parity vectors match within 5e-11. Source-prefix test January 1.5M quote prefix vs full 7.699M quote month **136/136** early closed trades identical. Independent raw data checks 9/9 hashes. Local V11 online cycle/action state contract and 6 associated causal unit tests included in package; that is groundwork, **not** an implemented/fitted V11 profit model.

**Next actual model to build (not yet completed):** whole minute-cycle semi-Markov action-value for WAIT vs first entry vs HOLD/HARVEST vs first-to-opposite-rearm, allowing future later bracket opportunities to compete economically; source-exact C++ quote simulation and full-nine in-sample *on-policy* replay required. Do not confuse the Q objective specification or hindsight future quote-path labels with proven trading performance.

**Rollback:** this isolated child branch inherits source-only V6 research MQL5 clone with trading disabled by default; the canonical original R9 branch is unmodified. No native MQL5 compilation or strategy tester V10S2 run has occurred.
