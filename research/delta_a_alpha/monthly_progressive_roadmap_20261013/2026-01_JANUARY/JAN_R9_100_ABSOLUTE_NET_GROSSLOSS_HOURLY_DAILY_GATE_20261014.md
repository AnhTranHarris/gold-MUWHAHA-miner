# January 2026 R9 $100 absolute hour/day acceptance ledger — no percentage spin

**Decision:** RESEARCH ONLY / **UNDER R9 BENCHMARK** / no accepted new profitable source. Owner January QC law and original 10-page R9 source-of-truth supersede this report. Frozen V1 unmodified, `J0183`, trading OFF. Only January original Dukascopy ticks tested; August never opened. Updated owner scoring standard: every attainment percentage has R9 SYNTH $100 as the denominator. Incompatible feed or clock metrics identified.

## Exact benchmark / student scorecard

| Measure | Coinexx R9 January $100 generated `Every tick` | Original Dukascopy student $100 | Student / R9 |
|---|---:|---:|---:|
| January booked net | **+$41,520.82** | **+$243.779** | **0.5871%** |
| Funded closed trades | 27,980 | 194 | 0.6934% |
| Booked gross losing closes | −$1,827.87 | −$438.611 | 23.9957% absolute |
| Gross losing cash per completed close | $0.0653277 | $2.26088 | **3460.6%** of R9 |
| Net/close | $1.483946 | $1.256593 | 84.679% |
| Gross profit / gross loss PF | 23.7154 | 1.555798 | 6.56% |
| Trade-active hours | 480 | 134 | 27.92% |
| Profit-positive trade-active hours | 480 | 84 | 17.50% as count |
| Hours with booked negative net | 0 | 50 | N/A |
| Net per own funded-active H1 | +$86.5017 | +$1.81925 | **2.103%** |
| Funded closes per own active H1 | 58.2917 | 1.44776 | **2.484%** |
| Trade-active tester-clock days (working +02 alignment) | 21 | 19 | 90.48% |
| Positive tester-clock days | 21 | 13 | 61.90% |
| Months / H1 with same-event performance target met | 1 month / 480 profit hours | **0 matching R9 profit hours; 0/21 profitable R9 dates matched** | 0% |

**Two nonhomogeneous execution models:** R9 produced generated-tick MT5 tester deals; student priced each fill on original 2026-01 Dukascopy Bid/Ask and modeled 0.01lot=1oz, $0.20 fee, 1:500 assumed leverage, 250ms minimum latency, single physical slot and broker not certified. Do not interpret synthetic R9 as executable return. Comparisons normalize the research objective, not market fill identity.

**R9 day/hour clock rule:** Coinexx source reports 21 positive *tester-clock* days and 480 net-positive tester hours. A separately inferred offset of approximately tester=UTC+2 is applied *to the student's UTC trades* to align against source H1 tester-clock buckets. Cross-midnight UTC rebucketing of the original R9 led to 26 apparent UTC trade dates; those are **not** 26 R9 tester trading days. Original owner R9 21 days retained as authority. Broker clock offset remains unverified.

**Gross loss denominator correction:** Student per-funded-close gross loss ~$2.261 vs R9 ~$0.06533. A small aggregate gross-loss total from 194 trades is **not** better gross-loss control than R9's $1,827.87 total from 27,980 trades. Gross loss is measured after fees, on losing closes; floating equity DD is distinct.

## New January original-tick production research — 36 multi-regime sources, 72 funded replays

Generated mechanically from *prior completed* S1, S5, S15, M5 and H1 bars without future labels; funded through same one-slot risk/quote executor: finite S5/S15 failed-break reclaim families, S5/S15 structure-aligned versus countertrend regrowth and S15 range rotation. 36 source variations tested as stand-alone and paired with the frozen source (72 total; plus the original control). All original outcomes including negative trial rows, cash, gross losers, halt timing, source proposal count, daily/h trade scorecards and source code are archived. **No added source achieved any positive full-January funded run in its tested original parameterization; no combination improved the held-fixed parent.** 0/72 new variants satisfy the owner R9 hourly/daily success gate. The source families should be treated as falsified under these costs/exit templates; do not re-run equivalent rules unmodified.

Historical positive child for comparison: completed S15 BB/Keltner squeeze -> quote wait -> M1 minute-open phase veto -> completed M5 ATR exit lifecycle. 194 closes and +$243.779 research net. Does not reach investor threshold; not V1 production wired.

### 18-second microstructure budget diagnostic (strictly noncausal, not executable signal)

Used original 9,135,062 January quotes. 86,478 spaced roughly 20-second **anchor samples**; at first real quote 250ms later, inspected best after-fee favorable long *or* short movement within 18 seconds. The oracle is allowed to know future direction and best exit; it is therefore optimistic hindsight. **9,765 / 86,478 (11.292%)** sampled anchors could attain the R9 synthetic historical *mean* net per close of $1.483946 after modeled $0.20 fee. **59 of 481** quote-active hourly buckets contained >=58 such oracle anchors under this particular 20s sampling. This is **not a global attainable-trade upper bound**: arbitrary intervening entries, larger holds or other strategies are outside the sample. It does quantitatively justify testing tick-phase/spread/economic opportunity before fitting more indicators.

### Architecture implications

- Preserve the positive S15 research child as control only; no wrong benchmark denominator.
- Prioritize quote-path/fee-aware **expected cash per trade**, not signal count. Additional source proposals are not funded profit.
- A grid adaptation is a finite **virtual candidate allocator** (rotation, retest, continuation, compression breakout) with only one actual 0.01lot order initially; no martingale/basket inventory.
- Audit source admission at exact time, same-feed spread, cost, stop/swap/margin, quote latency, maximum floating mark-to-market DD, time occupancy and all report-clock 744 hours.
- Do not claim broker real-tick parity from M1 TickLogger XLSX; that file contains identical tester Deals/Orders with logger enabled, not independently decoded raw Coinexx tick quotes.

## Durable recovery paths

- Source-of-truth institutional report: https://github.com/AnhTranHarris/gold-MUWHAHA-miner/blob/delta-A-alpha/research/delta_a_alpha/monthly_progressive_roadmap_20261013/2026-01_JANUARY/R9_JAN2026_INSTITUTIONAL_QUANT_REVERSE_ENGINEERING_SOURCE_OF_TRUTH_10P.md
- Original Coinexx R9 M1/M5/H1 reports: https://drive.google.com/drive/folders/1S0erLKfFpqQUVHHIHDql72PgsH6vQrMF
- Original January Dukascopy raw gzip: https://drive.google.com/file/d/1DyKXj-DDhsP3eMXm0j7QQimXRLoHSHKo/view ; original local/source SHA256 `d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5`.
- Original test skeleton and parent: protected January Drive and GitHub research source registry, e.g. https://github.com/AnhTranHarris/gold-MUWHAHA-miner/blob/delta-A-alpha/research/delta_a_alpha/monthly_progressive_roadmap_20261013/2026-01_JANUARY/JAN_R9_H1_GROSS_LOSS_M1_PHASE_ATR_20261014_VERIFIED_SOURCE_REGISTRY.md
- New exact code/trials/hour/day/oracle/custody package is provided by new companion Drive archive, with sha256 per internal member. No local-only helpers or temporary files are claimed durable without archive verification.
