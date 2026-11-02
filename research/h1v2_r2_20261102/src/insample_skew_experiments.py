"""Deliberate four-month H1V2 in-sample memorization, never deployable.
All features are quote-as-of and labels alone use the 30-second future.
"""
import json,time,hashlib,math
from pathlib import Path
import numpy as np
import lightgbm as lgb
R=Path('/mnt/data/h1v2/results');O=Path('/mnt/data/h1v2_r2/results')
MONTHS=('01','02','06','07')

def load():
    a=[];b=[];t=[];m=[]
    for month in MONTHS:
        with np.load(R/f'h1v2_{month}_causal_geometry_atlas.npz') as d:
            a.append(d['X'].copy());b.append(d['y'].copy());t.append(d['ts'].copy());m.extend([month]*len(d['y']))
    return np.concatenate(a),np.concatenate(b),np.concatenate(t),np.array(m)

def causal_interactions(x,t):
    w=np.array([.25,.5,1,5,15,30,45,60,300])
    a=x[:,:99].reshape(-1,9,11);r=a[:,:,0];order=a[:,:,1];loc=a[:,:,3];bp=a[:,:,6];ap=a[:,:,7];bl=a[:,:,8];al=a[:,:,9];eff=a[:,:,10]
    f=[x, 2*loc-1, (a[:,:,4]-a[:,:,5])/(r+.01), (bl-al)/(bl+al+1), (bp-ap)/(bp+ap+1),np.log1p(bp+ap)/np.log1p(w)[None,:],a[:,:,2]/(w*1000+1)[None,:],order*(2*loc-1), r/np.sqrt(w)[None,:],1-eff]
    for j in range(1,9):
        f.extend([((r[:,j]-r[:,j-1])/(r[:,j]+.01))[:,None],(order[:,j]-order[:,j-1])[:,None],(loc[:,j]-loc[:,j-1])[:,None]])
    h=(t//3600000)%24; dow=(t//86400000+3)%7
    for angle in (2*np.pi*h/24,2*np.pi*dow/7): f.extend([np.sin(angle)[:,None],np.cos(angle)[:,None]])
    return np.ascontiguousarray(np.column_stack(f),dtype=np.float32)

def wilson(correct,n):
    if not n:return 0.
    z2=1.96**2;p=correct/n
    return float((p+z2/(2*n)-1.96*math.sqrt(p*(1-p)/n+z2/(4*n*n)))/(1+z2/n))

def evaluate(p,y,months):
    side=1+np.argmax(p[:,1:3],axis=1);confidence=p[np.arange(len(y)),side]
    competitor=p[np.arange(len(y)),3-side];conditional=(confidence>=p[:,0]+.05)&(confidence>=competitor+.10)
    out={}
    for cutoff in (.5,.7,.8,.9,.95,.98,.99,.995,.999):
        valid=conditional&(confidence>=cutoff)
        n=int(valid.sum());good=int((valid&(side==y)).sum());neutral=int((valid&(y==0)).sum());wrong=int((valid&(y>0)&(side!=y)).sum())
        out[str(cutoff)]={'selected':n,'correct':good,'neutral':neutral,'wrong_direction':wrong,'precision':good/n if n else None,'wilson_lower':wilson(good,n),
           'month':{m:{'selected':int((valid&(months==m)).sum()),'correct':int((valid&(months==m)&(side==y)).sum())} for m in MONTHS}}
    return out

def train():
    O.mkdir(parents=True,exist_ok=True)
    x,y,ts,months=load(); assert len(y)==60000
    old=O/'H1V2_R2_INSAMPLE_MEMORIZATION.json'
    previous=json.loads(old.read_text()) if old.exists() else {}
    output={'intent':'TRAINING_SET_MEMORIZATION_ONLY_NOT_OUT_OF_SAMPLE','parent_source':'edce573d9c53b743dc5de1b0d741c81370af52c1',
      'n':len(y),'actual_labels_NO_GOOD_BUY_GOOD_SELL_GOOD':np.bincount(y,minlength=3).tolist(),'models':previous.get('models',{}),
      'safety':'No full-month decisions, no 80pct SYNTH volume verdict; all months seen during training; zero prospective claims.'}
    experiments=[('G0_low_capacity',70,15,90,False),('G1_high_capacity',300,63,12,False),('G2_bounded_overfit',460,63,6,False),('G3_motif_interactions',460,63,8,True)]
    for name,trees,leaves,minimum,motifs in experiments:
        if name in output['models']:continue
        st=time.monotonic();z=causal_interactions(x,ts) if motifs else x
        model=lgb.train(dict(objective='multiclass',num_class=3,num_leaves=leaves,min_data_in_leaf=minimum,max_depth=-1,learning_rate=.09,
                feature_fraction=1,force_col_wise=True,num_threads=4,verbosity=-1,seed=20261102),lgb.Dataset(z,label=y),num_boost_round=trees)
        p=model.predict(z,num_threads=4);gates=evaluate(p,y,months)
        path=O/f'{name}.txt';model.save_model(str(path))
        with path.open('rb') as fh:sha=hashlib.file_digest(fh,'sha256').hexdigest()
        output['models'][name]={'duration_sec':round(time.monotonic()-st,2),'num_features':z.shape[1],'trees':trees,'leaves':leaves,'min_leaf':minimum,
          'artifact':path.name,'sha256':sha,'gates':gates}
        (O/'H1V2_R2_INSAMPLE_MEMORIZATION.json').write_text(json.dumps(output,indent=2))
        print(json.dumps({'name':name,'s':output['models'][name]['duration_sec'],'features':z.shape[1],
           'gate80':gates['0.8'],'gate95':gates['0.95']}),flush=True)
    return output
if __name__=='__main__':train()
