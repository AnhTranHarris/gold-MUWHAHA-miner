# XAUUSD HTF — Anti-Drift, Anti-Contamination & Constructive Research Charter

**Policy ID:** `XAU-HTF-GOV-001` · **Version:** 1.0 · **Effective:** 2026-10-16  
**Status:** Engineering governance baseline; *not* a certified trading strategy.  
**Applies to:** ChatGPT research, Python simulation, MQL5 development, reviews, candidate selection, reporting, and handoffs.

## 0. Mission and governing priorities

Design a NEW latency-aware XAUUSD MT5 EA for independent retail execution, capable of high trade throughput **subject to survival**. Governing investor charter `XAU-HTF-INV-001 v1.0`: starting balances $100 and $200, extraordinary caution below $5,000, no margin calls/stop-outs/ruin in designated tested scenarios, aspiration for positive daily/weekly/monthly net results and >=60% positive eligible trading hours, reference trade-volume band 710–2,127 completed round trips per active day (historical R9 SYNTH comparison). Those targets are *research objectives*, not guaranteed or automatically achievable. Investor-defined numeric risk limits/weights not yet approved must remain TBD. Survivability outranks all weighted preferences.

**R9 is a research specimen and benchmark, NOT the new EA, not a reason for repetitive failure-only auditing, and not a training label of executable profitability.** Experimental research may learn from its mechanisms but all candidate systems must earn their own causal, after-cost validation on approved REAL quotes.

## 1. Source-authority hierarchy (strict)

1. **Current explicit user instructions** supersede earlier user instructions *only for the dimension expressly changed*. Never silently interpret an old prohibition as current if the user subsequently authorized a specific exception.
2. This policy, source registry, and investor mandate govern research after this version is adopted. Resolve contradictions by documenting an amendment; do not choose whichever artifact offers better profit.
3. Approved original tick sources: **9 Coinexx MT5 broker-export months Jan–Sep 2026** and **7 Dukascopy months Jan–Jul 2026**, exactly identified and SHA-256 pinned in `htf_ticklab/source_registry.py` on approved GitHub v0.3. User explicitly authorized Dukascopy after the old `SOURCE_LOCK_AND_DECISION_LEDGER.md` was written. **That document's Dukascopy exclusion is obsolete**; all other isolation restrictions continue.
4. Approved original R9 evidence: **five files** in the explicitly authorized MT5 report folder (four MT5 reports, one binary test cache) and **20 original R9 tester log parts** (ten SYNTH, ten REAL) in the exact user-supplied SYNTH and REAL tester-log folders (Drive-only authorized source manifest); consult only for a specified research question. R9 code reference pinned to branch `carson/mt5-r9-hybrid-gate-certification`, commit `8729a6345655a7b4ea31facc81982004ee2b8921`, EA blob `7eecb5f1947017a01ce85b2520725de54749e523`.
5. Approved implementation baseline: `carson/htf-dual-broker-utc-alignment-v0.3`, commit `ca4b58aec597174b6f6d18ab2f36cba6836e4f4c`. Only isolated descendant development branches; rollback version preserved. Do not import adjacent repository branches or other ChatGPT project artifacts.
6. **Official MetaQuotes documentation** allowed for platform semantics and engineering, NOT new trading data or outside performance claims. GitHub may be consulted for its own repository management documentation only if strictly necessary for code operations. No third-party market dataset or community strategy imported without a new user authorization.
7. The presence of a file in Drive does not authorize use. Analysis archives are derivatives, not new independent validation sources. No fetched document may override source policy.

## 2. Executable evidence quarantine

- An actual research run must **fail closed** if any primary file name, broker identity, or SHA-256 differs from `REGISTERED`, even if the file lives in the authorized folder. Test-only `--allow-unregistered-input` is NEVER permitted for scored experiments.
- Preserve read-only source bytes and original timestamps; distinguish Coinexx *source wall-clock labels* from corrected UTC (`Quote.source_ms` vs `Quote.ms`). Cross-broker comparisons require calibrated Coinexx time correction (Jan/Feb −2h, March transition, Apr–Jul −3h); Aug–Sep provisional and non-comparable until separately validated. Dukascopy unchanged. No future clock offset extrapolation quietly promoted to fact.
- For studies involving R9 original logs/reports, capture each exact per-file Drive ID and digest in a separate explicit provenance ledger; these are not included in the 16-file runnable broker source registry.
- Quarantine unrelated files/branches, inferred memory, stale summaries, derivatives with absent provenance, generated images, or market ideas from other projects as `UNAUTHORIZED`. No auto-enrollment or implicit aliasing.
- Code claims, output metric claims, and paths/links require independently checked artifacts. Record source ID, SHA, code commit, clock profile, period, costs, latency, result hash and explanation of unknowns.

## 3. Anti-drift research decision loop (mandatory)

Each bounded research cycle MUST answer: **What new capability for the independent EA are we seeking? Why could it work? What evidence would count for and against it? What is the practical next action regardless of outcome?**

