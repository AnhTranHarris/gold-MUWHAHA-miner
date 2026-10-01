# BETA064 MAJOR CHECKPOINT 03 — MT5 ENTRY + INITIAL-HOLD IMPLEMENTATION SPECIFICATION

**Checkpoint:** BETA064 Major Checkpoint 03 — High-Count Entry + Initial-Hold  
**Purpose:** complete engineering instructions for a future MT5 implementation.  
**This is NOT an EA and contains no MQL5 implementation.**  
**Hold→Exit:** intentionally undefined.  
**August:** SEALED.

## 1. Engineering objective

Reproduce the frozen Checkpoint-03 Python behavior in MT5 without reinterpretation.

Target observed Jan–Jul research identity:
- 5,469 one-position Entry→Initial-Hold trades;
- 88.3891% weighted survival to specialist checkpoint;
- 60.8155% favorable-first-passage success;
- +$5,981.669 diagnostic path value;
- every observed month >=85%;
- 7/7 leave-one-month-out months >=85%.

A future coder may not optimize, simplify, merge or substitute rules and still call the build Checkpoint 03.

## 2. Required module boundaries

Implement conceptually separate modules:

1. **TickChronologyEngine**
2. **OneSecondStateEngine**
3. **FiveSecondStateEngine**
4. **MultiScaleFeatureEngine**
5. **SessionAuthorityEngine**
6. **EntrySpecialistEngine**
7. **BaseEntryModelEngine**
8. **Checkpoint03SessionChildRouter**
9. **PositionOwnershipEngine**
10. **ThesisPacket**
11. **InitialHoldStateEngine**
12. **HoldContinuationModelEngine**
13. **ParityLogger / AuditEngine**

Do not build one monolithic OnTick decision block.

## 3. Tick chronology and executable-price contract

### Tick ordering
- preserve original chronological order;
- preserve same-millisecond order when the broker/feed exposes it;
- never sort same-time ticks by price;
- never fabricate ticks;
- MT5 `OnTick` coalescing must be reconciled using `CopyTicksRange` or equivalent tick-history reconciliation.

### Executable sides
- BUY proposal/entry uses observed Ask.
- SELL proposal/entry uses observed Bid.
- BUY markout / hypothetical close uses Bid.
- SELL markout / hypothetical close uses Ask.

### Runtime causality
- no future tick;
- no retroactive fill;
- no future bar;
- completed buckets only unless a feature is explicitly defined otherwise;
- confirmed pivot logic may act only after required right-side confirmation exists.

## 4. One-second state

The frozen five-second engine consumes a causal one-second ledger with at least:

- bid;
- ask;
- midpoint;
- spread;
- midpoint OHLC;
- tick count;
- quote-pressure proxy;
- quote-volume imbalance proxy.

The exact historical one-second cache builder is part of the older parent-source provenance gap. Therefore an MT5 implementation must not guess the final formulas for the one-second `quote_pressure` and `qv_imb` fields and claim parity.

Required approach:
- recover the original helper/cache builder, or
- reconstruct and prove feature parity against a frozen reference corpus before Checkpoint-03 naming is allowed.

## 5. Five-second completed state

Use 5-second windows `[t, t+5s)`.

Critical causal rule:
the bucket becomes observable only at `t+5s`.

For each completed 5s bucket:

- `open = first midpoint`
- `high = max midpoint`
- `low = min midpoint`
- `mid = last midpoint`
- `bid = last Bid`
- `ask = last Ask`
- `spread = last Ask - last Bid`
- `ticks = sum one-second tick_count`
- `qp = sum(quote_pressure * tick_count) / max(sum(tick_count), 1)`
- `qv = sum(qv_imb * tick_count) / max(sum(tick_count), 1)`
- `body = mid - open`
- `range = high - low`

## 6. Multi-scale return and efficiency state

For a 5-second close series `M_t` and lag `n` buckets:

`r_horizon = M_t - M_(t-n)`

Frozen horizon/bucket pairs:

