import json,numpy as np
import stmr_janjul as j, stmr_base as c, gamma02_m1_density as gmd
import gamma02_ny17_quantum_minute_window_075 as w

def prep_month(m):
 t,sa,sb,start,end=j.load_month(m,10);a,b=c.materialize(t,sa,sb);mid=((a.astype(np.int64)+b.astype(np.int64))//2).astype(np.int32);states=j.make_states(t,b,((8,21),(8,21),(8,21),(8,21)));return t,a,b,mid,*states,start,end

def failed_entries(t,a,b,pei,pxi,pd,qraw,window_ms):
 out=[]
 for p0,end,d in zip(pei,pxi,pd):
  d=int(d)
  deadline=t[p0]+window_ms;j=p0+1;hit=False
  ent0=int(a[p0] if d>0 else b[p0])
  while j<end and t[j]<=deadline:
   px=int(b[j] if d>0 else a[j])
   if (px-ent0)*d>=qraw:hit=True;break
   j+=1
  if hit or j>=end:continue
  out.append((j,-int(d)))
 return out

def mark(t,a,b,entries):
 hs=[1000,2000,5000,10000,15000,30000,60000,120000]
 rows=[]
 for h in hs:
  ps=[]
  for i,d in entries:
   ent=int(a[i] if d>0 else b[i]);j=np.searchsorted(t,t[i]+h,side='left');j=min(j,len(t)-1);ex=int(b[j] if d>0 else a[j]);ps.append(((ex-ent)*d)/1000.-.02)
  p=np.array(ps,float);rows.append(dict(h_ms=h,n=len(p),net=float(p.sum()),mean=float(p.mean()) if len(p) else 0,win=float(np.mean(p>0)) if len(p) else 0,pf=float(p[p>0].sum()/-p[p<=0].sum()) if np.any(p<=0) else 999.))
 return rows

def main():
 m=3
 def pp():return prep_month(m)
 gmd.prep=pp;D,pei,pxi,pd,src,mins,disp=w.prep();t,a,b=D[:3]
 me=(src==17)&(mins>=30)&(mins<=31)&(disp>=3.);ml=(src==17)&(mins>=33)&(mins<=39)&(disp>=5.)
 E=failed_entries(t,a,b,pei[me],pxi[me],pd[me],500,1000);L=failed_entries(t,a,b,pei[ml],pxi[ml],pd[ml],1250,2000)
 obj={'candidate':'GAMMA02_LOW_ACTIVITY_FAILED_IGNITION_MARKOUT_108','month':3,'early_failures':len(E),'late_failures':len(L),'early_reverse':mark(t,a,b,E),'late_reverse':mark(t,a,b,L)}
 open('/mnt/data/gamma02_low_activity_failed_ignition_markout_108.json','w').write(json.dumps(obj,indent=2));print(json.dumps(obj))
if __name__=='__main__':main()
