> **CORRECTION / SUPERSEDED MONETARY INTERPRETATION:** BETA 011 found that this study used $0.20 round-trip commission whereas the historical R9 Coinexx 0.01-lot report shows approximately $0.02 round trip. The 0.01-lot price-to-dollar scaling itself was correct. Corrected Jan–Jul results reduce the winning-trade-count gain to +5.78%, below the owner’s >10% winner-count target, and the $100k path becomes insolvent during April under the present Dukascopy-cost model. This document is retained for provenance but is **not a formal breakthrough or MT5 candidate**. See `research/BETA_011_PNL_LOT_AUDIT_CORRECTED.md`.

> **BETA 011 accounting correction (2026-09-29):** the earlier Python scorecard used the correct 0.01-lot price multiplier but overcharged commission at $0.20 round-trip. The actual Coinexx R9 deal ledger shows $0.01 per deal, or $0.02 round-trip at 0.01 lot. Corrected Jan–Jul: net **-$157,216.35**, gross loss **-$175,992.53**, max DD **$157,216.35**, 61,650 wins / 226,696 trades (27.20%). Versus the same-feed R9 control: wins **+5.78%**, relative win rate **+14.98%**, net-loss/DD reduction **18.04%**, gross-loss reduction **15.60%**. Therefore the old +10.13% winning-count claim is withdrawn; the candidate still clears >10% on entry accuracy and loss/DD economics. See [BETA 011](../BETA_011_LOT001_PNL_ACCOUNTING_CORRECTION.md).

# R09_BETA_001_ADAPTIVE_IGNITION_ENTRY

**Status:** CORRECTED 0.01-LOT PNL AUDIT COMPLETE. Entry candidate remains promising, but prior formal-breakthrough promotion is SUSPENDED pending requalification because the original Python model overstated roundtrip commission by 10x. **No MQL5 candidate has been coded.**

## Executive result

This breakthrough keeps the R9 hold/exit geometry fixed and replaces the immediate R9-style entry trigger with a causal **early-ignition + opportunity-cost gate**. On the same Dukascopy Jan–Jul 2026 feed, relative to the feed-normalized R9 control, the primary candidate produced:

- **Winning trades:** 61,650 vs 58,279 (**+5.78%**)
- **Win rate:** 27.20% vs 23.65% (**+14.98% relative**)
- **Net:** $-157,216.35 vs $-191,813.12; loss reduced **18.04%**
- **Gross loss:** $-175,992.52 vs $-208,514.23; absolute gross loss reduced **15.60%**
- **Max drawdown:** $157,216.35 vs $191,813.12; reduced **18.04%**
- **Commission basis:** original Coinexx R9 REAL deal history shows $0.01 entry commission + $0.01 exit commission at 0.01 lot = **$0.02 roundtrip**. The prior Python model used $0.20 roundtrip and was therefore 10x too punitive.

The strategy is **still loss-making**, so this is not a profitable EA claim. The corrected entry accuracy and economics remain materially better than the same-feed R9 control, but **winning-trade count improves only 5.78%**. Because the prior BETA 010 conjunctive gate required >10% winning-count as well as entry-quality/economic improvement, formal breakthrough promotion is suspended until the candidate is requalified or the owner explicitly changes that gate.

## Mechanism

The original R9 control admits a trade after its completed-S1 momentum/efficiency/range gate and completed-M5 ATR gate. This candidate retains those causal quality checks but adds a short-horizon ignition state and an opportunity-cost veto:

1. Completed R9 S1 gate remains valid: displacement, directional efficiency, recent range, turn count.
2. Completed M5 ATR/session gate remains valid.
3. Current tick direction must align with the movement observed over ~250ms.
4. One-second mid displacement must exceed $0.04 in the entry direction.
5. Five-second mid displacement must exceed $0.18 in the entry direction.
6. The ten observed S1 bars used by R9 must span no more than 12 elapsed seconds; stale sparse-second momentum is rejected.
7. Current observed Dukascopy Bid/Ask spread must be <= $1.00 and <= 65% of the recent R9 S1 price range.
8. Entry executes on the next causal tick at Ask (buy) or Bid (sell). No future information, future MFE/MAE, or R9 OVERFIT label is used.

The result supports a specific diagnosis: R9 REAL's entry hole is not simply “too little momentum.” The system needs **fast directional ignition plus a cost/opportunity-quality test** so it does not spend a tiny 30-second trade lifecycle on movement whose spread consumes too much of the available excursion.

## Jan–Jul monthly candidate results

| Month | Trades | Wins | Win rate | Net | Gross loss | Max DD |
|---|---:|---:|---:|---:|---:|---:|
| 2026-01 | 31,250 | 8,606 | 27.54% | $-21,026.53 | $-23,496.48 | $21,026.53* |
| 2026-02 | 27,117 | 7,278 | 26.84% | $-21,488.91 | $-24,438.06 | $42,515.43* |
| 2026-03 | 49,444 | 13,607 | 27.52% | $-37,586.67 | $-42,581.33 | $80,102.60* |
| 2026-04 | 30,134 | 8,032 | 26.65% | $-21,198.48 | $-23,534.21 | $101,300.58* |
| 2026-05 | 31,178 | 8,787 | 28.18% | $-18,993.58 | $-21,231.68 | $120,294.16* |
| 2026-06 | 34,522 | 9,763 | 28.28% | $-21,400.43 | $-23,909.88 | $141,694.59* |
| 2026-07 | 23,051 | 5,577 | 24.19% | $-15,521.76 | $-16,800.89 | $157,216.35* |

