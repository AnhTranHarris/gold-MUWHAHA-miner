# BETA 007 — First entry-first quant research pass: preregistration

Status: PREREGISTERED BOUNDED DIAGNOSTIC, not a qualifying strategy, certified feature cache, or approved EA.

Owner objective: establish correlation/interaction of ENTRY, HOLD and EXIT as a connected lifecycle, with first-stage priority on winning-entry count, after-cost entry accuracy, and opportunity throughput toward the R9 SYNTH aspirational ceiling. The historical R9 REAL report is the reference floor, NOT a same-feed Dukascopy strategy control.

Source: original verified January Dukascopy gzip. For this *bounded pilot*, read Jan 1 UTC for 5 fully completed 1-minute warm-up candles and only issue signals on Jan 2 UTC; do not touch August. This work does not replace future January-to-July scientific testing or certify a January full-month cache.

Fixed entry implementations and assumptions for this pilot (NOT externally sourced optimal parameters):
* Range: preceding 5 fully closed UTC M1 Bid candles. Upper H / lower L. Break buffer $0.25, retest cushion $0.15; max validation time 90 seconds. Raw breakout control: tick Bid crosses outside H+0.25 (long) or below L-0.25 (short). One trigger per side per 20 seconds at minimum.
* Continuation entry: preserve original breakout H/L, wait for quote to revisit/retest boundary, then renew outside H/L+/-$0.25 within 90s. This is break → retest → re-break in ordered quotes.
* Failed-ignition/sweep reversal: after original breakout, a quote crosses BACK inside the frozen range by $0.15 within 90s; countertrade direction. This is not a simultaneous fill with continuation; independent cohort events may overlap and are not an executable portfolio.
* Quote observations: Bid trigger levels, long buy at Ask and sell at Bid; short sell at Bid and buy-cover at Ask. Same-timestamp source rows retain original CSV order. Each next quote is eligible to trigger a state transition only after that quote is received. The first entry uses observed contemporaneous Bid/Ask; exit chronological.
* Markout label: fixed 5s, 15s, 30s, 60s future horizons using the first observed quote >= each horizon, and independent fixed bracket stop $1.5, target $3, 60s maximum hold, 0.01 lot XAUUSD assuming 100 oz/lot ($1 per $1 price move), $0.20 roundtrip *additional* modeled commission. These horizons, future MFE/MAE and after-the-fact win classifications are LABELS and never input to entries.
* Primary label: number of 60s bracket winning exits, while also measuring full cohort count, same-cohort win rate, net after spread + modeled commission, gross loss, max sequential diagnostic loss, false-entry latency and retention versus raw-break control. Results on a single day are UNVALIDATED exploratory labels and cannot satisfy >10% formal BETA breakthrough/promotion gates. Markout horizon net and per-event overlap are diagnostic only, not a real shared-account backtest.
* Future scientific tests: source-integrity certified Jan–Jul, statistical discovery/forward walls, monthly and total independent specialists plus jointly arbitrated chronological account, parameter and broker-cost neighborhoods, validation vs same-feed accepted parent. August sealed; no coding of MQL5 until owner authorization.

Source inspirations: public MetaQuotes opening-range and chart-object breakout retest workflows; TradingView open-source liquidity sweep/reclaim definitions. Specific pilot thresholds are independently chosen engineering controls, not copied from published tested-profit configurations.
