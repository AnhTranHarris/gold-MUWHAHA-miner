# HTF EA governance v1.1 — Resumption and next-build ledger

**Status:** Source-locked, UTC-corrected two-broker single-position Python replay exists. The v1.1 add-on is metadata lineage, integrated-system comparison and verified-file checks; **it does not yet construct a multi-strategy EA or make the existing replay account share broker margin across simultaneous signal programs**. No investor-certified strategy exists.

## Immutable authority
- User's explicitly supplied Coinexx Jan–Sep/Dukascopy Jan–Jul and pinned R9 research specimen; official MetaQuotes only for platform semantics.
- v1.0 anti-drift governance, current explicit Dukascopy source supersession, investor mandate v1.0.
- Verified v0.3 UTC-corrected backtest rollback: `ca4b58aec597174b6f6d18ab2f36cba6836e4f4c`.
- Governance v1.0 release commit: `46140d6be484f5bc87159bbe865eef31cf2fe3fb`.
- This v1.1 release commit: see `GOVERNANCE_V1.1_DEPLOYMENT_RECEIPT.md` in canonical Drive; never guess it from a filename.

## Mandatory first checks for a new conversation
1. Read the exact source-supersession record; do not revert to the older Dukascopy exclusion.
2. Read investor mandate, v1.0 charter and the v1.1 whole-system charter.
3. Verify GitHub branch HEAD; read SHA-256-pinned source registry and UTC clock module.
4. Run the regression tests and both example validation commands; do not mistake the example for validated performance.
5. Read the latest experiment handoff and result artifact hashes; do not repeat completed work or treat a chat timeout as research loss.
6. State any unknowns, blockers and the smallest safe next build action. No outside project/branch research is authorized.

## First next build (not yet implemented)
Develop a causally replayed **multi-signal strategy bus / central broker-execution arbitrator** that merges independent expert signals into one chronological position/margin/cash/equity account. Features: strategy ID, order-intent arbitration, group risk and capital headroom, deterministic priority at equal timestamps, netting/hedging choice pinned per broker scenario, slippage/latency/backlog, protective stop priority, and a full-account trade/equity ledger. Compare S vs S+C on the same Coinexx and Dukascopy sources, independent account per scenario. Existing single-position no-trade baseline must remain unchanged, and no trading strategy is certified merely by wiring the bus.

## Release verification boundary
The v1.1 module enforces configuration/provenance gates and validates SHA-256-shaped receipts. Its `attest-artifacts` command independently checks actual local output-file bytes when invoked. It **cannot** independently infer real transaction P&L, prevent arbitrary bypass of the low-level CLI, prove an EA binary implements the declared components, or grant investor approval. Achieving those requires a future trusted scored-launcher integration and full-account ledger replay checker. These are explicit pending tasks, not silent passes.
