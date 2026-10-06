from pathlib import Path
import json,time
import numpy as np,pandas as pd
from numba import njit
ROOT=Path('/mnt/data')
RAW=ROOT/'XAUUSD_DUKAS_2026_01_ticks.csv(3).gz'
LEGS=ROOT/'delta_a_research10/SA100_R10_JAN_CANDIDATE01_LEGS.csv'
DET=ROOT/'SA100_R10X3_CONT1800_BASKETKILL_EPISODES.csv'
ANN=ROOT/'SA100_R10I_ANNOTATED_EPISODES.csv'
OUT=ROOT/'SA100_R10Y_CONT180_FAILURE_STATE_SPECIALIST01_RERUN01.json'
DETAIL=ROOT/'SA100_R10Y_CONT180_FAILURE_STATE_EPISODES_RERUN01.csv'
LEGSOUT=ROOT/'SA100_R10Y_CONT180_FAILURE_STATE_LEGS_RERUN01.csv'
DAY=86400000;P75=np.array([20,20,21,21],np.int64);COST=.02

def econ(x):
    x=np.asarray(x,float); gp=float(x[x>0].sum()); gl=float(x[x<0].sum())
    return dict(n=int(len(x)),net=float(x.sum()),gp=gp,gl=gl,pf=float(gp/-gl) if gl<0 else None,win=float((x>0).mean()) if len(x) else None)

@njit(cache=False)
def eqscan(t,bid,ask,oi,ci,sd,ent,pnl):
    m=len(oi); O=np.argsort(oi); C=np.argsort(ci); op=cl=0; nl=ns=0; sel=ses=0.; bal=peak=100.; mineq=1e99; dd=0.; mf=1e99; ml=1e99; mp=0
    for k in range(len(t)):
        while cl<m and ci[C[cl]]<=k:
            j=C[cl]; bal+=pnl[j]
            if sd[j]==1: nl-=1; sel-=ent[j]
            else: ns-=1; ses-=ent[j]
            cl+=1
        while op<m and oi[O[op]]<=k:
            j=O[op]
            if ci[j]<=k: op+=1; continue
            if sd[j]==1: nl+=1; sel+=ent[j]
            else: ns+=1; ses+=ent[j]
            op+=1
        eq=bal+(nl*bid[k]-sel+ses-ns*ask[k])-COST*(nl+ns)
        if eq<mineq: mineq=eq
        if eq>peak: peak=eq
        if peak-eq>dd: dd=peak-eq
        pos=nl+ns
        if pos>mp: mp=pos
        if pos:
            mar=pos*((bid[k]+ask[k])/2.)/500.; fr=eq-mar; lv=eq/mar*100.
            if fr<mf: mf=fr
            if lv<ml: ml=lv
    return bal,mineq,dd,mf,ml,mp

def first_kill30(g,t,bid,ask):
    infos=[]
    for z in g.itertuples(index=False):
        oi=min(np.searchsorted(t,int(z.open_ms),side='left'),len(t)-1)
        ent=ask[oi] if int(z.side)==1 else bid[oi]
        infos.append((int(z.open_ms),int(z.close_ms),int(z.side),float(ent),float(z.pnl),str(z.leg)))
    a=np.searchsorted(t,min(x[0] for x in infos),side='left'); b=np.searchsorted(t,max(x[1] for x in infos),side='right')
    for k in range(a,b):
        tm=int(t[k]); real=0.; fl=0.
        for os,cs,sd,en,pf,lg in infos:
            if cs<=tm: real+=pf
            elif os<=tm<cs: fl += ((bid[k]-en) if sd==1 else (en-ask[k]))-COST
        if real+fl<=-30.: return k,infos
    return None,None

