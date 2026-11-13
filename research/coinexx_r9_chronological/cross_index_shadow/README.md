# R9 experimental cross-index leading intelligence: protocol v0.1

**Status: RESEARCH-ONLY. No fitted index-aware model, no ROC-AUC result, no MT5 EA mutation, and no claim of a substitute for an actual gold limit-order book.**

Base: `gold-MUWHAHA-miner` branch `carson/coinexx-r9-path-signature-shadow-p1-20261113`, research engine originally pinned at `de3e61702759af67f93eb12cff01084789357645`. The nine unmodified Coinexx gold tick files (Jan-Sep 2026) and previous five *failed* P1 shadow runs remain authoritative; do not re-create them. Reuse the original as-of candidate cache only for past-only gold features/entry points, not as a substitute for raw gold ticks when evaluating a new trading policy.

## Provider availability / integrity as verified 2026-11-13

- Connected Trader.AI's `backtest_options_get` supports **NAS100**, **SP500**, **XAUUSD** on its *own* historical-bar engine. It does **not** list US30, JP225, EU50, DE40, FR40, UK100 and does **not** provide a native synchronized multi-asset second/tick export. Its M1 backtest date span maximum is 60 days; do not confuse that with our Coinexx historical data.
- Connected TickerLayer catalog lists **US100, US500, US30, JP225, EU50, DE40, FR40, UK100**, but `get_history` returned **403 plan restriction for index data**, likewise ETFs QQQ, SPY, DIA, EWJ, FEZ. Catalog != entitlement != historical source. These quotes have NOT been integrated into research.
- User's primary Drive `Micro_account/gold_mt5_tick_all` contains nine Coinexx **XAUUSD** broker tick logs. It is not a demonstrated synchronized cross-asset dataset.
- Candidate third-party sources to audit, not yet approved: `syncster-data/historical-market-data` (data card says 1m indices/futures, unusual license `other`, actual Jan-Sep per-symbol coverage, timestamps, and rights unverified); `axb0306/cme-futures-ohlc` (CME/TopstepX provenance, real 2026 coverage/rights unverified); `historicalfuturesdata.com` (limited free samples, full tick history possibly paid). `FutureSharks/financial-data` is **historical 2010–2018**, not 2026 training. Do not silently substitute it.

**Important:** Spot/CFD index symbols are venue-dependent and not actual exchange order books. The index-derived factor is a proxy for *risk sentiment and cross-asset price discovery*, never a measurement of XAUUSD depth, trade aggressor volume or liquidity imbalance. Nikkei cash-index JPY and European EUR/GBP FX conversions must be separately controlled; do not add unobserved forex conversion data.

## Exact causal data contract

- Every source index quote carries UTC `source_ms`, UTC `available_ms` (historical feed availability, including dissemination/network latency), origin/venue, symbol, price, original source ordinal, and `quality` flags. `available_ms` and gold tick ordering must be auditable. If acquisition timestamps are unavailable, pre-register a **conservative fixed delay** and stress-test it; do not call this a measured latency.
- Complete OHLC index bar may be used only *after* its `bar_end_ms` plus conservative publication delay. At a R9 tick at time `t`, every feature must be computed from events whose availability is **strictly `< t`**. No same-index-minute high/low/close, no hindsight forward fill, no resampling-over-gap.
- 1-minute index data do **not** establish subsecond causality or an independent 1–30-second lead signal. Use completed index bars only for **>=1-minute context** with an explicit freshness window; the real-time lead/lag test needs synchronized quote/tick or faster data. The helper intentionally returns `None` for 1s–30s returns derived from M1 bars.
- No stale prices from exchange closure or absent feed. Session/holiday, FX translation, rollover/corporate actions, timestamp resolution, and observed quote changes must be source tested. Feed availability needs an exposure timestamp; bare daily close-date is insufficient.
- Do not claim cross-broker fills. Coinexx XAUUSD Bid/Ask and broker stop/slippage/margin parity are separate.
- Log each candidate's exact R9 tick ordinal, entry time, snapshot source ordinals, per-index `available_ms` and age, learned model version and decision. Complete periods with no index coverage or zero trades remain failures for frequency gates.

`crossindex.py` is a minimal, standard-library, *as-of* multi-feed adapter and unit-tested static training-weight composite, **not** a trading algorithm. It accepts either quotes or complete bars, enforces availability order, rejects future and staleness leaks, and reports missingness. It never manufactures volume, trades or bars. Example:

