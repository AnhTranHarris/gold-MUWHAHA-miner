# GRID-001 January Volatility-Expansion Route 001

**Status:** COMPLETE / JANUARY CANDIDATE ROUTE

Formal re-test used the current A05 adaptive lattice, completed-M1 ATR14/ATR240 expansion state, one-gap continuation proof within 3 seconds, 1.5-gap target, original-event-midpoint stop, original five-minute horizon, fixed 0.01, and one physical owner.

Expansion >= 1.75: **215 trades, +$135.59, PF 1.2064**; discovery **+$7.27 / PF 1.1681**; validation **+$128.32 / PF 1.2091**; max equity DD **$58.37**.

Expansion >= 2.00: **155 trades, +$146.11, PF 1.3039**; discovery **+$16.07 / PF 1.8672**; validation **+$130.04 / PF 1.2814**; max equity DD **$40.13**.

Both variants remain positive on the theoretical $100/$200/$300 equity diagnostic. Discovery samples are small, so this is not proof of a finished edge.

**Decision:** promote to the January candidate pool as a sparse high-confidence expansion-continuation route. It is too slow to bridge the R9 SYNTH gap alone and must be combined with higher-throughput routes later. No further threshold tuning is authorized before broader month validation.

August sealed. Main `delta` read-only. MQL5 unauthorized.