- r15: n=3
- r30: n=6
- r60: n=12
- r300: n=60
- r900: n=180
- r1800: n=360
- r3600: n=720
- r14400: n=2880

Directional efficiency:

`eff(n) = abs(M_t - M_(t-n)) / (sum_{i=t-n+1..t} abs(M_i - M_(i-1)) + epsilon)`

Frozen model feature set uses:
- eff15
- eff60
- eff300
- eff900
- eff3600

## 7. Volatility, ATR and structural ranges

- `vol60 = rolling_std(diff(mid), 12 completed 5s bars)`
- `vol300 = rolling_std(diff(mid), 60 completed 5s bars)`
- `vol900 = rolling_std(diff(mid), 180 completed 5s bars)`

Frozen range-style ATR features:
- `atr60 = rolling_max(high,12) - rolling_min(low,12)`
- `atr300 = rolling_max(high,60) - rolling_min(low,60)`

Confirmed prior structural ranges:
- `prior5_hi = rolling_max(high.shift(1),60)`
- `prior5_lo = rolling_min(low.shift(1),60)`
- `prior15_hi = rolling_max(high.shift(1),180)`
- `prior15_lo = rolling_min(low.shift(1),180)`
- `prior60_hi = rolling_max(high.shift(1),720)`
- `prior60_lo = rolling_min(low.shift(1),720)`

No current bucket may leak into these prior boundaries.

## 8. Tick intensity

`tick_z = (ticks - rolling_mean(ticks,180,min_periods=60)) / (rolling_std(ticks,180,min_periods=60) + 1e-6)`

## 9. Daily quote-activity-weighted value

Within each UTC day:

`w = max(ticks,1)`

`vwap_q = cumulative_sum(mid*w) / cumulative_sum(w)`

`vwap_dist = mid - vwap_q`

`vwap_z = vwap_dist / (rolling_std(diff(mid),180,min_periods=60) * sqrt(180) + 1e-6)`

Frozen five-second range ratio:

`range_ratio = (rolling_max(high,12)-rolling_min(low,12)) / (rolling_max(high,180,min_periods=60)-rolling_min(low,180,min_periods=60)+1e-6)`

## 10. Frozen base Entry model

The exact corrected V2 Entry models are LightGBM classifiers.

Outputs:
- `p_surv = P(survive to specialist checkpoint)`
- `p_win = P(favorable first passage before adverse)`
- `entry_score = p_surv * p_win`

Frozen base gates:
- `p_surv >= 0.88`
- `entry_score >= 0.30`

Base model feature order:

1. spread
2. r15
3. r30
4. r60
5. r300
6. r900
7. r3600
8. r14400
9. eff15
10. eff60
11. eff300
12. eff900
13. eff3600
14. vol60
15. vol300
16. atr60
17. atr300
18. tick_z
19. qp
20. qv
21. vwap_z
22. range_ratio
23. body
24. range
25. side
26. raw_score
27–38. specialist one-hot E1–E12

Do not reorder columns.

Base model parameters:
- n_estimators 180
- num_leaves 23
- learning_rate 0.045
- subsample 0.8
- colsample_bytree 0.8
- reg_lambda 2
- min_child_samples 80

MT5 must use deterministic tree translation or an explicitly owner-approved deterministic inference bridge.

## 11. Entry specialists and timing contracts

### E1 Macro Structural Trend
- horizon 900s
- Initial-Hold checkpoint 60s
- preserved V2 broad rule:
  - side = sign(r3600 + 0.35*r14400)
  - fresh 5m extreme in side direction
  - r900 agrees with side
  - eff3600 > 0.14
  - eff900 > 0.14
- raw score:
  `62 + 18*eff3600 + 12*eff900`

### E2 Structural Pullback / Reacceleration
- horizon 300s
- checkpoint 30s
- V2 broad rule:
  - side = sign(r3600)
  - r3600*side > 0
  - r300*side < 0
  - r60*side > 0
  - r15*side > 0
  - eff3600 > 0.12
- raw score:
  `60 + 15*eff3600 + 10*eff60`

