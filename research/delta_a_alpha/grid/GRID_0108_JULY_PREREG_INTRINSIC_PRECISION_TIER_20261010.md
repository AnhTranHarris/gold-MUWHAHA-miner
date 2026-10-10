# GRID0108 — July independent lockbox: cost-to-gap precision overlay versus base K4

**COMMITTED BEFORE opening original JULY Dukascopy 2026 XAUUSD raw quote file** (2026-10-10).
No trading/ML; **pre-session grid physics only**, UTC-hour groupings for **OFFLINE DIAGNOSTICS**, no clock-based trading decisions. Original August sealed.

## Frozen candidate selected during Jan–June development
Existing GRID0104 virtual grid source: one chronological tick per event, quote-mid virtual rung anchor, spread EWMA (.001), gap in dollars=max(0.75,1.5*EWMA spread), 7second output cooldown; every event updates anchor as appropriate. K5 = |current mid - latest quote mid known at or before t-300s| / max(current Ask-Bid,0.10).

Report three distinct NON-FUNDED event tiers:
1. **Broad opportunity supply**: K5≥2 — unchanged (not necessarily tradable or correctly signed).
2. **Original strict quality**: K5≥4 — GRID0107 source frozen, unchanged.
3. **NEW ultra-precision sub-tier**: K5≥4 **and contemporaneous observed spread / contemporaneous grid gap ≤0.65**. Source-only information; an entry-independent *friction gate*, never a trading instruction. No Martingale, no held loss inventory.

This .65 was selected from Jan–June DEVELOPMENT candidates (.60 to 1.00); July is the first independent lockbox for the overlay. Therefore do not claim Jan-Jun out-of-sample discovery for .65. Do not retune based on July.

## Critical anti-tautology validation — also frozen
The previously used outcome "abs midpoint future t+120s movement > 2×spread_now" becomes easier when we choose smaller-spread events. Therefore report it as **relative friction capacity**, not proof of increased true price motion. Independently report fixed **$1.50** and **$2.00** absolute midpoint future movement thresholds at the exact same first source quote t+120s within <=10s lateness. Also report average absolute future mid movement USD, and hypothetical BUY Ask→future Bid and SELL current Bid→future Ask 120/600s quote markouts for original creator reversal and counter direction. Subtract $0.02 round-trip XAUUSD 0.01 lot commission only as clearly labeled sensitivity, no broker live fills.

## Hourly and daily scoreboard, all UTC
- Outcome and paired baseline: source virtual grid ALL future-valid events in same UTC source hour, as above.
- Eligible reference UTC hour >=20 future-valid source-grid events; a high-quality tier is supported if that hour has >=5 future-valid tier events. Report (a) win rate among SUPPORTED hours and (b) positive hours out of the original eligible baseline set, treating unsupported hours as **not achieved**; never omit quiet difficult hours from denominator.
- Detail eligible Mon–Fri UTC source hours, all UTC quote-active hours including partial Sunday. Report gains, ties, declines and missing-support.
- Daily prior GRID0107 standard >=100 future-valid baseline events and >=1 tier event. Report ALL date types, Mon–Fri separately; if tiers don't cover every trading day, that's a failure of all-day coverage. Strong prior daily result 127/127 weekdays for *K4* only, not a profit claim.
- Count raw broad/strict/precision July and compare original R9 SYNTH JULY completed entries=24,382 (reference only), as well as monthly ratios. Neither monthly raw-count ratio nor hourly quality rate meets owner's >=75% per-day **qualified executable** trading target.
- Original July compressed raw source SHA256, tick count and first/last time to document. No Apr/March contamination or other derived funded engine import. No session, MTF, risk/capital/TP/SL, position or physical trade can run.
- July's result is final for this predeclared .65 precision rule. If it fails independent July, preserve failure; do not relabel or iterate on July and claim July lockbox.
- UTC clocks only for diagnostics; future broker timezone conversion and session state are separate later architecture. $100,000 hypothetical future funded-research account remains NOT relevant to this grid-only stage.
- Evaluate the corresponding FIVE/SIX prior observed development months with the same absolute-$1.50/$2.00 anti-tautology metrics for comparable full record. Do not call that independent validation.

Research inspirations (not empirical results): https://www.mql5.com/en/articles/21833 ; https://www.mql5.com/en/articles/22940 ; https://hudsonthames.org/does-meta-labeling-add-to-signal-efficacy-triple-barrier-method/
Dev code SHA256 fixed: hourly_feature_search.py 18d776a97e73ea2864da75bca49a296962712740a52f1425348cd105d1907e9d ; cost_ladder_compare.py 8c16a203a84c4c44a6f836019d773ecda8e9f859428a41b504c374ef91b7f068 .