```python
from crossindex import CausalCrossIndexPanel, IndexObservation, ex_ante_factor
panel = CausalCrossIndexPanel(max_age_ms=3000)
panel.observe(IndexObservation('US100', source_ms=1000, available_ms=1001, price=19000.0, kind='quote'))
# First legal gold snapshot at t>1001, never at t=1001.
features = panel.snapshot(1002)
```

For true 1-minute bar context choose an explicitly longer `max_age_ms` (e.g., 75,000) and **do not** claim that a 1m bar is a leading signal at 1s–30s; modify the feature-frequency contract before use. This module is independent from the production strategy and does not alter the original EA.

## Custom high-level mechanism: Conditional Cross-Index Transfer Pressure (CCITP)

Hypotheses only; all betas, decay/weights, state parameters and thresholds fit on PREVIOUS months and not on evaluation labels.

### 1. Real-time, lagged cross-index shocks

For index `i`, only price observations actually available before the current Coinexx gold tick are valid. Define

`r_i(t,delta) = log(P_i(t^-)/P_i((t-delta)^-))`, strictly as-of, no stale interpolation.

Normalize `z_i=clip((r_i-mu_i)/sigma_i,-6,6)` using strictly prior/training volatility. Missing, untraded or exchange-closed index means missing, not zero. Group US100/US500/US30 as a *joint factor* rather than counting them as 3 independent signals; treat JP225 and EU50/DE40/FR40/UK100 by geography and market hours. A causal low-rank shrinkage covariance/PCA filter can make groups, but train its loadings on earlier periods only.

`F_g(t) = w_g' z_g(t)`, with `w_g` regularized for correlated components. Distinct group shocks help distinguish a generalized risk-off shock from isolated US tech weakness.

### 2. Non-synchronous, directed lead-lag identification

For tick-level streams estimate a **Hayashi-Yoshida covariation across shifted non-overlapping observation intervals** on the TRAINING window only:

`C_iG(ell)=sum_(j,k) DeltaI_(i,j) DeltaG_k * 1[(T_(i,j-1)+ell,T_(i,j)+ell] intersects (T_(G,k-1),T_(G,k)]]`.

Compare `ell>0` index-leading-gold against `ell<=0` placebo. Then use a causal rolling lagged beta and shrink unstable lead effects. Estimate `ell` separately by session/regime and explicit clock uncertainty; never choose the strongest lag on held-out test months.

### 3. Dynamic hedge/correlation and tail asymmetry

An Engle-style *lagged* DCC-GARCH state (optional, useful at minute scale) is

`Q_t=(1-a-b) Qbar + a eps_(t-1)eps_(t-1)' + b Q_(t-1)`, `rho_ij(t)=Q_ij/sqrt(Q_ii Q_jj)`.

Gold's equity relationship can flip sign under stress. Fit a *filtered* (not backwards-smoothed) regime posterior `pi_s(t)=P(regime_t=s | information through t)` and estimate the index-to-gold kernel conditional on the regime. Avoid assuming that stocks-down always implies gold-up.

Use cross-quantile tail dependence or conditional exceedance `P(r_gold(t+h)>q_g | F_US(t)<q_US,regime_t)` rather than ordinary unconditional rolling correlation. Evidence from published gold/equity research finds regime-dependent and sometimes sign-changing correlation, predominantly daily rather than 1s horizons.

### 4. Transfer entropy as a falsification filter, not a price oracle

`TE_(i->G)(ell)=I(F_i(t-ell);r_G(t+h) | gold_past, other_index_past)`.

Estimate conditional transfer entropy only on historical fit windows, compare against time-block shuffled and lag-reversed surrogates; condition on common factors so correlation caused by shared news is not mislabeled as directed predictive flow. `AndrewFSee/cross-asset-lead-lag` (MIT) is a source design reference, but runs at DAILY horizon, not proof of 1–30-second XAUUSD accuracy.

### 5. Direction-conditioned latent pressure

Create `CCITP_h(t) = sum_g sum_ell pi_s(t) * beta_(g,ell,s,h) * F_g(t-ell) * exp(-age_g / tau_g)`.

This gives a signed *candidate predictor*, not an asserted probability or sign convention. Estimate `beta` using **future gold labels only on training data**, and use only past/available input features live. An HMM is optional and should be used only after a no-regime baseline; an online Kalman filter may update beta after labels actually mature. Missing group signals get missingness indicators; do not renormalize into false confidence.

### 6. Independent, executable-price action targets

For each R9 eligible timestamp, independently label BUY and SELL using future **Coinexx Bid/Ask** first-passage paths with explicit 1/3/5/10/15/30-second horizons, commissions and slippage stress. A buy's payoff is `Bid_exit - Ask_entry - costs`; a sell's payoff is `Bid_entry - Ask_exit - costs`. Observe whether favorable `+G` or adverse `-L` occurs FIRST, not whether the candle's later OHLC eventually contained the target. The labeling program may inspect future ticks, never the feature generator or online action.

