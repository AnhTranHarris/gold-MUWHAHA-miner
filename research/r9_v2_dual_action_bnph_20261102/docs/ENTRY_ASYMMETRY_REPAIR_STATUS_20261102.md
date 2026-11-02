# R9 v2 Entry-Asymmetry Repair Status — 2026-11-02

## Scope
Repair contract: `R9_V2_ENTRY_ASYMMETRY_SOURCE_AUDIT_20261102.md`.
Audited baseline: `a4ae6633b306b53057a71acb6ff1df6a63225d32`.
Repair branch: `carson/r9-v2-entry-asymmetry-repair-20261102`.

This ledger distinguishes **mechanical/source repairs** from **empirical trading qualification**.
No code change in this repair is permission to promote a trading policy.

## Audit defect -> repair -> verification

| Audit defect | Repair | Verification |
|---|---|---|
| Hand-weighted specialist nominated direction before probabilistic BUY/SELL evaluation | Repaired-policy path bypasses `specialist_evidence`; legacy evidence/lane are excluded from repaired feature contract | Audit regression deliberately makes legacy specialist throw; repaired path must continue |
| 102-feature aggregates lose order-dependent subminute geometry | v5 228-feature contract adds ordered Bid/Ask lag grid, segment geometry, extreme ordering, turn rate, ranges and six-mark quote excitation | Path-collision regression: opposite event order with same terminal aggregate must produce different repaired features |
| Offline/runtime geometry precision drift | Offline sampled Bid/Ask geometry is computed in float64 and cast only at final feature output | Online/offline grid parity test |
| Online geometry used nominal lag instead of actual observed quote age | v5 geometry ordering now uses actual sampled quote age | Sparse/gap online/offline parity regression |
| Quote drought could bridge subminute geometry/excitation | >15s gap resets ordered geometry and six-mark excitation; no synthetic cross-gap mark | Gap parity regression |
| Frozen FastClock records gap but ready() ignores valid_since | Repaired v5 route separately requires 300000ms continuous fresh ordered geometry after gap | Runtime post-gap five-minute warmup regression |
| Offline teacher warmed only once / could diverge from repaired runtime | 250ms candidate generator restarts warmup after >15s gap; domain shard records warmup/gap/spread provenance | Candidate-universe gap regression |
| Argmax-before-eligibility can let failed BUY mask valid SELL | Runtime and vectorized selectors filter each side for eligibility before comparison | BUY-fails/SELL-passes regression for both selectors |
| Opportunity timing is separate from direction | Independent opportunity gate plus BUY/SELL forecasts and WAIT arbitration retained | Opportunity-low must WAIT even with strong BUY; opportunity-high can pass |
| Negative expected payoff could be hidden by score threshold changes | Positive expected-net requirement remains fail-closed; no threshold weakening | p(correct)=0.999 with negative expected net still WAIT |
| Historical 250ms SELL teacher arithmetic was corrupted | Repaired builders reject `250MS_ACTION_TIMING` archives; corrected source-exact paired-action/full-250ms labels use executable BUY/SELL prices | Corrupted-teacher rejection regression |
| Fitted session mapping was January-UTC-specific | IANA ZoneInfo mapping for Sydney/Tokyo/London/New York with DST | January + July session regression |
| Offline evaluator relied implicitly on candidate spread filtering | Explicit runtime-equivalent hard spread gate in offline evaluation | .20 admitted / 1.80 rejected at max 1.50 regression |
| Old v4 artifacts could silently load after feature-value repair | Hard feature-contract break to `r9_v2_ordered_quote_grid_v5`; WAIT transition contract to v2; downstream filenames/receipts propagated | Version-contract regression + source scan |
| Same-shape stale model could still pass a 228-column count check | v5-specific component filenames; evaluator verifies fit receipt/version/SHA-256; runtime policy bundle stores and verifies exact opportunity/BUY/SELL model hashes | Full-source compile + version/hash fail-closed code path |
| Downstream pairwise/exit-value experiments could reuse stale generic pilot/value artifacts | Pairwise v2 and exit-value v2 artifact names; baseline pilot references changed to v5; fit receipt/version/SHA verification added | Static stale-name scan + full-source compile |
| New source edits might not be imported by targeted tests | CI compiles the complete repaired Python source tree before tests | GitHub Actions compileall step |

## Preserved causal architecture
Raw ordered Bid/Ask quotes -> 250ms observed slots -> 500ms/1s/5s/15s/30s/45s/60s/120s/300s ordered geometry -> 15m/1h/4h context priors -> independent opportunity/BUY/SELL estimation -> asymmetric eligibility/expected-value arbitration -> BUY/SELL/WAIT.

Higher timeframes remain context only. They do not replace the subminute entry state.

## Explicitly unresolved empirical gates
These are **not code bugs and have not been declared repaired**:

1. Existing frozen payoff calibrations were negative across populated buckets.
2. Earlier strict p>=0.80 candidate selections were zero or non-qualifying.
3. No fresh v5 full-month/raw-source model training has been completed after the precision/gap/version fixes.
4. No fresh v5 cross-month frozen out-of-sample qualification has been completed.
5. No fresh one-position-at-a-time tick-exact on-policy replay has been completed.
6. No MQL5 deployment build/compile has been promoted from this research branch.
7. Therefore no profitable/asymmetric trading edge is claimed and no policy is approved.

## Artifact compatibility
All pre-v5 repaired feature matrices/models/calibrators are research history only. They must be regenerated before v5 qualification. A stale v4 artifact must not be relabeled or reused as v5.

## Preservation
Progress is checkpointed independently in GitHub and Google Drive. Do not merge this branch to a deployment branch until fresh raw-tick chronological qualification passes the unchanged probability, expected-net, spread, volume and one-position execution gates.
