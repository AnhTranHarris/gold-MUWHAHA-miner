import sys,json,numpy as np
import stmr_janjul as j, stmr_base as c, gamma02_m1_density as gmd
import gamma02_ny17_quantum_minute_window_075 as w
import gamma02_083_global_child_cap_087 as cap
from gamma02_083_heat_parent_ownership_084 import renewal_owned

def prep_month(m):
 t,sa,sb,start,end=j.load_month(m,10);a,b=c.materialize(t,sa,sb);mid=((a.astype(np.int64)+b.astype(np.int64))//2).astype(np.int32);states=j.make_states(t,b,((8,21),(8,21),(8,21),(8,21)));return t,a,b,mid,*states,start,end

def rolling_mean(x,N):
 x=np.asarray(x,dtype=float);cs=np.r_[0.,np.cumsum(x)];out=np.empty(len(x))
 for i in range(len(x)):
  j=max(0,i-N+1);out[i]=(cs[i+1]-cs[j])/(i-j+1)
 return out

def run_month(m,N=64,te=13.,tl=65.,child_cap=703):
 def pp():return prep_month(m)
 gmd.prep=pp;D,pei,pxi,pd,src,mins,disp=w.prep();t,a,b=D[:3]
 me=(src==17)&(mins>=30)&(mins<=31)&(disp>=3.);ml=(src==17)&(mins>=33)&(mins<=39)&(disp>=5.)
 ie=np.nonzero(me)[0];il=np.nonzero(ml)[0];pe=pei[ie];pl=pei[il]
 ce=pe-np.searchsorted(t,t[pe]-1000,side='left');cl=pl-np.searchsorted(t,t[pl]-5000,side='left')
 re=rolling_mean(ce,N);rl=rolling_mean(cl,N);ie=ie[re>=te];il=il[rl>=tl]
 A=renewal_owned(t,a,b,pei[ie],pxi[ie],pd[ie],500,250,0,1);B=renewal_owned(t,a,b,pei[il],pxi[il],pd[il],1250,0,0,2)
 E=np.concatenate((A[0],B[0]));X=np.concatenate((A[1],B[1]));R=np.concatenate((A[2],B[2]));Dd=np.concatenate((A[3],B[3]));P=np.concatenate((A[4],B[4]));H=np.concatenate((A[5],B[5]));S=np.concatenate((A[7],B[7]));o=np.lexsort((np.arange(len(E)),E));Q=(E[o],X[o],R[o],Dd[o],P[o],H[o],S[o]);r,C=cap.one(Q,child_cap);r.update(month=m,N=N,early_roll_threshold=te,late_roll_threshold=tl,early_selected=int(len(ie)),late_selected=int(len(il)),early_total=int(np.sum(me)),late_total=int(np.sum(ml)),early_roll_min=float(re.min()) if len(re) else 0,early_roll_max=float(re.max()) if len(re) else 0,late_roll_min=float(rl.min()) if len(rl) else 0,late_roll_max=float(rl.max()) if len(rl) else 0);return r
if __name__=='__main__':
 m=int(sys.argv[1]);out=sys.argv[2];r=run_month(m);open(out,'w').write(json.dumps(r,indent=2));print(json.dumps({k:r[k] for k in ['month','net','trades','pf','win','expectancy','avg_hold_s','early_net','late_net','early_trades','late_trades','early_selected','late_selected','skips','all_metric_crossover']}))
