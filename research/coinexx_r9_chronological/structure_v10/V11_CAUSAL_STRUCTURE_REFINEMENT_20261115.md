# R9 V11 — evidence-grounded unresolved attribution, persistent higher-timeframe S/R, frozen invalidation

**Research-only | 2026-11-15 | Draft fork of frozen V10 source**.

## Why this exists

The prior January–September 2026 audit of **72,129,347** real Coinexx quotes
found **338,065** V9 entry opportunities with **162,309 (48.01%) classified
UNRESOLVED**. The 40-slot shared zone cache filled to 40/40, and **99,613**
V10 `THESIS_INVALIDATED` research transitions were vulnerable to referencing
support/resistance on the wrong side of the entry. These were never executed
exits and must not be presented as real exit accuracy.

V11 does not replace the R9 V9 trading engine or add more generic indicators.
It introduces *independent*, read-only evidence and structural reference
diagnostics. The exact earlier V10 `causal_structure.py` and `specialist_policy.py`
files are unchanged, enabling apples-to-apples experimental comparison.

## Three changes

### 1. Unresolved entry evidence rather than forced positive labels

`RefinedStructure.profile(snapshot, side, legacy_specialist)` examines
the exact **V10 specialist router fallback**, which can be UNRESOLVED
even when the primary market pattern is already recognised. It also uses
only **already completed**, contiguous S15, M1 and M5 observations to
subdivide remaining truly ambiguous cases. Its diagnostic categories are:

| Subtype | Observable requirement |
|---|---|
| CHANGE_ALARM_NO_CONFIRMED_THESIS | Recognised CUSUM transition without a matched entry thesis |
| ENTRY_SIDE_OPPOSES_CONFIRMED_TREND | Existing V9 entry direction opposes the observed micro trend |
| NESTED_STRUCTURE_SIDE_MISMATCH | Nested HTF/micro structure exists, but V9 side is not covered by original router |
| STRUCTURAL_EVENT_SIDE_MISMATCH | Breakout/retest/failure event exists on the other side of this V9 entry |
| REVERSAL_CANDIDATE_NOT_CONFIRMED | Causal reversal candidate lacks completed specialist-side evidence |
| BREAKOUT_PROBE_EXPIRED_UNCONFIRMED | Frozen breakout probe expired before confirmed acceptance |
| QUOTE_DISCONTINUITY | Current quote gap invalid |
| INSUFFICIENT_MICRO_EVIDENCE | Fewer than eight contiguous closed S15 bars |
| INSUFFICIENT_PARENT_EVIDENCE | M5 unavailable and micro evidence weak/mixed |
| MICRO_IMPULSE_UNCONFIRMED_PARENT | Strong directional S15 without closed M5 |
| CROSS_SCALE_ROTATION_CANDIDATE | S15 and M5 close-to-close efficiencies near zero |
| CROSS_SCALE_CONFLICT | Strong S15 and M5 signed efficiencies oppose |
| UNCONFIRMED_ALIGNED_IMPULSE | Strong efficiencies agree, swing validity not confirmed |
| MICRO_PULLBACK_OR_PAUSE | Strong M5, low-net S15 |
| MICRO_EXPANSION_PARENT_BALANCED | Strong S15, near-zero M5 |
| MIXED_STRUCTURE_INSUFFICIENT | None of the above can justify a firm inference |

These are *reasons* for the previously unresolved **specialist router**
state, not profitable trading signals. **The 48.01% was the share of V9
entries with specialist=UNRESOLVED, not the share whose primary price
pattern was literally UNKNOWN.** We do not present extra subtype names as
an accuracy improvement without independent label-quality evidence. Each existing V9
entry receives exactly one V11 profile record, which preserves its
as-of-time snapshot and the evidence-source names.

The signed path efficiency measures do not use active higher-timeframe
bar closes. Any unobserved interval prevents a contiguous path score.

### 2. Persistent support and resistance with timeframe-specific budgets

`ProtectedZoneBank` owns independent buckets:

- M5: 12 zones; eligibility lifetime 2 days after latest confirmation
- M15: 12 zones; eligibility lifetime 7 days
- H1: 16 zones; eligibility lifetime 21 days
- H4: 16 zones; eligibility lifetime 45 days

Pivot input is **the exact V10 two-right-closed-bar confirmation event**,
never the visually earlier pivot timestamp. Same-kind and same-timeframe
ATR-normalized online merges preserve the original date and extend last
confirmation. Each pool evicts only within its own timeframe; no subminute
noise can evict a confirmed H1/H4 level.

These timeouts and pool sizes are *frozen engineering priors*, not calibrated
profit parameters or asserted optimal settings. The bank is bounded by 56
zones plus the existing V10 base cache. A returned zone indicates confirmed
price geometry, **not actual resting liquidity or trading volume**. Quote
counts never masquerade as traded volume.

### 3. Executable-side frozen structural invalidation

For BUY:
- Open entry is paid at **Ask**, currently liquidated at **Bid**.
- Only a confirmed SUPPORT zone with its entire range **below Bid** is eligible.
- The proposed research invalidation price is frozen strictly below that zone.

For SELL:
- Entry is paid at **Bid**, liquidated at **Ask**.
- Only a confirmed RESISTANCE zone with its entire range **above Ask** is eligible.
- The invalidation price is frozen strictly above the zone.

The selector additionally requires a positive spread-adjusted clearance and a
bounded plausible distance from the current quote. If a valid level cannot
be found, the result is **NO_VALID_STRUCTURAL_STOP**, never a fabricated
thesis failure. Zone IDs, original lower/upper boundaries, side and
invalidation value are frozen at entry, immune to later merging/repainting.

