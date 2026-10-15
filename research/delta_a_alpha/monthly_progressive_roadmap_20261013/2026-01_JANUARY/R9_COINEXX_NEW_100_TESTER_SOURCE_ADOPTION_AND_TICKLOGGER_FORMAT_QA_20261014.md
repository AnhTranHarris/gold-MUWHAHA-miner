# R9 ORIGINAL COINEXX $100 TESTER SOURCE ADOPTION — JANUARY REFERENCE AND TICKLOGGER FORMAT QA
**Dated:** 2026-10-14 | **Research branch:** delta-A-alpha | **Status:** SOURCE-REFERENCE UPDATE; **no strategy promotion**; CURRENT_STATE J0183 unchanged, trading OFF, August SEALED.

## Owner-designated source folder (original files protected)
https://drive.google.com/drive/folders/1S0erLKfFpqQUVHHIHDql72PgsH6vQrMF?usp=drive_link
Accessible through connected Google Drive account. Do not relocate, edit, overwrite or collapse its full original MT5 tester reports; their report timeframe is a chart-configuration label, not proof of independent trade outcomes.

| Role | Unchanged original Drive file | SHA-256 evidence |
|---|---|---|
| **Canonical January 2026 trade-source M1 R9 HybridGate** | https://drive.google.com/file/d/1jASxs5gn3e1rzwGxlE-178aN07_5ksHE/view | **f9315c35bde962135785a0fb8fd268251086e9bebe27f5789757c69cfb38819d** — independently calculated from full 123,681,909-byte original downloaded xlsx |
| M5 HybridGate comparison | https://drive.google.com/file/d/1Fq5eku142DxoRpvBtqddR2xgbhOz4h_T/view | 3237dfe2ebec41c0cf0699dfa65dcff1020f94869ed099b5e109b7377459face — from folder companion manifest, not independently downloaded |
| H1 HybridGate comparison | https://drive.google.com/file/d/1nTbW7Y-bvYQO2IDHjQmLcEiFSHO5AET5/view | 76f478220a910a1fbc1a0fff3c0d9141617d109a25c6a9075a6806883f07adfd — companion manifest |
| M1 R9 TickLogger **tester report** | https://drive.google.com/file/d/1d6V3fHltXl7l2V8Wlu1BD-ubb78Qypnn/view | 2590b6d2b254d97a1b5a516be263bd64f4e81d92277b7114dbddefe1b96d55c2 — companion manifest |
| Compressed MT5 TickLogger-labeled file | https://drive.google.com/file/d/12jkIA2MRiFvH55rdeeABz-V0_E2hzw18/view | **3d60c65885c3df776629ca70f9118d1d9cb6300db9c7f3590abaa48c41f935ea** independently calculated from 33,329,369-byte gzip |
| Existing immutable extracted January deals / QC archive | https://drive.google.com/file/d/1fEaAqOkA2jg3aGiTxDduQh7hCHhQl3Yl/view | **16753f61feb320d45ed8c769b276407b5fc83c057acde3a04c62bc9fb5dafdc4** independently calculated; 939,342-byte ZIP |
| Original source manifest in same folder | https://drive.google.com/file/d/1wMt3SZjPiTi-KGIizrmVNQs5jRgrg8Pa/view | Read directly; full names and provenance, no destructive editing |

## January-only, separately reproducible performance target
From original M1 Coinexx HybridGate tester XLSX and its deterministic extracted read-only Deals CSV:
- Initial deposit **$100**; leverage **1:500**; lots **0.01** (as source manifest confirms).
- **27,980 distinct completed January 2026 R9 trade cycles**, **24,368 winners** (**87.0908%**).
- Realized **NET +$41,520.82**, gross winning after fees **+$43,348.69**, gross losing after fees **−$1,827.87**, after-fee PF **23.7154119**.
- Total commission **−$559.60 already INCLUDED** in trade net, not to be subtracted twice; swap zero.
- January end-of-last-close balance **$41,620.82**, exact equality with $100 + realized net; cash reconciliation **$0.00**.
- **21 positive active trading days**, no net-negative active trading days, **10 calendar days with zero closes**. Average **1,332.38 physical closes/active trading day**; actual daily range **783–2,049 closes**.
- **480 report-clock hours containing at least one close**, all positive in realized close sums (zero-close hours must still be retained for hourly gate); 18-second *median* and ~16.46-second *mean* completed hold (second-resolution report clock).
- Full January daily, hourly and ISO-week retained as separate files in the source ZIP. Existing historical R9 SYNTH January summary has the **same values**; these new native Coinexx Deal rows are a provenance improvement **not new independent profit evidence**.
- Source ledger checksum within ZIP: `R9_COINEXX_2026_01_M1_HYBRIDGATE_REPORTED_TRADES.csv` SHA256 `45788f00c2a47e7da2a6bacd49ad5ef3259a22fab79bad4f460f3d620712190c`. Recomputed independently from CSV: number of unique in/out deal pairs 27,980; net, gross winning, gross losing, fees and ending balance as above.
- Companion source manifest records all four reports' **identical Jan–Sep aggregate** 272,352 trades / +$360,693.05 net / PF 18.403069, so never sum their counts or profit as four independent experiments. Current research and acceptance is **January-only**. Do not open August tick data for training or inference under August seal.

## Crucial format distinction for tick-level per-trade analysis
The file named `GoldMuwahahaMiner_R9_TickLogger_XAUUSD_M1.gz` is a valid gzip, but first decompressed bytes are **binary MT5 SingleTestCache**, including UTF-16 MetaQuotes copyright and the literal `SingleTestCache` followed by EA tester input metadata (including UTF-16 `InpLogEveryTick`); it is **NOT an ordinary CSV tick logger**. Source gzip exact SHA above. Do not hallucinate a decoded subsecond tick series, raw MT5 Bid/Ask or independent tick-by-tick MT5 fills from this file. The large `MT5_100_M1_GoldMuwahahaMiner_R9_TickLogger.xlsx` is another MT5 **tester report** (manifest lists `InpRunLabel=SYNTH` and `InpLogEveryTick=true`), NOT proven to contain full executable quote events. Separately mentioned 303,581,440-byte .tst file in source manifest is **not among the seven current direct folder children** and was not verified.
Deal workbook gives exact *tester-reported* trade-level close/entry chronology at **seconds precision**, side, price, fee and balance. Pairing actual millisecond Coinexx quote-path to those orders requires separate verified readable raw-tick log or a trustworthy native MT5 cache parser; Dukascopy original ticks may provide separately labeled *cross-feed counterfactual* with clock-offset correction, not identical Coinexx execution.
No claim is made that `Every tick` vs `Every tick based on real ticks` mode has been resolved merely from “100% history quality”; do not infer feed mode or broker-real fill parity.

## Source authority and next use
User explicitly designates this folder as **new historical R9 performance and per-trade comparison source**. Repoint comparison tables to original M1 native Coinexx tester deals January; preserve R9 OVERFIT as hindsight-only teacher and original Dukascopy Jan Bid/Ask as live-causal Python simulator feed. For each January date/ISO week, compare actual **funded** student net/trades/gross losses/equity DD against matching R9 source row, and link source IDs. Preserve 0/negative hours and day counts. The fully measured R9 report cannot substitute for trader signal reconstruction or direct tick data.

**Governance:** January source/QC law, original full whitepaper, owner anti-summary requirements and performance benchmarks remain binding. No change to certified incumbent, scientific cursor or EA code, no trading enablement. User owner QC on eventual student mechanisms separately required.
