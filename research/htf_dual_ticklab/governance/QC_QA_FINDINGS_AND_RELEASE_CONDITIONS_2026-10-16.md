# XAUUSD HTF EA — QC/QA HANDOFF FINDINGS AND RELEASE CONDITIONS
Date 2026-10-16. This is a VERIFIED-CHECK record based on Google Drive folder listings, GitHub exact commit/readback and local source hashes/tests. No strategy edge, new trading code, or investor approval implied.

## Verified checks
- Primary Google Drive connection serves TRADING_RESEARCH folder 1IAoHUE9Gfb6YYrleZdLtiJ0jydc__gfZ; MT5_EXPAND serves MT5 folder 1iN-wfoCni64OX12r2FeGFVUzKOYSPcjv. Querying latter through the former gives 404, a WRONG CONNECTION, not absent data.
- Verified Coinexx Jan–Sep: 9 raw gzip files. Dukascopy Jan–Jul: 7 raw gzip files. R9 REAL tester: 10 parts. R9 SYNTH tester: 10 parts. R9 original tester folder: 4 XLSX + 1 SingleTestCache .gz. Those inventories were checked from provider direct folder listing.
- All 16 monthly authorized tick files were independently SHA-256 hashed from mounted source copies and matched exact GitHub source_registry.py pins. Source bytes/sizes match folder listing.
- Exact old pinned R9 specimen commit 8729a6345655a7b4ea31facc81982004ee2b8921 was read back. Governed dual-broker branch v1.2 HEAD 005addb2c8b05ff9734c28239810ce0ac3b7944f and ancestry checked. Current QC branch must be independently read back after commit.
- Reconstructed GitHub v1.2 Python source from source release archives, verified file blob checksums against GitHub, and ran pytest: 103 passed. The first test invocation used an incomplete local reconstruction lacking governance/EXPERIMENT_PLAN_EXAMPLE.json, causing 29 fixture-absence failures; restoring the EXACT pinned original resulted 103/103 pass. Do not misrepresent the initial reconstruction error as a GitHub engine failure.
- Confirmed original investor mandate, v1.0 anti-drift, v1.1 system governance, v1.2 continuity deployment receipt, UTC repair documents, primary data folders and canonical report archive are present.
- Two direct-MT5 research case folders and READ_FIRST reproduction documents exist, and were read back.

## Defects and remediations
F01 CRITICAL: Original START_HERE.md says Dukascopy is forbidden; subsequent user explicitly authorized seven exact files. FIX: Current QC entrypoint links SRC-002 supersession and source registry; old handoff preserved as historical evidence.
F02 HIGH: v1.2 GitHub Actions push branches contain only governance v1.0/v1.1, not v1.2. FIX: Change workflow to push carson/htf-* and workflow_dispatch on isolated descendant QC branch, verify commit and remote run if available; if none remains NOT VERIFIED.
F03 HIGH: MT5 parent and research Drive use two distinct Drive connections. FIX: Routing map and boot validation; do not misclassify 404 from incorrect connector as missing research.
F04 MODERATE: v1.2 full recovery ZIP was frozen pre-deployment. FIX: Read post-deployment verified receipt first; preserve old ZIP unchanged, do not treat old 'unpublished' text as current state.
F05 MODERATE: 07/08 empty nested archive case folders exist alongside direct MT5 failed/success folders. FIX: Direct-MT5 destinations explicitly authoritative; nested empty shadow folders must not receive scored cases until user elects otherwise. Do not delete or move silently.
F06 MODERATE: Extra similarly named Report3 forensics variants co-located in primary workspace. FIX: quarantine, only previously approved exact Report3 links used; no auto authority promotion.
F07 KNOWN LIMIT: NO fully reproduced original chat transcript proven in Drive, only original report/code artifacts and chat-dependent handoff snapshot. Therefore any statement that every chat word is preserved would be false. New chat must consume true original documents.
F08 KNOWN LIMIT: Backtester supports broker-specific chronological quote replay but not complete portfolio-level signal routing/arbitration; governance validators are procedural and can be bypassed by direct CLI.
F09 KNOWN LIMIT: Aug–Sep Coinexx seasonal clock mapping extrapolated without paired Dukascopy data. Jan–Jul paired normalization evidence remains a prerequisite.
F10 KNOWN LIMIT: Remote GitHub Actions v1.2 branch reported 0 runs at QC start; a committed workflow is not a remote pass.

## Handoff release test
1. Confirm current QC GitHub branch HEAD and commit ancestry.
2. Confirm intended workflow text and whether current branch CI ran (document pending if none).
3. Confirm primary Drive CURRENT ENTRYPOINT is readable inside canonical handoff folder.
4. Confirm identical CURRENT ENTRYPOINT material is available in MT5_EXPAND 00_CANONICAL_INDEX_AND_PROVENANCE.
5. Confirm 16 source pins, main source folders, law stack, investor mandate, Report4 SYNTH distinction, two-account routing, original report references and researcher next step.
6. Verify neither original market data nor R9 source nor predecessor branches were overwritten.
7. If unresolved, mark gate CONDITIONAL instead of declaring unqualified complete.

## Status
QC/QA concerns documentation and research reproducibility, NOT a validated trading strategy. No scored research experiment is currently active by this review alone; the next build target remains the multi-signal bus and shared-account router, subject to explicit user direction.
