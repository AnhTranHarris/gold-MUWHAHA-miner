# BETA063A — Entry + Hold: shared continuation *advantage* redesign
**2026-09-29. DESIGN/HYPOTHESIS ONLY, NO NEW BACKTEST, NO PROMOTION.** Independent beta. This does NOT advance BETA063 live scientific cursor or authorize MQL5. Current live status is branch beta/CURRENT_STATE.json. The owner defers specialist HOLD+EXIT optimization until the next research cycle. August SEALED.

## Existing verified gap
BETA063 already implements five SOFT entry/hold experts TREND/SWEEP/COMPRESSION/ROTATION/PREENTRY_LEADUP, global Ridge 60% + specialist Ridge 40%, 15/30/60/90s fixed-horizon quote-return projections, Jan1–Jan9 fit / Jan9–Jan11 threshold CAL, entry side inversion criterion >-$0.06 at 30s, +5s observed continuation re-evaluation and optional 350ms pre-entry spread snap. Causal and reproducible, NOT continuously self-training. Original full seven-month retest: corrected P89 incumbent -$118080.34 /166394 trades/39708 winners/PF .2506; 5-expert -$116008.01 /162899 trades/38774 winners/PF .2353 = +$2072.33 / 1.755% less negative net vs the correct incumbent; April and June regressed. The Jan17.5d hypothetical $100k account was still negative -$7894.89 vs -$9192.59 incumbent. NOT a robust >10% full-year gain or positive net, so do not label a breakthrough.

## Specific rework: same trade-life-cycle value for new and open positions

**Change the prediction target** from separate fixed-horizon signed return/direction classification and later hold horizon to a state- and *position*-conditional net *ADVANTAGE* over doing nothing or liquidating at the current market quote. Its training labels use later actual ORIGINAL source Bid/Ask observations **offline only**, while inference inputs see original quote order no later than actual current timestamp.

State at quote t:
- closed H1/M15 global structural ownership and volatility slope; closed M5/M1 regime, accepted body break/sweep/level age/touches, confirmed pivot with right-bar completion;
- completed 15s/5s/1s tick-path efficiency, 250ms signed quote-pressure, gap, quote cadence, spread/ATR normalized to current state;
- own position=flat/buy/sell; quote-executable entry price or current liquidatable PnL, elapsed time, observed-only MAE/MFE, last level/order activation, broker/account margin/risk and queue;
- owner original Gold Hunter M1 OCO/opposite original-level rearm as bounded state *feature*, not an automatic order/position claim;
- V8/MT5 REAL/SYNTH teacher only post-hoc offline score, never model feature.

Five specialists **do not issue hard required BUY/SELL confirmations**. Each j estimates joint executable action utility and uncertainty:
1. TREND continuation while level accepted and direction stable.
2. SWEEP/FADE conditional failed acceptance/reclaim.
3. COMPRESSION expansion/escape first passage.
4. ROTATION range-edge shift + mean reversion.
5. PREENTRY_LEADUP quote hazard / signed microprice path / spread compression just before originally eligible event.
Their outputs share the same dollars/one-ounce/same-horizon relative-to-flat scale.

**Soft gating** pi_j(s)=softmax(g_j(s)/T) with regularization for expert collapse and time-window instability; global backbone + mixture, train **same objective** rather than separately fit five regression heads and manually blend flat cost weights. Require as-of state; train temperature, gate, and model scale exclusively on fit/calibration windows; preserve interpretable exported coefficients or compact tree manifest/ONNX numeric parity for later authorized MT5.

Define W_t(p) = the after-cost value of LIQUIDATING a position p at current OBSERVED opposite quote, minus not-yet-paid fees. W_t(flat)=0. Let V(s,p) be future achievable after-cost continuation value under a frozen, feasible, source-replayed policy, with already-paid transaction costs accounted **only once**. Avoid an unsupported market-impact or hypothetical limit-order fill assumption.

At a flat original eligible opportunity, evaluate only **BUY_NOW**, **SELL_NOW**, **WAIT_SHORT**, and **SKIP**, at FIRST ACTUAL qualifying future tick; a wait that expires cancels. Compute learned **incremental advantage relative to WAIT** (not merely buy-vs-sell). `A_enter(s,a)=Q(s,flat,a)-Q(s,flat,WAIT)`, where `Q(s,flat,a)` includes *both observed Ask/Bid spread + commission* and continuation value and actual future opportunity-occupancy cost. Buy/sell labels can be generated counterfactually only from actual later Bid/Ask paths under a specified safe, fixed research exit; they are TRAIN LABELS, not online oracle fill. If both positive after costs but below model-uncertainty hurdle, do not claim an actionable edge. Explore ONLY ≤2 wait clocks (e.g. 250ms/1s), not retro-picked MFE.

