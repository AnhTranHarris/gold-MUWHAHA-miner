# F385-R02-S03-R01 — source-exact negative scientific checkpoint

**Status: unapproved, historically exposed, no verified R9 quota pass, no trading release.** Original owner research-stage ledger remains **20/39**; M-CX-07 and M-DK-01 open; all G01–G09 open.

## Source / reproducibility

- Immutable 2,574,251 original R00-054 events across Coinexx and Dukascopy Jan/Feb/Jun/Jul 2026; original t0 timestamp, BUY/SELL side, 30–32s midpoint truth unchanged.
- Frozen healthy replay engine commit: `ca4b58aec597174b6f6d18ab2f36cba6836e4f4c`; no engine changes.
- All eight native source gzip SHA256s checked against that commit's `research/htf_dual_ticklab/htf_ticklab/source_registry.py`. Coinexx UTC shift Jan/Feb -120min, Jun/Jul -180min; Dukascopy UTC.
- 1,322 ambiguous Coinexx same-ms source events **never vetoed**; all remain in denominators.
- Coinexx marks from native MqlTick BID/ASK flags; Dukascopy marks from exact raw integer bid/ask revisions. 137 causal t0 features including native quote-clock intensity and only completed M1/M5/M15/H1 structural bars.
- Independent broker-specific 3-class LightGBM, 511 leaves ×110 trees, Jan/Feb first70% FIT, Feb70–80 CAL, 40s embargo; Feb80–90 VAL; June/July historically exposed transfer. No own-month FILTER08 teacher score at inference.
- 40 CAL score/guardian policies per broker, 80 total; **zero** achieve >=20 wrong veto per 1 correct lost at >=500 CAL bad veto.

## CAL-frozen diagnostic (NOT qualified or deployable)

| Broker | Month | Wrong/neutral veto | Correct lost | Correct kept | Kept directional precision |
|---|---|---:|---:|---:|---:|
| Coinexx | Jan | 6,658 | 727 | 181,142 | 0.535955 |
| Coinexx | Feb | 11,280 | 1,045 | 154,493 | 0.488046 |
| Coinexx | Jun | 546 | 356 | 141,868 | 0.456018 |
| Coinexx | Jul | 529 | 288 | 143,074 | 0.446754 |
| Dukascopy | Jan | 945 | 108 | 178,534 | 0.520532 |
| Dukascopy | Feb | 2,642 | 323 | 143,600 | 0.446494 |
| Dukascopy | Jun | 288 | 99 | 132,006 | 0.444992 |
| Dukascopy | Jul | 682 | 259 | 130,149 | 0.433340 |

**Coinexx** Feb CAL wrong/right 49/32 (1.531:1); Feb VAL 96/78; July opposite 309 / neutral 220 veto; July wrong AUC 0.511548. **Dukascopy** Feb CAL 61/29 (2.103:1); Feb VAL 70/19; July opposite 227 / neutral 455 veto; July wrong AUC 0.535260. All June/July diagnostics historically exposed, not blind OOS.

Even necessary *source-correct-event* 90% hourly retention proxies fail in Coinexx Jan/Feb/Jun and Dukascopy Feb/Jun/Jul. These are **not** the original R9 SYNTH 4,178 eligible hour/day/week/month rows; actual R9 floor compliance remains **unverified**. No F234 full union, real bid/ask fills, commission/slippage, MQL5 parity, $100/$200 survivability, or profitability claim.

## Scientific controls and preserved artifacts

Four causal fixtures pass (quote prefix invariance, completed HTF publication, same-ms conservative index, t+32s matured-label lag). Eight original masks match F383 t/side/truth arrays. Same-hour/side fixed-volume placebo and frozen F383 t0-mask overlap reported in the MT5_EXPAND source-exact research Doc.

**Corrected model SHA256:** Coinexx `141e2904af863c7e3eb5bdfdd46ae8d10e841704941102fb43734866e1eee8e2`; Dukascopy `01aa8df79f977abf132d03fbf6ca3dc66e6b8578e8996a599f7529951a7b3264`.

Local complete original research ZIP: `F385_R02_S03_R01_ORIGINAL_EIGHTCELL_NATIVE_MARKED_HTF_NEGATIVE_20261024.zip`, **111,178,476 bytes**, SHA256 `deea0a4a72b7f028fd4f44baf6429b3af95420217219f419ec557826a2909579`, 48 members, CRC and member hashes PASS. Contains both model texts, all eight event score/mask arrays, all 80 CAL policies, feature/source hashes, code/tests and invalid initial R00 probe. **The ZIP is not yet authenticated as uploaded to cloud; do not infer availability from this note.**

Original R00 float32 mark detection was invalidated; corrected R01 used native Coinexx flags and exact Dukascopy integer revisions, recomputed all eight cells and refit both models. No changes to approved engines. Source-exact research Doc (MT5_EXPAND 01): https://docs.google.com/document/d/1ZjAi9Vj0HmcSOSeYXu2877iYQi3rKmLawYPZAwGQgJ0/edit

**Decision:** CLOSED/PARKED, UNAPPROVED NEGATIVE. No owner checklist modification; no approved 02 component, MQL5 build, demo/live deployment, or user success notification. March remains unopened.
