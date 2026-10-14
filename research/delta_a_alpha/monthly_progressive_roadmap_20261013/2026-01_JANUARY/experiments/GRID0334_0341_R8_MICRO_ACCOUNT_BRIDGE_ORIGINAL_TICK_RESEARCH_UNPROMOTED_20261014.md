# GRID0334–GRID0341 — January R8 $100 micro-account bridge to original Dukascopy Vertical Grid

**STATUS: ORIGINAL-SOURCE RESEARCH ONLY / UNPROMOTED / OWNER QC NOT COMPLETE.** Do not modify active `FourSessionV1`, the `CURRENT_STATE.json` scientific cursor `J0183`, August's SEALED state, or trading-OFF status on the strength of this report.

## Authorities — read originals, not this report as engineering source

- Owner full original ratified discussion: https://docs.google.com/document/d/1J9d_P4ooCnNmcxPwG1F178aE4ktpkLrFclcyQPaQJ8k/edit
- Original owner whitepaper Git: https://github.com/AnhTranHarris/gold-MUWHAHA-miner/blob/delta-A-alpha/research/delta_a_alpha/whitepapers/DAA_V1_OWNER_GOOGLE_WHITEPAPER_FULL_VERBATIM_030.txt
- Anti-drift and monthly evidence law: https://docs.google.com/document/d/1eG5F76uvm9M-1JXs4LvAaTzPEurU5l4Pgj2sUUelc1o/edit
- January source and QC law: https://docs.google.com/document/d/15psoEliXaPEXJr22cKlJb4OGmWo26j3Eu8GlTtH26Kw/edit
- Complete Jan–Jul roadmap: https://docs.google.com/document/d/1PcaksxuiayFXVW3QtKfzitARvQj6NyL4IIbGhG8K9z4/edit
- **Original R8 MQL5** (not current branch): https://github.com/AnhTranHarris/gold-MUWHAHA-miner/blob/carson/mt5-r8-s1-wave-confirm-certification/Experts/GoldMuwahahaMiner_R8_Microstructure.mq5 Git blob `6b2460074ed35d04cb9b4f7620194a483df17c2a`.
- Prior Jan R8 forensic mapping, source-code port: https://github.com/AnhTranHarris/gold-MUWHAHA-miner/blob/delta-A-alpha/research/delta_a_alpha/monthly_progressive_roadmap_20261013/2026-01_JANUARY/experiments/R8_JANUARY_MT5_TO_DUKAS_SOURCE_EXACT_MAPPING_REPORT_UNPROMOTED_20261014.md
- Last inherited GRID0320–0329 source and full ledger ZIP in the new archive's `ORIGINAL_PREDECESSOR/`, original Drive: https://drive.google.com/file/d/1gptbz4HcVutV7IBYzSEvAPK2pW4-5pBB/view
- **Original tick file** `XAUUSD_DUKAS_2026_01_ticks.csv(3).gz`: 9,135,062 UTC ordered Bid/Ask ticks, SHA-256 `d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5`. Not substituted with R8 tester ticks.

## Objective

Investigate if R8's historical ability to trade a **$100 starting deposit with 0.01 lots, one position at a time** can improve the currently funded L7 January micro-account risk regime *without* importing or copying historical MT5 R8 trade timestamps, result labels or synthetic quotes. Continue R9 SYNTH 100% of each day's/week's/month's net, trades, risk and R9 OVERFIT six offline dimensions. Independently sample 10 January seven-day $100 starts aiming toward $10,000 without martingale. Cash profit is not a substitute for solvency, live fill proof or missing weekly/daily R9 parity.

## Original mechanism evidence

The R8 original MQL5 `FindOurPosition` / `Reconcile` / `ManagePosition` allows one R8 position and no additional entry until the existing position closes; default cooldown 1 second, five trades per minute, 60-second max hold, 20 completed bid-second liquidity bars, five completed bid-second velocity and directional-efficiency, 4 states, trailing activated after $0.18 and trailing by $0.05 (under source $0.01 per hunter pip). Historical MT5 R8 January reported 34,763 completed trades and +$26,578.23 from its $100 initial deposit; a **single historic tester run** and **not Dukascopy validation**. Prior causal port at a hypothetical $0.25 spread limit ended January $66.01 from $100 on original Dukascopy, 105 closed positions. Spread and execution feed transfer are the primary bottleneck.

## GRID0334 — source custody