### E3 Opening Range Break
- horizon 300s
- checkpoint 30s
- role: completed session/opening-range break and acceptance.

### E4 VWAP / Value Trend Pullback
- horizon 300s
- checkpoint 30s
- V2 broad rule:
  - side = sign(r3600)
  - `abs(vwap_dist) < 0.75*atr60`
  - r3600*side > 0
  - r60*side > 0
  - eff3600 > 0.12
- raw score:
  `58 + 15*eff3600 + 8*eff60`

### E5 VWAP / Value Reclaim
- horizon 120s
- checkpoint 15s
- role: accepted value break/reclaim transition.

### E6 Statistical Value Reversion
- horizon 180s
- checkpoint 20s
- role: statistical return toward value in rotational state.

### E7 Liquidity Sweep / Reclaim
- horizon 120s
- checkpoint 15s
- role: failed liquidity excursion followed by reclaim/rejection.

### E8 Key-Level Bounce / Rejection
- horizon 300s
- checkpoint 30s
- role: higher-timeframe/key-level auction rejection.

### E9 Key-Level Break / Acceptance
- horizon 300s
- checkpoint 30s
- role: accepted structural/key-level migration.

### E10 Compression → Expansion
- horizon 120s
- checkpoint 15s
- role: volatility compression followed by directional release.

### E11 Kinetic Ignition
- horizon 45s
- checkpoint 10s
- role: tick/quote velocity, acceleration, efficiency and quote-pressure ignition.

### E12 Failed Expansion / Contradiction
- horizon 120s
- checkpoint 15s
- role: failed breakout / contradiction / recross.

### Provenance rule for E3/E5/E6/E7/E8/E9/E10/E11/E12 parent clocks

Their authoritative historical helper `beta064_multidesk_loop.py` is currently missing from durable storage.

Therefore this document freezes their economic role, horizon/checkpoint, model identity and observed selected behavior, but does **not** invent line-for-line formulas.

Before official MT5 coding:
- recover the helper, or
- independently reconstruct each proposal clock and prove exact candidate parity against a frozen candidate corpus.

A merely similar technical rule is not Checkpoint 03.

## 12. Session Authority Engine

Frozen sessions:

- AUSTRALIA: Australia/Sydney 08:00–17:00
- ASIA: Asia/Tokyo 09:00–18:00
- MIDEAST: Asia/Dubai 08:00–17:00
- EUROPE: Europe/Berlin 08:00–17:00
- UK: Europe/London 08:00–17:00
- NY: America/New_York 08:00–17:00

For each active session model, compute:
- session_p_surv
- session_p_win

Choose the active authority with maximum:

`session_p_surv * session_p_win`

Blend:

`ps_b75 = 0.25*p_surv + 0.75*session_p_surv`

`pw_b75 = 0.25*p_win + 0.75*session_p_win`

`es_b75 = ps_b75 * pw_b75`

Session model features:
- p_surv
- p_win
- entry_score
- normalized relative time from local open
- first-90-min flag
- number of simultaneously active sessions
- six overlap flags
- specialist one-hot columns

Session model parameters:
- n_estimators 120
- num_leaves 15
- learning_rate 0.04
- subsample 0.8
- colsample_bytree 0.8
- reg_lambda 4
- min_child_samples 100

## 13. Checkpoint-03 session-child authority

Broad precheck:
- `ps_b75 >= 0.89`
- `es_b75 >= 0.08`

Only:
- E5
- E6
- E7
- E9
- E10
- E11
- E12
may own a session-child position.

### E5
`ps_b75 >= 0.9145`

### E7
`ps_b75 >= 0.9150`

### E9
`ps_b75 >= 0.9150`

### E10
`ps_b75 >= 0.9145`

### E12
`ps_b75 >= 0.9145`

### E11
No deficit expansion. Require frozen session threshold:
- AU 0.920
- Asia 0.900
- Middle East 0.915
- Europe 0.910
- UK 0.925
- NY 0.925

