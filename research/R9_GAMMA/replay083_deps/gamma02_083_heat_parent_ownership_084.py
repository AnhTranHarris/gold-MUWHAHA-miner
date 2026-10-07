import json, numpy as np
from numba import njit
import gamma02_ny17_quantum_minute_window_075 as w
import gamma02_funded_cap_equity_dd_028 as eq

SYN=dict(net=41520.82,trades=27980,pf=23.715411927544082,win=0.8709077912794854,expectancy=1.4839463902787706,avg_hold_s=16.462687634024302)

@njit(cache=True)
def renewal_owned(t,a,b,parent_ei,parent_xi,dirs,quantum_raw,rearm_raw,initial_rearm_raw,desk_code):
    cap=3000000
    ent_i=np.empty(cap,np.int64);ex_i=np.empty(cap,np.int64);ent_raw=np.empty(cap,np.int64);out_d=np.empty(cap,np.int8)
    pnl=np.empty(cap,np.float64);hold=np.empty(cap,np.float64);owner=np.empty(cap,np.int32);desk=np.empty(cap,np.int8)
    n=0;wins=0;resid=0
    for k in range(parent_ei.size):
        d=dirs[k];p0=parent_ei[k];end_i=parent_xi[k];ref=int(b[p0] if d>0 else a[p0])
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
                ent_i[n]=cur_i;ex_i[n]=j;ent_raw[n]=cur_raw;out_d[n]=d;pnl[n]=fav/1000.-.02;hold[n]=(t[j]-t[cur_i])/1000.;owner[n]=k;desk[n]=desk_code;n+=1;wins+=1
                ref=fav_px;open_trade=False;cur_i=j
            j+=1
        if open_trade:
            px=int(b[end_i] if d>0 else a[end_i]);ent_i[n]=cur_i;ex_i[n]=end_i;ent_raw[n]=cur_raw;out_d[n]=d;pnl[n]=((px-cur_raw)*d)/1000.-.02;hold[n]=(t[end_i]-t[cur_i])/1000.;owner[n]=k;desk[n]=desk_code;n+=1;resid+=1
    return ent_i[:n],ex_i[:n],ent_raw[:n],out_d[:n],pnl[:n],hold[:n],owner[:n],desk[:n],wins,resid

def metric(P,H):
    gp=float(P[P>0].sum()); gl=float(P[P<=0].sum())
    return dict(net=float(P.sum()),trades=int(P.size),pf=float(gp/-gl if gl<0 else 999.),win=float(np.mean(P>0)),expectancy=float(np.mean(P)),avg_hold_s=float(np.mean(H)))

def crossover(m):
    return dict(net=m['net']>=SYN['net'],trades=m['trades']>=SYN['trades'],pf=m['pf']>=SYN['pf'],win=m['win']>=SYN['win'],expectancy=m['expectancy']>=SYN['expectancy'],avg_hold_s=m['avg_hold_s']<=SYN['avg_hold_s'])

def thin_first_per_tick(ei,max_per_tick):
    if max_per_tick<=0:return np.arange(ei.size,dtype=np.int64)
    keep=[]; last=-1; n=0
    for k,v in enumerate(ei):
        v=int(v)
        if v!=last:last=v;n=0
        if n<max_per_tick:keep.append(k);n+=1
    return np.asarray(keep,dtype=np.int64)

def thin_spacing(t,ei,min_ms):
    if min_ms<=0:return np.arange(ei.size,dtype=np.int64)
    keep=[];last=-10**30
    for k,v in enumerate(ei):
        tv=int(t[int(v)])
        if tv-last>=min_ms:keep.append(k);last=tv
    return np.asarray(keep,dtype=np.int64)

def owner_stats(t,pei,pxi,children_ei,owner):
    vals,counts=np.unique(pei,return_counts=True)
    cev,cc=np.unique(children_ei,return_counts=True)
    ownc=np.bincount(owner,minlength=len(pei)) if len(owner) else np.zeros(len(pei),dtype=int)
    return dict(parents=int(len(pei)),unique_parent_entry_ticks=int(len(vals)),parent_same_tick_fraction=float(np.sum(counts[counts>1])/len(pei) if len(pei) else 0),max_parents_same_tick=int(counts.max() if len(counts) else 0),
                children=int(len(children_ei)),unique_child_entry_ticks=int(len(cev)),child_same_tick_fraction=float(np.sum(cc[cc>1])/len(children_ei) if len(children_ei) else 0),max_children_same_tick=int(cc.max() if len(cc) else 0),
                children_per_parent_mean=float(ownc.mean() if len(ownc) else 0),children_per_parent_p95=float(np.quantile(ownc,.95) if len(ownc) else 0),children_per_parent_max=int(ownc.max() if len(ownc) else 0))

