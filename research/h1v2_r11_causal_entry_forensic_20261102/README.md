# H1V2 R11 — isolated causal entry forensics (NOT a trading EA)

This additive research directory is attached to Git branch
\`carson/h1v2-r11-causal-entry-forensic-remediation-20261102\`,
based exactly on H1V2 R10 a22218b14ed387ecc0dea9ba8d867cd33c4b4ee7.
It changes NONE of the historical H1V2 R0–R10 or R9 v2 production source.

**Full audit:** https://docs.google.com/document/d/1wF8VFJJOiT3rhyABfLb3DTFsQ_b6ln8WZHxmRakRcXI/edit
**Full falsification hypotheses:** https://docs.google.com/document/d/1gWzTfqwkZmbtaMw7kilI8JS6Vc8rpnOtEsVp3C7gEkM/edit
**Append-only recovery journal:** https://docs.google.com/document/d/1WOLjboMzmc729xl0NWQsjiEYlqKJ2ZRlwg7v7pPW1nk/edit

## Mechanisms implemented in this additive source-only checkpoint
- \`r11_entry_admission.py\`: independently evaluates original H1V2 first-observed-250ms/300s-reset and **v5 shadow** >15s-reset/300s warmup. It DOES NOT yet certify every internal v5 production admission criterion. Fail on original H1V2 parity mismatch.
- \`r11_quote_marks.py\`: exposes mixed Bid-up/Ask-down and Bid-down/Ask-up marks, explicit quote-gap epoch, preserved same-ms ordinal, and physically timed causal prefix reference features.
- \`r11_policy.py\`: independent BUY/SELL chronological-calibration/strict-class/expected-net/tail/support admission BEFORE utility comparison. No trained data provided means WAIT.
- \`tests/test_r11_source_contract.py\`: synthetic adversarial prefix/gap/mixed-mark and action-gate tests. They test source invariants, not financial profit.

## Unresolved scientific requirements
1. Recover and verify exact archived R8 source and original R9/h1v2 raw artifacts; revalidate CRC and SHA. No raw full-month replay claimed by this checkpoint.
2. Original H1V2 baseline candidate parity on pinned monthly raw source; v5 full runtime/offline parity is NOT proven by gap mirror.
3. Efficient full-population streaming implementation for quote-mark state: \`observed_prefix_state\` is intentionally a reference implementation, not an HFT throughput solution.
4. Fit and qualify separately genuinely causal competing event hazards and observed WAIT value; do not confuse oracle schedule with online learnability.
5. Perform source-exact chronological frozen training, cross-source/month test, one-position replay, account survival, slippage/latency and original strict throughput.
6. No MQL5 compilation, no demo authorization, no live-trading approval or profit statement.

Research invocation (after editable source checkout):
\`\`\`bash
PYTHONPATH=research/h1v2_r11_causal_entry_forensic_20261102/src \
python -m pytest -q research/h1v2_r11_causal_entry_forensic_20261102/tests/test_r11_source_contract.py
\`\`\`