### E6 New York
Require all:
- ps_b75 >= 0.920
- eff60 >= 0.30
- friction <= 0.14
- session_value_z >= -2.5

### E6 UK
Require all:
- ps_b75 >= 0.905
- eff60 >= 0.40
- eff300 <= 0.10
- session_value_z >= -4.0

### E6 other sessions
Use frozen session threshold.

`friction = spread / max(atr60, 0.05)`

For session-value normalization, durable derivative research uses:

`z_value = (mid - session_vwap) / max(atr60,0.05)`

and reversion side points toward session value.

For the C02C field `session_value_z`, implementation must reproduce the frozen E6 feature ledger; a consistent reconstruction is the side-aligned value displacement:

`session_value_z = side * z_value`

but this formula must be parity-certified against the historical E6 ledger before official Checkpoint-03 MT5 naming.

## 14. Session value and boundaries

For each local session:
- session_vwap uses completed 5s midpoint weighted by completed 5s tick count;
- first 15 local minutes define ORB;
- previous 30 local minutes define pre-open high/low;
- running session high/low excludes current incomplete bucket;
- preserve previous completed session high/low;
- track relative local minutes from open.

DST-aware timezone conversion is mandatory.

## 15. Base-first ownership

### Base schedule
Candidate pool:
`p_surv >= 0.88 AND entry_score >= 0.30`

Sort:
1. time ascending;
2. entry_score descending.

Accept first non-overlapping proposal and reserve:

`[proposal_time, proposal_time + specialist_horizon)`

### Session-child eligibility
A child proposal must fit **entirely outside** all reserved base intervals.

Base trades may never be displaced by a child.

### Session-child scheduling
For approved child proposals:
- `end = time + horizon`
- sort end ascending;
- tie-break ps_b75 descending;
- then es_b75 descending;
- accept chronologically if proposal time is not before current busy end.

One position at a time.

## 16. Thesis packet at fill

Persist immutably:

- checkpoint id;
- model version hashes;
- proposal timestamp;
- fill timestamp;
- specialist id;
- router origin BASE or SESSION_CHILD;
- side;
- horizon;
- Initial-Hold checkpoint age;
- raw specialist score;
- p_surv;
- p_win;
- entry_score;
- session authority;
- session_p_surv;
- session_p_win;
- ps_b75;
- pw_b75;
- es_b75;
- all runtime feature values;
- structural/value reference levels;
- entry Bid/Ask;
- entry spread.

Do not rewrite origin after fill.

## 17. Initial-Hold research geometry

For offline labels:

`spread_label = max(candidate_spread, 0.05)`

`atr_label = max(atr60, spread_label)`

`fav = max(0.35, 1.25*spread_label, 0.30*atr_label)`

`adv = max(0.30, 1.00*spread_label, 0.22*atr_label)`

Survival:
adverse executable excursion does not hit `-adv` before the specialist checkpoint.

First passage:
`+fav` occurs before `-adv` inside specialist horizon.

These formulas are **labels and parity diagnostics**, not a live exit system.

## 18. H1–H8 post-fill state

At the specialist checkpoint calculate at minimum:

- MFE
- MAE
- current executable excursion
- path efficiency
- entry recross count
- new-extreme renewal ratio
- hold age
- spread evolution
- quote intensity
- signed quote pressure

Frozen research descriptors:

- H1 Ignition: current >0, efficiency >0.45, renewal >0.15
- H2 Extension: MFE >0.45*fav, current >0.55*MFE, efficiency >0.30
- H3 Healthy Pullback: MFE >0.35*fav, current >-0.25*adv, current <0.70*MFE, recross <=3
- H4 Reacceleration: current >0, renewal >0.10, MFE >0.20*fav
- H5 Transient: MFE >0.55*fav, current <0.35*MFE, current >-0.20*adv
- H6 Stall/Chop: efficiency <0.18 and recross >=2
- H7 Failed Acceptance: current <-0.35*adv or (current <0 and recross >=4)
- H8 Exhaustion: MFE >0.80*fav, current <0.45*MFE, renewal <0.12