Treat `BUY_FIRST`, `SELL_FIRST`, `NEITHER`, `AMBIGUOUS` and `CENSORED` separately. Report **per-side ROC-AUC on all eligible uncensored examples and opportunity coverage**, alongside multiclass ranking and calibrated net utility. Do not condition evaluation only on retrospective winner-selected opportunities.

## Five chronological experiments and hard rejection criteria

The research family is not trained until aligned index data are present. Five *different*, preregistered mechanisms should be ablated on the SAME common evaluation partitions to support paired comparisons; a moving month-to-month AUC is NOT an improvement measure.

1. Gold-only frozen causal R9 baseline plus consistent first-passage labels, trading-cost and sample/clock audit.
2. + raw lagged index shocks / one US factor + regional factors (no dynamic correlation).
3. + Hayashi-Yoshida lag-filtered transfer pressure; train-only lag selection and permutation controls.
4. + as-of conditional-tail / DCC regime switching and conditional cross-market surprise.
5. + an ensemble of the *proven incremental* mechanisms, with economically calibrated BUY/SELL/WAIT and an on-policy replay.

Use Jan–Jun for initial development, July for calibration, August and September for chronological shadow checks; **September was already exposed in older gold-only research**, so October-or-later genuinely new and timestamp-verifiable Coinexx-plus-index observations are required for a final independent acceptance. Purge labels that straddle splits and embargo at least the maximum label horizon and relevant index lookback; correct overlapping-event statistical confidence with calendar-day block bootstrap.

**Owner rule:** `ROC_AUC < 0.75 => FAIL`; `0.75 <= ROC_AUC <= 0.80 => RESEARCH ONLY`; `ROC_AUC > 0.80 => target reached, NOT deployment approval`. Report every required session/source/month and per-side target AUC with its confidence interval; avoid achieving `0.80` by removing hard examples, changing target ex post, peeking at future index bars, or selecting only one class. Zero-trade days and thin/selective high AUC cannot pass the frequency requirement. Gate account-level payoff, latency/slippage/stop requirements, stability, and drawdown independently.

Negative controls: future-bar leakage sentinel, cross-feed backward/same-ms tie checks, reverse index/gold lag, calendar-day block permutation, stale-quote false carry, duplicated US index vote, news-day/session stability, timezone/DST error, and comparisons against gold-only R9. No claim of 0.8 ROC-AUC is made now.

## Permissively licensed / research-only public implementations

- MIT: `https://github.com/KinH8/Hayashi-Yoshida-estimator` (asynchronous price lead/lag; inspect performance/clock resolution). License verified via GitHub.
- Apache-2.0: `https://github.com/Topaceminem/DCC-GARCH` (experimental bivariate GARCH/DCC). License verified via GitHub; intended older Python, adapt as necessary.
- MIT: `https://github.com/AndrewFSee/cross-asset-lead-lag` (transfer entropy, regime models, walk-forward; DAILY system, no automatic 1s validity). License verified via GitHub.
- GPL-3.0: `https://github.com/jakobrunge/tigramite` (PCMCI conditional-dependence investigation only; do NOT copy GPL code into proprietary MQL5 without license review). License verified via GitHub.
- `https://github.com/microsoft/qlib` (research architecture, not evidence of gold 1–30s target performance; check current LICENSE before copying components).
- Community warnings: `https://www.reddit.com/r/algotrading/comments/ofdvqh` describes lead/lag reversing by regime and suggests rolling cross-correlation; anecdotal, not scientific validation.
- Academic anchor: Huth & Abergel (2014), *High frequency lead/lag relationships — Empirical facts*, https://doi.org/10.1016/j.jempfin.2014.01.003, reports 60% next-midquote directional accuracy for its studied liquid/lagging instruments, **not** a gold AUC of 0.8.
- Regime anchor: `https://doi.org/10.1002/ijfe.70006` (2025 dynamic gold/equity correlation), `https://doi.org/10.1016/j.gfj.2025.101145` (2025 evidence sign-changing gold stock co-movement).

All external code/data ingestion requires separate source SHA, modification licence and attribution, as well as actual 2026 temporal coverage and original quote granularity. This research repository contains new clean-room code; no third-party implementation has been copied into the EA.

## Validation

```sh
PYTHONPATH=research/coinexx_r9_chronological/cross_index_shadow python -m unittest discover -s research/coinexx_r9_chronological/cross_index_shadow/tests -v
```
