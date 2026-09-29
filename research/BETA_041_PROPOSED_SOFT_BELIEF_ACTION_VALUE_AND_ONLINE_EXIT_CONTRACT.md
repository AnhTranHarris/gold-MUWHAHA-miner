# BETA041 — PROPOSAL, NOT EXECUTED: continuous state belief, action value and online position stopping

**Source date:** 2026-09-29. **Status:** exact experiment specification for NEXT bounded unit, **NOT a completed market backtest**. Source branch `beta`; authoritative live status `CURRENT_STATE.json`. Owner directive removing further *stacked technical confirmation gates* is permanently recorded at `research/BETA_040_NO_STACKED_CONFIRMATION_OWNER_DIRECTIVE.md`. Prior entry/hold/exit initial research attention remains EQUAL, with state-conditional module weights allowed. No authorized official MQL5 EA. August SEALED.

## What actually motivates this design
BETA040 executed the unfiltered side+entry-time-selected-exit prototype with 60 causal source features and 6 actions. On its Jan11–Jan18 historical test, BETA040 **global six-action** reduced shadow loss 18.334%, but preserved **21.656% of same-incumbent winning event identities**, flipped approximately 4,400 of 6,473 event sides, and reduced *SELECTED* same-side SYNTH matches 1,114->444. Four-state blend was 16.908% less loss /19.649% matched winner identity /445 teacher matches. Every model still lost money, and BETA040 was correctly NOT promoted; the exit policy was decided once at entry, not re-assessed each observed tick. This does not establish actual positive future-executable expectancy. Historical 11.881% BETA039 sign-corrected rolling spread veto is diagnostic OPTIONAL ablation, not a compulsory confirmation filter; its full Jan–Jul after-cost net remained -$118,080.34 and funded floor breached in Jan.

## ONE recommendation: no veto committee; cost-and-risk-adjusted continuous action-value policy
Market context is an as-of-time **probability distribution**, not an AND-chain. Build a low-dimensional causal latent state belief:
```
P_t(z) = P(UP_TREND, DOWN_TREND, RANGE, VOLATILE_BREAK, TRANSITION | observed quote events through t)
```
Features are always source-index and end-of-interval timestamped: 250ms/1s/S5 quote path, spread and source quote age; S15/M1 impulse/efficiency and volatility; confirmed completed M1/M5 structural levels/touch age; completed M15/H1 trend/volatility ownership; observed quote cost and 5/15s quotes. Existing BETA026 quote_pressure1 is ALREADY entry-side signed; do not multiply by side twice. When no observation exists, retain unknown/uncertain state rather than fabricate no-tick OHLC.

**Entry** takes values rather than confirmations: for each of BUY/SELL/FLAT, estimate costed distribution for near-term possible PnL *with the projected downstream stopping policy*, including spread/fee and opportunities blocked by being in a position:
```
Q_t(a) = sum_z P_t(z) * E[PnL_after_cost(a, future_stop_policy) | F_t,z]
         - lambda_tail * ExpectedShortfall_downside(a)
         - lambda_occupied * FutureOpportunityCost(a)
choose argmax_a Q_t(a), subject to NON-NEGOTIABLE broker validity, real quote age, 1-position,
volume/margin, and BETA015 funded daily/equity limits.
```
Cost and risk checks are legitimate constraints, NOT technical bullish/bearish confirmations. FLAT is the economic opportunity to not enter when net expected benefit is negative. Uncertainty penalties must be fitted/calibrated ONLY on training sequences. Maintain R9 direction as a soft Bayesian/log-odds prior, not a hard rule and not an indiscriminate inversion target; log each changed side and original-event winner identity.

**Hold/exit** changes at each new ACTUAL observed executable quote after fill. A competing-risks model estimates P(target-before-stop over Δt), P(stop-before-target over Δt), surviving regime/run length (optional explicit HSMM) and post-entry quote drift under each action. Only the **first decision tick** can act. Sequential comparison:
```
V_exit(t) = current valid opposite-side executable Bid/Ask liquidation after exit costs
V_hold(t) = E[future stopped/trailing realized payout | F_t,current position] 
            - risk_charge - occupied-capital opportunity charge
V_trail(t) = E[frozen monotonic real stop/trailing payout | F_t]
exit = argmax(V_exit,V_hold,V_trail), with mandatory catastrophic/BETA015 risk guards
```
No oracle future MFE/MAE, no retroactive exits, no stop/limit execution at a quote not actually available. Dynamic hold policy and entry are fitted/tested together, but run *entry-only*, *lifecycle-only* and *combined* ablation against the SAME one-position source and same registered opportunity IDs; do not sum standalone sleeve profits.

