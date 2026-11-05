# H1V2 / R9 v2 H9 — high-precision correct-side hindsight teacher
2026-11-05 CT. NEW additive scientific child, never a live-EA mutation.

## Inherited immutable source basis
- GitHub R26 frozen baseline: carson/h1v2-r26-broker-asymmetric-opportunity-hazard-20261104, HEAD 22e0318f033f9946ad199815ed1946d049c399bb.
- Original full forensic V00–V06 audit, R27 V08, R28 append-only R28-0000..0008 preserved.
- Original raw source January DUKASCOPY_RAW 2026-01, SHA256 d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5. This source had 9,135,062 ordered quotes in frozen R0 baseline.
- H8 full 1,512,178 candidate first-observed 1-second signal ordinals, first-100ms fill ordinals and all first 60-second labels. January H8 ZIP SHA 84e443c3bb490e3f183d37ab85432356e4ccc394507a438f0a3389383d72592f.
- R9 original source-aligned Jan SYNTH reference: 27,980 entries, 26 active UTC days, 480 active hours, 1,878 active quarters.
- Separate QUOTE-price RAW (0.001 USD/XAU) from cash-account USD. Coinexx contract size, margin, dealer execution, slippage and vintage news remain UNVERIFIED.

## Hypotheses preregistered before any new model/experiment
- H9A early side purity: at the real 100ms-delayed fill, an initial +0.10 signed midpoint favorable mark must occur by 15s and before an adverse -0.25 signed midpoint mark. This is a future-only teacher label, not an as-of entry signal.
- H9B executable precision: same side must hit +0.10/+0.30/+0.50 REAL Bid/Ask liquidation-price net, inclusive of original H8 0.02 quoted-price fee, first before spread-adaptive adverse barrier and strictly before 30s. Reuse original H8 firstpassage labels by ordinal/time, no fresh refitting.
- H9C aspiration: extend the original source-exact label family to +3.00 and +5.00 quoted-price net strictly before 30s after original 100ms first observed fill, with H8 spread-adaptive loss stop, observed gap >15s censored. No artificial quote interpolations.
- H9D negative-control: compare the same horizon targets without the early-side purity filter and quantify selection reduction. H9 early-purity acceptance is allowed to reduce frequency; do not weaken threshold to rescue throughput.
- H9E risk: record worst observed pre-exit liquidation-price net (MAE), elapsed ms, stable source quote ordinals and position nonoverlap. No zero-marginal drawdown inference from a winner-only oracle.
- H9F correct signal vs incorrect signal must be different labels: TARGET_FIRST_STRICT30, WRONG_DIRECTION_FIRST15, STOP_FIRST, TIMEOUT, CENSORED, UNFILLED, WAIT. The teacher may select only true target-first winning candidates; report the rejected and wrong-side population, never count teacher-selected precision as proof of forecasting.
- H9G compute full Jan UTC minute/15min/hour/day including zero-reference periods. A positive period means realized source quote PnL >0, not a volume or directional-correctness proxy. For R9-reference-active periods missing trades count as nonpositive. Target day 100%, hour >=90%, quarter>=80%; R9 trade counts tracked independently, both as volume pressure and reference; no quota as feature.
- H9H keep multi-horizon future labels (H5/H10/H15/H30) and as-of multitimeframe/multiregime candidate state proposals separate. H9 first run teacher only; never claim Bayesian, Hawkes or NP fitted before actual model/test receipt. No hindsight feedback into causal state features.

## Exact scientific firebreak and execution contract
1. Source ordinals are stable original input order including same-ms rows; reject source-order/shape SHA mismatches. Raw ticks from Dukas cannot confirm real Coinexx dealer fills.
2. At signal ordinal i, fill at original H8 first observed actual quote at least 100ms later; source gap/censor remains hard rejection.
3. BUY liquidation net in 0.001 USD quote units: bid_exit-ask_entry-20; SELL: bid_entry-ask_exit-20. Never use midpoint as cash payoff.
4. Stop barrier original H8: max(500, fill_spread+20+250) raw, reject if >1500 raw. First adverse before target => incorrect (never cherry-pick later recovery). This is a research stop, NOT an approved live stop.
5. Initial correctness: first favorable signed 0.10 midpoint threshold within 15s at actual quote ordinal, before first -0.25 signed adverse midpoint mark; both may be at same quote on jump, mark tie cautiously.
6. Exit time t_exit-t_fill <30000ms. Nonoverlap by actual source observed quote ordinal/time globally across quarter/hour/day boundaries; no positions stacked.
7. Positive-oracle net is by construction selected winning trades; all period pass rates are non-predictive upper bounds. Mark whole program HISTORICALLY EXPOSED / FUTURE_PRIVILEGED / NO OOS / NO EA PERMISSION.
8. Preserve source identity, all losses/errors/negative experiments; append checkpoints, do not overwrite previous logs. Full negative evidence in MT5_EXPAND; only actual successful experimental outcomes are eligible for short chat reporting.

## Code scope
New bounded source reader/teacher study only. Do not mutate original H8 R28 R26 executable source or repaired R9 v2. Reuse original H8 labels and R9 period table. Source data February/June/July and MT5 must be independently acquired and pinned to test all eight source-months. Do not generalize Jan findings to all four months or both feeds.
