"""Out-of-time verification for fitted discrete six-mark slot excitation."""
from __future__ import annotations
import argparse,json
from pathlib import Path
import numpy as np
from sklearn.metrics import mean_poisson_deviance,roc_auc_score
from build_repaired_matrix import load_raw
from fitted_slot_excitation import MARKS,slot_dataset,design_matrix,predict

def ev(t,bid,ask,day,coef,scales,session_means):
 slot,Y,S,sess=slot_dataset(t,bid,ask,day);X,_=design_matrix(S,sess,scales);P=predict(X,coef);B=np.maximum(1e-9,session_means[sess]);mse=float(np.mean((Y-P)**2));bmse=float(np.mean((Y-B)**2));dev=[];bdev=[]
 for j in range(6):dev.append(float(mean_poisson_deviance(Y[:,j],P[:,j])));bdev.append(float(mean_poisson_deviance(Y[:,j],B[:,j])))
 up=Y[:,0]+Y[:,2];down=Y[:,1]+Y[:,3];m=up!=down;score=(P[:,0]+P[:,2])-(P[:,1]+P[:,3]);y=(up>down).astype(np.uint8);sw=Y[:,4];sn=Y[:,5];ms=sw!=sn;sscore=P[:,5]-P[:,4];ys=(sn>sw).astype(np.uint8)
 return dict(day=day,slots=len(Y),mse=mse,session_baseline_mse=bmse,mse_improvement=(bmse-mse)/bmse,mean_poisson_deviance=float(np.mean(dev)),session_baseline_mean_poisson_deviance=float(np.mean(bdev)),poisson_deviance_improvement=(np.mean(bdev)-np.mean(dev))/np.mean(bdev),per_mark={MARKS[j]:dict(deviance=dev[j],baseline_deviance=bdev[j]) for j in range(6)},directional_unequal_slots=int(m.sum()),directional_auc=float(roc_auc_score(y[m],score[m])),spread_unequal_slots=int(ms.sum()),spread_narrow_auc=float(roc_auc_score(ys[ms],sscore[ms])))

def main(a):
 t,bid,ask=load_raw(Path(a.raw),'coinexx','01');z=np.load(Path(a.model));r=dict(identity='R9_V2_FITTED_SLOT_EXCITATION_V1_EVALUATION',calibration=ev(t,bid,ask,a.cal_day,z['coef'],z['scales'],z['session_means']),holdout=ev(t,bid,ask,a.holdout_day,z['coef'],z['scales'],z['session_means']),admit_as_model_feature=False,status='PENDING_INCREMENTAL_MODEL_TEST')
 Path(a.out).mkdir(parents=True,exist_ok=True);(Path(a.out)/'coinexx_01_fitted_slot_excitation_v1_evaluation.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--raw',required=True);p.add_argument('--model',required=True);p.add_argument('--out',required=True);p.add_argument('--cal-day',default='2026-01-08');p.add_argument('--holdout-day',default='2026-01-14');main(p.parse_args())
