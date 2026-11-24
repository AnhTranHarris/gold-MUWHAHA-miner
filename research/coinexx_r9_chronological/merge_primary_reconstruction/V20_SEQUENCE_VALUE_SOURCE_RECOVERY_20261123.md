# V20 — R9 HybridGate merged-primary two-slot sequence-value entry research (23 Nov 2026)

**STATUS: ENTRY-ONLY NINE-MONTH HEAVY IN-SAMPLE RESEARCH. V20B improves the V17B research control, but does NOT reconstruct most merged entries. NO native MQL5 compile, trading, funding, fills, holds, exits, or profit evidence.**

## Source authority and exact recovery — README IS NOT SOURCE DOCUMENTATION

**[COMPLETE V20 actual C++17/Python source and models, 55-member ZIP on MT5_EXPAND](https://drive.google.com/file/d/1Yz6GKqkaKlZJe2XPegibEIpciBhQPQxm/view)**

- ZIP exact SHA-256 `62b5da42bc4fdc4a69bc9ff8f901012fe2fa474a040e7613904a3460fbb20ba5`; 9,030,132 bytes, 55 ZIP members, all 54 payload SHA-256 verified, ZIP CRC PASS, **no raw Coinexx tick or original merged history copies**. Clean archive C++17/zlib build and original January 1.2-million-quote causal-prefix 70,469 event rows PASS.
- Read `V20/README_SOURCE_EXACT_V20.md` INSIDE THE ZIP. Read the ACTUAL scripts `v20_sequence_credit.py`, `fit_v20_sequence.py`, `score_v20_events.py`, `v20_online_arbiter.py`, `source_only_proposal_features.py`, `fit_v20_confidence_offline.py`, `score_v20_action_confidence.py`, `v20_integrated_stateful_gate.py`, `qa_v20_source_only.py`, full parent V19/V17/V16/V14 original C++ source lineage, all 5 frozen model text files, accepted/rejected numeric receipts and original V17B source-only fallback ledger. Do not substitute summaries for executable source.
- Original XAUUSD R9 v1.90 MT5 EA `Experts/GoldMuwahahaMiner_R9_HybridGate.mq5` Git blob SHA `7eecb5f1947017a01ce85b2520725de54749e523`, unchanged; canonical approved branch `carson/mt5-r9-hybrid-gate-certification`.
- ORIGINAL authoritative new merged January 2026 and Feb–Sep 2026 R9+Coinexx source ZIPs: 272,352 historically outcome-aligned mapped entry times, sides and recorded +$360,693.05 historical net. These are OFFLINE training/alignment TARGETS, never live in-run order instructions. Source Coinexx MT5 TickLogger Jan–Sep original chronological gzip files: 72,129,347 original Bid/Ask quotes. 9/9 original gzip hashes and 2/2 frozen merge ZIP hashes verified and pinned in ZIP QA.

## Mechanism

Source-real V19 R9 event queue and frozen V17B clock supply the only opportunity timestamps. V20 offline Bellman training creates rank-0 and rank-1 action labels: for each observed event t_j and retrospectively mapped target tau_k, reward r_jk = 1(abs(t_j-tau_k)<=5000ms) * (1-0.00003*abs(t_j-tau_k)), with 3s min sequential action gap and two slots per minute. The full future opportunity is allowed only to construct in-sample SUPERVISED TARGETS; never as an input to online inference.
V20 has independent first/rearm multiclass action and Q(ENTER)-Q(WAIT) regressors trained on 993,271 bounded samples from all nine months. Source-only V20A generated 293,702 entries, 104,155 same-direction ±5s alignment, but lowered precision due extra proposals. V20B adds a learned probability of a correctly aligned entry trained OFFLINE on frozen merged target pairing; the confidence model has a 26,844-row complete-minute-block internal holdout AUC 0.65937 (only a research within-month diagnostic, NOT untouched forward test).
At each *chronological source event/fallback action*, confidence is computed exclusively from source-observed prior market state, chosen role, and frozen model. With confidence below 0.08, NO entry slot is consumed; future eligible events may compete. This is an integrated stateful replay, not a retrospective mask of old V20A output.

## EXACT all-nine-month entry-only alignment

| Controller | Source-generated proposals | ±2s correct side | ±5s correct side | ±15s | ±30s | ±5s per-proposal |
|---|---:|---:|---:|---:|---:|---:|
| V17B previous governing research control | 287,770 | 53,384 | 102,681 | 148,895 | 182,699 | 35.68% |
| V20A sequence value, ungated | 293,702 | 54,052 | 104,155 | 151,263 | 185,413 | 35.46% |
| **V20B source-chronological confidence gate=0.08** | **288,317** | **54,016** | **104,014** | **150,287** | **183,460** | **36.08%** |

V20B advances over V17B in **all four timing windows and precision**. All **nine months** separately satisfy >=90% original merged entry count (actual 103.4–109.1%). Every month increases ±5s same-side matches; 9m improvement **+1,333** at net +547 proposals. Yet only **104,014/272,352 = 38.19%** of frozen entries align ±5s: main entry reconstruction GOAL NOT MET. Heavy nine-month in-sample grading, no deployment/MT5 tester claims.

Offline target attribution: V20B newly matches 1,493 originally missed frozen entries and loses 160 previously matched ones, net +1,333. Net by original trade position: first +686; second/recovery +650; third+ -3. New captures concentrate at minutes seconds 10–35, especially 30–34 (+474 net), 25–29 (+251), 10–14 (+185), 15–19 (+175); 40–54 still largely missed. Never use this retrospective attribution to instruct source-only inference.

## QA and rejected variants

- Independent source-only replay of **all 288,317** V20B entries and direction/source/confidence values, all 9/9 months, against saved frozen executable models: PASS without opening any merged reference targets; when confidence gate disabled, all nine V20A signals exactly match previous source-only ledger.
- Jan 1.2M quote C++ prefix (70,469 source event observations) byte-identical to full 7.699M January quote replay. Clean ZIP-only C++17 rebuild and prefix reproduction PASS. All 11 original datasets (9 quote logs + 2 merge ZIPs) SHA256 verified.
- Rejected V20 recovery-only deferral model: Jan/Mar/Jul best ±5s matches 36,100 versus baseline 36,121; no promotion.
- Rejected fixed-clock side override: best 36,123 vs 36,121 on Jan/Mar/Jul, inconsequential.
- Alternate confidence gates .10/.12/.16 trade absolute target recall for precision; fixed gate .08 was chosen within in-sample research and is not out-of-sample approved.

## Next evidence-based focus

First/recovery event-credit selection is incrementally better, but missed merge entries at phase seconds **35–54** remain unresolved. Investigate a new, **restricted late-stage opposite-reclaim/recovery reservation specialist** on real tick-derived quote states and previously observed first-leg setup; compare incremental source-only same-side one-to-one timing and nine independent >=90% monthly count floors. Do not broaden into unrelated generic indicators, do not add guessed order-book/volume history, do not rebuild original quote files, and do not change original approved R9 v1.90.

**GitHub branch here is an additive rollback/source recovery checkpoint; working C++/Python source and frozen models are in the SHA-pinned MT5_EXPAND ZIP above, not a summary.**