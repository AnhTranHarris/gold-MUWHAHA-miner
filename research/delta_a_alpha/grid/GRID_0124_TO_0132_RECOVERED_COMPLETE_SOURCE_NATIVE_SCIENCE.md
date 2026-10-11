# GRID0124–GRID0132 — RECOVERED REPRODUCIBLE SCIENTIFIC HANDOFF

**2026-10-10 Chicago.** Existing `delta-A-alpha` only. This is a recovery of completed source-native quote studies after UI message delivery timeout; it is **not** a restart or a new profit certification.

## Verified recovered state

- Original Dukascopy Jan–Jul 2026 raw source used, August **SEALED**. GRID0108 K2/K4 creator genesis and GRID0109 original 3,332 baseline UTC hours / 1,389 previously weak hour diagnostic preserved. Original R9 SYNTH/REAL and owner V1 source untouched.
- All 9 numbered stage output sets `out124` … `out132` have 7/7 monthly JSON files with expected variant counts. Exactly **5621 method-month panels** available. This is not 5,621 statistically independent hypotheses; strong overlap exists.
- Restart interrupted **after** GRID0132 all seven native original quote months and 12 deterministic tests had passed. Explicit recovery reran the same 12 tests (12/12 PASS) with log `tests_recovery_20261010.log`; no original 57.5m-tick rescan necessary to recover completed results.
- J0124 J0125 causal horizon and preemptive slot competition; J0126 causal campaign confirmations; J0127 medium/long direction agreement; J0128 local gate robustness; J0129/0130 one-second source-quote entry delay; J0131 short-horizon exit; J0132 *exact-quote first-passage stop/target stress*.
- Original models trained Jan–Apr and MAY–JUL previously inspected, so **not** untouched out-of-sample. No broker fill confirmation, margin modeling or global funded equity replay. **trading_enabled=false**.

## Four-minute candidate, native quoted entry at T1+1,000ms (as previously frozen)

Precondition: Jan–Apr trained causal HGB7 expected 600s and 1800s midpoint directional forecasts agree with original later-observed GRID0111 T1 side; 600s magnitude >=1.5 times (T1 observed source spread plus $0.02); chronological first-in virtual cap=4; exit first actual opposite Bid/Ask source quote >= delayed actual entry +240 seconds. Fixed source entry/exit quoted sides, not midpoint, fee $0.02 once. Additional +$0.25 cost stress shown separately.

| Month | Hypothetical quotes | Mean $/oz after source spread/fee | Mean $/oz +$0.25 slippage | Worst single $/oz | Original weak hours touched |
|---|---:|---:|---:|---:|---:|
| 01 | 223 | +5.305 | +5.055 | -96.737 | 5 |
| 02 | 190 | +1.286 | +1.036 | -55.324 | 2 |
| 03 | 270 | +1.643 | +1.393 | -55.167 | 7 |
| 04 | 65 | +0.603 | +0.353 | -12.990 | 2 |
| 05 | 39 | +0.416 | +0.166 | -16.310 | 0 |
| 06 | 63 | +2.301 | +2.051 | -22.020 | 1 |
| 07 | 44 | +0.269 | +0.019 | -18.780 | 2 |

- Source quote entry rows **894**; weighted seven-month mean **$+2.330 per 1oz hypothetical mark**, before additional $0.25 slippage and without broker fills.
- May–July 1,000ms-delayed 240s cap4 subset: **146** source quote marks, **43** distinct dates, +$0.25 stress mean **$+0.935/oz**, UTC day-block 95% interval **[-1.240, +3.143]**, including zero.
- 4-minute cap4 historical original weak-hour support remains very low; this is a **sparse specialist research lead**, not a repair of the monthly->daily->hourly grid campaign or the owner’s R9 75%-daily qualified opportunity floor.

## GRID0132 protective exits: completed, no repair of the tail

- Frozen J0131 entry set and source quotes were compared across all 7 months under 4 adverse barrier levels (-$4,-$8,-$12,-$20), 4 favorable levels (+$2,+$4,+$8,+$12) and four stop-only combinations, plus the original time-only exit = **21 methods x 7 months (147 method-month panels)**.
- Actual tick first-passage after true delayed source quote at actual opposite-side liquidation prices, never an invented threshold fill; fixed virtual occupancy retained (conservative), $0.02 fee once, +$0.25 separate stress.
- **Only `SLNONE_TPNONE` had positive average in all seven months**, including the +$0.25 scenario. Any nontrivial protective stop/target combination failed the all-month condition. Do not promote an unbounded tail-risk trade merely because its mean is positive.
- Worst original individual quote outcome and gross loss are in each month JSON; fixed barriers may still overshoot in gaps and have no broker exchange guarantee.

## Source lineage and archive replay

- The ZIP includes J0124–J0132 executable Python, source/native out124..out132 complete month, day and hour CSVs, 7 frozen predicted source event tape slices, original GRID0117/J0114 dependencies and a source hash manifest. **Do not open arbitrary pickle without independent local trust validation**. The ticker input is deliberately excluded from the ZIP to prevent copying or rewriting user-owned raw Jan-Jul quotes.
- Original input paths refer to `/mnt/data/XAUUSD_DUKAS_2026_MM_ticks.csv*.gz` and earlier checked project workspaces. Recreate the mounted original data/source directories for exact replay. Recovered outputs themselves do not require a rerun.
- The frozen Jan–July history was already used by past development; no clean holdout exists. August original file remains sealed and deliberately uninspected.
- 12/12 test PASS is a bounded regression suite, not broker execution certification or statistical proof. No physical orders, no EA edits, no account PnL or drawdown claims.

## Next scientific task (not done by this recovery)

Independent GRID0133 time-conditioned wrong-way early-exit / deferred-trailing research, preserving the original four-minute entry and actual quoted fill. Judge bounded gross-loss tail **and** whether positive multi-month source mean and daily/hourly activity survive. If it fails, archive and keep pursuing complex complementary mechanisms, not forced performance.
