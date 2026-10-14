# R9 OVERFIT → RSI/ATR causal teacher investigation — Jan–Jul 2026
**Owner request**: Deliberately overfit historical R9 teacher/student ticklog as a *research laboratory*; reverse-engineer contextual RSI, ATR, session, intrasecond geometry, market state, and subsequent excursions; mutate reconstructible mechanisms and test independently on original Dukascopy Bid/Ask, with heavy daily-net and daily-trade-count targets.

**Scientific disposition**: DIAGNOSTIC OVERFIT / RESEARCH ONLY / **NO APPROVED EDGE**. Existing delta-A-alpha branch preserved, CURRENT_STATE J0183 remains unadvanced; August SEALED; no live trade/MQL5/EA changes.

## Original confirmed inputs and pairing
- **R9 OVERFIT_TEACHER_STUDENT Drive archive**: https://drive.google.com/file/d/1BuH9_1Zp_SEhvf5RlPsvACggJeKM9Fjw/view ; within https://drive.google.com/drive/folders/1DcF0rW9P9UDZjfyWXxX7n7T-2v96hBQC . The original is a 7-member gzip tar, SHA256 `4a09b2b3af81b24f7ba4f48eebc6c32fcab664102de8edbe078f48baf449c4fb`. Contains 169,889 paired REAL/SYNTH trade records Jan–Jul by counted month: 21,395 / 26,512 / 31,974 / 24,596 / 21,910 / 24,318 / 19,184; 33 source fields including REAL entry time, direction, ATR, spread, S1 displacement/efficiency/turns, REAL future MFE/MAE, paired SYNTH future MFE/MAE/duration, side agreement.
- **Critical pair uncertainty**: REAL and SYNTH timestamp median difference 10.808 seconds; 72.08% differ >5 seconds, 8.63% >30 seconds; pairs are minute-scale *diagnostic labels*, not same-exact-price order or guaranteed teacher action.
- **Original Dukascopy real quotes**: 57,527,562 Jan–Jul ordered UTC-ms records. All synthetic RSI/ATR indicator features are computed from prior fully completed BID S1,S5,S15,S30,M1,M5 bars at the R9 REAL entry instant, no filled bars, RSI(5,7,9,14,21) Wilder, ATR(7,14,21) Wilder. The source R9 REAL broker ATR is retained separately. PYTHON ATR may not have exact MT5 iATR smoothing/quote feed equivalence; both feeds' dollar spread geometry requires broker precision parity before conclusions.
- Research label: **historical SYNTH-high** = hindsight max favorable move >= $1.20 AND MAE <= $0.50 AND historical SYNTH hold >=8s; 37.5% positive. **REAL historical favorable** = REAL MFE >= $0.90 AND MAE <= $0.50, 3.73% positive. Historical paired teacher-agreement is separate. Labels are FUTURE ORACLES; **none enters executable trading**.

## Prespecified split / retrospective classifier
Train Jan–Mar; inspect Apr–May; month-ordered June–July assessment (historical known data, NOT untouched final market OOS). Fixed gradient boosting (max 75 iterations, 7 leaves, max depth 3, min 500 observations per leaf, L2=3), four predeclared feature families; AUC = ranking discrimination, **not trading PnL**.

| June–July historical target | R9 REAL as-of source features | +RSI features | +ATR features | + RSI+ATR |
|---|---:|---:|---:|---:|
| SYNTH-high hindsight label | .6368 | .6365 | .6368 | .6364 |
| Paired teacher direction agreement | .5850 | .5837 | .5866 | .5855 |
| REAL future favorable excursion | .5832 | .5819 | .6088 | .6101 |
| REAL favorable excursion AND teacher agreement | .5609 | .5611 | .5970 | .6025 |

- Among ATR features, M5 ATR(21) ranked highest for future REAL favorable excursion: univariate June–July AUC=.6031 versus ATR14 M5=.5982 and ATR7 M5=.5862. Higher volatility supplies more *potential movement*, **not direction or net profit**. Univariate RSI top feature RSI14 M5 AUC=.5392; RSI7 S5 30/40/50/60/70 bands show historical high SYNTH rate ~37.4–37.9%, near-useless discrimination for this target. Adding RSI to the existing R9 entry state did not generalize profit.
- Session/geometry stratification on **June–July pairs within <=5 seconds timestamp offset** (11,757 total; 1.97% REAL-favorable): Sydney/Tokyo overlap 3188 pairs, 2.51%; NY-only 2902, 1.55%; London-only 2647, 1.70%; London+NY overlap 2073, 1.93%. ATR21 M5 LOW regime 7405, 1.57%; NORMAL_HIGH 1111, 4.32%; HIGH 107, 5.61%. These are **different sample bases** and exploratory event rates, not executable edge or daily revenue. Post-hoc tiny cells should never be promoted. Session bounds DST-aware (local Sydney, Tokyo, London, NY).
- Definitional warning: retrospective `ATR14_S15 / (entry_spread_r*0.01)` ratio mixes independent **Dukascopy ATR** with original **R9 Coinexx spread proxy**. This is only contextual cross-feed diagnostic. Future funded tests must calculate the actual *same-feed* Dukascopy ask-bid spread at each candidate order/fill, commission, timing, slippage, broker contract.