def run_variant(D,pei,pxi,pd,src,mins,disp,mode,value):
    t,a,b=D[:3]
    me=(src==17)&(mins>=30)&(mins<=31)&(disp>=3.)
    ml=(src==17)&(mins>=33)&(mins<=39)&(disp>=5.)
    ie=np.nonzero(me)[0]; il=np.nonzero(ml)[0]
    if mode=='per_tick':
        ie=ie[thin_first_per_tick(pei[ie],int(value))]; il=il[thin_first_per_tick(pei[il],int(value))]
    elif mode=='spacing':
        ie=ie[thin_spacing(t,pei[ie],int(value))]; il=il[thin_spacing(t,pei[il],int(value))]
    E1,X1,R1,D1,P1,H1,O1,S1,W1,Z1=renewal_owned(t,a,b,pei[ie],pxi[ie],pd[ie],500,250,0,1)
    E2,X2,R2,D2,P2,H2,O2,S2,W2,Z2=renewal_owned(t,a,b,pei[il],pxi[il],pd[il],1250,0,0,2)
    # remap late owners only for local diagnostics; no ownership overlap needed across desks
    E=np.concatenate((E1,E2));X=np.concatenate((X1,X2));ER=np.concatenate((R1,R2));DD=np.concatenate((D1,D2));P=np.concatenate((P1,P2));H=np.concatenate((H1,H2))
    m=metric(P,H); R=eq.exact_equity_sweep(t,a,b,E,X,ER,DD,P); peak_total=100000.+R[3]
    out=dict(mode=mode,value=int(value),early_parents=int(len(ie)),late_parents=int(len(il)),**m,balance_dd=float(R[2]),equity_dd=float(R[4]),equity_dd_pct_peak=float(R[4]/peak_total*100),minimum_total_equity=float(100000.+R[5]),maxopen=int(R[9]),pnl_reconstruction=float(R[0]),crossover=crossover(m))
    out['all_metric_crossover']=all(out['crossover'].values())
    out['early_ownership']=owner_stats(t,pei[ie],pxi[ie],E1,O1); out['late_ownership']=owner_stats(t,pei[il],pxi[il],E2,O2)
    return out

def main():
    D,pei,pxi,pd,src,mins,disp=w.prep(); rows=[]
    # baseline plus causal parent-thinning variants
    for mode,value in [('baseline',0),('per_tick',1),('per_tick',2),('per_tick',4),('per_tick',8),('spacing',50),('spacing',100),('spacing',250),('spacing',500),('spacing',1000),('spacing',2000),('spacing',5000)]:
        r=run_variant(D,pei,pxi,pd,src,mins,disp,mode,value);rows.append(r)
        print(json.dumps({k:r[k] for k in ['mode','value','early_parents','late_parents','net','trades','pf','win','expectancy','avg_hold_s','equity_dd','equity_dd_pct_peak','minimum_total_equity','maxopen','all_metric_crossover']}),flush=True)
        json.dump({'candidate':'GAMMA02_083_HEAT_PARENT_OWNERSHIP_QA_084','rows':rows},open('/mnt/data/gamma02_083_heat_parent_ownership_084.partial.json','w'),indent=2)
    valid=[r for r in rows if r['all_metric_crossover']]
    valid.sort(key=lambda r:(r['maxopen'],r['equity_dd'],-r['net']))
    obj={'candidate':'GAMMA02_083_HEAT_PARENT_OWNERSHIP_QA_084','r9_synth':SYN,'rows':rows,'best_low_heat_crossover':valid[0] if valid else None}
    json.dump(obj,open('/mnt/data/gamma02_083_heat_parent_ownership_084.json','w'),indent=2)
if __name__=='__main__':main()