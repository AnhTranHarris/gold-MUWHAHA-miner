# F408-R01 — R00-054 causal event-hazard research (NEGATIVE)

**Executed 2026-10-25 America/Chicago / 2026-10-26 UTC. UNAPPROVED.** Source-exact scientific closeout in writable MT5_EXPAND/01: https://docs.google.com/document/d/1fVb6Np4CXTN6L1f4zbF0kwW2GUqH-krg_AUVGFr5qTs/edit

This additive research branch is based on the existing F385-S03 research checkpoint `6aec8d1b7f50e074619a4216aecfbaafd524de69`. No approved Coinexx/Dukascopy tick-replay engine or MT5 EA was modified. PRIMARY Google Drive remains READ ONLY; /02 owner-approved components remain untouched. Original FILTER08 fitted same-month teacher is NEVER a live input.

## Exact input and provenance

Input `F394_F395_EIGHTCELL_NATIVE_PATH_FROZEN_RESEARCH_UNAPPROVED_20261024.zip`, 29,336,863 bytes, SHA256 `a3367cba013912749cc31a6c7fde034dfb6546c4fd6a182d40d774414748e41d`. Original 2,574,251 R00 events across Jan/Feb/Jun/Jul × Coinexx/Dukascopy; original event index, t0 UTC millisecond, side, 30–32s 3-class diagnostic truth and frozen F395 veto preserved. 8/8 event mask member SHA and 8/8 output mask-score identity recounts PASS. Raw bid/ask tick tapes were NOT re-read/re-hashed in F408. This is an event-only research probe, not a quote-tape replay or executable trade test.

F395 original member SHA256:
- CX Jan `553e62f546a57c6b89daa75adf67b688179093a54b6b53b97c1457d4319cf5f2`; Feb `e46d6c72208a2ac842d551b02e3f77a1192f3b87d51b17e264cdb3e005fbe819`; Jun `d625fbf6c65eb801c625d0c2958c333382c5ac6a7e92bfbbcc7129569d440f14`; Jul `34fd6b8dae9cb0a2bda94febefb300dbb44f76c8f80de55de5135eb804088349`.
- DK Jan `cb528259ec0a03e7d68bb5eb9a025f84facaf44681b9bd27b943de847a986436`; Feb `e69c2c621b4defe643ed6094ab692b4bb4987c16c08cc8cac1708934340099da`; Jun `59bb1cb013f92fbbeb97d8ea7e0ebe49c5979991865638c5bbf5063b09d75c7b`; Jul `2f5c68cfe25f43ff0f7569e812bd1502ab08edf6453e9333168dce811deda51c`.

## Mechanism, chronological controls and tests

77 original-t0 event-only features: historical R00 event-arrival counts (NOT raw quote intensity or OFI), side-switch and imbalance, past 33,002ms-matured same/opposite-side correct/opposite/neutral hazard, UTC session phase and short/long regime jump. Overlaps prior F396/F403 event-history features; **incremental novelty is not established**. No genuine price HTF completed bars, native bid/ask quote-intensity, fitted teacher, current label or post-t0 quote in inference. Four synthetic causal invariance classes PASS. A real EA would require a separate restart-stable historical label streamer, which is NOT built.

Two independent LightGBM 3-class models, 127 leaves × 75 fixed rounds, seed 408, deterministic 100,000-row cap per broker. Chronological FIT: Jan first 80% and Feb first 60% with 40s embargo. CAL Feb 60–80%; VAL Feb 80–100%. Frozen CAL q=.71 correct-risk cutoffs: CX `0.5394577919516697`; DK `0.5919803108792839`. June/July assessed only as **historically exposed** transfer, not virgin OOS. Models TXT SHA256: CX `8ed7d10e44df48ad0514d471ae96d68af5fde8c37111f155692f77d30f20b2fd`; DK `b041cc29ab89daa66c8f6f0a8862031121e5572717987a2e61e6449109421750`.

## Frozen full original-event results

| Source | Correct retained | Wrong+neutral rejected | Kept precision |
| --- | ---: | ---: | ---: |
| CX Jan | 160,902/181,869 (88.47%) | 37,611/163,496 (23.00%) | 56.11% |
| CX Feb | 126,867/155,538 (81.57%) | 46,175/173,341 (26.64%) | 49.94% |
| CX Jun | 109,880/142,224 (77.26%) | 41,403/169,780 (24.39%) | 46.12% |
| CX Jul | 100,158/143,362 (69.86%) | 58,219/177,707 (32.76%) | 45.60% |
| DK Jan | 168,948/178,642 (94.57%) | 21,211/165,395 (12.82%) | 53.95% |
| DK Feb | 121,299/143,923 (84.28%) | 44,419/180,659 (24.59%) | 47.10% |
| DK Jun | 93,753/132,105 (70.97%) | 54,877/164,930 (33.27%) | 46.00% |
| DK Jul | 80,883/130,408 (62.02%) | 73,943/170,872 (43.27%) | 45.49% |

Feb CAL/VAL wrong rejection: CX 30.91%/27.45%; DK 36.72%/25.83%. Incremental wrong:correct veto against frozen F395 surviving source events: CX Jun 27,698:32,033, Jul 40,655:42,865; DK Jun 39,073:37,998, Jul 54,967:49,003. No 20:1 asymmetry. 90% original-event correct-retention hour/day proxy failures: CX Jun 392/26, Jul 473/28; DK Jun 386/26, Jul 460/27. **This proxy is NOT the source-matched R9 SYNTH 4,178 reference floor.** The exact R9 quota rows were absent; no hourly/day source floor certification is claimed.

**Result: FAIL.** All exposed cells fall well below 90% wrong rejection; CX Jul and DK Jun/Jul also fail 71% correct retention. No material improvement, no blind generalization, no owner acceptance, no live PnL or MQL5 parity. Original F395 owner-approved research atom unchanged. All G01–G09 whole-EA gates open.

## Archive / recovery

Complete 20-member local research archive (source, tests, two model TXT weights, eight full aligned NPZ scores/masks, stdout, JSON negative/positive register, source hashes): `F408_R01_EIGHTCELL_T0_EVENT_HAZARD_NEGATIVE_CODE_MODELS_MASKS_20261025.zip`, **23,772,720 bytes, SHA256 `acf4dabe0cd45ab9c2a067446c1cdbaee4947d6bde54770e12ceb79dfeecfeaa`**; ZIP CRC and 19/19 member hashes PASS. The binary archive was not uploaded: MT5_EXPAND upload attempt returned `container_session_unavailable`. Do not invent a cloud ZIP link. The full negative scientific receipt is cloud-durable in MT5_EXPAND/01; source Python files here match local Git blob SHA exactly. To regenerate outputs, place the pinned F395 ZIP next to this `experiments` directory, run `python test_f408.py`, `python f408_run.py`, `python verify_f408.py`.

Next safe direction: recover registered original quote tapes and F401/F402/F406 native features for a genuinely different completed-HTF/quote-intensity competing-risk test; maintain original t0 and side, CAL-only policy freeze, and exact 4,178 R9 reference checks. Do not continue F408 event-only threshold tuning.
