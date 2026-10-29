#!/usr/bin/env python3
"""Unsupervised multiresolution trend manifold on original t0 information.
This is diagnostic topology discovery, NOT yet an authorized veto model.
"""
import io,json,zipfile,pathlib,argparse,hashlib
import numpy as np
from sklearn.cluster import MiniBatchKMeans
from sklearn.preprocessing import RobustScaler
from r120_multiclock_geometry import ROOT,ORIG,FEATURES

# All geometries are computed strictly as-of t0 in the frozen source-native engine.
SC=6;P=11

def learned_geometry(X):
    # 6 scale trend/curvature/efficiency/support/contact/quote pressure; 3 overlapping sessions.
    use=[]
    for i in range(6):
        j=i*11
        use.extend([j+0,j+1,j+2,j+3,j+4,j+5,j+7,j+8,j+10])
    for z in range(3):
        s=66+6*z
        use.extend([s,s+1,s+2,s+3,s+4])
    use.extend([84,85,86,87,88,89])
    raw=X[:,use].astype(np.float32)
    # Causal dynamic grid nodes at 0,1/4,1/2,3/4,1 of rolling completed high-low interval.
    # Coordinates are price-normalized, not a guessed static-dollar grid.
    pos=np.stack([X[:,i*11+4] for i in range(6)],axis=1)
    nearest=np.abs(pos*4-np.round(pos*4))
    trend=np.stack([X[:,i*11] for i in range(6)],axis=1)
    grid_signed=trend*(1.-nearest)
    # Interscale path frustration: pairwise signed-slope disagreement L2.
    disagree=np.sqrt(np.mean((trend[:,1:]-trend[:,:-1])**2,axis=1))
    H=np.column_stack([raw,nearest,grid_signed,disagree]).astype(np.float32)
    return H, ['state_'+FEATURES[k] for k in use]+[f'grid_quartile_distance_{i}' for i in range(6)]+[f'grid_trend_phase_{i}' for i in range(6)]+['interscale_path_frustration']

def orig_labels(m):
    with zipfile.ZipFile(ORIG) as z:
        with np.load(io.BytesIO(z.read(f'F395_S14_dukascopy_{m}_FROZEN_ORIGINAL_EVENT_MASK.npz'))) as q:
            return {k:q[k] for k in q.files}

def cluster_census(labels, truth, mask):
    tbl=[]
    for z in np.unique(labels):
        ix=(labels==z)&mask
        right=int(np.count_nonzero(ix&(truth==0)))
        opp=int(np.count_nonzero(ix&(truth==1)))
        neut=int(np.count_nonzero(ix&(truth==2)))
        n=right+opp+neut
        if not n:continue
        tbl.append(dict(phase=int(z),total=n,right=right,opposite=opp,neutral=neut,wrong_rate=(opp+neut)/n,ratio=(opp+neut)/max(right,1)))
    return sorted(tbl,key=lambda r:(r['wrong_rate'],r['total']),reverse=True)

def main():
    pa=argparse.ArgumentParser();pa.add_argument('--months',nargs='+',default=['01','02']);args=pa.parse_args()
    o=orig_labels('01');truth=o['truth'];
    X=np.load(ROOT/'R120_01_MULTICLOCK_GEOMETRY.npy',mmap_mode='r')
    assert len(X)==len(truth)
    train=np.arange(len(X))<int(.60*len(X))
    cal=(np.arange(len(X))>=int(.60*len(X)))&(np.arange(len(X))<int(.80*len(X)))
    val=(np.arange(len(X))>=int(.80*len(X)))&(np.arange(len(X))<int(.90*len(X)))
    # Existing outcomes t+33.001 sec; split embargo stricter than 60s (on both edges).
    t=o['t'];bound=[t[int(.60*len(X))],t[int(.80*len(X))],t[int(.90*len(X))]]
    train &= t<bound[0]-60000
    cal &= (t>bound[0]+60000)&(t<bound[1]-60000)
    val &= (t>bound[1]+60000)&(t<bound[2]-60000)
    H,features=learned_geometry(X)
    rng=np.random.default_rng(120)
    fit_idx=rng.choice(np.flatnonzero(train),size=min(45000,int(train.sum())),replace=False)
    scale=RobustScaler(quantile_range=(10,90)).fit(H[fit_idx])
    # Preconditioner is learned FIT ONLY; extreme feature magnitudes clipped from FIT.
    train_geom=np.clip(scale.transform(H[fit_idx]),-8,8)
    model=MiniBatchKMeans(n_clusters=24,random_state=120,batch_size=2048,n_init=2,max_iter=85).fit(train_geom)
    output={'description':'R120 causal six-clock/session geometry unlabelled phase topology; exploratory original-label census only, NOT certified foresight, not real trade economics',
      'fit_data':'DK January first60% only with 60s temporal embargo; embeddings trained unsupervised; phase-risk census uses original labels retrospectively',
      'n_dimensions':len(features),'n_phases':24,'features':features,'months':{},
      'source_ref':'Original F395 immutable source-event index; no futures as inference inputs',
      'limits':'No actual traded volume, L2, true DST session hours or missing F234 overlap input; January original source historically exposed'}
    for month in args.months:
        xm=np.load(ROOT/f'R120_{month}_MULTICLOCK_GEOMETRY.npy',mmap_mode='r')
        om=orig_labels(month)
        hm,_=learned_geometry(xm)
        # Predict in bounded chunks; avoid any enormous dense features or DRAM duplication.
        pred=np.empty(len(xm),dtype=np.int8)
        for s in range(0,len(xm),40000):
            pred[s:s+40000]=model.predict(np.clip(scale.transform(hm[s:s+40000]),-8,8))
        np.save(ROOT/f'R120_{month}_UNSUPERVISED_PHASES.npy',pred)
        maskdict={'full':np.ones(len(pred),dtype=bool)}
        if month=='01':maskdict.update({'FIT':train,'CAL':cal,'VAL':val})
        output['months'][month]={k:{'count':int(mask.sum()),'census':cluster_census(pred,om['truth'],mask)} for k,mask in maskdict.items()}
        print('ATLAS',month,len(pred),'overall',sum(q['opposite']+q['neutral'] for q in output['months'][month]['full']['census']),flush=True)
    (ROOT/'R120_FOUR_CLOCK_PHASE_ATLAS_RESEARCH.json').write_text(json.dumps(output,indent=2))
    import joblib
    joblib.dump({'scaler':scale,'model':model,'features':features},ROOT/'R120_FIT_ONLY_UNSUPERVISED_ATLAS.joblib')
    print('SAVED',flush=True)
if __name__=='__main__':main()