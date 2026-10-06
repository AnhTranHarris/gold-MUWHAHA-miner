from __future__ import annotations
import argparse, json
from pathlib import Path
import numpy as np
from numba import njit

from grid001_january_event_label_lab import load, materialize, PRICE_SCALE
from grid001_january_early_thesis_failure import m1_atr_gap, gen_events

@njit(cache=True)
def simulate_opened(t,a,b,ei,ed,eg,horizon=300000):
    n=ei.size
    proof_idx=np.full(n,-1,np.int64)
    pnl=np.zeros(n,np.float64)
    reason=np.zeros(n,np.int8)
    for k in range(n):
        i=int(ei[k]); d=int(ed[k]); g=int(eg[k]); end=t[i]+horizon
        side=-1 if d<0 else 1
        event_entry=a[i] if side>0 else b[i]
        proof=max(1,int(round(0.25*g))); fail=max(1,int(round(0.50*g)))
        pi=-1; decided=False; j=i+1
        while j<t.size and t[j]<=end:
            px=b[j] if side>0 else a[j]
            if side>0:
                if px<=event_entry-fail: reason[k]=1; decided=True; break
                if px>=event_entry+proof: pi=j; decided=True; break
            else:
                if px>=event_entry+fail: reason[k]=1; decided=True; break
                if px<=event_entry-proof: pi=j; decided=True; break
            j+=1
        if not decided or pi<0:
            if not decided: reason[k]=5
            continue
        proof_idx[k]=pi
        entry=a[pi] if side>0 else b[pi]
        tp=entry+g if side>0 else entry-g
        sl=entry-g if side>0 else entry+g
        ex=entry; last=pi; rr=4; q=pi+1
        while q<t.size and t[q]<=end:
            last=q
            if side>0:
                if b[q]>=tp: ex=b[q]; rr=2; break
                if b[q]<=sl: ex=b[q]; rr=3; break
            else:
                if a[q]<=tp: ex=a[q]; rr=2; break
                if a[q]>=sl: ex=a[q]; rr=3; break
            q+=1
        else:
            ex=b[last] if side>0 else a[last]
        reason[k]=rr
        pnl[k]=((ex-entry) if side>0 else (entry-ex))/PRICE_SCALE-0.02
    return proof_idx,pnl,reason

def minute_state(t,bid):
    bucket=t//60_000
    starts=np.r_[0,np.flatnonzero(bucket[1:]!=bucket[:-1])+1]
    ends=np.r_[starts[1:]-1,len(t)-1]
    hi=np.maximum.reduceat(bid,starts).astype(np.int64)
    lo=np.minimum.reduceat(bid,starts).astype(np.int64)
    cl=bid[ends].astype(np.int64)
    prev=np.r_[cl[0],cl[:-1]]
    tr=np.maximum(hi-lo,np.maximum(np.abs(hi-prev),np.abs(lo-prev))).astype(float)
    cs=np.r_[0.0,np.cumsum(tr)]
    atr14=np.full(len(tr),np.nan); atr240=np.full(len(tr),np.nan)
    for k in range(14,len(tr)): atr14[k]=(cs[k]-cs[k-14])/14.0
    for k in range(240,len(tr)): atr240[k]=(cs[k]-cs[k-240])/240.0
    ratio=np.divide(atr14,atr240,out=np.full(len(tr),np.nan),
                    where=np.isfinite(atr14)&np.isfinite(atr240)&(atr240>0))
    return bucket[starts],ratio

def stats(x):
    x=np.asarray(x,float)
    gp=float(x[x>0].sum()); gl=float(x[x<0].sum())
    return {'n':int(len(x)),'net':float(x.sum()),'gross_profit':gp,'gross_loss':gl,
            'pf':gp/abs(gl) if gl<0 else None,
            'expected':float(x.mean()) if len(x) else None,
            'win_pct':100*float((x>0).mean()) if len(x) else None}

