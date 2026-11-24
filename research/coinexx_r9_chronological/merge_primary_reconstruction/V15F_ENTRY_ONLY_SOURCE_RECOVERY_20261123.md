# V15F: R9 HybridGate merged-primary entry-only reconstruction (2026-11-23)

**RESEARCH ONLY.** No native MQL5 compile, order execution, or profit/loss claim. Entry-only: holding/exits unchanged. Original approved EA is untouched.

## Recover COMPLETE executable sources, not this handoff

- [MT5_EXPAND 59-member full-source ZIP](https://drive.google.com/file/d/1ijVx9NalyL5wIThhWPVjxuMKSRZCAybn/view), 9,477,453 bytes, SHA-256 a3837c50633af0bdacf66731a4cfd70fbea936a7626309bc778094ccc81251a9; all 58 payload SHA-256 checks pass. Includes actual V14/V15 C++17-zlib source, Python fit/export/replay source, model coefficients, 268,270 source-generated entry signals, full month receipts and QA scripts, with NO raw tick library copies.
- Original approved R9 MQL5 `Experts/GoldMuwahahaMiner_R9_HybridGate.mq5` pinned blob 7eecb5f1947017a01ce85b2520725de54749e523 on carson/mt5-r9-hybrid-gate-certification.
- Frozen Jan and Feb-Sep new merged R9+Coinexx archives contain 272,352 reference mapped entries and directions. Source chronological original Coinexx TickLogger Jan-Sep gzip holds 72,129,347 original quotes; all nine file SHA256 checks pass.

## Research method

Full nine-month intentionally in-sample training as authorized. Reference mapped entry times and directions are offline labels and benchmarking clocks, NEVER inference inputs. Derive 250ms/1s/5s/15s/30s/M1/M5/M15/H1 candles, quote-arrival, directional-change/overshoot causally from source ticks. Match entry-only signals one-to-one by same side at +/-2, +/-5, +/-15 and +/-30 seconds. Minimum 90% volume EACH month and >=245,117 over nine months. Explicitly report alignment separately from count.

| Policy | Proposals | +/-2s | +/-5s | +/-15s | +/-30s |
|---|---:|---:|---:|---:|---:|
| Frozen V14 entry clock | 268,270 | 33,701 | 88,833 | 139,703 | 178,909 |
| V15F fixed V14 clock plus independent first/rearm side specialists | 268,270 | 36,087 | 94,373 | 142,182 | 174,217 |

V15F volume 98.50% (lowest monthly 95.59%): count PASS. Matched 5-second target coverage 94,373/272,352=34.65%: **alignment FAIL**. Wider 30-second matches dropped versus V14, so no full-system promotion. Separate V15B time-hazard policy achieved 70,376 5-second matches and is a rejected negative control. All fit/test source and models preserved in above ZIP.

## Independent scientific QA

- Original source quote counts and all 9 SHA receipts validated; C++ event-state extraction 3,178,466 source-derived complete five-second snapshots.
- January 1.2m-quote causal prefix generated 54,771 completed five-second events byte-identical to full-month prefix.
- `replay_v15f_from_frozen_models.py` regenerates all 268,270 exact timestamp+side decisions without loading merged target labels, by reading source-only quote-derived features and frozen V14 first/rearm models. Full equality PASS.
- Native MT5 real-tick tester, funded positions/stopout, trade P&L, holds and exits NOT measured in this entry-only pass.

## Required next mechanism, not yet built

Improve trigger CLOCK rather than simply recomputing direction on the same original times. V14 source clock has time-only upper bound 125,075/272,352 possible 5-second matches even with hindsight-perfect side. Develop R9 minute-state event triggers from completed sub-second/1-second candles, prior R9 setup impulses, directional-change/reclaim/overshoot, causal quote-duration acceleration and separately first/rearm hazards, then grade entry count and one-to-one alignment before trading exits.

**GitHub branch is documentation-only checkpoint. Full executable research sources live in the pinned Drive ZIP; approved R9 v1.90 original MQL5 unchanged.**