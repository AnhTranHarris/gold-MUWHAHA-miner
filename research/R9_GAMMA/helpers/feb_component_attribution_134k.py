import sys,json,heapq
from pathlib import Path
import numpy as np
sys.path[:0]=['/mnt/data','/mnt/data/gamma02_jan_repro']
import feb_vertical_stack_134b as V
B=Path('/mnt/data/gamma02_jan_repro')
def loadq(fn):z=np.load(B/fn);Q=tuple(z[x] for x in ['E','X','R','D','P','H']);z.close();return Q
def q(z,pre):return tuple(z[pre+'_'+x] for x in ['E','X','R','D','P','H'])
z=np.load(B/'feb_baseline_components_133b.npz');BB={k:z[k] for k in z.files};z.close()
streams=[('NATIVE_PF10',loadq('feb_native_pf10_stream_134c.npz')),('COVERAGE',q(BB,'COV')),('HOURLY_LEARNER',loadq('feb_learner_D_stream_133c.npz')),('COLD',q(BB,'COLD')),('ASIA_REGIME',loadq('feb_asia_regime_filtered_stream_134f.npz')),('LATE21',q(BB,'LATE21_LONG')),('RECOVERY_PF4',loadq('feb_recovery_PF4_stream_134f.npz')),('HOURLY_RESIDUAL_PF4',loadq('feb_residual_hourly_PF4_134h.npz'))]
# supplemental dedup, preserving stream priority and labels
seen=set(); vals=[[] for _ in range(6)]; lab=[]
for si,(name,Q) in enumerate(streams):
 for k,e in enumerate(Q[0]):
  if int(e) in seen: continue
  seen.add(int(e));lab.append(name)
  for j in range(6):vals[j].append(Q[j][k])
dtypes=[np.int64,np.int64,np.int64,np.int8,float,float];S=tuple(np.asarray(vals[j],dtype=dtypes[j]) for j in range(6));lab=np.asarray(lab,object)
# supplemental cap640 as in 134J
E,X,R,D,P,H=S;o=np.argsort(E,kind='stable');S=tuple(x[o] for x in S);lab=lab[o];heap=[];keep=[]
for k,now in enumerate(S[0]):
 while heap and heap[0][0]<=now:heapq.heappop(heap)
 if len(heap)>=768:continue
 keep.append(k);heapq.heappush(heap,(int(S[1][k]),k))
kk=np.asarray(keep);S=tuple(x[kk] for x in S);lab=lab[kk]
wd=loadq('feb_wd_L30_C384_134e.npz')

def run(capn):
 # combine wd + supp with labels then cap
 E=np.concatenate([wd[0],S[0]]);X=np.concatenate([wd[1],S[1]]);R=np.concatenate([wd[2],S[2]]);D=np.concatenate([wd[3],S[3]]);P=np.concatenate([wd[4],S[4]]);H=np.concatenate([wd[5],S[5]]);L=np.concatenate([np.full(len(wd[0]),'WATCHDOG',object),lab])
 o=np.lexsort((np.arange(len(E)),E));E,X,R,D,P,H,L=[z[o] for z in (E,X,R,D,P,H,L)];heap=[];keep=[]
 for k,now in enumerate(E):
  while heap and heap[0][0]<=now:heapq.heappop(heap)
  if len(heap)>=capn:continue
  keep.append(k);heapq.heappush(heap,(int(X[k]),k))
 kk=np.asarray(keep);P=P[kk];L=L[kk];out={}
 for name in np.unique(L):
  p=P[L==name];gp=float(p[p>0].sum());gl=float(p[p<=0].sum());out[str(name)]={'net':float(p.sum()),'trades':int(len(p)),'gross_loss':gl,'pf':float(gp/-gl if gl<0 else 999),'win':float(np.mean(p>0))}
 return out
obj={str(c):run(c) for c in (384,600)};(B/'feb_component_attribution_134k.json').write_text(json.dumps(obj,indent=2));print(json.dumps(obj,indent=2))