def bin_report(values,pnl,disc,edges,labels):
    out={}
    for j,label in enumerate(labels):
        lo=edges[j]; hi=edges[j+1]
        mask=(values>=lo)&((values<=hi) if j==len(labels)-1 else (values<hi))
        out[label]={'full':stats(pnl[mask]),'discovery':stats(pnl[mask&disc]),
                    'validation':stats(pnl[mask&~disc])}
    return out

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('source',type=Path)
    ap.add_argument('--output',type=Path,required=True)
    z=ap.parse_args()

    t,sa,sb=load(z.source)
    a,b,maxe=materialize(t,sa,sb)
    gaps=m1_atr_gap(t,b,1.5)
    ei_all,ed_all,eg_all=gen_events(t,a,b,gaps)
    pi_all,pnl_all,_=simulate_opened(t,a,b,ei_all,ed_all,eg_all)
    op=pi_all>=0
    ei=ei_all[op]; ed=ed_all[op]; eg=eg_all[op]; pi=pi_all[op]; pnl=pnl_all[op]
    split=2*len(t)//3; disc=ei<split

    mins,ratio=minute_state(t,b)
    proof_min=t[pi]//60_000
    mi=np.searchsorted(mins,proof_min,side='left')-1
    vr=np.full(len(pi),np.nan); ok=mi>=0; vr[ok]=ratio[mi[ok]]

    cap=(eg>=5000).astype(float)
    mid2=a.astype(np.int64)+b.astype(np.int64)
    dm=np.abs(np.diff(mid2,prepend=mid2[0])).astype(np.int64)
    cum=np.cumsum(dm,dtype=np.int64)
    si=np.searchsorted(t,t[pi]-300_000,side='left')
    net=(mid2[pi]-mid2[si])/2.0
    path=(cum[pi]-np.where(si>0,cum[si-1],0))/2.0
    eff=np.divide(np.abs(net),path,out=np.zeros_like(net,dtype=float),where=path>0)
    side=np.where(ed<0,-1.0,1.0)
    aligned=(side*net)/eg

    pace_all=np.full(len(ei_all),np.nan)
    if len(ei_all)>1:
        pace_all[1:]=(t[ei_all[1:]]-t[ei_all[:-1]])/1000.0
    event_pace=pace_all[op]

    out={
      'schema':'delta-a-alpha-grid001-january-proof-state-diagnosis-v1',
      'unit':'DAA_GRID_001_JANUARY_PROOF_STATE_DIAGNOSIS_001',
      'status':'COMPLETE','surface':'DUKAS_COINEXX_LIKE_P75',
      'opened_trades':int(len(pnl)),
      'full':stats(pnl),'discovery':stats(pnl[disc]),'validation':stats(pnl[~disc]),
      'state_population':{
        'discovery_n':int(disc.sum()),'validation_n':int((~disc).sum()),
        'discovery_gap_cap_pct':100*float(cap[disc].mean()),
        'validation_gap_cap_pct':100*float(cap[~disc].mean()),
        'discovery_vol_ratio_median':float(np.nanmedian(vr[disc])),
        'validation_vol_ratio_median':float(np.nanmedian(vr[~disc])),
        'discovery_eff5m_median':float(np.nanmedian(eff[disc])),
        'validation_eff5m_median':float(np.nanmedian(eff[~disc])),
        'discovery_aligned5m_gap_median':float(np.nanmedian(aligned[disc])),
        'validation_aligned5m_gap_median':float(np.nanmedian(aligned[~disc])),
        'discovery_event_pace_median_s':float(np.nanmedian(event_pace[disc])),
        'validation_event_pace_median_s':float(np.nanmedian(event_pace[~disc]))
      },
      'vol_ratio_bins':bin_report(vr,pnl,disc,[0,0.75,1.0,1.25,1.5,2.0,np.inf],
        ['<0.75','0.75-1.00','1.00-1.25','1.25-1.50','1.50-2.00','>=2.00']),
      'gap_cap':{
        '<5':{'full':stats(pnl[cap<0.5]),'discovery':stats(pnl[(cap<0.5)&disc]),'validation':stats(pnl[(cap<0.5)&~disc])},
        '==5':{'full':stats(pnl[cap>=0.5]),'discovery':stats(pnl[(cap>=0.5)&disc]),'validation':stats(pnl[(cap>=0.5)&~disc])}},
      'eff5m_bins':bin_report(eff,pnl,disc,[0,0.10,0.25,0.50,0.75,np.inf],
        ['<0.10','0.10-0.25','0.25-0.50','0.50-0.75','>=0.75']),
      'event_pace_bins':bin_report(event_pace,pnl,disc,[0,1,5,30,120,np.inf],
        ['<1s','1-5s','5-30s','30-120s','>=120s']),
      'max_midpoint_quantization_error_price':float(maxe/(2*PRICE_SCALE))
    }
    z.output.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))

if __name__=='__main__':
    main()
