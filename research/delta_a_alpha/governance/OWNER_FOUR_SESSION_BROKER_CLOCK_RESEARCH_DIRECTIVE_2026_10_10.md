# Owner directive — broker aligned four-session whole V1 cycle — 2026-10-10

## Human owner instruction (verbatim)

that is okay please start your reaserch over with session and proceed wiht the remaining layers.session two clocks has the added benefits of the system self aligning to broker clock so that the rest of the system can alaign properly, i included that that since in previous chat you kpet complain the coinexx utc clock differes from dukascopy utc clock. this way the system will auto adjust easily to any broker clocks.  which in turn help the session clocks auto align so that the system is not off by an hour or more.  with that in mind your reaserch should have 4 best possible system for each layer one for each session so this way the system will be session aware as you do your research cycle for each layer.

## Operational clarification

UTC remains the canonical time for executable Dukascopy and MT5 Python ticks (as confirmed by the MQL5 copy_ticks_from documentation). MT5 chart/server time is a separate date/time presentation, not a second authoritative event-time clock. Preserve UTC plus a broker-server offset mapping plus Australia/Sydney, Asia/Tokyo, Europe/London and America/New_York IANA civil clocks. Determine live broker offset only from independent trustworthy UTC + contemporaneous broker clock observations, monitor DST and drift, and fail closed when confidence is insufficient; never silently change correct UTC timestamps based on a historical tester's simulated GMT. MT5 quote/trade sessions are independent broker-time schedules and need actual broker metadata.

The four session profiles are research hypotheses until they demonstrate better economic performance; none qualifies as a separate funded trading algorithm. Each of L1–L7 is session-conditioned but still shares one vertical system, one globally funded L7, no session-only trades, no MTF-only trades. London/NY and Sydney/Tokyo overlaps are contextual intersections rather than new independent strategies. Maintain the original owner's raw Dukascopy and R9 Gamma HybridGate SYNTH/REAL protection.

This owner directive authorized J0101 clean-room code, session re-research and whole-funnel tests. Negative results cannot be concealed, and winning profitability or the daily R9 75% opportunity floor cannot be claimed from incomplete time windows.

Research cycle source: https://github.com/AnhTranHarris/gold-MUWHAHA-miner/blob/delta-A-alpha/research/delta_a_alpha/state_journal/0101_CLEAN_V1_FOUR_SESSION_BROKER_CLOCK_FULL_SPINE_RESEARCH_CYCLE003.json
Evidence package: https://drive.google.com/file/d/1B7Z4nXr5rQzyURIMMtbzhUpXLOzbbBi1/view
