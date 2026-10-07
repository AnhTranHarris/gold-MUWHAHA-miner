# GAMMA-02 — Selective Rebreak Latency 017

**Status:** COMPLETE JANUARY DISCOVERY REFINEMENT  
**Parent:** GAMMA_02_SELECTIVE_UNIQUE_TICK_REBREAK_016.md  
**Opportunity counting:** max one new ticket per source per market tick  
**August:** SEALED

The selective pullback/reclaim/re-break engine was given a causal minimum elapsed-time requirement between the first qualifying pullback and the reclaim of the prior favorable extreme.

Cap 128, reset $0.10:

| Minimum pullback-to-reclaim time | Net | Trades | PF | Exp/trade |
|---:|---:|---:|---:|---:|
| 0 ms | +$80,358.08 | 10,749 | 5.3690 | +$7.4759 |
| 250 ms | +$80,683.93 | 10,732 | 5.4076 | +$7.5181 |
| **500 ms** | **+$80,822.30** | **10,710** | **5.4608** | **+$7.5464** |
| 1,000 ms | +$80,521.15 | 10,659 | 5.4460 | +$7.5543 |
| 2,000 ms | +$79,704.21 | 10,613 | 5.4279 | +$7.5101 |
| 5,000 ms | +$78,930.05 | 10,540 | 5.4048 | +$7.4886 |
| 10,000 ms | +$78,229.70 | 10,483 | 5.3937 | +$7.4625 |

The 500 ms rule is the net-maximizing result in this screen and improves both net and PF versus immediate reclaim.

Interpretation: immediate pullback/reclaim cycles contain some quote-level noise. Requiring the reset to survive for roughly half a second produces a cleaner auction reset without materially reducing chronological trade density.

Exact artifacts are persistent in Library:
- gamma02_rebreak_latency_017.py
- gamma02_rebreak_latency_017_cap128.json

Next: source-specific reset/latency, especially a deeper NY17 reset while preserving dense London re-arms.

No MQL5 build. No Jan-Jul promotion yet. R9 SYNTH remains the hard target.
