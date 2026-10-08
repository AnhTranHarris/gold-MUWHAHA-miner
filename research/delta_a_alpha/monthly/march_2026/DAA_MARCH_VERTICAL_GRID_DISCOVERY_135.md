# Delta-A-alpha — March 2026 Vertical Grid System Discovery 135

**Status:** COMPLETE MAJOR MARCH DISCOVERY  
**Market:** XAUUSD Dukascopy March 2026 ordered ticks  
**Raw SHA-256:** `814ba35e72f219a58badd806ed5c0f30ef0fb4ffe56a48205d873706513bd177`  
**August:** SEALED

## Permanent architecture

The March work preserves the whitepaper spine unchanged:

**ordered ticks → session-specific grid geometry → completed H4/H1/M15/M5 structure → London/overlap/NY hourly high-volume harvesting + separate Asia geometry → Watchdog/regime renewal → trend-within-trend native routing → wrong-direction recovery → portfolio heat/capital governor**

The month is a discovery/evaluation partition only. Calendar month/date is not a deployable strategy feature.

## Timeout recovery and runtime hardening

The timed-out research block had no finished result. Two partial helpers survived, but the expensive parent path repeatedly rebuilt warmup ticks and four timeframe states. March was therefore restarted only from the smallest missing atomic block.

The runtime was hardened by building one reusable surface:

- 1,968,158 warmup ticks from 2026-02-19 onward;
- 9,433,179 March ticks;
- 11,401,337 total ordered cached ticks;
- one normalized executable Bid/Ask surface;
- one continuous completed EMA8/EMA21 H4/H1/M15/M5 state cache.

Every subsequent March layer reused those bytes instead of decompressing/rebuilding the month.

## March R9 SYNTH benchmark

- net **$75,698.63**
- trades **40,985**
- gross loss **$-2,024.86**
- PF **38.3846**
- win **90.01%**
- expectancy **$1.85/trade**
- closed-trade balance DD **$2.62**

## Recovered March layer engines

| Layer | Net | Trades | Gross loss | PF | Win | Expectancy |
|---|---:|---:|---:|---:|---:|---:|
| Native PF10 | $67,574.54 | 6,746 | $-4,399.88 | 16.36 | 85.93% | $10.02 |
| Native cell PF15 | $43,407.34 | 4,032 | $-1,270.11 | 35.18 | 88.39% | $10.77 |
| Native cell PF30 | $22,615.82 | 2,029 | $-164.84 | 138.20 | 94.18% | $11.15 |
| High-volume broad | $77,965.73 | 11,573 | $-6,859.37 | 12.37 | 81.44% | $6.74 |
| High-volume PF20 | $37,621.47 | 3,450 | $-451.85 | 84.26 | 93.48% | $10.90 |
| Asia broad | $17,839.87 | 3,076 | $-2,456.09 | 8.26 | 73.54% | $5.80 |
| Asia PF20 | $9,544.57 | 597 | $-18.43 | 518.88 | 96.65% | $15.99 |
| Watchdog quality | $8,983.90 | 5,545 | $-50.24 | 179.82 | 99.87% | $1.62 |
| Recovery | $3,154.72 | 839 | $-532.08 | 6.93 | 85.22% | $3.76 |

## March portfolio frontiers

| Frontier | Global cap | Net | Trades | Gross loss | PF | Win | Expectancy | Balance DD | Full-tick equity DD | Positive days | Weeks beating SYNTH |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Profit | 600 | $203,212.88 | 29,969 | $-14,491.24 | 15.02 | 86.05% | $6.78 | $800.06 | $8,280.96 | 21/22 | 5/5 |
| Balanced | 448 | $173,381.19 | 22,224 | $-7,332.85 | 24.64 | 90.83% | $7.80 | $800.06 | $8,171.52 | 21/22 | 5/5 |
| Quality | 448 | $125,792.74 | 15,988 | $-1,994.07 | 64.08 | 94.41% | $7.87 | $240.93 | $8,171.52 | 22/22 | 4/5 |
| Ultra | 448 | $105,083.99 | 14,040 | $-897.07 | 118.14 | 96.02% | $7.48 | $121.57 | $8,171.52 | 22/22 | 4/5 |
| Cap92 | 92 | $76,996.60 | 9,543 | $-1,387.01 | 56.51 | 92.90% | $8.07 | $121.57 | $3,088.37 | 22/22 | 2/5 |

