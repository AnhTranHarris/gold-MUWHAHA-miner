# XAUUSD HTF — Whole-System, Research-Lineage & Constructive Progress Charter v1.1

**Policy:** XAU-HTF-SYSTEM/1.1  
**Status:** Engineering governance and pre-promotion gate, **not** investor approval or proof of a trading advantage.  
**Adds to, does not replace:** `XAU-HTF-GOV-001/1.0`, `XAU-HTF-INV-001 v1.0`, and `XAU-HTF-SRC-002`.

## Controlling principle

> Judge the **complete EA against the complete EA**, not one subsystem against the profit factor of an entire system, and never add isolated component profits as if they shared no position/margin/execution conflicts.

An individual strategy can be weak alone yet reduce aggregate drawdown, increase trading coverage, protect risk during certain sessions, or diversify an existing system. A great standalone strategy can impair the whole EA by duplicating signals, increasing correlated losses, overusing margin, delaying orders, or consuming broker capacity. **No automatic dismissal or promotion from component-only results.**

The investor mandate requires priority on $100/$200 survival below $5,000, after-cost growth, losses and equity drawdown, then suitable throughput. Positive hours/days/weeks/months and 710–2,127 active-day closed trades remain targets, not fabricated guarantees. No new numeric investor weights were approved; the comparison uses a **vector of whole-system metrics and explicit hard survival gates**, not a fictitious weighted scalar.

## Six independent interlocks

### 1. Source quarantine and temporal alignment
Only expressly supplied authorized Coinexx and Dukascopy monthly files are eligible for paired research. Every source is verified by filename, broker, and SHA-256. R9 is research-only and bounded by the existing budget. New feeds, similar filenames, older ChatGPT work, foreign branches and adjacent Drive files cannot auto-enroll. The already calibrated Coinexx UTC normalization is mandatory; Dukascopy remains on native UTC. Cross-broker comparisons use the **intersection of valid UTC coverage** and stay separate per broker. August–September Coinexx lack matching approved Dukascopy, so are not independently replicated.

### 2. Sealed lineage DAG (anti-amnesia, anti-hallucinated origin)
Every scored mechanism must have connected lineage nodes `SOURCE → TRANSFORM → HYPOTHESIS → EXPERIMENT → RESULT → DECISION → BUILD`. Each node has a unique ID, permitted parent type, immutable artifact digest and pinned code commit; source roots must match the allowed registry. The checker detects duplicate IDs, orphaned results, unapproved sources, dangling edges and cycles. A lineage node **records a claim of ancestry**; its digest alone is not proof of the underlying market computation. Actual file bytes must be independently attested.

### 3. Dual-track research (anti-failure-only, pro-results)
Keep two active lanes: **constructive system building** and **adversarial validity checking**. Every experiment has a proposed new implementable subsystem and an orthogonal repair/alternative, a disconfirming test, an ablation, and a finite stop rule. A failed configuration triggers diagnosis then bounded repair or retirement of that **mechanism**, not a conclusion that the new EA is impossible. A favorable configuration triggers stress tests, not automatic promotion. This explicitly blocks endless R9 forensics and artificial positivity alike.

### 4. Complete-EA paired counterfactual (anti-single-candidate evaluation)
For each study, run the baseline integrated EA **S** and the candidate integrated EA **S'** independently from the same capital on the same quote stream, time intervals, broker cost assumptions and latency model. Both have a single shared cash, equity and margin state **within each replay**. Other existing components stay active unless explicitly changed in the new build. Compare the entire chronological account path and all unfavorable hours/days/weeks/months; standalone component returns are diagnostics only.

The core signal is a *multidimensional marginal system effect*:

`Δ_system = metrics(S') − metrics(S)`

Interpret the direction of each metric correctly: higher after-cost net is better, lower gross loss and equity drawdown are better, zero margin calls/stop-outs/ruin events is mandatory for research advancement; throughput is evaluated against the investor band without forcing trades. Avoid pooling Coinexx and Dukascopy profits: separate broker accounts/scenarios are independent counterfactuals, never one pooled tradable account.