*The DD values above are **cumulative Jan-to-month-end drawdown**, not month-local reset drawdown. The full Jan–Jul maximum drawdown is $157,216.35.*

## Nearby robustness

The higher-volume sibling `ADAPT_110_065` also passed the complete Jan–Jul entry gate: **+12.52% winners**, **+19.97% relative win rate**, **13.60%** net-loss reduction and **13.60%** drawdown reduction. A three-point absolute-spread neighborhood showed the expected trade-off: tighter $0.75 improved economics but sacrificed winner count; looser $0.85 increased winners but no longer cleared the >10% economics gate. This means the mechanism family is supported, while the exact spread threshold remains a parameter requiring broker-specific MT5 translation rather than blind copying.

## R9 REAL → SYNTH reference bridge

Historical Coinexx R9 REAL and generated SYNTH are different tester processes from the Dukascopy Python experiment. They cannot be treated as directly additive dollars or identical trades. For the owner's requested bridge bookkeeping only:

- historical REAL→SYNTH net gap = **$359,408.13**; the corrected candidate same-feed net improvement of **$34,596.77** equals **9.63%** of that historical gap as a purely arithmetic cross-feed proxy;
- historical REAL→SYNTH winner-count gap = **88,751**; the corrected candidate adds **3,371** same-feed wins, an arithmetic proxy of **3.80%** of that historical count gap.

These percentages are **not claims of executable REAL→SYNTH gap closure**. Coinexx MT5 must determine translation.

## Community and research reconstruction

The mechanism was derived by cross-referencing transparent logic across several source families, then testing independently rather than trusting reported performance:

- MetaQuotes/MQL5 English discussion on XAUUSD false-entry filtering with time/structure/volatility: https://www.mql5.com/en/forum/504875
- MQL5 Russian ORB example using breakout → retest → repeat-break confirmation: https://www.mql5.com/ru/articles/18486
- MQL5 Chinese momentum/mean-reversion framework and false-break / squeeze / retest mechanics: https://www.mql5.com/zh/articles/18037 and https://www.mql5.com/zh/articles/18842
- MQL5 Japanese XAUUSD volatility-breakout and structural-break examples: https://www.mql5.com/ja/articles/20745 and https://www.mql5.com/ja/articles/21277
- TradingView open-source XAUUSD accumulation/breakout/retest and multi-setup scalping logic: https://www.tradingview.com/script/NF9u4E7Q-IANI-Accumulation-Breakout-Scalper/ and https://www.tradingview.com/script/0ytEVtgd/
- Academic FX microstructure evidence that bid/ask spread, quote timing and short-horizon order flow/price impact matter: https://www.nber.org/papers/w12682 and https://www.sciencedirect.com/science/article/pii/S1044028306000251

No source's profitability claim was imported. Only reconstructible mechanism ideas entered the BETA simulator.

## Evidence and reproducibility

- Original Dukascopy Jan–Jul monthly SHA256 values match the frozen BETA source manifest.
- January full gzip was read through EOF/CRC; 9,135,062 rows and all 17 resolution layers were causally reconstructible.
- Jan–Jul validation uses original ordered Bid/Ask ticks, prior-month warm-up only, actual observed spread in fills, plus **$0.02 roundtrip commission**, reconciled directly to the owner's Coinexx MT5 R9 REAL deal history ($0.01 on entry + $0.01 on exit at 0.01 lot).
- R9 fixed Hold/Exit: $0.30 initial stop, $0.10 trailing activation, $0.03 trail, 30-second max hold.
- August 2026 was not accessed.
- January was discovery, so Jan–Jul is not represented as pristine untouched OOS. The later MT5 broker test is an independent translation gate, not proof of OOS research purity.

## Owner gate

This record authorizes **nothing automatically**. Per BETA 003/BETA 006, explicit owner approval is required before any MQL5 candidate is written. If authorized, the first MT5 implementation should be this exact entry mechanism layered over the historical R9 logic with Hold/Exit unchanged, then tested locally on Coinexx XAUUSD M1 using **Every tick based on real ticks**. The ordinary compact tester report is sufficient; no giant tick log is requested.


## 0.01-lot PnL audit correction

The owner requested an explicit lot-value audit before discarding or promoting this candidate. The Coinexx R9 REAL MT5 report confirms `InpLots=0.01`; a 0.01-lot XAUUSD buy at 4332.34 closed at 4331.68 records trading Profit = -$0.66, so a $1.00 XAUUSD price move corresponds to $1.00 PnL at 0.01 lot. The same deal pair charges Commission = -$0.01 on entry and -$0.01 on exit. Therefore the simulator's **price-delta-to-USD conversion was correct**, while its extra roundtrip commission was **10x too large**. Corrected metrics were recomputed trade-by-trade with $0.02 roundtrip commission; gross loss and drawdown were not merely arithmetically rescaled.