# V2 F1 timeout recovery and zero-mutation source audit — 2026-10-15

**Disposition:** RESUMABLE RESEARCH CHECKPOINT, UNPROMOTED. This document audits existing bytes and tests; it does not advance science or improve profitability. Owner original V1 January governance and 60%-of-R9 hourly/daily cash/velocity promotion gate remain binding.

## What survived the failed UI delivery

- The screenshot says **“Message delivery timed out”**, following two truncated ZIP attachment cards labeled `V2_F1_JAN2026_INTEGRATED_1921_...`. UI delivery status alone is not a filesystem/GitHub mutation indicator. The **exact identity and redundancy of both UI attachment cards have not been established**; a verified single canonical complete Drive archive is available.
- GitHub working research branch `v2-f1-january-research`: original verified head before this recovery note **`910535d9f038cf6e0d36b07ad602b5dacd2b3a26`**, 8 additive commits vs untouched `delta-A-alpha` baseline head `53547d519cb4781e05581e142f105a34d9351288`. Compare API shows `8 added / 0 modified / 0 deleted existing paths`.
- V2 source lives in `research/delta_a_alpha/implementation/v2_f1/`: README, six .py test/engine/audit source files, and a separate V2 publication provenance Markdown. All 7 original README/Python archive blobs exactly match GitHub source blobs. `V2_PUBLICATION_PROVENANCE.md` lives separately on GitHub and Drive (not in the 55-member ZIP), so retain it as a required companion rather than call archive self-contained for publication metadata.
- Full canonical protected January Drive ZIP https://drive.google.com/file/d/1oDoDjPefjreY_cH60vDkIJ5FVeYxHmep/view . **SHA256 `6936f3b0845fc2fe6f2a8f944657e67815c3f45653531e54e9b0a96ab8e2514f`**, **452024 bytes**, ZIP CRC test passed, 55 members, all **54 payload entries match byte counts and SHA256 in the internal manifest**. Cloud published manifest https://drive.google.com/file/d/1zIiDrTWTodn_8wrIIKv6kp5TYujucNNk/view is byte-identical to member `V2_F1_ARCHIVE_MANIFEST.json`.
- Original raw January Dukascopy 9,135,062 quote feed **SHA256 `d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5`** verified directly this recovery turn; no change or replacement.
- Original V1 branch is still `delta-A-alpha`, official `CURRENT_STATE.json` latest_scientific_sequence `183` and `engine.trading_enabled=false`. Four checked core paths have **identical Git blobs on both branches**: `CURRENT_STATE.json` blob `81bdeaf0ccf2a3cb8bbc31b82ae192fec02c5f9e`, original `v1_four_session_architecture.py` `64b75c39c41ff8ccd0d0e8b02e45bdf5b9ca54e2`, `v1_vertical_grid.py` `85e7d55944a3a1fd4e12d244c466210f6a0c4a22`, cumulative adapter `43a8bf139c7b14163f4f5b75af09ddda57c58926`.

## Independently rerun after the timeout

- `python -m unittest discover -p 'test*.py' -v` on extracted V2 source: **5/5 PASS**.
- `python v2_original_feed_stream_parity_qa.py`: 180000 actual original Bid/Ask quotes; **206495 completed M1/M5/M15/H1/H4 comparisons; 41275 S1-quality comparisons; zero discrepancies**.
- `python v2_source_and_r9_audit.py`: all 9,135,062 January original quote rows referenced; **27/27 native-control funded entry and exit pairs exact**, original Bid/Ask prices, 250ms minimum first eligible quote, cash and single-slot chronology; zero errors. **0 of 480 R9 trade-active hours and 0 of 21 R9 trade-active tester-days** meet 60% R9 cash or funded velocity, with UTC+2 source alignment explicitly unverified.
- All 4 freshly recomputed outputs (2 JSON QA and 744-hour / 31-day CSVs) are **byte-for-byte identical to original ZIP**, not just numerically similar. Exact SHA256 in machine JSON companion.
- 1921 trial rows present with unique IDs? Full 0..1920 range; original `V2_JAN2026_INTEGRATED_QA.json`: **zero cases reaching 60% R9 monthly net or throughput**; best no-halt case actually traded **zero positions** and generated **zero profit**, so no spurious success. Native accelerated control -$41.126, 27 closed trades, halt triggered. Separate 12 high-capital throughput runs are *not* $100 investor simulations.

## Safe restart contract

1. **Do not delete, replace, or reset** the original immutable V1 or V2 GitHub branches or raw original data. Continue from V2 Git commit `910535d9f038cf6e0d36b07ad602b5dacd2b3a26` plus this additive QA note, not from the interrupted answer text.
2. Validate source SHA and 54-file manifest before any optimization. Preserve source graphs, failed trials, QA, the source archive and publication provenance. Remote Drive folder for readable source modules: https://drive.google.com/drive/folders/1G7-vrkhbfA4AzMsM4eQsu_cFjkP1r4ic .
3. V2 is a **new standalone integrated research chassis**, not yet fully parity-integrated with all old `FourSessionV1` native subgrid/source genealogies or broker's MT5 stop, freeze, margin and transaction mechanics. Do not claim full original V1 rollover or real broker parity.
4. Next safe task: complete source-by-source parity of old original native V1 grid producers and paid-close chronology into V2 G0-L7; rerun January $100 fully funded physical-account scenarios against real Dukascopy quotes, comparing all 744 H1 and 31 tester-aligned days, preserve the original R9 synthetic benchmark and strict 60% gate. No MQL5/live, no later months, August SEALED.

**Result:** Timeout damaged the *message delivery*, not the 55-member preserved research package or the inspected GitHub source lineage. No scientific success or profitability was certified by this recovery.
