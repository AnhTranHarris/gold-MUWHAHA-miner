#!/usr/bin/env python3
"""FIT-only multiscale geometric regime factorization; descriptive source-forensic census.

A product manifold of microstructure and higher-timeframe trend with 12x24
unsupervised states, plus session and original side. This is an engineered trend
state for complex filters, NOT a validated rejection policy.
"""
import json,io,zipfile,joblib,numpy as np
from sklearn.preprocessing import RobustScaler
from sklearn.cluster import MiniBatchKMeans
from r120_multiclock_geometry import ROOT,ORIG
from r120_regime_atlas import learned_geometry,cluster_census

WIDTHS=['M1','M5','M15','H1']

def htfsignature(X):
 # Higher TF state: 4 clocks, no current partial bars; directional trend4,8 and accel;
 # midrange support rank, grid proximity, volatility, quote counts, age.
 vals=[]
 for j in range(4):
  u=j*9
  vals.extend([u,u+1,u+2,u+3,u+4,u+5,u+6,u+7])
 raw=X[:,vals].astype(np.float32)
 slopes=X[:,[0,9,18,27]].astype(np.float32)
 mean=slopes.mean(axis=1)
 # Cross-scale trend phase-alignment; macroscopic conflict no future labels.
 coh=(np.sum(slopes,axis=1)**2)/(4*np.sum(slopes**2,axis=1)+1e-6)
 frustration=np.sqrt(np.mean(np.diff(slopes,axis=1)**2,axis=1))
 return np.column_stack([raw,mean,coh,frustration]).astype(np.float32)

def labels(m):
 with zipfile.ZipFile(ORIG) as z:
  with np.load(io.BytesIO(z.read(f'F395_S14_dukascopy_{m}_FROZEN_ORIGINAL_EVENT_MASK.npz'))) as a:
   return {k:a[k] for k in a.files}

def full_census(z,truth,minn=0):
 counts=[]
 for k in np.unique(z):
  mask=z==k
  n=mask.sum()
  if n<minn:continue
  right=int(np.sum(mask&(truth==0)))
  opp=int(np.sum(mask&(truth==1)))
  neut=int(np.sum(mask&(truth==2)))
  counts.append({'state':int(k),'n':int(n),'right':right,'wrong':opp+neut,'opposite':opp,'neutral':neut,'wrong_share':(opp+neut)/max(n,1),'ratio':(opp+neut)/max(right,1)})
 return counts

def main():
 o=labels('01');y=o['truth'];t=o['t']
 n=len(y);boundary=t[int(n*.60)];fit=(np.arange(n)<int(.6*n))&(t<boundary-60000)
 X=np.load(ROOT/'R120_01_COMPLETED_HTF_BRIDGE.npy',mmap_mode='r')
 H=htfsignature(X)
 rng=np.random.default_rng(120)
 f=rng.choice(np.flatnonzero(fit),size=min(42000,int(fit.sum())),replace=False)
 scaler=RobustScaler(quantile_range=(10,90)).fit(H[f])
 kmeans=MiniBatchKMeans(n_clusters=12,random_state=120,batch_size=2048,n_init=2,max_iter=65).fit(np.clip(scaler.transform(H[f]),-8,8))
 model={'scaler':scaler,'kmeans':kmeans,'meaning':'12 higher TF regimes FIT-only, product 24 micro phase FIT-only'}
 joblib.dump(model,ROOT/'R120_FIT_ONLY_HFT_STATE_MAP.joblib')
 totals=[]
 for mo in ['01','02','06','07']:
  x=np.load(ROOT/f'R120_{mo}_COMPLETED_HTF_BRIDGE.npy',mmap_mode='r')
  micro=np.load(ROOT/f'R120_{mo}_UNSUPERVISED_PHASES.npy',mmap_mode='r')
  states=np.empty(len(x),dtype=np.uint16)
  for i in range(0,len(x),50000):
   ht=htfsignature(x[i:i+50000]);mac=kmeans.predict(np.clip(scaler.transform(ht),-8,8))
   states[i:i+50000]=micro[i:i+50000].astype(np.uint16)*12+mac.astype(np.uint16)
  np.save(ROOT/f'R120_{mo}_TENSOR_PHASES.npy',states)
  lab=labels(mo);cs=full_census(states,lab['truth'])
  totals.append({'month':mo,'n':len(x),'n_states':len(cs),'counts':cs})
  print('TENSOR',mo,'events',len(x),'states',len(cs),flush=True)
 source={'model':'Six native 0.25-30s OHLC + four completed M1/M5/M15/H1 trend geometries, three overlapping session anchors; FIT-only 24x12 product regime atlas','status':'UNAPPROVED science; no filter/loss claim','source':'Original source-exact Dukascopy 4-month original F395 masks and SHA raw; all event t0 states causal, original outcomes diagnostic labels only','results':totals}
 (ROOT/'R120_PRODUCT_MANIFOLD_288_STATE_ATLAS.json').write_text(json.dumps(source,indent=2))
 # Cross-month support for each exact structural state - diagnostics, NOT trained veto.
 d={v['month']:{q['state']:q for q in v['counts']} for v in totals}
 recurring=[]
 for state in range(24*12):
  r=[d[m].get(state,{'n':0,'right':0,'wrong':0,'wrong_share':0}) for m in ['01','02','06','07']]
  if min(v['n'] for v in r)>=100:
   recurring.append({'state':state,'n':sum(x['n'] for x in r),'wrong':sum(x['wrong'] for x in r),'right':sum(x['right'] for x in r),'min_month_wrong_rate':min(x['wrong_share'] for x in r),'rates':[x['wrong_share'] for x in r]})
 recurring.sort(key=lambda x:(x['min_month_wrong_rate'],x['wrong']),reverse=True)
 (ROOT/'R120_PRODUCT_MANIFOLD_RECURRING_STATES.json').write_text(json.dumps({'min_support_per_month':100,'n_recurring':len(recurring),'recurring':recurring,'no_deployment_claim':True},indent=2))
 for i in recurring[:6]:print('RECURRING',i['state'],i['n'],i['wrong'],i['right'],'minWrongRate',round(i['min_month_wrong_rate'],3),flush=True)
if __name__=='__main__':main()