# F348-R10 — Coinexx February / original eight-cell historical quote-risk score regime research

**Date:** 2026-10-23  
**Status:** UNAPPROVED, RESEARCH-ONLY. No M-CX-02 checkoff, no G01–G09. Original checklist owner status remains **18/39** (F01–F17, M-CX-01). No native tick-engine/source/parent-model change.

## Frozen provenance and results

Parent research receipt HEAD `266280756d2c23a0869d6c09d15994625f16b213`; backtest/source baseline `ca4b58aec597174b6f6d18ab2f36cba6836e4f4c` remains unchanged. SOURCE_LOCK original broker JanFebJunJul (Coinexx JanFeb broker clock minus120min, JuneJuly minus180min; Dukascopy UTC). Full original event t/side/truth and fixed outcome first native tick in [t+30,t+32) retained.

Archived original parent ZIP pins:
- F333/R08 original exact full eight-cell masks: `ce9bfbe8d1e7c5bc3e6bc3f45674eda1768ae9f2d752db88843d5ff7f0ed5583`
- R09P original source emission candidate score masks: `c5a93759efeb3ef870300e2875abd3fc22851eed8f499ecb7979d218e1c47158`
- F332 pinned native quote-risk scores: `39482a31610550adb940734b581e1eb6cc7335ed404e29c447e81e8bc9277605`

**New mechanism:** preceding frozen native t+15 F332 quote-risk score distribution in 30s/2m/10m windows, rolling mean/dispersion, original side, hour phase, current already-available F332 and R09P score, and prior matured original outcome fractions (previous-label availability strictly after tprev+32.001s). Separate Coinexx/Dukascopy LightGBM 511-leaf×85-round, opposite-vs-correct and neutral-vs-correct heads; 40s embargo, JanFebJunJul early80 chronological fit, later20 already historically exposed. A t+15 decision only if the original F330 candidate remains unfilled and PENDING.

**Independent eight-cell results:** +10,077 additional incorrect/neutral vetoes and +1,099 correct losses, **9.1692:1**, exactly disjoint from R09P q999 veto mask; same UTC-hour and original-side equal-count random-suppression expected 4,471.69 wrong removals, measured 2.254× expected. Original source R9 UTC quota windows 4,178/4,178 PASS (min slack5). New exploratory full-eight-cell R09P+R10 combined: **726,530/1,366,180 incorrect removed=53.17967%**; **1,018,849/1,208,071 correct retained=84.33685%**; NOT 90% wrong removal in every source cell. Coinexx Feb new +774 wrong /52 correct; total Coinexx Feb 77,456 wrong removed, below original same-month fitted teacher 106,881 and 90%-of-teacher volume 96,193.

**Important qualification:** Source last20 previously exposed +596 wrong /308 correct (1.935:1). All 2026 JanFebJuneJuly training/evaluation are previously inspected, and upstream R09P/F332 model fitted on same months. No true untouched OOS, full raw quote tick tapes currently not mounted, NO new actual raw tick arrival detector, no BOCPD posterior, no actual MT5 fill P&L, MQL5 compiler, $100/$200 capital survival, or owner approval. The new input is a *frozen native quote-risk SCORE stream*, not original tick arrival intensity. May remains the single previously randomly selected and historically exposed OOT candidate; neither March nor April scored in this experiment.

**Original portable complete source/masks/weights package:** `F348_R10_MCX02_QUOTE_RISK_STREAM_HISTORICAL_UNAPPROVED_20261023.zip`, 20,329,984 bytes, SHA-256 `a2bd339b4ae80c7a78ddc647a9821309667caf885a83e376beea750fdb33058c`, 15-member ZIP, CRC and internal source member-SHA PASS. Created locally in this chat; **NO authenticated remote Google Drive archive upload is claimed**. Includes predeclared frozen plan, model source, four LightGBM text weights, 8-cell candidate original-index masks, independently recomputed metrics, quota ledger, historical weaknesses, scientific receipt and manifest. User should preserve this exact archive in authorized Drive if durable source bytes beyond this conversation are needed.

**NEXT candidate R11:** actual approved native raw quote arrivals (bid-only/ask-only/joint marks, time-gaps, Hawkes or Poisson-BOCPD change posterior) × completed M1/M5/M15/H1 × prior matured three-class history, separate opponent and neutral heads, high-capacity first, correct guardian; exact source SHA verification and stable original event t/side/truth, 8 cells and 4,178 quotas. No replay-engine rebuild absent ENGINE_DEFECT_TICKET.

Authority: original full governor [Google Doc](https://docs.google.com/document/d/12lnZDGOGynu9APzK6nh0nuYeEOpB1hbgaeOszMuMFms/edit), [full forensic log](https://docs.google.com/document/d/1cYkw43LC5Ot-V686onwQS5cDZRKPyw1T1T6MvbFVSCA/edit), [original checklist](https://docs.google.com/document/d/1i2GyLfwVFvyjxB-sNaOwkS6kzZLSWTsijGXaA9qJou0/edit).