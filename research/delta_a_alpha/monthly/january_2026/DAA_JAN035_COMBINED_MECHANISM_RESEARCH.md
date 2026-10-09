# Delta-A-Alpha — January 035 Combined-Mechanism Risk Research

**Checkpoint:** 035 / 2026-10-08–09 research continuity  
**Original system source of truth:** `research/delta_a_alpha/whitepapers/DAA_V1_OWNER_GOOGLE_WHITEPAPER_FULL_VERBATIM_030.txt` (original L0–L7); Owner Hard Lock 031 and Source Restoration 030.  
**Upstream:** Jan032 original 131E source Bid/Ask tape, Jan033 source-labeled exact equity reconstruction, Jan034 54 causal fixed-tape screening tests.  
**Status:** **SCREENING — NO OWNER V1 ECONOMIC PROMOTION**. Original physically funded 049/051/075/084/119→131E parent genealogy, later native/recovery and Coinexx order/margin parity **NOT** certified. Never call these a full integrated V1 deployment.

## Objective and absolute constraints

Improve January gross loss, maximum full-tick equity drawdown, PF and ideally net profit while retaining high trade velocity **without Martingale, increased lot sizes, normalized spread, future bars, hindsight admission, or replacing the original hourly harvesting engine**. Jan→Jul accumulation is based on completed causal state rather than month labels. January has already been outcome-exposed and **is not a pristine holdout**. August sealed; September reserved.

Source: Dukascopy 2026-01 actual 9,135,062 ordered Bid/Ask ticks, `XAUUSD_DUKAS_2026_01_ticks.csv(3).gz`, archival SHA-256 `d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5`. Trades: original source 47,511 opportunities; fixed 0.01 lots; 0.01 lot treated as 1 XAU ounce, $0.02 research fee per trade. Per-ticket P/L recomputed from recorded entry Ask/exit Bid for buys, entry Bid/exit Ask for sells. No additional slippage or Coinexx verified broker commission and margin.

## Cross-check: independently inspectable public implementations

