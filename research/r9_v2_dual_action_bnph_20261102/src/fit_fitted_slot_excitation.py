"""Fit nonnegative session-baseline six-mark 250ms excitation model on raw ticks."""
from __future__ import annotations
import argparse,hashlib,json,time
from pathlib import Path
import numpy as np
from build_repaired_matrix import load_raw
from fitted_slot_excitation import MODEL_VERSION,MARKS,SESSIONS,slot_dataset,design_matrix,fit_nonnegative_ridge,stabilize,predict

def sha256(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for c in iter(lambda:f.read(1<<20),b''):h.update(c)
 return h.hexdigest()

def main(a):
 start=time.monotonic();raw=Path(a.raw);t,bid,ask=load_raw(raw,'coinexx','01');states=[];targets=[];sessions=[];rows={}
 for day in a.fit_days:
  slot,c,x,s=slot_dataset(t,bid,ask,day);states.append(x);targets.append(c);sessions.append(s);rows[day]=len(c)
 S=np.concatenate(states);Y=np.concatenate(targets);sess=np.concatenate(sessions);X,scales=design_matrix(S,sess);C=fit_nonnegative_ridge(X,Y,ridge=a.ridge,iterations=a.iterations);Cs,r0,r1,k,B=stabilize(C,scales,a.max_radius)
 pred=predict(X,Cs);base=np.zeros_like(pred);session_means=np.zeros((len(SESSIONS),6),np.float64)
 for ss in range(len(SESSIONS)):
  m=sess==ss;mu=np.maximum(1e-9,Y[m].mean(axis=0)) if m.any() else np.full(6,1e-9);session_means[ss]=mu;base[m]=mu
 out=Path(a.out);out.mkdir(parents=True,exist_ok=True);p=out/'coinexx_01_fitted_slot_excitation_v1.npz';np.savez_compressed(p,coef=Cs,scales=scales,branching=B,session_means=session_means,marks=np.asarray(MARKS),sessions=np.asarray(SESSIONS))
 mse=float(np.mean((Y-pred)**2));bmse=float(np.mean((Y-base)**2))
 r=dict(identity=MODEL_VERSION,fit_days=a.fit_days,slot_rows=rows,total_rows=len(Y),ridge=a.ridge,pre_stability_radius=r0,post_stability_radius=r1,excitation_scale=k,mse=mse,session_baseline_mse=bmse,mse_improvement=(bmse-mse)/bmse if bmse else None,model_sha256=sha256(p),raw_tick_sha256=sha256(raw),fitted=True,continuous_time_mle=False,status='FITTED_DISCRETE_SLOT_EXCITATION_RESEARCH',elapsed_sec=round(time.monotonic()-start,2))
 (out/'coinexx_01_fitted_slot_excitation_v1_fit.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--raw',required=True);p.add_argument('--fit-days',nargs='+',required=True);p.add_argument('--out',required=True);p.add_argument('--ridge',type=float,default=25.);p.add_argument('--iterations',type=int,default=20000);p.add_argument('--max-radius',type=float,default=.95);main(p.parse_args())