The 12 mandatory scenario slots for paired research are `broker ∈ {Coinexx, Dukascopy}`, `initial_balance ∈ {$100, $200}` and `latency ∈ {0, 250, 1000 ms}` (the example plan's predeclared research delays). Scenario values can only change through a versioned experiment plan. Every slot needs both the baseline and candidate full-EA scorecard with the same input/fee configuration digest, plus full interval coverage and trade-ledger/run-artifact hashes. Required metrics include net, gross loss, equity drawdown, PF, trade counts, win accuracy, win/loss ratio, hourly/day/week/month results and capital-survival incidents.

**Research-only advance** is permitted only when all candidate scenarios have zero margin calls, zero stop-outs and zero ruin events, and at least one verified system metric improves under the same paired conditions. This weak advance permits *additional integrated research only*, not deployment or investor certification. The final investor release standard requires far stronger durability, whole-path audit, actual artifact verification, approved risk limits and forward-demo evidence.

### 5. Explicit synergy and interaction (pro-composition)
A candidate that seems poor in isolation may have useful conditional/portfolio value. When claiming synergy between subsystem A and B, execute four **entire-EA** arms under identical account/broker/latency conditions: `S`, `S+A`, `S+B`, `S+A+B`. Require distinct integrated build compositions and separate chronological replay receipts. For any scalar *diagnostic* metric F, the interaction is:

`I_F(A,B) = F(S+A+B) − F(S+A) − F(S+B) + F(S)`

For drawdown and profit factor, don't interpret the numerical interaction as additive dollars: record direct four-arm distributions, tail risk and broker differences. No synergy claim can be supported by summing separate backtest profits. A subsystem is only retired after its paired *whole-system* removals/replacements fail the predeclared purposes, with lineage evidence and finite resource budgets.

### 6. Build-first recovery and human promotion (pro-system build/anti-fail)
Every result must document a **specific next implementable EA build action**, a next experiment ID distinct from the current one, positive and negative follow-ups, stop rule, recovery pointer and hashed handoff. It is not enough to write “research failed.” Full source remains on an isolated GitHub branch with rollback ancestry. Stream one month at a time with atomic checkpoints. On timeout, reconcile current Drive/GitHub hashes and test output before rerunning; no destruction of the prior working system.

**Decision states:** `research_only / requires_repair / inconclusive`. A passing metadata gate **never** declares `live_ready`, `investor_approved`, or a guaranteed profit. Actual capital-survival and edge certification require independent replay evidence, chronological ledger inspection, cross-broker durability, broker-specific fill-model calibration and investor decision.

## Additional enforcement layers recommended for later implementation

The current v1.1 checker is an **additive evidence and decision guard**, not an alteration of the live-trading engine. Further hardening candidates (to be separately implemented and tested):

1. Make the scored backtest launcher require a sealed plan digest and write an immutable execution receipt; leave the low-level CLI for exploratory runs.
2. Recompute all strategy and **portfolio** figures directly from tick-marked position/equity ledgers, including simultaneous order priority and shared margin. A digest-shaped string alone cannot certify a financial result.
3. Require exact per-broker and per-session regime coverage, bootstrap uncertainty ranges and time-purged walk-forward studies while acknowledging that 2026 data has been viewed before.
4. Add causal feature dependency tracing (max observed source time for every decision), including tick handler backlog and broker callback simulation.
5. Add an independent portfolio-integration test harness to replay multiple sub-strategies together with single execution/risk arbitration; validate that their order streams and fills are not merely concatenated.
6. Add explicit human investor sign-off backed by an approval record, never by a Boolean set by the same evaluator.

## How to use

From `research/htf_dual_ticklab`:

```bash
python -m pytest -q
python -m htf_ticklab.research_guard check-plan governance/EXPERIMENT_PLAN_EXAMPLE.json
python -m htf_ticklab.system_guard check-lineage governance/SYSTEM_LINEAGE_EXAMPLE.json
python -m htf_ticklab.system_guard check-system-plan governance/EXPERIMENT_PLAN_EXAMPLE.json governance/SYSTEM_PLAN_EXAMPLE.json governance/SYSTEM_LINEAGE_EXAMPLE.json
```

**Examples are mock governance structures, not actual experiments, successful strategies or validated live builds.** A real experiment needs its own frozen files and proof of market data, code, and actual ledger integrity. `check-system-result` reads the four files `v1_plan.json system_plan.json lineage.json system_result.json`; `attest-artifacts ROOT manifest.json` checks that referenced output files exist and their actual bytes match SHA-256.

## Lineage and anti-drift handoff after each cycle

Mandatory packet: current approved research folder/IDs (private on Drive), pinned raw hashes, normalized timestamp profile, baseline and candidate code commits, full system compositions, experiment ID and frozen plan digest, monthly checkpoints and trade ledgers, matched broker/capital/latency scenario vectors, all weak months, root cause of failure, additive/ablation outcomes, decision and next build action, rollback branch, file SHA-256 receipts. A missing element remains **UNKNOWN**, not assumed successful.

**Scope:** New independent XAUUSD HTF EA; R9 remains a pinned diagnostic research reference, not this product. All investor criteria remain subject to versioned approval.