At an already-open buy or sell position compute `A_hold(s,p)=E[W_(t+delta)(p)-W_t(p)|s,p]+E[continuation beyond delta]-RiskPenalty-MissedOpportunityPenalty`, using a short horizon predeclared as the next *observable* forecast update. This model can prioritize persistence *within currently fixed protective $2 stop / $2 target / max allowed holding time*; it cannot silently rewrite stop/target from backtest future. It can supply the HOLD+EXIT cycle with a calibrated `V_hold` later but cannot claim to have independently optimized the exit now. Limit/risk policy outside the learned function is deterministic.

Joint action-value perspective (research, NOT assumed validated market dynamics):
`Q(s,p,a)=E[r(s,p,a,next_s)+gamma*V(next_s,next_p)] - lambda_DD*TailRisk(s,p,a) - lambda_occ*blocked_future_setup_value`
where r is realized quote-side cash increment, includes costs ONCE, and next_s is obtained only from next observed quote. A finite-horizon episode ends at actual first stop/target/timeout or risk floor. Compare Q for all allowed actions with each other; no mandatory trend/MA/sweep AND/AND rules. Direction skill and holding skill are coupled because opening a trade inherits a future holding policy, not a separate fixed 15s forward label.

## Training and leakage defenses
- Source original continuous January 1–18 12:00Z (17.5d stage 1); Jan1–9 fit, Jan9–11 calibration, Jan11–18 historically consulted validation is an exploratory diagnostic only. May–Jul all previously consulted; never call OOS. August SEALED.
- For each generated training opportunity, store exact **source entry and terminal quote index and label interval**. Purge any train label interval crossing a chronological calibration/test boundary; embargo overlap and regime/cache fit. Fit feature standardization, state-duration empirical distributions and quantiles fold-locally. Avoid previous BETA031 duration-CV holdout inclusion.
- Counterfactual target regression is *off-policy* offline fitted; on-policy sequential replay must regenerate new entry and occupied-position sequence after policy decisions. Do NOT sum per-action rewards as realized trades or use model future PnL at decision time.
- To prevent high dimensional overfit on 17.5d, start with few target features and regularized ridge / shallow fixed-depth boosted trees; compare to the SAME P89-corrected baseline. No uncontrolled infinite grid, no online model updates in tester, no self-training from one narrow source.
- Multi-objective validation: after-cost REALIZED one-position net/expectancy/GP/GL/PF, floating DD/tail loss, number of actual winning close trades, count retained, daily/wk regime stratification, per-side expert routing, cost-veto interaction, action clock and original teacher offline diagnostics. Value calibration and incremental action-vs-WAIT reliability by state decile. Pin same baseline/fee/spread/position/risk first. BETA015 exact 100k-funded equity floor NY17 4k soft/5k hard, 90k overall required before investor/funded claim.
- Owner screen remains STRICTLY >10% predeclared comparable economic improvement with winner, trade velocity, gross loss and DD safeguards from initial 17.5d; >20% target; only freeze guarded winners then Jan–Jul, acknowledge inspected months, no false blind evidence. On full seven-month replay a candidate must also beat the current P89 + BETA063 baseline in truly same-feed executable terms, not only old unfiltered E060.
- Subsequent **HOLD+EXIT** cycle learns `Q_hold` vs `Q_liquidate` using this same state representation plus actual current bid/ask/liquidation value and independent competing stop/target hazard, never hindsight best exit. Do NOT roll that second phase into the entry/hold claim.

## Community research methodological anchors
- Expected value/action-value Bellman conditional policy https://doi.org/10.1111/mafi.12382 ; optimal entry and liquidation as TWO stopping decisions with costs/stop https://doi.org/10.1142/S021902491550020x .
- Action-based Q learning and risk of overclaim https://doi.org/10.1109/ACCESS.2022.3203697 .
- Mixture soft gates/specialist routing https://doi.org/10.1016/j.procs.2026.06.366 ; these are daily stock prediction benchmarks, NOT evidence of XAU tick profitability.
- Purged and overlap-aware financial labels https://www.quantresearch.org/Innovations.htm and https://python.financial/concepts/purged-cross-validation/ .
- MetaQuotes ONNX MQL5 interface for post-owner-approved model transport https://www.mql5.com/en/docs/onnx/onnx_prepare .
- Historical research exact BETA063 model and replay: https://github.com/AnhTranHarris/gold-MUWHAHA-miner/blob/beta/research/BETA_063_FIVE_SOFT_EXPERT_ENTRY_HOLD_SHARED_CONTINUATION_VALUE_SPEC.md .

**Checkpoint disposition:** DESIGN SPECIFICATION ONLY. NO NEW TICK BACKTEST OR MODEL FIT IN THIS DOCUMENT. No approved BETA MQL5 code, no result guarantee, August SEALED. Keep experimental negative work in existing BETA Research Journal, compact user-facing answer should not misrepresent a proposed model as a discovered positive-alpha breakthrough.
