# V11 — SHA-verified January real-Coinexx bounded forensic receipt

**2026-11-15. In-sample preliminary diagnostic only. NOT nine-month V11
replay, NOT OOS predictive validation, NOT native MQL5 parity.**

Original broker archive:
`XAUUSD_MT5_BROKER_2026_01_ticks_ALL.csv.gz`.
Entire compressed-source SHA-256 verified against frozen V9 historical receipt:
`1307a75df5d635678de7691908600090a552f38543e0512187dcd7b37fbc66b8`.

**Exact original quote prefix used: 200,000 / 7,699,274 January records.**
Original source row order preserved; no resampling/re-downloading/rebuilding.

Baseline execution invariants:
- V9/V10/V11 **906 exact same entries and 905 exact completed trade
  event tuples**, including original source ordinals, entry/exit prices, side,
  reason and open-position state. Final original trade remains open at the
  artificial 200,000-record boundary.
- Original V10 specialist `UNRESOLVED`: **414 / 906 (45.70%)**.
- New V11 unresolved evidence reason total: **exactly 414**.
- No PnL objective or trading parameters were changed.

| Reason within the *original V10 router fallback* | Entries |
|---|---:|
| CHANGE_ALARM_NO_CONFIRMED_THESIS | 115 |
| ENTRY_SIDE_OPPOSES_CONFIRMED_TREND | 84 |
| NESTED_STRUCTURE_SIDE_MISMATCH | 45 |
| STRUCTURAL_EVENT_SIDE_MISMATCH | 19 |
| REVERSAL_CANDIDATE_NOT_CONFIRMED | 8 |
| MIXED_STRUCTURE_INSUFFICIENT | 107 |
| MICRO_PULLBACK_OR_PAUSE | 14 |
| MICRO_EXPANSION_PARENT_BALANCED | 9 |
| CROSS_SCALE_ROTATION_CANDIDATE | 9 |
| CROSS_SCALE_CONFLICT | 3 |
| UNCONFIRMED_ALIGNED_IMPULSE | 1 |
| **Total old unresolved** | **414** |

**Interpretation:** 271 / 414 have a recognisable *causal event or
direction/side disagreement* behind the original fallback, even where the
observed event did not qualify for a named original specialist. This is not
a claim that those 271 are safe to trade or accurately predict a future
pattern. The router simply lacked appropriate distinct attribution.

Persistent zone bank after source prefix:
- M5: 12 / 12 slots; 34 created, 22 locally evicted, 17 merged.
- M15: 12 / 12 slots; 12 created, 6 merged.
- H1 and H4: **zero active** in this limited initial source prefix;
  do NOT claim higher-timeframe persistence has been empirically certified
  across complete trading sessions.
- Micro pivots cannot consume protected M5/M15/H1/H4 budgets.

Frozen protection reference (research ONLY):
- **275 / 906** actual entries had a valid entry-side support/resistance
  zone within the explicitly bounded reference distance.
- **631 / 906** had no eligible structural zone; they were marked
  `NO_VALID_STRUCTURAL_STOP` rather than given a fabricated wrong-side
  reference. This is a structural coverage deficit, not a trading risk
  override.
- Confirmed structural invalidation did NOT occur in this short prefix;
  old V10's large invalidation counter must not be compared as though
  both represented actual positions closed.
- Existing broker stops remained authoritative and unchanged.

Causal validation:
- Two completed, consecutive observed 1-second liquidation quote closes,
  supporting midquote movement and limited spread stress are required.
- Source timestamp discontinuities reset candidate confirmations.
- Equal-millisecond ticks cannot substitute for distinct completed seconds.
- All evaluated V11 proposals are read-only; no broker orders or account
  risk parameters changed.

Runtime for the verified 200k triple comparison: **16.16 seconds**,
peak process RSS **~106 MB** in the local Python environment.
This is not a full nine-month throughput benchmark.

**Next gate:** a complete pinned 9-month V11 attribution with monthly warm-up
accounted for, *after* stable tests, plus independent, time-frozen pattern
evaluation, side-specific first-passage analysis, and native MT5 source-clock
parity. Do not promote any V11 recommendation into an order or exit.

Institutional/quant/community rationale and code contracts:
`V11_CAUSAL_STRUCTURE_REFINEMENT_20261115.md`.