1. QuantConnect LEAN [MaximumDrawdownPercentPortfolio](https://github.com/QuantConnect/Lean/blob/master/Algorithm.Framework/Risk/MaximumDrawdownPercentPortfolio.py) provides a documented portfolio risk gate that monitors portfolio drawdown. We adapt its **concept**, not its fixed percent thresholds or forced liquidation.
2. QuantConnect LEAN [MaximumSectorExposureRiskManagementModel](https://github.com/QuantConnect/Lean/blob/master/Algorithm.Framework/Risk/MaximumSectorExposureRiskManagementModel.py) illustrates aggregating related exposure into one bound. Our analogue is **net directional XAUUSD/parent-campaign exposure**, not security-sector names.
3. River [ADWIN](https://github.com/online-ml/river/blob/main/river/drift/adwin.py) is a reproducible streaming change detector; it motivates an optional **already-observed change/volatility state**, not a future-return oracle or a direct imported trading rule.
4. MetaQuotes [constrained-grid research](https://www.mql5.com/en/articles/21833) explores finite cycles, ATR/cycle filters and CUSUM. We keep the **owner whitepaper's exact session grid/MTF/event genealogy**, reject imported loss-dependent sizing, and use only disclosed reconstructible reasoning. Claims of profitability from the article were **not** assumed.
5. MetaQuotes [`PositionCloseBy`](https://www.mql5.com/en/docs/standardlibrary/tradeclasses/ctrade/ctradepositioncloseby) and [`PositionClose`](https://www.mql5.com/en/docs/standardlibrary/tradeclasses/ctrade/ctradepositionclose) clarify that hedging/close execution is broker- and account-type-dependent and server return-code verification is necessary. An opposite position is not a profit guarantee.

## Atomic experiment cycle

Three separately checkpointed screen families:

- **198 combinations**: fixed quote-concurrency caps, floating-only no-new-admission gates, spread ceilings, 5/15s already-observed adverse microtrend, position concurrency and entry-known quote-volatility stress, plus combined states.
- **55 combinations**: adaptive same-quote limit using **previously observed 5/15/60s price drift** with current candidate direction and entry spread. Large sweep was interrupted after completed samples; rescheduled a smaller atomic set and verified all 55. No unfinished computations are represented as complete.
- **38 combinations**: broker-rate proxies of 1/2/4/8/16/32/48/64 orders per recorded quote, spread ceilings and total active Watchdog inventory limits.

**Total 291 complete configurations**, some with intentionally duplicate equivalent parameters. All 8 selected full-tick replays have reconciled daily/weekly trade counts and realized P/L, and preserve unchanged +$60,197.326 original hourly harvesting P/L. Precise per-campaign funding genealogy **remains fixed**; future parent suggestions do not disappear after rejected/early-closed child trades.

## Main January 2026 comparison

| Configuration | Net USD | Trades | Gross loss USD | PF | Max tick-equity DD USD | Description |
|---|---:|---:|---:|---:|---:|---|
| Original 131E actual Bid/Ask | +93,425.31 | 47,511 | -31,946.45 | 3.924 | 56,921.60 | Original candidate tape |
| Fixed 384 Watchdog proposals/quote | **+93,656.48** | **39,292** | **-18,361.18** | **6.101** | **43,224.84** | Improves net, gross loss, PF and DD; velocity lower |
| 384 + current entry spread at most $3 | +93,319.44 | 34,112 | -10,868.60 | 9.586 | 43,224.84 | Stronger gross-loss/PF, slightly lower net |
| 256 + WD floating loss blocks new entries below -$500 | +85,483.62 | 28,679 | -9,488.44 | 10.009 | 28,727.62 | Preserves >R9 SYNTH 27,980 monthly trades |
| Fixed 192 proposals/quote | +86,667.92 | 29,801 | -10,044.87 | 9.628 | 26,148.36 | Prior 034 balanced reference replicated |
| 256 + entry spread at most $2 | +76,451.48 | 20,905 | -5,225.01 | 15.632 | 9,043.71 | Low-risk high PF; fails desired velocity |
| 512 + entry spread at most $3 | **+93,864.17** | 37,509 | -15,656.39 | 6.995 | 54,609.16 | Highest January net among three screens, but DD remains high |
| One Watchdog ticket per observed quote | +66,159.82 | 13,087 | -4,386.37 | 16.083 | 6,863.37 | More conservative execution-rate proxy; misses volume goal |
| **R9 SYNTH January** | **+41,520.82** | **27,980** | **-2,071.61** | **21.043** | MT5 tester realized-balance DD not comparable | Original canonical MT5 benchmark |

All eight replayed research scenarios had positive net in all five ISO weeks and beat the R9 SYNTH weekly **net** number. The 384 cap scenario had 20/21 positive active days and beat R9 SYNTH daily net on 13/21 dates. Its entire +$231.171 profit uplift and 8,219 removed candidate tickets occur **on January 30 only**; no claim of calendar-independent behavior is warranted. Results are January-selected, and the total-stress improvement also depends heavily on that episode.

### Quantifying what the improvement did not prove

- January R9 SYNTH still dominates on **gross loss and PF**, despite exceeding its net and (selected configs) trades.
- The raw 131E inherited report admits **hundreds of simultaneous prospective orders on a single raw-market quote**. One-per-quote testing sharply reduces 0.01-lot trade count. Actual broker supported execution rate and slippage are **unknown**.
- We did not recompute future 049/051/075/084/119 Watchdog parent-selection and four-fast-funded-win streaks after rejected children. **The measured result is conditional on the archived potential-entry stream.** It cannot be promoted into original whitepaper V1 performance.
- We did not rebuild the complete source-exact trend-within-trend native/surgical recovery routes in this screen. Generic recovery in 034 failed. No foundation for claiming that new opposite-direction trades automatically convert Watchdog losses to profit.
- No January 1 300-second cold-start certification: December 2025 complete H4/H1/M15/M5 broker warmup remains missing.
- The 55-case adaptive momentum sweep **did not generate a stronger performance frontier than simple quote-concurrency/spread gates** at tested parameters. This is a negative scientific finding; do not rebrand it.

## Hypotheses to transfer to **source-exact funded engine**

### H1: physical cluster risk escrow (L4→L7)

Fund first-parent Watchdog scout exactly per original source; attach a parent/campaign + quote-event identity to each child. Require that the governor has enough *signed* portfolio stress allowance to fund an additional 0.01 lot. Debit the entire same-tick correlated cohort as one group for stress accounting. Admit less when directional heat is high; hold disabled proposals as **shadows with zero funded P/L**. Broker fill acknowledgements and margin determine actual admission. **Do not** infer that 384 identical orders will be accepted by Coinexx.

### H2: native trend transfer before recovery (L2→L5→L6→L7)

Preserve completed H4 environment, H1 location, M15 phase, M5 transfer, and original tick-first session-grid anchor/birth. On causal wrong-direction/failed-ignition evidence, **relock campaign renewal and stop allocating new wrong-side Watchdog funding**. Reallocate capacity only to the source-exact independently qualified trend-within-trend native proposal. Then permit *one* source-owned fixed 0.01-lot recovery only after actual failed ignition/transfer evidence; it is **not** a loss-scaled hedge. No generic reverse-on-stop.

### H3: escrow-release/ratchet (L4→L5→L7)

Propose retaining a small number of funded runner positions across eligible continuation regimes when their *executable* favorable excursion proves persistence, instead of issuing many clone tickets at one quote. Only change actual stop/lifecycle when separately tick-replayed. Account for funded parent-child renewal evidence after funding selection, no virtual credits. This could improve realized profit *per funded position* and make broker execution rate more realistic. No proof in 035—research item.

### H4: lifecycle-aware regime confidence (L2→L4)

Use previous funded *closed* child P/L, hold buckets, depth and causally completed market-state transitions (April 136T2) for admission decisions. Unfunded shadow outcomes can inform estimation but must never increment Watchdog's funded four-win unlock. Cold start retains original scout route immediately once quote/history/margin valid; online maturity must not delay readiness.

## Next proof gate

1. **Build the original source-exact physical 049/051/075/084/119→131E parent-child engine** so the prior profitable child is credited only if physically funded and exited before the next proposed parent; enforce broker-constrained order submission rate, 0.01 lot and unified source/time/event ownership.
2. Restore source-exact all-original L0–L7 components, including L3 London/overlap/NY and distinct Asia, L5 trend-within-trend, L6 funded wrong-direction recovery, L7 actual bid/ask/margin/free-equity/stopout governor.
3. Transfer the basic 192/256/384 quote-concentration controls and causal market-state refinements **without reranking against future weeks/months**. Re-run Jan raw tick level daily/weekly/month net/PF/gross-loss/velocity/full-tick DD and *physical* broker constraints; then use Jan→Jul lineage with clean forward periods.
4. The initial trade-readiness rule remains ≤300 seconds **from the first eligible broker quote with valid completed prestart history**, never forced or guaranteed-profit entry.
5. Do not open August or September without owner consent.

**Scientific decision:** The January-source quote-concentration fix is worth source-faithful integration, but **no confirmed full-system breakthrough** yet. Raising net while radically reducing loss/DD and maintaining reliable broker-sized velocity still requires genuine parent genealogy and live-grade order mechanics.