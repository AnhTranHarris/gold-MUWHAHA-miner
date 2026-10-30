"""F401-R150E exact missing direct R147 broker-invariant HTF + interaction publisher.

Adds only the 36 direct R147 common-state coordinates not already directly available
through R150C's full 92D R120 block and R150D's full 57D strict path block:
16 completed-HTF publication/geometry coordinates +20 cross-scale interactions.
All features are causal at the first genuine native t0+[15,16)s decision quote.
No FILTER08 teacher/truth/future outcome enters predictors.
"""
from __future__ import annotations
import sys,pathlib,json,hashlib,gc
import numpy as np
ROOT=pathlib.Path('/mnt/data'); OUT=ROOT/'R150E'/'features';OUT.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(ROOT/'r149_work'/'R147_PACKAGE'/'source'))
sys.path.insert(0,str(ROOT/'R149'/'research'))
from r147_build_source_features import htf_features,add_interactions
from r149_causal_latent import load_ticks,PINS

def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(4<<20),b''):h.update(b)
 return h.hexdigest()

def build(b,m):
 key=f'{b}_{m}'
 base=np.load(ROOT/'R150C'/'features'/f'R150C_{key}_WORLD_STATE.npz',allow_pickle=False)
 path=np.load(ROOT/'R150D'/'path'/f'R150D_{key}_R147_STRICT_PATH.npz',allow_pickle=False)
 assert np.array_equal(base['t'],path['t']) and np.array_equal(base['side'],path['side'])
 ev=base['t'].astype(np.int64); decision=base['decision'].astype(np.int64);side=base['side'].astype(np.int8)
 micro=base['X_source'][:,:92].astype(np.float32)
 xp=path['X'].astype(np.float32)
 t,bid,ask=load_ticks(b,m)
 mid=(bid.astype(np.float64)+ask.astype(np.float64))*.5
 # midpoint at the actual first native decision quote is target-time anchor only for geometry;
 # HTF bars themselves are strictly completed before decision.
 fi=np.searchsorted(t,decision,side='left')
 safe=np.minimum(fi,len(t)-1)
 found=(fi<len(t))&(t[safe]==decision)
 mid_dec=mid[safe]
 htf,hnames=htf_features(t,bid,ask,decision,side,mid_dec)
 inter,inames=add_interactions(micro,htf,xp)
 # Exact R147 common-state rules: completed HTF keeps published, close_from_low,
 # close_from_high, age_sec; interactions drop m1-h1 raw body/1bar and wallclock raw fields.
 hkeep=[i for i,n in enumerate(hnames) if any(n.endswith(x) for x in ('published','close_from_low','close_from_high','age_sec'))]
 idrop={'ix_m1_minus_h1_body','ix_m1_minus_h1_1bar','ix_wallclock_spread','ix_wallclock_quote_age'}
 ikeep=[i for i,n in enumerate(inames) if n not in idrop]
 X=np.hstack([htf[:,hkeep],inter[:,ikeep]]).astype(np.float32)
 names=[f'r147htf::{hnames[i]}' for i in hkeep]+[f'r147ix::{inames[i]}' for i in ikeep]
 assert X.shape==(len(ev),36),(key,X.shape)
 valid=base['valid'].astype(bool)&path['available'].astype(bool)&found&np.isfinite(X).all(axis=1)
 out=OUT/f'R150E_{key}_R147_DIRECT_HTF_INTER36.npz'
 np.savez_compressed(out,X=X,names=np.asarray(names),t=ev,decision=decision,side=side,valid=valid)
 rec=dict(cell=key,n_events=int(len(ev)),valid=int(valid.sum()),shape=list(X.shape),names=names,raw_sha256=PINS[key],output_sha256=sha(out),
   causal_contract='completed HTF bars end <= actual first native t0+[15,16)s decision; interaction inputs are R150C 92D causal micro + R150D path strict <t0+15000; no truth/teacher/future predictor',
   dimension_audit='R147 common153 = 75 common micro +16 common HTF +42 common path +20 common interactions. R150C already contains full92 micro; R150D contains full57 path. Direct missing common mechanisms are therefore 16+20=36, not 61.')
 (OUT/f'R150E_{key}_RECEIPT.json').write_text(json.dumps(rec,indent=2))
 print(json.dumps({k:rec[k] for k in ('cell','valid','shape','output_sha256')}),flush=True)
 del base,path,t,bid,ask,mid,htf,inter,X;gc.collect()
if __name__=='__main__': build(sys.argv[1],sys.argv[2])
