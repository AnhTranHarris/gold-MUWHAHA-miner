# R9 GAMMA-01 — H1 Structural Persistence Sleeve

## Status

**Classification:** MT5 TEST CANDIDATE — not yet PROMOTED or MT5-certified.

**Parent:** `carson/r9-gamma-00-baseline`

**Candidate branch:** `carson/r9-gamma-01-h1-structural-trend`

**EA:** `Experts/GoldMuwahahaMiner_R9_GAMMA_01.mq5`

**EA implementation commit:** `2ae365bb6c866b7554889d1981f03f348f064b25`

The exact R9 HybridGate logic remains present. GAMMA-01 adds one independently tagged structural sleeve. The new sleeve uses its own magic number and trade state so that its lifecycle cannot overwrite R9 core lifecycle globals.

This checkpoint is deliberately classified below PROMOTED because it has not yet passed MetaEditor compilation and Coinexx "Every tick based on real ticks" certification.

---

## 1. Hypothesis

R9 REAL does not fail because XAUUSD lacks directional opportunity. It fails because the M1/tick breakout logic expects persistence at a horizon where real Gold frequently churns, snaps back, and stops the position before the synthetic path's persistence develops.

The hypothesis for GAMMA-01 is:

> Persistent XAUUSD displacement exists more reliably on a slower structural horizon, so a causal H1 Donchian breakout with volatility-scaled risk can provide an economically different return stream alongside the R9 high-frequency core.

This is an **orthogonal specialist**, not a replacement for R9 and not a claim that slower trading alone can bridge the full R9 SYNTH gap.

---

## 2. Public provenance and reconstructibility

The mechanism is intentionally public and reconstructible:

1. **Donchian-style structural breakout:** enter only after price crosses the highest high or lowest low of a fixed number of completed higher-timeframe bars.
2. **ATR-normalized risk:** express initial risk and trailing distance in units of recent completed-bar true range.
3. **Trend persistence lifecycle:** tolerate a low win rate in exchange for capturing larger persistent excursions.

Public references used as architectural corroboration, not as evidence of our profitability:

- [MetaQuotes Strategy Tester documentation](https://www.metatrader5.com/en/terminal/help/algotrading/testing) — why real-tick certification is required for execution-sensitive EAs.
- [MQL5 ADX Trend Pullback EA](https://www.mql5.com/en/code/73958) — open-source example separating trend state, pullback geometry, and ATR-normalized risk.
- [Public Gold Donchian/trend-following discussion](https://www.reddit.com/r/algotrading/comments/1unk44b/stairway_to_heaven_a_trendfollowing_breakout/) — anecdotal performance only; used because the entry/trailing mechanism is independently reconstructible.

No proprietary indicator, hidden coefficient table, vendor signal, or opaque external model is required.

---

## 3. Exact research definition

Let completed H1 bars be indexed so that bar 1 is the most recently completed H1 bar.

For the selected predeclared candidate, the Donchian lookback is:

`N = 4`

The causal upper and lower structural boundaries during the current H1 interval are:

`U_t = max(H_1, H_2, H_3, H_4)`

`L_t = min(L_1, L_2, L_3, L_4)`

No current unfinished H1 high or low is admitted into either boundary.

True range for a completed H1 bar k is:

`TR_k = max(H_k - L_k, |H_k - C_(k+1)|, |L_k - C_(k+1)|)`

The research ATR is a **simple arithmetic mean**, not an assumed Wilder EMA:

`ATR14_t = (1/14) * sum(TR_k), k=1..14`

All fourteen TR observations are completed H1 bars.

### Long entry

A long event requires the price path to cross from inside/below the causal upper boundary to or above it:

`P_(t-1) < U_t and P_t >= U_t`

### Short entry

`P_(t-1) > L_t and P_t <= L_t`

### Initial catastrophic stop

Long:

`SL_0 = Entry - 2 * ATR14_t`

Short:

`SL_0 = Entry + 2 * ATR14_t`

### Structural trailing stop

For long positions:

`HighWater_t = max(HighWater_(t-1), P_t)`

`SL_t = max(SL_(t-1), HighWater_t - 2 * ATR14_t)`

For short positions:

`LowWater_t = min(LowWater_(t-1), P_t)`

`SL_t = min(SL_(t-1), LowWater_t + 2 * ATR14_t)`

The ATR is allowed to update only when a new H1 interval begins, because every value still depends exclusively on completed H1 bars.

There is no fixed take profit and no fixed maximum holding time.

---

## 4. Causal execution controls

The Python research engine used the canonical Dukascopy Jan–Jul tick chronology and derived one-second mid-price bars directly from that chronology.

Key controls:

- UTC-anchored H1 bars.
- Donchian and ATR values use completed H1 bars only.
- No unfinished H1 high/low/close is used.
- Entry requires an actual crossing from inside to outside; an already-broken level does not generate repeated entries.
- Ambiguous same-second two-sided crossings are skipped.
- Existing stop is checked before a newly observed high/low can improve the trailing stop. This is conservative against the strategy.
- One structural position at a time.
- Fixed 0.01 lot research normalization.
- Explicit round-trip cost stress.
- August 2026 was not used.

The MT5 implementation maps the research mid-price signal into executable bid/ask orders. Therefore MT5 certification may differ from the Python result; that difference is intentional evidence, not something to hide.

---

## 5. Exact source-data identity

The research used the following Jan–Jul Dukascopy archives. SHA-256:

| Month | SHA-256 |
| --- | --- |
| Jan | `d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5` |
| Feb | `ed3b3545c990c88d78519594c17c8915b0f679adcb0a94920ba7524f1f6d5c5d` |
| Mar | `814ba35e72f219a58badd806ed5c0f30ef0fb4ffe56a48205d873706513bd177` |
| Apr | `30375098f62aed6cabc32ec6b67c57c20baec9b6d9be1ce0a204e09806c1ec0f` |
| May | `3a50e0f1eba3076154238290ec02842cf3744ab192e5c9a2acc1cc07367c6a0d` |
| Jun | `34686ce53ba992dfb83ea35d555b6a4947a9216635853857c8bf11ce70c00ae2` |
| Jul | `e171e8c2fb59f3f4147a6f845eb68e664fa9c0f4815caa33acdbb42cc2f768b7` |

Research artifact SHA-256:

- `test_structural_trend.py`: `ff16fd550392b599251cc3aae9d79bef0d4bf64e80cf1b71163929792ef7da8c`
- `test_h1_neighborhood.py`: `e5879844ab74f136b371c808cff8502458d005197e36526ee7af2281d3679c50`
- selected trade list: `e923b065636c2aef2532150f51b3a68baf834f36b7bb25a8b83b57e9ba14a63e`
- neighborhood results: `39cae2a73f0589f1677ce08405f20e7849d2ab30127de2f154921594612c57ec`
- structural comparison results: `f0d776521396046a98dc667b8c3b19cc05fd8dc935a2ac8d52030de51adc1df7`

---

## 6. Fresh Jan–Jul result

Selected candidate was seeded **before** the local parameter-neighborhood scan:

- timeframe: H1
- Donchian lookback: 4 completed bars
- ATR window: 14 completed bars
- initial stop: 2 ATR
- trailing distance: 2 ATR
- cost: $0.20/trade
- lot normalization: 0.01

Aggregate:

| Metric | Result |
| --- | ---: |
| Trades | 370 |
| Net | **+$2,042.17** |
| Gross profit | +$7,461.26 |
| Gross loss | -$5,419.08 |
| Profit factor | **1.3768** |
| Win rate | 40.81% |
| Average net/trade | +$5.52 |
| Median hold | 6.92 hours |
| Mean hold | 11.30 hours |
| Max sequential trade-equity drawdown | about $894.55 |
| Max losing streak | 10 |

### Monthly attribution

| Month | Trades | Net | PF | Win rate | Median hold |
| --- | ---: | ---: | ---: | ---: | ---: |
| Jan | 49 | +$797.39 | 2.089 | 40.82% | 6.51 h |
| Feb | 53 | +$6.20 | 1.006 | 37.74% | 5.86 h |
| Mar | 60 | +$453.83 | 1.408 | 35.00% | 4.95 h |
| Apr | 53 | +$120.58 | 1.180 | 45.28% | 6.90 h |
| May | 46 | +$274.13 | 1.517 | 41.30% | 8.76 h |
| Jun | 50 | +$356.64 | 1.526 | 48.00% | 8.80 h |
| Jul | 59 | +$33.40 | 1.056 | 38.98% | 7.53 h |

All seven months are positive, although February and July are near breakeven and therefore remain important fragility checks.

---

## 7. Cost sensitivity

The selected candidate is comparatively insensitive to transaction-cost stress because the average structural excursion is large relative to the HFT cost scale.

| Assumed round-trip cost | Net | PF |
| ---: | ---: | ---: |
| $0.20 | +$2,042.17 | 1.3768 |
| $0.25 | +$2,023.67 | 1.3727 |
| $0.30 | +$2,005.17 | 1.3685 |
| $0.35 | +$1,986.67 | 1.3644 |

This does **not** prove live execution quality. It only shows that this mechanism is not dependent on a few cents of cost modeling.

---

## 8. Parameter-neighborhood result

After fixing N=4 / stop=2 / trail=2 as the candidate, a local neighborhood was inspected.

Important observations:

- N=4 / stop=1.5 / trail=2 was stronger in the now-observed sample, but it was discovered during the neighborhood scan and is **not substituted** for the predeclared candidate.
- N=4 / stop=2.5 / trail=2 produced essentially the same result as 2 ATR because the 2 ATR trailing geometry dominated much of the initial-stop behavior.
- N=3 through N=7 with a 2 ATR trail produced broadly positive aggregate results, though several lost one month.
- The selected N=4 / 2 / 2 candidate was one of the rare nearby points with all seven months positive.

The purpose of the neighborhood scan is robustness evidence, not post-hoc parameter replacement.

---

## 9. Small-account survivability

This sleeve is **not safe for the preferred $100 initial account at fixed 0.01 lot**.

Applying the selected research trade sequence to different starting balances:

| Start | Minimum balance path | Minimum / start |
| ---: | ---: | ---: |
| $100 | -$104.91 | -104.9% |
| $200 | -$4.91 | -2.5% |
| $500 | $295.09 | 59.0% |
| $1,000 | $795.09 | 79.5% |

Therefore GAMMA-01 introduces a default:

`InpStructuralMinBalance = 1000.0`

The structural sleeve must remain inactive below that balance unless the tester explicitly overrides the research safety gate.

This is an auxiliary capital-tier specialist. It must not be represented as a $100-account solution.

---

## 10. Rejected alternatives in this fresh cycle

### Shallow event router

A deterministic shallow-tree CONTINUE/FADE router built from causal R9/Dukascopy state variables produced promising Jan–April samples but failed May–June. It is rejected rather than fitted further.

### Simple sweep/reclaim specialist

A public, reconstructible sweep/reclaim rule family was tested over hundreds of causal combinations using prior highs/lows, sweep penetration, reclaim, reversal body, relative tick activity, ATR-buffered stop, and fixed reward/risk.

Discovery performance was weak and no leading configuration survived April validation. The straightforward formulation is rejected as a standalone specialist.

These failures matter because they support the need for **economic-mechanism diversification**, not simply a more complicated classifier on the same R9 event.

---

## 11. MQL5 implementation

GAMMA-01 adds:

- independent `CTrade structuralTrade`
- independent magic `5560`
- independent structural position lookup
- completed-H1 Donchian calculation
- completed-H1 simple TR/ATR calculation
- structural crossing detector
- independent high-water / low-water trailing state
- $1,000 default activation floor
- optional core/structural concurrency control
- hedging-account guard when simultaneous same-symbol sleeves are enabled
- `InpCoreEnabled` A/B control for clean Strategy Tester isolation

During static integration review, a cross-sleeve retcode bug was found: the initial implementation reused the R9 core's `ResultAccepted()` helper for structural orders. This would have read the wrong `CTrade` object's last retcode. The candidate now has `StructuralResultAccepted()`, isolating structural execution state.

The file has balanced structural braces and expected integration markers, but **has not yet been compiled in MetaEditor**.

---

## 12. Required MT5 certification tests

This candidate earns MT5 testing, not promotion.

Minimum next tests:

1. MetaEditor compile with zero errors.
2. Structural-only A/B:
   - `InpCoreEnabled=false`
   - `InpStructuralEnabled=true`
   - Jan–Jul, "Every tick based on real ticks"
3. Exact R9 regression:
   - `InpCoreEnabled=true`
   - `InpStructuralEnabled=false`
   - result must reproduce the R9 baseline within explained tester/environment tolerance.
4. Cumulative GAMMA-01:
   - core ON
   - structural ON
   - evaluate simultaneous-sleeve interactions, gross loss, drawdown, monthly attribution, and position overlap.
5. Run fixed 0.01 lot before any MUWHAHA balance ladder.
6. Test $100 / $200 / $500 / $1,000 starts and report both 60% and 30% survivability floors.
7. Do not open August. August remains sealed.

Only after those tests can this checkpoint become **PROMOTED** and serve as the parent of GAMMA-02.

---

## 13. Why it deserves an MT5 integration test

The candidate meets the research threshold for an implementation bridge because it is:

- independently reconstructed from the current canonical Jan–Jul data;
- causal and based only on completed structural bars;
- positive in all seven observed months;
- robust to transaction-cost stress;
- supported by a useful local parameter neighborhood;
- economically different from R9's high-frequency path;
- fully reconstructible with public formulas;
- simple enough to map deterministically to MQL5;
- honest about its serious drawdown and small-account limitation.

It does **not** meet the threshold for final promotion because broker-native real-tick execution, compile behavior, and cumulative interaction with R9 are still unknown.

That distinction is deliberate.

---

## Promotion decision

**Decision: ADVANCE TO MT5 TESTING. DO NOT YET PROMOTE.**

If MetaEditor/REAL-tick certification fails, return to `carson/r9-gamma-00-baseline`; do not use this branch as the parent of another GAMMA breakthrough.

If it passes the full gate, update this note and manifest to PROMOTED before creating GAMMA-02.