## Four initial PARALLEL, qualitatively distinct research candidates
A. **Prior-constrained global side+exit utility:** noncontextual action regression with side-prior strength and utility uncertainty; compare unchanged R9 side vs soft side override; baseline unchanged one-position L30.
B. **Belief mixture-of-experts direction:** state posterior **soft weights** global/state experts; preserve total setup count, test calibration, no technical veto, late flip behavior and identical-event winner identity.
C. **Causal after-fill competing risks:** keep original R9 side & original entry clock, now re-estimate Hold / Stop / Trail / Close once per new actually observed quote, including early probation vs runner persistence. This isolates entry-independent HOLD/EXIT value.
D. **Belief + dynamic stop joint policy:** combine A/B direction and C position decision; ablate HSMM residual-time state and BOCPD change probability as *soft context*, not mandatory trade disqualification. This is joint training / sequential replay, never hindsight-optimal exit.

Each family use at most ~3 preregistered reasonable neighbors, including a strong R9 direction-prior vs weak prior; fit January opening contiguous block only, temporal embargo >= largest outcome horizon, compare late January FIRST 17.5 days (already inspected, never 'blind OOS'). Overlapping paths embargoed; no event-time label leaks. Reasonably preserve first-cycle R9 E060 baseline as audit clock, but design a separate M1/V8 minute-order opportunity generator for subsequent source lineage experiments after matched equivalence. Gold Hunter V8 original stop bracket/rearm remains forensic clue, not verified hidden signal.

## Falsifiable advance gates and explicit due diligence
- SAME Jan01 00 UTC – Jan18 12 UTC original 4,205,709 Dukascopy bid/ask rows and exactly registered 14,174 R9-like first-cycle origination event cohort (source parent baseline). Different model may skip on negative *economic value* (FLAT); count every declined origin, missed source-original winner and lost future opportunity.
- Predeclare primary KPI **realized chronological after-cost full-position net loss reduction >10% vs matched same-window E060 30s/$2stop/$2target**, using same contract size and commission, AND incumbent winning **same-event identity >=90%**, original total win/trade count safeguards, gross realized loss and max floating-equity drawdown no worse, no material capital floor impairment. This is strict gate (>10%), owner desired stronger target >=20%. High relative win rate on tiny handful of trades explicitly rejected.
- Preserve separate 3s/5s/15s executable markouts, selected historical R9 teacher matches and full unpaired original logger sample where actually verified, each clearly named. Absolute correct and same-event winning identities should not be silently conflated.
- For candidates passing initial bounded 10% gate, FREEZE code and parameters, then replay all 57,527,562 original Jan–Jul ticks and compare full BETA015 funded $100k 0.01lot one-open-position $4k soft/$5k hard daily limit $90k absolute floating equity floor/NY5pm reset; don't credit untradeable trades after floor. No initial screen winner => **STOP**, report rejection, don't claim long run.
- Jan–Jul already inspected in earlier work: NOT independent unseen OOS. August SEALED until OWNER explicit permission. No official MQL5 EA code until separate owner approval. Initial BETA005 original feature grid/count consistency passes but full 17-layer materialized parity is outstanding; report this limitation.
- Reproducibility artifact must include original quote source SHA, exact event source ordinal/time, feature as-of timestamps and sign conventions, model scaler+coefficients/optional portable ONNX manifest, independent Python numeric parity QA, first observed executable quote and position/account ledger, scripts+output SHA, calibration/holdout windows and financial and teacher metrics; original source user monthly gzip remains external and hashed.
- MT5 eventual portability: terminal `OnTick` can coalesce queued events: always source-reconcile `CopyTicksRange`, preserve same-ms source order and mark price staleness, use `OnTradeTransaction` fill/exit reconciliation; port source-disclosed models via MQL5 native numeric arrays or ONNX. Explicit implementation below, not claimed compiled.

## External public-source logic, NOT validated alpha
- MQL5 BOCPD causal change posterior, no directional signal: https://www.mql5.com/en/articles/23482
- Explicit duration HSMM and Python-to-MQL5 numeric manifest https://www.mql5.com/en/articles/24460 ; same article's XAUUSD M5 reported tested strategy was **NET UNPROFITABLE**, so don't transfer a profitable claim or presume duration will make gold positive.
- Source-auditable MQL5 multi-regime trading architecture https://www.mql5.com/en/articles/17781 .
- MetaQuotes ONNX inference https://www.mql5.com/en/docs/onnx/onnx_mql5 ; NewTick queue https://www.mql5.com/en/docs/event_handlers/ontick .
- Chronological training protocol purged walk-forward and multiplicity caveats https://github.com/Iftekhar-mobin/quant-market-regime-research . Software license and data provenance audit required if porting any public code. Strategies here are independent clean-room formulations.

**STATUS: PLAN ONLY. BETA040 150QA completed no promotion; BETA041 results do NOT EXIST yet.** Maintain next active science unit BETA041; do not mutate `last_verified_durable_unit` for planning work.
