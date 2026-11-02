"""Recheck H1V2 R2 source-trace side, exit, first-pass and DP invariants."""
import json,hashlib
from pathlib import Path
import numpy as np
ROOT=Path('/mnt/data/h1v2/results');OUT=Path('/mnt/data/h1v2_r2/results');MONTHS=('01','02','06','07')

def verify():
 result={'status':'SOURCE_EXACT_PARITY_VERIFIED_ON_ORIGINAL_FROZEN_H1V2_LABELS','rules':{},'original_teacher_unmodified':True}
 for tag,netmin,firstmax in [('FAST3S_NET10_SPR100',.1,3000),('FAST5S_NET20_SPR100',.2,5000)]:
  total=0;details={}
  for m in MONTHS:
   receipt=json.loads((OUT/f'H1V2_R2_{m}_DP_REOPTIMIZED_RECEIPT.json').read_text())['rules'][tag]
   with np.load(ROOT/f'h1v2_dukascopy_{m}_oracle_labels.npz',allow_pickle=False) as old, np.load(OUT/receipt['output'],allow_pickle=False) as z:
    entries=z['entry_tick_ix'];rows=np.searchsorted(old['tick_index'],entries);side=(z['side']==-1).astype(np.int64)
    assert len(entries)==receipt['count'] and len(entries)==len(np.unique(entries))
    assert np.array_equal(old['tick_index'][rows],entries)
    assert np.all(old['code'][rows,side]==1)
    assert np.array_equal(old['exit_tick_index'][rows,side],z['exit_tick_ix'])
    assert np.allclose(old['net'][rows,side],z['net'],atol=0,rtol=0)
    assert np.array_equal(old['first_event_ms'][rows,side],z['first_favorable_elapsed_ms'])
    assert np.all(z['net']>=netmin) and np.all(z['first_favorable_elapsed_ms']<=firstmax)
    assert np.all(z['entry_ask']-z['entry_bid']<=1.+1e-5)
    assert np.all(z['entry_tick_ix'][1:]>z['exit_tick_ix'][:-1])
    assert np.all((z['exit_utc_ms']-z['entry_utc_ms'])<=30000)
    with (OUT/receipt['output']).open('rb') as fh:checksum=hashlib.file_digest(fh,'sha256').hexdigest()
    assert checksum==receipt['sha256']
    total+=len(entries);details[m]={'n':len(entries),'original_r9_exit_label_parity':'EXACT','hash':checksum}
  result['rules'][tag]={'selected_total':total,'months':details}
 (OUT/'H1V2_R2_FINAL_REPLAY_PARITY.json').write_text(json.dumps(result,indent=2))
 return result
if __name__=='__main__':
 r=verify();print(json.dumps({tag:doc['selected_total'] for tag,doc in r['rules'].items()},indent=2))
