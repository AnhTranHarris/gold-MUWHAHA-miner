# R00-054: Verified seven-month human-in-loop high-throughput entry-direction research continuation
**Date:** 2026-10-19. **Status:** RESEARCH_ONLY; no executed trades/holds/exits/P&L, no blind test, no promotion to MT5 live.

## Governance and code ancestry
- Explicit human in loop designation: **retain R00-054 as primary high-throughput entry-candidate foundation**, not demote to the later low-density R00-081 frontier.
- This *separate* branch was created from approved R00-082 emergency recovery commit `7722d095c09189c82d2e31337cd6875a6223e278`. Do not modify existing baseline/backtest engines.
- Recovered **original immutable** R00-054+055 source, January broker-specific model joblibs, frozen Feb model policy `lgb_oracle_weighted`, and original monthly event caches from MT5_EXPAND: https://drive.google.com/file/d/1-emfM0lzKC87JiKewWDYTophCqvp80JD/view (core SHA256 `b9dc16e230b27a6659d6fb583f2120a1fda8a82e775fd2bbe8bb5ae61f2f190c`). Original 8 monthly native caches from the **approved** source directory were verified against full internal member hashes.
- Original experimental plan SHA256 `717b3f218906282ef96840668f1773adcf9fa34eee892df3d23bccc3f4ecd3ac`.
- Replayed March, April, May with original `build_native_features.py` operations in **additive copy**, using only approved source pin additions and empirically validated March DST transitions from GitHub `htf_ticklab/clock.py` at `ca4b58aec597174b6f6d18ab2f36cba6836e4f4c`. Six raw original Coinexx/Dukascopy gz files verified byte-for-byte against registered SHA pins before use. Jan/Feb/Jun/Jul cache hashes and frozen June/July original source event vectors exactly match the immutable originals; Feb calibration scores also reproduced.
- Original R00-040/046 ancestor not fully recovered; **genealogical reconstruction of original event generator BLOCKED_PENDING_RECOVERY**, not this original R00-054 frozen-model inference based on byte-verified recorded events.

## Diagnostic definition — no executable P&L claim
One original first-source-quote in populated 5-second slot produces one BUY or SELL signal. Correct only when original first observed native midpoint `[t+30s,t+32s)` moves by **>$0.10** in forecast direction. Neutral or missing label is incorrect. These are highly overlapping source event opportunities, **not** independently funded real MT5 trades or profit outcomes.

Original R9 SYNTH comparison = exact number of completed synthetic positions from original hourly Report 2 annex, normalized to UTC by approved Coinexx offset; not equivalent to 86.7% profitable SYNTH tester win rate or execution feasibility.

## Original source-month counts by independently scored broker
| Source month | Coinexx signals | Coinexx correct | Coinexx accuracy | Dukascopy signals | Dukascopy correct | Dukascopy accuracy | Period role |
|---|---:|---:|---:|---:|---:|---:|---|
| 2026-01 | 345365 | 181869 | 52.66% | 344037 | 178642 | 51.93% | Jan TRAIN in sample |
| 2026-02 | 328879 | 155538 | 47.29% | 324582 | 143923 | 44.34% | Feb model-selection in sample |
| 2026-03 | 363943 | 172563 | 47.41% | 363174 | 165931 | 45.69% | historically exposed frozen extrapolation |
| 2026-04 | 347267 | 158869 | 45.75% | 345092 | 152013 | 44.05% | historically exposed frozen extrapolation |
| 2026-05 | 345324 | 158029 | 45.76% | 343395 | 151044 | 43.99% | historically exposed frozen extrapolation |
| 2026-06 | 312004 | 142224 | 45.58% | 297035 | 132105 | 44.47% | original Jun transfer reproduced byte-for-byte |
| 2026-07 | 321069 | 143362 | 44.65% | 301280 | 130408 | 43.28% | original Jul transfer reproduced byte-for-byte |

**Two independent broker total:** **4,682,446 signals / 2,166,520 correct = 46.269%**. **Frozen historically exposed Mar-Jul only:** **3,339,583 signals / 1,506,548 correct = 45.11186%**. Original June+July frozen R00-054 record **1,231,388 signals / 548,099 correct =44.5107%**, reproduced exactly.

Total error distribution: **1,990,627 opposite-side**, **525,299 neutral/missing**. Forecasted BUY 2,899,948 / correctly BUY 1,338,429; forecasted SELL 1,782,498 / correctly SELL 828,091. Forecast errors NOT executed losing positions.

