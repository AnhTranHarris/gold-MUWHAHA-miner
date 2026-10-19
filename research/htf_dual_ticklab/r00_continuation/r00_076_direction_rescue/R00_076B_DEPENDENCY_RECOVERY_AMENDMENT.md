# R00-076B dependency recovery: original R00-072 Jan-only evidence

**Status: targeted reproducibility recovery; not a new research hypothesis, no change to candidate policies or data.** Training completed January. February scoring stopped before outcomes because original R00-072 portable archive has `EPISODES_*_01.npz` only. Its own report identifies the R00-072 work as Jan-only partial. All 8 R00-070 structural quote-aligned caches ARE present, including original expert observations and exact source quote indices.

## Safe source reconstruction plan, pinned before resumed scoring
- Recover and execute the original R00-072 `r00_072_episode/src/episode_072.py` Numba `episodes(t,observed,maxage,cd)` function **unchanged**, extracted byte-for-byte from authorized source ZIP SHA256 `a27be6347b3cada464727cc57038d8fcc7450fc0d2da893fd556dd714f458a83`.
- Verify exact byte-equal Jan `emitted_side`, `expert_stage`, `expert_episode_id` arrays against the registered original Jan archive for each broker, using as inputs the original R00-070 published `expert_observed` and source timestamp indices.
- Only after pass, generate Feb/Jun/Jul arrays using that exact same original function and original R00-070 observations. Reuse protected original event `ts_ms`, `quote_index`, `y`, `reference_side` from established R00-076A source and original R00-068 reference. Verify event matching before use.
- Create append-only independent SHA-256 receipts for regenerated files. Never mislabel these recomputed Feb/June/July episode state files as originally archived R00-072 artifacts. They are **new R00-076B derivations using the original R00-072 code**.
- Resume the exact 14 already predeclared R00-076B policies, January models `H,L,F` fitted and frozen in this session. February freezes policy; June/July remain historically exposed.
- Do not change initial signal event generator, existing native bid/ask reader, the Coinexx UTC shifts, original source authorization or R9 benchmarks. No exit/P&L.

Recorded blocker is a missing derived Jan-only artifact, NOT evidence of a faulty research backtester. Re-running original approved deterministic specialist event-state function is appropriate targeted derivation, NOT engine rebuild.
