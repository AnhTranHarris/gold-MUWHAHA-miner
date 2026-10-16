# 000 — CURRENT VERIFIED RESEARCH ENTRY POINT (QC RELEASE)
**Date:** 2026-10-16 | **Purpose:** immutable navigation/authority order only, NOT a replacement for original research.
**Current QC development branch:** carson/htf-qc-handoff-2026-10-16
**Approved pre-QC parent:** 005addb2c8b05ff9734c28239810ce0ac3b7944f (v1.2).
**Canonical GitHub repository:** https://github.com/AnhTranHarris/gold-MUWHAHA-miner
**Most authoritative current HEAD:** READ LIVE from above QC branch, match the published QC receipt. Never presume a cached SHA.

## Distinct Google Drive account routing (CRITICAL)
- **Research and approved market evidence — PRIMARY Google Drive connection**, research root https://drive.google.com/drive/folders/1IAoHUE9Gfb6YYrleZdLtiJ0jydc__gfZ .
- **Long-term MT5 maintenance/archives — MT5_EXPAND Google Drive connection**, root https://drive.google.com/drive/folders/1iN-wfoCni64OX12r2FeGFVUzKOYSPcjv .
- Do NOT query the MT5_EXPAND folder using the PRIMARY account and infer a missing/deleted folder from its 404. Verify with the proper connector, and confirm both connections are accessible in a new chat.

## Exact permitted ORIGINAL research sources (PRIMARY connection)
1. Coinexx broker-recorded Jan–Sep 2026 XAUUSD bid/ask months, 9 files: https://drive.google.com/drive/folders/1XzHug6HYQdSKIbKuGhBTOUHawAXynIb4
2. Dukascopy user-approved Jan–Jul 2026 XAUUSD bid/ask months, 7 files: https://drive.google.com/drive/folders/1lSCfO_awUKkbR4I6xDTy9orjIl0SrgIV
3. R9 4 tester reports + SingleTestCache binary, 5 files: https://drive.google.com/drive/folders/1S0erLKfFpqQUVHHIHDql72PgsH6vQrMF
4. R9 REAL tester logging parts 01–10: https://drive.google.com/drive/folders/1NGQ15bZ962HuHjada2U-xpnecVudsOwG
5. R9 SYNTH tester logging parts 01–10: https://drive.google.com/drive/folders/1r5LJ0s8XdQDql7J-utNBExugZkdi8oOB
6. Exact approved 16-file SHA-256 allowlist: GitHub research/htf_dual_ticklab/htf_ticklab/source_registry.py on the CURRENT approved branch. No other data or branches authorized by mere co-location.
7. R9 specimen (READ-ONLY), exact SHA 8729a6345655a7b4ea31facc81982004ee2b8921: https://github.com/AnhTranHarris/gold-MUWHAHA-miner/tree/carson/mt5-r9-hybrid-gate-certification .
Official MetaQuotes documentation allowed only for platform mechanics. Source trust comes from user approval and SHA not from an assistant response.

## Current authority stack — always read originals, not summaries
0. Latest explicit user direction, including this QC/handoff instruction, takes precedence for named changes.
1. Source supersession XAU-HTF-SRC-002 (the Dukascopy exception): GitHub research/htf_dual_ticklab/governance/SOURCE_AUTHORIZATION_SUPERSESSION_v1.0.md; Drive original https://drive.google.com/file/d/1qElhwjYLxunB1D_whIC6EJOSY8cHZ3qa/view .
2. Investor mandate XAU-HTF-INV-001 v1.0: https://drive.google.com/file/d/1rSWeGBht_IvEWzS9gf5qIZprPIotuxvb/view .
3. Anti-drift v1.0: https://drive.google.com/file/d/1kS11NY0RRFaL0NQ-BxUc21u85Dej5VFq/view .
4. Whole-system/build-lineage v1.1: https://docs.google.com/document/d/1f65dWnWa9AGGTKYoqQ_7rr28lQbx4EppQEGUUAMWW9U/edit and exact GitHub SYSTEM_BUILD_AND_RESEARCH_LINEAGE_v1.1.md.
5. Cross-cutting anti-summary / continuation v1.2: GitHub governance/CROSS_CUTTING_CONTINUITY_LAW_v1.2.md and governance/NEW_CHAT_BOOTSTRAP_PROTOCOL_v1.2.md. Deployment receipt: https://docs.google.com/document/d/1ovyJqkODv4OexhOlwFjirXu6yae-KV5BhaI7Wc_ADW0/edit ; source release ZIP https://drive.google.com/file/d/1fLFoVxZqoBhdfDZCiglA1BZ5x49EPFA-/view.
6. Legacy snapshot/decision history: https://drive.google.com/drive/folders/1v1bhQx_6LvM9-Xv5oJtYP8fImFR_Bzkp . Preserve original START_HERE.md and SOURCE_LOCK... as historical records. **They wrongly say Dukascopy excluded for present-day research**; that provision was EXPLICITLY superseded. DO NOT USE THEIR OBSOLETE INSTRUCTION AS THE ACTIVE SOURCE LIST. Reports 1–3, original methods, original ledgers, annexes, and Report 4 remain original evidence.
7. Report 4 SYNTH forensic folder: https://drive.google.com/drive/folders/1lgcMc7EQvCUK_8aQ-dJne2yNEwTVjGha . Historical synthetic tester results only, not live executable proof.
8. MT5_EXPAND maintenance archive: https://drive.google.com/drive/folders/1sYo8A-W9vCPtIunure_j7hicOosQGLdV ; its read-first policy https://docs.google.com/document/d/1ffmv2raWYPGydVAeTpWhBapcvjyFXAN2T6iTAYaF-Qk/edit ; artifact register https://docs.google.com/document/d/1qNUtacP4x2UzTvttZO5ivbYPXZc-fYrNj8GRGSIS0T0/edit .
9. Canonical future REPRODUCTION folders directly under MT5 root: failed https://drive.google.com/drive/folders/1lq7Hr2qMQvW8FHqwE_47CTZkVT2y7F9G and successful https://drive.google.com/drive/folders/1BmtxKanACUvjz0kCb1_tTMiEZngOCFM1 . Both contain full-case contract docs.

