# H1V2 R11 offline oracle frontier — explicitly future-privileged

Original H1V2 must remain intact. The separate \`r11_future_frontier.py\`
implements three distinct historical scheduling objectives (count, modeled
repriced net, net penalized by time-in-position). Each accepts optional original
strict first-hit constraints and original vs v5-shadow entry eligibility.
It never trains a causal predictor and its results cannot certify prospective
profitability. It also cannot correct net-first barrier labels for incremental
execution cost; extra-cost is a *post-hoc close-payoff sensitivity only*.

\`r11_frontier_runner.py\` loads original Dukascopy raw files and H1V2
binary label receipts, independently verifies original source SHA-256,
re-runs original quote candidate parity and original max-count scheduling,
then writes separate exact-ordinal R11 traces and detailed JSON receipts.

Original raw files and H1V2 labels are intentionally NOT in GitHub. To run:
\`\`\`bash
PYTHONPATH=research/h1v2_20261102/src:research/h1v2_r11_causal_entry_forensic_20261102/src \
python research/h1v2_r11_causal_entry_forensic_20261102/src/r11_frontier_runner.py \
 --month 01 --raw-root <verified-raw-root> --labels-root <verified-original-h1v2-results> \
 --out-root <new-immutable-r11-output> --contract v5_shadow --objective count
\`\`\`
No executed raw-month result has yet been established by adding this script.
The source parity requirement is mandatory before computing an R11 result.
