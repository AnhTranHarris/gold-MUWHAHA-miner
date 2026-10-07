import json,numpy as np
import gamma02_ny17_quantum_minute_window_075 as w
import gamma02_funded_cap_equity_dd_028 as eq
from gamma02_083_heat_parent_ownership_084 import renewal_owned,metric,crossover,SYN

def dedup_signals(E,X,R,D,P,H):
    # deterministic first representative per entry tick; verify cluster homogeneity
    order=np.argsort(E,kind='stable');E=E[order];X=X[order];R=R[order];D=D[order];P=P[order];H=H[order]
    starts=np.r_[0,np.flatnonzero(E[1:]!=E[:-1])+1];ends=np.r_[starts[1:],len(E)]
    hom_exit=hom_dir=hom_pnl=hom_entry=True; max_cluster=0
    for s,e in zip(starts,ends):
        max_cluster=max(max_cluster,e-s)
        if np.unique(X[s:e]).size>1:hom_exit=False
        if np.unique(D[s:e]).size>1:hom_dir=False
        if np.unique(P[s:e]).size>1:hom_pnl=False
        if np.unique(R[s:e]).size>1:hom_entry=False
    q=starts
    return (E[q],X[q],R[q],D[q],P[q],H[q]),dict(unique_signals=int(len(q)),max_cluster=int(max_cluster),homogeneous_exit=hom_exit,homogeneous_direction=hom_dir,homogeneous_pnl=hom_pnl,homogeneous_entry_price=hom_entry)

def replicate(sig,mult):
    E,X,R,D,P,H=sig
    if mult<=0:
        return tuple(np.empty(0,dtype=x.dtype) for x in sig)
    return tuple(np.repeat(x,mult) for x in sig)

def one(D,sigE,sigL,me,ml):
    t,a,b=D[:3]; A=replicate(sigE,me); B=replicate(sigL,ml)
    E=np.concatenate((A[0],B[0]));X=np.concatenate((A[1],B[1]));R=np.concatenate((A[2],B[2]));Dd=np.concatenate((A[3],B[3]));P=np.concatenate((A[4],B[4]));H=np.concatenate((A[5],B[5]))
    if len(E):
        o=np.argsort(E,kind='stable');E=E[o];X=X[o];R=R[o];Dd=Dd[o];P=P[o];H=H[o]
    m=metric(P,H); Q=eq.exact_equity_sweep(t,a,b,E,X,R,Dd,P); peak=100000.+Q[3]
    r=dict(early_mult=int(me),late_mult=int(ml),**m,balance_dd=float(Q[2]),equity_dd=float(Q[4]),equity_dd_pct_peak=float(Q[4]/peak*100),minimum_total_equity=float(100000.+Q[5]),maxopen=int(Q[9]),pnl_reconstruction=float(Q[0]),crossover=crossover(m));r['all_metric_crossover']=all(r['crossover'].values());return r

def main():
    D,pei,pxi,pd,src,mins,disp=w.prep();t,a,b=D[:3]
    e=(src==17)&(mins>=30)&(mins<=31)&(disp>=3.);l=(src==17)&(mins>=33)&(mins<=39)&(disp>=5.)
    E1,X1,R1,D1,P1,H1,*_=renewal_owned(t,a,b,pei[e],pxi[e],pd[e],500,250,0,1)
    E2,X2,R2,D2,P2,H2,*_=renewal_owned(t,a,b,pei[l],pxi[l],pd[l],1250,0,0,2)
    sE,qaE=dedup_signals(E1,X1,R1,D1,P1,H1);sL,qaL=dedup_signals(E2,X2,R2,D2,P2,H2)
    rows=[]
    # search all integer wave sizes likely to straddle SYNTH trade target; include one-desk extremes
    for me in range(0,41):
      for ml in range(0,41):
        tr=me*len(sE[0])+ml*len(sL[0])
        if tr<24000 or tr>36000:continue
        r=one(D,sE,sL,me,ml);rows.append(r)
    valid=[r for r in rows if r['all_metric_crossover']]
    valid.sort(key=lambda x:(x['maxopen'],x['equity_dd'],-x['net']))
    profit=sorted(valid,key=lambda x:x['net'],reverse=True)
    obj=dict(candidate='GAMMA02_083_WAVE_MULTIPLICITY_085',early_signal_qa=qaE,late_signal_qa=qaL,early_unique_signal_metrics=metric(sE[4],sE[5]),late_unique_signal_metrics=metric(sL[4],sL[5]),tested=len(rows),valid_count=len(valid),best_low_heat=valid[:20],best_profit=profit[:20])
    json.dump(obj,open('/mnt/data/gamma02_083_wave_multiplicity_085.json','w'),indent=2)
    print('EARLY_QA',json.dumps(qaE),'MET',json.dumps(obj['early_unique_signal_metrics']))
    print('LATE_QA',json.dumps(qaL),'MET',json.dumps(obj['late_unique_signal_metrics']))
    print('VALID',len(valid))
    for r in valid[:20]:print('LOWHEAT',json.dumps({k:r[k] for k in ['early_mult','late_mult','net','trades','pf','win','expectancy','avg_hold_s','equity_dd','equity_dd_pct_peak','minimum_total_equity','maxopen']}))
    for r in profit[:10]:print('PROFIT',json.dumps({k:r[k] for k in ['early_mult','late_mult','net','trades','pf','win','expectancy','avg_hold_s','equity_dd','maxopen']}))
if __name__=='__main__':main()