# Micro180 V8: source-exact measurement and parity repair checkpoint

**2026-11-14 · ACTIONED Stage 1 ONLY · Python/MT5 source alignment, no alpha retuning, no production release.** Branch: `carson/r9-micro180-v8-measurement-parity-repair-20261114`. Source rollback parent: `731cdc51fe30b8c8305c53050123da109b2499e1`. Original R9 production EA Git blob `07222b1a3800c9cc826abe10a4ce6afbd97b0af5` **unchanged**. Original V7 native EA blob `716c21f415e8def3adf987385bf509ff70f49137` and old V7 cash include `ee945d8e2a3dda669b4aa8405c43ea38d1b1a78e` **unchanged**. Native repairs are isolated to `GoldMuwahahaMiner_R9_Micro180_V8_Research.mq5` + `GoldMuwahahaR9V8ConditionedCash.mqh`; demo orders and V7 conditional entry gate OFF.

## Development-log reuse (never redo without new information)
- Frozen R9 Jan–Sep 2026 original: 303,934 trades / -$120,212.46 modeled net.
- 4-lane dual basket Jan–Sep: 419,389 / -$162,656.05.
- Selective Micro180 Jan–Sep: 61,258 / -$24,158.30, zero positive months.
- V3 directional score, V4 delayed fill/opposite tests, V5 250ms and protective runner, V6 unconditional past-cash, V7 conditioned-kernel previous Jan/Sep pilots are **negative** or sub-volume; NOT rerun.
- Preserved previous formula warnings: inverted SELL teacher, choosing action before eligibility, source-path feature collisions, V5 cash-stop high-watermark ratchet (fixed in V6), V6 unconditioned cash prior (replaced by V7), quote-only Last/Volume zero, no native broker fills.
- Do NOT rebuild original monthly Coinexx tick files, Dukascopy archives, 155-feature model, or huge derived caches.

## V8 corrections — code implemented and contract-tested
1. **New-source-minute cooldown**: `Micro180R9._rearm_ready` applies the same 3,000ms cooldown AND 5s and 15s basket rollover conditions within and across source-minute boundaries. A new minute resets the *minute count* but does not grant an early reentry.
2. **Actual 5s basket evidence**: trade candidate requires >=1,500ms between first and last quote in its *active* five-second basket, plus max actual interquote gap <= configurable 2,500ms; equal-ms bursts are not false micro-momentum.
3. **Completed 15s observation validity**: source-ordered candle requires >=9,000ms observed span, max intrabasket quote gap <=2,500ms and last quote within 2,500ms of basket end. An opt-in *active* 15s branch requires >=3,000ms observed span, at least five actual quote updates, and no excessive internal gap. Strict completed-only remains default.
4. **V7 historical anchor linkage**: eligibility and first-passage examples require quote-continuity across **the last setup second into the historical anchor** and throughout its completed six-second past first-passage window, not merely internal prior/future segments. Python and native both check actual first-ms vs preceding last-ms, not only second bucket stamps. Native temporary QBar length is shrunk to populated history before current quote reference; avoids reading a phantom uninitialized candle.
5. **Same-second / same-ms forecast stale cache removed**: both BUY and SELL forecasts and optional hold comparison refresh when source ordinal/ms/executable quote/quote activity changes. Python exact quote tuple; native ms+Bid+Ask+active-second quote count. Thus a second's first forecast cannot govern its later, changed quote. Heavy future performance profiles needed; one 180s kernel per changed candidate, no big persistent cache.
6. **Native research router modes exposed**: V8 MQL5 mirrors Python strict completed-15/strict-30/S1 defaults and makes the prior Python pilot's active 15s, `micro_only` S1 and balanced 30s veto explicit *opt-in research inputs*. V5 ordered 250ms quote path is now enabled in the V8 source fork as Python V7 already does. No change to V7 source.
7. **Source protection**: existing $2 intended cash loss, $0.10/$1.75 harvest objective, 25% capital emergency, 10% peak, daily gross governor, no old high-AUC model or transaction-volume claims remain. No production order option enabled.

