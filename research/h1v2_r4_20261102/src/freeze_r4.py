"""Deterministic R4 source-exact research receipts and continuation packaging."""
from pathlib import Path
import hashlib,json,zipfile,platform,os
import numpy as np
R4=Path('/mnt/data/h1v2_r4');RES=R4/'results'
SRC=Path('/mnt/data')
def digest(p):
 with open(p,'rb') as fh:return hashlib.file_digest(fh,'sha256').hexdigest()

def main():
 j=json.loads((RES/'R4_HOLDOUT_COMPARISON.json').read_text());b=json.loads((RES/'R4_HIERARCHICAL_BAYESIAN_ABSTENTION.json').read_text());prov=json.loads((RES/'R4_MARKED_SOURCE_RECEIPTS.json').read_text())
 report=['# H1V2 R4 — Four-month ordered quote mark and strict asymmetric rejection research','',
 '**2026-11-02 — Final research status: intentional overfit confirms high in-sample memorization; July-withheld transfer fails; no eligible execution policy.**','',
 '## Source-exact dependency chain','',
 '- Repaired R9 v2 baseline Git SHA `997dfdbd06157faa426c143874ad84277971570e`. Original source engine and exits **not modified**.',
 '- Original H1V2 Git SHA `edce573d9c53b743dc5de1b0d741c81370af52c1`; original teacher on four Dukascopy source months: 513,262 selected future-privileged wins, explicitly not tradable.',
 '- R2 parent Git SHA `0a6f860bf2b3e265922af55bd2547e4970037101`. Original strict rapid-hindsight nonoverlapping FAST3S/NET10/SPREAD100 reference = 241,459. All counts future privileged.',
 '- R3 112 finely binned session/regime trend grid configurations had failed leave-self-out and July-withheld; the signed true-path and quote rates used here come from its exact-source, as-of 15k monthly feature matrices.',
 '- R4 separate branch: `carson/h1v2-r4-ordered-marks-hawkes-skew-20261102`. Created from frozen R2 parent. New R4 source is additive only; prior files preserved.',
 '- Raw gzip SHA-256 original Dukascopy month pins checked January, February, June, July; original candidate ordinals `ix` and millisecond timestamps joined exactly to all source derived arrays.',
 '- Dataset per month 15,000 independently sampled as-of candidate timestamps, each independently labeled BUY and SELL as R2 WRONG/NEUTRAL/WEAK_GOOD/STRONG_GOOD. **This is a 60k timestamp sample, NOT the exhaustive 15.4M event universe.**','',
 '## New untried vs R2/R3 mechanism families','',
 '1. **M1:** Six observable quote revision marks (bid up/down, ask up/down, both up/down) in original time and row order, including simultaneous millisecond ordering and abstention on mixed revisions. Not actual executed order/book volume.',
 '2. **M2:** Multi-horizon marked-event count/intensity 250ms,1s,5s,15s,30s and exponential excitation **basis** 250ms,1s,5s; this is not a fitted multivariate Hawkes intensity model, only observed past explanatory covariates.',
 '3. **M3:** Full 6x6 ordered mark transitions 5s, three latest marks, event-run dynamics, signed bid/ask quote revision asymmetry, and raw event count; no future tick leakage.',
 '4. **M4:** Four-class action-conditional competing consequence head: 4-class LightGBM trained on BUY and SELL independently (shared parameters with direction indicator). Neyman–Pearson-style constrained selective gate: choose side by strong-probability minus 1.5x wrong-probability minus 0.3x neutral-probability, otherwise WAIT. Policy needs Wilson 95% lower-bound >=80%, 150+ June calibrator actions; failed.',
 '5. **M5:** Hierarchical Dirichlet empirical-Bayes posterior shrinkage side x session x spread x signed quote event flow x 5m true trend; coarse and fine motifs; smoothing 20 and 100 observations. Tried with all-four contaminated scores and July withheld independently.',
 '6. **M6:** Model ablation baseline causal original geometry+true signed path, plus quote mark counts, plus full order/decay; same exact 15k July tuples, controlled 120 rounds. Full-order model did NOT improve strict withheld accuracy.',
 '', '## 3s strong teacher definition and evidence boundary','',
 'STRONG_GOOD requires independently checked exact original BUY or SELL R9 quote-side exit, first favorable >=$0.10 net ahead of adverse -$0.10, first favorable <=3000ms, exit net >=$0.10, and spread <=$1.00. The other R2 labels: WRONG, NEUTRAL, WEAK_GOOD. Original R9 hard stop, trail and exit, fee remain pinned. Do not use hindsight price/net/first_ms labels as model input.',
 '', '## Strict July-withheld top-ranked outcomes (train Jan+Feb+Jun)','',
 '| Frozen causal features | 150 top-ranked July entries | STRONG_GOOD | WRONG | NEUTRAL | WEAK | Strict correctness |',
 '|---|---:|---:|---:|---:|---:|---:|']
 for k in ['baseline','counts','ordered']:
  row=j['models'][f'{k}_train_01_02_06_test_07']['july']['top_rankings'][1]
  report.append(f"| {k} | {row['admitted']} | {row['strong']} | {row['wrong']} | {row['neutral']} | {row['weak']} | {row['strict_precision']*100:.2f}% |")
 report+=['','Held-out selected outcomes are **not** nonoverlapping source-simulator trades; the figures are action-label diagnostics only. Strict admission requires much more than selecting a top-ranked row.',
 '','## January/February fit — June qualification; July untouched','']
 c=j['models']['ordered_janfeb_june_cal_july_untouched']
 report+=[f"- June calibrated 95% Wilson lower >=80% at n>=150: **{c['calibration']['qualified']}**; maximum reported top-bin Wilson lower **{c['calibration']['max_top_wilson']*100:.2f}%**.",
 f"- Threshold: **{c['threshold']}**. Frozen July entries admitted: **{c['july']['threshold_admitted']}**. No authorized classifier or trading policy.",'','## Intentionally overfitted four-month teacher (label contamination disclosed)','',
 '| Training and scoring month | Top 1% selected | Strong | Wrong | Strict precision |', '|---|---:|---:|---:|---:|']
 for m in ('01','02','06','07'):
  x=j['models']['ordered_all_4_contaminated_resubstitution']['months'][m]['top_rankings'][1]
  report.append(f"| {m} | {x['admitted']} | {x['strong']} | {x['wrong']} | {x['strict_precision']*100:.1f}% |")
 report+=['', 'This 100% top-1% resubstitution is contamination / memorization: the fitted model is tested on its own labels. The 600 selected sampled timestamps do not establish the 94,150 full-market monthly-volume target or remotely indicate forward predictions.',
 '', '## Empirical Bayesian rejection diagnostic','',
 '| Feature motif | Prior support | Fit months | July top 1% strong | July max posterior P(strong) |','|---|---:|---|---:|---:|']
 for k in b['results']:
  if len(k['train_months'])==3:
   q=k['months']['07'];report.append(f"| {k['degree']} | {k['alpha']:.0f} | Jan/Feb/Jun | {q['top'][0]['precision']*100:.2f}% | {q['posterior_max_strong']*100:.2f}% |")
 report+=['','The smoothed independent class posterior never approaches an 80% conditional strong label threshold; high-confidence rejection is the correct response. Sophisticated priors do not manufacture missing information.',
 '', '## Audits and precise scope','',
 '- 29/29 combined original H1V2+R2+R3+R4 tests passed, including exact same-ms ordinal prefix invariance, six mark classes, Markov transition order-change detection, 4-class posterior training-exclusion and strict Wilson bound tests.',
 '- Four-month original raw gzip SHA pins independently verified; each novel 15k-row 92-column mark atlas stored, SHA receipts below. Existing exact-exit validation from H1V2/R2 retained, not rerun in R4.',
 '- Original tick exit mechanism was never modified; model trial not translated into MQL5, no Coinexx out-of-sample domain, no latency/slippage/margin / nonoverlap on-policy replay.',
 '- Experimental external academic context: Oxford JFE 2024 order-book-dependent Hawkes, and 2026 journal research on multivariate Hawkes with limit order book data. These use **order book** events, which are NOT available in Dukascopy best Bid/Ask feed; our quote revision marks are not market-order flow. No fitted Hawkes claim.',
 '', '## Next distinct scientific hypothesis (do not repeat past failed G1-G14 grid or this R4 model)','',
 'Implement a **properly fitted** six-mark self/cross excitation likelihood, with out-of-sample quote mark arrival prediction and a time-order shuffled control; test whether fitted excitations improve directional strong-vs-wrong discrimination at shared as-of event timestamp before adding any policy. Also test competing risk first-hit-to-positive vs first-hit-to-adverse with real 0.25/1/3/5s elapsed source labels, dropout detection, domain robustness and strict nonoverlap replay only after qualifying. Never confuse future-selected oracle supply and real policy action volumes.',
 '', '## Full reproducibility','',
 'Restoration: original H1V2 complete dependency ZIP, R2 full ZIP, R3 multigrid ZIP and R4 full ZIP; preserve these original independent artifacts without overwriting. R4 code expects R2 and R3 matrices in original directory layout or source-tracked equivalents. Rebuild mark atlas from original raw gzip using:',
 '```bash',
 'PYTHONPATH=/mnt/data/h1v2/src:/mnt/data/h1v2_r4/src python /mnt/data/h1v2_r4/src/extract_marked_atlas.py',
 'PYTHONPATH=/mnt/data/h1v2/src:/mnt/data/h1v2_r2/src:/mnt/data/h1v2_r3/src:/mnt/data/h1v2_r4/src python /mnt/data/h1v2_r4/src/finish_competing_risks.py',
 'PYTHONPATH=/mnt/data/h1v2/src:/mnt/data/h1v2_r2/src:/mnt/data/h1v2_r3/src:/mnt/data/h1v2_r4/src python /mnt/data/h1v2_r4/src/bayesian_quote_abstention.py',
 'PYTHONPATH=/mnt/data/h1v2/src:/mnt/data/h1v2_r2/src:/mnt/data/h1v2_r3/src:/mnt/data/h1v2_r4/src pytest -q /mnt/data/h1v2/tests /mnt/data/h1v2_r2/tests /mnt/data/h1v2_r3/tests /mnt/data/h1v2_r4/tests',
 '```','', 'Status: **R4_HINDSIGHT_RESUB_100_PERCENT_AT_TOP1 / R4_CROSS_MONTH_DIRECTIONAL_STRICT_FAIL / R4_CAUSAL_APPROVAL_NONE**.']
 (R4/'H1V2_R4_RESEARCH_VERIFICATION_20261102.md').write_text('\n'.join(report)+'\n')
 paths=[p for p in R4.rglob('*') if p.is_file() and '__pycache__' not in str(p) and '.pytest_cache' not in str(p) and p.name!='SOURCE_EXACT_SHA256_MANIFEST.json']
 paths.extend([SRC/'R9_V2_ENTRY_ASYMMETRY_SOURCE_AUDIT_20261102.md',SRC/'h1v2_r2'/'H1V2_R2_RESEARCH_VERIFICATION_20261102.md',SRC/'h1v2_r3'/'H1V2_R3_RESEARCH_VERIFICATION_20261102.md'])
 manifest={'format':'H1V2_R4_SOURCE_EXACT_MANIFEST','source_months':prov['months'],'recovery_sources':{
 'h1v2_base':'https://drive.google.com/file/d/14Zqs-PyZ70qr0NTvpJRxpT0XcVc8msUu/view',
 'r2':'https://drive.google.com/file/d/11vsLhtdkDUfdEF34Q7zPYqpIJibu-aPV/view',
 'r3':'https://drive.google.com/file/d/17oxTABUOMNq7Zc8nFpsbVpYJZ8xx75B4/view'},
 'files':{str(p.relative_to(R4) if p.is_relative_to(R4) else 'parent_audit/'+p.name):{'size':p.stat().st_size,'sha256':digest(p)} for p in paths}}
 (R4/'SOURCE_EXACT_SHA256_MANIFEST.json').write_text(json.dumps(manifest,indent=2))
 zip_path=SRC/'H1V2_R4_FOUR_MONTH_ORDERED_MARKS_COMPLETE_SOURCE_EXACT_20261102.zip'
 with zipfile.ZipFile(zip_path,'w',zipfile.ZIP_DEFLATED,compresslevel=7) as z:
  for p in paths:
   z.write(p,str(p.relative_to(R4) if p.is_relative_to(R4) else 'parent_audit/'+p.name))
  z.write(R4/'SOURCE_EXACT_SHA256_MANIFEST.json','SOURCE_EXACT_SHA256_MANIFEST.json')
 with zipfile.ZipFile(zip_path) as z:
  assert z.testzip() is None
  for n,vals in manifest['files'].items():assert hashlib.sha256(z.read(n)).hexdigest()==vals['sha256']
 print('ZIP',zip_path,zip_path.stat().st_size,'SHA256',digest(zip_path),'MEMBERS',len(manifest['files'])+1)
if __name__=='__main__':main()
