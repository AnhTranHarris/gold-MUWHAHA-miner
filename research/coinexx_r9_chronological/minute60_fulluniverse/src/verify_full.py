"""Crosscheck every new full-universe derived month against immutable prior pilot cache,
original source monthly receipts, all source-ordinal labels and field completeness."""
import json,hashlib
from pathlib import Path
import numpy as np
from hft import hft_features
ROOT=Path('/mnt/data/r9_m60_expanded')
ref=json.loads((ROOT/'source_receipt.json').read_text())
completeness=json.loads((ROOT/'full_results/quote_field_completeness.json').read_text())
checks=[]
for i in range(1,10):
 m=f'{i:02}';fd=np.load(ROOT/f'full_derived/full_month_2026_{m}.npz',allow_pickle=False)
 old=np.load(ROOT/f'sample_cache/multiscale_2026_{m}.npz',allow_pickle=False)
 rs=json.loads((ROOT/f'full_derived/full_receipt_2026_{m}.json').read_text())
 assert rs['raw_sha256']==ref['source_months'][m]['source_sha256']
 assert rs['raw_rows']==ref['source_months'][m]['rows']==completeness[m]['rows']
 assert len(fd['entry_times'])==ref['source_months'][m]['closed_positions']
 assert fd['features'].shape==(ref['source_months'][m]['closed_positions'],145)
 assert (fd['labels'][:,1]>=0).sum()>=len(fd['labels'])-10
 idx={int(o):k for k,o in enumerate(fd['entry_ordinals'])}
 oi=np.array([idx[int(o)] for o in old['ordinals']])
 np.testing.assert_array_equal(fd['labels'][oi],old['labels'])
 np.testing.assert_array_equal(fd['entry_times'][oi],old['entry_times'])
 np.testing.assert_array_equal(fd['features'][oi,14:117],hft_features(old['X']))
 assert np.all(fd['valid'][oi])
 assert completeness[m]['nonzero_last']==completeness[m]['nonzero_volume']==completeness[m]['nonzero_volume_real']==0
 checks.append({'month':m,'sample_parity':len(oi),'exact_match':True,'n_all':int(len(fd['entry_times'])),'full60_valid':int(fd['valid'].sum())})
print(json.dumps({'verified_months':len(checks),'sample_parity_total':sum(x['sample_parity'] for x in checks),'details':checks},indent=2))
(ROOT/'full_results/verification.json').write_text(json.dumps({'verified_months':len(checks),'sample_parity_total':sum(x['sample_parity'] for x in checks),'details':checks},indent=2)+'\n')
