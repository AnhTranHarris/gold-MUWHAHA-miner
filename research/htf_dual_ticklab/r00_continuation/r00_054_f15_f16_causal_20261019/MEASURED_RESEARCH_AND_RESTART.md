# R00-054 elected entry engine — FILTER15/FILTER16 causal substitution research

**Status:** original R00-054 untouched; executed teacher-free mechanisms and frozen-result ledger; RESEARCH ONLY. This checkpoint is an additive descendant of GitHub commit d7c8fdb9418468d2e5362fcfa350c885284a5136.

## Scientific improvement established — F15

The **FILTER10 same-month-fitted teacher is completely excluded from inference**. Candidate entry remains on original R00-054 quote event time and BUY/SELL side. A new deterministic veto uses the two most recent *already matured* R00-054 shadow event outcomes: older event j is eligible only after its complete original +30..32s source-quote labeling window, at t >= t_j+33,000ms. Retain the current event if both prior matured observations had a non-neutral 30s quote displacement. Past unfilled shadow signals are labeled after maturation from the observed original quote stream, independently of actual orders. Every condition is decision-time computable; no current signal outcome is inspected.

**Exact 8 source-month historical observations (Jan, Feb, Jun, Jul; Coinexx and independent Dukascopy):** original 2,574,251 signals / 1,208,071 correct (46.929%); F15 emits **2,048,235 signals / 978,629 correctly directed (47.7791367%)**, removes 296,574 original incorrect/neutral candidates and 229,442 correct candidates, with **zero ADDITIONAL failures** of R9 SYNTH 90% correctly-directed source-month hourly/daily matching windows in either broker. F15's n=2 parameter was selected from historically exposed evidence; this is an operationally causal discovery and a historical evaluation, NOT a clean blind validation or the requested 70% predictive filter.

## Large cooperative research batch — F16

Used **F09/F11/F12/F13 original-source JAN/FEB-trained independent neutral/opposite/classification specialists**, F15's >=33-sec matured shadow state, and independent rescue/veto combinations. Exactly 2,861 predeclared arm names evaluated in each of four JUN/JUL broker-month historical transfer sets = **11,444 configuration observations**; complete CSVs preserve all positives, negatives and hourly/daily misses without contaminating future claims.

Highest retrospective zero-additional-misses rule across all four evaluations: `O12_O13_t0.525_OR_F13`: **411,919 correct / 901,515 emitted (45.691863%)**, 193,693 original wrong/neutral signals rejected, zero additional matched R9 source-month hour/day failures. The comparator is original 548,099/1,231,388 (44.5107%). **The winner was selected AFTER exposed June–July outcomes, so this is a hypothesis to freeze on an earlier calibration window, not a validated transferable improvement.**

## Source/infrastructure and limitations

Original authorized SHA-pinned Coinexx/Dukascopy Jan/Feb/Jun/Jul month tapes; Coinexx UTC offset -120min JanFeb, -180min JunJul; Dukascopy UTC unchanged. Reused original R00-054 event tables and existing F09/11/12/13 derived models. Original Python tick replay engines, source bytes, event direction and labels untouched. Historical label: correctly directed if first observed original quote midpoint at t+30..32s displaced >$0.10 along predicted BUY/SELL. Not an executable position, profitable closed trade, after-cost result, or MT5 EA deployment.

No claims of 70% teacher-free accuracy or genuine blind generalization: FILTER08/FILTER10 original ~70–84% figures require target-month label-fitted teachers and cannot be used in a pretrade decision. Full source, every tested rule, exact evaluation CSV, SHA256 member manifest, and continuity handoff archived in independently verified immutable cloud copies.

**Full exact code and research package**:
- PRIMARY Drive: https://drive.google.com/file/d/1NDRcG1gl1JyLkGwhMBOeLKBUqGeM8F8y/view
- MT5_EXPAND: https://drive.google.com/file/d/194R2q9cUbXadl0o5QDPVg04iue3bwUL1/view
- File SHA-256 `4287d142a628db4ece521e04003302712bf7b53379f6c9825578b9b49607ccaf`, 415,382 bytes, ZIP CRC PASS, 28 members.
- Includes original `R00_054_FILTER15_MATURED_RESPONSE_VOTING.py`, `R00_054_FILTER16_COOPERATIVE_CAUSAL_DISCOVERY.py`, optimized equivalent execution script, frozen plan JSON, all 8 F15 month-grids, all 4 F16 month-grids, combined panels, community-source links, member hashes and full original R&D receipt. Rebuild nothing.

**Next atomic continuation:** treat F15 matured shadow quote-state as new valid at-decision input, use F09/12/13 N/O specialists with documented independent lifecycle states, optimize selection using JAN/FEB chronological purged blocks only, freeze code and thresholds before June/July historical-transfer evaluation. Genuinely blind tests require a newly authorized and SHA-pinned future month, not previously inspected March–Sept 2026. Do not tune on June/July and later declare those months blind. Complete user governing laws and investor requirements remain in force; only entry-direction veto is in scope.

**External strategy inspirations; not extra price sources:** MetaQuotes online signal filtering https://www.mql5.com/en/articles/23700 ; MetaQuotes multi-regime meta-labeling https://www.mql5.com/en/articles/22754 ; MetaQuotes purged labeling CV https://www.mql5.com/en/articles/23310 ; ForexFactory gold false breaks https://www.forexfactory.com/thread/post/15940710 ; original TradingView source-native confirmed-pivot sweep reclaim https://www.tradingview.com/script/EWSTOkEN-Liquidity-Sweep-Reversal-forexobroker/ ; Reddit meta-labeling https://www.reddit.com/r/algotrading/comments/1lnm48w/meta_labeling_for_algorithmic_trading_how_to/ . These are research hypotheses, not authoritative claims about market behavior or user-authorized historical price data.
