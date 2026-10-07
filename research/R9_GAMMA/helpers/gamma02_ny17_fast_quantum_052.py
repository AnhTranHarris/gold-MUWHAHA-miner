import json, numpy as np
from numba import njit
import gamma02_profit_funded_surge_049 as f
import gamma02_profit_funded_surge_equity_051 as eq51
import gamma02_campaign_heartbeat_019 as hb

@njit(cache=True)
def quantum_rollover_events(t,a,b,A_et,A_ei,sel_idx,sel_xt,sel_xi,d,quantum_raw):
    max_slices=4000000
    pnl=np.empty(max_slices,np.float64); hold=np.empty(max_slices,np.float64); n=0
    for jj in range(sel_idx.size):
        k0=sel_idx[jj]; direction=d[jj]; entry_idx=A_ei[k0]
        entry=int(a[entry_idx] if direction>0 else b[entry_idx]); start_t=A_et[k0]; k=k0+1; end_t=sel_xt[jj]
        while k<A_et.size and A_et[k] < end_t:
            ci=A_ei[k]; px=int(b[ci] if direction>0 else a[ci]); fav=(px-entry)*direction
            if fav>=quantum_raw:
                pnl[n]=fav/1000.0-0.02; hold[n]=(A_et[k]-start_t)/1000.0; n+=1
                entry=int(a[ci] if direction>0 else b[ci]); start_t=A_et[k]
            k+=1
        px=int(b[sel_xi[jj]] if direction>0 else a[sel_xi[jj]])
        pnl[n]=((px-entry)*direction)/1000.0-0.02; hold[n]=(sel_xt[jj]-start_t)/1000.0; n+=1
    return pnl[:n],hold[:n]

def run(out):
    D,A=f.build(120); t,a,b,mid,h4,h1,m15,m5=D[:8]
    cfg=dict(base_cap=64,base_step=64,base_unit=2500.,base_max=256,initial_surge=512,surge_step=256,surge_unit=1000.,max_surge=3328,hard_max=3584)
    idx,sk,mo=eq51.select_idx(A[0],A[1],A[2],A[4],*cfg.values())
    et=A[0][idx].astype(np.int64); xt=A[1][idx].astype(np.int64); src=A[4][idx].astype(np.int16)
    ei=np.searchsorted(t,et); xi=np.searchsorted(t,xt); d=np.empty(idx.size,np.int8)
    for j,(ii,s) in enumerate(zip(ei,src)):
        d[j]=hb.ny_dir(int(s),int(h4[ii]),int(h1[ii]),int(m15[ii]),int(m5[ii]))
    A_et=A[0].astype(np.int64); A_ei=np.searchsorted(t,A_et).astype(np.int64)
    minute=((et//60000)%60).astype(np.int16); b10=minute//10; minute_start=(et//60000)*60000
    ai=np.searchsorted(t,minute_start,side='left'); disp=((mid[ei]-mid[ai])*d)/1000.0
    rows=[]
    for thr in (3,5,8,10):
      mask=(src==17)&((b10==2)|(b10==3))&(disp>=thr)
      for q in (500,750,1000,1250,1500,2000,3000,4000):
        p,h=quantum_rollover_events(t,a,b,A_et,A_ei,idx[mask],xt[mask],xi[mask],d[mask],q)
        gp=float(p[p>0].sum()); gl=float(p[p<=0].sum())
        rows.append(dict(displacement_min=float(thr),quantum=float(q/1000.0),parents=int(mask.sum()),net=float(p.sum()),trades=int(p.size),pf=float(gp/-gl if gl<0 else 999),win=float(np.mean(p>0)),expectancy=float(np.mean(p)),avg_hold_s=float(np.mean(h)),median_hold_s=float(np.median(h)),p90_hold_s=float(np.quantile(h,.9))))
    obj={'candidate':'GAMMA02_NY17_FAST_QUANTUM_052','parent':'GAMMA02_PROFIT_FUNDED_SURGE_EQUITY_051','entry_window_utc':'17:20-17:39','source':17,'rows':rows}
    json.dump(obj,open(out,'w'),indent=2)
    rows.sort(key=lambda r:(r['net']),reverse=True)
    for r in rows[:12]: print(json.dumps(r),flush=True)
if __name__=='__main__':
    run('/mnt/data/gamma02_ny17_fast_quantum_052.json')
