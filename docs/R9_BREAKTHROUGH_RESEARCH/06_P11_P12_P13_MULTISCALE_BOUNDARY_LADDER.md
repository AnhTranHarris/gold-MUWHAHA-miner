# 06 — P11/P12/P13 Multiscale Boundary Auction Ladder

**Status:** research architecture reconstructed from project evidence.

## Discovery

The sweep/reclaim and acceptance phenomena reproduced beyond one minute.

- P11: ~3-minute acceptance desk, ≈ +$24,090 / 80,463 trades / 7 positive months.
- P12: ~3-minute sweep/reclaim, ≈ +$19,395 / 53,854 trades / 7 positive months; rolling May/Jun/Jul all positive.
- Later research propagated the same family to 1m, 3m, 5m, 10m and 20m.

## P13 hierarchy

- 1m: frequency engine / auction discovery
- 3m and 5m: intermediate structural states
- 10m and 20m: lower-frequency, higher-expectancy boundary states
- H1/H4 P5: separate structural persistence sleeve

Each scale independently classifies:
- ACCEPT
- SWEEP/RECLAIM
- NO-TRADE

Then an action layer selects:
- CONTINUE
- FADE
- ABSTAIN

## Agreement rule

Agreement across scales is a **priority modifier**, not a hard vote. The 10m+20m same-direction agreement state raised expectancy, but killing unconfirmed lower-scale trades destroyed too much profitable activity.

## Causality

All scale boundaries and confirmation states must derive from completed observations only.
