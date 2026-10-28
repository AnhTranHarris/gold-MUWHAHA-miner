# F401-R97/R98 — XAUUSD HTF original-source economic action-space and bid/ask quote-volume falsification

**2026-10-28; EXISTING FILTER08 M-DK-01; RESEARCH ONLY, UNAPPROVED.** Freeze: previous complete R96 504D multi-specialist test negative; engine PIN `ca4b58aec597174b6f6d18ab2f36cba6836e4f4c` untouched, PRIMARY read-only and MT5_EXPAND owner-approved /02 unchanged. Original owner 21/39 historical-research signoffs, individual M-DK-01 and G01–G09 OPEN. This is NOT an original R9 filled-order replay, full-account performance, real executable pending-fill ledger, full G09, or future blind OOS. Results show an original-source *opportunity* counterfactual, not a deployable system.

## Reorientation: actual research design defect addressed

F401 R94–R96 repeatedly appended features to a same-timestamp `keep/veto` prediction objective. R97 changed the **decision set** and the **supervised target**: original FILTER08 immutable event at t0 becomes a HYPOTHETICAL NEW NEVER-SUBMITTED order opportunity with mutually competing actions: first available market ask/bid, 45-second passive quote-touch with adjustable quote-spread discount, 45-second stop continuation quote trigger, 5-second later directional reconfirmation, or no order. Future quote-path label is an entry/exit branch payoff; learned action selection uses only pre-t0 information. The intent is NOT original R9 OrderSend, and R94 already proved the actual R9 logs cannot be joined to FILTER08 event IDs merely by nearest timestamp. R98 independently identified genuine additional quoted-volume CSV columns omitted from prior static models and tested whether these supply independent economic-passage information.

## Exact original pins and event population

- FILTER08 byte-identical original ZIP 51,096,243B, SHA256 `7edaddf30f3a19cafd364a270333c6f87962960233f9d10ccbfb6e2a3b23b2ad`.
- Original Dukascopy January full quote archive gzip SHA256 `d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5` — 9,135,062 source quotes, 344,037 immutable original events.
- Original Dukascopy February full quote archive gzip SHA256 `ed3b3545c990c88d78519594c17c8915b0f679adcb0a94920ba7524f1f6d5c5d` — 7,538,339 source quotes, 324,582 immutable events.
- Dukascopy original UTC, original side and three-class source outcomes unchanged. Pre-event feature watermark excludes **all** quotes in original event UTC second and any later source quote. Hypothetical action first observable quote strictly AFTER original t0; delayed decisions have their own actual as-of time. Future labels may use future quote prices for **training targets only**. Five independent deterministic mutation/invariance tests PASS.

## R97: actual independent counterfactual path evaluation, NOT a benchmark success

Exact bid/ask quote paths, 180s maximum exit time from original t0, +$4/oz target / −$1.5/oz stop with first quote touch, illustrative $0.20 round-trip charge per 0.01 lot assumed 1 oz and no latency. Market first quote, passive limits and stop-entry quote touches **do not** model queue priority, partial fills, contract size certification, actual broker execution, stop slippage, account overlaps, margin, or realistic ruin. Every source event is scored separately; summing branch PnL does not produce an account equity path. These are not predeclared broker execution parameters or R9 original exits, merely one falsifiable research environment.

| Split | Market-now mean net per opportunity | JAN-fitted conditional action selector mean net on filled | Conditional selector filled events | Future-known best-action oracle opportunity net (unattainable diagnostic) |
|---|---:|---:|---:|---:|
| JAN CAL 68,807 | −$0.5262 | −$0.5341 | 4,807 | +$66,294.94 |
| JAN VAL 34,404 | −$0.6079 | −$0.6271 | 2,760 | +$39,377.67 |
| JAN TAIL 34,404 | −$1.4088 | −$0.6193 | 991 | +$28,123.16 |
| FEB exposed transfer 324,582 | −$1.1541 | −$1.0337 | 7,244 | +$206,488.02 |

**Key distinction:** Future-known oracle selects the profitable action only **after observing future prices**, so it is useful only to show hypothetical action opportunity exists; it is not exploitable at t0. JAN-fitted conditional selector did NOT convert this oracle opportunity to positive after-cost actual simulated entry; it skipped the vast majority of original signal opportunities, including correct-labeled signals. This exact 29-feature action-selector implementation is **not promoted**. It does not prove all action-space methods fail.

## R98: actual newly audited numeric volume columns, not invented trade volume

