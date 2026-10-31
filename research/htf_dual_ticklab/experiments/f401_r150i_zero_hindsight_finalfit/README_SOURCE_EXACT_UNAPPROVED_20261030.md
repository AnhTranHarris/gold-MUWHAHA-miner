# F401-R150I — hindsight-supervised offline / zero-hindsight-input final-training initial fit

**Status:** research-only, unapproved. **Parent:** F401-R150H `96802ea6479cab5a59ae5e05ed1ee896873f3911`.

Owner correction implemented exactly: Jan/Feb/June/July historical FILTER08 hindsight may teach offline; runtime inference accepts **zero hindsight input**. This is not “teacher-free training.”

## Runtime market-only bank

252D per eligible T1 event:
- R120 92D native 250ms/500ms/1s/5s/15s/30s + session/grid state.
- R120 36D completed M1/M5/M15/H1 state.
- R147 57D strict event-origin-to-decision path.
- R150E 20D source-only cross-scale interactions.
- R150F2 23D genuine first t0+[15,16)s quote-prefix state, absolute tape index removed.
- R150F3U 24D Jeffreys Beta-binomial quote reliability/path interactions.

Forbidden from runtime: truth/teacher score/rank/mask, matured class state/rates, R24/R148B outputs or monitor, R150G parent scores, sampled-event BOCPD8, future outcomes.

All eight authorized raw Jan/Feb/Jun/Jul Coinexx+Dukascopy sources were freshly SHA-256 reverified before feature construction. Entire eight original event populations were aligned and scored; missing T1 decision quote fails closed/abstains.

## Initial final-training pass

Per broker: deterministic 400,000-row four-month fit (100,000 valid rows/month). Five runtime heads:
1. historical teacher selected-mask student;
2. continuous within-cell teacher-rank student;
3. CORRECT specialist;
4. OPPOSITE specialist;
5. NEUTRAL specialist.

The five models take only 252D market state at runtime. On both brokers, arbitrary mutation of truth, continuous teacher score and teacher mask after feature creation produced bit-identical output on 2,048 genuine January rows.

Full-cell fitted CORRECT-class AUC of the class-specific bank:
- Coinexx Jan/Feb/Jun/Jul: 0.82147 / 0.82917 / 0.83506 / 0.83196.
- Dukascopy Jan/Feb/Jun/Jul: 0.81979 / 0.82686 / 0.83489 / 0.82939.

This is exposed historical final-fit research, not G08.

## M-DK-01 replacement comparison

Original Dukascopy January hindsight teacher: 94,603 wrong veto / 7 CORRECT lost.
Strict R150I market-only loss-matched best current score at <=7 CORRECT losses: **1,016 wrong veto / 7 CORRECT lost** (990 OPPOSITE + 26 NEUTRAL).

Therefore M-DK-01 remains OPEN. This initial fit proves real zero-hindsight selectivity but does not reproduce the historical teacher’s capacity.

## Preservation

MT5_EXPAND /00 scientific receipt:
https://drive.google.com/file/d/1xocOxuk4EnDLZByquVmXFyh6mdYp_WR_/view

MT5_EXPAND /01 code/models/eight-cell scores/tests/manifest ZIP:
https://drive.google.com/file/d/19SKrtZQcY3grwnTt6wCp4FgFONWxccJF/view

ZIP: 73,560,269 bytes, SHA-256 `87a2f477099cf9fc4871df7e1adac643543179ba36fe092025f215ea4cc4bd7e`, 42 members, CRC PASS and internal SHA manifest PASS.

Scientific receipt SHA-256 `52f0029362609a2c96ab81b50e6ad8c0489051ebc52c1be1eaeb82a18d1b0cf4`.

Full Python source is preserved in the /01 ZIP; this GitHub branch is a lineage/readback receipt and does not claim that the large score/model evidence is committed.

No /02 promotion, no checklist self-approval, no G07/G08/G09, no OrderSend or P&L claim.
