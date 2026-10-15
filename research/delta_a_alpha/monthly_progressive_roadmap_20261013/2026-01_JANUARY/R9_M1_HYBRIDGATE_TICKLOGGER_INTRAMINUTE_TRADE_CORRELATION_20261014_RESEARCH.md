# January R9 SYNTH M1 HybridGate ↔ TickLogger exact trade-level correlation — owner F1 chassis research
Date: 2026-10-14. Existing branch delta-A-alpha only; scientific state J0183, trading OFF, August SEALED. Status: **January diagnostic, NOT approved causal strategy or native full V1 integration**.

## Original source and independent exact trade re-read
Owner's Coinexx MT5 $100 "Every tick" synthetic runs, source folder https://drive.google.com/drive/folders/1S0erLKfFpqQUVHHIHDql72PgsH6vQrMF
- **M1 HybridGate original** https://drive.google.com/file/d/1jASxs5gn3e1rzwGxlE-178aN07_5ksHE/view SHA256 `f9315c35bde962135785a0fb8fd268251086e9bebe27f5789757c69cfb38819d`
- **M1 TickLogger original tester report XLSX** https://drive.google.com/file/d/1d6V3fHltXl7l2V8Wlu1BD-ubb78Qypnn/view SHA256 `2590b6d2b254d97a1b5a516be263bd64f4e81d92277b7114dbddefe1b96d55c2`
- New source-traceable exact two-report **January research ZIP** https://drive.google.com/file/d/1f6TVclfwCjrkNv3n_BqB2e205KMWL8AH/view SHA256 `a83981da546df1e2f45851a0f17b05e406bc90739e9a5b29ee5b8148833c00f0` (1,726,055 bytes). Includes read-only Python scripts, both 27,980-row normalized deal ledgers, 60-second and day × entry-phase tables, full JSON audit and SHA256 manifest. **Source archive actually uploaded to owner's protected January folder**, not merely linked as a promise.
- Readable fully detailed study in same January folder: https://drive.google.com/file/d/1NeMh36RFyy51bR4AX75M4xJBUk0JIsVv/view
- Original source XLSX contain >1.6GB XML worksheet each; streaming XML extractor used, Jan-only. Original TickLogger has 4 additional settings rows (`InpTickLoggerEnabled=true`, `InpRunLabel=SYNTH`, `InpLogEveryTick=true`).
- **10 exact individual trade fields match for all 27,980 trades**: entry/exit timestamp, entry/exit deal IDs, buy/sell, entry/exit price, after-fee net PnL, hold seconds and last close balance. Identical histories reflect two distinct reports of same recorded trades, **not two independent execution confirmations**.
- Separate compressed `GoldMuwahahaMiner_R9_TickLogger_XAUUSD_M1.gz` is a MetaQuotes `SingleTestCache` binary, not decoded raw sequential tick CSV. These workbooks contain second-resolution **Deals** and Orders, not individual millisecond Bid/Ask ticks; do not mislabel them as an independently verified raw tick tape.

## New full-sample, in-sample R9 SYNTH trader-geometry discovery
January 2026, entry second relative to current M1 bar:
| Entry second | Trades | Win rate after fees | Reported cash net |
|---|---:|---:|---:|
| 00–09 | 11,203 | 71.4809% | +$5,239.42 |
| **10–39** | **16,113** | **99.6276%** | **+$36,194.39** |
| 40–59 | 664 | 46.2349% | +$87.01 |
| ALL | 27,980 | 87.0908% | +$41,520.82 |
- 10–39s captures **87.17% of historical January reported net** with 57.59% of January reported positions, **NOT a profit forecast or causal gate**. Across **21/21 active January trade days**, 10–39s entry-group reported aggregate cash profit exceeded 00–09s group; these are different numbers of trades, not matched counterfactual positions.
- **27,266 / 27,980 = 97.448%** entered and exited inside the SAME M1 candle.
- **19,775** unique entry-clock M1 candles, **8,205** candles with exactly TWO entry events; highest entry events in any M1 candle=2. The EA's configuration lists max same-minute rearm=3; this monthly outcome is observed actual count, not permitted max.
- Average durations by class: 00–09s 12.168s; 10–39s 19.463s; 40–59s 16.122s. Risk of selection/hold confounding is material.
- Full minute-by-minute and daily partitions are included in research ZIP with no winning-trade cherry-picking.

## Reverse engineering—not simply a timestamp veto
Owner intent: exploit the **F1 chassis** tick behavior and M1 candle behavior across M1/M5/H1 synthetic reports, then engineer equivalent *causal* mechanics in January Dukascopy quote replay. MetaQuotes docs describe per-M1 synthetic tick generation from historical OHLC/tick volume and per-minute fixed synthetic spread: https://www.metatrader5.com/en/terminal/help/algotrading/tick_generation . A 99.63% historical win-rate phase may partly be a GENERATED-TICK ALGORITHM fingerprint, not a true market opportunity. Therefore:
1. From original tick-derived prior completed M1 and *as-of current M1* only: examine current bid displacement/open, live-so-far high/low, micro efficiency and turns, CUSUM flow and time-in-minute. DO NOT use final current M1 high/low/close before known.
2. Reconstruct stop/target/trailing event chronology (R9 original settings: stop 30 pips, trail 3, arm 10, maxhold 30s, <=3 same-minute rearm) and identify which child event structures produce 10–39s success. Annotate source to session and completed M5 ATR14/H1 structural state; need exact original R9 EA MQL5 logic for faithful parity.
3. Port *state-machine/causal price-geometry* rather than an absolute second-of-minute rule into the existing V1 vertical grid research child; compare against prior original R8 and S15 quote-queue profit-harvest control without changing protected V1 code.
4. Research on **January original Dukascopy ordered Bid/Ask ticks only**, with physically funded 0.01-lot $100/$200 accounts, verified conversion, commission, latency, spread, physical singleton, actual daily/weekly/hourly ledger, source hashes; separate historical R9 SYNTH comparison from causal student.
5. No hypothetical subportfolio “only execute 10–39s winners” gain may be claimed from reselecting historical R9 trades; removing early entries changes slot occupancy and later signals. The true test is fresh funded chronological execution.

**January owner law:** full month-specific January source/QA: https://docs.google.com/document/d/15psoEliXaPEXJr22cKlJb4OGmWo26j3Eu8GlTtH26Kw/edit . Original frozen V1 + owner anti-summary/QC remain binding. No official scientific advance, owner signoff or authorized MQL5 build from this diagnostic alone.
