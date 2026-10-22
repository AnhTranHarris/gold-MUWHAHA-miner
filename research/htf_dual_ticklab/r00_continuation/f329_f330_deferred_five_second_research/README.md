# F329 / F330 — XAUUSD M-CX-01 source-native five-second deferred confirmation research
**2026-10-22 | RESEARCH ONLY | OWNER UNAPPROVED | ORIGINAL M-CX-01 OPEN | NO LIVE EA AUTHORITY.**

## Exact source and experiment identity
- PRIMARY research governor: https://docs.google.com/document/d/12lnZDGOGynu9APzK6nh0nuYeEOpB1hbgaeOszMuMFms/edit (v1.4 and 1.5-A1/A2/A3), complete original audit/log https://docs.google.com/document/d/1cYkw43LC5Ot-V686onwQS5cDZRKPyw1T1T6MvbFVSCA/edit, owner checklist https://docs.google.com/document/d/1i2GyLfwVFvyjxB-sNaOwkS6kzZLSWTsijGXaA9qJou0/edit. **Historical original status 17/39 accepted, 22 OPEN.**
- Uses eight original SHA-pinned Coinexx and Dukascopy XAUUSD bid/ask January, February, June, July 2026 source files, unchanged original 2,574,251 event times/truth/side/F234 parent. Coinexx original JanFeb wallclock -120 minutes, JunJul -180 minutes UTC; Dukascopy native UTC. Original evaluated event outcome t+30 to t+32 seconds ±$0.10 unchanged.
- F329 new competing first-passage **FUTURE TRAINING LABEL ONLY** pilot Jan/Feb did NOT pass original immediate-t0 development wrong/correct veto screen and is parked; full code/output/models preserved inside the portable ZIP.
- **F330 is materially different from an instant-t0 filter**: new independent PENDING state waits until t+5000 milliseconds before any hypothetical entry decision. It can use only source bid/ask quote trajectory by that later clock; selected adverse-first-by5s pending candidates use 124 t0 source-causal F323 features +31 frozen source quote marks +15 observed t+5s state, then a 127-leaf 75-round four-month historical trained LightGBM wrong-risk gate. Current-event future labels / original fitted teacher p are NOT inputs to F330 runtime.
- Model fit exactly 24,000 early-tranche candidates in EACH JanFebJuneJuly Coinexx original month (96,000 historical source events), >=40 second original time embargo before month late20 diagnostics. Top5% wrong-risk action threshold **0.8297866412301467** derived ONLY on original training scores and frozen. Four original Coinexx later20 segments were fitting-disjoint but 2026 months historically exposed; **NOT genuine untouched holdout**. No Dukascopy model fit or cutoff selection; separate eight-cell independent broker transfer.

## Positive results — full original eight broker-month source-shadow events vs original F234 ALONE
Additional **37,243 originally incorrect/neutral cancellation labels** versus **4,553 originally correct cancellations** = **8.17988 wrong:correct**, using fixed source threshold, across 8 month-broker cells. Opposite/neutral per-cell and original parent/side/UTC event masks inside archive. **4,178/4,178 exact original R9 historical correctly-directed source supply rows PASS**, zero failed, NOT executed orders.
- CX Jan 3,979 wrong/517 correct; Feb 6,292/782; Jun 6,231/690; Jul 5,793/578.
- DK Jan 2,710 wrong/394 correct; Feb 4,310/618; Jun 4,449/563; Jul 3,479/411.
- Coinexx later20 original-month development: Jan 753/140 (5.38), Feb 1,295/182 (7.12), June 1,204/143 (8.42), July 1,022/120 (8.52). Dukascopy later20 independent same model: Jan 461/73 (6.32), Feb 854/121 (7.06), June 959/130 (7.38), July 551/72 (7.65).
- All four Coinexx later20 month-selected wrong counts beat **all 100 same-hour fixed-count random placebo controls**; finite Monte Carlo p floor 1/101, no blind significance claim; synthetic perturbation of post-t+5 source quotes leaves 5s decision features unchanged.

## Full portable research package (code + frozen weights + eight original event masks + negatives)
MT5_EXPAND exact archived research ZIP:
https://drive.google.com/file/d/1AxBZPzjdwcrH_-OF1Ltyj3QhXx5rASNZ/view

Name: `F329_F330_MCX01_SOURCE_NATIVE_5S_DEFERRED_POSITIVE_RESEARCH_ONLY_20261022.zip`
Size: **11,432,449 bytes**. SHA-256 **df0d13314da9283c05164f84bf44885b5566631e2cbaaeff1b7f34ce48bce472**. 62 ZIP members, CRC PASS, all 61 member SHA256 PASS. Includes original 8 frozen source t/side/truth/parent/DEFER_CANCEL/keep shadow masks, trained LightGBM text model, Python source and exact dependent F323/F324/F329 code, all F330 results, source SHA records, original hour/day/week/month quota outcomes, same-hour placebo, future-quote-causality fixture, failed F329/timeout F330 attempts and instructions. Original raw tick tape and multi-gigabyte derived source caches stay in owner-authorized source locations, not embedded; rebuild scientifically if needed from included source and SHA pin.

PRIMARY compact full scientific receipt (separate from approved filter folder):
https://drive.google.com/file/d/1Nme5Y0zbdL-ph_qR86hnRhmumKKNuwlO/view

Primary 11MB binary upload returned 403. It is **not** claimed copied to PRIMARY; raw-byte backup is stored at MT5_EXPAND.

## Hard original-model and whole-EA release distinctions
Original M-CX-01 Jan fitted same-month 450-tree/255-leaf/93-feature teacher vetoed 86,336 wrong and 5 correct using contaminated January labels/quantile selection. F330 CX Jan full-month cancels 3,979 originally wrong, only 4.6% of fitted-teacher bad veto volume; this is NOT 90% original teacher numerical equivalence. F330 decision occurs 5 seconds LATER, and its original event labels are NOT the actual after-delay bid/ask trade P&L.
Original F17 P05 owner-approved final exact event mask unavailable, so these new incremental values **MUST NOT** be added to F234+F17 approved whole-system tallies. Dukascopy July correct retention F234+F330 source shadow **67.4284% <71% per-month floor** and all 8 wrong-rejection month rates <90%. No MQL5 compiled Python parity, no true untouched authorized April test, no real transaction spreads/fees/latency, no shared-capital $100/$200 survival. G01–G09 OPEN. No promotion to APPROVED_FILTER_COMPONENTS, no demo/live EA.

## Research continuation
Prioritize further ORIGINAL WRONG-class rescue/veto architecture: controlled reactivation of F234-rejected correct signals especially Dukascopy July, with explicitly measured bad re-admission, broker/side/session/HTF conditional state and strict t+5 decision-clock, plus after-delay bid/ask hypothetical fill and shared-equity proof. Rapidly fail low-value repeated score grids, preserve positives and negatives, freeze real source tests. April sole reserved candidate of MarAprMay, unopened; all 2026 prior exposure prevents claiming prospective blind validation without distinct owner-approved new data.
