# R9 V10 full original Coinexx Jan–Sep 2026 market-structure audit
**Research-only | 2026-11-15 | no PnL optimization | no native execution changes**

## Source-exact result
- All **72,129,347** original Coinexx XAUUSD quote rows in **nine complete original month files** (January–September 2026) processed in source order.
- All **nine SHA-256 digests match the independent, pre-existing V9 nine-prefix receipt** at `micro180_20261114/V9_NINE_PREFIXES_20261114.json`.
- Each full monthly file replayed **both frozen V9 and V10 shadow** in parallel. All nine matched **every ordered completed trade entry/exit ordinal, side, entry/exit price and close reason**, as well as ending-position state.
- **338,065 trade entries; 338,064 completed trades**. One trade remains open at a monthly data boundary. Data from different months was not stitched into a new raw file.
- Full supervisor run: **1064.2 seconds wall-clock**. Each independent monthly source was replayed from its beginning to EOF, not a 200,000-row prefix.
- The risk governor was OFF for high-volume research capacity; no native MT5 compilation or broker execution parity is claimed. The native V10 observer remains opt-in and OFF, and V9 demo orders remain OFF.

## Monthly full-period attribution

| Month | Quotes | Entries | Completed trades | Unresolved | Range | Trend aligned | Local reversal label | Nested countertrend | Breakout-family entry |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2026-01 | 7,699,274 | 35,500 | 35,500 | 17,244 | 7,077 | 5,662 | 2,952 | 2,387 | 178 |
| 2026-02 | 7,102,818 | 42,742 | 42,742 | 20,848 | 7,947 | 6,568 | 3,365 | 2,648 | 1,358 |
| 2026-03 | 8,859,103 | 51,841 | 51,841 | 24,999 | 10,057 | 8,233 | 4,312 | 3,620 | 615 |
| 2026-04 | 7,831,685 | 37,341 | 37,340 | 17,699 | 7,305 | 5,591 | 2,801 | 2,650 | 1,285 |
| 2026-05 | 8,011,360 | 32,514 | 32,514 | 15,361 | 6,758 | 4,813 | 2,662 | 2,396 | 522 |
| 2026-06 | 9,347,508 | 37,190 | 37,190 | 17,899 | 7,432 | 5,896 | 3,038 | 2,603 | 322 |
| 2026-07 | 8,075,197 | 33,758 | 33,758 | 16,009 | 6,746 | 5,126 | 2,676 | 2,249 | 947 |
| 2026-08 | 7,468,061 | 32,896 | 32,896 | 15,768 | 6,631 | 5,279 | 2,571 | 2,277 | 369 |
| 2026-09 | 7,734,341 | 34,283 | 34,283 | 16,482 | 6,975 | 5,363 | 2,714 | 2,519 | 228 |

**Whole-period actual V9 entry-time specialist labels:** unresolved 162,309 (48.011%), range interior 56,035 (16.575%), range boundary 10,893 (3.222%), aligned trend 52,531 (15.539%), local reversal 27,091 (8.014%), nested countertrend 23,349 (6.907%), breakout retest 4,039 (1.195%), breakout initiation 1,188 (0.351%), breakout acceptance 589 (0.174%), exhaustion 33, failed breakout 8.

**Market-structure observations, not trades:** 669,257 confirmed support pivot seeds, 667,334 confirmed resistance pivot seeds, 64,220 support-zone retests, 58,300 resistance-zone retests, 13,755 breakout probes, 10,995 accepted breakouts, 10,449 retest events, 2,584 retest resumptions, 3,109 failed-break observations, 88,555 source quote-gap resets.

**Holding advice *transitions*, NOT actual exits:** 228,830 HOLD_OBSERVE, 99,613 THESIS_INVALIDATED, 28,564 DEFEND, 7,189 RISK_REVIEW.

## Critical findings / release blockers
1. **48.0% unresolved** is a coverage limitation, not a measurement that those trades are wrong; no trade reduction is authorized.
2. All nine monthly observations saturate the **40/40 zone memory budget**. S5 and other small-timeframe pivot seeds may displace important HTF levels. Examine separate zone budgets by timeframe, lifetime and relevance, not blind threshold searches.
3. The default specialist's proposed structural-stop reference selects nearest support (BUY) or resistance (SELL) but does **not establish the level lies behind the actual entry quote**. Consequently THESIS_INVALIDATED transition counts can be spurious. **Do not connect this advice to MT5 exits until corrected and source-exact revalidated.**
4. `STRUCTURAL_REVERSAL` confirms a local S15 swing orientation plus a recent change alarm opposing the parent. It is **not proof that the H1/H4 trend reversed**; labels need independent future-only evaluation.
5. Breakout probes, acceptance, retests and failures are **overlapping market events**, not mutually exclusive outcomes or win rates. Low breakout specialist coverage at actual entries indicates timing or zone-context mismatch needing forensic review.
6. Each month starts fresh, so the nine months are fully processed but **not one continuous nine-month account-state simulation**. Higher-timeframe warm-up and open positions do not carry across file boundaries.
7. The test verifies **zero decision drift**, not improved classification truth, entry quality, holding quality, profitability, MT5 native parity or out-of-sample deployment performance.

## Reproducibility
Original full-month file SHA-256 values exactly match the historical V9 pinned nine-prefix JSON. Full audit command (once for each month, existing files only):
```bash
R9_RESEARCH_ROOT=research/coinexx_r9_chronological \
 python research/coinexx_r9_chronological/structure_v10/run_structure_audit.py \
 --ticks /path/to/original/XAUUSD_MT5_BROKER_2026_MM_ticks_ALL.csv.gz \
 --expected-sha FROZEN_MONTH_SHA256 --limit 20000000 --out /tmp/month_v10.json
```
The 9/9 full month checks used the exact Python source bundle from the V10 passing CI. No Coinexx or Dukascopy data was uploaded to GitHub, no duplicate historical archives created in Drive, and no live or demo orders enabled.

**Next scientific gate:** certify structural classification accuracy at event time, correct wrong-side zone protection, and establish native indicator/structural event parity before allowing V10 to change any entry or exit policy.
