# GAMMA-02 — London + NY Hourly Conviction 002

**Status:** MAJOR JANUARY DISCOVERY FRONTIER — RECONSTRUCTED AND PARITY VERIFIED AFTER TIMEOUT  
**Predecessor:** GAMMA_02_LONDON_NY_INTEGRATED_PORTFOLIO_001.md  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## What changed

The grouped London/overlap conviction thresholds were replaced with per-hour causal favorable-M1-displacement gates while the previously earned NY time-decay engine remained unchanged.

Hour thresholds:
- 07 UTC: $1.00
- 08 UTC: $3.00
- 09 UTC: $0.00
- 11 UTC: $2.00
- 12 UTC: $0.00
- 13 UTC: $4.00
- 14 UTC: $4.00
- 15 UTC: $3.00

NY remains:
- 16 UTC minimum favorable displacement $0.50;
- 17 UTC time-decay map `lateBias`;
- 18 UTC time-decay map `lateClean`.

Every threshold is based only on favorable M1 displacement already realized at entry.

## Parity recovery

After a ChatGPT delivery timeout, this helper was reconstructed from the prior durable integrated helper and replayed independently.

Cap 128 reproduced exactly:
- **+$102,623.09**
- **16,299 trades**
- **PF 4.7680978545**
- **+$6.296281/trade**
- realized balance DD **$2,017.55**

Therefore the pre-timeout result is recovered rather than inferred from chat memory.

## Full January cap frontier

| Cap | Net | Trades | PF | Expectancy | Realized balance DD |
|---:|---:|---:|---:|---:|---:|
| 32 | +$24,505.26 | 5,320 | 3.1736 | +$4.606 | $934.37 |
| 64 | **+$50,670.39** | **9,498** | **3.7568** | **+$5.335** | $1,496.09 |
| 96 | +$77,048.91 | 13,137 | 4.3624 | +$5.865 | $1,734.41 |
| 128 | **+$102,623.09** | **16,299** | **4.7681** | **+$6.296** | $2,017.55 |
| 160 | +$123,997.28 | 19,174 | 4.9205 | +$6.467 | $2,980.99 |
| 192 | +$143,379.02 | 21,738 | 5.0553 | +$6.596 | $3,685.07 |
| 256 | **+$178,616.58** | **25,705** | **5.0973** | **+$6.949** | $5,667.30 |
| 384 | **+$235,099.81** | **32,010** | 5.0550 | **+$7.345** | $7,509.64 |
| 512 | **+$284,779.60** | **36,486** | **5.1840** | **+$7.805** | $8,614.31 |

High caps are deliberate research heat frontiers, not deployment recommendations.

## Cap-128 source economics

- 07 UTC: +$458.87 / 229 trades / +$2.004 expectancy
- 08 UTC: +$2,572.55 / 503 / +$5.114
- 09 UTC: +$4,313.57 / 2,066 / +$2.088
- 11 UTC: +$7,547.77 / 1,145 / +$6.592
- 12 UTC: +$12,216.12 / 3,400 / +$3.593
- 13 UTC: +$6,313.24 / 585 / +$10.792
- 14 UTC: +$3,087.70 / 732 / +$4.218
- 15 UTC: +$11,387.84 / 1,945 / +$5.855
- 16 UTC: +$15,379.96 / 1,297 / +$11.858
- 17 UTC: +$28,593.00 / 570 / +$50.163
- 18 UTC: +$10,752.47 / 3,827 / +$2.810

## Scientific interpretation

This improves the cap-128 integrated London+NY parent from +$96,827.41 to **+$102,623.09** while reducing realized balance DD from ~$3,522.88 to ~$2,017.55 and slightly reducing trade count.

The next problem is not raw opportunity supply. It is **capacity allocation**: low-expectancy dense sources can consume global slots that later high-expectancy sources need.

Required next work:
1. source-slot reservation / conviction auction without forced closing of profitable active tickets;
2. London 11/12/15 subphase/lifecycle refinement analogous to NY17;
3. full tick-level equity-DD replay for finalists;
4. chronological Jan-Jul validation only after January freezes.

## Exact durability

Helper SHA-256:
`ed295208316732acb6e208562f7e0ae4c27278680370f5335fab7e3ca698a8a5`

Cap-128 parity JSON SHA-256:
`a90d47d3502d6880b724739dffece2b8981007aa3bff40af77140ec57ab47631`

Persistent Library:
`/xauusd-trading-bot/r9-gamma-02-velocity-geometry/2026-10-07/m1-density/`