### Profit frontier

The broad vertical machine at cap600 reaches **$203,212.88**, or **2.68× March R9 SYNTH net**, with 29,969 trades. It is profitable on 21/22 SYNTH trading days and beats SYNTH in all five weeks. Its weakness is risk/quality: gross loss is **7.16×** SYNTH and full-tick equity DD is $8,280.96.

### Quality frontier — strongest scientific result

The PF15-native / PF20 high-volume / PF20 Asia stack at cap448 reaches:

- **$125,792.74** = **1.66× SYNTH net**
- **15,988 trades**
- gross loss **$-1,994.07**, slightly **better** than SYNTH $-2,024.86
- PF **64.08** vs SYNTH 38.38
- win **94.41%** vs SYNTH 90.01%
- expectancy **$7.87**, **4.26× SYNTH**
- **22/22 positive SYNTH trading days**
- **5/5 positive weeks; 4/5 beat SYNTH**

The remaining deficits are velocity and drawdown: only 39.0% of SYNTH trade count, balance DD $240.93, and full-tick equity DD $8,171.52.

### Low-cap frontier

The smallest tested four-step cap that still clears March R9 SYNTH net is **cap92**:

- net **$76,996.60**
- trades **9,543**
- gross loss **$-1,387.01** — 31.5% lower than SYNTH
- PF **56.51**
- win **92.90%**
- expectancy **$8.07**
- full-tick equity DD **$3,088.37**
- max open **92**
- 22/22 positive SYNTH trading days

This is important for eventual arbitrary-start/small-capital work: March does not require a 448–600 inventory ceiling merely to exceed SYNTH monthly net.

## March behavior learned by the spine

1. **March native continuation is real and large.** The March-native PF10 specialist remains a core engine.
2. **Hourly reset geometry is the second major March engine.** London/overlap/NY cannot be reduced to a static session grid; fresh hourly ownership recovers a large volume of high-quality opportunity.
3. **Asia is different.** Broad Asia is useful, but PF20 causal state/subphase filtering creates an exceptionally clean sleeve.
4. **Watchdog is useful as a renewal layer, not the whole strategy.** March quality Watchdog cells are near-lossless but lower expectancy per ticket.
5. **Recovery must remain state-conditioned.** Opposite-direction recovery adds a modest positive sleeve only after observed adverse behavior and causal-state qualification.
6. **Heat is the remaining engineering problem.** High monthly capture is easy to buy with large concurrency; the scientifically important frontier is the one that keeps net above SYNTH while lowering gross loss and inventory.

## Scientific boundary

These rule keys are causal and calendar-blind, but their cell/config selections were discovered using March outcomes. They are **March discovery evidence, not deployment authority**. April–July must show which mechanics generalize and which need online market-state adaptation.

The eventual EA must not contain `if month == March`. It should observe the same causal state variables—session, hour/subphase, completed H4/H1/M15/M5, activity, realized displacement/failed ignition, renewal state, and current heat—and route accordingly.

## Recovery artifacts

Use the companion machine files rather than reconstructing from chat:

- `DAA_MARCH_VERTICAL_GRID_DISCOVERY_135.json`
- `DAA_MARCH_VERTICAL_GRID_CELLS_135.json`
- `DAA_MARCH_VERTICAL_GRID_STREAMS_135.npz`
- `daa_march_vertical_grid_replay_135.py`

Next research month: **April**, from the same frozen whitepaper spine.