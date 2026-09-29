# R09_BETA_001_ADAPTIVE_IGNITION_ENTRY

**Status:** Formal BETA ENTRY/ACTION breakthrough; owner review pending. **No MQL5 candidate has been coded.**

## Executive result

This breakthrough keeps the R9 hold/exit geometry fixed and replaces the immediate R9-style entry trigger with a causal **early-ignition + opportunity-cost gate**. On the same Dukascopy Jan–Jul 2026 feed, relative to the feed-normalized R9 control, the primary candidate produced:

- **Winning trades:** 31,704 vs 28,789 (**+10.13%**)
- **Win rate:** 13.99% vs 11.68% (**+19.70% relative**)
- **Net:** $-198,021.63 vs $-236,165.84; loss reduced **16.15%**
- **Gross loss:** $-208,393.67 vs $-245,050.95; absolute gross loss reduced **14.96%**
- **Max drawdown:** $198,021.63 vs $236,165.84; reduced **16.15%**
- **Fee stress:** still improves net vs the same baseline by **15.38%** at $0.30 and **14.74%** at $0.40 additional roundtrip fee.

The strategy is **still loss-making**, so this is not a profitable EA claim. It is a material entry-quality breakthrough under the owner's category-specific >10% rule.

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
| 2026-01 | 31,250 | 4,189 | 13.40% | $-26,651.53 | $-27,981.41 | $26,651.53 |
| 2026-02 | 27,117 | 4,350 | 16.04% | $-26,369.97 | $-28,263.33 | $26,369.97 |
| 2026-03 | 49,444 | 7,938 | 16.05% | $-46,486.59 | $-49,529.22 | $46,486.59 |
| 2026-04 | 30,134 | 4,064 | 13.49% | $-26,622.60 | $-27,866.45 | $26,622.60 |
| 2026-05 | 31,178 | 4,138 | 13.27% | $-24,605.62 | $-25,679.14 | $24,605.62 |
| 2026-06 | 34,522 | 4,662 | 13.50% | $-27,614.39 | $-28,827.34 | $27,614.39 |
| 2026-07 | 23,051 | 2,363 | 10.25% | $-19,670.94 | $-20,246.77 | $19,670.94 |

## Nearby robustness

The higher-volume sibling `ADAPT_110_065` also passed the complete Jan–Jul entry gate: **+12.52% winners**, **+19.97% relative win rate**, **13.60%** net-loss reduction and **13.60%** drawdown reduction. A three-point absolute-spread neighborhood showed the expected trade-off: tighter $0.75 improved economics but sacrificed winner count; looser $0.85 increased winners but no longer cleared the >10% economics gate. This means the mechanism family is supported, while the exact spread threshold remains a parameter requiring broker-specific MT5 translation rather than blind copying.

## R9 REAL → SYNTH reference bridge

Historical Coinexx R9 REAL and generated SYNTH are different tester processes from the Dukascopy Python experiment. They cannot be treated as directly additive dollars or identical trades. For the owner's requested bridge bookkeeping only:

- historical REAL→SYNTH net gap = **$359,408.13**; the candidate's same-feed net improvement of **$38,144.21** equals **10.61%** of that historical gap as a purely arithmetic cross-feed proxy;
- historical REAL→SYNTH winner-count gap = **88,751**; the candidate adds **2,915** same-feed wins, an arithmetic proxy of **3.28%** of that historical count gap.

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
- Jan–Jul validation uses original ordered Bid/Ask ticks, prior-month warm-up only, actual observed spread in fills, plus $0.20 extra roundtrip commission.
- R9 fixed Hold/Exit: $0.30 initial stop, $0.10 trailing activation, $0.03 trail, 30-second max hold.
- August 2026 was not accessed.
- January was discovery, so Jan–Jul is not represented as pristine untouched OOS. The later MT5 broker test is an independent translation gate, not proof of OOS research purity.

## Owner gate

This record authorizes **nothing automatically**. Per BETA 003/BETA 006, explicit owner approval is required before any MQL5 candidate is written. If authorized, the first MT5 implementation should be this exact entry mechanism layered over the historical R9 logic with Hold/Exit unchanged, then tested locally on Coinexx XAUUSD M1 using **Every tick based on real ticks**. The ordinary compact tester report is sufficient; no giant tick log is requested.