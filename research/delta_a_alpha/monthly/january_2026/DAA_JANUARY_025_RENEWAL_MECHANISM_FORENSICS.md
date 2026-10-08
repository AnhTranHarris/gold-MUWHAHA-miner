# Delta-A-Alpha January 025 — Hidden Mechanisms, Real-Quote Friction, and Causal Funding Audit

**2026-10-08 | exploratory; source backed, actual January Dukascopy where specified.**

**Scope:** Original January Gamma 131E *frozen historical archive* and Jan 024 *new raw-Bid/Ask tick-executed prototype* are separate systems. No original 131E raw-quote run was achieved in this unit. January–July are development; August and September remain untouched holdouts; May 137 paused. No accepted V1 funded-rule modifications or MQL5 updates.

## 1. Exact January source and historical mechanism decomposition

Dukascopy Jan 2026 raw source SHA256 `d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5`. 9,135,062 quote updates. The historical *normalized-spread* 131E L35_C640 archived result $194,425.92 net / 80,929 simulated 0.01-lot trades / PF 54.37 / -$3,642.86 gross loss / 640 simultaneous / $57,139.20 full-tick equity DD comprises:

| Original L35_C640 source | Net | Trades | Share |
|--|--:|--:|--:|
| Watchdog 119 → 131E child renewal | +$125,843.01 | 69,913 | 64.73% of net; 86.39% of trades |
| All original supporting session/coldstart/native | +$68,582.91 | 11,016 | 35.27% of net; 13.61% of trades |

Original L35_C512 $173,965.80 / 69,925 trades depended on January 30 for **$106,332.25 (61.12%)** and **59,156 trades (84.60%)**; excluding Jan 30 leaves +$67,633.55 / 10,769 trades. Even those are historical optimized research figures, not portable execution evidence.

## 2. NEW critical friction forensic: the exceptional trading day had radically different executable spread

Raw Dukascopy `ask_raw-bid_raw` converted /1000 (sampled from **every quote**, not time-weighted):

| Scope | Quotes | Median spread | p90 spread |
|--|--:|--:|--:|
| All January | 9,135,062 | $0.700 | $1.360 |
| January 30 | 823,245 | $1.797 | $2.710 |
| Jan 30 at 17:00–17:59 UTC | 49,967 | $2.027 | $2.657 |
| January excluding Jan 30 | 8,311,817 | $0.680 | $0.930 |

Legacy 131A -> 131E uses `stmr_base.materialize` with session-normalized approx **$0.20–0.21** spread, not these raw quote sides. The historical WD q is `$1.19`, except 10-minute-bin-5 `$1.10` with 0.01-lot accounting. On Jan 30 the **actual raw spread frequently exceeds an entire child TP quantum**. This is not merely a constant commission correction; the altered Bid/Ask surface changes which exits trigger, residual-child outcomes, Watchdog four-fast-win credit, and later campaign routing. Never report an old timestamp repricing as full raw-execution parity.

## 3. NEW potential source-code funding-credit defect (not quantified as January incidence)

- `GAMMA_02_JAN_WD119_PROFIT_PER_HEAT_131E` sources (`jan_profit_per_heat_atomic_131e.py`, `jan_profit_per_heat_highrange_131e.py`) first compute **all** parent-child exit/P&L and use previous child win/hold for admission (`build_raw`), then apply Watchdog cap `capsel` to the children and separately supplement before final portfolio funding.
- If a predecessor child was *rejected* by a later physical cap, its precomputed P&L may nevertheless have counted as funded predecessor credit for a subsequent parent unlock. This is a code-ordering possibility, **not proof that a particular January trade was wrong**. The bundled toy counterexample verifies the logical inconsistency is possible with four precomputed winning children and zero physically funded child wins.
- The 049→051 parent selector employs its own hypothetical funded stream and expanding realized-parent-profit capacity. The resulting parent tickets are not obviously included as physical positions in the final 131E `wdq + supplemental` funded output. Exact parent exposure, funded predecessor semantics, and whether any parent profits act as shadow credit must be reconstructed in a single tick-event ledger.
- Do NOT blindly fix historic results; rebuild the **actual physical economic state** and compare parent/child/per-campaign financed events, then recalculate Jan 131E parity and gross loss/velocity/risk.

## 4. NEW profit-overfill stress: the original TP arithmetic captures quote overshoot

The old `renewal_owned` uses `(first_quote_beyond_quantum - entry_quote)` as realized P/L, including *favorable* overshoot of the trigger quantum. In the separately rebuilt Jan024 raw first-touch Watchdog sample: 97 executed tickets, 91 q-trigger exits, net **+$85.719**, $38.359 favorable quote overshoot in those TP outcomes (26.94% of their +$142.399 TP gains). If favorable TP fill is capped at the requested q on exactly those same timestamps, sample net falls to **+$47.360**. This is only a sensitivity scenario; MT5 broker TP execution can differ both ways (gaps/slippage/price improvement). Crucially, **do not extrapolate the $38 difference proportionally to original 69,913 renewal tickets** without exact lineage re-execution.

