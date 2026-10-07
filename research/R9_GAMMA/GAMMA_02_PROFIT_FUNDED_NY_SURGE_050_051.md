# GAMMA-02 — Profit-Funded NY Surge 050/051

**Status:** MAJOR JANUARY EXPOSURE-FINANCING BREAKTHROUGH / FULL-TICK EQUITY CERTIFIED  
**Parent:** GAMMA_02_QUALITY_CORE_CROSSOVER_EQUITY_048.md  
**August:** SEALED

## Causal capacity rule

Keep the ordinary cumulative funded base:
- start cap 64
- +64 slots per $2,500 already-realized net
- base ceiling 256

NY16/17 receive temporary campaign capacity, but the majority of that extra capacity is itself unlocked only from already-realized cumulative profit.

No lot escalation. Every ticket remains 0.01.

## Best tested expanded funded-surge point

- heartbeat: 120 ms, NY16/17 only
- initial surge: 512 slots
- then +256 surge slots per $1,000 realized net
- maximum surge: 3,328
- hard NY research ceiling: 3,584

Unlock chronology:
- first qualified campaign activity: allowed ~576
- Jan 20: ~1,984
- Jan 21: ~3,328
- Jan 26: full 3,584

January closed trades:
- **+$974,669.38**
- **29,863 trades**
- **PF 45.2172**
- **90.0311% wins**
- **+$32.6380 expectancy/trade**

This exceeds exact January R9 SYNTH on net, trade count, PF, win rate, and expectancy while avoiding an extreme full-cap grant at the beginning of January.

## Full ordered-tick equity certification

P/L reconstruction error: 0.0

- equity DD: **$242,617.46**
- equity DD ~22.29% of peak total equity
- minimum total equity from $100K start: **$90,045.26**
- max open: 3,584
- average hold: **1,250.43 s**
- median hold: **1,200.07 s**
- p90 hold: ~1,800.05 s

Disposition:
- **KEEP** as exposure-financing/profit ceiling evidence.
- **DO NOT** treat as final R9-SYNTH-like lifecycle architecture.
- Remaining problem is floating heat + 20-30 minute lifecycle.

## Next atomic unit

`GAMMA_02_CAMPAIGN_BASKET_HARVEST_052`

Test campaign-level profit harvesting/recycling rather than small individual TPs:
- structural state ownership unchanged;
- aggregate basket profit is evaluated causally at executable Bid/Ask;
- basket may realize together when per-ticket floating profit threshold is reached;
- re-entry only on subsequent qualified market ticks;
- goal is shorter lifecycle and lower floating heat without destroying the 16/17 quality edge.

Exact 049-051 helpers/results are durable in persistent Library.
