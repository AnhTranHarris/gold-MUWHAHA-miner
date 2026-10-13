# GRID0265 — Actual Python implementation integration, not a detached ZIP

**Branch:** `delta-A-alpha`; active Python source modified IN PLACE in `research/delta_a_alpha/implementation/`. **Trading remains OFF**, official J0183 unchanged, August sealed. No MT5 EA conversion or live execution was attempted.

## Current-code re-audit: finding and resolution

Prior audit package 0264 was stale relative to actual GitHub implementation: GitHub already has the **current GRID0264 cumulative G0 adapter** wired to `FourSessionV1.creator_genesis`. Do **not** replace it with the 0257 archive. Confirmed source chain is:

`v1_vertical_grid.CleanV1Engine` → current `CumulativeCreatorAdapter` → current `GridStrategySourceRouter` → completed M1/H4 and other finished H4/H1/M15/M5 G0 evidence → L1–L7 quality path → latency-gated shadow quote book.

What was *not* actually wired in the active Python implementation was hardened broker transaction evidence into the **same** cumulative G0 parent credit identity. The historical GRID0264 ZIP contains a repaired transaction class but was NOT merged into the active implementation, and its older GRID0263 base lacked individual `deal_evidence` retention required by the current `GridSourceBrokerAckBridge0264`. A local direct integration test first exposed that exact version conflict.

## Code FIXED in the ACTUAL implementation folder

1. **Installed** `v1_grid_mt5_transaction_contract_0264_repaired.py`: rejects invalid/terminal/cancelled broker order and position transitions, out-of-order deal events, entry phantom realized cash, invalid stop ACK or postclose modification.
2. **Installed** `v1_grid_broker_evidence_port_0265.py`: takes actual current cumulative adapter + hardened event contract, not recovered 0257 router; an external `BrokerOrder`, confirmed OrderCheck, OrderSend, `BrokerDeal` DEAL_ADD, stop ACK and closed position events are distinct; only evidence-complete paid 0.01 lots can reach `GridSourceBrokerAckBridge0264`. No Dukascopy quote becomes an alleged broker fill.
3. **MODIFIED `v1_four_session_architecture.py`**: constructs `self.broker_evidence=V1BrokerEvidencePort(self.creator_genesis)` (optional injectable hardened broker event contract for real-evidence research). `result()` displays separate broker-event account status; never adds shadow quote PnL to confirmed broker profit.
4. **MODIFIED `v1_four_session_architecture.py`** again: retains `paid_proposal_id` on Opportunity and `source_proposal_id` on simulated Position, preserving identity through latency/entry/exit, and keeps quote-only `realized_source_lineage` separate from verified DEAL_ADD. Missing source IDs are left None, not guessed.
5. **INSTALLED** `test_v1_grid_broker_evidence_port_0265.py` (11 tests including current actual FourSessionV1 object).
6. **MODIFIED** `test_v1_four_session.py` with two direct engine-wiring, quote-to-source-provenance and separation-of-broker-cash cases.

## Verification evidence and limits

- Local ZIP-based recovered dependency suite plus exact new broker-evidence port tests passed: **255 tests, 1 skipped**. To run the new port tests locally against the newer current broker contract, the older archive copy of `v1_grid_mt5_transaction_contract_0263.py` was updated **locally only** with `deal_evidence` recording already present in GitHub current source. That mismatch is why using old ZIPs alone was unsafe.
- **All five modified/new GitHub implementation/test files were fetched and verified** on the current `delta-A-alpha` branch after commits.
- The **full up-to-date current repository suite, including the two new FourSessionV1 integration tests, has not been executed on a cloned current branch** because GitHub network checkout is unavailable in the local runner. Do **not** represent 255 inherited/local tests as entire up-to-date repository certification. The new tests are committed for the next repository-runtime execution.
- The verified external MT5 evidence remains missing: Coinexx contract, verified margin/tick/fee server clock, real order ACK/fill/SLTP notifications. The interface defaults UNKNOWN/False and fails closed. This is **not proof of EA parity**; it is removal of the software gap between current source logic and broker-evidence ledger.
- All existing GRID0258 original source research controls preserved; no science advancement, no R9 SYNTH performance promotion.

## Next actual engineering gate before renewed trading research

Run the complete `implementation/test_*.py` suite on this exact branch checkout; perform bounded raw Jan–Jul *full-tick* replay through `FourSessionV1` and the new evidence port, with explicit hypothetical permission and a separate real-deal ledger; validate all source-to-trade ancestry and source ACKs (including earned GRID0258 child propagation) in one book. Then obtain real Coinexx observed metadata for strict MT5 equivalence. No broker facts, missing strategy source or winning edges can be fabricated.

**Recovery:** Current GitHub implementation folder is authoritative; old GRID0262–0264 ZIP files are regression dependencies only, not a substitute for updated live source.
