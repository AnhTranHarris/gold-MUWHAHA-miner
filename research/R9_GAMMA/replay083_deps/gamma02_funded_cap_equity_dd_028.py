import sys,json,numpy as np
from numba import njit
from datetime import datetime, timezone
sys.path.insert(0,'/mnt/data')
import gamma02_m1_density as gmd
import gamma02_intrinsic_cusum_pulse_024 as ip
import gamma02_campaign_heartbeat_019 as hb
import gamma02_ny_campaign_inventory_portfolio_001 as g

@njit(cache=True)
def funded_select_indices(ev_times,exit_t,pnl,base_cap,step_slots,profit_unit,max_cap):
    active=np.zeros(max_cap,np.uint8);aend=np.zeros(max_cap,np.int64);apnl=np.zeros(max_cap,np.float64)
    out=np.empty(ev_times.size,np.int64);accepted=0;realized=0.;skips=0
    for k in range(ev_times.size):
        now=ev_times[k];open_n=0
        for z in range(max_cap):
            if active[z]:
                if aend[z]<=now:realized+=apnl[z];active[z]=0
                else:open_n+=1
        fund=realized if realized>0 else 0.
        allowed=base_cap+int(fund//profit_unit)*step_slots
        if allowed>max_cap:allowed=max_cap
        if allowed<base_cap:allowed=base_cap
        if open_n>=allowed:skips+=1;continue
        q=-1
        for z in range(max_cap):
            if not active[z]:q=z;break
        if q<0:skips+=1;continue
        active[q]=1;aend[q]=exit_t[k];apnl[q]=pnl[k];out[accepted]=k;accepted+=1
    return out[:accepted],skips

@njit(cache=True)
def exact_equity_sweep(t,a,b,entry_idx,exit_idx,entry_raw,dirs,pnl):
    ntr=entry_idx.size;eorder=np.argsort(entry_idx);xorder=np.argsort(exit_idx)
    ie=0;ix=0;nlong=0;nshort=0;sum_long=0;sum_short=0;bal=0.;peak_bal=0.;max_bdd=0.;peak_eq=0.;max_edd=0.;min_eq=1e100
    min_eq_i=0;peak_eq_i=0;dd_peak_i=0;dd_trough_i=0;maxopen=0
    for i in range(t.size):
        while ix<ntr and exit_idx[xorder[ix]]==i:
            q=xorder[ix];bal+=pnl[q]
            if dirs[q]>0:nlong-=1;sum_long-=entry_raw[q]
            else:nshort-=1;sum_short-=entry_raw[q]
            ix+=1
        if bal>peak_bal:peak_bal=bal
        bdd=peak_bal-bal
        if bdd>max_bdd:max_bdd=bdd
        while ie<ntr and entry_idx[eorder[ie]]==i:
            q=eorder[ie]
            if dirs[q]>0:nlong+=1;sum_long+=entry_raw[q]
            else:nshort+=1;sum_short+=entry_raw[q]
            ie+=1
        op=nlong+nshort
        if op>maxopen:maxopen=op
        floating=0.
        if nlong:floating=(nlong*int(b[i])-sum_long)/1000.-.02*nlong
        if nshort:floating+=(sum_short-nshort*int(a[i]))/1000.-.02*nshort
        eq=bal+floating
        if eq>peak_eq:peak_eq=eq;peak_eq_i=i
        edd=peak_eq-eq
        if edd>max_edd:max_edd=edd;dd_peak_i=peak_eq_i;dd_trough_i=i
        if eq<min_eq:min_eq=eq;min_eq_i=i
    return bal,peak_bal,max_bdd,peak_eq,max_edd,min_eq,min_eq_i,dd_peak_i,dd_trough_i,maxopen

def iso(t,i):return datetime.fromtimestamp(int(t[int(i)])/1000,tz=timezone.utc).isoformat()

def one(t,a,b,h4,h1,m15,m5,A,name,cfg,initial_balance=100000.):
    idx,sk=funded_select_indices(A[0],A[1],A[2],cfg[0],cfg[1],cfg[2],cfg[3])
    et=A[0][idx];xt=A[1][idx];p=A[2][idx];src=A[4][idx].astype(np.int16)
    ei=np.searchsorted(t,et);xi=np.searchsorted(t,xt);d=np.empty(idx.size,np.int8)
    for j,(ii,s) in enumerate(zip(ei,src)):
        d[j]=1 if s<=15 else hb.ny_dir(int(s),int(h4[ii]),int(h1[ii]),int(m15[ii]),int(m5[ii]))
    er=np.where(d>0,a[ei],b[ei]).astype(np.int64);xr=np.where(d>0,b[xi],a[xi]).astype(np.int64)
    recon=((xr-er)*d)/1000.-.02
    if np.max(np.abs(recon-p))>1e-12:raise RuntimeError('PnL parity failed')
    R=exact_equity_sweep(t,a,b,ei,xi,er,d,p);peak_total=initial_balance+R[3]
    return dict(name=name,config=dict(base_cap=cfg[0],step_slots=cfg[1],profit_unit=cfg[2],max_cap=cfg[3],mode='cumulative'),
                net=R[0],trades=int(idx.size),balance_dd=R[2],equity_dd=R[4],peak_equity_delta=R[3],peak_total_equity=peak_total,
                equity_dd_pct_of_peak_total=R[4]/peak_total*100,minimum_equity_delta=R[5],minimum_total_equity=initial_balance+R[5],
                min_equity_time_utc=iso(t,R[6]),max_equity_dd_peak_time_utc=iso(t,R[7]),max_equity_dd_trough_time_utc=iso(t,R[8]),max_open=R[9])

if __name__=='__main__':
    import argparse
    ap=argparse.ArgumentParser();ap.add_argument('--out',required=True);z=ap.parse_args()
    t,a,b,mid,h4,h1,m15,m5,es,ee=gmd.prep();A=ip.heartbeat_frontier((t,a,b,mid,h4,h1,m15,m5))
    cfgs=[('funded128',(64,16,5000.,128,0)),('funded192',(64,32,5000.,192,0)),('funded256_primary',(64,64,2500.,256,0))]
    rows=[one(t,a,b,h4,h1,m15,m5,A,n,c) for n,c in cfgs]
    obj=dict(candidate='GAMMA02_FUNDED_CAP_EQUITY_DD_028',initial_balance=100000.,rows=rows)
    with open(z.out,'w') as f:json.dump(obj,f,indent=2)
    print(json.dumps(obj,indent=2))