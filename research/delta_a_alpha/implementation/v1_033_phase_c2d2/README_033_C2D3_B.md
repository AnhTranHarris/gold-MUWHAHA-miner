# DAA-033 Phase C2D3-B: Continuous real February paid 049→119→084 L7 replay

## Decision

**Completed bounded bridge replay; NOT a full eight-layer original V1 certification or profitable deployed strategy.** This continues and preserves the exact full literal owner V1 whitepaper (`research/delta_a_alpha/whitepapers/DAA_V1_OWNER_GOOGLE_WHITEPAPER_FULL_VERBATIM_030.txt`, Git blob `1b92b3c89159681a7181508de158af685cf5780c`). All inherited Phase C2D2/C2D3-A source blob hashes were individually verified against GitHub before local execution. This checkpoint is frozen source-grounded engineering, not new architecture.

## Reconstructed proof

- Input exact January Dukascopy SHA256: `d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5`.
- Input exact February Dukascopy SHA256: `ed3b3545c990c88d78519594c17c8915b0f679adcb0a94920ba7524f1f6d5c5d5`.
- **3,900,880 January prehistory ticks** supply completed H4/H1/M15/M5 original EMA-sign **proxy** states. Not the owner's distinct-role H4/H1/M15/M5 structure.
- **1,136,212 continuous executable February Bid/Ask ticks** from Feb 2 06:30 UTC; 049 original 001/017/019 offline vs online **13,063/13,063 exact tick index, side and UTC-hour agreement**, *before* any L7 physical funding decisions.
- All funded child proposals are regenerated from actual parent fills; denied children have no earned credit. Actual L4 child close/parent termination flows through shared L7 order-per-second entry+exit capacity and live Bid/Ask equity marks.
- **5 actual funded 119 parent windows, 18 accepted 084 children, 18 executed child closes** (12 fast profitable, 6 bad/slow); 208 total closed physical positions and zero funded second-generation 119 parent admissions.
- Baseline **+$12.263 net** from $100,000 research equity, 208 closed, PF **1.00646**, maximum quote-equity DD **$2,339.194**, 32 max simultaneous open and four combined orders/sec; independently maintained cash/open-book/equity audit found zero discrepancies.
- The $2,339 equity drawdown versus $12 profit is weak economics and **does not** demonstrate $100–$500 survival; performance of original JAN039/FEB045/FEB047 source-research tapes is not attributed to this bounded replay.

## Causal restriction and actual-exit ablations

| Setting | Trades closed | Funded 119 windows | Funded 084 children | Net USD | Equity DD USD |
|---|---:|---:|---:|---:|---:|
| baseline | 208 | 5 | 18 | +12.263 | 2339.194 |
| cap1 | 8 | 2 | 0 | -34.095 | 110.727 |
| spread010 | 0 | 0 | 0 | +0.000 | 0.000 |
| orders1 | 200 | 5 | 15 | -546.607 | 2333.717 |
| sourcecap2 | 26 | 2 | 10 | -57.074 | 223.503 |
| parentttl25 | 356 | 5 | 20 | -1193.463 | 2109.870 |

All six cases observed the same 13,063 source-level 049 candidates. Independent quote-equity/cash audits had **zero** mismatches. Spread and global capacity denial eliminate entire funded child ancestry; changed per-second order admission or real funded parent TTL changes child funding and net P&L. The TTL variant changes order *exit geometry*, not the historical frozen source candidate tape. No month identity optimization was used.

## Source-grounded execution

Use exact three archives under `--root`: `XAUUSD_DUKAS_2026_01_ticks.csv(3).gz`, `XAUUSD_DUKAS_2026_02_ticks.csv(3).gz`, `JAN037_ITERATIVE_XAUUSD_TICK_RESEARCH_BUNDLE.zip`. The inherited source helper modules from Phase C2D1 ZIP and latest exact C2D2 code must be importable. Reproduction with numpy/pandas:

```bash
python -m unittest -v test_original_119_multi_parent_033c2c test_funded_084_l7_bridge_033c2d2 test_c2d3_queue_stress_033 test_c2d3b_real_quote_oracle_033
python c2d3b_feb_funded_replay_033.py --root /mnt/data --prepare
python c2d3b_source_index_parity_033.py
python c2d3b_feb_funded_replay_033.py --cap 1 --out cap1.json
python c2d3b_feb_funded_replay_033.py --spread .1 --out spread010.json
python c2d3b_feb_funded_replay_033.py --orders 1 --out orders1.json
python c2d3b_feb_funded_replay_033.py --low-surge --out sourcecap2.json
python c2d3b_feb_funded_replay_033.py --parent-ttl-scale .25 --out parentttl25.json
```

The 57-MB `.npz` source-state cache is **derived ephemeral data, not part of Git**. Every newly executed run records exact filled/closed actual physical ledger events in `*_PHYSICAL_LEDGER.jsonl`, with file SHA256 in that run's JSON result. The full input archives and prior code are not vendored or duplicated in this GitHub patch.

## Unfinished acceptance

The frozen V1 architecture retains native L0–L7 order: session/Asia/London/hourly grid geometry, true differentiated completed H4/H1/M15/M5, L3 hourly harvest, L4 paid renewal genealogy, L5 trend-within-trend, L6 failure-bounded recovery, L7 physically unified portfolio heat/capital. This **partial bridge** still lacks complete L1–L6 owned source reproduction, original 075 physical parent selection, full January+February economics, actual Coinexx slippage/rejections/margin/hedging/stopout, MetaEditor compile and MT5 real-tick broker parity. The owner whitepaper, JAN039, FEB045/FEB047, MT5 observe-only EA and production `delta` are not modified; March held; August sealed; September reserved.
