"""Report training memorization vs July left-out directional and abstention audits."""
import json
from pathlib import Path
import numpy as np
import lightgbm as lgb
from insample_skew_experiments import load,causal_interactions,wilson
O=Path('/mnt/data/h1v2_r2/results')

def metrics(p,y):
 n=len(y);s=np.argmax(p[:,1:3],axis=1)+1;c=np.max(p[:,1:3],axis=1)
 opposite=p[np.arange(n),3-s];rule=(c>=p[:,0]+.05)&(c>=opposite+.10)
 o={'n':n,'good_base_rate':float((y!=0).mean()),'gates':{}}
 for t in (.2,.3,.4,.5,.6,.7,.8):
  mask=rule&(c>=t);cnt=int(mask.sum());good=int((mask&(s==y)).sum());o['gates'][str(t)]={'n':cnt,'correct':good,'neutral':int((mask&(y==0)).sum()),'incorrect_direction':int((mask&(y!=0)&(s!=y)).sum()),'precision':good/cnt if cnt else None,'wilson_lower':wilson(good,cnt)}
 for frac in (.01,.05):
  k=int(n*frac);ix=np.argsort(-c)[:k];o[f'top{int(frac*100)}pct']={'n':k,'correct':int(np.sum(s[ix]==y[ix])),'neutral':int((y[ix]==0).sum()),'wrong_direction':int(((y[ix]!=0)&(s[ix]!=y[ix])).sum())}
 return o

def run():
 x,y,ts,mon=load();o={'purpose':'falsify extreme in-sample skew when month unseen','models':{}}
 for name,X in [('G2_bounded_overfit',x),('G5_july_never_trained_motifs',causal_interactions(x,ts))]:
  p=lgb.Booster(model_file=str(O/f'{name}.txt')).predict(X,num_threads=4)
  o['models'][name]={'all':metrics(p,y),'months':{m:metrics(p[mon==m],y[mon==m]) for m in ('01','02','06','07')}}
 (O/'H1V2_R2_MEMORIZATION_VS_TRANSFER.json').write_text(json.dumps(o,indent=2))
 for name,d in o['models'].items():
  print(name,'all @.5',d['all']['gates']['0.5'],'july @.5',d['months']['07']['gates']['0.5'],'july top5',d['months']['07']['top5pct'],flush=True)
if __name__=='__main__':run()
