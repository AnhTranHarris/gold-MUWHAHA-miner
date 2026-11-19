# AR1 January R5 — Atlas-first reverse engineering and strict-entry self-proof

**Research-only branch:** `carson/ar1-january-r5-atlas-first-strict-asof`, isolated from the R9 EA and owner-frozen S100 V2.

## Source contract

- The January 2026 **R9 SYNTH original history** supplies 27,980 immutable entries, exits, sides, cycle/leg identities, fee-inclusive booked net outcomes and historical booked balance. R9 synthetic intraday prices are **not** inputs.
- The **Coinexx REAL TickLogger** supplies original January millisecond Bid/Ask quotes, observed intrahold price paths and causal market context; 21 original daily gzip tick files, 7,699,274 quotes. No raw ticks committed to GitHub.
- **S100 V2** remains owner-frozen. Per-position $100-tier allowance serves as read-only reference. Neither S100 nor original trade timing, fees or outcomes are changed.
- The Atlas has 27 reporting lines (23 disjoint atomic, 4 overlapping A/B/C/D rollups) and January 240 key witnesses. Reporting rollups are not additive.

## Method — historical point → mechanism → formula → full self-proof

1. `01_atlas_reverse_engineering.py` identifies and matches original R9 loss, recovery, extreme floating-drawdown and profitable-trade protection witnesses.
2. `03_atlas_microstructure_ha_fib_scan.cpp` performs read-only full January Coinexx scan. It constructs completed 1/5/15/30-second Heikin-Ashi states, causally confirmed Fibonacci swing geometry and real-tick quote context.
3. **Strict entry timestamp:** market features use quotes STRICTLY BEFORE the beginning of the original R9 entry second. A previous January feature index was one second after original textual entry, an unverified predictor clock; R5 does not reuse it for entry prediction. Known previous-trade outcomes are causally constrained, including ambiguity around 21 same-second exits/reentries.
4. `04_atlas_micro_witness_mechanism_contrasts.py` and `06_verify_strict_entry_clock_independent_python.py` independently check Atlas contrasts and raw tick witness time ordering.
5. `07_strict_book_context_and_ha_fib_models.py` fits distinct entry-time earlier-train/later-test January models of R9 recorded negative-leg risk, including explicit HA × Fibonacci × lifecycle interactions. These are observational scores, not trade directives.
6. `08_january_full_source_exact_observer_selfproof.py` checks all original trades, 240 Atlas witnesses, 270 family-by-frozen-S100 cells and diagnostic model results.
7. `09_nonleakage_negative_control_and_day_bootstrap.py` evaluates internal negative controls and conditional day-block uncertainty.
8. `10_python_full_coinexx_fixed_r9_observer_selfproof.py` independently walks all 21 original January Coinexx gzip files and verifies quote counts, MFE, MAE and floating giveback for **all 27,980** R9 positions against previous exact-window records.

## January chronological internal results

- **21,069 later-date trades** in four strictly chronological earlier-train/later-test blocks; 2,637 recorded losing R9 legs in the test rows.
- Strict causal baseline **AP 0.710462 / ROC-AUC 0.950241**.
- Atlas-driven combined short-horizon HA + Fibonacci + lifecycle interactions **AP 0.718657 / ROC-AUC 0.952295**, Brier 0.056083.
- Day-block bootstrap for incremental AP (internal conditional): **+0.00259 to +0.01347**.
- Shuffled-label within-day/leg control: **AP 0.17530**, not a substitute for independent future-year validation.
- At *diagnostic* score 0.50: **1,633** of **2,637** losing trades flagged and **737 originally profitable** trades also flagged. Not authorized to veto them.
- Full original fixed-window Python source parity: **0 mismatches** across 27,980; 2,272,602 observed intrahold quotes; 33 windows without observed inside-window tick; 930 trades with ≥25% S100 utilization, 110 with ≥50%, 0 observed full S100 touches.

**Important limits:** stronger January retrospective loss discrimination is not verified ability to preserve profitable trades under altered order behavior. January $4/$5 early-capital tiers lacked earlier-in-January training observations. Four validation blocks are still entirely within January and were subject to research iteration; forward performance, executions, account-risk interventions, future regime transfer and realized Coinexx account protection are **not certified**. The frozen original R9 booked balance $100 → $41,620.82 is unchanged.

## Authoritative reproducibility artifacts

- Verified research report: https://drive.google.com/file/d/1iX74oHE3uv0odIdHDnNDRTDq1z539Rnp/view
- Complete **19.17 MB** read-only reproducibility archive, with source receipts and small derived tables: https://drive.google.com/file/d/1JPqefJIXQMvaKGQcbnPyjRqVRLIk9Dkf/view
- This GitHub branch contains reproducible source code but not the original private Coinexx gzip inputs or full result tables. The complete archive plus unchanged original historical data is required to rerun the self-proof.

**No R9 EA code edits, S100 reoptimization, trade filters, alternative exits, trades rebooked, or live deployment.**