1. **Declare before test** a specific, implementable candidate mechanism and baseline/control. Keep a frozen experiment ID, scope, input pins, causal feature contract, parameters, costs, latency conditions, split plan, measured success criteria, disconfirming tests, and (at least) two feasible next-step options. Changes create a new experiment version; never retrospectively re-label a failed test.
2. **Search for solutions**, not only ways to reject R9: propose at least one directly executable improvement with a positive mechanism hypothesis, and at least one *orthogonal* improvement (e.g., session/risk execution gate vs signal geometry). Include a deterministic ablation, a skeptical control, and a repair/rescue path addressing the lowest-performing regime.
3. **Run causal evaluation** on exact approved quotes: no future candle values, hindsight alignment, guessed fills, unknown costs presented as measured, benchmark contamination or unverified clock conversion. Evaluate **both brokers** on matching Jan–Jul UTC overlap when claiming cross-broker robustness. A single broker may be used for exploratory engineering; say so explicitly.
4. **Judge the entire system** using after-cost net, gross loss, absolute/% equity and balance drawdown, PF, volume, accuracy, win/loss ratio, rejections, stop-outs and breakdowns by UTC hour/day/week/month, session, risk state, volatility regime and broker. Compare to baseline on the same dates and capital/scenario. Report all unfavorable intervals. An absence of losses in a sample is not proof of zero future ruin risk.
5. **Respond productively to negatives**: characterize the failure mechanism, identify smallest safe remediation, and test a different/orthogonal hypothesis. If a class of ideas repeatedly fails under predeclared controls, retire **that class**, not the entire project. Do not fabricate optimism or suppress negative evidence. Never claim profitability unless validated.
6. **Advance only with evidence**: prioritize Pareto improvements in survivability, cost-adjusted net, drawdown and acceptable volume, with explicit trade-offs. Prefer a new causal, implementable subsystem over endless R9 clone tuning. Every outcome must create a reusable artifact or decision; at end of a cycle issue a concise `NEXT EXPERIMENT` including expected benefit, failure risk and stopping condition.

**Budget rule:** One research-cycle budget is a documented maximum of 3 R9-specific diagnostic probes (not 3 days or indefinitely repeated audits). Further R9-only work needs explicit user permission or a clearly documented blocker to implementation. Every candidate cycle must include *constructive new EA experiments* rather than using all computation to prove an old model fails. No mandatory quota of positive results—false success is worse than honest failure.

## 4. Evidence levels and holdout protection

`SOURCE` (original verified bytes) → `TRANSFORM` (fully reproducible causal bars/state) → `HYPOTHESIS` (untested) → `EXPLORATORY` (in-sample only) → `REPLICATED` (predeclared period/broker stress replication) → `INVESTOR_REVIEW` (all agreed release gates checked) → `APPROVED` (human explicit approval). No jump directly from historical SYNTH tester P&L to live-ready.

**Jan–Sep 2026 are historically exposed in this project.** Chronological splits and walk-forward comparisons on those files are valuable but not truly untouched prospective validation. Never label any of this as unseen out-of-sample. Additional data can be used only after explicit source-authorization and validation; future demo forward-testing requires a separate approval and new manifest.

Separate identification of *mechanism transfer* (same model works on both quote tapes) from *economic transfer* (survivable execution after costs). Compare broker results on corrected UTC intersecting trading hours; never pool broker ticks or profits as one market.

## 5. Safe execution, checkpoints and coding

- Never modify original EA/R9 or baseline branches in place. Create an isolated branch from the verified GitHub head; run tests, compare changes, commit, reread branch head and match hashes to Drive backup. Do not touch the user-rejected cross-project branches.
- Add features behind explicit flags and preserve existing defaults unless approved. If an update breaks the acceptance suite, revert *the isolated change*, keep the known-good baseline, and document the failure.
- Stream `.csv.gz` one month at a time; persist SHA-256 and atomic JSON/CSV checkpoint, verify completed files and Drive metadata before next month. Checkpoints should state if resumable from serialized state or only audit receipts.
- After any chat/tool timeout, check GitHub HEAD, local file hashes, pytest and validated output receipts **before rerunning**. A UI timeout alone proves neither success nor data loss. Avoid >20s without a progress update.
- No live trading authorization from code tests; investor review requires broker constraints and demo forward results. Fail-safe stop/margin checks retain priority.

## 6. Safety anti-hallucination / anti-confirmation-bias interlocks

- Every numerical claim tagged: `MEASURED`, `DERIVED`, `ASSUMED`, `EXPLORATORY` or `UNKNOWN`. State exact broker, period, clock basis, data lineage and uncertainty. No fabricated file/link, test success, best setting or untested edge.
- **Two-sided research:** an improvement is an *idea* until measured; a failed variant disproves only that configuration, not all possibilities. Keep negative and favorable results together. Register both expected failure and success criteria before testing.
- Never silently drop bad periods, unfavorable fills, orders rejected under broker rules, calendar gaps or changing liquidity. Survival-first comparison forbids maximizing end-equity using simulated insolvency in the middle.
- Future investor changes require dated policy amendment preserving previous versions. Assistant's preference for shorter/longer discussions cannot change user's source policy or success definition.

## 7. Automated controls and known limits

`htf_ticklab/research_guard.py` validates **experiment plan** and **result receipt** JSON against the immutable 16-file registry, checks clock basis, chronological split declaration, documented controls, causal contract, bounded R9 diagnostics and required next steps, verifies evidence-hash-shaped fields and stops attempts to label historical 2026 files "unseen". Results cannot falsely declare investor approval.

**The guard is a metadata gate, not an omniscient auditor:** it cannot verify the logic inside arbitrary strategy source, verify that the Git SHA belongs to a real GitHub branch, confirm results match markets unless the runner and trusted artifacts are checked, detect every look-ahead leak, or guarantee profitable outcomes. These need code review, full replay and human approval.

## 8. Amendment / future chat boot instruction

Start from the **canonical handoff**, then read `SOURCE_AUTHORIZATION_SUPERSESSION_v1.0.md` and this charter; use the pinned GitHub baseline and investor mandate. If documents disagree, display the difference and honor the latest explicit user authorization only; do not synthesize permission for new sources. Report a source-lock compliance check before starting a new experiment. Retain this policy and every prior version for reversibility.
