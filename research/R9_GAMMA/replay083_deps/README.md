# GAMMA-02 083 Replay Dependency Closure

This directory is the exact Python code closure required to replay the January 083/084 research checkpoints without depending on this chat's transient notebook state.

## Entry points

- `gamma02_dual_phase_renewal_quantum_083.py` — exact January all-metric crossover.
- `gamma02_083_heat_parent_ownership_084.py` — parent ownership / synchronized-child heat QA.

## Data requirement

The historical tick data are intentionally not stored in GitHub. The helper `stmr_janjul.py` expects the canonical Project/Dukascopy monthly files under `/mnt/data`, including January 2026. Those raw files remain external source data.

## Replay

Put this directory on `PYTHONPATH` (or run from it) with the canonical Dukascopy files mounted under the paths encoded in `stmr_janjul.py`.

The exact January 083 result must reproduce:

- +$76,586.24
- 49,466 child tickets
- PF 30,758.5261044
- 99.9353091% wins
- +$1.548260219/trade
- 12.295035s average hold
- full-tick equity DD $19,371.52
- max open 1,443

084 must reproduce the ownership finding that parents are unique but ~97% of child tickets fall into same-market-tick clusters across overlapping parents.

## SHA-256 manifest

```text
3ddb58c2096cf33ffc092335cfae8bc3ee78d828901423f1466f3024593016d4  gamma02_campaign_heartbeat_019.py
8bb8fd7c69e79f1232ec8257a64b2b30d4d32670ed92c43b5fa311e909acd7d1  gamma02_hour_specific_heartbeat_022.py
a7e9e699f10c075f957634f6e052c6bf4471dfec2d55b84e598f96fff46f8b53  gamma02_intrinsic_cusum_pulse_024.py
ed295208316732acb6e208562f7e0ae4c27278680370f5335fab7e3ca698a8a5  gamma02_london_ny_hourly_conviction_002.py
a237386cf53cf8aad8abd2f63040a7277a7ca1184e7a5c702da84e6b1b21a414  gamma02_london_overlap_markout_stream_001.py
a772ddd8ee71c64f826b8db045ed3190511e1bc09ee472d7fc980391739e2112  gamma02_london_overlap_portfolio_001.py
53f8a5a3e8106b75cb454ee75676dbe0b5cc4b2da7c14eae25e4ec5c4ad16bcf  gamma02_m1_density.py
3a222847d8e29fe097fa133a469feb4b393252fce22c9be5188943a451d19926  gamma02_ny16_17_18_subphase_lifecycle_001.py
4f66675f4ce49ee042051592980a30a90dbd7f40fa4e0b3a834220f6cf3eea33  gamma02_ny17_fast_quantum_exact_053.py
238b947d49d46c252fc583fe4db7f88e02f9dd530d1419323eb571daf7bf98a8  gamma02_ny17_quantum_minute_window_075.py
8cf55fe2365f25b9a8acc7996f0f2c72eba7c2c9bc6a90a8e6d97f528b5c7131  gamma02_ny_campaign_inventory_portfolio_001.py
6f566cd0dc7544ba2d2829b175515a76d2de8c08ba40627831f94ad3b4043b61  gamma02_one_event_per_tick_audit_014.py
84b0fe8b184f6c47d41dd2413d3374f1274c26ea71e3d102e5dd5e7b218751d0  gamma02_profit_funded_surge_049.py
687f1886001766d05aee6bc8f24bdf84ff2d66bfd3631811a09843cdbbf4b2b2  gamma02_profit_funded_surge_equity_051.py
6c80f3991ad9f618913da9f6311f1ba76330193144fc2e3e65b89d156669f3b0  gamma02_rebreak_desk_specific_018.py
818e8e020ad971ec2f3599d613c4e68a3550c1b6471e37a871f41ed1b9fdd5f1  gamma02_rebreak_latency_017.py
0b8edc63efd38af10f47519c67b0247b7e99f972757d34af04c977bda25cf414  gamma02_time_decay_conviction_001.py
5c0a2802d8c883d0612ba7549ac7c146836d93907d6b3182fc7857d2f2bc08f1  stmr_base.py
f89e85ade7aaeb7ccffec19215795876f5d811af2ba8a7a6c1f646aef030ec08  stmr_janjul.py
bb83dd19b610e7d77d9dfac658aef01ee8cf4f7524dbef1919b3a7b5efd0c308  gamma02_funded_cap_equity_dd_028.py
5ccf5581688fdb45b7f1dfd0441af9bdc89a478cc6f229dd8ec0f60eee8f5dac  gamma02_dual_phase_renewal_quantum_083.py
9552a525108dfc11ea3d4f2c3c1f930e64a65447f583b328fd28b677668fcda4  gamma02_083_heat_parent_ownership_084.py
```

## Recovery authority

Read in this order:

1. `../GAMMA_02_DUAL_PHASE_RENEWAL_QUANTUM_083.md`
2. `../GAMMA_02_083_HEAT_PARENT_OWNERSHIP_QA_084.md`
3. `../GAMMA_02_CURRENT_RESEARCH_CURSOR.json`

Do not rerun <=084 after a chat/UI timeout. Resume with 085.
