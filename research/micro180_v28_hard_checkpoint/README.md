# MICRO180 V28 — HARD HUMAN-APPROVED ENTRY CHECKPOINT (2026-11-17)

## Scope and authority

The owner has declared **entry development milestone accepted** based on the January–July cumulative research and the untouched August–September V28 forward entry replay. Acceptance is a project-governance decision, **not** a claim of high target-identity precision, MT5 compilation, broker-executed profitability, or completed hold/exit logic. **Entry-only shadow EA**: it emits an intent trace but does not place trades. Do not couple this checkpoint to an invented exit algorithm.

The **immutable behavioral authority** is the original C++ `v28_forward_frozen.cpp` and original `MICRO180_Jan_through_07_merged_weights.tsv`, SHA256:

`92719ae1edd78c91e63f151da7d2f3607c7d5f42119b07613b8b20a7cce3997b`

The source file `GoldMuwahahaMiner_MICRO180_V28_FrozenEntry.mq5` (native port revision 28.11) is the native MQL5 port. Model and EA are version-coupled. Do **not** regenerate prototypes, change score weights, "fix" last-prototype selection, change the family's role mapping, or blend monthly specialists. Fork this milestone to experiment; never silently edit the accepted checkpoint.

## Complete policy encoding inventory

| Frozen component | Native EA representation |
|---|---|
| Jan–Jul append-only monthly specialists | All 2,658 `G` experts loaded from exactly the July-final TSV |
| Eight role heads | `A_EARLY`, `A_LATE`, `B_FIRST`, `C_FIRST`, `D_FIRST`, `B_SECOND`, `C_SECOND`, `D_SECOND` |
| Two directions and six observable regimes | BUY/SELL; trend, nested trend, reversal, consolidation, breakout, transition |
| 25 normalized model components | Exact 25-element `FEATURE_MAP`, `CENTER`, `SCALE`, expert `center/width/threshold` |
| Full 38 quote feature slots | 5/15/60/180/300s returns, efficiencies, 1/3/5m quote VWAP proxies, EMA3/8/21, channels, contraction, R9 ±0.15, spread, 10S S1, quote intensity |
| Model conditional prior | `PRIOR` for all eight role heads |
| Learned entry-phase clock | `P` (60 seconds × each role/side) and `PHASEMIN` |
| Hour/session intensity | `RATE` (24 UTC hours × eight heads) and capped per-role tokens |
| Synthetic-to-real bridge | First-passage `HitProbability` scoring term and R9 opening ±15-cent geometry |
| One first entry, conditional opposite second | State `gHaveFirst`, `gHaveSecond`, `gFirstRole`, side/opposite rearm, 7-second minimum spacing; never any fabricated exits |
| C++ quote evaluation order and internal gaps | Source computes its phase-evaluation eligibility before resetting the minute basket; a missing intermediate efficiency sample yields zero efficiency. Native port preserves both semantics. |
| Monthly intensity reset | `gModelCalendarMonth` clears tokens at UTC month change, preserves rolling quote history |
| Auditable quote-level intent | Logs and writes TSV (`ms,minute,leg,side,role,state,score,price_u,conditional_on_flat`) |
| Original C++ prototype selection nuance | Native port deliberately chooses **last** matching expert in source-file order, because frozen C++ keeps `Candidate.score==-1e9` throughout its prototype loop. Changing to closest expert would alter the accepted test behavior. |

**Historical original R9 geometry and economics are only reference records:** they are not reimplemented as live stop, trailing stop, fill, commission or profit mechanisms. This is deliberate because exits are not yet being redesigned.

## Install and run (no trading)

Place `GoldMuwahahaMiner_MICRO180_V28_FrozenEntry.mq5` under the terminal's `MQL5/Experts` folder. Place the **exact** `MICRO180_Jan_through_07_merged_weights.tsv` under `Terminal/Common/Files`. Use `install_frozen_entry.ps1` for a checksum-checked, no-overwrite installation. Compile with your local MetaEditor and check the compiler log. Attach only to the correct XAUUSD symbol on MT5 in demo/tester **Every tick based on real ticks** mode. The code initializes a completed-M5 `iATR`, processes causal mid-price history and writes entry intent records; it **never calls an order execution method**.

For a native timing comparison, compare the generated `Terminal/Common/Files/MICRO180_V28_MT5_ENTRY_INTENTS.tsv` with the authoritative reference `aug_sep_fast_intents.tsv` from the previously preserved forward-test ZIP. The original source 10-part TickLogger CSV stores explicit real-R9 S1 quality fields and as-of ATR; the EA must infer S1 from its own completed-second buffer and reads completed ATR through the terminal indicator. Those sources **may differ**. Do not assert native quote-for-quote equivalence until checked.

### Known remaining parity gates

1. **MetaEditor compilation not performed here.** This environment has no Windows MT5/MetaEditor. Source was statically checked, not compiled as `.ex5`.
2. **Quote stream equivalence unverified.** The C++ source consumes every original REAL_TESTER row, while MQL5 `OnTick` may coalesce high-frequency events. For full live tick capture, a separately validated `CopyTicks/CopyTicksRange` catch-up feed may be needed; it is *not* silently inserted into the frozen entry logic. See MetaQuotes [CopyTicks](https://www.mql5.com/en/docs/series/copyticks) documentation.
3. **Feature input parity unverified.** C++ reads `s1_disp`, `s1_eff`, `s1_range` and M5 ATR directly from original TickLogger columns, whereas native computes S1 from its completed-second history and M5 ATR from `CopyBuffer(shift=1)`. An as-of-feature trace comparison is required before calling the two implementations executable equivalents.
4. **CDF implementation variation.** C++ uses `erfc`, MQL5 uses a documented rational approximation for Normal CDF. Near-threshold decision differences are possible.
5. **Second basket is a conditional intent** and requires an independent executor to be flat. There is no holding/exit or PnL model in this artifact.

The above are implementation-parity risks, *not* a request to redesign the accepted entry strategy. The exact C++ and weights have been preserved to allow resolving them without changing the frozen reference.

## Recorded accepted benchmark — do not misstate accuracy

January–July reference: 56,608,185 original real quotes; 123,426 profitable mapped targets; 120,010 independent entry intentions; **1,306** matched within ±2s / 5¢. August–September (July-frozen, no retraining): 14,867,805 evaluation quotes + 6,664,211 July warmup quotes; 29,038 targets; 33,864 independent intentions; **227** matched within ±2s / 5¢. These are entry-intent comparisons with the **hypothetical positive-cycle teacher**, not executed trading PnL or certified exact entry replication. The owner explicitly accepted this as the first design milestone.

## Preservation and rollback

- Primary Drive research folder: https://drive.google.com/drive/folders/1XMtVJhXWC_roG1IXar688UgBFw8Qjlli
- Previously preserved V28 cumulative source package: https://drive.google.com/file/d/1lp0hNX6cBCPFWxJrMwWKe6jgUDSbP_88/view
- Previously preserved V28 August–September benchmark: https://drive.google.com/file/d/1id-5_Gupl4YmUH-xRvpngqFUstjNYCqE/view
- The GitHub milestone branch stores this MQL5 source, complete frozen coefficient file, source C++ replay, original result receipts, and invariant tests.
- SHA validation: `python -m unittest -v test_entry_checkpoint.py`

Do not merge onto the live EA branch. Do not modify the historical R9 implementation or the previous MICRO180 source. This checkpoint is a safe, additive foundation for future hold/exit research only after source compilation and parity are complete.