def main():
    st=time.time()
    D=pd.read_csv(DET).sort_values('event_id').reset_index(drop=True)
    A=pd.read_csv(ANN).sort_values('event_id').reset_index(drop=True)
    assert np.array_equal(D.event_id.values,A.event_id.values)
    legs=pd.read_csv(LEGS)
    orig={int(k):g.sort_values(['open_ms','close_ms']).copy() for k,g in legs.groupby('event_id')}
    raw=pd.read_csv(RAW,compression='gzip',usecols=['timestamp_ms_utc','ask_raw','bid_raw'],dtype={'timestamp_ms_utc':'int64','ask_raw':'int32','bid_raw':'int32'})
    t=raw.timestamp_ms_utc.to_numpy(np.int64); ar=raw.ask_raw.to_numpy(np.int64); br=raw.bid_raw.to_numpy(np.int64)
    tod=t%DAY; il=(tod>=8*3600000)&(tod<16.5*3600000); iny=(tod>=13*3600000)&(tod<22*3600000); ss=np.where(il&iny,2,np.where(il,1,np.where(iny,3,0))).astype(np.int8)
    spr=P75[ss]*10; mm=ar+br; bid=((mm-spr+10)//20)*10/1000.; ask=bid+spr/1000.

    # Reconstruct already-frozen X3 basket-kill episodes exactly from original physical legs.
    x3kill={}
    for qi in np.flatnonzero(D.tag.astype(str).to_numpy()=='BASKET_KILL30'):
        ev=int(D.event_id.iloc[qi]); k,infos=first_kill30(orig[ev],t,bid,ask)
        if k is None: raise RuntimeError(f'cannot reconstruct BASKET_KILL30 event {ev}')
        x3kill[ev]=(k,infos)

    # New R10Y specialist: only residual HOLD / CONT / 180s.
    target_y=(D.tag.astype(str)=='HOLD')&(D.candidate_pnl!=0)&(A.owner.astype(str)=='CONT')&(A.horizon_s==180)
    ysel={}; ystats=[]
    for qi in np.flatnonzero(target_y):
        ev=int(D.event_id.iloc[qi]); g=orig[ev]; pg=g[g.leg.astype(str)=='PRIMARY'].iloc[0]
        pside=int(pg.side); os=int(pg.open_ms); tm=os+10000
        oi=min(np.searchsorted(t,os,side='left'),len(t)-1); k=min(np.searchsorted(t,tm,side='right')-1,len(t)-1)
        entry=ask[oi] if pside==1 else bid[oi]; ix=np.arange(oi,k+1)
        aligned=(bid[ix]-entry) if pside==1 else (entry-ask[ix]); ppath=aligned-COST
        disp=float(ppath[-1]); rng=float(aligned.max()-aligned.min()); mae=float(ppath.min())
        fire=(disp<=4.0) and (rng>5.2) and (mae>-4.9)
        ystats.append((ev,fire,disp,rng,mae))
        if fire: ysel[ev]=(tm,k,pside)

    clegs=[]; new=D.candidate_pnl.to_numpy(float).copy(); tags=D.tag.astype(str).to_numpy(object)
    et=A.event_time_ms.to_numpy(np.int64); side_arr=A.side.to_numpy(np.int8)
    for qi,r in D.iterrows():
        ev=int(r.event_id); tag=str(r.tag)
        if float(r.candidate_pnl)==0: continue
        if tag=='HOLD' and ev in ysel:
            tm,k,pside=ysel[ev]; g=orig[ev]; tot=0.
            for z in g.itertuples(index=False):
                os=int(z.open_ms); cs=int(z.close_ms); sd=int(z.side); lg=str(z.leg)
                if cs<=tm:
                    clegs.append((ev,lg,os,cs,sd,float(z.pnl))); tot+=float(z.pnl)
                elif os<=tm<cs:
                    oix=min(np.searchsorted(t,os,side='left'),len(t)-1); en=ask[oix] if sd==1 else bid[oix]
                    pp=((bid[k]-en) if sd==1 else (en-ask[k]))-COST
                    clegs.append((ev,'R10Y_CLOSE10_'+lg,os,tm,sd,float(pp))); tot+=float(pp)
            rs=-pside; rtm=tm+30000; rk=min(np.searchsorted(t,rtm,side='right')-1,len(t)-1); ren=ask[k] if rs==1 else bid[k]
            rp=((bid[rk]-ren) if rs==1 else (ren-ask[rk]))-COST
            clegs.append((ev,'R10Y_REV30',tm,int(t[rk]),rs,float(rp))); tot+=float(rp)
            new[qi]=tot; tags[qi]='R10Y_REV30'
        elif tag=='HOLD':
            for z in orig[ev].itertuples(index=False): clegs.append((ev,str(z.leg),int(z.open_ms),int(z.close_ms),int(z.side),float(z.pnl)))
        elif tag=='BASKET_KILL30':
            k,infos=x3kill[ev]; tm=int(t[k]); tot=0.
            for os,cs,sd,en,pf,lg in infos:
                if cs<=tm:
                    clegs.append((ev,lg,os,cs,sd,pf)); tot+=pf
                elif os<=tm<cs:
                    pp=((bid[k]-en) if sd==1 else (en-ask[k]))-COST
                    clegs.append((ev,'BASKET_KILL30',os,tm,sd,float(pp))); tot+=float(pp)
            if abs(tot-float(r.candidate_pnl))>1e-6: raise RuntimeError(f'X3 pnl mismatch event {ev}: {tot} vs {r.candidate_pnl}')
        elif tag in ('R1','R3'):
            tm=int(et[qi]+5000); clegs.append((ev,tag+'_EXIT5',int(et[qi]),tm,int(side_arr[qi]),float(r.candidate_pnl)))
        elif tag=='R2':
            p1=float(A.exit5_pnl.iloc[qi]); tot=float(r.candidate_pnl)
            clegs.append((ev,'R2_EXIT5',int(et[qi]),int(et[qi]+5000),int(side_arr[qi]),p1)); clegs.append((ev,'R2_REV120',int(et[qi]+5000),int(et[qi]+125000),-int(side_arr[qi]),tot-p1))
        elif tag=='R4':
            p1=float(A.exit5_pnl.iloc[qi]); tot=float(r.candidate_pnl)
            clegs.append((ev,'R4_EXIT5',int(et[qi]),int(et[qi]+5000),int(side_arr[qi]),p1)); clegs.append((ev,'R4_REV90',int(et[qi]+5000),int(et[qi]+95000),-int(side_arr[qi]),tot-p1))
        elif tag=='J':
            clegs.append((ev,'J_EXIT10',int(et[qi]),int(et[qi]+10000),int(side_arr[qi]),float(r.candidate_pnl)))
        else: raise RuntimeError(tag)

    L=pd.DataFrame(clegs,columns=['event_id','leg','open_ms','close_ms','side','pnl']).sort_values(['close_ms','open_ms']).reset_index(drop=True)
    disc=D.discovery.to_numpy(bool)
    b0=100.; pk=100.; dd=0.; mn=100.
    for z in L.itertuples(index=False): b0+=z.pnl; pk=max(pk,b0); dd=max(dd,pk-b0); mn=min(mn,b0)
    oi=np.minimum(np.searchsorted(t,L.open_ms.to_numpy(np.int64),side='left'),len(t)-1); ci=np.minimum(np.searchsorted(t,L.close_ms.to_numpy(np.int64),side='left'),len(t)-1)
    sd=L.side.to_numpy(np.int8); ent=np.where(sd==1,ask[oi],bid[oi]); fb,meq,edd,mf,ml,mp=eqscan(t,bid,ask,oi.astype(np.int64),ci.astype(np.int64),sd,ent,L.pnl.to_numpy(float))

    detail=D.copy(); detail['candidate_pnl']=new; detail['tag']=tags; detail.to_csv(DETAIL,index=False); L.to_csv(LEGSOUT,index=False)
    ys=pd.DataFrame(ystats,columns=['event_id','selected','disp10','range10','mae10'])
    selected_ids=set(ys.loc[ys.selected,'event_id'].astype(int)); sel=np.array([int(e) in selected_ids for e in D.event_id],dtype=bool)
    base=D.candidate_pnl.to_numpy(float); changed=new[sel]; conv=int(np.sum((base[sel]<0)&(new[sel]>0)))
    dates=pd.to_datetime(A.event_time_ms,unit='ms',utc=True).dt.strftime('%Y-%m-%d').to_numpy()
    def daystat(day):
        m=(dates==day)&sel
        return dict(n=int(m.sum()),changed_win=float((new[m]>0).mean()) if m.sum() else None,delta_usd=float((new[m]-base[m]).sum()),converted_losses=int(np.sum((base[m]<0)&(new[m]>0))))
    out={
      'id':'SA100_R10Y_CONT180_FAILURE_STATE_SPECIALIST01_RERUN01','status':'COMPLETE_EXACT_TICK_FAILURE_STATE_CONVERSION',
      'prior_failed_attempt':'INCOMPLETE_TECHNICAL_FAILURE_DO_NOT_RESUME__wrapper omitted frozen BASKET_KILL30 tag handling; no economics produced',
      'rule':'remaining executed HOLD & owner CONT & horizon 180s; at +10s if aligned pnl<=+$4.00, path range>$5.20, MAE>-$4.90: close current basket/cancel future legs and reverse one 0.01 for 30s',
      'target_episodes':int(target_y.sum()),'selected_episodes':int(sel.sum()),'specialist_changed_win':float((changed>0).mean()),'converted_losses':conv,
      'jan29':daystat('2026-01-29'),'jan30':daystat('2026-01-30'),
      'physical_legs':econ(L.pnl),'episodes':econ(new),'discovery':econ(new[disc]),'holdout':econ(new[~disc]),
      'delta_net_usd':float(new.sum()-base.sum()),'episode_gl_reduction_usd':float(base[base<0].sum()-new[new<0].sum()),
      'realized_balance_dd_usd':dd,'realized_min_balance_usd':mn,'tick_min_equity_usd':meq,'tick_max_equity_dd_usd':edd,'min_free_margin_usd':mf,'min_margin_level_pct':ml,'max_positions':int(mp),
      'executed_episode_win':float((new[new!=0]>0).mean()),'disc_exec_win':float((new[disc&(new!=0)]>0).mean()),'hold_exec_win':float((new[(~disc)&(new!=0)]>0).mean()),
      'august_accessed':False,'elapsed_s':time.time()-st}
    OUT.write_text(json.dumps(out,indent=2)); print(json.dumps(out,indent=2))
if __name__=='__main__': main()