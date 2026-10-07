import json,numpy as np
from numba import njit
import gamma02_profit_funded_surge_049 as f
import gamma02_m1_density as gmd
import gamma02_campaign_heartbeat_019 as hb
import gamma02_funded_cap_equity_dd_028 as eq

@njit(cache=True)
def select_idx(et,xt,pnl,source,base_cap,base_step,base_unit,base_max,initial_surge,surge_step,surge_unit,max_surge,hard_max):
    active=np.zeros(hard_max,np.uint8);aend=np.zeros(hard_max,np.int64);apnl=np.zeros(hard_max,np.float64)
    out=np.empty(et.size,np.int64);n=0;realized=0.;skips=0;maxopen=0
    for k in range(et.size):
        now=et[k];open_n=0
        for z in range(hard_max):
            if active[z]:
                if aend[z]<=now:realized+=apnl[z];active[z]=0
                else:open_n+=1
        base_allowed=base_cap+int(max(0.,realized)//base_unit)*base_step
        if base_allowed>base_max:base_allowed=base_max
        if base_allowed<base_cap:base_allowed=base_cap
        surge=initial_surge+int(max(0.,realized)//surge_unit)*surge_step
        if surge>max_surge:surge=max_surge
        allowed=base_allowed+surge
        if allowed>hard_max:allowed=hard_max
        if open_n>=allowed:skips+=1;continue
        q=-1
        for z in range(hard_max):
            if not active[z]:q=z;break
        if q<0:skips+=1;continue
        active[q]=1;aend[q]=xt[k];apnl[q]=pnl[k];out[n]=k;n+=1
        if open_n+1>maxopen:maxopen=open_n+1
    return out[:n],skips,maxopen

def run():
    D,A=f.build(120);t,a,b,mid,h4,h1,m15,m5=D[:8]
    cfg=dict(base_cap=64,base_step=64,base_unit=2500.,base_max=256,initial_surge=512,surge_step=256,surge_unit=1000.,max_surge=3328,hard_max=3584)
    idx,sk,mo=select_idx(A[0],A[1],A[2],A[4],*cfg.values())
    et=A[0][idx];xt=A[1][idx];p=A[2][idx];src=A[4][idx].astype(np.int16)
    ei=np.searchsorted(t,et);xi=np.searchsorted(t,xt);d=np.empty(idx.size,np.int8)
    for j,(ii,s) in enumerate(zip(ei,src)):
        d[j]=hb.ny_dir(int(s),int(h4[ii]),int(h1[ii]),int(m15[ii]),int(m5[ii]))
    er=np.where(d>0,a[ei],b[ei]).astype(np.int64);xr=np.where(d>0,b[xi],a[xi]).astype(np.int64)
    recon=((xr-er)*d)/1000.-.02;err=float(np.max(np.abs(recon-p)))
    if err>1e-12:raise RuntimeError(err)
    R=eq.exact_equity_sweep(t,a,b,ei,xi,er,d,p);holds=(xt-et)/1000.;gp=float(p[p>0].sum());gl=float(p[p<=0].sum());peak_total=100000.+R[3]
    o=dict(candidate='GAMMA02_PROFIT_FUNDED_SURGE_EQUITY_051',config=cfg,net=float(p.sum()),trades=int(len(p)),pf=float(gp/-gl),win=float(np.mean(p>0)),expectancy=float(p.mean()),
      balance_dd=float(R[2]),equity_dd=float(R[4]),equity_dd_pct_peak=float(R[4]/peak_total*100),peak_total_equity=float(peak_total),minimum_total_equity=float(100000.+R[5]),
      min_equity_time_utc=eq.iso(t,R[6]),equity_dd_peak_time_utc=eq.iso(t,R[7]),equity_dd_trough_time_utc=eq.iso(t,R[8]),maxopen=int(R[9]),admission_maxopen=int(mo),skips=int(sk),pnl_parity_max_abs_err=err,
      avg_hold_s=float(np.mean(holds)),median_hold_s=float(np.median(holds)),p90_hold_s=float(np.quantile(holds,.9)),p95_hold_s=float(np.quantile(holds,.95)),
      source16_trades=int(np.sum(src==16)),source17_trades=int(np.sum(src==17)),source16_net=float(p[src==16].sum()),source17_net=float(p[src==17].sum()))
    json.dump(o,open('/mnt/data/gamma02_profit_funded_surge_equity_051.json','w'),indent=2);print(json.dumps(o,indent=2))
if __name__=='__main__':run()