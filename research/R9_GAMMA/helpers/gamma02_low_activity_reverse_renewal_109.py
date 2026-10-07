import sys,json,numpy as np
import stmr_janjul as j, stmr_base as c, gamma02_m1_density as gmd
import gamma02_ny17_quantum_minute_window_075 as w
import gamma02_083_global_child_cap_087 as cap
from gamma02_083_heat_parent_ownership_084 import renewal_owned

def prep_month(m):
 t,sa,sb,start,end=j.load_month(m,10);a,b=c.materialize(t,sa,sb);mid=((a.astype(np.int64)+b.astype(np.int64))//2).astype(np.int32);states=j.make_states(t,b,((8,21),(8,21),(8,21),(8,21)));return t,a,b,mid,*states,start,end

def fail_late(t,a,b,pei,pxi,pd,window_ms=2000,qraw=1250,campaign_ms=120000):
 starts=[];ends=[];dirs=[]
 for p0,end,d0 in zip(pei,pxi,pd):
  d=int(d0);deadline=t[p0]+window_ms;j=p0+1;hit=False;ent0=int(a[p0] if d>0 else b[p0])
  while j<end and t[j]<=deadline:
   px=int(b[j] if d>0 else a[j])
   if (px-ent0)*d>=qraw:hit=True;break
   j+=1
  if hit or j>=end:continue
  starts.append(j);ce=np.searchsorted(t,min(t[j]+campaign_ms,t[end]),side='left');ends.append(min(int(ce),int(end),len(t)-1));dirs.append(-d)
 return np.asarray(starts,np.int64),np.asarray(ends,np.int64),np.asarray(dirs,np.int8)

def run(m,qraw,rearm,campaign_ms=120000,child_cap=703):
 def pp():return prep_month(m)
 gmd.prep=pp;D,pei,pxi,pd,src,mins,disp=w.prep();t,a,b=D[:3];ml=(src==17)&(mins>=33)&(mins<=39)&(disp>=5.)
 S,E,Dd=fail_late(t,a,b,pei[ml],pxi[ml],pd[ml],2000,1250,campaign_ms)
 A=renewal_owned(t,a,b,S,E,Dd,qraw,rearm,0,3)
 Q=(A[0],A[1],A[2],A[3],A[4],A[5],A[7]);o=np.lexsort((np.arange(len(Q[0])),Q[0]));Q=tuple(x[o] for x in Q);r,C=cap.one(Q,child_cap);r.update(month=m,qraw=qraw,rearm=rearm,campaign_ms=campaign_ms,failed_parents=int(len(S)),wins_raw=int(A[8]),residuals_raw=int(A[9]));return r
if __name__=='__main__':
 m=int(sys.argv[1]);q=int(sys.argv[2]);re=int(sys.argv[3]);out=sys.argv[4];r=run(m,q,re);open(out,'w').write(json.dumps(r,indent=2));print(json.dumps({k:r[k] for k in ['month','qraw','rearm','campaign_ms','failed_parents','net','trades','pf','win','expectancy','avg_hold_s','skips','maxopen_event']}))
