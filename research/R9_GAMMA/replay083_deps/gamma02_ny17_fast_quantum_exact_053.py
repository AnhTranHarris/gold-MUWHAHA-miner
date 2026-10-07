import json, numpy as np
from numba import njit
import gamma02_profit_funded_surge_049 as f
import gamma02_profit_funded_surge_equity_051 as eq51
import gamma02_campaign_heartbeat_019 as hb
import gamma02_funded_cap_equity_dd_028 as eq

@njit(cache=True)
def exact_quantum(t,a,b,parent_ei,parent_xi,dirs,quantum_raw):
    cap=2000000
    ent_i=np.empty(cap,np.int64); ex_i=np.empty(cap,np.int64); ent_raw=np.empty(cap,np.int64)
    out_d=np.empty(cap,np.int8); pnl=np.empty(cap,np.float64); hold=np.empty(cap,np.float64)
    n=0
    for k in range(parent_ei.size):
        d=dirs[k]; cur_i=parent_ei[k]; cur_raw=int(a[cur_i] if d>0 else b[cur_i]); start_t=t[cur_i]; end_i=parent_xi[k]
        j=cur_i+1
        while j<end_i:
            px=int(b[j] if d>0 else a[j])
            fav=(px-cur_raw)*d
            if fav>=quantum_raw:
                ent_i[n]=cur_i;ex_i[n]=j;ent_raw[n]=cur_raw;out_d[n]=d
                pnl[n]=fav/1000.0-0.02;hold[n]=(t[j]-start_t)/1000.0;n+=1
                cur_i=j;cur_raw=int(a[j] if d>0 else b[j]);start_t=t[j]
            j+=1
        px=int(b[end_i] if d>0 else a[end_i])
        ent_i[n]=cur_i;ex_i[n]=end_i;ent_raw[n]=cur_raw;out_d[n]=d
        pnl[n]=((px-cur_raw)*d)/1000.0-0.02;hold[n]=(t[end_i]-start_t)/1000.0;n+=1
    return ent_i[:n],ex_i[:n],ent_raw[:n],out_d[:n],pnl[:n],hold[:n]

def main(out):
    D,A=f.build(120);t,a,b,mid,h4,h1,m15,m5=D[:8]
    cfg=dict(base_cap=64,base_step=64,base_unit=2500.,base_max=256,initial_surge=512,surge_step=256,surge_unit=1000.,max_surge=3328,hard_max=3584)
    idx,sk,mo=eq51.select_idx(A[0],A[1],A[2],A[4],*cfg.values())
    et=A[0][idx].astype(np.int64);xt=A[1][idx].astype(np.int64);src=A[4][idx].astype(np.int16)
    ei=np.searchsorted(t,et);xi=np.searchsorted(t,xt);d=np.empty(idx.size,np.int8)
    for j,(ii,s) in enumerate(zip(ei,src)):d[j]=hb.ny_dir(int(s),int(h4[ii]),int(h1[ii]),int(m15[ii]),int(m5[ii]))
    minute=((et//60000)%60).astype(np.int16);b10=minute//10;ms=(et//60000)*60000;ai=np.searchsorted(t,ms,side='left');disp=((mid[ei]-mid[ai])*d)/1000.0
    mask=(src==17)&((b10==2)|(b10==3))&(disp>=5.0)
    E,X,ER,D,P,H=exact_quantum(t,a,b,ei[mask],xi[mask],d[mask],1000)
    gp=float(P[P>0].sum());gl=float(P[P<=0].sum());R=eq.exact_equity_sweep(t,a,b,E,X,ER,D,P);peak_total=100000.+R[3]
    obj=dict(candidate='GAMMA02_NY17_FAST_QUANTUM_EXACT_053',parent='GAMMA02_PROFIT_FUNDED_SURGE_EQUITY_051',source=17,entry_window_utc='17:20-17:39',entry_displacement_min=5.0,quantum=1.0,parent_campaigns=int(mask.sum()),net=float(P.sum()),trades=int(P.size),pf=float(gp/-gl if gl<0 else 999),win=float(np.mean(P>0)),expectancy=float(np.mean(P)),avg_hold_s=float(np.mean(H)),median_hold_s=float(np.median(H)),p90_hold_s=float(np.quantile(H,.9)),p95_hold_s=float(np.quantile(H,.95)),max_hold_s=float(np.max(H)),balance_dd=float(R[2]),equity_dd=float(R[4]),equity_dd_pct_peak=float(R[4]/peak_total*100),peak_total_equity=float(peak_total),minimum_total_equity=float(100000.+R[5]),maxopen=int(R[9]),pnl_reconstruction=float(R[0]),original_parent_selection_maxopen=int(mo),original_parent_skips=int(sk))
    json.dump(obj,open(out,'w'),indent=2);print(json.dumps(obj,indent=2))
if __name__=='__main__':main('/mnt/data/gamma02_ny17_fast_quantum_exact_053.json')