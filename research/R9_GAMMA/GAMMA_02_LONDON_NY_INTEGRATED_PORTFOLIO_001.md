# GAMMA-02 — London + NY Integrated Portfolio 001

**Status:** MAJOR JANUARY DISCOVERY FRONTIER — CONTINUOUS ONE-LEDGER REPLAY  
**Predecessor:** GAMMA_02_TIMEOUT_RECOVERY_CHECKPOINT_004.md  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Architecture

### London / overlap engine

Continuous full-January event stream.

The entry direction is fixed by the already-completed H4/H1 macro state and exact M15/M5 state signature selected during January discovery.

Causal displacement filters:
- 07-09 UTC early London: favorable M1 displacement >= **$3.00**
- 11-12 UTC established London: no additional displacement minimum
- 13-15 UTC overlap / US handoff: favorable M1 displacement >= **$4.00**

Each event is one-shot at a new favorable $0.05 extension. No repeated-tick duplication.

### NY engine

Inherited recovered time-decay conviction routing:
- 16 UTC: favorable displacement >= $0.50;
- 17 UTC: subphase-specific `lateBias` displacement thresholds;
- 18 UTC: `lateClean` subphase-specific displacement bands.

All events share one global cap.

## Integrated January frontier

This is one chronological admission ledger. London/overlap and NY profits are not arithmetically added after independent tests.

| Global cap | Net | Trades | PF | Exp/trade | Realized balance DD |
|---:|---:|---:|---:|---:|---:|
| 32 | +$25,230.11 | 5,419 | 3.4827 | +$4.6559 | $950.61 |
| 64 | **+$50,952.42** | **9,804** | **3.8770** | **+$5.1971** | $2,186.39 |
| 96 | +$73,350.71 | 13,593 | 4.0565 | +$5.3962 | $3,184.40 |
| 128 | **+$96,827.41** | **16,890** | **4.4088** | **+$5.7328** | $3,522.88 |
| 160 | +$117,068.74 | 19,868 | 4.6005 | +$5.8923 | $3,932.03 |
| 192 | **+$134,578.03** | **22,568** | **4.7284** | +$5.9632 | $4,206.61 |
| 256 | **+$167,706.98** | **26,689** | **4.7994** | **+$6.2837** | $5,215.63 |

High caps are research heat frontiers only. They are not production or low-capital recommendations.

## Representative cap-128 source attribution

- 08 UTC: +$2,572.55 / 503 trades
- 09 UTC: +$2,251.79 / 793
- 11 UTC: +$7,079.66 / 4,241
- 12 UTC: +$11,729.93 / 3,257
- 13 UTC: +$6,313.24 / 585
- 14 UTC: +$3,087.70 / 732
- 15 UTC: +$9,813.34 / 1,097
- 16 UTC: +$14,691.29 / 1,277
- 17 UTC: +$28,593.00 / 570
- 18 UTC: +$10,752.47 / 3,827

07 UTC remains a tiny negative residue and should be challenged in the next refinement.

## Interpretation

The opportunity-density problem is no longer confined to New York.

The current January architecture has:
- high-volume established-London/overlap execution,
- high-quality NY trend inventory,
- fast NY harvesting,
- one global capacity ledger,
- positive expectancy at every tested global cap.

Cap 64 already produces more than $50K January net at fixed 0.01 tickets. Cap 128 approaches $97K.

This is a discovery frontier. It is not yet a Jan-Jul claim and not yet equity-DD certified.

## Exact artifacts

Persistent Library:
`/xauusd-trading-bot/r9-gamma-02-velocity-geometry/2026-10-07/m1-density/`

- `gamma02_london_overlap_portfolio_001.py`
  SHA-256 `a772ddd8ee71c64f826b8db045ed3190511e1bc09ee472d7fc980391739e2112`
- `gamma02_london_overlap_portfolio_cap64.json`
  SHA-256 `d275864629ee289d17fd1738a0f6f8be94c0aac2d48e17928cd3480e20ee50a3`
- `gamma02_london_overlap_portfolio_cap128.json`
  SHA-256 `8fe8b282e208c5247bc31012d93fcbd61a6d4bbdfbca67ee805261c78ef30f62`
- `gamma02_london_ny_integrated_001.py`
  SHA-256 `1ee7046b03a139b875eaa0d4379304e84f7d5371d619bdabb589646c69d194ef`
- `gamma02_london_ny_integrated_001.json`
  SHA-256 `f14226057dbb736007d28cee82066cd0d9d677d1809410e0004a254fda177a1f`

## Next units

1. Remove or repair weak 07/08 residuals without reducing high-quality London volume.
2. Refine 11/12/13/15 source-slot economics under a global cap.
3. Integrate the stronger NY conviction-depth/time-decay maps at matched cap.
4. Test London/overlap + NY state-signature lifecycle combinations for a quality frontier and a velocity frontier.
5. Exact tick-level equity-DD replay on finalists.
6. Extract actual January R9 SYNTH monthly benchmark.
7. Jan-Jul validation only after January architecture stabilizes.

R9 SYNTH remains the hard target.
