# DELTA R037 — Donchian Confirmed-Close Breakout Stage-A Screen — Checkpoint 17B

**Status:** COMPLETE / NO SCREEN SURVIVOR / FAMILY RETIRED
**Unit:** R037_NEXT_INDEPENDENT_ENTRY_SOURCE_HARVEST
**Family:** R037-DCB-v1
**Parent:** R037_VCE_STAGE_A_SCREEN_CHECKPOINT_17A
**Surface:** DUKAS_COINEXX_LIKE_P75 / Stage-A
**August:** SEALED
**MQL5:** NOT AUTHORIZED

## Timeout-safe recovery

This unit resumed from the already committed DCB preregistration and producer after repeated ChatGPT message-delivery timeouts. Before compute, the live branch, CURRENT_STATE, CURRENT_INFLIGHT and timeout recovery pointer were reconciled. No prior DCB result/report/manifest existed, so the producer was run exactly once.

The official local execution used the GitHub Actions recovery snapshot from run 37173833277 at branch commit 24a51ec00ba2751e871982b13024deebf59933cc. The DCB producer SHA-256 matched the frozen pointer exactly:

`e1440f9d68e47cef3ee7820f85ef502e7eb3e9651fbdc00af51293c71b95d6da`

Canonical January source SHA-256:

`d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5`

Stage-A ticks: **4,205,709**.

The bounded runner exited **0** in approximately **30 seconds**. Official local raw result SHA-256:

`31aed2ce69af15cfb7c7e77c1dce639d5e4ae40a05f038aac775ff6be80ceb11`

## Frozen basket

- C01: M1 close beyond previous 20 completed-bar Donchian channel.
- C02: C01 plus EMA200 directional filter.
- C03: M5 close beyond previous 20 completed-bar Donchian channel.
- C04: C03 plus EMA200 directional filter.

All use the frozen parent-priority scheduler, <=25-point spread gate, 0.01 lot, $0.30 stop, +$0.10 trail arm, $0.03 trail and 30-second max hold. No threshold/lookback retuning, session slicing, direction splitting or post-result merge was permitted.

## Results

Parent control: **14,034 trades / 6,349 official wins / -$2,944.94 net / $2,946.43 max equity DD**.

- **C01 M1 Donchian20:** 1,898 proposals, 1,799 accepted entries, +1,753 combined trades, +870 official wins, **-$311.22 net delta**, direct DCB net **-$328.92**, max-equity-DD deterioration **+10.53%**.
- **C02 M1 Donchian20 + EMA200:** 1,496 source-eligible, 1,421 accepted, +1,387 trades, +697 wins, **-$241.65 net delta**, direct DCB net **-$260.26**, DD deterioration **+8.19%**.
- **C03 M5 Donchian20:** 318 proposals, 309 accepted, +308 trades, +162 wins, **-$46.03 net delta**, direct DCB net **-$48.28**, DD deterioration **+1.56%**.
- **C04 M5 Donchian20 + EMA200:** 242 source-eligible, 235 accepted, +235 trades, +121 wins, **-$38.14 net delta**, direct DCB net **-$35.02**, DD deterioration **+1.29%**.

## Interpretation

DCB solved opportunity density but failed quality. The family produced abundant incremental entries and official wins, yet every preregistered configuration increased gross loss enough to overwhelm its gross-profit contribution. The EMA200 filter reduced damage but did not change the sign of the edge.

This is therefore a useful negative result: **simple confirmed-close Donchian continuation is not compatible with the current 30-second initial-hold economics on the Stage-A P75 surface.**

No posthoc Donchian lookback, timeframe, long/short, session or exit retuning is authorized from this result.

## Decision

**Checkpoint 17B = NO SCREEN SURVIVOR. RETIRE R037-DCB-v1 FROM THE ACTIVE PROMOTION PATH.**

Preserve as forensic evidence that high-density trend breakouts can add winning trades while still worsening aggregate loss/DD.

## Next

`R037_NEXT_INDEPENDENT_ENTRY_SOURCE_HARVEST`

The next family must remain structurally independent of:
- session opening ranges,
- previous-day sweep/reclaim,
- volatility-compression release,
- simple Donchian confirmed-close continuation.

August remains sealed and MQL5 remains unauthorized.