## R9 SYNTH 90% correct-direction supply contract
The exact UTC hour passes only if **both** candidate emitted and correctly directed events ≥ `ceil(0.9 * R9 SYNTH completed entries in that identical hour)`. Reconciled source ZIP month-boundary quote observations by checking **actual adjacent approved** preceding/following monthly quotes; NEVER fabricated missing ticks or changed model decisions.
- **Each broker 3,408 / 3,408 matched UTC hours, 181 / 181 UTC days, 31 / 31 ISO weeks, 7 / 7 UTC calendar months PASS** on candidate correct-direction counts.
- Month-ZIP-isolated scorecards keep 8 Dukascopy month-boundary reference-hour misses across Apr–Jul and provide transparent comparison to corrected continuous UTC scorecards; no silent dropping.
- R9 hourly source originally derived from immutable Report 2 annex https://drive.google.com/file/d/1_Xy0szTUv8IwXRa4I3dZxlhckHL64d2D/view ; newly normalized seven-month source hourly CSV in MT5_EXPAND https://drive.google.com/file/d/1lQCL6MKFmkM_fNpX5KGx48H_FJoz0AJI/view (all 1,003 original R00-054 June/July hour keys and completed R9 reference counts matched exactly). Jan-May R9 clock profile follows approved, but original SYNTH logger identity not independently checked per-hour for those months.
- **This is a reference event-count supply test, not completed executable trade-volume compliance**; margin/fills/latency/P&L/exit/survivability UNKNOWN.

## Verified complete immutable artifacts — cloud readback SHA matched
Original downloaded files and March–May derived caches all source-hash checked. All newly generated per-broker 30-second direction arrays, week/day/hour/month ledgers, workbook, original 054 core and training models, helper scripts and state/clock implementation bundled in:
- **Portable exact original source+models+results** `XAUUSD_R00_054_SEVEN_MONTH_PORTABLE_RESEARCH_20261019.zip`, 56,278,686 bytes; SHA256 **`35f7d1f024604436c6c6d1ccc0f0e05951e558ea3694cce7fa81c3e4486d9c5d`**, full ZIP CRC and 119 SHA per-member manifest PASS. **MT5_EXPAND cloud** https://drive.google.com/file/d/14Nx4rl3OjqkwL6tXMlXHAnc7yHwHWNE4/view; exact original bytes re-downloaded and SHA rechecked.
- **Six large new March/April/May exact NPZ native source feature caches** `XAUUSD_R00_054_NEW_MAR_MAY_ORIGINAL_FEATURE_CACHES_20261019.zip`, 160,119,675 bytes; SHA256 **`97ad209f7696510f538012e61899bae779f7375c97ce9d6e365e93647e465b72`**, ZIP CRC PASS; exact original bytes preserved in FOUR parts, SHA manifest https://drive.google.com/file/d/1oVN8QRz9J5-0nnWR_Az4jm0IeW5JLYQx/view . Parts: [01](https://drive.google.com/file/d/1oeTXgbEbTKjySNZ25S7j9Cycl-JXXAgA/view), [02](https://drive.google.com/file/d/1QuFiFGGzTdvdKcZ34ZwlA5LbMU07Xip8/view), [03](https://drive.google.com/file/d/13YxVQYARobV6sfbugQoll6jhhUPWGryT/view), [04](https://drive.google.com/file/d/1jhiAppV6FXIG3dDNRWY_hZgOTJbmqMCM/view); each downloaded from cloud and independently SHA-matched to original manifest.
- **Excel complete 10-sheet analysis**: https://docs.google.com/spreadsheets/d/1K_HTAPtyXzVkYUdyW5hdmAQUd6kQzL1T/edit ; individual direction vs. R9 full hour, day, ISO week, month, provider, model errors, train/test roles.
- Full research report PRIMARY https://drive.google.com/file/d/1xs2ym0n3bzGHd89EemSpgySp8o9WpaRk/view and MT5_EXPAND https://drive.google.com/file/d/15-TdEInY99lyn4yQeHcgdxJrCuz25iYU/view .
- All six new cloud copies located in authenticated MT5_EXPAND folder: https://drive.google.com/drive/folders/1_CHwI4CbI4_dRtAzSuC1ENfeeJec-tS9 .

**Original market tick source bytes remain exclusively at authorized original Drive locations**, pinned 16-source registry. Do not import the derived caches as new independent market observations.

## Next action / research continuation
Keep R00-054 unchanged as high-density entry-signal foundation. Use complete causal error ledger by broker/month/hour/session and matured confirmed M15/H1 state to research **independent** specialist state lifecycles (impulse, reversal, structural, quote response, regime, maturity), independently reset, with conditioned direction-correction rather than confidence dropping or duplicate model votes; maintain all original timestamps, original BUY/SELL signal population and >=90% R9 hourly/day correct-count floors. Target 80% initial directional accuracy via information-additive causal improvements, no claim of success without rechecking both independent providers on new authorized blind month. Holds/exits/funded profitability expressly deferred.

No previous branches rewritten, no live EA touched. Protect the original R00-054 frontier and all failed/successful R00 tests as original evidence.