## Critical technical prerequisites
- Coinexx export source clock is not correctly cross-broker aligned if treated as raw UTC; corrected UTC follows empirically observed minus 120 minutes Jan–Feb and minus 180 minutes later, March DST transition. Original source_ms and corrected Quote.ms must both be preserved; Dukascopy already uses UTC. Aug–Sep correction is extrapolated, not independently paired with Dukascopy. UTC research receipt: https://drive.google.com/drive/folders/15etN9KMQxZKbApGu0gtml1R2a6SUET6N .
- Use Coinexx and Dukascopy independently on matched Jan–Jul corrected UTC windows. Never merge both quote tapes into one fictitious broker. All 16 monthly SHA-256 pins checked against mounted files on 2026-10-16; full source bytes in their original Drive folders remain authoritative.
- Initial capital $100/$200 and pre-$5k survival-first. Trade-volume target 710–2,127/day is a benchmark, NOT a hard reason to force trade submissions. Daily/weekly/monthly and hourly investor goals are goals not guarantees. Whole-system shared cash/equity/margin is the scoring unit; standalone alpha diagnostic only.
- The implemented Python replay is currently a two-broker research baseline, not a complete multi-signal router or a production EA. Never claim profitability or investor certification. Planned next build: deterministic multi-signal bus with central position/margin/execution/risk arbitration and portfolio-level paired replay.

## Exact new-chat bootstrap (NO UNVERIFIED RESEARCH)
A. Open this CURRENT index; inspect the original full policies and deployment receipts above.
B. Confirm both Drive account connections with an actual folder listing. Verify current GitHub HEAD, parents, source registry SHA-256, UTC module, tests.
C. Retrieve original complete research evidence relevant to the specific active task, current experiment ID/frozen plan, complete results, lineage and checkpoints. Treat previous chat recaps as pointers only.
D. Establish LAST_VERIFIED_HEAD, LAST_VERIFIED_EXPERIMENT, LAST_COMPLETE_CHECKPOINT, BLOCKERS, NEXT_BUILD_ACTION and a full actual-artifact list. If there is no frozen active experiment, state NOT STARTED (do not invent one).
E. Do not start new strategy research simply because a new chat opened. If evidence is unavailable, mark affected scored work BLOCKED_PENDING_RECOVERY and locate only the authorized missing item.
F. Execute new work ONLY after the user confirms the next research or build objective; preserve branch ancestry and create fresh versioned receipts. No off-project sources.

## Known QC findings (not silently resolved)
- Historical START_HERE.md explicitly conflicts with later Dukascopy approval: this present index supersedes its *navigation*, not its original scientific evidence.
- Original v1.2 full recovery archive is PREDEPLOYMENT and contains an older deployment-status field; the v1.2 deployment receipt supersedes that field. No intact full verbatim chat export has been independently verified.
- Additional EMPTY nested 07_FAILED/08_SUCCESSFUL folders exist under MT5 archive. These are NOT the authoritative failed/successful case destinations; the two direct-MT5 folders above are.
- The GitHub metadata governance and continuity checkers are not an investor-certified real execution/portfolio proof. Historical R9 SYNTH outcomes are not real fills.
- Existing old/alternative Report3 files in workspace are QUARANTINED until specifically user-authorized. Never infer permission from name or co-location.
- Remote GitHub Actions passing status must be checked live; no success is assumed from local pytest or a workflow file.
