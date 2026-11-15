# R9 V10 — causal hierarchical structure, zones and specialist policy

**Status 2026-11-15: RESEARCH / SHADOW ONLY. NOT DEPLOYABLE.**

## Frozen parents / non-negotiable boundaries

- Parent: `carson/r9-micro180-v9-volume-executable-or-20261114`, `493f76ab22c48ea92cac1ca9c2d44c8ffdb76c46`.
- Original `Experts/GoldMuwahahaMiner_R9_HybridGate.mq5` blob `07222b1a3800c9cc826abe10a4ce6afbd97b0af5`, never changed.
- V8 native reference blob `0c52da7ea7e22701e607181380a4f49f9aad78eb`, never changed.
- V9's actual BUY/SELL, risk governor, net-cash harvest, 30s time limit, account locks and entries-per-minute remain inherited.
- V10 never executes trades, modifies stops, or blocks original V9 signals. Its default native flag `InpV10StructureShadow=false`; demo orders remain OFF.
- **No new tick warehouse, no downloaded history, no optimization loop, no profit ranking.**

## Files

- `causal_structure.py`: bounded, source-exact Python quote observer and multiscale bars/zone detector
- `specialist_policy.py`: per-pattern entry thesis and structural lifecycle proposal
- `structure_overlay.py`: unchanged V9 execution with V10 entry/hold diagnostics
- `run_structure_audit.py`: frozen V9 vs V10 bounded source replay and exact trade-event assertions
- `test_causal_structure.py`, `test_specialist_policy.py`, `test_overlay_parity.py`: synthetic causality and untouched-V9 regression tests
- `Experts/GoldMuwahahaR9V10StructureShadow.mqh`: terminal-native completed-bar and indicator observer
- `Experts/GoldMuwahahaMiner_R9_Micro180_V9_Research.mq5`: native V9 research fork with optional V10 read-only call
- `.github/workflows/r9_v10_causal_structure_shadow.yml`: no-download Python CI and source guards

## High-frequency architecture

Original, millisecond ordered Coinexx quotes feed a single **observed** S1 bucket.
Completed S1 bars are rolled into observed S5, S15, S30, M1, M5, M15, H1,
H4 hierarchy; no missing bar is inserted. Higher frames advance on S1
completion, not once per raw quote. Zones and swings are recomputed only
on higher-frame completion; a nearby confirmed zone can then be tested using
the current executable Bid or Ask on each original quote.

Runtime: constant-time update on ordinary raw ticks; the occasional observed
second boundary updates at most nine frames; at most 40 zones and 128
completed bars per frame. Diagnostics hold only the newest 512 event records.
No unbounded trade ticks or copied raw tick CSVs are created.

## Causal support and resistance

A high pivot at bar `i` becomes a resistance seed only after **two strictly
lower completed bars on its right**, with two lower completed bars on its left.
A confirmed low pivot analogously becomes support. Thus bar `i` is NEVER
actionable as a zone at its actual pivot timestamp. Any gap among the five
bars invalidates the pivot.

Zone half-width is an explicit *research hypothesis* in integer XAU point
units (0.01 price): `min(500, max(2, spread/2, 0.16 * closed_ATR14))`.
Same-kind candidate seeds within 1.5 times the larger zone half-width merge
using an online weighted centroid. The pooled zone retains source timeframes,
touch count, last confirmation, and compact source identity. Re-entry touch
counts are debounced to at least five seconds; active structural zones expire
after 14 days without new confirmation. The 40-zone bound evicts weak/old
candidates. These are zones, not infinitely precise support lines.

**Do not call the touch count actual volume, resting liquidity or a DOM
liquidity wall.** It is simply repeated observed price contact. Midquote is
used to create source-side neutral Python zones; the breakout must clear the
preexisting zone on the executable liquidation side: BUY uses current Bid;
SELL uses current Ask. The threshold is frozen on breakout detection.

Causal breakpoint phases: `PROBE`, `ACCEPTED` (two separately closed
source seconds), `RETEST`, `RETEST_CONFIRMED`, `FAILED`, `EXPIRED`.
An accepted breakout may still fail later. A retest is not equivalent to
a confirmed rejection. Higher-timeframe trend is derived from two validated
successive swing highs/lows where available, otherwise an explicitly marked
closed-bar direction-efficiency proxy. Stale trends expire.

## Hierarchical structural specialists

| Specialist | Required structural hypothesis | Response type |
|---|---|---|
| BREAKOUT_INITIATION | Current executable Bid/Ask penetrates frozen zone | WAIT_CONFIRM |
| BREAKOUT_ACCEPTANCE | Two separately completed seconds remain outside | STRUCTURAL_CANDIDATE |
| BREAKOUT_RETEST | Previously accepted move returns to boundary | WAIT_REJECTION |
| BREAKOUT_RETEST | Retest is followed by executable-side continuation | STRUCTURAL_CANDIDATE |
| FALSE_BREAK_DEFENSE | Break returns through full frozen zone | AVOID_UNTIL_NEW_SETUP |
| TREND_CONTINUATION | Confirmed parent and micro directions agree | STRUCTURAL_CANDIDATE |
| NESTED_COUNTERTREND | Parent direction opposes micro direction | WAIT_PARENT_RESOLUTION |
| RANGE_BOUNDARY | Compression and near a support/resistance zone | WAIT_REJECTION |
| STRUCTURAL_REVERSAL | Opposed confirmed micro swing topology plus change alarm | STRUCTURAL_CANDIDATE |
| TREND_EXHAUSTION | Earlier 1s impulse weakens near confirmed opposing zone | WAIT_IMPULSE_RENEWAL |
| UNRESOLVED | Insufficient causal evidence | OBSERVE_ONLY |

