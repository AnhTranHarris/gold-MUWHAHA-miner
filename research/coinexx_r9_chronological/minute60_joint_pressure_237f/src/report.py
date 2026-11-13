"""Generate scientific training summary without inventing AUC or execution metrics."""
import json,hashlib,zipfile
from pathlib import Path
R=Path('/mnt/data/r9_m60_joint_20261113');summary=json.loads((R/'results/SUMMARY.json').read_text());agg=summary['aggregates'];folds=summary['results']
names=['frozen_155','frozen_182_append','capacity_182','synergy_joint','original_side_specialist','fixed_half_joint_specialist','fixed_half_frozen_synergy']
labels={
 'frozen_155':'Frozen 155 baseline',
 'frozen_182_append':'Previous 182 append-only',
 'capacity_182':'Expanded 182 capacity (control)',
 'synergy_joint':'All 182 + 55 explicit interaction features',
 'original_side_specialist':'237-feature original-R9-direction specialist',
 'fixed_half_joint_specialist':'Fixed 50/50 synergy+specialist',
 'fixed_half_frozen_synergy':'Fixed 50/50 baseline+synergy'}
lines=[
'# R9 M60 — January–September aggressive joint-training audit',
'', '**Classification: RETROSPECTIVE RESEARCH ONLY. No MT5 EA promotion, no original-direction 0.75 gate pass, no 0.80 breakthrough.**',
'', '## Owner question and fixed experiment',
'', 'Can previously constructed QRB/QAF, event-time trend, CUSUM, signed quote-intensity, analytical first-passage, marked-Hawkes-inspired excitation, latent-pressure estimates, and quoted-spread-resilience proxies predict R9 five-second favorable-first events more accurately when jointly trained, rather than merely appended?',
'', '- Original Coinexx XAUUSD source: 72,129,347 quote rows, Jan–Sep 2026; **303,934 original R9 entry decisions**.',
 '- Both hypothetical sides at each R9 decision: 607,868 action records; 120 censored across nine months, resulting in 607,748 uncensored actions for final pooled training.',
 '- Five chronological expanding folds: Jan–Apr→May; Jan–May→June; Jan–June→July; Jan–July→August; Jan–August→September. Entire held-out month scored (except frozen censor handling).',
 '- Historical feature schema: original 155-feature direct 5s binary classifier, full 27 price-derived quote-only proxies (182), **55 predeclared cross-family features (237)**, including pressure consensus, disagreements, trend × Hawkes × pressure, QAF × quote-excitation, CUSUM × spread response, and analytical barrier interactions.',
 '- Additional capacity-only control (182 features, identical hyperparameters) isolates the value of explicit interaction terms from simply increasing tree capacity.',
 '- Original-direction-only specialist and frozen 50/50 blends test whether training on R9 action side gives better discrimination without changing decision moments.',
 '- Fixed joint LightGBM settings: binary loss, 160 boosting trees, learning rate .04, max 23 leaves, min leaf 220, lambda L2=24, L1=3, max bins 63, seed 20261113. No per-month parameter optimization or target tuning in this experiment.',
 '- Causal features use original source-ordinal quote prices and timestamps. Undefined histories remain NaN in base features; neutral cross products carry an explicit missing-60s flag. The feature generator never accesses future labels.',
 '- **All evaluated months have been exposed in prior R9 research; this is NOT independent, fresh, prospective OOS certification.**',
 '', '## Full evaluation — five-second ROC-AUC', '',
 '| Evaluation month | Frozen 155 pooled | Expanded 182 pooled | Synergy 237 pooled | Frozen R9 side | Expanded 182 R9 side | Synergy 237 R9 side |',
 '|---|---:|---:|---:|---:|---:|---:|'
]
for f in folds:
 mm=f['evaluation_month'];m=f['models']
 lines.append(f'| {mm} | {m["frozen_155"]["pooled_auc"]:.6f} | {m["capacity_182"]["pooled_auc"]:.6f} | {m["synergy_joint"]["pooled_auc"]:.6f} | {m["frozen_155"]["r9_direction_auc"]:.6f} | {m["capacity_182"]["r9_direction_auc"]:.6f} | {m["synergy_joint"]["r9_direction_auc"]:.6f} |')
