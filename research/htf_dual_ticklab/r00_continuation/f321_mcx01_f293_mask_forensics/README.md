# F321 — Original F293 mask stratification for M-CX-01 (2026-10-22)

**RESEARCH-HISTORICAL FORENSIC ONLY. No M-CX-01 model accepted. No demo/live MT5 authorization.**

## Fixed ancestry and scientific authority

Parent: `0a2eb1ffce203e842525fc224b6694f220859fb1` (F318–F320 branch). PRIMARY governing original checklist: **17/39 historically approved; M-CX-01 and G01–G09 remain OPEN**.
Canonical append-only forensic log: https://docs.google.com/document/d/1cYkw43LC5Ot-V686onwQS5cDZRKPyw1T1T6MvbFVSCA/edit

The adjacent `F321_MCX01_F293_SOURCE_MASK_STRATIFICATION_RESEARCH_ONLY_20261022.zip` is a **complete 7-member reproducible source/test/results archive**, NOT a production filter or a derived-cache replacement.
Archive SHA-256: `81d61d59df8038536679124cb609c3609231f31a0b38fb09166738767781c7cd` (17,414 bytes). Members: Python source, four-test unittest file, 8-cell original summary CSV, 384-cell UTC-hour×side CSV, JSON receipt, signed per-member SHA manifest and detailed Markdown report.
Independently verified source recovery kit SHA: `00a63974729667568297ed1aa713f8d102929cf393e57e8c3509cb4d8ca94397`; original 8 F293 mask NPZ member hashes/CRC pass. Archive raw recovery original: https://drive.google.com/file/d/1pDEEcImXIznKq9qqujxR7jwl2wFiV1AT/view

## Findings (historical fitted, NOT predictive)

Reproduced immutable eight original broker-month event totals: 2,574,251 original emissions, 1,208,071 correct, 1,064,545 opposite, 301,635 neutral. Exact F293 incremental original-F234-parent bad veto/correct loss: **134,801 / 3,957**; same-period overfit diagnostic 34.06646:1.

**January:** Coinexx original-parent bad veto BUY 8,180 vs SELL 3,229, correct losses BUY 128 vs SELL 49; Dukascopy bad veto BUY 6,380 vs SELL 2,971, correct loss BUY 106 vs SELL 59. These are descriptive effects of a hindsight-trained specialist on its exposed month. They do not prove side-based predictive alpha.

As-of evidence: original NPZ `t` is already normalized UTC; no extra Coinexx wallclock offset is applied. Original `truth`: 0=correct,1=opposite,2=neutral. 8/8 exact `veto => parent` and `keep==parent & ~veto` invariants pass. All four synthetic input-validation unit tests pass.

## Reproduce

Unzip the included research archive and run:

```bash
python -m unittest -v test_f321
python f321_f293_mask_forensics.py --archive path/to/XAUUSD_HTF_MT5_BUILD_RECOVERY_KIT_20261022.zip --out .
```

Complete PRIMARY source archive: https://drive.google.com/file/d/1zCAek9c1y0kt0ClNZgkk1Lgg00VR-ec6/view
MT5_EXPAND research backup: https://drive.google.com/file/d/1LxpBBTTGHAB1HlSzo77eAKsMHYaO4jdm/view

## Scientific boundaries and forward cursor

This diagnostic **does not** fit an M-CX-01 replacement, train on unlabeled future markets, establish all-cell 71%/90%, test execution, compile MQL5, or provide a $100/$200 capital survivor. It cannot be combined with approved F17 because original P05 exact masks are missing; F17 shadow is not a substitute. F318–F320 package (104MB) still NOT remotely verified. Jan/Feb F295 derived-byte parity unresolved. No engine rebuild or historic artifact modification.

Next distinctly scoped, unexecuted hypothesis: **side-conditioned ordered bid-only/ask-only reversal × completed M15/H1 HTF phase × spread/age × mature past outcomes** with classwise opponent/neutral specialists and explicit correct-preservation arbiter. Use original same-event IDs, purged Jan/Feb fit/Feb-late calibration, June/July as research-exposed, original R9 quotas, per-cell 71%/90% gates. No genuine blind April experiment without separate owner source authorization. Park repeat F315–F320 percentile grids.
