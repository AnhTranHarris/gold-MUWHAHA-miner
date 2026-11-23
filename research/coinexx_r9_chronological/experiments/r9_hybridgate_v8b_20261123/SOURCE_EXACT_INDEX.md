# R9 V8B — exact-source multi-event research, 2026-11-23

**RESEARCH ONLY. Not a compiled or approved MT5 EA. Original R9 source, V6/V7 research source and all approved risk policies are unchanged.**

## FULL executable source and tests (AUTHORITATIVE for V8B, not this index page)

**[Open exact V8B source archive in MT5_EXPAND](https://drive.google.com/file/d/1_pr73FIpJuBC6hk-AS92QeTtXkx7mLtn/view)**

Archive: `R9_HYBRIDGATE_V8B_MULTI_EVENT_SOURCE_ONLY_20261123.zip`; 816,821 bytes; SHA-256 `f2f96709b7f69324a6b70814f3e376a706226d329d0ab06c10b98dd04bf16bda`. 58 entries, 57 hashed source/test/receipt files, zero duplicate raw tick files.

**Read code files, DO NOT SUBSTITUTE THIS PAGE OR AN ASSISTANT SUMMARY:**
- `R9_V8B_20261123/source/r9_hybridgate_v8.cpp`
- `R9_V8B_20261123/source/r9_hybridgate_v8b.cpp`
- `R9_V8B_20261123/source/r9_v7_value_model.hpp`
- `R9_V8B_20261123/source/r9_v8_value_model.hpp`
- `R9_V8B_20261123/source/r9_v8b_value_model.hpp`
- `R9_V8B_20261123/source/v8b_heavy_insample_model.txt`
- `R9_V8B_20261123/research/fit_v8b.py`, `build_v8.py`, `build_v8b.py`, `replay_v8b.py`, `causal_prefix_test_v8b.py`
- `R9_V8B_20261123/REPRODUCE_V8B.sh`, `MANIFEST_SHA256.json`, `RESEARCH_SOURCE_EXACT_CONTINUATION.md`
- `R9_V8B_20261123/receipts/v8b_ninemonth_research_scorecard.csv`, `source_sha256_v8b_independent.json`, `v8b_causal_prefix_receipt.json`, full model parity vectors and all experimental controls.

## Original source precedence

1. Original R9 v1.90 source `Experts/GoldMuwahahaMiner_R9_HybridGate.mq5` at `carson/mt5-r9-hybrid-gate-certification`, **blob SHA** `7eecb5f1947017a01ce85b2520725de54749e523`, is immutable.
2. January retrospective merged trade book: https://drive.google.com/file/d/1BUUQV_enLHz-OaswCrTfoTF7ibf7YCuY/view .
3. February–September retrospective merged book: https://drive.google.com/file/d/11hdLG-OI7OsG4uH75_0mNvFadBF6Szvx/view .
4. Nine original Coinexx TickLogger CSV.gz files on PRIMARY Drive (01–09): https://drive.google.com/drive/folders/1XzHug6HYQdSKIbKuGhBTOUHawAXynIb4 .
5. V7 full source archive: https://drive.google.com/file/d/15sr5-gvdGnNqhXxr7vInLDGOJrFZVsgq/view .

The merged book gives frozen historical economic targets, while its hindsight-selected actual quote endpoints **are not deployable orders**. Do not use future matched entry/exit ordinals in V8B model inputs.

## QA and exact economic checkpoint

- All 9 original raw gzip files independently SHA256 verified; **72,129,347 source ticks**.
- January V8/V8B switches-off control exact ledger matches prior R9 V7E source (32,179 trades).
- Added V8B features OFF leaves V8 on-policy active-mode entries/exit ledger unchanged byte-for-byte.
- 36/36 frozen 43-feature LightGBM predictions match C++ within 1e-6 cents.
- January V8B model-gated 3M-quote causal-prefix: first 148 closed positions identical to full 7,699,274 quote source.
- Nine-month V8B on-policy frozen -10 cent model gate: **16,209 completed trades; -$393.36**, **0/9 months** achieve 90% original R9 net; $100 cash boundary fails in March and April monthly replays. The historic nine-month original R9 SYNTH net is $360,693.05 (272,352 trades) and the combined minimum target is $324,623.75. The studied V8B model was deliberately fitted across all nine months; this is not forward evidence.
- The quote-based Python/C++ engine uses 0.01-lot-equivalent one-ounce exposure, actual ordered Bid/Ask, $0.02 fee once per closed position, no extra spread charge. No MT5 broker filling, margin, or actual native tester claim.

## Required next engineering design

Inside the **same R9 minute-cycle/rearm architecture**, use observed source-first-passage to learn a policy-conditioned semi-Markov action-value/competing-risk model for qualified breakouts, failed-break reclaims, overshoot continuations and opposite rearms. Update model on on-policy *completed* paths to avoid the V8B off-policy admission failure. Build the entire lifecycle and account risk governor together, test each individual month and preserve source hashes and scripts. Expand as-of Bid/Ask proxy microstructure; never claim level-2 depth that is absent.

No new MQL5 production EA order action or main branch merge has been performed or approved.