lines +=['', '## Five-month mean comparison', '', '| Model | Pooled 5s AUC | Original R9 direction AUC | Original direction AP | Original R9 months ≥0.75 |','|---|---:|---:|---:|---|']
for n in names:
 d=agg[n]
 lines.append(f'| {labels[n]} | {d["mean_pooled_auc"]:.6f} | {d["mean_original_direction_auc"]:.6f} | {d["mean_original_direction_ap"]:.6f} | {", ".join(d["original_direction_months_ge_075"]) or "None"} |')
b=agg['frozen_155'];a=agg['capacity_182'];j=agg['synergy_joint']
lines +=['','**Measured change:** expanded 182 vs frozen 155 = '+f'{a["mean_pooled_auc"]-b["mean_pooled_auc"]:+.6f} pooled AUC, {a["mean_original_direction_auc"]-b["mean_original_direction_auc"]:+.6f} original-direction AUC. ',
       '**55 explicit interaction features vs 182 capacity-only** = '+f'{j["mean_pooled_auc"]-a["mean_pooled_auc"]:+.6f} pooled AUC, {j["mean_original_direction_auc"]-a["mean_original_direction_auc"]:+.6f} original-direction AUC. ',
       '', '## What high volume means here',
       '', '- All R9 entry opportunities are *scored*. No threshold or new trading logic changes the original R9 opportunity universe. This is **NOT** equal to actual new trades, on-policy order routing, broker fills, or improved account turnover.',
       '- At 75%/50% diagnostic retention, a top-k threshold is derived from the held-out monthly score distribution solely for ranking analysis; it cannot be deployed without a training-only fixed threshold and measured test-month coverage. The complete no-selection 100% denominator is preserved.',
       '- No new 5s quote-side terminal fills or separate commissions/slippage/occupancy simulation performed. Do not report positive after-cost profitability or live capability.',
       '', '## Final all-nine-month fit', '']
for fam in ('joint','r9_specialist'):
 d=json.loads((R/'results'/f'FULL_{fam}_RECEIPT.json').read_text());
 lines.append(f'- {fam}: **{d["training_actions"]:,}** uncensored training actions, **{d["feature_count"]}** features, artifact `{d["model_file"]}`, SHA-256 `{d["model_sha256"]}`. **IN-SAMPLE TRAINING ONLY; no held-out AUC.**')
lines +=['','## Interpretation and next-governor rule',
'','- The attempt to make the proxy families enhance each other **has been executed and measured**, not merely hypothesized. More trees and deeper interactions gave only small aggregate discrimination changes; existing event-time trend and price/spread geometry remain dominant.',
'- Combined feature importance from a full-data model is an **in-sample attribution only**; correlated features share importance and it is not evidence of new exploitable liquidity data.',
'- AUC remains below 0.80 and R9 original-direction 0.75. Do not optimize further on July/August thresholds without a fresh independent later period.',
'- Preserve the 155 baseline and all new models separately; neither replace nor merge the deployed R9 EA. QRB/QAF research observation remains enabled in the existing source branch.',
'- Research gate for next phase: freeze models, measure full original R9 trade occupancy, exits, stop geometry and account-level after-cost performance; preserve a truly unseen later period for evaluation.',
'']
for name in ('VERIFICATION','DESCRIPTIVE_UNCERTAINTY'):
 p=R/'results'/f'{name}.json'
 if p.exists():
  lines.append(f'## {name.replace("_"," ").title()}')
  lines.append('')
  js=json.loads(p.read_text())
  if name=='VERIFICATION':
   lines.append(f'- Revalidated **{len(js["monthly_raw_sha256_reverified"])}** original source-month SHA256 values and **{js["models_verified_n"]}** held-out model hashes and **{js["reproduced_auc_ap_values_n"]}** AUC/AP metrics; **{js["all_nine_models_verified_n"]}** final model hashes.')
  else:
   for k,v in js['pairs'].items():
    lines.append(f'- `{k}`: mean delta {v["mean_delta"]:+.6f}, descriptive day-block 95% interval [{v["descriptive_95_interval"][0]:+.6f}, {v["descriptive_95_interval"][1]:+.6f}]; prior exposure invalidates confirmatory inference.')
  lines.append('')
(R/'RESULTS.md').write_text('\n'.join(lines)+'\n')
print('WROTE_REPORT',len(lines),'lines')
