"""Reconstruct original Jan 131E accepted research ticket source labels and exact tick equity attribution.
This is an attribution diagnostic only; NEVER treat as funded-broker execution certification.
"""
from pathlib import Path
import sys, json, datetime, time
import numpy as np
from numba import njit
D=Path('/mnt/data/daa_jan_exact_032'); OUT=Path('/mnt/data/daa_jan_risk_audit_033')
sys.path.insert(0,str(D))
import stmr_base as st
st.materialize=lambda t,sa,sb:(sa.copy(),sb.copy())
import jan_profit_per_heat_highrange_131e as F
import jan_session_portfolio_131d as J
import jan_session_portfolio_lean_131d as L
from datetime import timezone

@njit(cache=True)
def sweep(t,a,b,E,X,R,DIR,P,S,ng=7):
    n=len(E); kE=np.argsort(E); kX=np.argsort(X)
    nb=np.zeros(ng,np.float64); nl=np.zeros(ng,np.int64);ns=np.zeros(ng,np.int64)
    suml=np.zeros(ng,np.int64);sums=np.zeros(ng,np.int64)
    peq=np.zeros(ng,np.float64);pdd=np.zeros(ng,np.float64)
    peak=-1e30; peakidx=0; maxdd=-1;globalpk=0;globaltr=0
    epk=np.zeros(ng,np.float64);etr=np.zeros(ng,np.float64)
    opk=np.zeros(ng,np.int64);otr=np.zeros(ng,np.int64)
    equity_at_tr=0.;open_max=0; max_loss_floating=-1e20; max_loss_float_i=0
    ie=0;ix=0
    for i in range(len(t)):
        while ix<n and X[kX[ix]]==i:
            k=kX[ix];g=S[k];nb[g]+=P[k]
            if DIR[k]>0:nl[g]-=1;suml[g]-=R[k]
            else:ns[g]-=1;sums[g]-=R[k]
            ix+=1
        while ie<n and E[kE[ie]]==i:
            k=kE[ie];g=S[k]
            if DIR[k]>0:nl[g]+=1;suml[g]+=R[k]
            else:ns[g]+=1;sums[g]+=R[k]
            ie+=1
        eq=0.;floating=0.;op=0
        v=np.empty(ng,np.float64)
        for g in range(ng):
            fl=(nl[g]*int(b[i])-suml[g]+sums[g]-ns[g]*int(a[i]))/1000.-0.02*(nl[g]+ns[g])
            floating+=fl;op+=nl[g]+ns[g]
            gq=nb[g]+fl;v[g]=gq;eq+=gq
            if gq>peq[g]:peq[g]=gq
            dd=peq[g]-gq
            if dd>pdd[g]:pdd[g]=dd
        if op>open_max:open_max=op
        if floating<max_loss_floating or max_loss_float_i==0: max_loss_floating=floating;max_loss_float_i=i
        if eq>peak:
            peak=eq;peakidx=i
            epk[:]=v
            opk[:]=nl+ns
        dd=peak-eq
        if dd>maxdd:
            maxdd=dd;globalpk=peakidx;globaltr=i
            etr[:]=v;otr[:]=nl+ns
            # epk changes later so snapshot peak contributions when drawdown is found
            # pass in separately below
            equity_at_tr=eq
    return maxdd,globalpk,globaltr,epk,etr,opk,otr,pdd,open_max,max_loss_floating,max_loss_float_i,equity_at_tr

@njit(cache=True)
def sweep_fixed(t,a,b,E,X,R,DIR,P,S, peak_i, trough_i,ng=7):
    n=len(E); kE=np.argsort(E); kX=np.argsort(X)
    nb=np.zeros(ng,np.float64);nl=np.zeros(ng,np.int64);ns=np.zeros(ng,np.int64);suml=np.zeros(ng,np.int64);sums=np.zeros(ng,np.int64)
    marks=np.zeros((2,ng),np.float64);floats=np.zeros((2,ng),np.float64);balances=np.zeros((2,ng),np.float64);op=np.zeros((2,ng),np.int64)
    ie=0;ix=0
    for i in range(len(t)):
        while ix<n and X[kX[ix]]==i:
            k=kX[ix];g=S[k];nb[g]+=P[k]
            if DIR[k]>0:nl[g]-=1;suml[g]-=R[k]
            else:ns[g]-=1;sums[g]-=R[k]
            ix+=1
        while ie<n and E[kE[ie]]==i:
            k=kE[ie];g=S[k]
            if DIR[k]>0:nl[g]+=1;suml[g]+=R[k]
            else:ns[g]+=1;sums[g]+=R[k]
            ie+=1
        if i==peak_i or i==trough_i:
            slot=0 if i==peak_i else 1
            for g in range(ng):
                fl=(nl[g]*int(b[i])-suml[g]+sums[g]-ns[g]*int(a[i]))/1000.-0.02*(nl[g]+ns[g])
                floats[slot,g]=fl;balances[slot,g]=nb[g];marks[slot,g]=nb[g]+fl;op[slot,g]=nl[g]+ns[g]
            if i==trough_i:break
    return marks,floats,balances,op


