# F401 R148B three-feed source-exact real-tick signal classification — 2026-10-30

**UNAPPROVED research; frozen R148B and R24 unchanged. No main merge or trading orders.** This is a filter replay on original R00 5s hypothetical still-unfilled intents, not actual R9 fills or account profitability.

## Source-exact frozen test results (zero teacher/oracle inference)

| Metric | Coinexx May | Dukascopy May | Coinexx Aug |
|---|---:|---:|---:|
| Original source candidates | 345324 | 343395 | 347256 |
| Real t0+15 eligible quote decisions | 330465 | 298809 | 326560 |
| Abstained | 14859 | 44586 | 20696 |
| R148B opposite vetoed | 66463 | 67325 | 67662 |
| R148B neutral vetoed | 7436 | 10981 | 8545 |
| R148B bad vetoed | 73899 | 78306 | 76207 |
| R148B correct lost | 14097 | 17422 | 14423 |
| R148B correct released (eligible only) | 137819 | 116671 | 132864 |
| R24 bad vetoed | 73875 | 78280 | 76183 |
| R24 correct lost | 14090 | 17409 | 14409 |

Combined **1,035,975** original candidate signals; **955,834** eligible, **80,141** abstain. R148B **228,412 BAD veto / 45,942 CORRECT lost** vs R24 **228,338 BAD / 45,908 CORRECT lost** = only **+74 BAD / +34 CORRECT lost** marginal.

**Critical failure:** matured-correct risk monitor gates R148 overrides off on 329653/330465 Coinexx May, 298198/298809 Dukascopy May, 325930/326560 Coinexx Aug eligible decisions. Therefore these results are functionally dominated by frozen R24, not a genuinely active R148 improvement.

All quotes from real native broker/source ticks; R00 original t0/side/class labelled from original +30..32 window and used only for offline retrospective evaluation. R15 68D native as-of, R17 completed HTF, R120 92D/R147 153D, R24 65D matured and R148B frozen models. August 0 mismatched R24 masks vs frozen R25; 4/4 R148B contract tests pass.

## Complete reproducible evidence in MT5_EXPAND

- /00 detailed scientific report: https://drive.google.com/file/d/1wUEpun5HlwGPnLm_MJyAJbTnT0AZv8ia/view
- /01 **source scripts**, original event identity/time/side/truth decision masks, exact counts, source hashes, logs and readback zip: https://drive.google.com/file/d/1m8YdyKHAISnfGUC82hbEaUF4fhe1amNQ/view
- evidence ZIP 9,786,766 bytes SHA256 `4fc6e3fb44e9f0a69599b604036dc3929a323f021c6a5031a0e65109d5771563`; cloud download exact hash readback PASS.
- original frozen R148B ZIP SHA256 `5fd66ba3394b66160f0a951fbfd1a743b2511c4a164b5f947f8e10b95fb67554`.

The source programs and model weights exist in the complete Drive evidence/original pinned archives. This repo commit is a provenance receipt; no source model or baseline decision has been changed. May/Aug have been research-exposed; **not** new G08 promotion evidence. M-DK-01 and G01–G09 OPEN; /02 untouched.