## Verification so far
- Existing 49 Python V3–V7 contract tests plus seven V8 measurement/native-source checks: **56 tests** in V8 GitHub Actions Python suite; source default/rollback blob invariants also tested in CI. GitHub Actions success is **NOT** MetaEditor compile or MT5/Python event parity.
- Local same code implementation: prior 49 inherited plus six targeted source-level regression tests = 55 PASS; the seventh native static test is evaluated on the actual full GitHub repository by CI.
- Only read **existing original source** January and September gzip files for **first 50,000 quotes each**, no rewrite/download. This is an **IN-SAMPLE engineering smoke test**, using the existing ungoverned research-only fast profile, illustrative K=$1 account cash per $1 XAUUSD price displacement and extra C=$0.20/trade on top of historical Bid/Ask spread, not real Coinexx fills.

| First 50,000 original quotes | Frozen V7 fast cash-first (before repair) | V8 repaired fast cash-first (after) | V8 optional conditional protected hold |
|---|---:|---:|---:|
| January | 216 trades / -$72.21 | **202 / -$71.86** | 200 / -$70.90 |
| September | 232 / -$96.54 | **205 / -$82.99** | 205 / -$84.10 |

The V8 shadow vs V8 unchanged V5 entry/harvest comparator matched exactly in both month slices. Entry counts fell by 14 (January) and 27 (September) after removing invalid/immature candidate opportunities. **ALL examined economic arms remain negative.** Reduced gross negative amounts are not positive profit or complete nine-month throughput evidence. V8 strict positive-cash gate produced 0 completed January trades in the first 50k—no nonzero net outcome and no high-volume pass. The V8 runner worsened September compared to V8 cash-first and is NOT an approved exit policy.

## Native parity still BLOCKED, explicitly
The following remain unverified and are not presumed corrected by the 56 Python/static tests:
- MetaEditor compilation with zero errors/warnings, native stop/freeze/margin and broker `OrderCalcProfit` costs, commissions and slippage;
- actual source event/entry/exit parity between Python and MT5 terminal, including `OnTick` coalescence, `CopyTicks` equal-ms pagination, 250ms path sequence and quote latency;
- completed M1 `iADXWilder` buffer, M1 EMA20 and M1/M5 `iATR` seeding/series parity. **A known distinct M5 regime gate remains:** the Python baseline is session-adaptive, while native V8 still defaults to a flat M5 ATR threshold 1.75. Before native entry/indicator parity, align and freeze a shared profile, do NOT silently claim these paths are the same;
- native holding policy is still inherited from V7/V6 rather than a proven exact port of the experimental Python V7 conditional-hold branch;
- account-wide cross-terminal risk locking, broker slippage and exact realized risk cap not certified. A $2 protective order can gap past $2, and neither 25% nor smaller equity drawdown can be mathematically guaranteed by market exit.

**Technical reference:** https://www.mql5.com/en/docs/event_handlers/ontick (NewTick event coalescing); https://www.mql5.com/en/docs/series/copyticks (chronological MqlTick records and terminal sync); https://www.mql5.com/en/docs/indicators/iadxwilder (+DI/-DI buffer semantics).

## Acceptance before Stage 2
1. Compile `Experts/GoldMuwahahaMiner_R9_Micro180_V8_Research.mq5` in actual MT5 MetaEditor and obtain actual compiler artifact, no guesswork.
2. Use tiny deterministic shadow event traces (same source original ordinals in Python and MQL5) comparing per tick all active/closed 5s/15s/30s OHLC, gap/span counters, strict vs balanced breakout permission and BOTH V7 cash estimates; preserve equal-ms source ordering.
3. Align and inspect M1/M5 indicator readiness/values and session-adjusted ATR profile before full original-source parity.
4. After parity, separately design an actual-candidate ordinal first-passage audit and measure high volume + NET jointly; freeze later untouched genuine OOS. NO auto-tuning, no feature library rebuild, no deployment now.

**Disposition:** Measurement/entry-source semantics repaired in V8 and rollback protected. Native execution/indicator parity **not yet certified**. Research profits **negative**, therefore strategy NOT READY for deployment.