The frozen Hold model consumes grouped H-state features plus entry/state features.

## 19. Hold continuation model

Target:
`P(favorable first passage after checkpoint | survived and unresolved at checkpoint)`

Frozen threshold:

`P_continue >= 0.6185642603486833`

Model parameters:
- n_estimators 140
- num_leaves 15
- learning_rate 0.04
- subsample 0.8
- colsample_bytree 0.8
- reg_lambda 3
- min_child_samples 50

The output is continuation worthiness only.

**It must not close a trade because Hold→Exit is not frozen.**

## 20. Learned-model artifact authority

Use only:

`BETA064_MAJOR_CHECKPOINT_02_ENTRY_HOLD_MODEL_FREEZE_BUNDLE_V2.zip`

Drive ID:
`1phzsMX0SKESoqJ4O53vI9nE7fffrX6T-`

Bundle SHA-256:
`ccfc0d18d733e97b18bbd183c6cc56b6bcac0f1c2c6c525bda596d0406eb98d3`

Checkpoint 03 changes router authority only; it does not retrain those models.

## 21. Mandatory MT5 parity tests

### A. Tick parity
Same source tick order and executable Bid/Ask.

### B. 5s state parity
For sampled timestamps compare every frozen feature.

### C. Candidate parity
Per specialist:
- timestamp
- side
- raw_score
- horizon
- checkpoint age

must match Python/reference corpus.

### D. Model parity
For every sampled proposal:
- p_surv
- p_win
- entry_score
- session_p_surv
- session_p_win
- ps_b75
- pw_b75
- es_b75

must match within a separately frozen numeric tolerance.

### E. Ownership parity
Exact selected sequence must reproduce the Checkpoint-03 panel for the same source data.

### F. Initial-Hold parity
At fixed post-fill timestamps:
- MFE/MAE
- current excursion
- recross
- renewal
- H-state flags
- p_continue

must match.

No Hold→Exit coding before these tests pass.

## 22. Exact checkpoint proof

Observed selected-panel reconstruction:

Start with C02C selected ledger and remove:

`(specialist == E7 or E9) AND ps_b75 < 0.915`

Result:
- exactly 5,469 trades;
- selected CSV SHA-256 `2fe7b28280d670b915c0968e8daac5fbcf23193faf2c36b0b6f45c0e6d480cc5`;
- weighted survival 0.8838910221;
- weighted FP 0.6081550558;
- diagnostic value 5981.669.

This is a required parity checkpoint for any future implementation.

## 23. Prohibited implementation shortcuts

Do not:
- import Alpha/GAMMA strategy rules;
- use R9 as hidden eligibility logic;
- merge all specialists into one universal signal;
- let child routing steal a base slot;
- use forming bars where completed state is required;
- use fixed UTC session times through DST;
- execute on synthetic Heikin-Ashi prices;
- enable C02G derivative clocks as entries;
- enable C02H adapters as authority;
- enable E13–E16;
- retrain frozen models and retain the checkpoint name;
- invent Hold→Exit;
- call an approximate proposal generator Checkpoint 03.

## 24. Required recovery before official EA coding

The missing historical `beta064_multidesk_loop.py` helper is a hard blocker for exact parent-clock parity for several specialists.

An official MT5 build may begin with chronology/state/model instrumentation, but may not be labeled Checkpoint-03 Entry parity until the missing proposal logic is recovered or independently reconstructed and certified.

## 25. Recommended future MT5 build order

When the owner separately authorizes MQL5 coding:

1. chronology/audit logger only;
2. one-second and completed-5s state engine;
3. state parity;
4. timezone/session engine;
5. recovered E1–E12 proposal engine;
6. candidate parity;
7. frozen model inference;
8. probability parity;
9. base ownership;
10. Checkpoint-03 child router;
11. selected-sequence parity;
12. thesis packet;
13. Initial-Hold state;
14. frozen Hold continuation model;
15. Initial-Hold parity;
16. only then resume Hold→Exit research.

No actual MQL5 source is created by this specification.
