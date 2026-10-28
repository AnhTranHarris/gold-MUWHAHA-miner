# Reproduce R116-ACTION (unapproved)

Extract all delivery ZIPs into the same directory, retaining the research_r116/ prefix. Place existing approved original FILTER08 ZIP at sources/filter08_recovered.zip and four approved original DK CSV.GZ files under sources/. Preserve the unchanged engine modules under repo/research/htf_dual_ticklab/. Source pins are in SOURCE_CONTRACT.json; do not fetch substitute data. Python3.12, NumPy, pandas, Numba and LightGBM are required. No imported third-party strategy.

Run tests: `python -m unittest discover -s research_r116 -p 'test_*.py' -v`.
Feature caches are deliberately omitted; use a fresh reproduction directory with empty cache/results/models. Prepare each month: `python research_r116/run.py prepare --month 01` (then02,06,07). The saved models are authoritative; copying them into models/ permits frozen prediction without fitting. Use `fit --view full` or `fit --view ablation` only for a deliberately requested fresh reproduction in an empty model directory, not a new scientific result.

For each static view: predict01, calibrate once, score01; then predict and score02/06/07. Call syntax: `python research_r116/run.py predict --view full --month 01`; replace stage by calibrate (omitmonth) or score. Online: `python research_r116/online.py --month 01`, then02/06/07. Saved results must not be overwritten. Full package already includes all scores and decisions, so `python research_r116/verify_saved.py` can independently recount them without regeneration once original FILTER08 is supplied.

Models checkpoint every16rounds. Never mix code/plan hashes with a different run; no auto-refit on interrupted session. Main experiment is hypothetical never-submitted source-quote action exploration, not a live EA or originalR9 order replay. No deployment or owner signoff follows.
