import sys,json,numpy as np
sys.path.insert(0,'/mnt/data')
import stmr_janjul as j, stmr_base as c, gamma02_m1_density as gmd
import gamma02_ny17_quantum_minute_window_075 as w
import gamma02_083_global_child_cap_087 as cap
from gamma02_083_heat_parent_ownership_084 import renewal_owned

def prep_month(m):
 t,sa,sb,start,end=j.load_month(m,10);a,b=c.materialize(t,sa,sb);mid=((a.astype(np.int64)+b.astype(np.int64))//2).astype(np.int32);states=j.make_states(t,b,((8,21),(8,21),(8,21),(8,21)));return t,a,b,mid,*states,start,end

def run(m,child_cap=703):
 def pp():return prep_month(m)
 gmd.prep=pp;D,pei,pxi,pd,src,mins,disp=w.prep();t,a,b,mid,h4,h1,m15,m5=D[:8];start,end=D[-2],D[-1]
 target=(t[pei]>=start)&(t[pei]<end)
 aligned_short=(h4[pei]==-1)&(h1[pei]==-1)&(m15[pei]==-1)&(m5[pei]==-1)&(pd==-1)
 m40=target&(src==17)&(mins>=40)&(mins<50)&aligned_short
 m50=target&(src==17)&(mins>=50)&(mins<60)&aligned_short
 A=renewal_owned(t,a,b,pei[m40],pxi[m40],pd[m40],1250,0,0,4)
 B=renewal_owned(t,a,b,pei[m50],pxi[m50],pd[m50],1250,0,0,5)
 E=np.concatenate((A[0],B[0]));X=np.concatenate((A[1],B[1]));R=np.concatenate((A[2],B[2]));Dd=np.concatenate((A[3],B[3]));P=np.concatenate((A[4],B[4]));H=np.concatenate((A[5],B[5]));S=np.concatenate((A[7],B[7]))
 if len(E)==0:return dict(candidate='GAMMA02_APRIL_PERSISTENT_NY17_SHORT_116',month=m,net=0.,trades=0,parents40=int(m40.sum()),parents50=int(m50.sum()))
 o=np.lexsort((np.arange(len(E)),E));Q=(E[o],X[o],R[o],Dd[o],P[o],H[o],S[o]);r,C=cap.one(Q,child_cap);r.update(candidate='GAMMA02_APRIL_PERSISTENT_NY17_SHORT_116',month=m,parents40=int(m40.sum()),parents50=int(m50.sum()),raw_trades=int(len(E)),raw_net=float(P.sum()),qraw=1250,rearm=0,child_cap=child_cap);return r
if __name__=='__main__':
 m=int(sys.argv[1]);out=sys.argv[2];r=run(m);open(out,'w').write(json.dumps(r,indent=2));print(json.dumps({k:r.get(k) for k in ['month','parents40','parents50','raw_net','raw_trades','net','trades','pf','win','expectancy','avg_hold_s','skips','maxopen_event']}))
