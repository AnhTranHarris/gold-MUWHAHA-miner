# R9 January 2026 Aalen–Johansen cause-specific cash utility chronology pilot

**Research-only.** Identical original Coinexx January raw SHA256 and frozen R9 entries as documented in R9_JAN2026_ORIGINAL_COINEXX_REAL_TICK_CASH175_PILOT_20261113.md. No additional raw archives, indicator libraries, model fits or EA edits. Results come from an independent compact 32,179-original-trade January source-ordinal first-cause table, **not actual broker fills**, and are NOT a new on-policy Python R9 portfolio simulation.

## Predeclared, explicitly illustrative economics

Original 0.01 lot; USD account ASSUMED (not observed); K=1.0 account cash per $1 XAU quote movement ASSUMED; C=0.20 account cash for roundtrip commission/slippage ASSUMED; goal = +1.75 net account cash; liquidation-side price target = 195 cents from actual ASK/SELL BID. All source names, quote positions and scenario assumptions are pinned by the accompanying January pilot receipt.

## Earlier train → later evaluation on the SAME historically exposed month

- Training original R9 entries strictly before source-clock January 16, 2026: **15,726** positions.
- January 16 and January 17 entry days omitted as a conservative TWO-DAY calendar embargo. Neither training nor test includes them.
- Evaluation original R9 entries on/after source-clock January 18, 2026: **14,932** positions.
- Only as-of entry metadata used for model contexts: original source-native R9 trading-session code and quote spread bands, with original research cutpoints **15 and 25 cents**.
- Aalen–Johansen cause-specific risk-set incidence with 10-second gap right-censor; cumulative probability by 1/3/5/10/15/20/30 sec. Cause-specific cash payoff means TRAIN ONLY. Cash-risk penalty = 0.25 × observed bottom-five-percent conditional loss amount. No recalibration using evaluation labels.
- Minimum group size 100 and maximum train censor share 10%; sparsity/censor abstention, no invented probabilities for other contexts.
- **8** observed training context keys; **4** train-eligible keys with adequate evidence.

| Frozen chronological result | Value |
|---|---:|
| Goal-first TRAIN count | **24 / 15,726** |
| Goal-first EVAL count | **69 / 14,932** |
| EVAL original positions with eligible group and observed payoff | **14,795** |
| EVAL positions whose TRAIN-only risk-adjusted utility is positive | **0 / 14,932** |
| Mean frozen TRAIN-only *unpenalized* predicted account-cash payoff on comparable EVAL | **−0.391906** |
| Mean actually observed early-goal shadow payoff on same EVAL subset | **−0.382220** |
| Mean TRAIN-only **risk-adjusted** predicted utility on comparable EVAL | **−0.658459** |
| Mean original R9 baseline account cash in all EVAL under scenario | **−0.381757** |

The four eligible TRAIN-only context risk-adjusted utility scores were:
- session 0, spread band 1: −0.667685 account cash
- session 1, spread band 1: −0.643173
- session 2, spread band 1: −0.647506
- session 3, spread band 1: −0.667086

Global Aalen–Johansen TRAIN cumulative goal-before-original-exit incidence at 30 sec = 0.001527. Retrospective EVAL incidence at 30 sec = 0.004621; this is an observed shift in event prevalence, NOT an unexposed prospective test or proof of model calibration.

## Mathematical interpretation and go/no-go

- Current R9 original entry + unchanged stop/trail/timeout dynamics have NEGATIVE net cash scenarios across every adequately sampled session/spread bucket in this January subset.
- A simple utility>0 policy would select **ZERO** entries in the EVAL and destroy throughput. That is an economic warning, not a safe production entry policy.
- The unpenalized predicted payoff is close to the observed shadow payoff in aggregate but this single exposed January split cannot validate future risk calibration, conditional hazard accuracy, or broker-dollar P&L. Most target-first events are so rare that confidence intervals and later-month evaluation matter.
- The earlier approved 155-feature LightGBM probability was **not injected** as a false chance of the 1.75 cash goal: it predicts a DIFFERENT 5-second fixed-barrier event. It may later be treated only as a causally joined entry-time explanatory covariate after exact source-ordinal score parity.
- This Aalen–Johansen estimate describes **original R9 trade lifecycle**, not a better counterfactual exit policy. The NEXT Python phase must independently replay alternative R9 entries/holds/exits under the FULL chronological quote stream, preserving original same-minute rearming, after-cost trade occupancy and risk governor capacity. It must train on earlier dates and score later dates, with all trade count and net cash/hour metrics, without a new tick engine.

**Promotion status:** FAIL for a positive utility+high volume combined gate on this January pilot; do not change MQL5 or loosen gross-loss limits. This is a necessary early diagnosis for genuinely advanced competing-risk utility research.
