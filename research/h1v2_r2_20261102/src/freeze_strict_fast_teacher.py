"""Freeze H1V2-R2 extreme quality future oracle subsets without replanning.

The selected trade schedule comes from original future-privileged H1V2 DP.
Filtering is a conservative subset preserving original quote-ordinal nonoverlap.
Neither gate nor outcome is available as a causal trading decision.
"""
import hashlib,json,math
from pathlib import Path
import numpy as np
ROOT=Path('/mnt/data/h1v2/results');OUT=Path('/mnt/data/h1v2_r2/results')
SYNTH={'01':27980,'02':33523,'06':31801,'07':24382}
CONFIGS={'FAST3S_NET10_SPR100':dict(first_max_ms=3000,net_min=.10,spread_max=1.0),
         'FAST5S_NET20_SPR100':dict(first_max_ms=5000,net_min=.20,spread_max=1.0)}

def quality_gate(first_ms,net,spread,first_max_ms,net_min,spread_max):
    return (first_ms>=0)&(first_ms<=first_max_ms)&(net>=net_min)&(spread<=spread_max+1e-5)

def run():
 report={'scope':'FILTERED_FUTURE_PRIVILEGED_H1V2_ORACLE_UNCHANGED_ENGINE','configurations':{},'warning':'These gates know future label and realized net; never feed those to a live model. Retained set is NOT a re-optimized maximal schedule.'}
 for tag,cfg in CONFIGS.items():
    info={'params':cfg,'months':{},'total':0}
    for mon in ('01','02','06','07'):
      with np.load(ROOT/f'h1v2_dukascopy_{mon}_selected_exact_trace.npz',allow_pickle=False) as s:
        data={k:s[k].copy() for k in s.files}
      spread=data['entry_ask']-data['entry_bid']
      mask=quality_gate(data['first_favorable_elapsed_ms'],data['net'],spread,**cfg)
      sel={k:v[mask] for k,v in data.items()}
      n=int(mask.sum());floor=math.ceil(.8*SYNTH[mon])
      if n>1:assert np.all(sel['entry_tick_ix'][1:]>sel['exit_tick_ix'][:-1])
      assert np.all(sel['net']>=cfg['net_min']) and np.all(sel['first_favorable_elapsed_ms']<=cfg['first_max_ms'])
      assert np.all((sel['entry_ask']-sel['entry_bid'])<=cfg['spread_max']+1e-5)
      out=OUT/f'H1V2_R2_{tag}_{mon}_EXACT_SELECTED_TRACE.npz'
      np.savez_compressed(out,**sel)
      with out.open('rb') as f:digest=hashlib.file_digest(f,'sha256').hexdigest()
      info['months'][mon]={'count':n,'floor':floor,'floor_pass':n>=floor,'sha256':digest,'output':out.name,'original_count':len(spread),
                           'modeled_net_sum':round(float(sel['net'].sum()),3),'median_first_hit_ms':float(np.median(sel['first_favorable_elapsed_ms']))}
      info['total']+=n
    info['all_months_pass']=all(x['floor_pass'] for x in info['months'].values());report['configurations'][tag]=info
    print(tag, 'retained', info['total'],'all_months_pass',info['all_months_pass'], 'monthly',[info['months'][k]['count'] for k in ('01','02','06','07')],flush=True)
 (OUT/'H1V2_R2_STRICT_TEACHER_FREEZE.json').write_text(json.dumps(report,indent=2));return report
if __name__=='__main__':run()
