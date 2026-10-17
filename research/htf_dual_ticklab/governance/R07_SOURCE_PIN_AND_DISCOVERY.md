# R07: Exact experimental evidence and next causal development cycle

**Study:** `XAU-HTF-20261016-R07-QUOTE-FLOW-PATH-AUCTION`  
**Classification:** research-only / no investor-approved system / no live trading.

## Authoritative original evidence in MT5_EXPAND

- Complete original tick research and 240 trade-level scenario ledgers: https://drive.google.com/file/d/1Jk8ubgEPEK-xoRRh7nX51paQPVgPhQr9/view  
  **1,359,605 bytes; SHA-256** `aec1b65eb361eee76132c72954ec969be1759d6da2d67cdbb0fc01ef39ee6dd8`. 291 ZIP members including SHA-256 manifest. Upload independently read back and ZIP CRC verified.
- Derived quote-update microstructure from four exact raw market tapes: https://drive.google.com/file/d/1ydWR85gUcDhAuCorMTw9JXtmRGM3sVkr/view  
  **43,474,304 bytes; SHA-256** `8d48e122d2915784d59d4943fa97be265a650967815dbb85047ac82efec403ab`. Five ZIP members, full per-member manifest, readback and CRC verified.

Parent research GitHub R06: `c39db6fcd4682a346f5174323f3483bb32c117a5`. All original R05/R06 branches and canonical PRIMARY approved market sources remain unmodified. Broker source registry: Coinexx Jan `1307a75df5d635678de7691908600090a552f38543e0512187dcd7b37fbc66b8`, Feb `5de772aab4d15ebf18aa48850e847c98e2bcb639064790bbed9d87a598c3bf05`; Dukascopy Jan `d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5`, Feb `ed3b3545c990c88d78519594c17c8915b0f679adcb0a94920ba7524f1f6d5c5d`. Full compressed source bytes independently SHA-256 checked in R07.

## New reusable mechanism assets

- `htf_ticklab/quote_flow.py`: bid-only, ask-only, coordinated quote update, spread-compression and completed-second causal state. No fabricated order-book volume.
- `htf_ticklab/path_auction.py`: deterministic, uncertainty-penalized, broker-priced multi-specialist favorable/adverse path auction. Predictive values require calibrated historical evidence and independent survival/margin approval. **An interface and tests, not a trained profitable policy or a live engine.**
- `scripts/verify_r07_archives.py`: exact cloud archive SHA/per-member integrity/experiment contract verifier.
- Research archive includes feature builder from all 31,475,493 January-February ticks, 4,000 candidate grammar rows, 2,000 session cells, 144 native-tick funded account replays, 96 matched baseline-versus-new-exit funded replays, 240 individual trade ledgers, 2,591 UTC hour/day/week/month period rows, and full scripts/parameters.

## Constructive finding and measured limitation

The essential new variable is *trade-path opportunity versus captured executable profit*, not simply RSI threshold or isolated M1 strategy win rate. Among 7,884 Coinexx modeled trades, 57.18% had favorable quote-side movement above the modeled .17 USD/oz remaining closing-cost threshold, and 22.50% had such movement but closed with nonpositive net. Dukascopy: 3,850 trade instances, 39.77% and 12.39%, respectively. These are **hindsight path diagnostics and overlapping independent research simulations**, NOT attainable trade profit or statistical independence.

Three new price-floor and flow-reversal exit laws were compared against 24 full-account baseline configurations each on original 250ms modeled broker ticks. Improvement counts were 10/24, 9/24, and 8/24 with mean whole-account net changes of -$0.244, -$0.254 and -$0.392 respectively. No R07 candidate meets the combined mandatory profitable/high-throughput/$100-$200-survivable mandate; a gain in a narrow diagnostic is not a system advancement. Results use illustrative fees, leverage, slippage and loss brakes, not owner-approved monetary limits. R07 does not include 0/1000ms validation, all Jan-Jul, broker demo execution or full tick-equity paths. No investor or live certification.

## NEXT EXPERIMENT: R08 causal quote-path first-passage timing

Use R07's original recorded-tick MFE/MAE ledgers as historical outcomes and build separate causal predictors of (i) first arrival at executable after-cost profit before adverse stop, and (ii) conditional reversal hazard after entering profit territory. Jointly choose specialist entry type, stop, target, profit retention and rearm with broker-specific constraints while retaining a single funded shared account. Explicit bid/ask cost floors and 0/250/1000ms latency. Compare complete baseline S vs candidate S' over both brokers, $100/$200 and continuous months without future-event features. Preserve all positive and adverse regimes; no fabricated fills, pooled profits or high-volume success claims.

**GitHub CI passing tests verifies code contracts only, not runtime equivalence between the stand-alone native-tick Python experiment and new additive modules.**
