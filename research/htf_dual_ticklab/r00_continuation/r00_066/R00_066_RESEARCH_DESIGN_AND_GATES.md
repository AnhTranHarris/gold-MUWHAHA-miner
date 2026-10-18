# R00-ENTRY-066: Native quote chronology and competing first-passage hazard

**Status:** DESIGN ONLY. Four synthetic unit tests passed; no month replay, model fit, calibration, score, executable fill or P&L.

Canonical unchanged contract resides in all complete original R00-063/064/065 research ZIPs as R00_066_DESIGN_ONLY_NEXT_CONTRACT.json.

Use exactly eight approved, individually SHA-256 pinned Coinexx and Dukascopy January, February, June and July 2026 XAUUSD bid/ask tapes; brokers stay separate. Coinexx local wall-clock to UTC: Jan/Feb -120 minutes, Jun/Jul -180 minutes; Dukascopy native UTC unchanged.

Hypothesis: original quote-side bid-only/ask-only/both innovations, response order, spread recovery, observed quote arrival rates, independent expert stage/age/conflict and fully completed M15/H1 structure improve causal 30-second UP/DOWN/NEUTRAL hazard discrimination and preserve high-volume correct signal supply. Dealer quote updates must never be claimed as actual traded exchange volume.

January training; February frozen selection; June/July historically exposed (not blind) comparison. No future-data feature gating. Confirmed swing features require timestamped availability at or before decision. Primary diagnostic: first original midpoint at or after decision+30s with freshness strictly under two seconds, > $0.10 signed move for selected side, neutrals/missing wrong.

Targets: >=80% directional accuracy, >=90% of matched R9 correct-direction count in every eligible UTC hour/day, both sides, publish all misses and intervals. Reference old R00-054 548099/1231388 and original R00-063 177178/389558; original R00-064/065 require separately relabeled training/calibration/transfer before being treated as valid 30s controls.

Ablations: full vs minus quote chronology, bid/ask asymmetry, completed HTF, independent hazard and cooperation; include a matched-throughput skeptical control. Test full tick prefix invariance and max feature dependency timestamp.

Next engineering action: scoped +30s target repair of R00-064/065 on isolated working copy, preserving originals, then implement and freeze the new R00-066 hazard experiment.

Full EA evaluation later requires survival-first whole-account paired $100/$200 capital, independent broker execution, realistic spread, margin and 0/250/1000ms latency; no investor approval or profit metrics are established here.
