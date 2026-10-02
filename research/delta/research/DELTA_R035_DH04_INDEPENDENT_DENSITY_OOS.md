# DELTA R035 — DH-04 Independent Density Source OOS Validation

**Status:** COMPLETE — NO VIABLE DH-04 DENSITY ADDITION  
**Parent:** R032-C03  
**Surface:** P90  
**Holdout:** later January out-of-sample  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Frozen configurations

- R035-A01_DENSITY = C03 + DH04-A01
- R035-S03_QUALITY_DENSITY = C03 + DH04-S03
- R035-S07_QUALITY_LOW_DENSITY = C03 + DH04-S07
- R035-DH04_UNION_3 = C03 + A01 + S03 + S07

All were selected/frozen before late-January results.

## Results

| Config | Trades | Wins | Trade Retention | Winner Retention | Net | ΔNet vs Parent |
|---|---:|---:|---:|---:|---:|---:|
| C03 | 2115 | 875 | 79.5412% | 78.0553% | -500.16 | 0 |
| A01 | 2200 | 914 | 82.7379% | 81.5343% | -513.64 | -13.48 |
| S03 | 2123 | 876 | 79.8420% | 78.1445% | -504.45 | -4.29 |
| S07 | 2117 | 877 | 79.6164% | 78.2337% | -499.93 | +0.23 |
| Union | 2205 | 915 | 82.9259% | 81.6236% | -515.94 | -15.78 |

## Decision

DH04-A01 restores activity but at a large net cost. DH04-S03 is also negative. DH04-S07 produces only a two-trade +$0.23 micro-edge, so it cannot promote and advances only to exact robustness testing.

Result SHA-256:
`eb4bf32f4cf4c4f4e8359ef11e2d2e63a760ba48a6969cb79bbf48053249a523`

Drive:
https://docs.google.com/document/d/1Lwrkofu4dz-slY6QpH13ZnKbMGeQ4OzqSsbYuVCBI7U/edit
