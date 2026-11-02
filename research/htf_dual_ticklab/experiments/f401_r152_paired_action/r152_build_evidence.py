from pathlib import Path
import json,hashlib,zipfile,os,subprocess
import numpy as np
from r152_paired_action_replay import ROOT,CONFIG,PINS,sha
rows=json.loads((ROOT/'R152_FROZEN_FOUR_MONTH_RESULTS.json').read_text())
source=Path('/mnt/data')
# Exact immutable original event arrays are contained in each full-source event mask.
# Feature caches are reproducible and intentionally excluded from archive to avoid
# duplicating >680MB of source-derived 128D floats.
with zipfile.ZipFile(ROOT/'R152_FULL_ORIGINAL_EVENT_AND_ACTION_MASKS.zip','w',compression=zipfile.ZIP_DEFLATED,compresslevel=4) as z:
 for m in ['01','02','06','07']:
  a=np.load(ROOT/f'R152_DK_{m}_FEATURES_AND_ACTIONS.npz')
  keys=[k for k in a.files if k!='X']
  compact=ROOT/f'R152_DK_{m}_ORIGINAL_EVENT_AND_ACTION_OUTCOMES.npz'
  np.savez_compressed(compact,**{k:a[k] for k in keys})
  a.close()
  z.write(compact,compact.name)
  z.write(ROOT/f'R152_DK_{m}_FROZEN_POLICY_ACTION_MASKS.npz',f'R152_DK_{m}_FROZEN_POLICY_ACTION_MASKS.npz')
assert zipfile.ZipFile(ROOT/'R152_FULL_ORIGINAL_EVENT_AND_ACTION_MASKS.zip').testzip() is None