## Teacher-conditioned original Dukascopy independent funded falsification
Eight test variants, separate $100 and $200 initial 0.01-lot assumed one-ounce accounts, Jan/June/July chronological original Bid/Ask replays, >=250ms observed-tick execution, assumed leverage 1:500, 0.20 USD roundtrip modeled fee, one physical position, 60%-initial-equity *new-entry halt*. Original R8 source is a Python approximation (not literal Coinexx MT5 parity). M5 ATR21 threshold policies use Jan–Mar empirical median 7.644435 USD and P75 10.846470 USD, *not* retrospective selection of winning trades. No future teacher features passed to executor.

| Account $100 | Jan net / closes | Jun net / closes | Jul net / closes |
|---|---:|---:|---:|
| R8_APPROX_CONTROL | -25.612 / 63 | -39.638 / 73 | -24.135 / 57 |
| R8_PLUS_ATR21_M5_MEDIAN | -3.944 / 16 | -19.737 / 34 | -3.250 / 2 |
| R8_PLUS_ATR21_M5_P75 | -1.797 / 9 | +.150 / 1 | +.000 / 0 |
| R8_PLUS_ATR21_M5_RSI5_ALIGNMENT | -.230 / 15 | -17.510 / 26 | +.240 / 1 |
| RSI5_REIGNITION_CONTROL | -40.032 / 49 | -39.456 / 42 | -40.570 / 60 |
| RSI5_REIGNITION_ATR21_M5_MEDIAN | -40.160 / 28 | -42.915 / 40 | -39.610 / 38 |

Two additional R8+RSI5 combined cases also lost cash all three months. **Not a breakthrough**: stringent ATR filters protect balances by vetoing nearly all trades. A single +$0.15 close or a 0-close $0.00 month FAILS daily profit + velocity.

## Distinct testable strategy mutations inspired, NOT validated
1. **Dual-horizon trend state**: completed M5 ATR21 as movement budget, completed S15/S30 structure as directional *context*, S1/S5 RSI momentum slope/cross acceleration, same-second observed bid/ask R8 sweep/continuation confirms actual side. Compare three separate source families vs flat control; no hard-coded universal RSI/ATR direction.
2. **Net-executable adaptive virtual grid**: frozen completed S5/S15 ATR7/14/21 rung spacing scaled against actual same-feed quoted spread, $0.20 fee, slippage stress and timing. Regime defines rotation-vs-ignition states. One 0.01-lot physical position initially, *no averaging down*; shadow simultaneous opportunities separately.
3. **Causal exit-hazard controller**: prior-completed S1/S5 RSI slowing plus tick-executable accumulated favorable price, local ATR state, gap-safe stop. Train on *closed* teacher outcome paths but do not use future best MFE/best exit; compare to original R8 cost-protect, all costs and hours/daily volumes.
4. **Session-aware but not session-fitted router**: session DST conversion, pooled shrinkage for per-session thresholds, min samples, last-N-decayed outcomes from already closed trades. Require profitability in adjacent months, not just high-label correlation.
5. **Paid execution queue/economic opportunity frontier**: score every independent source's after-cost entry opportunity at time, account for fill/latency, slot occupancy, missed candidates and drawdown; optimize actual positive trading days *jointly* with paid daily closes rather than optimizing signal frequency in isolation.
6. **Teacher/Student contamination guards**: paired teacher future fields allowed only on offline label table; student features only time-as-of; alternative future labels must be defined before cross-month checks. Rebuild exact coinexx R9 point, spread, costs, ATR platform parity before any claimed cross-feed geometry translation.

## Evidence packages / recovery
The exact-source archive `R9_TEACHER_RSI_ATR_20261014_EXACT_RESEARCH_BUNDLE.zip`, SHA256 `b3e4a447270e4d90dc87c1cb3e511256f85aa3cab7d28d968caf189871501ca0`, is a verified conversation artifact, **not asserted to be on GitHub or Drive**; contains 46 members: original teacher archive, seven aligned feature tables, all exploratory scripts, classifier results, regime tables, three months funded replays and ledgers, report and manifest.
`R9_TEACHER_RSI_ATR_20261014_FULL_RESEARCH_REPORT.md` is the readable full report.

Scientific gate: **NO tested variant meets robust positive daily realized NET AND high daily funded trade count with $100/$200 cash, or investor PF >=30 / active-hour >75% requirements.** Preserve original source and all failure records; owner approval required before changing official EA.