Reconstituted original preselected GRID0283/0325 candidate genealogy using byte-verified cached raw tick arrays and the unchanged actual native `materialize()` code. 9,135,062 quote rows, 236,324 proposed events, 12,490 parent events, 189,341 potential child events. The **candidate source itself was selected historically during January research**, and scheduled future exits are inherited; it is NOT an entirely endogenous independent `FourSessionV1` trading system. Source 'materialization cache' is not permission to use original R9 labels or future outcomes in admission.

## GRID0335 — R8 five-second directional-efficiency + initial R8 single-slot policy

As-of feature time is at least **one second before** each inherited candidate's modeled quote-side fill. For each source event take the most recent five *completed* observed bid-second closes, derive signed bid displacement from the oldest close to the as-of Bid, divide absolute displacement by four complete-second absolute close changes plus the last-to-current Bid change, as in original MQL5 `MicroVelocity()`. Do not fill unseen seconds; no future quotes. Apply new gates to ordinary source proposals only; parent-child genealogy and physical funding are preserved as their own separate gate. Existing prior five-second shock threshold remains unchanged. This is a pre-entry **veto hypothesis**, not autonomous R8 direction generation.

Ten seeded complete seven-UTC-calendar-day windows: Jan 05, 08, 09, 12, 15, 19, 20, 21, 22, 23, each resetting modeled cash to $100. Same fixed 0.01 lot ≈ 1 oz research contract, hypothetical 500:1 leverage, $0.20 round trip, 20% admission margin budget, modeled 50% stop-out, original Bid/Ask, no martingale.

| Research condition | Positive accounts | Modeled stopout-free | 7d closing trades, total | 7d final range | Worst hourly tick DD | Full tick DD | $10,000 achieved |
|---|---:|---:|---:|---:|---:|---:|---:|
| `CONTROL` preserved GRID0325 ordinary shock gate; two initial slots | 10/10 | 10/10 | 711 | $243.14–$396.04 | $82.36 | $107.15 | 0/10 |
| `R8_ONE` one initial slot; second earned at previously CLOSED cash >=$150 | **10/10** | **10/10** | 327 | $142.89–$243.59 | **$42.18** | $45.86 | 0/10 |
| `EFF30` completed-second efficiency >=0.30 for ordinary source | 10/10 | 10/10 | 706 | $227.25–$396.04 | $82.36 | $107.15 | 0/10 |
| `EFF60` >=0.60 | 10/10 | 10/10 | 689 | $227.28–$411.71 | $82.36 | $110.35 | 0/10 |
| `R8_DIR30` signed velocity agrees with proposed direction, eff >=0.30 | 10/10 | 10/10 | 708 | $196.16–$450.39 | **$144.13** | $165.82 | 0/10 |
| `R8_DIR60` | 10/10 | 10/10 | 674 | $196.41–$445.47 | $144.13 | $181.72 | 0/10 |
| `R8_DIR30_ONE` | 10/10 | 10/10 | 327 | $139.08–$257.06 | $42.18 | $45.86 | 0/10 |

**Conclusion:** R8 one-position-at-inception is a meaningful physical heat-reduction combination. It cuts worst-hour DD 48.8% relative to the preserved control but sacrifices 54% of throughput. MQL5-style efficiency gating does not reliably improve the risk/throughput frontier, and direction alignment raises worst-hour risk. Keep all failed combinations recorded; do not rerun identical hypotheses. Historical full source selection prevents official promotion.

## GRID0339 — true strict R8 single-position MAX 1 at all account balances

**Additional independent completed test**, not the same as `R8_ONE` above (which can earn higher capacity after $150). The exact original one-position lifecycle constraint is held permanently. Ten-of-ten modeled episodes end positive with no modeled stop-out, total **242** completed closes, ending equity **$142.89–$196.83**, worst-hour floating equity DD **$23.00**, full-tick DD **$29.92**, peak concurrent positions **1**, zero reaching $10,000. Worst hourly DD down **72.1%** from the protected GRID0325 baseline but trades down **66.0%**. This is a survivability-oriented low-risk control; cannot be advertised as full R9 throughput.

## GRID0337 — source session clock cross-feed control

R8 MQL5 calls `TimeCurrent()` and source input `InpQuoteUtcOffsetMinutes=0`. Prior Jan original tester entry-versus-raw-quote mapping favored historical MT5 server clock **UTC+2**, provisional and not broker-confirmed. Test shift=0 vs +120 minutes for the completed-M5 ATR session gate, at $0.25/$0.50/$0.75 hypothetical spread ceilings. **All six causal full-month original Bid/Ask variants produced identical cash/close outcomes for paired clock shifts.** E.g. original-like $0.25 limit: 105 closes, final $66.011 from $100; $0.50: 103 closes, final $8.799; $0.75: 102 closes, final $8.680. Session clock correction by itself is not the missing R8 edge under the tested spread/economics.

