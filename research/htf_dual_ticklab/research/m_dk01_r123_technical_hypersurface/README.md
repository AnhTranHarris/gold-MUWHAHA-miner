# F401-R123 — Four-month broker-held-out nonlinear technical indicator hypersurface (UNAPPROVED)
Scientific date 2026-10-28; UTC archive date 2026-10-29.

**SOURCE-EXACT RESEARCH ONLY. NO LIVE-DEMO VETO, MQL5 PARITY, MT5/EA ORDER APPROVAL.**

## Why this branch
Owner correctly identified excessive R121/R122 quote-order classifier fixation. We executed a distinct **124-channel technical structural family**, from real approved raw tick-derived completed candles at 1s/5s/15s/30s/M1/M5/M15/H1. 8 scales x14 =112 ATR-like volatility, EMA(8/21/55), SMA(20/50), Bollinger(20), completed 55-bar Fibonacci range rank, trend acceleration + 12 cross-timeframe conflict/squeeze calculations. Full original R120 128-channel 250/500ms plus multiscale session/HTF geometry is included in separately trained 252-channel fused model. Strictly pre-t0, no same-millisecond tick, unfinished HTF bar, target label, F395 t0+15 SHADOW or target broker quote input at inference.

## Original source input and honest mathematical caveat
- Original F395 Jan/Feb/Jun/Jul, both independent Coinexx real ticklogger and Dukascopy source, eight independent raw SHA-256 pins verified against original source registry. Coinexx historical UTC minus120min Jan-Feb, minus180min Jun-Jul; DK UTC unchanged.
- ATR-like volatility term **uses exponentially smoothed true range**, NOT guaranteed equality to native MetaTrader iATR/Wilder ATR. Python Pandas EWM seed similarly differs from TA-Lib's canonical SMA seed. Fibonacci rank is of prior 55 fully completed observed bars, not a retrospectively confirmed pivot.
- 3/3 synthetic strict clock tests PASS and full-vs-prefix real JAN exact 124D rows PASS on original ordinals 50,000–50,002 for BOTH brokers (DK 1,151,090 quote ticks; CX 1,091,584). Eight source NPY cache SHA checks retained; deterministic regeneration script in portable bundle.

## Training/audit
Four multiclass correct/opposite/neutral heads, two per source broker: 124D technical-only (127 leaves/100 rounds) and fused 252D (95 leaves/65 rounds). Train source January first60% (Coinexx 69,073 and DK 68,808 thinned rows), frozen source Jan 63–78% CAL after40s embargo at q99.5% of correct-risk for wrong class heads; score the **OPPOSITE broker's Jan/Feb/June/July** original unchanged event indices. No evaluation broker labels enter training/calibration. Historical months are already **PROJECT-EXPOSED**, not virgin future blind, and cross-broker January early calendar overlaps training source timeline. Zero source or engine changes.

Exact eight original cells: 2,574,251 events, correct 1,208,071 and wrong 1,366,180.
| Final veto | Wrong rejected | Correct lost | Wrong/good |
|---|---:|---:|---:|
| Indicator-only class support | 7,894 | 3,699 | 2.134 |
| R120-fused class support | 16,470 | 7,369 | 2.235 |
| Independent specialist union | 21,502 | 9,922 | 2.167 |
| Independent specialist intersection | 2,862 | 1,146 | 2.497 |

All 8 original component index, timestamp, side and truth masks independently full-recounted, original counts unchanged. Historical Jan post-82% same-source diagnostic weak: CX indicator 61 wrong/98 good lost; CX fused17/24; DK indicator12/11; DK fused1/0.

Original **M-DK-01** January hindsight teacher 94,603 wrong/7 correct veto; F395 historical t0+15 SHADOW 403,180/9,797 cannot be used at original t0. **No pre-t0 R123 model approaches >400,000 wrong/<10,000 correct. Park these tested configurations; no nearby span/threshold optimization.** Whole-system G01–G09 all OPEN; owner historical approvals 21/39 unchanged.

## Portable complete source/masks/weights
Local verified user artifact `XAUUSD_F401_R123_INDICATOR_MULTITREND_EIGHTCELL_ORIGINAL_MASKS_UNAPPROVED_20261028.zip`, **14,009,630 bytes**, SHA-256 `7cd54a8e04ea006ddea92e71349afeebbcc1f6ccd87a18d96e581002db21cb18`, ZIP CRC 33/33 PASS and 32/32 member SHA PASS. Includes all 4 frozen model weights/calibration, eight original per-event cooperative masks (complete source ordinal/time/side/truth), code and scientific report. 1.2GB reproducible 8x124 cached features and original 500MB market raw retained separately, not duplicated in ZIP. **MT5_EXPAND /01 binary upload not yet proved**. This README is not an executable GitHub-source substitute until Python source files are committed separately.

## Community-sourced distinct next mechanism, not an achieved result
- TA-Lib technical indicator definitions: https://ta-lib.org/functions/ema.html ; https://github.com/TA-Lib/ta-lib-python/blob/master/docs/funcs.md.
- Kaufman adaptive efficiency/KAMA: https://ta-lib.org/functions/kama.html
- Ehlers 2013 adaptive dominant cycle: https://onlinelibrary.wiley.com/doi/10.1002/9781118728611.ch11
- Confirmed, not theoretical/hindsight directional change FX: https://onlinelibrary.wiley.com/doi/full/10.1002/isaf.1552 ; https://journals.sagepub.com/doi/10.3233/AF-160054.
- Serial dependence and purged heldout labels: https://ppuertos.github.io/financial-ml-core/reference/model_selection/split/

Next R124 requires **new structural event-time information**, not same indicators retuned: causal confirmed directional change/overshoot, adaptive KAMA/Ehlers phase, multi-resolution Kalman innovation / change-point, session-aware expert conditional veto and source-causal correct rescue. Run a small truthful information probe first, then eight exact cells only if it adds high-purity information; original M-DK-01 benchmark per-component, cooperative 71%/90% G06 separately, full shared-equity G09 later. PRIMARY READ ONLY, /02 untouched.
