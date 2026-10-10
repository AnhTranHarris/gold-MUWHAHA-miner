# Delta-A-alpha CLEAN V1 — cycle 001

**One clean vertical program, not the deleted Jan/Feb engine.**

- [Python context core](v1_vertical_grid.py): L0 ordered Bid/Ask ticks, L1 UTC + Sydney/Tokyo/London/NY civil session clocks with separate overlaps, and completed H4/H1/M15/M5 bars.
- [Seven deterministic contracts](test_v1_vertical_grid.py): passed in local Python 3.11.
- [Machine research checkpoint](../state_journal/0099_CLEAN_V1_L1_SESSION_FIRST_RESEARCH_CYCLE001.json).
- [Exact zipped source, tests, raw-tick experimental code and complete results](https://drive.google.com/file/d/16Lb-eus4mPvMJwxngEHds71wU1ufQJax/view).

**L3/L4/L5/L6 trading behavior and L7 execution remain UNIMPLEMENTED/FAIL-CLOSED; this is NOT a profitable or deployable engine.** The source's proposed desk clocks are research approximations, not verified Coinexx trading-session hours. All 16,673,401 raw Jan/Feb Dukascopy quotes were used strictly as *new market inputs* for the three new context-screen hypotheses (no older derived mechanism or result reused). January/February derived research removed under Journal 0098 stays invalid. Raw Dukascopy and R9 SYNTH protected.

Highest first **research priority: L1** session intelligence with integrated L0 time root, L2 completed structure, L3 opportunity measurement, and L7 cost/risk envelope in the same machine. No single-EMA universal trading filter.

Owner original V1 whitepaper and full conversation remain higher authority; every five human prompts re-read entire governing conversation.
