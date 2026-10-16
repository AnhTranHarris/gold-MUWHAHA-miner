# XAUUSD HTF EA — Cross-Cutting Anti-Amnesia and Evidence Preservation Law v1.2

**Policy:** `XAU-HTF-CONTINUITY/1.2` — additive to *all* existing governance laws and the investor mandate. Effective 2026-10-16. This is not a trading-system certification.

## Binding interpretation

User instructions take precedence when explicitly changed. Existing `XAU-HTF-SRC-002`, `XAU-HTF-INV-001 v1.0`, `XAU-HTF-GOV-001/1.0` and `XAU-HTF-SYSTEM/1.1` remain in force. This law **strengthens** their evidence- and process-continuity requirements; it does not overwrite the earlier documents or reinterpret investor success.

## Law 1 — No self-summary as an authority or self-direction mechanism

An assistant-authored summary, brief, paraphrase, recap, chat-memory inference, or compressed handoff **must not** substitute for the original data, source code, raw experiment plan, numeric results, evaluation matrices, trade ledgers, decision records, or the complete analytic methods used to generate the research. Never reconstitute missing numbers or methodology by guessing from a summary. Assistant summaries may appear only as **navigational indexes**, with a pointer to the intact source artifact and a verifiable digest for each material claim. The assistant must not make new strategic decisions from such summaries alone.

## Law 2 — Preserve original artifacts, not just prose

A completed research cycle must retain frozen inputs and source hashes, exact code/version, full parameter configurations, time/UTC rules, original output matrices and negative periods, code for derived transformations, completed results, risk/fee assumptions, rejected trades, timestamps and chronology, lineage graph, exact decision history, and the next in-progress action. Large raw tick sources may remain in their authorized Drive locations rather than be copied. Handoff entries cite immutable source IDs, SHA-256, content paths and intended roles. A short description is never the only surviving research artifact.

## Law 3 — New conversation = continuation of the same research

New chat sessions do not start new investigations merely because the UI changed. Before choosing any research action, retrieve and inspect: (1) latest canonical START HERE and source supersession; (2) investor mandate and each active governance amendment; (3) exact authorized source manifest; (4) GitHub branch head and ancestry; (5) latest *full* experiment plan, results and lineage, not a synopsis; (6) completed/partial checkpoints and last journal event; (7) unsolved blocker and concrete next build action. Then continue the last verified in-progress research task. Repeating completed research, replacing it with a fresh unrelated plan, starting from `main`, or resetting results based on narrative is prohibited unless the user explicitly authorizes a new workstream.

## Law 4 — Fail-closed recovery instead of false continuation

If the artifact location is unavailable, its checksum disagrees, code branch ancestry differs, or the last experiment is unclear: label the state `BLOCKED_PENDING_RECOVERY`; identify exactly which source is missing; search only approved Drive/GitHub paths; verify the most recent complete checkpoint; do **not** fabricate a reconstruction, invent a missing test result, silently restart from the beginning, or substitute another project's data. If the user must supply a file or authorize a change, request only that missing item.

## Law 5 — Append-only decision lineage and supersession

Maintain a monotonically increasing hash-chained event journal for source approvals, frozen plans, source transformations, completed runs, tested decisions, build commits, and recovery. Publish the last event digest and exact count in the handoff and an independent Drive receipt. If a prior decision becomes outdated, append a **supersession** event referencing the old decision; do not delete or rewrite the original. A local hash chain detects accidental edits **only when its head is externally pinned**—it is not a cryptographic signature.

## Law 6 — Evidence reconciliation precedes interpretation

At new-chat bootstrap and after any timeout, independently check GitHub HEAD, approved source hash registry, complete evidence manifests, checkpoint hash, clock profile, full-portfolio evaluation context and next build action. Reconcile contradictions by returning to original sources, preserving both conflicting claims with provenance. The latest summary cannot overrule original source bytes. Record what was actually verified and what remains unknown.

## Law 7 — No branch drift or research fragmentation

Every development branch must descend from an authorized, explicitly verified project head and preserve rollback ancestry; this must be checked against **GitHub parentage** rather than accepted merely because an experiment JSON says so. `main` and unrelated branches are not default continuation choices. New chats must not create sibling projects to avoid a failing research result. A requested independent experiment requires explicit scope and lineage, while the main research continues.

## Law 8 — Whole-system evaluation stays binding

A subsystem or alternate mathematical indicator is research evidence, **never** the final unit of success. Promote only on paired complete-system assessments with a shared capital/margin/execution ledger, $100 and $200 survivability, both authorized brokers where required, execution latency, full hourly/daily/weekly/monthly interval reporting and recorded losses. Preserve negative evidence even when it lowers headline results. A failed individual candidate does not imply the portfolio system cannot succeed; a successful individual candidate does not certify it.

## Law 9 — Constructive research continuation

Every verified cycle concludes with a precise next experiment, a next code-build action, a falsifiable success and disconfirming criterion, a bounded repair attempt, an orthogonal path, a retirement rule and a stop condition. An inconclusive or negative test must preserve its evidence and present a safe testable remedy or justified retirement. No requirement to fabricate a positive result.

## Law 10 — Operational enforcement and limits

`htf_ticklab.continuity_guard` checks a handoff contract against an observed GitHub head (obtained via independent readback), original-artifact fingerprints (when local copies provided), required policy layers, current research state and chained journal. It rejects summary authority, fresh-research reset, missing lineage, and missing next actions. **The tool cannot read ChatGPT's hidden context, guarantee that the assistant processed each original artifact, cryptographically attest cloud content by itself, or automatically load all files in a future chat.** The operator must retrieve the Drive handoff and verify referenced artifacts. The current low-level backtest CLI can be run separately; unguarded outputs remain exploratory.

### Mandatory resumption outcome

Each new chat must state: `LAST_VERIFIED_HEAD`, `LAST_VERIFIED_EXPERIMENT`, `LAST_COMPLETE_CHECKPOINT`, `UNRESOLVED_BLOCKERS`, `NEXT_BUILD_ACTION`, `SOURCE_AUTHORIZATION_STATUS` and `VERIFIED_ARTIFACT_REFERENCES`, or fail closed. This is an exact provenance receipt, not a lossy summary of research.
