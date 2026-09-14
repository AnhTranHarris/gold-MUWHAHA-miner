# R3 Session Time Notes

MetaQuotes documents that during Strategy Tester runs `TimeLocal()`, `TimeTradeServer()`, and `TimeGMT()` all return the same simulated server/quote time. Therefore R3 must not assume `TimeGMT()` is real UTC in the tester.

R3 session classification uses the current quote timestamp plus a configurable `InpQuoteUtcOffsetMinutes` input. The default is 0 because the Coinexx historical archive used for the Python campaign and the corresponding tester reports align on the same timestamps.

London and New York DST are calculated from reconstructed UTC rather than relying on tester `TimeGMT()`.
