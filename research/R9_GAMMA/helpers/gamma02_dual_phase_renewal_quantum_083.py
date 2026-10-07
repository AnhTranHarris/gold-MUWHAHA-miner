import json,numpy as np
from numba import njit
import gamma02_ny17_quantum_minute_window_075 as w
import gamma02_funded_cap_equity_dd_028 as eq

@njit(cache=True)
def renewal_quantum_exact(t,a,b,parent_ei,parent_xi,dirs,quantum_raw,rearm_raw,initial_rearm_raw):
    cap=3000000
    ent_i=np.empty(cap,np.int64);ex_i=np.empty(cap,np.int64);ent_raw=np.empty(cap,np.int64);out_d=np.empty(cap,np.int8)
    pnl=np.empty(cap,np.float64);hold=np.empty(cap,np.float64);n=0;wins=0;resid=0
    for k in range(parent_ei.size):
        d=dirs[k];p0=parent_ei[k];end_i=parent_xi[k]
        ref=int(b[p0] if d>0 else a[p0])
        if initial_rearm_raw<=0:
            cur_i=p0;cur_raw=int(a[cur_i] if d>0 else b[cur_i]);open_trade=True;j=cur_i+1
        else:
            open_trade=False;cur_i=-1;cur_raw=0;j=p0+1
        while j<end_i:
            fav_px=int(b[j] if d>0 else a[j])
            if not open_trade:
                need=initial_rearm_raw if cur_i==-1 else rearm_raw
                if (fav_px-ref)*d>=need:
                    cur_i=j;cur_raw=int(a[j] if d>0 else b[j]);open_trade=True
                j+=1;continue
            fav=(fav_px-cur_raw)*d
            if fav>=quantum_raw:
                ent_i[n]=cur_i;ex_i[n]=j;ent_raw[n]=cur_raw;out_d[n]=d;pnl[n]=fav/1000.0-0.02;hold[n]=(t[j]-t[cur_i])/1000.;n+=1;wins+=1
                ref=fav_px;open_trade=False;cur_i=j
            j+=1
        if open_trade:
            px=int(b[end_i] if d>0 else a[end_i]);ent_i[n]=cur_i;ex_i[n]=end_i;ent_raw[n]=cur_raw;out_d[n]=d;pnl[n]=((px-cur_raw)*d)/1000.-0.02;hold[n]=(t[end_i]-t[cur_i])/1000.;n+=1;resid+=1
    return ent_i[:n],ex_i[:n],ent_raw[:n],out_d[:n],pnl[:n],hold[:n],wins,resid

def metrics(P,H):
 gp=float(P[P>0].sum());gl=float(P[P<=0].sum())
 return dict(net=float(P.sum()),trades=int(P.size),pf=float(gp/-gl if gl<0 else 999),win=float(np.mean(P>0)),expectancy=float(np.mean(P)),avg_hold_s=float(np.mean(H)),median_hold_s=float(np.median(H)),p90_hold_s=float(np.quantile(H,.9)),p95_hold_s=float(np.quantile(H,.95)),max_hold_s=float(np.max(H)))

def main():
 D,pei,pxi,pd,src,mins,disp=w.prep();t,a,b=D[:3]
 me=(src==17)&(mins>=30)&(mins<=31)&(disp>=3.)
 E1,X1,R1,D1,P1,H1,W1,Z1=renewal_quantum_exact(t,a,b,pei[me],pxi[me],pd[me],500,250,0)
 ml=(src==17)&(mins>=33)&(mins<=39)&(disp>=5.)
 E2,X2,R2,D2,P2,H2,W2,Z2=renewal_quantum_exact(t,a,b,pei[ml],pxi[ml],pd[ml],1250,0,0)
 E=np.concatenate((E1,E2));X=np.concatenate((X1,X2));ER=np.concatenate((R1,R2));DD=np.concatenate((D1,D2));P=np.concatenate((P1,P2));H=np.concatenate((H1,H2))
 m=metrics(P,H);R=eq.exact_equity_sweep(t,a,b,E,X,ER,DD,P);peak_total=100000.+R[3]
 obj=dict(candidate='GAMMA02_DUAL_PHASE_RENEWAL_QUANTUM_083',parent='GAMMA02_PROFIT_FUNDED_SURGE_EQUITY_051',initial_balance=100000.,
          early=dict(window='17:30-17:31',disp_min=3.,quantum=.5,rearm=.25,parents=int(me.sum()),quantum_wins=int(W1),residuals=int(Z1),**metrics(P1,H1)),
          late=dict(window='17:33-17:39',disp_min=5.,quantum=1.25,rearm=0.,parents=int(ml.sum()),quantum_wins=int(W2),residuals=int(Z2),**metrics(P2,H2)),
          combined=m,balance_dd=float(R[2]),equity_dd=float(R[4]),equity_dd_pct_peak=float(R[4]/peak_total*100),peak_total_equity=float(peak_total),minimum_total_equity=float(100000.+R[5]),maxopen=int(R[9]),pnl_reconstruction=float(R[0]))
 syn=dict(net=41520.82,trades=27980,pf=23.715411927544082,win=.8709077912794854,expectancy=1.4839463902787706,avg_hold_s=16.462687634024302)
 obj['r9_synth']=syn;obj['metric_crossover']={k:(m[k]>=v if k!='avg_hold_s' else m[k]<=v) for k,v in syn.items()};obj['all_metric_crossover']=all(obj['metric_crossover'].values())
 json.dump(obj,open('/mnt/data/gamma02_dual_phase_renewal_quantum_083.json','w'),indent=2);print(json.dumps(obj,indent=2))
if __name__=='__main__':main()
