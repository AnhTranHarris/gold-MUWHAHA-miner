# R8 January 2026: MT5 $100 survivability mapped to original Dukascopy ticks

**Disposition:** R8 original-source forensic recovery and causal **approximation**. Unpromoted research. The original R8 MT5 report is **not** a Dukascopy result; retrospective tape repricing is **not** a causal backtest. No changes to current `delta-A-alpha` engine/J0183, no MQL5 deployment.

## Provenance and controlling original inputs

- Original MT5 tester: `ReportTester-871471_jan2026_aug2026_R8_1(1).xlsx` (in ChatGPT project attachments), EA `GoldMuwahahaMiner_R8_Microstructure`, broker `Coinexx-Demo`, initial deposit **$100.00**, leverage **1:500**, input volume **0.01 lots**, history quality **100%**. Its header does **not** unambiguously state the selection of MT5 `Every tick` versus real-tick modeling mode. No undocumented tester mode is asserted.
- **Recovered actual source MQL5:** [Experts/GoldMuwahahaMiner_R8_Microstructure.mq5](https://github.com/AnhTranHarris/gold-MUWHAHA-miner/blob/carson/mt5-r8-s1-wave-confirm-certification/Experts/GoldMuwahahaMiner_R8_Microstructure.mq5), immutable Git blob `6b2460074ed35d04cb9b4f7620194a483df17c2a`.
- Original Dukascopy Jan full ordered UTC Bid/Ask CSV.GZ `XAUUSD_DUKAS_2026_01_ticks.csv(3).gz`, **9,135,062 ticks**; compressed source SHA-256 `d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5`. No synthetic MT5 prices ever substituted into the tick stream.
- Owner original [roadmap](https://docs.google.com/document/d/1PcaksxuiayFXVW3QtKfzitARvQj6NyL4IIbGhG8K9z4/edit), [anti-drift law](https://docs.google.com/document/d/1eG5F76uvm9M-1JXs4LvAaTzPEurU5l4Pgj2sUUelc1o/edit), [January source law](https://docs.google.com/document/d/15psoEliXaPEXJr22cKlJb4OGmWo26j3Eu8GlTtH26Kw/edit) remain authoritative.

## January MT5 deal reconstruction — directly measured, not inferred

- **34,763** completed trades, **69,526** matching in/out deals, zero unmatched. **At most one concurrent open position** across January; this is directly verified from ordered in/out ledger rather than inferred from EA design alone.
- Monthly cash net after original report commission/swap **+$26,578.23**, January-end balance **$26,678.23** from initial $100. Original deal-based win rate **74.35%**, median holding **24s**, average **30.6s**. 21/21 January report exit-days had positive net after fees. Earliest observed report-clock trade exit with balance >=$10,000: **2026-01-26 03:03:42**. This is one historic continued account, not ten independent starts.
- Largest January **closed-balance** peak-to-trough drawdown **$31.28**; tick-floating equity/margin path **cannot** be inferred from these second-resolution MT5 deal rows. Minimum closing balance $100.00. Full January R8 report and its 8-month aggregates must not be conflated.

### Mechanism breakdown from actual entry comments

| Observed R8 entry mechanism | January closes | Net after reported fees | Wins | Mean holding |
|---|---:|---:|---:|---:|
| CONT_UP | 19,888 | +11,807.77 | 72.2% | 32.7s |
| CONT_DN | 8,812 | +6,848.94 | 72.0% | 25.3s |
| SWEEP_DN | 800 | +1,706.62 | 90.0% | 32.7s |
| SWEEP_UP | 5,263 | +6,214.90 | 84.0% | 31.4s |

### Recovered implementation contract from original MQL5

- Fixed 0.01 lots; **one managed position at a time** via `FindOurPosition`, then `Reconcile`/`ManagePosition` before allowing any new signal.
- Completed **1-second Bid bars**, last **20 completed second bars** for liquidity upper/lower, last **5 completed second closes** plus current Bid for directional displacement and path efficiency. No uncompleted future bar is input.
- `MICRO_IDLE → UPPER/LOWER_BREAK → UPPER/LOWER_RECLAIM` state machine: CONT_UP, CONT_DN, SWEEP_UP, SWEEP_DN; 2-second persistence, 20-second expiry, 10/15/8/15 pip buffer/reclaim/confirm/velocity thresholds using `InpHunterPipPrice=0.01` and directional efficiency >=0.30.
- M5 ATR(14) read at **shift 1 completed bar**; session-specific minimum ($2 London / $1.75 overlap or NY / $2.50 off session); fail-closed on missing ATR; configured max spread **25 symbol points**. A $0.25 gate in Python is conditional on `SYMBOL_POINT = 0.01` (symbol precision not independently verified from the original XLSX).
- 300 pip ($3) initial stop from Bid for a buy / Ask for a sell, trailing activated at 18 pips ($0.18), trail distance 5 pips ($0.05), max hold 60s, 1s cooldown, 5 new trades/minute, no martingale.

## Cross-feed report-clock and quote matching

R8 tester stamps are in **broker report time**, not proven UTC. Original Dukascopy clock is UTC. For the first 2,500 MT5 trades, compare the reported MT5 entry price with the first Dukascopy same-side executable quote 250ms after the candidate UTC-adjusted entry time, requiring a quote within 2s:

| Offset applied to R8 timestamp to get UTC | Matched entry subset | Median absolute entry-price difference |
|---|---:|---:|
| -3 hours | 31173 full-Jan pairs repriced | $7.465 |
| -2 hours | 32907 full-Jan pairs repriced | $0.438 |
| -1 hours | 31419 full-Jan pairs repriced | $7.248 |
| +0 hours | 30730 full-Jan pairs repriced | $10.778 |

**UTC = R8 report clock − 2 hours** fits distinctly best among tested offsets and is adopted only as a research clock hypothesis. Source `InpQuoteUtcOffsetMinutes=0` does not prove the broker report server runs at UTC.

## Historical MT5 tape → original Dukascopy quote repricing (NOT a causal strategy)

- Keep each MT5 historical entry **and exit** timing and side fixed as retrospective observations, price only at the first executable original Dukascopy Bid/Ask quote ≥250ms later, requiring ≤2s staleness. Commission/cost is replaced with **$0.20 round-trip** for the project research contract. **32,907/34,763** trades found both required quotes; **1,856** have unmatched quote constraints and are never booked as wins.
- Under the -2h clock hypothesis, **repriced matched-only net = −$22,786.18**, win rate **24.61%**, and a $100 closed-cash overlay breaches zero after the 107th matched historical close. This cash overlay is invalid after zero for any actual account and **does not** include tick-floating drawdown, broker position rejection, or forced-liquidation effects.
- The original MT5 report produced +$26,578.23 on those historic January trade decisions. The reversal highlights severe feed dependence. **Do not claim this counterfactual is the R8 causal Dukascopy strategy P&L**, because copying historical MT5 exit times leaks decisions from a different feed.

## Causal Python port: original tick-only source reconstruction

The new `r8_causal_tick_port.py` does **not** inspect MT5 entry or exit histories. It derives prior completed-second microstructure, finished M5 ATR, state, and positions from ordered Dukascopy ticks; simulated 250ms market requests execute at first eligible original quote; exits use original-side Bid/Ask and source-inspired trailing/60s maximum hold. Fixed 0.01 lot assumed 1 oz, 500:1 leverage, 100% modeled margin stopout, 20-cent round-trip. No future-market features; in-sample only. The MQL5 port is approximate where Coinexx broker symbol metadata and order execution behavior are unavailable.

For spread control below, symbol point **assumed** $0.01, so configured 25 points means $0.25. The Dukascopy monthly median spread was **$0.700**, while only **4,346/9,135,062** quotes (**0.0476%**) have spread ≤$0.25. Compare wider thresholds only as *counterfactual modifications*, never original R8 equivalence:

| Dukascopy max spread allowed | Executed closed trades | Ending $100 equity | Minimum marked equity | Maximum tick-equity DD | Wins |
|---|---:|---:|---:|---:|---:|
{variant}

**Result:** The source-equivalent 25-point approximation finds limited valid tick opportunities and loses money; widening the ceiling increases request activity but quickly depletes fundable equity. The original **R8 survivability is not causally replicated** by current Dukascopy fee, spread, latency, margin and broker-stop assumptions. Under strict source-like spread, account minimum marked equity fell to ~$45.95 (not $0); under looser variants margin-based risk throttled the account near $8.7. None of these are profitable over January.

## What to carry into January Vertical Grid micro-account research

1. **Preserve the R8 single-position active-risk budget** as an experimental L7 micro-account sleeve; it eliminates the 128–256 simultaneously funded inventory problem from later shadow campaigns. Its 34,763 January MT5 trades demonstrate that historical high velocity did **not** require position pyramiding.
2. Port the **four independent R8 continuation/sweep state** transitions and **completed-second liquidity/velocity** as a reconstructible *opportunity source*, keeping signal states detached from historical MT5 trade IDs.
3. Preserve **tick-sided 1-second cooldown**, five-per-minute counter, ATR-shift-1 regime gating, spread admission, time cap, trail-profit capture, and realized equity/margin admission. Do not loosen risk rules just to match trade counts.
4. Treat **spread geometry and source-clock mismatch** as central research constraints. Candidate module should record tick-level entry-spread percentile, realized net after original Bid/Ask, slippage stress, and hourly equity with the original Dukascopy data.
5. **Do not promote or combine profit numbers** until source-only micro-account trade/position/cost/risk ledgers beat the defended January controls at the same hypothetical $100 account size. In particular, do not interpret R8 $100 MT5 as equivalent to R9 OVERFIT retrospective teacher scores.

### Reproducibility and limitations

Run `r8_jan_fast_extract.py` on the original R8 `.xlsx`, then `r8_analyze_jan_deals.py`, then `r8_map_fast.py` to reprice historic tape and `R8_JAN_DUKAS_RESEARCH/r8_causal_tick_port.py` to run genuinely causal original-tick sensitivity. The first scripts require the original workbook and tick gzip at the exact configured paths; adapt paths locally if necessary. The zip report includes all derived original January deal mappings but **does not redistribute the owner's original XLSX, full original 9M-tick dataset, or proprietary font files**. R8 original EA source is read directly through GitHub using the immutable blob cited above.

Known emulator limitations: exact `SYMBOL_POINT`, contract size and hedged margin from Coinexx account, broker fill/stop/limit price policy, tick volume quality, last-known-ATR at first trading minute, executed stop modifications and original tester tick modeling mode are not independently proved here. Research-only approximations may legitimately differ in trade count and trade direction from original MT5 execution; R8 source was not edited. All tests are in-sample and not evidence of future profits or guaranteed survival.


---
**Full source-exact package (SHA-256 d93fbe832b37c9e34da85dafc8e41c0fad7fadc5a85d0b43a979bf539d09a9cf):** https://drive.google.com/file/d/1c9r22cPgDZ_d90Cl4x6-V1Lm7i3E2zng/view
**Original R8 MQL5 source:** https://github.com/AnhTranHarris/gold-MUWHAHA-miner/blob/carson/mt5-r8-s1-wave-confirm-certification/Experts/GoldMuwahahaMiner_R8_Microstructure.mq5
**Status:** unpromoted research; FourSessionV1 and J0183 not changed.
