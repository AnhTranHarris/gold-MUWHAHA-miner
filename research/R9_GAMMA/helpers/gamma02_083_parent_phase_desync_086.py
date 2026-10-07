import json, numpy as np
from numba import njit
import gamma02_ny17_quantum_minute_window_075 as w
import gamma02_funded_cap_equity_dd_028 as eq
from gamma02_083_heat_parent_ownership_084 import metric,crossover,SYN

@njit(cache=True)
def renewal_phase(t,a,b,parent_ei,parent_xi,dirs,quantum_raw,rearm_values,phase_unit_raw):
    cap=3000000
    E=np.empty(cap,np.int64);X=np.empty(cap,np.int64);R=np.empty(cap,np.int64);D=np.empty(cap,np.int8)
    P=np.empty(cap,np.float64);H=np.empty(cap,np.float64);n=0
    nc=rearm_values.size
    for k in range(parent_ei.size):
        d=dirs[k]; p0=parent_ei[k]; end_i=parent_xi[k]
        parent_exec=int(a[p0] if d>0 else b[p0])
        # Causal stable price-phase cohort, fixed for this parent at admission.
        phase=((parent_exec//phase_unit_raw)%nc) if nc>1 else 0
        rearm=int(rearm_values[phase])
        ref=int(b[p0] if d>0 else a[p0])
        cur_i=p0; cur_raw=parent_exec; open_trade=True; j=p0+1
        while j<end_i:
            fav_px=int(b[j] if d>0 else a[j])
            if not open_trade:
                if (fav_px-ref)*d>=rearm:
                    cur_i=j;cur_raw=int(a[j] if d>0 else b[j]);open_trade=True
                j+=1;continue
            fav=(fav_px-cur_raw)*d
            if fav>=quantum_raw:
                E[n]=cur_i;X[n]=j;R[n]=cur_raw;D[n]=d;P[n]=fav/1000.-.02;H[n]=(t[j]-t[cur_i])/1000.;n+=1
                ref=fav_px;open_trade=False;cur_i=j
            j+=1
        if open_trade:
            px=int(b[end_i] if d>0 else a[end_i])
            E[n]=cur_i;X[n]=end_i;R[n]=cur_raw;D[n]=d;P[n]=((px-cur_raw)*d)/1000.-.02;H[n]=(t[end_i]-t[cur_i])/1000.;n+=1
    return E[:n],X[:n],R[:n],D[:n],P[:n],H[:n]

def cluster_stats(E):
    if len(E)==0:return dict(unique_ticks=0,cluster_fraction=0.,max_cluster=0,p95_cluster=0.)
    _,c=np.unique(E,return_counts=True)
    return dict(unique_ticks=int(len(c)),cluster_fraction=float(c[c>1].sum()/len(E) if len(E) else 0),max_cluster=int(c.max()),p95_cluster=float(np.quantile(c,.95)))

def maxopen_event(E,X):
    if len(E)==0:return 0
    # exit before entry on same tick, matching exact equity sweep ordering
    ev=np.concatenate((X,E)); delta=np.concatenate((-np.ones(len(X),np.int32),np.ones(len(E),np.int32)))
    typ=np.concatenate((np.zeros(len(X),np.int8),np.ones(len(E),np.int8)))
    o=np.lexsort((typ,ev)); cur=0;mx=0
    for z in o:
        cur+=int(delta[z]);
        if cur>mx:mx=cur
    return int(mx)

def combine(A,B):
    out=[]
    for i in range(6):out.append(np.concatenate((A[i],B[i])))
    if len(out[0]):
        o=np.argsort(out[0],kind='stable');out=[x[o] for x in out]
    return tuple(out)

def compact_result(E,X,R,D,P,H,tag):
    m=metric(P,H); cs=cluster_stats(E); mo=maxopen_event(E,X)
    r=dict(tag=tag,**m,**cs,maxopen_event=mo,crossover=crossover(m));r['all_metric_crossover']=all(r['crossover'].values());return r

def exact(D,A,r):
    t,a,b=D[:3];E,X,R,Dd,P,H=A
    Q=eq.exact_equity_sweep(t,a,b,E,X,R,Dd,P);peak=100000.+Q[3]
    r=dict(r)
    r.update(balance_dd=float(Q[2]),equity_dd=float(Q[4]),equity_dd_pct_peak=float(Q[4]/peak*100),minimum_total_equity=float(100000.+Q[5]),maxopen_exact=int(Q[9]),pnl_reconstruction=float(Q[0]))
    return r

def arr(v):return np.asarray(v,dtype=np.int32)
EARLY={
 'E250':[250],
 'E2_125_375':[125,375],
 'E4_0_125_250_375':[0,125,250,375],
 'E4_125_250_375_500':[125,250,375,500],
 'E8_0_75_150_225_300_375_450_525':[0,75,150,225,300,375,450,525],
}
LATE={
 'L0':[0],
 'L2_0_250':[0,250],
 'L4_0_125_250_375':[0,125,250,375],
 'L4_0_250_500_750':[0,250,500,750],
 'L8_0_125_250_375_500_625_750_875':[0,125,250,375,500,625,750,875],
}

def main():
    D,pei,pxi,pd,src,mins,disp=w.prep();t,a,b=D[:3]
    me=(src==17)&(mins>=30)&(mins<=31)&(disp>=3.)
    ml=(src==17)&(mins>=33)&(mins<=39)&(disp>=5.)
    # unit 125 raw = $0.125; absolute entry-price phase is causal and stable.
    rows=[]; cacheE={};cacheL={}
    for en,vals in EARLY.items():
        A=renewal_phase(t,a,b,pei[me],pxi[me],pd[me],500,arr(vals),125);cacheE[en]=A
    for ln,vals in LATE.items():
        B=renewal_phase(t,a,b,pei[ml],pxi[ml],pd[ml],1250,arr(vals),125);cacheL[ln]=B
    for en,A in cacheE.items():
      for ln,B in cacheL.items():
        C=combine(A,B);r=compact_result(*C,tag=en+'__'+ln);r.update(early=en,late=ln,early_rearm=EARLY[en],late_rearm=LATE[ln]);rows.append(r)
        print(json.dumps({k:r[k] for k in ['tag','net','trades','pf','win','expectancy','avg_hold_s','unique_ticks','cluster_fraction','max_cluster','maxopen_event','all_metric_crossover']}),flush=True)
        json.dump({'candidate':'GAMMA02_083_PARENT_PHASE_DESYNC_086','rows':rows},open('/mnt/data/gamma02_083_parent_phase_desync_086.partial.json','w'),indent=2)
    valid=[r for r in rows if r['all_metric_crossover']]
    valid.sort(key=lambda q:(q['maxopen_event'],q['max_cluster'],q['cluster_fraction'],-q['net']))
    # exact equity for up to five lowest-heat all-metric candidates plus baseline
    exact_rows=[]
    tags=[]
    if valid:tags=[q['tag'] for q in valid[:5]]
    if 'E250__L0' not in tags:tags.append('E250__L0')
    for tag in tags:
        en,ln=tag.split('__');C=combine(cacheE[en],cacheL[ln]);base=next(q for q in rows if q['tag']==tag);ex=exact(D,C,base);exact_rows.append(ex)
        print('EXACT',json.dumps({k:ex[k] for k in ['tag','net','trades','pf','expectancy','avg_hold_s','unique_ticks','cluster_fraction','max_cluster','equity_dd','equity_dd_pct_peak','minimum_total_equity','maxopen_exact','all_metric_crossover']}),flush=True)
    obj=dict(candidate='GAMMA02_083_PARENT_PHASE_DESYNC_086',phase_source='parent executable entry price // $0.125 modulo cohort count',rows=rows,valid_count=len(valid),best_low_heat=valid[:10],exact_rows=exact_rows)
    json.dump(obj,open('/mnt/data/gamma02_083_parent_phase_desync_086.json','w'),indent=2)
if __name__=='__main__':main()