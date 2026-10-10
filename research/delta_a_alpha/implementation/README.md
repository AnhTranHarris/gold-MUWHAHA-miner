# Delta-A-alpha V1 — CLEAN four-session research prototype, cycle003

Single vertical research route under `v1_four_session_architecture.py`; imports ONLY the cleaned original `v1_vertical_grid.py` and `v1_session_broker_clock.py` (new). Four desk-specific L1–L7 quality/participation profiles; actual overlapping desks share one physical capital governor. No session or timeframe alone can authorize a position.

UTC-authoritative tick path, independently calibrated broker-server wall offset, and IANA Sydney/Tokyo/London/New York local clocks. Broker mapping requires at least 3 paired trusted UTC observations and fails closed on stale/discontinuous offsets; offline MT5 tester UTC cannot independently identify historical broker DST. Tested code is illustrative; live brokerage clock/lot/margin/latency not available.

## Files

- `v1_vertical_grid.py`: prior clean UTC tick/root/completed HTF context
- `v1_session_broker_clock.py`: paired UTC↔broker server offset, DST, stale rejection
- `v1_four_session_architecture.py`: one owner L0–L7 whole-funnel prototype (not production ready)
- `test_v1_four_session.py`: 18 locally passed tests
- `research_cycle003_sessions.py`: full original JAN/FEB 16,673,401 quote window research
- `run_cycle003_integrated_replay.py`: six representative partial-quote, hypothetical-margin delayed Bid/Ask research runs

## Honest status

**Not profitable, not MT5-certified, not ready for deployment.** Early $300 research slices lost heavily in January; February generated very few fills. The 75% original R9 Gamma HybridGate SYNTH daily qualified-opportunity floor is not demonstrated; actual broker contract and latency unknown. No system/profile is proven best. Raw Dukascopy data and original R9 SYNTH/REAL are untouched, prior contaminated source variants excluded.

[Complete detailed report](../research_cycles/cycle003/CYCLE003_FOUR_SESSION_WHITEPAPER_RESEARCH_REPORT.md) · [Journal 0101](../state_journal/0101_CLEAN_V1_FOUR_SESSION_BROKER_CLOCK_FULL_SPINE_RESEARCH_CYCLE003.json) · [Full ZIP source and results](https://drive.google.com/file/d/1B7Z4nXr5rQzyURIMMtbzhUpXLOzbbBi1/view?usp=drivesdk)
