# GRID0342–GRID0345 | January micro-capital risk envelope and fully endogenous virtual-liquidity grid — UNPROMOTED
**2026-10-14. Original Dukascopy 2026 January, 9,135,062 Bid/Ask ticks. RESEARCH ONLY, not broker-certified, not owner QC.**
## Owner governing sources (unchanged, original technical authority)
- [Full original owner roadmap](https://docs.google.com/document/d/1PcaksxuiayFXVW3QtKfzitARvQj6NyL4IIbGhG8K9z4/edit)
- [Verbatim anti-drift original-source QC law](https://docs.google.com/document/d/1eG5F76uvm9M-1JXs4LvAaTzPEurU5l4Pgj2sUUelc1o/edit)
- [January original-source evidence law](https://docs.google.com/document/d/15psoEliXaPEXJr22cKlJb4OGmWo26j3Eu8GlTtH26Kw/edit)
- [Full ratified owner governing conversation](https://docs.google.com/document/d/1J9d_P4ooCnNmcxPwG1F178aE4ktpkLrFclcyQPaQJ8k/edit)
- [Master seven-month project folder](https://drive.google.com/drive/folders/1dVkQzUNfsE1nGAvcBYfrAadYNVyn9hn9)
- Original full V1 whitepaper Git blob `1b92b3c89159681a7181508de158af685cf5780c`, original `FourSessionV1` SHA `64b75c39c41ff8ccd0d0e8b02e45bdf5b9ca54e2`, preexisting scientific journal J0183. No edits.
- Direct previous R8 bridge archive: https://drive.google.com/file/d/1EqpiNQt-d4M7yer2Na7mv4NIzOWU53Pr/view; original R8 MQL5: https://github.com/AnhTranHarris/gold-MUWHAHA-miner/blob/carson/mt5-r8-s1-wave-confirm-certification/Experts/GoldMuwahahaMiner_R8_Microstructure.mq5

## Better research question
Can a dedicated $100–$5,000 XAUUSD capital regime combine a physically funded one-position microstructure executor, realized-cash earned inventory, stress-loss escrow, and session/source selection to survive and grow rapidly before handoff to the existing L0–L7 system, **without** relying on historically preselected January winners, loss-increasing lots, brokerless fills, or an unrealistic assumption of guaranteed account survival?

## Two independent experiment branches
**Branch A — L7 risk envelope:** source-candidate and planned future exits are inherited from the historically selected January GRID0283–0325 original research. Admission checks use only marked equity and already booked cash; original Bid/Ask fill and settlement are preserved. Ten fixed-seed random start dates, each seven UTC calendar days, $100 initial, 0.01 lot=assumed 1oz, modeled 500:1, $0.20 fee, original Bid/Ask, 20% margin admission, 50% stopout. In-sample source selection remains an explicit limitation.
**Branch B — fully endogenous L3–L5 standalone candidate:** new `grid0344_endogenous_virtual_liquidity_grid.py` reads original quote ticks and completed one-second bid-high/low levels, detects virtual sweep-reclaim or continuation, waits 250ms to physical quote entry, trades a single 0.01-lot physically funded position, uses quote-side cash stops, targets, 90s max life, cooldown and source-independent paid-loss pause. **No** R8 MT5 deal time, R9 label, or inherited candidate is used. Four variants run on full month. This is an intentionally *simple reconstructible* microstructure hypothesis, not the accepted V1 architectural integration.

## Branch A — completed ten-start frontier
| Policy | Positive ending accounts | No modeled stopout | Total booked trades | Seven-day ending cash range | Worst hourly equity DD | Cash-escrow vetoes | $5k endpoints |
|---|---:|---:|---:|---:|---:|---:|---:|
| `CONTROL_2` | 10/10 | 10/10 | 711 | $243.14–$396.04 | $82.36 | 0 | 0/10 |
| `R8_SINGLE_TO_5000` | 10/10 | 10/10 | 242 | $142.89–$196.83 | $23.00 | 0 | 0/10 |
| `ESCROW_8USD_70PCT` | 10/10 | 10/10 | 242 | $142.89–$196.83 | $23.00 | 0 | 0/10 |
| `ESCROW_4USD_65PCT` | 10/10 | 10/10 | 327 | $142.89–$243.59 | $42.18 | 0 | 0/10 |
| `ESCROW_8USD_90PCT` | 7/10 | 10/10 | 194 | $95.80–$227.85 | $42.18 | 15,491 | 0/10 |
| `ESCROW_12USD_80PCT` | 10/10 | 10/10 | 326 | $142.89–$241.82 | $42.18 | 173 | 0/10 |

**Selection:** no micro-capital risk change is a combined risk+profit+velocity breakthrough. Strict single-position is materially safer in-sample but has only 242 vs 711 completed trades. The two initial mild escrow variants never actually vetoed entries, therefore they CANNOT be credited with independent risk efficacy. Tighter 8 USD/stressed 90% cash floor activates 15,491 times, but 3/10 seven-day accounts finish *below* their $100 starts. Reject for the user’s all-positive objective. No sampled account reaches $5,000 or $10,000. All 10/10 no-stopout claims are modeled historical data only—not probability-one or live survival.

## Branch B — independent full original January event-generation test
| Fully endogenous January virtual grid | Completed trades | Starting $100 -> ending cash | Wins | Gross profit | Gross loss | Max full-tick equity DD | Worst hourly DD | Original quote ledger error |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `SWEEP_A` | 41 | $43.27 | 7 | $9.29 | −$66.01 | $57.01 | $25.10 | 7.2e-13 |
| `SWEEP_B` | 47 | $41.29 | 9 | $12.65 | −$71.36 | $60.55 | $17.56 | 8.4e-13 |
| `CONT_A` | 39 | $43.59 | 9 | $8.76 | −$65.17 | $58.16 | $21.40 | 8.4e-13 |
| `CONT_B` | 38 | $42.80 | 9 | $4.72 | −$61.92 | $58.25 | $18.06 | 8.1e-13 |

**Disposition:** all 4 endogenous variants LOST money on January Dukascopy Bid/Ask after costs. None is a candidate to deploy or combine as a proven profit source. Trading without preselection is decisive: an appealing virtual-grid concept does not itself create a profitable microstructure edge. Do not rescue losing variants through martingale or extra leverage. Windows and parameters were selected for research; none was externally validated.

## Cross-language reconstructible research insights — NONPROFIT-CLAIMED external hypotheses
1. [MQL5 Portfolio Basket Risk, 2026](https://www.mql5.com/en/articles/24331): separate aggregate current risk, realized costs and portfolio margin. Our L7 cash+stress envelope is an independent testable adaptation, not a reproduction of any unclaimed results.
2. [MQL5 order execution risk, 2026](https://www.mql5.com/en/articles/21231): check spread, stop distance, minimum volume, order margin and actual funding as independent admission requirements. Fixed 0.01 lots can violate a safe cash-risk cap; skip rather than round upward.
3. [MQL5 Chinese scalp/order-flow writeup](https://www.mql5.com/zh/articles/15895): lose-streak gate, trailing, liquidity-context filtering. Caution: indicator-volume/DOM proxies unavailable on Dukascopy OTC quote data; no fabricated true order book. The source is an educational implementation, not an independently validated XAUUSD profit engine.
4. [TradingView HTF sweep/reclaim, open source](https://www.tradingview.com/script/FG507Q8S-HTF-Liquidity-Sweep-Reclaim/): completed swing liquidity and reclaim are reconstructible from price candles, unlike inaccessible proprietary black boxes. We tested an original-tick virtual sweep/reclaim approximation and it **failed** in January.
5. [MQL5 Bid/Ask Spread Analysis](https://www.mql5.com/en/articles/9804): execution spread can overwhelm seconds-scale profit targets, even when midprice setups look good; do not infer close-side net profitability from candidate labels.

## Proposed $100–$5,000 subsystem design — NOT ACCEPTED OR PROVEN
**L0:** raw original Bid/Ask, timestamp consistency, broker cash-per-tick, spread and symbol contract; no external tick-to-order-book fiction. **L1–L3:** completed-second micro-bar and completed M5/15 regime classification; virtual liquidity levels may be scanned, never assumed to represent resting executable limit orders. **L4–L5:** fast causal entry confirmation and hard physically quoted exits with loss cap, time limit, slippage stress, skip when projected stop loss + spread + fee exceeds cash risk. **L6:** one actual 0.01-lot position initially, never loss-escalate or average down, no ghost Watchdog funding, unlock up to 2/4 positions only with already BOOKED surplus and favorable marked-equity runway. **L7:** stressed portfolio loss reserve, validated free margin, liquidation fail-closed progress, per-UTC-hour MFE/MAE ledger, circuit break on account deterioration, graduate only after *actual* $5,000 marked equity AND causal QC; rollback to smaller tier below threshold.

This architecture is a **design proposal**, not proof of achieving 100% survival, rapid multiplication or a broker-compatible trade edge. A $100→$5,000 within seven days requires a 50× wealth multiple with no loss overrun in all 10 start dates; it is exceptionally demanding, and no strategy can guarantee zero chance of ruin through all future market conditions.

## Independent QC, evidence ledger and fail-closed acceptance
- **103 independent assertions PASS** for all 6 completed ten-start portfolios and four whole-month fully endogenous alternatives, including archive identity, exact original quote-side fees and per-trade ledger reconciliation, single-position no-overlap, summary repeatability and original gzip SHA `d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5`.
- The fail-closed copy of GRID0324 adds a `STOP_OUT_NO_PROGRESS` RuntimeError when an attempted liquidation fails to decrease funded live position count. Original predecessor source, official state and active production code are not edited. This check has been exercised by normal completed runs; no intentional stopout fault-injection proof is claimed.
- Exact dependent original predecessor package is nested in this archive; raw 66MB original tick gzip is referenced by hash and not duplicated. Inherited absolute entry+exit candidates remain January in-sample; a full original tick and bridge account result is not a live fill certification.
- NOT owner QC, NOT broker-calibrated, NOT matched all R9 SYNTH days/weeks/net/risk/velocity, NOT R9 OVERFIT six scores, NOT successful $5,000 graduation, NOT 10×7-day autonomous profitable original-tick proof. Trading OFF, scientific cursor J0183, August SEALED.

### Archive source manifest
- `grid0342_hyperrisk_escrow.py`: new quote-side admission/L7 failing close guard research-only copy
- `grid0343_ten_start_microcapital.py`: six 10-day [sic: six policies × 10 random seven-day windows] comparisons with full ten-start JSON, separate partial checkpoints and run logs
- `grid0344_endogenous_virtual_liquidity_grid.py`: fully endogenous virtual grid, four original-tick entry/exit variants plus exact trade ledgers
- `grid0345_independent_qc.py`: read-only 103 assertions and JSON proof
- `ORIGINAL_PREDECESSOR/`: immutable GRID0334–0341 dependency archive; raw original tick source not duplicated
- `grid0343_partial_checkpoint.json` contains persisted original seven-day portfolio outcomes, not a summary substitute.


---
## Verified current preservation references
- [Exact runnable Python + January original tick-trade-ledger results + previous preserved GRID0334 source archive](https://drive.google.com/file/d/1p61tu7WOKHFLsvEwEQgx_levgihRIrrm/view), complete archive SHA-256 `3d3ff7348fd9f5508549058a064a2dd3f8712ede9fff09f3ab0d315afec841c9`.
- [Four exact standalone new Python research scripts](https://github.com/AnhTranHarris/gold-MUWHAHA-miner/tree/delta-A-alpha/research/delta_a_alpha/monthly_progressive_roadmap_20261013/2026-01_JANUARY/experiments/GRID0342_0345_SOURCE_CODE).
- [Same unmodified human report preserved in Google Drive](https://drive.google.com/file/d/1TIumeCqdBZotwyhyChXtwxk1Rk_h03ER/view).
- [Original source transfer retained for independent GitHub byte readback](https://drive.google.com/file/d/10IKxIjrCgJn00yOimWKZRFiX1wF4CrnQ/view).
- Original governing release remains `J0183`, trading OFF, August SEALED; the active FourSessionV1 file has not been altered.
