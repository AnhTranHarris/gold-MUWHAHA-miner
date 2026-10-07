import json,numpy as np
import gamma02_ny17_fast_quantum_exact_053 as qx
import gamma02_profit_funded_surge_049 as f
import gamma02_profit_funded_surge_equity_051 as eq51
import gamma02_campaign_heartbeat_019 as hb

def prep():
 D,A=f.build(120);t,a,b,mid,h4,h1,m15,m5=D[:8];cfg=dict(base_cap=64,base_step=64,base_unit=2500.,base_max=256,initial_surge=512,surge_step=256,surge_unit=1000.,max_surge=3328,hard_max=3584);idx,_,_=eq51.select_idx(A[0],A[1],A[2],A[4],*cfg.values());et=A[0][idx];xt=A[1][idx];src=A[4][idx].astype(np.int16);ei=np.searchsorted(t,et);xi=np.searchsorted(t,xt);d=np.empty(len(idx),np.int8)
 for j,(ii,s) in enumerate(zip(ei,src)):d[j]=hb.ny_dir(int(s),int(h4[ii]),int(h1[ii]),int(m15[ii]),int(m5[ii]))
 mins=((et//60000)%60).astype(np.int16);ai=np.searchsorted(t,(et//60000)*60000,side='left');disp=((mid[ei]-mid[ai])*d)/1000.;return D,ei,xi,d,src,mins,disp

def main():
 D,ei,xi,d,src,mins,disp=prep();t,a,b=D[:3];rows=[];windows=[(30,34),(35,39),(30,32),(33,35),(36,39),(30,39)]
 for lo,hi in windows:
  for thr in (3.,5.,8.,10.):
   m=(src==17)&(mins>=lo)&(mins<=hi)&(disp>=thr)
   if not np.any(m):continue
   for q in (.5,.75,1.,1.25,1.5,2.):
    E,X,ER,Dd,P,H=qx.exact_quantum(t,a,b,ei[m],xi[m],d[m],int(q*1000));gp=float(P[P>0].sum());gl=float(P[P<=0].sum());rows.append(dict(window=f'{lo:02d}-{hi:02d}',displacement_min=thr,quantum=q,parents=int(m.sum()),net=float(P.sum()),trades=int(P.size),pf=float(gp/-gl if gl<0 else 999),win=float(np.mean(P>0)),expectancy=float(np.mean(P)),avg_hold_s=float(np.mean(H)),median_hold_s=float(np.median(H)),p90_hold_s=float(np.quantile(H,.9))))
 json.dump({'candidate':'GAMMA02_NY17_QUANTUM_MINUTE_WINDOW_075','rows':rows},open('/mnt/data/gamma02_ny17_quantum_minute_window_075.json','w'),indent=2)
 syn=(41520.82,27980,23.7154119,.87090779,1.48394639)
 elig=[r for r in rows if r['net']>=syn[0] and r['trades']>=syn[1] and r['pf']>=syn[2] and r['win']>=syn[3] and r['expectancy']>=syn[4]];elig.sort(key=lambda r:(r['avg_hold_s'],-r['net']))
 print('FASTEST ALL-METRIC');[print(json.dumps(r)) for r in elig[:25]]
 print('ALL <=20s');[print(json.dumps(r)) for r in sorted([r for r in rows if r['avg_hold_s']<=20],key=lambda x:x['net'],reverse=True)[:25]]
if __name__=='__main__':main()