- Original Dukascopy raw CSV **does have nonconstant** `ask_volume` and `bid_volume` alongside timestamp, ask_raw, bid_raw. January has 209 unique ask values and 163 unique bid values; February 145 and 118. January quote-side volumes match exactly only 62.62% of source records, February 57.83%. This is a real, previously UNUSED input channel in this local research work. Units and relationship to deliverable transaction liquidity are unknown. Never call it exchange traded volume, true book depth, firm available size, or certified Coinexx orderbook volume. Broker-portability still needs explicit investigation.
- Built 80 numeric pre-event quote-volume features (bid/ask current indicative quantities, side-relative imbalance, quantized size state and 8/32/128/512-quote multi-horizon size-change/risk interactions), compared with identical 29D base as-of source context, identical Jan first60% FIT, Jan next20% CAL, Jan80–90% VAL, Jan90–100% shadow, Feb entirely frozen exposed transfer.
- Target **NOT** original FILTER08 correct-veto: hypothetical market first-passage +$4/−$1.5 within 180s and $0.20 assumed fee, labeled price-executed positive vs other; predictions from identical 160-round,127-leaf LightGBM with 120-child minimum and L2=22 for exact matched ablation.

| Frozen economic-label AUC | Prior 29D context | +80 quoted-volume features | Difference |
|---|---:|---:|---:|
| JAN CAL | 0.52931 | 0.52501 | −0.00430 |
| JAN VAL | 0.53485 | 0.54011 | +0.00526 |
| JAN TAIL | 0.74450 | 0.75109 | +0.00658 |
| FEB exposed transfer | 0.59559 | 0.59797 | +0.00237 |

At the JAN CAL-frozen q=.95 economic selection threshold, actual simulated net for selected hypothetical market fills remained **negative**: JAN VAL −$0.5789 without volume versus −$0.5959 with; FEB −$0.8289 versus −$0.8547. This is a targeted source-volume **ablation**, not a claim to validate the full latent volume-state hypothesis. It establishes that numeric L1 volume exists in authorized source but does not give sufficient standalone economic edge in this exact test.

## Strategic decision, not another threshold grid

**RETIRED as tested variants:** Static R94–R96 keep/veto regressions; R97 29D direct action value regression under fixed simplistic bracket; R98 economic positive vs negative LGBM with simple quote-volume features. Preserve every negative result, no same-test retuning, no model promotion.

**NEW research category** for future original-source development is a structurally conditional ensemble of *genuinely different alpha engines and action controllers*: a structural-pullback entry discount engine, independent displacement-continuation specialist, liquidity-sweep/reclaim specialist, quote-renewal/session-pressure specialist and correct-opportunity rescue guard. Use prior experimentally measured structural successes only after original source readback; never turn narrative recalled PnL into formal evidence. Shared-capital arbiter must decide among market/limit/defer/standdown with stochastic branch costs and 0/250/1000ms latency on actual broker contract. Rather than maximizing rejected wrong labels alone, maximize incremental bad-opportunity suppression and preserve good *executable* entry opportunities, alongside owner M-DK-01 atomic predecessor comparison and later G06 8-cell original label/quota metric.

Community techniques scouted but **not** imported as XAUUSD results: adaptive execution state-mixture methods (2025 ACM ICAIF DOI 10.1145/3768292.3770390), QRM RL for optimal execution https://github.com/TomasEspana/qrm_optimal_execution (requires real LOB queue inputs, not available), online streaming changepoints https://github.com/online-ml/river/blob/main/river/drift/adwin.py and https://github.com/fiannai/bocd, competing-risk options https://github.com/havakv/pycox. No external market-feed data or unverified source implementations used in scorer.

**Hard provenance blockers:** original FILTER05 last64 `QUOTE_ORDER_` arrays and producer missing for exact 93D parity; original R9 authentic intent_id/order-state unlinked; original F400 full ZIP missing. Nothing written to PRIMARY, original GitHub engine or MT5_EXPAND /02. No original 39-objective status changed. No forward-blind market month remains within previously exposed Jan/Feb/Jun/Jul. No 400K realized wrong-veto or profitable whole-EA claim.

## Scripts, tests and replay

`f401_r97_action_space_tick_oracle.py` (source entry/action), `f401_r98_quote_volume_option_ablation.py` (original Dukascopy quoted-volume ablation), `test_f401_r97_r98_source_causality.py` (5/5 PASS), and two full result JSONs with all splits and policies in original research ZIP, immutable SHA manifest. External raw sources are NOT recopied; required original hashes above must be checked before rerun. `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=4 python f401_r97_action_space_tick_oracle.py` then `python f401_r98_quote_volume_option_ablation.py`; `python -m unittest -v test_f401_r97_r98_source_causality.py`.
