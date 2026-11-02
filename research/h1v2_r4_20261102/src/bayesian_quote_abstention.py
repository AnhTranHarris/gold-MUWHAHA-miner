"""R4 hierarchical empirical-Bayes selective BUY/SELL/WAIT competitor.

No independent action is authorized without a positive spread-adjusted
expected response and stringent Wilson directional success bound. Posterior
is deliberately smoothed to eliminate singleton memorization. Four-month
contaminated fit is separately identified from July-withheld transfer.
"""
from pathlib import Path
import json
import numpy as np
from four_month_competing_risks import load,MONTHS,wilson
ROOT=Path('/mnt/data/h1v2_r4/results')

def cells(d,degree='coarse'):
 b,path,marked,k,t=d
 h=((t//3600000)%24).astype(np.int32)
 session=np.where((h>=12)&(h<=17),2,np.where((h>=6)&(h<=11),1,0))
 spread=np.where(b[:,99]<.65,0,np.where(b[:,99]<.95,1,2))
 # Observed signed event flows: mark classes plus both-up/down. Only past.
 one=marked[:,6:12]; five=marked[:,12:18]
 signed1=(one[:,0]-one[:,1]+one[:,2]-one[:,3]+2*(one[:,4]-one[:,5]))
 signed5=(five[:,0]-five[:,1]+five[:,2]-five[:,3]+2*(five[:,4]-five[:,5]))
 signed1=np.where(signed1>2,2,np.where(signed1<-2,0,1))
 signed5=np.where(signed5>6,2,np.where(signed5<-6,0,1))
 displacement=path[:,6*3]
 trend=np.where(displacement>.3,2,np.where(displacement<-.3,0,1))
 if degree=='coarse':return ((session*3+spread)*3+signed5).astype(np.int32),81
 if degree=='fine':return ((((session*3+spread)*3+signed5)*3+signed1)*3+trend).astype(np.int32),729
 raise ValueError(degree)

def fit(data,months,degree,alpha):
 ncell=81 if degree=='coarse' else 729
 # Global prior using *training month* data only, not future labels.
 gs=np.zeros(4,np.float64);tables=np.zeros((2,ncell,4),np.int32)
 for m in months:
  d=data[m];keys,_=cells(d,degree);classes=d[3]
  for side in range(2):
   np.add.at(tables,(np.full(len(keys),side),keys,classes[:,side]),1)
   gs+=np.bincount(classes[:,side],minlength=4)
 global_prior=(gs+1)/(gs.sum()+4)
 return tables,global_prior,alpha

def score(data,model,degree,month):
 tables,prior,alpha=model;d=data;keys,n=cells(d,degree);k=d[3]
 probs=(tables[:,keys,:]+alpha*prior)/(tables[:,keys,:].sum(axis=2,keepdims=True)+alpha)
 probs=np.transpose(probs,(1,0,2));utility=probs[:,:,3]-1.5*probs[:,:,0]-.3*probs[:,:,1]
 side=np.argmax(utility,axis=1);s=utility[np.arange(len(k)),side];chosen=k[np.arange(len(k)),side]
 top=[]
 for frac in (.01,.05,.10):
  idx=np.argsort(s)[-int(frac*len(k)):];classes=np.bincount(chosen[idx],minlength=4)
  top.append({'top':frac,'n':len(idx),'strong':int(classes[3]),'wrong':int(classes[0]),'neutral':int(classes[1]),'weak':int(classes[2]),'precision':float(classes[3]/len(idx)),'wilson':float(wilson(classes[3],len(idx)))})
 return {'month':month,'top':top,'posterior_max_strong':float(probs[:,:,3].max()),'count_positive_utility':int((s>0).sum())}

def run():
 data=load(ROOT);out=[]
 for deg in ('coarse','fine'):
  for alpha in (20.,100.):
   for group in (('01','02','06'),MONTHS):
    model=fit(data,group,deg,alpha)
    months={m:score(data[m],model,deg,m) for m in MONTHS}
    out.append({'degree':deg,'alpha':alpha,'train_months':list(group),'months':months,'audit':'resubstitution' if len(group)==4 else 'july_heldout'})
    print(deg,alpha,group,'July top1% precision',months['07']['top'][0]['precision'],'max post',months['07']['posterior_max_strong'],flush=True)
 (ROOT/'R4_HIERARCHICAL_BAYESIAN_ABSTENTION.json').write_text(json.dumps({'science':'Dirichlet shrinkage of four disjoint action classes; quote-mark data only; no broker liquidity prediction','results':out,'status':'RESEARCH_NOT_APPROVED'},indent=2))
if __name__=='__main__':run()
