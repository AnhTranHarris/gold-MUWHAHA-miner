"""Offline H1V2 future-privileged counterfactual side audit; never as-of.
Assess whether selected profitable BUY/SELL has a demonstrably incorrect opposite
trade, rather than an opposite-neutral ambiguity. Do NOT promote hindsight gates.
"""
from pathlib import Path
import json,math
import numpy as np
R=Path('/mnt/data/h1v2/results');O=Path('/mnt/data/h1v2_r2/results')
SYNTH={'01':27980,'02':33523,'06':31801,'07':24382}

def audit():
 out={'status':'FUTURE_PRIVILEGED_PAIRED_SIDE_ORACLE_DIAGNOSTIC_ONLY','months':{},'notes':'code=1 strictly favorable, -1 adverse, 0 neutral at original R9 quote ordinal; cannot be input to foresight.'}
 for m in ('01','02','06','07'):
  with np.load(R/f'h1v2_dukascopy_{m}_oracle_labels.npz',allow_pickle=False) as z:
   sel=z['selected_row'].copy();side=z['selected_side'].copy();w=(side==-1).astype(np.int64);opp=1-w
   c=z['code'];other=c[sel,opp];correct=c[sel,w];goodfirst=z['first_event_ms'][sel,w];otherfirst=z['first_event_ms'][sel,opp]
   nc=len(sel);assert np.all(correct==1)
   wrong=int(np.sum(other==-1));neutral=int(np.sum(other==0));both=int(np.sum(other==1))
   breakdown={}
   for ms in (1000,2000,3000,5000,10000,30000):
    flag=(other==-1)&(goodfirst<=ms)
    n=int(flag.sum());breakdown[str(ms)]={'anti_opposite_wrong_and_right_hit_by':n,'share':n/nc,'coverage_vs_R9_SYNTH':n/SYNTH[m], 'passes_monthly_volume_floor':n>=math.ceil(.8*SYNTH[m])}
   out['months'][m]={'n_selected':nc,'other_side_wrong':wrong,'other_side_neutral':neutral,'other_side_good':both,'fraction_other_side_wrong':wrong/nc,'qualifying_counterfactual':breakdown}
   print(m, 'other_wrong',wrong,'neutral',neutral,'both',both,'fast3s + wrongopp',breakdown['3000']['anti_opposite_wrong_and_right_hit_by'],flush=True)
 out['all_months_counterfactual_strong_at_3s']=all(v['qualifying_counterfactual']['3000']['passes_monthly_volume_floor'] for v in out['months'].values())
 (O/'H1V2_R2_COUNTERFACTUAL_SIDE_AUDIT.json').write_text(json.dumps(out,indent=2))
 return out
if __name__=='__main__':audit()
