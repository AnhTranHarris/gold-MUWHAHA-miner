# January-only: R9 generated "Every tick" M1 / M5 / H1 multi-scale diagnostic and hourly investor scorecard
**2026-10-14 | delta-A-alpha source-observation research | UNPROMOTED | no V1 executable edit / no cursor advancement**

## Owner-scoped exact primary sources
Unchanged original M1, M5, H1 Coinexx tester reports from https://drive.google.com/drive/folders/1S0erLKfFpqQUVHHIHDql72PgsH6vQrMF?usp=drive_link . SHA256 M1 `f9315c35bde962135785a0fb8fd268251086e9bebe27f5789757c69cfb38819d`, M5 `3237dfe2ebec41c0cf0699dfa65dcff1020f94869ed099b5e109b7377459face`, H1 `76f478220a910a1fbc1a0fff3c0d9141617d109a25c6a9075a6806883f07adfd`. M1 TickLogger source matched M1 reported 27,980 unique deal cycles. All three timeframe native XLSX trade ledgers match by price, ID, side and UTC-clock-second timestamp; not three independent performances. "Every tick" generated-tick mode confirmed by owner, not broker real ticks.

**COMPLETE ORIGINAL SOURCE-PINNED RUNNABLE QA ZIP UPLOADED TO PROTECTED JANUARY FOLDER** https://drive.google.com/file/d/1TemWNkYXeFl7RTx-4btGRseoRH2jO0tF/view SHA256 `37712dcefa26c2b5092d49b298bc6614f86621328bc84c06479473f30455a923`. 21 full members: both exact analysis scripts, 27,977 trade-level as-of crossfeed feature rows, original *extracted Coinexx Deals read-only* source ZIP, all **44,640 M1**, **8,928 M5**, **744 H1** bucket CSV rows incl zeros, 480h investor statistics, session/liquidity quote-density, H1/M5 direction and M5 ATR(14) attribution, JSON and source hashes. Original >100MB native xlsx and 66MB original source tick gzip remain at their existing protected source links, hashes in manifest. Do not accept this summary without source. Readable full report https://drive.google.com/file/d/1av7BAO47PFXNIv4hioY5fSIsiSYwmxnS/view SHA256 `504ccd1a1b060f1c8d9330f997c903d68b70e0ab50288ddeb7163a74e814cfd4`.

## January original R9 SYNTH tester trade outcome
$100 test start, 0.01 lot, **27,980 closes**, +$41,520.82 net, +$43,348.69 gross winners, −$1,827.87 gross losing, PF23.7154, 87.0908% winners. 21/21 trade-active UTC-calendar report dates positive, 480/480 trade-active report hours positive; **436/480** hourly winning-close percentage strictly >75%; 44/480 below or equal. **264 zero-trade** January report clock hours. 97.448% trade entries and closes within one M1. Ending closed balance $41,620.82.

## Actual signed risk and velocity by report-clock trade close bucket
**M1** 20,023 close-active of 44,640 minutes (1.40 closes/active minute), 1,418 negative net minutes, largest M1 gross loss -$1.42, largest within-minute closed-balance drawdown $1.42.
**M5** 5,338 close-active of 8,928 5m buckets (5.24 closes/active M5), 190 negative net buckets, largest M5 gross loss -$2.58, largest within-M5 closed-balance drawdown $2.16.
**H1** 480 close-active of 744 hours (58.29 closes/active hour; max 104), 0 net-negative close-active hours, largest hourly gross loss -$9.18, largest within-hour **CLOSED**-balance drawdown $3.40.
**WARNING:** those DDs are CLOSED-TRADE balance path drawdowns only, **NOT INTRATRADE FLOATING EQUITY MAX DD**. All scales are disjoint temporal groupings of same 27,980 trades and same total gross losing -$1,827.87, cannot add the values.

## Sessions, quote activity and ATR regime mechanism discovery
Cross-feed UTC offset inferred `Coinexx tester ≈ UTC+2` from price-alignment median error $0.485 vs nearest nonselected offset $8.705. Not certified; do not hide inference. Non-overlapping UTC hour buckets used to avoid ambiguous official session opening hours. Session table from original observed tester closes:
- **00–08 UTC Asia:** 9,380 closes, **56.2/active h**, net +$12,341.07, gross loss -$622.38, PF20.83.
- **08–13 UTC London pre-US:** 4,981, 47.4/h, +$6,055.21, -$377.51, PF17.04.
- **13–17 UTC overlap:** **6,908, 82.2/h**, +$11,771.93, -$402.37, PF30.26.
- **17–22 UTC US later:** 5,493, 53.3/h, +$8,907.93, -$358.87, PF25.82.
- **22–24 UTC rollover/pre-Asia:** 1,218, 58.0/h, +$2,444.68, -$66.74, PF37.63 (only 21 source-active hours).
Jan real original Dukascopy 9,135,062 quote updates as liquidity **activity proxy, NOT actual traded volume**. Same UTC active-hour quote update count vs Coinexx R9 SYNTH completed trades r≈0.611; quote updates vs synth net r≈0.716.

As-of prior completed H1/M5 price direction (on separate feed, 27,977 joinable R9 trades): H1/M5 *same sign* 14,232 historical R9 closes / net +$22,330.60 / PF25.81; *opposed* 13,616 / +$19,053.89 / PF21.69. Counter-direction **H1 vs M5 disagreement is not itself a complete veto**.
At R9 close-active hours grouped by **pre-completed Dukascopy M5 Wilder ATR14** quartile: lowest 120h ~3,666 historical closes / **+$20.92 per hour, PF8.21**; upper 120h ~9,210 historical closes / **+$199.62 per hour, PF54.10** and 120/120 hours over 75% win. **Retrospective context stratum, not a funded independent strategy**. Hourly M5 ATR vs SYNTH net/trade correlation ~.893; quote-density and volatility correlate with opportunity, but high historical hourly profitability is associated more strongly with payout/trade than simple raw trade count.
R9 M1 entry 10–39sec history: 16,113 / 99.63% wins / +$36,194.39 net, gross loss -$28.38, persists across all 5 fixed UTC windows and both H1/M5 agreement regimes; this could reflect MT5 generated-tick path and exit-stop lifecycle. Do NOT use a retrospectively selected clock phase as a executable gold strategy without causal Dukascopy full-trade replay.

## Owner January QC and promotion lock
January full law: https://docs.google.com/document/d/15psoEliXaPEXJr22cKlJb4OGmWo26j3Eu8GlTtH26Kw/edit ; preserve full V1 original owner whitepaper and anti-summary law, trade/daily/weekly/monthly originals, no January date switches, one funded physical position 0.01 fixed $100/$200; source/entry as-of; UTC crossfeed distinctions; genuine tick-level equity mark-to-market and margin. August SEALED. Historical R9 teacher labels must not migrate into student execution. This research observes the performance reference and generates tested *hypotheses*; not a new profitable strategy, not a modification to V1 production Python EA, and not approved QC. CURRENT_STATE/J0183 unchanged; trading disabled.
