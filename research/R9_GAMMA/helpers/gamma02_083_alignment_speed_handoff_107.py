import json,numpy as np
import stmr_janjul as j, stmr_base as c, gamma02_m1_density as gmd
import gamma02_ny17_quantum_minute_window_075 as w
import gamma02_083_global_child_cap_087 as cap
from gamma02_083_heat_parent_ownership_084 import renewal_owned
DAY=86400000

def prep_month(m):
 t,sa,sb,start,end=j.load_month(m,10);a,b=c.materialize(t,sa,sb);mid=((a.astype(np.int64)+b.astype(np.int64))//2).astype(np.int32);states=j.make_states(t,b,((8,21),(8,21),(8,21),(8,21)));return t,a,b,mid,*states,start,end

def run_month(m,hold_thr=12.,min_early=1,capn=703):
 def pp():return prep_month(m)
 gmd.prep=pp
 D,pei,pxi,pd,src,mins,disp=w.prep();t,a,b,mid,h4,h1,m15,m5=D[:8];start,end=D[-2],D[-1];pt=t[pei];dst=c.US_DST_START_2026_MS
 target=(pt>=start)&(pt<end);local=np.where(pt<dst,src==17,src==16)
 aligned=(h4[pei]!=0)&(h4[pei]==h1[pei])&(h1[pei]==m15[pei])&(m15[pei]==m5[pei])&(pd==h4[pei])
 me=target&local&aligned&(mins>=30)&(mins<=31)&(disp>=3.);ml=target&local&aligned&(mins>=33)&(mins<=39)&(disp>=5.)
 A=renewal_owned(t,a,b,pei[me],pxi[me],pd[me],500,250,0,1);B=renewal_owned(t,a,b,pei[ml],pxi[ml],pd[ml],1250,0,0,2)
 # early realized speed by UTC day before local :33 cutoff
 allow_days=set();daystats={}
 for day in np.unique(t[A[0]]//DAY if len(A[0]) else np.empty(0,np.int64)):
  day=int(day);# determine clock hour from day time
  probe=day*DAY+12*3600000;hour=16 if probe>=dst else 17;cut=day*DAY+(hour*60+33)*60000
  mday=(t[A[0]]//DAY==day)&(t[A[1]]<=cut);n=int(np.sum(mday));ah=float(np.mean(A[5][mday])) if n else 1e9;net=float(np.sum(A[4][mday])) if n else 0.
  daystats[day]=(n,ah,net)
  if n>=min_early and ah<=hold_thr:allow_days.add(day)
 lk=[]
 for k in range(len(B[0])):
  if int(t[int(B[0][k])]//DAY) in allow_days:lk.append(k)
 lk=np.asarray(lk,np.int64)
 E=np.concatenate((A[0],B[0][lk]));X=np.concatenate((A[1],B[1][lk]));ER=np.concatenate((A[2],B[2][lk]));Dd=np.concatenate((A[3],B[3][lk]));P=np.concatenate((A[4],B[4][lk]));H=np.concatenate((A[5],B[5][lk]));S=np.concatenate((np.ones(len(A[0]),np.int8),np.full(len(lk),2,np.int8)))
 if len(E)==0:return {'month':m,'net':0.,'trades':0,'allowed_days':0}
 o=np.lexsort((np.arange(len(E)),E));Q=(E[o],X[o],ER[o],Dd[o],P[o],H[o],S[o]);r,B2=cap.one(Q,capn);z=cap.exact(D,B2,r);z.update(month=m,hold_thr=hold_thr,min_early=min_early,early_parents=int(me.sum()),late_parents_raw=int(ml.sum()),late_children_kept=int(len(lk)),allowed_days=len(allow_days),daystats={str(k):v for k,v in daystats.items()});return z
if __name__=='__main__':
 import argparse;ap=argparse.ArgumentParser();ap.add_argument('--hold',type=float,required=True);ap.add_argument('--out',required=True);z=ap.parse_args();rows=[]
 for m in (1,2,3):
  r=run_month(m,z.hold);rows.append(r);print(json.dumps({k:r.get(k) for k in ['month','net','trades','pf','win','expectancy','avg_hold_s','equity_dd','maxopen_exact','early_parents','late_parents_raw','late_children_kept','allowed_days']}),flush=True)
 obj={'candidate':'GAMMA02_083_ALIGNMENT_SPEED_HANDOFF_107','hold_thr':z.hold,'cum_net':sum(x.get('net',0) for x in rows),'cum_trades':sum(x.get('trades',0) for x in rows),'months':rows};open(z.out,'w').write(json.dumps(obj,indent=2))