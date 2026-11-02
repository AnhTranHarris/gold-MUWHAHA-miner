# H1V2 R9 separate-side hyper-rejection — frozen four-month research

**Status: 4/4 Dukascopy full eligible 250-ms populations evaluated; joint extreme skew target FAIL.**

Primary original immutable H1V2 teacher repository branch: `carson/h1v2-fourmonth-hindsight-teacher-20261102` @ `edce573d9c53b743dc5de1b0d741c81370af52c1`.

H1V2 R9 dedicated research branch: `carson/h1v2-r9-fourmonth-competing-side-hyperreject-20261102`.

Read `H1V2_R9_FOURMONTH_SOURCE_EXACT_VERIFICATION_20261102.md` before rerunning; it contains source audit, exact months, every entry count, strict correctness, failure cases, and the distinct next experiment. Preserve all original R9 v2 and H1V2 source code and original BUY/SELL 30s label arrays.

## Recovery structure

- `src/r9_side_competing.py`: 53-feature BUY/SELL independent BAD/NEUTRAL/GOOD rankings and source parity, fast numba exact one-position replay.
- `src/r9_split.py`: restartable independent-side fit and threshold freezing.
- `src/r9_checkpoint_replay.py`: 500k-candidate bounded scoring plus precise full-month replay.
- `src/r9_compact_recovery.py`: stable all-threshold exact replay compact storage.
- `dependencies`: the original R7 as-of nested-regime generator, R8 as-of per-event feature builder and source audit.
- `results/R9_{all4|lomo07}_...`: frozen training weights, exact full-month replay receipts and compact per-event ranked score + side lists. The latter were **fully replayed against the exact original teacher 30s exit matrix at all nine thresholds** with no mismatch.

## Recreate locally

Set `H1V2_R9_ROOT` to the directory containing `h1v2/results`, `h1v2_r7/results`, `h1v2_r8/results`, `h1v2_r9_hyperreject/results`; default is `/mnt/data`. The raw source archives for original H1V2 are at https://drive.google.com/drive/folders/1lSCfO_awUKkbR4I6xDTy9orjIl0SrgIV. Original H1V2 full source/executable dependency kit: https://drive.google.com/file/d/14Zqs-PyZ70qr0NTvpJRxpT0XcVc8msUu/view .

Restore H1V2 original exhaustive `h1v2_dukascopy_{month}_oracle_labels.npz` files from raw ticks using original H1V2 code, verifying published SHA. Restore `R7_FULL_REGIME_{month}.npz` with original R7 code (included as dependency), and `R8_ASOF_{month}.npy` with original R8 code (included). Do not change strict event order or costs.

Run `PYTHONPATH=h1v2_r9_hyperreject/src python -m pytest -q h1v2_r9_hyperreject/tests` (five tests). Exact top-25 admissions and net reconciliations can be reproduced by `PYTHONPATH=h1v2_r9_hyperreject/src python h1v2_r9_hyperreject/src/r9_compact_recovery.py --mode all4 --month 01` after restoring original score blocks; alternatively use saved TOP25 archive directly and the frozen FULL_REPLAY receipts (no source scores needed).

**No MT5 compile, live deployment, Coinexx economic validation, model-policy approval, or true independent out-of-sample evidence.**
