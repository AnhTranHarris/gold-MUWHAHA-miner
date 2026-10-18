"""Native original quote time-to-direction oracle diagnostic, strictly outcomes only.
The original R00-067 loader and source hashes/UTC profile are imported unchanged.
"""
from importlib.machinery import SourceFileLoader
from pathlib import Path
import json,sys,time,hashlib
import numpy as np,pandas as pd
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'r00_075_horizon/results';OUT.mkdir(parents=True,exist_ok=True)
RAW=SourceFileLoader('approved_r00_067_native',str(ROOT/'src/01_relabel_native_events.py')).load_module()
H=(1,2,3,5,10,15,20,30,45,60)
def run(b,m):
 start=time.time();t,bid,ask,sha=RAW.load_raw(b,m)
 source=(ROOT/f'r00_072_episode/results/EPISODES_{b}_01.npz') if m=='01' else (ROOT/f'r00_073_arbiter/results/ALL_DIRECTIONS_{b}_{m}.npz')
 with np.load(source) as z:
  j=z['quote_index'].copy();et=z['ts_ms'].copy();side=z['reference_side'].copy();label=z['y'].copy()
 assert np.array_equal(et,t[j]);mid=(bid+ask)*.5
 rows=[];frows=[]
 for h in H:
  target=et+h*1000;ix=np.searchsorted(t,target,side='left');exists=ix<len(t);idx=np.minimum(ix,len(t)-1)
  known=exists&(t[idx]>=target)&(t[idx]<target+2000)
  change=mid[idx]-mid[j]
  neutral=~known | (np.abs(change)<=0.10)
  up=known&(change>0.10);down=known&(change<-.10)
  correct=(up&(side==1))|(down&(side==-1))
  neg=(up&(side==-1))|(down&(side==1))
  sign_correct=known&(np.sign(change)==side)&(change!=0)
  rows.append(dict(broker=b,month=m,horizon_s=h,events=len(j),known=int(known.sum()),neutral_or_missing=int(neutral.sum()),direction_right=int(correct.sum()),direction_wrong=int(neg.sum()),accuracy=float(correct.mean()),nonneutral_pct=float((~neutral).mean()),conditional_precision=float(correct.sum()/max(int((~neutral).sum()),1)),zero_threshold_sign_fraction=float(sign_correct.mean()),original_tick_sha256=sha))
  # Keep exact event and future quote index per evaluated outcome for scientific recovery.
  np.savez_compressed(OUT/f'OUTCOME_INDEX_{b}_{m}_h{h:02d}.npz',ts_ms=et,quote_index=j,future_quote_index=np.where(exists,ix,-1),known=known,side=side,correct=correct,nonneutral=~neutral)
  if h==30:
   recon=np.where(up,1,np.where(down,-1,0)).astype(np.int8)
   assert np.array_equal(recon,label),(b,m,'original frozen +30s label differs from reconstructed tick source')
 df=pd.DataFrame(rows);df.to_csv(OUT/f'ALL_075_HORIZONS_{b}_{m}.csv',index=False)
 print('HORIZONS',b,m,'native_quotes',len(t),'events',len(et),'seconds',round(time.time()-start,2),'h30',df[df.horizon_s==30][['accuracy','conditional_precision','neutral_or_missing']].to_dict('records'),'BEST_exploratory',df.sort_values('accuracy',ascending=False)[['horizon_s','accuracy']].head(3).to_dict('records'),flush=True)
if __name__=='__main__':run(sys.argv[1],sys.argv[2])
