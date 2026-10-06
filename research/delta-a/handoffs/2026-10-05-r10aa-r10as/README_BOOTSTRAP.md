# DELTA-A R10AA-R10AS Breakthrough Handoff — 2026-10-05

This archive exists to prevent a Gamma-style reconstruction failure after chat-length/time-limit errors.

## Authority
- GitHub branch: `delta-A`
- Snapshot branch to be created from the committed handoff state: `delta-A-r10aa-r10as-breakthrough-handoff-20261005`
- Main `delta` branch remains untouched.
- August 2026 remains SEALED.
- Production MQL5 remains NOT AUTHORIZED.

## Current promoted research parent
Use as the next supermodel core:

`R10AA -> R10AB -> R10AG SEQ45_60 -> R10AH`

Do **not** replace this with R10AI from $100. R10AI improves net/GL but lowers minimum equity; test it behind a capital gate.

## Key stack economics (January research replay)
- R10AB: +$4,470.41 net; physical GL -$11,566.18; episode GL -$9,300.01; tick min equity $87.17; executed success 60.04%.
- + R10AG SEQ45_60: +$4,700.42; physical GL -$10,482.89; episode GL -$8,244.58; tick min equity $99.51.
- + R10AH: +$4,824.61; physical GL -$10,383.63; episode GL -$8,125.21; tick min equity $99.51; executed success 61.15%.
- + R10AI ungated: +$4,969.73; physical GL -$10,321.74; episode GL -$7,975.16; tick min equity $81.37; executed success 61.47%.

## Immediate next work
1. Capital-gate R10AI at $150/$175/$200/$250/$300; prefer a gate preserving the AG+AH ~ $100 floor.
2. Forensic the ~ $203 max tick-DD episode in AG+AH and create a specialist only for that path.
3. After loss/DD stabilization, test R10AP as a capital-gated velocity desk; R10AR remains a second velocity desk candidate.
4. Preserve virtual pre-warm from $100.
5. Continue January R9-SYNTH parity objective: trade count, net, gross loss and true DD simultaneously; do not optimize survival alone.

## Helper policy
Every helper/artifact in `files/` is immutable evidence for this handoff. Use `MANIFEST.json` SHA-256 values to verify copies. An incomplete helper must be rerun from scratch; never resume partial state.