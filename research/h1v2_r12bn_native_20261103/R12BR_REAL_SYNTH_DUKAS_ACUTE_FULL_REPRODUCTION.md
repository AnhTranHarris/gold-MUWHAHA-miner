# R12BR — separately verified R9 REAL-tick Strategy Tester acute cross-feed research, 2026-11-03

Classification: NON-CAUSAL, RETROSPECTIVE FUTURE-KNOWN HINDSIGHT, NOT VERIFIED COINEXX LIVE BROKER FILL DATA, NOT DEPLOYABLE. Original R11S4, R12, R12D-Q, R12BN and patched R9 v2 remain unchanged.

## Distinct source contracts

- Original R9 REAL tester 2026-02-02 gzip is PRIMARY Drive file 1-oT2D3Lqhs8XLWYS-Sgjxk49j4IkLM_q, 12,187,405 source bytes, SHA256 24e4b31935ead7b0eb039fe84dc8972c59500b362cac21721739f1b0c050b3d7.
- Original R9 SYNTH tester 2026-02-02 gzip SHA256 dcedb28f7453c80d2dec5ffe5d386dad1661134ba61765337155fbbaeb6213a2.
- Original Dukascopy full February raw gzip SHA256 ed3b3545c990c88d78519594c17c8915b0f679adcb0a94920ba7524f1f6d5c5d.
- Original R9 06:00 UTC source-aligned hour reference is 104 entries, not an invented quota. R9 tester server UTC offset -2h for February from original R11S3.
- Never mix source entry and exit prices. Use independent quote order, original Bid/Ask, integer USD0.001 source price resolution and source timestamp/ordinal.
- Quote admission: observed-as-of first250 and all distinct-ms separate, >15s quote drought reset, >=300s fresh warmup, spread <=USD1.50; no same entry millisecond later-ordinal fill. BUY enter Ask/exit Bid, SELL enter Bid/exit Ask.
- Strict R11S1 target: +USD0.10 nominal net after USD0.02 fee within first15s, no >=USD0.10 adverse movement from opening liquidation at any observed quote through FULL30s. Gap>15s or incomplete horizon censored.
- Hypothetical position exit: first observed later-millisecond TP >=USD0.10 after nominal fee. Exact source-isolated intervals selected with earliest-finish greedy. A source quote crossing TP is not an independently certified market fill.

## Feb 2, 2026 at 06:00 UTC original source witness

| Metric | R9 REAL tester | R9 SYNTH tester | Dukascopy |
|---|---:|---:|---:|
| Full source file quotes | 594,529 | 570,377 | 7,538,339 |
| Hour observed quotes | 29,884 | 28,978 | 43,657 |
| Hour raw spread median USD | .66 | .20 | 3.157 |
| Hour raw spread >1.50 fraction | .015493240530049525 | 0.0 | .9947087523192157 |
| Hour eligible first250 observations | 13,694 | 14,376 | 92 |
| Hour eligible distinct-ms observations | 29,421 | 28,978 | 231 |
| Distinct-ms strict GOOD15+SAFE30 candidate timestamps | 3,166 | 12,563 | 13 |
| First250 strict GOOD15+SAFE30 timestamps | 1,520 | 6,247 | 6 |
| Isolated-hour first250 TP nonoverlap intervals | 705 | 1,853 | 6 |
| Isolated-hour distinct-ms TP nonoverlap intervals | 852 | 2,137 | 7 |
| Original R9 SYNTH hour reference | 104 | 104 | 104 |

Real-tick Strategy Tester is NOT live Coinexx fill verification. Hour-isolated capacities ignore incoming prior-hour occupancy and are optimistic. Original frozen fixed30 R11S4 count4 in Dukascopy this hour is not the same lifecycle as firstTP 6/7. All success-qualified selections are retrospectively future-known. No inference of predictability, positive expected return or robustness follows.

## Exact source and recovery

Source: src/r12br_real_testlog_acute_single_day.py, Git blob SHA1 832a8fa2386fa4f998b6f21c70b1dd70aaa93a2a, original source SHA256 7d354a19602682c54e08db4fb003a10d4c8e58a8d022beddd34b0923b12f7608. Depends on frozen parent R12D-Q source at SHA c46d6bd30ec5a4a2ca120dcd46246114eadbed98, Python numpy/pandas/numba and three original quote files.

Complete original output JSON SHA256 c9554a0a665ee076c506db0e8fa5d34a68ce35eb1060131d6e83e801fb17b4c6. GitHub result JSON is a same-fields reserialization, NOT byte-identical to original file.

Exact original source script, exact JSON, execution log and preserved original failed-run traceback are all inside MT5_EXPAND https://drive.google.com/file/d/1CIxT_Ysxc9y4YT8Bji6NnjZz8PZahDP7/view ; ZIP SHA256 ea090e37082a420402f569f4c8fe5ae17cb128737e489b9d1a735e80b308e4c5, 5 members, all member SHA and ZIP CRC verified. Uploaded, downloaded and verified exact bytes. Failure F01: source classifier compared label DUKASCOPY instead of DUKASCOPY_RAW, triggering pandas ValueError for missing source columns on third feed. Corrected ONLY this new source and reran all three.

Main MT5_EXPAND progress ledger: https://docs.google.com/document/d/1v0X5Vkif81qV784Ja6FVe5DfyQLx7RoEw-yjC4m7D1Y/edit
Original R12BN 127-member full source science archive: https://drive.google.com/file/d/1fPU9qC7QSQInPHoL2jlxNzK2zrSAf4li/view
Original R12BN 177-member all 88 atomic source ordinal traces: https://drive.google.com/file/d/1HMj9LVRpmYxjIQJEz_Qolb1lt7iFzq4c/view

Mandatory next scientific work: full archived R9 REAL-tick tester four-month source under strict separate execution, then true broker ticks/fills where available, cost and latency stress, dynamic stop/trail and portfolio risk, as-of student freeze, chronological purged calibration and genuinely new OOS. No MT5 compile, real broker execution, causal student, profitability or deployment approval here.
