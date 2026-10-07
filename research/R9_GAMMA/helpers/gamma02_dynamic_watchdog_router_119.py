import sys,json,heapq,numpy as np
import stmr_janjul as j, stmr_base as c, gamma02_m1_density as gmd
import gamma02_ny17_quantum_minute_window_075 as w
import gamma02_083_global_child_cap_087 as cap
from gamma02_083_heat_parent_ownership_084 import renewal_owned
DAY=86400000

def prep_month(m):
 t,sa,sb,start,end=j.load_month(m,10);a,b=c.materialize(t,sa,sb);mid=((a.astype(np.int64)+b.astype(np.int64))//2).astype(np.int32);states=j.make_states(t,b,((8,21),(8,21),(8,21),(8,21)));return t,a,b,mid,*states,start,end

def local_minute(t):
 off=np.where(t<c.US_DST_START_2026_MS,-300,-240);return (((t//60000)+off)%1440).astype(np.int16)

def cell_admit(t,a,b,pei,pxi,pd,jj,n_consec,hold_thr):
 # precompute q1.25 children for every parent, then causally admit parent campaigns using realized exits only
 A=renewal_owned(t,a,b,pei[jj],pxi[jj],pd[jj],1250,0,0,1)
 E,X,R,Dd,P,H,O=A[:7]
 if len(jj)==0 or len(E)==0:return np.empty(0,np.int64),dict(parents=len(jj),admitted=0,children=0,relocks=0,unlocks=0)
 by=[[] for _ in range(len(jj))]
 for ci,oo in enumerate(O):by[int(oo)].append(ci)
 porder=np.argsort(t[pei[jj]],kind='stable')
 # scheduled realized exits from admitted parents: heap(exit_time, child_index)
 heap=[];admitted=np.zeros(len(jj),dtype=np.bool_);streak=0;gate=False;relocks=0;unlocks=0
 # first chronological parent always scouts
 first=int(porder[0]);admitted[first]=True
 for ci in by[first]:heapq.heappush(heap,(int(t[X[ci]]),int(ci)))
 for po in porder[1:]:
  po=int(po); now=int(t[pei[jj[po]]])
  while heap and heap[0][0]<=now:
   _,ci=heapq.heappop(heap); good=(P[ci]>0 and H[ci]<=hold_thr)
   old=gate
   if good: streak+=1
   else: streak=0
   gate=streak>=n_consec
   if gate and not old:unlocks+=1
   if old and not gate:relocks+=1
  if gate:
   admitted[po]=True
   for ci in by[po]:heapq.heappush(heap,(int(t[X[ci]]),int(ci)))
 keep=np.nonzero(admitted[O])[0]
 stats=dict(parents=int(len(jj)),admitted=int(admitted.sum()),children=int(len(keep)),relocks=int(relocks),unlocks=int(unlocks))
 return keep,stats,A

def run_month(m,n_consec=4,hold_thr=60.,capn=703):
 def pp():return prep_month(m)
 gmd.prep=pp
 D,pei,pxi,pd,src,mins,disp=w.prep();t,a,b,mid,h4,h1,m15,m5=D[:8];start,end=D[-2],D[-1];pt=t[pei]
 lm=local_minute(pt);lh=lm//60;lmin=lm%60;target=(pt>=start)&(pt<end);macro=(h4[pei]!=0)&(h4[pei]==h1[pei])&(pd==h4[pei]);base=target&macro&(lh>=12)&(lh<=13)
 sigcode=((h4[pei]+1)*81+(h1[pei]+1)*27+(m15[pei]+1)*9+(m5[pei]+1)*3+(pd+1)).astype(np.int16);keys=np.stack((pt//DAY,lh,lmin//10,sigcode),axis=1);cand=np.nonzero(base)[0];u=np.unique(keys[cand],axis=0) if len(cand) else np.empty((0,4),np.int64)
 parts=[];cells=[]
 for key in u:
  day,hh,b10,sc=[int(x) for x in key];mask=base&(keys[:,0]==day)&(keys[:,1]==hh)&(keys[:,2]==b10)&(keys[:,3]==sc);jj=np.nonzero(mask)[0]
  if not len(jj):continue
  res=cell_admit(t,a,b,pei,pxi,pd,jj,n_consec,hold_thr)
  if len(res)==2: continue
  keep,st,A=res;E,X,R,Dd,P,H,O=A[:7]
  if len(keep):parts.append((E[keep],X[keep],R[keep],Dd[keep],P[keep],H[keep],np.full(len(keep),2,np.int8)))
  st.update(day=day,hour=hh,bin=b10,sigcode=sc);cells.append(st)
 if not parts:return dict(month=m,net=0.,trades=0,cells=len(cells),cell_stats=cells)
 arr=[np.concatenate([p[k] for p in parts]) for k in range(7)];o=np.lexsort((np.arange(len(arr[0])),arr[0]));Q=tuple(x[o] for x in arr);r,B=cap.one(Q,capn);r.update(month=m,n_consec=n_consec,hold_thr=hold_thr,cells=len(cells),admitted_parents=sum(x['admitted'] for x in cells),total_parents=sum(x['parents'] for x in cells),relocks=sum(x['relocks'] for x in cells),unlocks=sum(x['unlocks'] for x in cells),cell_stats=cells);return r
if __name__=='__main__':
 m=int(sys.argv[1]);out=sys.argv[2];n=int(sys.argv[3]);h=float(sys.argv[4]);r=run_month(m,n,h);json.dump(r,open(out,'w'),indent=2);print(json.dumps({k:r.get(k) for k in ['month','net','trades','pf','win','expectancy','avg_hold_s','admitted_parents','total_parents','unlocks','relocks','maxopen_event','skips']}))
