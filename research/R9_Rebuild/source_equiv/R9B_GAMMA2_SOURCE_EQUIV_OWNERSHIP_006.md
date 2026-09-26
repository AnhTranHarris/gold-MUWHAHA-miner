# R9B_GAMMA2_SOURCE_EQUIV_OWNERSHIP_006

January-only exact source-equivalence diagnostic.

Reconstructed the certified R8 MQL5 chronological ownership semantics rather than generating detached sweep events:
- one live R8 position owns the interval;
- CONT and SWEEP share the same per-minute quota;
- signal processing is suspended while a position is live;
- state resets after closure;
- cooldown begins after closure;
- R8 lifecycle is stop $3.00 / activation $0.18 / trail $0.05 / max hold 60s;
- only sweep entries actually observable under full R8 occupancy are retained;
- the frozen Gamma_2 five-scale structure lifecycle is then applied to that sweep population.

Authoritative frozen midpoint arithmetic was preserved as separate ask_raw/1000 and bid_raw/1000 reductions followed by midpoint averaging. A mathematically equivalent raw-sum/2000 expression was rejected because floating-point ordering changed a small number of threshold events.

Result:
- full R8 January entries: 55,391
- CONT entries: 39,176
- causally observable SWEEP entries: 16,215
- Gamma_2 lifecycle on those sweeps: 16,215 trades / 11,074 winners / 68.295% wins / -$2,590.27 net / -$7,109.23 GL / PF 0.6356 / max DD $2,595.00
- certified Gamma_2 January target remains 30,943 trades / 25,368 winners / 81.983% wins / +$5,131.05 net / -$6,091.21 GL

Conclusion: full original-R8 position ownership over-suppresses the sweep population and does not recover certified Gamma_2. The missing helper semantics are therefore neither simple CONT quota/cooldown, the frozen alignment cache, nor full original-R8 occupancy.

Source SHA-256: 63ceb8a782a642b238ea8a1c00cd455b85b27f534046fc125e8ead5c8cab0aa6
Result SHA-256: e833a930612135d0028e88a40700410e85ec2931147561cff16960577aa60e20

August remains sealed.