## 5. NEW Jan tick replay experiment A: bounded structural-native stops

12 physically executed raw-quote portfolio sweeps: caps 64/128, no stop vs stops at $0.50, $1, $2, $4, $8 for only the source 6 native positions previously lacking a stop; original fixed TP/SL session routes untouched. Same 0.01-lot, observed Bid/Ask at every first-touch exit, +$0.02/ticket cost, exactly one physical entry per tick. Baseline cap64 **+$12,496.98 / 5,240 trades / -$6,098.86 gross loss / PF3.049 / equity DD $1,761.11**. All new stops 64-cap reduce net (best new stop +$10,795.82); cap128 baseline **+$20,469.05 / 7,213 trades / PF3.597 / equity DD $3,246.53**; new stops at cap128 net <=+$18,905.68. **REJECT new native hard stop family for Jan evidence.** Reduced gross loss alone does not compensate forgone gains. Numeric output `JAN025_NATIVE_STOP_SWEEP.json`.

## 6. NEW Jan tick replay experiment B: spread-relative renewal quantum

10 physically tick-replayed scenarios in **Jan024 incomplete parent prototype only**: keep session cells, L0 Bid/Ask, 0.01 lot, global cap, and set Watchdog TP quantum `q=max(original $1.10/$1.19, k*observed_spread)` at entry, for k=0/1/1.5/2/3; target must be known on entry tick, no future data. At cap128:

| k | Net | Physical tickets | WD tickets | WD net | PF | Gross loss | Eq DD |
|--:|--:|--:|--:|--:|--:|--:|--:|
|0|$20,469.05|7,213|97|$85.72|3.597|-$7,883.05|$3,246.53|
|1|$20,499.24|7,202|86|$115.92|3.600|-$7,883.05|$3,246.53|
|1.5|$20,530.21|7,192|76|$146.88|3.604|-$7,883.05|$3,246.53|
|2|$20,547.07|7,185|69|$163.74|3.606|-$7,883.05|$3,246.53|
|3|$20,577.26|7,171|55|$193.93|3.611|-$7,880.74|$3,246.53|

At k=3, **+$108.21** vs prototype control, but loses 42 Watchdog trades (43.3% WD velocity), gives no equity DD reduction, and has negligible portfolio-quality impact. January-only parameter testing and tiny WD sample prevent acceptance. **RESEARCH LEAD, NOT PROMOTED**. Do not assert that 131E or April would behave similarly.

## 7. Creative next hypotheses, reproducible and not accepted

1. **Parent-funding truth ledger:** One event queue funds parent, children, supplemental, recovery under one position inventory, with `parent_id`, `child_id`, actual funded predecessor and same-tick priority; compare old pre-cap unlocks vs genuinely-funded unlocks and original q-crossing. This is scientifically mandatory before tuning.
2. **Execution-friction compensated quantum:** Minimum TP distance should cover actual spread and expected first-passage excursion, with session-specific completed HTF confirmation; must co-optimize with *velocity preservation* and ensure no dependence on Jan30 label. Calibrate Jan–Jul sequentially, measure in quiet-January and high-range-January in **causal** first-touch paths.
3. **Parent-lifecycle economics:** Treat every parent as inventory with its own market-price marked outcome, not a free option to mint offspring; child renewal only when funded parent still alive and final global heat permits.
4. **Venue-aware profit ceiling:** three broker fill scenarios: (a) first observed quote; (b) requested TP clipped unless broker explicitly improves; (c) 1+ tick delayed fill and adverse spread. Real Coinexx trade logs/contract/margin are needed for release.
5. **Role-separated dynamic phase governor:** Change renewal eligibility/geometry based on completed-M5 **net executable excursion vs current spread** and prior *funded* child residual loss hazard, not only probability of 2 large ranges. Native/Asia independent opportunity generation must retain full first-scout ability within five minutes at arbitrary deployment T0.
6. **Virtual vs physical ownership separation:** allow informative shadow quote paths to train prior statistics, but never count shadow child/parent profit toward earned funding unlocks; distinguish shadow trade count from actual 0.01 funded deal count.

## Hard scientific conclusion

The archive’s extraordinary result has at least three likely contributors: (i) multiple parallel renewal offspring, (ii) exceptional Jan30 directional displacements, and (iii) a low normalized spread / quote-overshoot accounting surface. It may also have eligibility/funding optimism from staged precomputation and cap order. These are **testable mechanisms**, not proof of deployable alpha. No original economic parity or $100 account survivability is certified. January–July development; August and September remain sealed/reserved. Production V1 stays unchanged.

**Reproduction:** `forensic_hidden_mechanisms_025.py`, `test_native_stop_025.py`, `jan025_native_stop_overlay_engine.py`, `test_spread_relative_renewal_025.py`, `jan025_spread_relative_renewal_engine.py`, exact result JSONs/logs, source Jan024 SHA-locked core. All computations are single-period research; no blind-holdout touched.