files=['r152_paired_action_replay.py','r152_fit_freeze_action_portfolio.py','r152_frozen_transfer_resume.py','r152_build_evidence.py','test_r152_action.py','r120_multiclock_geometry.py','r120_htf_bridge.py','r151_t1_core.py','r150x_marked_renewal_action.py']
copy={name:source/name for name in files}
manifest={name:sha(p) for name,p in copy.items()}
model_files=sorted(ROOT.glob('R152_*_JAN_FROZEN.joblib'))+sorted(ROOT.glob('R152_*_FEB_CAL_FROZEN.joblib'))
manifest.update({p.name:sha(p) for p in model_files})
scientific={
 'title':'F401-R152 original-source Dukascopy four-month T1/T2/LIMIT action replay, research-only',
 'date':'2026-11-02',
 'source':'Original immutable F401-R32 event population and R151 approved Dukascopy raw SHA registry; exact original GitHub R120 publisher source',
 'source_sha256':PINS,
 'R120_GitHub_blob_SHA':{'r120_multiclock_geometry.py':'e44fbc375bae8865ff9e5376ca15ca7d96d05c7f','r120_htf_bridge.py':'6af69001ee1f71f20c552f76d378e36874c2efc4'},
 'config':CONFIG,
 'training':'Jan first 80% chronological with 70s embargo; T1/T2/LIMIT 95-tree 275216-row Jan models; uplift/fill/correct-guardian 55-tree deterministic half-stride of Jan FIT; February first60% bias/isotonic calibration with 70s embargo; February last35% pretransfer selection across 3 predeclared policies each; June/July no retuning',
 'families':list(rows[0]['families']),
 'rows':rows,
 'aggregate_original_events':sum(r['n_original'] for r in rows),
 'aggregate_correct':sum(r['original_classes']['0'] for r in rows),
 'aggregate_opposite':sum(r['original_classes']['1'] for r in rows),
 'aggregate_neutral':sum(r['original_classes']['2'] for r in rows),
 'full_eight_cell_filter_gate_passed':False,
 'status':'UNAPPROVED, NO FILTER REPLACEMENT, NO MT5 EXECUTION, NO REAL ORDER INTENT',
 'limitations':['Only original Dukascopy four source-month cells were available in this run; original Coinexx raw tapes not located in connected Drive','Original signed governor, forensic, 39-checklist and active ledger links returned 404; owner default and GitHub owner directive read','The original t0 R9 market orders remain immutable; hypothetical t0+15s T1/T2/LIMIT never-submitted actions cannot count as original wrong vetoes','Optimistic L1 touch is not a queue-aware or broker-confirmed fill','Costs are assumed 0.20 USD/ounce, not verified Coinexx fees/latency; independent event utility cannot be summed as shared capital P&L','June and July are historically exposed, not untouched blind validation','R120 original six-clock and completed M1/M5/M15/H1 states reused with exact GitHub blob SHA; no teacher, original truth, or matured outcome is used at runtime'],
 'source_and_model_sha256':manifest,
 'mask_archive_sha256':sha(ROOT/'R152_FULL_ORIGINAL_EVENT_AND_ACTION_MASKS.zip')
}
(ROOT/'R152_FULL_SCIENTIFIC_RECEIPT.json').write_text(json.dumps(scientific,indent=2))
lines=['# F401-R152 — ORIGINAL-SOURCE FOUR-MONTH PAIRED ACTION RESEARCH (UNAPPROVED)','',
'2026-11-02 | Original Dukascopy Jan/Feb/Jun/Jul | 1,266,934 immutable events | original R120 92+36 source-published features.',
'','## Mechanisms implemented and evaluated','',
'1. A_PAIRED_OPTIMAL_STOP: new T1 MARKET versus T2 5-second WAIT, trained on paired native bid/ask 30s first-touch economic uplift.','2. B_PASSIVE_LIMIT_HAZARD: 0.50 USD improved-price LIMIT, 2s TTL, optimistic native L1 touch, separate fill probability and expected utility.','3. C_INDEPENDENT_CORRECT_RESCUE: independent original-correct guardian trained only offline; pre-T1 market-only runtime features; no t0 veto.',
'','Jan FIT with 70s future-outcome embargo; February calibration and frozen selection; June/July frozen historically exposed transfer. Full 128D R120 features derived from original registered tapes, not invented.','',
'## Exact original counts and frozen transfer','',
'| DK month | Original events | Correct | Opposite | Neutral | T1 net USD/original | T2 net USD/original | LIMIT net USD/original | Frozen A actions | Frozen B actions | Frozen C actions | Frozen C net USD/original |',
'|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
for r in rows:
 f=r['families'];lines.append('| '+ ' | '.join([r['month'],str(r['n_original']),str(r['original_classes']['0']),str(r['original_classes']['1']),str(r['original_classes']['2']),f"{r['baseline_T1_net_per_original_intent']:.6f}",f"{r['baseline_T2_net_per_original_intent']:.6f}",f"{r['baseline_LIMIT_net_per_original_intent']:.6f}",str(f['A_PAIRED_OPTIMAL_STOP']['n_new_hypothetical_actions']),str(f['B_PASSIVE_LIMIT_HAZARD']['n_new_hypothetical_actions']),str(f['C_INDEPENDENT_CORRECT_RESCUE']['n_new_hypothetical_actions']),f"{f['C_INDEPENDENT_CORRECT_RESCUE']['hypothetical_net_per_original_intent_USD']:.8f}"])+' |')
lines+=['','## Frozen policy details','', 'February-frozen thresholds: '+json.dumps(json.loads((ROOT/'R152_FEB_FROZEN_POLICIES.json').read_text())), '',
'## Scientific boundaries','',
'All proposed actions are hypothetical NEW T1/T2 never-submitted intents; they do not retroactively cancel t0 orders. R9 original 4,178 quota bins are unchanged by construction, but were not re-audited for any new EA deployment. No 71%/90% eight-cell result is established. No funded fills, margin or shared-capital economics. June/July previously exposed.','',
'Original full governor, forensic, checklist and active ledger IDs returned 404 in both connected Drive accounts on 2026-11-02; preserved original owner directive and exact GitHub source instead. Do not mark any original checklist objective approved.','',
'11 deterministic tests passed, including all four raw tape SHA checks, original immutable event arrays and original R120 prefix causality. Full failed results and model weights preserved.','',
'## Reproducibility','',
'Original source hashes: '+json.dumps(PINS),
'Original R120 GitHub blobs e44fbc375bae8865ff9e5376ca15ca7d96d05c7f and 6af69001ee1f71f20c552f76d378e36874c2efc4, byte-for-byte verified after authenticated source transport.','',
'Event/action masks archive SHA256 '+scientific['mask_archive_sha256'],
'Original event counts: '+str(scientific['aggregate_original_events'])+', correct '+str(scientific['aggregate_correct'])+', opposite '+str(scientific['aggregate_opposite'])+', neutral '+str(scientific['aggregate_neutral'])+'.','',
'Next genuinely different family: a pre-OrderSend genuine intent capture (intent ID, quote-as-of, broker order state) with latency/queue-aware limit execution and capital-coupled 12-scenario replay; do not repeat flat static classifier threshold grids.']
(ROOT/'R152_FULL_SCIENTIFIC_RECEIPT_UNAPPROVED.md').write_text('\n'.join(lines)+'\n')
with zipfile.ZipFile(ROOT/'R152_EXECUTABLE_SOURCE_MODELS_RECEIPTS.zip','w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for name,p in copy.items():z.write(p,name)
 for p in model_files:z.write(p,p.name)
 for p in ROOT.glob('*.json'):z.write(p,p.name)
 for p in ROOT.glob('*.md'):z.write(p,p.name)
 for name in ['r152_jan.log','r152_02.log','r152_06.log','r152_07.log','r152_training.log','r152_training_resume.log','r152_transfer.log','r152_tests.log']:
  p=source/name
  if p.exists():z.write(p,name)
assert zipfile.ZipFile(ROOT/'R152_EXECUTABLE_SOURCE_MODELS_RECEIPTS.zip').testzip() is None
print(json.dumps({'original':scientific['aggregate_original_events'],'correct':scientific['aggregate_correct'],
 'opposite':scientific['aggregate_opposite'],'neutral':scientific['aggregate_neutral'],
 'source_zip':{'bytes':(ROOT/'R152_EXECUTABLE_SOURCE_MODELS_RECEIPTS.zip').stat().st_size,'sha256':sha(ROOT/'R152_EXECUTABLE_SOURCE_MODELS_RECEIPTS.zip')},
 'mask_zip':{'bytes':(ROOT/'R152_FULL_ORIGINAL_EVENT_AND_ACTION_MASKS.zip').stat().st_size,'sha256':scientific['mask_archive_sha256']}},indent=2))