The `STRUCTURAL_CANDIDATE` label is an **unfitted research proposal**,
not an actual V9 order and not a probability of success. Each actual V9 entry
retains a frozen structural stop/reference; the policy can emit
`HOLD_OBSERVE`, `DEFEND`, `RISK_REVIEW`, or `THESIS_INVALIDATED`
without modifying the original trade.

## Native MT5 indicator/proxy design

| Source | Usage | Causal constraint |
|---|---|---|
| `CopyRates(M1/M5/M15/H1/H4, shift=1, 5)` | Confirmed symmetric pivot support/resistance | Pivots only after two right-hand CLOSED bars (center shift=3) |
| `iATR(14)` | Zone bandwidth and cross-timeframe volatility normalization | Read `CopyBuffer(handle,0,1,1)`; closed only |
| `iADXWilder(14)` | M1 ADX regime context, +DI/-DI direction vote | Buffers 0/1/2 at shift=1 |
| `iMA(20,MODE_EMA)` | Closed M1 directional slope normalized by M1 ATR | EMA shifts 1 and 2 |
| `iBands(20,2)` | Compression proxy: closed band width / ATR | Buffers 1 upper, 2 lower; never a breakout guarantee |
| `iFractals` (optional reference) | Check terminal pivot attribution | Only fully confirmed buffer values shift>=3; current pivots can repaint |
| Observed `MqlTick` | Bid/Ask breakout and entry quality | Quote-only; flags and equal-ms ordering matter |

All indicator thresholds here are engineering hypotheses rather than fitted
cutoffs. The native comparator uses broker Bid M1+ bars, while Python creates
quote-mid bars from the chronological Coinexx stream and explicitly uses
S5/S15 pivots as well. **Native / Python zone parity is NOT established.**
The native observer runs only on the latest fully synchronized terminal quote,
while Python consumes every original quote in order. Do not claim structural
event-time parity or enable its advice as a real-time gate until the difference
is explicitly resolved and logged.

Avoid using OBV, MFI, VWAP, DOM delta or transaction-volume claims without
a real source for executed quantity. `tick_volume` measures quote activity,
not centralized spot gold trade volume. `MarketBookGet` requires valid broker
DOM; if unsupported, do not manufacture it.

## Existing-data-only bounded experiment

Use the **already available** Coinexx source `.csv` or `.csv.gz`,
not the Dukascopy ticks as a silent broker substitute. The inherited reader
validates the existing source schema, timestamp order and Bid/Ask; it does
not sort or deduplicate equal-millisecond rows:

```bash
cd research/coinexx_r9_chronological
python structure_v10/run_structure_audit.py \
  --ticks "/path/to/EXISTING_COINEXX_SOURCE.csv.gz" \
  --limit 200000 \
  --expected-sha "SHA256_OF_EXISTING_FROZEN_SOURCE" \
  --out "/tmp/r9_v10_structure_audit.json"
```

The Python runner simultaneously replays existing V9 and the V10 shadow
on the same ordered source quotes, hard-fails if any entry/exit ordinal,
side, fill price, close reason or ending position diverges, and returns
a compact structure/volume diagnostic JSON. The script never creates a
second quote archive or profit report. The 512 most recent advice events
are optional interpretive diagnostics, not the complete event ledger.

For a more complete causal attribution, compare frozen candidate snapshots
by month, session, BUY/SELL and parent-regime, with future path used ONLY
to score the historical labels and never as an entry-time feature.
Evaluate pattern coverage, breakout acceptance, failed-break latency,
entry delay, zone-touch error, same-entry exit consistency, original
entry count, and native-to-Python event coverage. **This round excludes
profit rankings and hyperparameter searches.**

## Release gates and limitations

1. GitHub Python unit + inherited V9 regression + source guards pass.
2. Real original Coinexx bounded sample audit completed; stable V9 event
   invariants and per-pattern coverage reported. **NOT YET RUN HERE.**
3. Full-month chronological source replay with causal warmup, then time-frozen
   out-of-sample structure audit. **NOT YET RUN HERE.**
4. Full MQL5 MetaEditor zero-error compile of V10-enabled fork. **NOT VERIFIED.**
5. Native terminal quote/bars/indicator seeding benchmark versus Python,
   including session gap, equal-ms event order, missing bars, partial closes,
   source timezone and different higher-TF initialization. **NOT VERIFIED.**
6. Strict demo-only tests of any *future* explicitly authorized entry/exit
   routing with the existing account-wide governor and real broker fills.
   **NOT AUTHORIZED / NOT ACTIVE.**

The native observer itself has no broker order methods. The underlying
V9 fork still defaults to `InpEnableDemoOrders=false`; experimental V10
observer defaults OFF to guarantee untouched V9 behavior.

## References

- MetaQuotes `CopyRates`: https://www.mql5.com/en/docs/series/copyrates
- MetaQuotes `CopyBuffer`: https://www.mql5.com/en/docs/series/copybuffer
- MetaQuotes `CopyTicks`: https://www.mql5.com/en/docs/series/copyticks
- MetaQuotes `iATR`: https://www.mql5.com/en/docs/indicators/iatr
- MetaQuotes `iADXWilder`: https://www.mql5.com/en/docs/indicators/iadxwilder
- MetaQuotes `iBands`: https://www.mql5.com/en/docs/indicators/ibands
- MetaQuotes `iFractals`: https://www.mql5.com/en/docs/indicators/ifractals