def main():
    tick=time.time();A,lay=F.build_raw();E,X,R,Dd,P,H=A
    base=np.flatnonzero(lay<=35);idx=base[F.capsel(E[base],X[base],640)]
    wd=tuple(z[idx] for z in A)
    parts=[('L4_WATCHDOG',wd),('L3_HOURLY_COVERAGE',J.build_coverage()),('L3_HOURLY_COLDSTART',J.build_coldstart(50,450,64))]
    parts+=[('L3_'+n,L.build_rule(k,l,stp,cap)) for k,l,n,stp,cap in L.LEAN]
    labels={}
    for g,(_,p) in enumerate(parts[1:],start=1):
        for ei in p[0]:labels.setdefault(int(ei),g)
    supp,_=J.dedup_market_tick([p for name,p in parts[1:]])
    ss=np.argsort(supp[0],kind='stable');supp=tuple(v[ss] for v in supp)
    supp,_,_=J.cap_arrays(*supp,512)
    s=np.array([0]*len(wd[0])+[labels[int(ei)] for ei in supp[0]],dtype=np.int8)
    merged=[np.concatenate([wd[i],supp[i]]) for i in range(6)]
    order=np.lexsort((np.arange(len(merged[0])),merged[0])); merged=[v[order] for v in merged];s=s[order]
    es,xs,rs,ds,ps,hs=merged
    np.savez_compressed(OUT/'JAN033_ORIGINAL_SOURCE_LABELED_POSITIONS.npz',
        entry_index=es, exit_index=xs, entry_price_raw=rs,
        direction=ds, pnl=ps, source_id=s,
        source_names=np.asarray([n for n, _ in parts]))
    print('SOURCE_REBUILT',len(es),'net',round(ps.sum(),3),'component_ids',dict(zip(*np.unique(s,return_counts=True))),'seconds',round(time.time()-tick,2),flush=True)
    assert len(es)==47511 and abs(float(ps.sum())-93425.311)<.005
    D=J.DATA;t,a,b=D[:3]
    dd,pki,tri,_,_,_,_,alone,maxop,mfl,mfi,eqtr=sweep(t,a,b,es,xs,rs,ds,ps,s)
    marks,floating,balance,opens=sweep_fixed(t,a,b,es,xs,rs,ds,ps,s,pki,tri)
    peak=marks[0].sum();trough=marks[1].sum(); delta=marks[0]-marks[1]
    assert abs(peak-trough-dd)<0.01,(peak,trough,dd)
    assert abs(dd-56921.6)<0.05,(dd,pki,tri)
    name=[n for n,p in parts]
    def iso(i):return datetime.datetime.fromtimestamp(int(t[i])/1000,timezone.utc).isoformat()
    comp=[]
    for i,n in enumerate(name):
        vs=ps[s==i]
        comp.append(dict(layer=n,net=float(vs.sum()),trades=int(len(vs)),gross_profit=float(vs[vs>0].sum()),gross_loss=float(vs[vs<0].sum()),gross_loss_share=float(-vs[vs<0].sum()/31946.454),peak_to_trough_equity_contribution_usd=float(delta[i]),standalone_max_tick_dd_usd=float(alone[i]),peak_mark_equity=float(marks[0,i]),trough_mark_equity=float(marks[1,i]),peak_balance=float(balance[0,i]),trough_balance=float(balance[1,i]),peak_floating=float(floating[0,i]),trough_floating=float(floating[1,i]),peak_open=int(opens[0,i]),trough_open=int(opens[1,i]),winning_trades=int(np.count_nonzero(vs>0)),losing_trades=int(np.count_nonzero(vs<=0))))
    out={'study':'ORIGINAL_131E_RAW_BIDASK_SOURCE_COMPONENT_TICK_EQUITY_ATTRIBUTION_ONLY','raw_source':'same preserved 032 original Jan helper, not reoptimized','full_owner_L0_L7_certified':False,'capital_broker_certified':False,'data_quote_count':len(t),'drawdown':{'global_full_tick_equity_dd_usd':float(dd),'peak_time_utc':iso(pki),'trough_time_utc':iso(tri),'peak_tick':int(pki),'trough_tick':int(tri),'peak_research_equity_delta':float(peak),'trough_research_equity_delta':float(trough),'peak_to_trough_net_change':float(-delta.sum()),'peak_total_open':int(opens[0].sum()),'trough_total_open':int(opens[1].sum()),'largest_floating_unrealized_negative':float(mfl),'largest_floating_unrealized_negative_time':iso(mfi),'maxopen':int(maxop)},'components':comp,'qa':{'31_946_gross_reconciles':abs(sum(x['gross_loss'] for x in comp)+31946.454)<.02,'93425_net_reconciles':abs(sum(x['net'] for x in comp)-93425.311)<.02,'56921_dd_reconciles':abs(dd-56921.6)<.05,'sum_component_peak_trough_contributions':abs(sum(x['peak_to_trough_equity_contribution_usd'] for x in comp)-dd)<.01}}
    f=OUT/'JAN033_ORIGINAL_SOURCE_EXACT_TICK_LAYER_DD_ATTRIBUTION.json';f.write_text(json.dumps(out,indent=2))
    print('RESULT',json.dumps({'time':(iso(pki),iso(tri)),'dd':dd,'net':sum(x['net'] for x in comp),'maxopen':maxop,'components':[{k:x[k] for k in ('layer','gross_loss','peak_to_trough_equity_contribution_usd','standalone_max_tick_dd_usd','peak_open','trough_open')} for x in comp],'qa':out['qa']},indent=2),flush=True)
if __name__=='__main__':main()