## GRID0336/GRID0340 — capacity transition experiment: reproducibility blocker, no claim

Tested 'one position first; subsequent second slot unlocked after previous booked cash reaches $110, $125 or $150' (never on loss or future P&L). Some early seeded seven-day episodes ran and produced profits, but complete ten-date execution **stalled** in the quote-margin liquidation interpreter, and tests were terminated rather than fabricate eight-to-ten-starter summaries. GRID0336 and GRID0340 are **INCOMPLETE**, not candidate promotions, even though their early rows are retained. Root-cause investigation should instrument the chronological `scan_and_apply` liquidation loop and fail-closed on no progress; stop testing more similar thresholds until the executor is deterministic. The original source files remain untouched.

## GRID0338/GRID0341 — QC and acceptance boundary

GRID0338 reconstructed cash/quote-side entry/exit economics, all per-trade fees, pre-entry and post-entry hourly equity marks on 8 of the 10 seeded dates across three chosen policies, successfully matching source engine through 1,624 accrued checks. The remaining two sampled dates **did not complete**, so an 8/10 independent audit is not 10/10 certification. GRID0341 separately passed **73 independent research-integrity and acceptance-boundary checks**, including the original gzip SHA-256, recorded cohort, exact original GRID0325 control reproduction, ten-episode complete numerical summaries for GRID0335 and GRID0339, exact clock-shift paired parity, and correct FAIL acceptance on the unattained 7-day growth target. These checks are **NOT owner acceptance**, broker margin calibration or a production engine audit.

## Explicitly missing before promotion

1. Reconstruct original R8 source trade lifecycle **endogenously** inside the owner-frozen L0–L7 `FourSessionV1`; retained original R8 market generated tick signals themselves lost money with reasonable Dukascopy spread under current assumptions. Separate the role of R8's single-position *risk discipline* from its untransferred synthetic tester profitability.
2. Recover meaningful **new post-cost high-turnover opportunity generation**, not just slower/sparser filters, while preserving R8 micro-account heat protection and previously accepted funded Watchdog source genealogy.
3. Resolve `scan_and_apply` replay stall for earned second-slot cases, and produce independent full 10/10 intratick equity and booked-deal ledger QC after repair.
4. Obtain genuine Coinexx account symbol `SYMBOL_POINT`, trade contract size, historical raw tick spreads, exact margin/stop-out mode, commission/fill rules, realistic adverse slippage. Existing tests assume 1 oz/0.01 lot, 500x; ten historical positives do not prove future 100% survival.
5. Per actual owner requirements: R9 SYNTH >=100% for **each January day, ISO week, month, trade count and risk**, R9 OVERFIT six individually scored offline trade features >=75%, all-timeframe original tick source engine, and Feb–Jul month-blind regression. No currently complete experiment passes every gate.

## Source/experiment provenance and append-only custody

Full source exact scripts, JSON trial results, partial logs and failure states, prerequisite source archive and SHA-256 file manifest are in the accompanying same-folder original zip. Original raw Dukascopy file and R8 source remain their original upstream assets and are not modified. **Owner scientific cursor J0183 remains; August SEALED; trading OFF.** This report is a locator for the original Python code/settings and objective evidence, NOT engineering-source replacement.


---
**Full original self-auditing Python code/results and source-cache archive:** https://drive.google.com/file/d/1EqpiNQt-d4M7yer2Na7mv4NIzOWU53Pr/view
**Archive SHA256:** `644a8e3b2dca016063da90dad8082feecadf2ed2500cb68f7937393b6d63621e`
**Original exact nine new research scripts:** https://github.com/AnhTranHarris/gold-MUWHAHA-miner/tree/delta-A-alpha/research/delta_a_alpha/monthly_progressive_roadmap_20261013/2026-01_JANUARY/experiments/GRID0334_0341_SOURCE_CODE
**Drive same original report:** https://drive.google.com/file/d/1nzAWecEnwJrm4qIypPfncuiUD9XV-Q6R/view
**Original source transfer:** https://drive.google.com/file/d/1aeWpBlM-vQfj-fijz4t3gkB2kMKctAE0/view
**No scientific cursor advance or active runtime change; J0183, trading OFF.**
