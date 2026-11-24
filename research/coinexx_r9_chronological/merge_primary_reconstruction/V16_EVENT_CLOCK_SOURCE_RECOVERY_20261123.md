# V16 R9 HybridGate — merged-primary causal event-clock continuation (2026-11-23)

**STATUS: HEAVY NINE-MONTH IN-SAMPLE ENTRY-ONLY RESEARCH.** Entry volume PASS, aligned-entry reconstruction INCOMPLETE. NOT a native MT5 EA, not a funded account backtest, not deployed.

## Mandatory exact-source recovery (not this summary)

**[Complete 37-member C++17/Python/model/QA V16 source ZIP in MT5_EXPAND](https://drive.google.com/file/d/1scbHJXlkSFTLRWl1iqEJGSHpx-TwElb2/view)**

- ZIP SHA256 `82219d9dc86f033f82b2688eecd64d92b2ad9deea6b1bf5a9986e830c592ca52`, 6,678,540 bytes. Contains **36 executable-source/model/scorecard/QA payloads, all 36 SHA256 verified**; ZIP CRC PASS. NO raw tick library or large original merged-ledger duplication.
- Read **SOURCE_EXACT_CONTINUATION_V16.md** in that ZIP then examine **the actual** `v16_event_candidates.cpp`, `fit_v16_eventclock.py`, `hybrid_v16_clock.py`, `v16_event_side_specialist.py`, `replay_v16_without_merge.py`, and the numerical month-by-month scorecard/model receipts. Read the complete prior V15F parent source ZIP, too.
- Canonical R9 `Experts/GoldMuwahahaMiner_R9_HybridGate.mq5` v1.90, original blob SHA `7eecb5f1947017a01ce85b2520725de54749e523` UNMODIFIED.
- Authoritative historical reference: NEW original Jan + Feb–Sep **R9+Coinexx outcome-aligned MERGE** trade ZIPs (272,352 entry timestamps/directions; +$360,693.05 historical label-account net). Source chronological Coinexx TickLogger January–September gzip streams (72,129,347 quotes), 9/9 original SHA256 fingerprints verified. Frozen merge is the **supervised target**; no reference entry timestamps or sides are loaded into runtime inference.

## Scope and precise results

Original source-derived V15F: 268,270 entry-only proposals; 36,087 exact same-side ±2s matches, 94,373 ±5s, 142,182 ±15s, 174,217 ±30s.

**V16 accepted research candidate:** C++ tick-built 250ms/1s/5s/15s/30s/M1/M5/M15/H1 candle and 14 microstructure event families; two corrected 3-class first/late event models; chronological source-event admission **preempts** the V15F source-only fallback only when its as-of score passes frozen in-sample cutoffs **0.45/0.45**; a separately trained source-event side specialist refines BUY/SELL.

V16: **277,582 source-only entry proposals** (**101.92%** historical count; every month 98.38%–107.59%, count requirement PASSES).
One-to-one same-direction matches: **51,894 within ±2s**, **101,108 within ±5s**, **146,142 within ±15s**, **178,851 within ±30s**. Same-side ±5s recall of frozen 272,352 entries = **37.12%**. Alignment remains BELOW goal; NO MT5 proof of concept, no holding/exit changes.

The first pure V16 event-hazard replacement produced 90,780 ±5s matches and was REJECTED (worse than V15F). Chronological event+fallback hybrid then improved to 101,053, and separate source-event side model only +55 further to 101,108. Fixed additional 1–8-second quote-confirmation delay was evaluated on actual Jan/Mar/Jul source quotes and **rejected** due worse ±2s/±5s alignment.

Nine-month original frozen labels were used for fully in-sample fitting and threshold selection, which is permitted by owner instruction. At inference models use ONLY observed source quotes and already completed tick-built candles. Event source timing and model side are generated without target ledger rows. 9/9 **independent source-only inference replays** regenerate all 277,582 V16 signals exactly. First 40,629 event observations from Jan 1.2M quote prefix match full source byte-for-byte. Corrected an initial three-way training label precedence error BEFORE accepting models; rejected invalid model never used.

## Next research, not yet completed

Upgrade the **timing** of event triggers, not an isolated direction threshold. Existing 14-event retrospective upper coverage 164,785/266,776 first/second mapped positions ±5 seconds; only 101,108/272,352 actual same-side signals aligned. Research quote-clocked 1-second competing event hazards and fast structural recapture without future knowledge; preserve 90% monthly entry floor and R9 minute-cycle/rearm architecture. Do not change original trade holds/exits or production MQL5 before entry-only gate.

**GitHub branch only pins original-source lineage and recovery; the complete V16 executable C++/Python sources are in the linked ZIP, not native MQL5 committed into this branch.**
