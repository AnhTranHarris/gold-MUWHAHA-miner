# F401-R150 — native bid/ask unsubmitted-intent first-passage SHADOW

**2026-10-30 · research-only · unapproved.** Additive successor to R149, with frozen R148B/R24 parent unchanged. Original M-DK-01 remains OPEN, 21/39 owner historical research-stage approvals unchanged, G01–G09 OPEN. No order sent, no native MT5 parity, no /02 promotion.

## Three independent hypotheses

1. **Competing favorable/adverse-first bid/ask passage** for genuinely NEW never-submitted limit intents: IMPLEMENTED in `r150_native_intent_first_passage.py`, 19/19 deterministic tests pass. Strict first native quote in [t0+15s,t0+16s), strictly prior R120/R147/R149 published state, completed micro/HTF/session geometry, buy ask / sell bid entry touch, buy bid / sell ask exit, fees, latency and 30s NEW action-time outcomes. Never reuse original t0+30..32 truth as a new entry outcome.
2. **Sequential value-of-information optimal stopping:** designed, not trained or tested; compare act-now versus wait using new native quotes and economic labels.
3. **Independent correct guardian / regime-conditioned action router:** designed, not trained or tested; preserve frozen parent veto until genuine forward validation.

## Verified source continuity

Original R149 archive SHA256 `91a219e7cd159a86fd25aa68afa5275c156fa0b8f898209a65000359ca389920`, 129 members and ZIP CRC passed. Eight original R149 source receipts reconcile 2,574,251 immutable events, 2,342,805 valid historical hypothetical t0+15 first-quote decisions, and four frozen R149 July masks loaded and recounted. This is **archive continuity**, not a fresh eight-month raw tick replay. Registered raw tapes were not available in this execution container.

Exact local R150 source SHA256 `37aa4839fa750baa83755fe5e21dd6d67591bedb0cdcb96aa124173486302f9b`. Exact local R150 tests SHA256 `b91e1bff7bac725d7c7a8711b79e20f09178e4f8785c94425d974d10e5f3bb33`. GitHub files are intended to be byte-exact copies; fetch/readback is mandatory. Complete nine-member local source/test/receipt archive SHA256 `e135f4e81ea6c5627d3298f8a7693f9cc21599a6bffa5525ac46d93a41877cb9`, CRC/member hashes passed.

**Result:** 19/19 synthetic deterministic tests passed. Twelve 2-broker × 2-balance × 3-latency synthetic fixtures executed; NOT real account/economic G09 testing. No new original wrong-veto, correct-loss, 4178 quota, or real execution performance measured. FILTER05 QUOTE_ORDER and authentic R9 pre-OrderSend intent IDs remain missing. R149 telemetry-only and R148B parent unchanged.

Next: run this module on registered raw Coinexx/Dukascopy source tapes with a **genuinely new unsubmitted intent** and source-authentic quote sequence; obtain separately matured action-time economic labels. Keep original event identities and R9 quotas independent, and evaluate a truly untouched future stream before any promotion.

Research evidence: [MT5_EXPAND /00 R150](https://docs.google.com/document/d/1gOgVUiw63anM25OG3enLgwOcZWmB0mwbJFVrkuOPtG0/edit), [MT5_EXPAND /01 R150](https://docs.google.com/document/d/1j6gD5PKkPpxOCUiMAl7e3GL109nh6oB0JJbbqKQ1Rt4/edit).