The read-only invalidation observer requires **two separately completed,
contiguous observed source seconds** beyond the frozen boundary, with both
the liquidation quote and the midquote confirming price displacement.
Large spread-only quote shocks invalidate the observational window
(`SPREAD_STRESS_UNCERTAIN`); source gaps reset confirmation. A generic
later failed breakout of some *other* zone is not used as proof that this
entry's thesis failed.

**This level is not and must not replace the broker stop.** Original V9
protective loss exits, account governor, re-arm, cash-harvest and timeout
remain independent and authoritative. V11 never tells MT5 to cancel, widen,
tighten, move or defer any protective order.

## Exactly what changed

Added source-only files:
- `structure_refinement_v11.py`: protected zone bank, evidence subtyping,
  entry-valid frozen thesis, price-path/quote-spread invalidation observer.
- `structure_overlay_v11.py`: subclass of V10 attaching diagnostics to the
  *unchanged* original V9 entry and holding callbacks.
- `run_structure_refinement_v11.py`: bounded existing Coinexx source replay
  of V9, V10, V11 simultaneously, hard-failing any order-event drift.
- `test_structure_refinement_v11.py` and `test_runner_v11.py`: safety
  tests, including sell Ask-only spread spike, same-ms false confirmation,
  wrong-side anchor rejection, expiry, HTF quota and original trade parity.
- `.github/workflows/r9_v11_structure_evidence_ci.yml`: no market data
  downloads and source identity guards.

Original R9, V8, V9, V10 sources **must remain byte-identical**. CI verifies
the frozen R9/V8 hashes, unchanged V10 Python source SHA, disabled native
demo orders, and inherited V9 test suite.

## Bounded source replay

Use only the **existing** Coinexx files (not re-exported ticks), with
`R9_RESEARCH_ROOT` pointing to the preexisting research source root:

```bash
python research/coinexx_r9_chronological/structure_v10/run_structure_refinement_v11.py \
 --ticks /path/to/EXISTING/XAUUSD_MT5_BROKER_2026_01_ticks_ALL.csv.gz \
 --expected-sha 1307a75df5d635678de7691908600090a552f38543e0512187dcd7b37fbc66b8 \
 --limit 200000 \
 --out /tmp/r9_v11_bounded_january.json
```

The runner preserves source order and requires equality of original V9,
V10 and V11 ordered entry and exit ordinals, execution prices, reasons,
open-position state and baseline stats. JSON contains compact aggregate
counters, not a new quote cache or full per-tick archive.

Monthly full-replay, native MetaEditor compile and broker/MQL5 indicator
source-clock parity are independent **not-yet-completed** release gates.
Do not substitute synthetic 37+ inherited test successes for nine-month
source coverage or claim reduced prediction error.

## Why institutional / academic / community literature informs this

- **Federal Reserve Bank of New York, Carol Osler (2000–2003):**
  documented intraday FX S/R conditional behavior and differential
  stop-loss / take-profit clustering. Use *zones with confirmation*,
  distinct break/reversal hypotheses, never imaginary hidden orders:
  https://www.newyorkfed.org/research/epr/00v06n2/0007osle.html
  https://www.newyorkfed.org/research/staff_reports/sr125.html
  https://www.newyorkfed.org/research/staff_reports/sr150.html
- **BIS 2025 global FX market structure:** OTC venues are fragmented and
  much trading is internalized, so Coinexx quote-price proxies must not be
  interpreted as market-wide traded volume/DOM:
  https://www.bis.org/publications/qr-202512/fx-trade-execution-landscape-through-prism-2025-bis-triennial-survey
- **Lo, Mamaysky and Wang (NBER/J. Finance, 2000):** explicitly defined
  computational chart pattern studies and conditional distribution testing,
  motivating mechanism-specific, testable causal labels:
  https://www.nber.org/papers/w7613
- **Adams–MacKay (2007), Bayesian online changepoints:** motivates
  preserving uncertainty and separating change/age state from mere
  directional displacement. Not claimed implemented as a calibrated
  posterior in V11:
  https://lips.cs.princeton.edu/bibliography/adams2007changepoint/
- **MetaQuotes official:** `CopyRates` start position 1 for completed
  bars and `CopyBuffer` closed indicators; no native code is changed
  in this Python-only prototype:
  https://www.mql5.com/en/docs/series/copyrates
- **Practitioner check, r/algotrading / r/Forex:** recurring caution on
  HTF lookahead and zone touch-failure assumptions; opinions are
  hypothesis sources, not proof of an XAUUSD edge:
  https://www.reddit.com/r/algotrading/comments/1xsardy/how_do_u_define_a_higher_timeframes_trend/
  https://www.reddit.com/r/algotrading/comments/1vtkunw/do_support_and_resistance_zones_really_weaken/
  https://www.reddit.com/r/Forex/comments/1xmsseq/profitable_sr_traders_what_evidence_tells_you_a/

## Priority checks before policy promotion

1. Quantify the *original 162,309 UNKNOWN entries* by new evidence subtype,
   month, session and BUY/SELL **on the same pinned Jan–Sep original sources**.
   All categories remain preliminary until validated.
2. Compare zone stability and useful contextual reach relative to the
   original saturated 40-zone cache, with both preserved HTF zone age and
   actual original V9 entry locations.
3. Audit valid-versus-invalid frozen references and structural confirmation
   latency on matched entry events. A large drop in speculative invalidations
   is not evidence of improved exit timing without a future-only benchmark.
4. Run a frozen-policy, true chronological out-of-sample study with
   independent pattern labels and confidence/abstention; no PnL-driven tuning.
5. Establish source-clock parity (source ordered tick vs MT5 OnTick) and
   native MetaEditor build *before* adding a read-only MT5 V11 equivalent.
6. **Any future action affecting orders requires a new explicitly approved
   source fork and broker safety certification.**
