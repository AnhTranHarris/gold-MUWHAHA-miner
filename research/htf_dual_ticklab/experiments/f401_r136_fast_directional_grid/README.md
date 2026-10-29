# F401-R136 six-clock directional fast-grid — UNAPPROVED
Owner objective: aggressively reject incorrect and neutral, protect original correct under a hard loss budget. No symmetric classifier or M1/M5/M15/H1 decision clock.

Both independent registered Coinexx and Dukascopy original ticklog feeds, January/February/June/July, source SHA independently checked. Original 2,574,251 event indices/t0/side/truth/F392 masks preserved. Coinexx UTC offsets JanFeb -120min, JunJul -180min. No dual replay engine rebuilt.

Only 250ms, 500ms, 1s, 5s, 15s, 30s native subminute clocks: side-specific EMA/ATR/ADX-DI/Bollinger/AMA approximations, quote intensity, nonlinear grid/SR/volatility geometry and directional signed interactions.

New never-submitted order-intention clock d=t0+15sec. At d, last prior broker quote must be fresh <=300ms; indicative BUY ask entry/bid exit, SELL bid entry/ask exit; first +$1 favorable, first -$1 adverse, otherwise neutral/censored over next 30sec. These are NOT immutable original t0 labels or fills.

Trained separate favorable-protection, adverse-first, neutral-first heads on Jan early+Feb early, Feb late CAL, frozen JunJul historical transfer. Later: DK Jun 3390 bad/89 favorable; DK Jul 6109/113; CX Jun 2741/107; CX Jul 7624/310. TOTAL NEW action-time 19,864 bad/619 favorable (32.1:1), but evaluating SAME predicted vetoes against ORIGINAL t0 gives only 12,193 original bad /8,290 original correct (1.47:1). Thus NOT high-capacity FILTER08 replacement or live result. Both July favorable loss rates exceed Feb CAL target.

Preserved negative tests of 24-state and full 92+18D original-correct rescue. Original privileged F392 399,049 bad /9,404 good and R133 406,447/9,931 remain historical-only.

Full executable Python, MQL5 research-only fast-grid publisher, eight original-event-aligned masks, six action-time fitted heads, input and feature hashes, tests are archived in MT5_EXPAND /01:
https://drive.google.com/file/d/1nho1ylxr_a9g7WNp4OrKnK8MqeX2GB5r/view
ZIP SHA256 1653ba6dbb40fe20eca17014567d6076550417924c2f0d43e6bfa041c95d8e48; 35,498,410 bytes; 51 ZIP members; CRC + 50 member SHA PASS; Drive re-downloaded SHA verified.
Scientific MT5_EXPAND /00: https://docs.google.com/document/d/14xyZD_J4BbWjeBCC1dCxZk-Hwr4lMtm5qw5DxeItfd4/edit

R137: improve 6-clock direction-conditioned first-passage/Hawkes and semi-Markov change point, broker-specific opposite+neutral hunter, original correct guardian with hard per-cell budget and optional sequential observe/reprice. No MQL5 native compile or numeric parity, G08 untouched time or G09 after-cost validation performed. /02 untouched; M-DK-01, G01–G09 OPEN.
GitHub branch preserves lineage and source receipts. Full executable source resides in verified /01 ZIP, not this README.