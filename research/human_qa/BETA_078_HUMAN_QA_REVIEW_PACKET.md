# BETA078 Human-Facing QA Review Packet — QA V2

Status: **HUMAN_QA_RESEARCH_CANDIDATE_NONBLIND**  
Engineering QA: **102/102 PASS**  
August: **SEALED**  
MQL5: **NOT AUTHORIZED**

## Frozen research candidate

**M5 FIRST_RETEST → level maturity 7–9 completed M5 bars → fixed 1800s hold.**

Jan–Jul nonblind research score: **420 trades, $509.21 net, PF 1.350, 48.3% win rate, $1.212/trade, max DD $99.70.**

One July trade is exact-flat in integer quote units; QA V2 classifies it as flat rather than allowing floating-point dust to change the win count.

## Monthly scorecard
- 2026-01: 61 trades, 27 wins, $111.46 net, PF 1.460, avg $1.827
- 2026-02: 55 trades, 28 wins, $177.20 net, PF 1.821, avg $3.222
- 2026-03: 69 trades, 38 wins, $114.44 net, PF 1.430, avg $1.659
- 2026-04: 53 trades, 27 wins, $81.04 net, PF 1.465, avg $1.529
- 2026-05: 66 trades, 26 wins, $-12.66 net, PF 0.938, avg $-0.192
- 2026-06: 46 trades, 25 wins, $54.80 net, PF 1.310, avg $1.191
- 2026-07: 70 trades, 32 wins, $-17.08 net, PF 0.902, avg $-0.244

## Neighbor support
- AGE_7_9 @ 1200s: 422 trades, $167.24, PF 1.120
- AGE_7_10 @ 1800s: 476 trades, $487.97, PF 1.289
- AGE_8_9 @ 1800s: 252 trades, $296.24, PF 1.317

## Engineering evidence

- Source identity: all seven canonical Jan–Jul gzip SHA-256 checks pass.
- Timing: entry is first source quote strictly after the completed retest event; exit is first source quote at/after 1800 seconds from actual entry.
- Execution: BUY Ask→Bid; SELL Bid→Ask; $0.02 round-trip fee.
- Ownership: one position globally; overlaps are blocked.
- Exact accounting: integer-mill quote arithmetic agrees with recorded P&L (max numerical representation error 8.73e-13 USD).
- Manual QA set: 50 cases across admitted trades, maturity rejects and ownership rejects.

## Interpretation boundary

This is **ready for human-facing engineering QA**, not independently validated alpha. The maturity/hold neighborhood was discovered on historically inspected Jan–Jul data. Human QA should verify causality, state transitions, execution accounting, ownership, explainability and reconstruction. **Do not open August during this review.** August remains the sealed blind gate to use only after the human QA disposition is recorded.