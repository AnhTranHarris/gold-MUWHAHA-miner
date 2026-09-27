import argparse, gc, json, math, os, time, hashlib
from pathlib import Path
import numpy as np
import pandas as pd
from numba import njit

ROOT=Path('/mnt/data')
CACHE=ROOT/'r9b020a_cache'
CACHE.mkdir(exist_ok=True)
FILES={
1:ROOT/'XAUUSD_DUKAS_2026_01_ticks.csv(3).gz',
2:ROOT/'XAUUSD_DUKAS_2026_02_ticks.csv(3).gz',
3:ROOT/'XAUUSD_DUKAS_2026_03_ticks.csv(3).gz',
4:ROOT/'XAUUSD_DUKAS_2026_04_ticks.csv(3).gz',
5:ROOT/'XAUUSD_DUKAS_2026_05_ticks.csv(3).gz',
6:ROOT/'XAUUSD_DUKAS_2026_06_ticks.csv(3).gz',
7:ROOT/'XAUUSD_DUKAS_2026_07_ticks.csv(2).gz',
}
TFS=(60,180,300,600,1200,3600,14400)
TF_NAMES={60:'M1',180:'M3',300:'M5',600:'M10',1200:'M20',3600:'H1',14400:'H4'}


def sha256(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for b in iter(lambda:f.read(1<<20),b''): h.update(b)
    return h.hexdigest()

def load_ticks(path):
    d=pd.read_csv(path,compression='gzip',usecols=['timestamp_ms_utc','ask_raw','bid_raw','ask_volume','bid_volume'],
                  dtype={'timestamp_ms_utc':'int64','ask_raw':'int64','bid_raw':'int64','ask_volume':'float64','bid_volume':'float64'})
    t=d.timestamp_ms_utc.to_numpy(np.int64)
    # Authoritative V2 convention: divide each quote separately, then average.
    ask=d.ask_raw.to_numpy(np.float64)/1000.0
    bid=d.bid_raw.to_numpy(np.float64)/1000.0
    mid=(ask+bid)*0.5
    av=d.ask_volume.to_numpy(np.float64); bv=d.bid_volume.to_numpy(np.float64)
    del d
    return t,mid,av,bv

def aggregate_active_seconds(t,mid,av,bv):
    sec=t//1000
    ids,idx,cnt=np.unique(sec,return_index=True,return_counts=True)
    last=idx+cnt-1
    o=mid[idx]; c=mid[last]
    h=np.maximum.reduceat(mid,idx); l=np.minimum.reduceat(mid,idx)
    asum=np.add.reduceat(av,idx); bsum=np.add.reduceat(bv,idx)
    return ids.astype(np.int64),o,h,l,c,cnt.astype(np.int64),asum/cnt,bsum/cnt

def build_s1(sec_ids,o,h,l,c,n,am,bm):
    N=len(sec_ids)
    disp=np.full(N,np.nan); eff=np.full(N,np.nan); rng=np.full(N,np.nan); turns=np.full(N,99.0)
    for i in range(10,N):
        w=c[i-9:i+1]; d=np.diff(w); travel=np.abs(d).sum()
        disp[i]=w[-1]-w[0]; eff[i]=abs(disp[i])/(travel+1e-12)
        rng[i]=h[i-9:i+1].max()-l[i-9:i+1].min()
        nz=np.sign(d); nz=nz[nz!=0]; turns[i]=np.sum(nz[1:]!=nz[:-1]) if len(nz)>1 else 0
    return disp,eff,rng,turns

def aggregate_tf(t,mid,tfsec):
    bucket=t//(tfsec*1000)
    ids,idx,cnt=np.unique(bucket,return_index=True,return_counts=True)
    last=idx+cnt-1
    o=mid[idx]; c=mid[last]; h=np.maximum.reduceat(mid,idx); l=np.minimum.reduceat(mid,idx)
    end=(ids+1)*tfsec
    prev=np.r_[np.nan,c[:-1]]
    tr=np.maximum(h-l,np.maximum(np.abs(h-prev),np.abs(l-prev)))
    atr=np.full(len(tr),np.nan); e=np.nan
    for i,x in enumerate(tr):
        if not np.isfinite(x): continue
        e=x if not np.isfinite(e) else (13.0/14.0)*e+(1.0/14.0)*x
        if i>=13: atr[i]=e
    return {'end':end.astype(np.int64),'o':o,'h':h,'l':l,'c':c,'atr':atr}

def build_m5_atr_by_sec(sec_ids,t,mid):
    z=aggregate_tf(t,mid,300)
    j=np.searchsorted(z['end'],sec_ids,side='right')-1
    out=np.full(len(sec_ids),np.nan); ok=j>=0; out[ok]=z['atr'][j[ok]]
    return out

@njit(cache=True)
def session_for_sec(sec):
    lon_off=60 if (sec>=1774746000 and sec<1792890000) else 0
    ny_off=-240 if (sec>=1772953200 and sec<1793512800) else -300
    lm=((sec+lon_off*60)%86400)//60; nm=((sec+ny_off*60)%86400)//60
    l=(lm>=480 and lm<990); n=(nm>=480 and nm<1020)
    if l and n: return 2
    if l: return 1
    if n: return 3
    return 0

@njit(cache=True)
def r9_baseline_events(t,mid,sec_ids,s1_disp,s1_eff,s1_rng,s1_turns,atr_by_sec):
    maxtr=max(50000,len(t)//20)
    ev_i=np.empty(maxtr,np.int64); ev_secidx=np.empty(maxtr,np.int64); ev_side=np.empty(maxtr,np.int8)
    pnl=np.empty(maxtr,np.float64); hold=np.empty(maxtr,np.float64)
    ntr=0; sec_idx=-1; last_sec=-1; minute=-1; buy_lvl=0.; sell_lvl=0.; pending=0; rearms=0
    pos=0; entry=0.; stop=0.; opent=0; last_pos=0; rearm_pending=0
    for i in range(len(t)):
        tt=t[i]; p=mid[i]; sec=tt//1000
        if sec!=last_sec:
            while sec_idx+1<len(sec_ids) and sec_ids[sec_idx+1] < sec: sec_idx+=1
            last_sec=sec
        mn=tt//60000
        if mn!=minute:
            minute=mn; rearms=0; pending=2
            buy_lvl=round((p+.15)*100.)/100.; sell_lvl=round((p-.15)*100.)/100.
        bid=p-.10; ask=p+.10
        if pos!=0:
            exited=False; ex=0.
            if (pos>0 and bid<=stop) or (pos<0 and ask>=stop): ex=bid if pos>0 else ask; exited=True
            elif tt-opent>=30000: ex=bid if pos>0 else ask; exited=True
            else:
                if pos>0 and bid-entry>=.10:
                    cand=bid-.03
                    if cand>stop+.005: stop=cand
                elif pos<0 and entry-ask>=.10:
                    cand=ask+.03
                    if cand<stop-.005: stop=cand
            if exited:
                pnl[ntr-1]=(ex-entry)*pos; hold[ntr-1]=(tt-opent)/1000.; last_pos=pos; pos=0; rearm_pending=1
            continue
        if rearm_pending:
            rearm_pending=0
            if tt//60000==minute and rearms<3: rearms+=1; pending=-last_pos
            else: pending=0
            continue
        if pending==0 or sec_idx<10: continue
        av=atr_by_sec[sec_idx]
        if not np.isfinite(av): continue
        ss=session_for_sec(sec_ids[sec_idx]); floor=2.5
        if ss==1: floor=2.0
        elif ss==2 or ss==3: floor=1.75
        if av+1e-12<floor: continue
        side=0
        if (pending==2 or pending==1) and ask>=buy_lvl: side=1
        elif (pending==2 or pending==-1) and bid<=sell_lvl: side=-1
        if side==0: continue
        dd=s1_disp[sec_idx]; ee=s1_eff[sec_idx]; rr=s1_rng[sec_idx]; tr=s1_turns[sec_idx]
        if not(ee>=.70 and rr>=.50 and tr<=9): continue
        if side>0 and dd<.15: continue
        if side<0 and dd>-.15: continue
        if ntr>=maxtr: break
        ev_i[ntr]=i; ev_secidx[ntr]=sec_idx; ev_side[ntr]=side
        entry=ask if side>0 else bid; stop=bid-.30 if side>0 else ask+.30
        pos=side; opent=tt; pending=0; pnl[ntr]=np.nan; hold[ntr]=np.nan; ntr+=1
    return ev_i[:ntr],ev_secidx[:ntr],ev_side[:ntr],pnl[:ntr],hold[:ntr]

@njit(cache=True)
def cf_trade(t,mid,start_i,side,stopdist,activation,trail,maxhold_ms):
    p=mid[start_i]; entry=(p+.10) if side>0 else (p-.10)
    stop=(p-.10-stopdist) if side>0 else (p+.10+stopdist)
    opent=t[start_i]; end_i=start_i
    for i in range(start_i+1,len(t)):
        tt=t[i]
        if tt-opent>maxhold_ms+2000: break
        p=mid[i]; bid=p-.10; ask=p+.10
        fav=(bid-entry) if side>0 else (entry-ask)
        if (side>0 and bid<=stop) or (side<0 and ask>=stop):
            ex=bid if side>0 else ask; return (ex-entry)*side
        if tt-opent>=maxhold_ms:
            ex=bid if side>0 else ask; return (ex-entry)*side
        if side>0 and fav>=activation:
            cand=bid-trail
            if cand>stop+.005: stop=cand
        elif side<0 and fav>=activation:
            cand=ask+trail
            if cand<stop-.005: stop=cand
        end_i=i
    p=mid[end_i]; ex=(p-.10) if side>0 else (p+.10)
    return (ex-entry)*side

@njit(cache=True)
def harv_counterfactuals(t,mid,ev_i,side):
    n=len(ev_i); cont=np.empty(n,np.float64); fade=np.empty(n,np.float64)
    for k in range(n):
        cont[k]=cf_trade(t,mid,ev_i[k],side[k],5.00,.03,.02,90000)
        fade[k]=cf_trade(t,mid,ev_i[k],-side[k],5.00,.03,.02,90000)
    return cont,fade

def structural_state(bars,k=2):
    h=bars['h']; l=bars['l']; c=bars['c']; atr=bars['atr']; n=len(c)
    state=np.zeros(n,np.int8); age=np.full(n,9999,np.int32); bos_age=np.full(n,9999,np.int32)
    boundary=np.full(n,np.nan); dist=np.full(n,np.nan); depth=np.zeros(n); event=np.zeros(n,np.int8)
    last_sh=np.nan; last_sl=np.nan; st=0; state_start=-1; last_bos=-1; active=np.nan; last_depth=0.
    for i in range(n):
        center=i-k
        if center>=k:
            wh=h[center-k:center+k+1]; wl=l[center-k:center+k+1]
            if h[center]>=np.nanmax(wh)-1e-12: last_sh=float(h[center])
            if l[center]<=np.nanmin(wl)+1e-12: last_sl=float(l[center])
        prevc=c[i-1] if i>0 else c[i]
        ev=0; dep=last_depth
        if np.isfinite(last_sh) and c[i]>last_sh and prevc<=last_sh:
            dep=(c[i]-last_sh)/(atr[i]+1e-12) if np.isfinite(atr[i]) else 0.
            ev=1; active=last_sh; last_bos=i
            if st!=1: st=1; state_start=i
        elif np.isfinite(last_sl) and c[i]<last_sl and prevc>=last_sl:
            dep=(last_sl-c[i])/(atr[i]+1e-12) if np.isfinite(atr[i]) else 0.
            ev=-1; active=last_sl; last_bos=i
            if st!=-1: st=-1; state_start=i
        if ev!=0: last_depth=max(0.,dep)
        state[i]=st; event[i]=ev; boundary[i]=active; depth[i]=last_depth
        if state_start>=0: age[i]=i-state_start
        if last_bos>=0: bos_age[i]=i-last_bos
        if np.isfinite(active) and np.isfinite(atr[i]) and atr[i]>0: dist[i]=abs(c[i]-active)/atr[i]
    return {'state':state,'age':age,'bos_age':bos_age,'boundary':boundary,'dist':dist,'depth':depth,'event':event}

def event_struct_features(ev_sec,side,tf_bars):
    cols={}; states=[]; dists=[]; ages=[]; bosages=[]; depths=[]
    for tf in TFS:
        z=tf_bars[tf]; st=z['struct']; j=np.searchsorted(z['end'],ev_sec,side='right')-1
        ok=j>=0; jj=np.clip(j,0,len(z['end'])-1)
        s=st['state'][jj].astype(float); ag=st['age'][jj].astype(float); ba=st['bos_age'][jj].astype(float)
        di=st['dist'][jj].astype(float); de=st['depth'][jj].astype(float); ev=st['event'][jj].astype(float)
        s[~ok]=0; ag[~ok]=9999; ba[~ok]=9999; di[~ok]=np.nan; de[~ok]=0; ev[~ok]=0
        tag=TF_NAMES[tf]
        cols[f'{tag}_state_al']=s*side; cols[f'{tag}_age']=ag; cols[f'{tag}_bos_age']=ba
        cols[f'{tag}_dist']=di; cols[f'{tag}_depth']=de; cols[f'{tag}_event_al']=ev*side
        states.append(s); dists.append(di); ages.append(ag); bosages.append(ba); depths.append(de)
    S=np.column_stack(states); D=np.column_stack(dists); A=np.column_stack(ages); BA=np.column_stack(bosages); DP=np.column_stack(depths)
    align=S*side[:,None]
    cols['struct_align_count']=np.sum(align>0,axis=1)
    cols['struct_conflict_count']=np.sum(align<0,axis=1)
    # Default semantic owner: highest active TF with accepted structure within 3 ATR and BOS age <= 20 bars.
    owner_idx=np.full(len(ev_sec),-1,np.int16); owner_al=np.zeros(len(ev_sec)); owner_dist=np.full(len(ev_sec),np.nan)
    owner_age=np.full(len(ev_sec),9999.); owner_bos_age=np.full(len(ev_sec),9999.); owner_depth=np.zeros(len(ev_sec))
    for j in range(len(TFS)-1,-1,-1):
        elig=(owner_idx<0)&(S[:,j]!=0)&np.isfinite(D[:,j])&(D[:,j]<=3.0)&(BA[:,j]<=20)
        owner_idx[elig]=j; owner_al[elig]=align[elig,j]; owner_dist[elig]=D[elig,j]
        owner_age[elig]=A[elig,j]; owner_bos_age[elig]=BA[elig,j]; owner_depth[elig]=DP[elig,j]
    cols['owner_tf']=owner_idx.astype(float); cols['owner_align']=owner_al; cols['owner_dist']=owner_dist
    cols['owner_age']=owner_age; cols['owner_bos_age']=owner_bos_age; cols['owner_depth']=owner_depth
    # lower-TF confirmation/conflict relative to chosen owner direction/event side
    lc=np.zeros(len(ev_sec)); lf=np.zeros(len(ev_sec))
    for r in range(len(ev_sec)):
        oi=owner_idx[r]
        if oi>0:
            own=np.sign(owner_al[r])
            vals=align[r,:oi]
            lc[r]=np.sum(np.sign(vals)==own) if own!=0 else 0
            lf[r]=np.sum((vals!=0)&(np.sign(vals)!=own)) if own!=0 else 0
    cols['lower_confirm']=lc; cols['lower_conflict']=lf
    return cols

def month_cache(m):
    out=CACHE/f'R9B_020A_M{m:02d}.pkl.gz'
    summ=CACHE/f'R9B_020A_M{m:02d}_summary.json'
    if out.exists() and summ.exists():
        return pd.read_pickle(out,compression='gzip'), json.load(open(summ))
    t0=time.time(); t,mid,av,bv=load_ticks(FILES[m])
    sec_ids,o,h,l,c,n,am,bm=aggregate_active_seconds(t,mid,av,bv)
    sd,se,sr,st=build_s1(sec_ids,o,h,l,c,n,am,bm); atrsec=build_m5_atr_by_sec(sec_ids,t,mid)
    ev_i,ev_si,side,pnl,hold=r9_baseline_events(t,mid,sec_ids,sd,se,sr,st,atrsec)
    good=np.isfinite(pnl); ev_i=ev_i[good]; ev_si=ev_si[good]; side=side[good]; pnl=pnl[good]
    cont,fade=harv_counterfactuals(t,mid,ev_i,side)
    tf_bars={}
    for tf in TFS:
        z=aggregate_tf(t,mid,tf); z['struct']=structural_state(z); tf_bars[tf]=z
    cols={'month':np.full(len(ev_i),m,np.int8),'time_ms':t[ev_i],'event_sec':t[ev_i]//1000,'side':side,
          'base_pnl':pnl,'cont_pnl':cont,'fade_pnl':fade}
    cols.update(event_struct_features(t[ev_i]//1000,side,tf_bars))
    df=pd.DataFrame(cols)
    df.to_pickle(out,compression='gzip')
    gp=float(pnl[pnl>0].sum()); gl=float(pnl[pnl<0].sum())
    sm={'month':m,'raw_sha256':sha256(FILES[m]),'ticks':int(len(t)),'trades':int(len(pnl)),'net':float(pnl.sum()),'gp':gp,'gl':gl,
        'win':float((pnl>0).mean()),'elapsed_seconds':time.time()-t0,'cache_sha256':sha256(out)}
    json.dump(sm,open(summ,'w'),indent=2,sort_keys=True)
    del t,mid,av,bv,sec_ids,o,h,l,c,n,am,bm,tf_bars; gc.collect()
    return df,sm

def metrics(pnl):
    x=np.asarray(pnl,float); x=x[np.isfinite(x)]
    if len(x)==0: return {'trades':0,'winners':0,'win':0.,'net':0.,'gp':0.,'gl':0.,'pf':0.}
    gp=float(x[x>0].sum()); gl=float(x[x<0].sum())
    return {'trades':int(len(x)),'winners':int((x>0).sum()),'win':float((x>0).mean()),'net':float(x.sum()),'gp':gp,'gl':gl,'pf':float(gp/(-gl)) if gl<0 else 1e9}

def fit_eval(all_df):
    from sklearn.tree import DecisionTreeClassifier
    feat=['owner_tf','owner_align','owner_dist','owner_age','owner_bos_age','owner_depth','lower_confirm','lower_conflict','struct_align_count','struct_conflict_count']
    d=all_df.copy()
    # Teacher-only label: best profitable fixed HARVEST action; abstain if neither positive.
    y=np.where(np.maximum(d.cont_pnl.values,d.fade_pnl.values)<=0,2,np.where(d.cont_pnl.values>=d.fade_pnl.values,1,0)) # 1 CONT, 0 FADE, 2 abstain
    d['label']=y
    X=d[feat].replace([np.inf,-np.inf],np.nan).fillna(99.0).to_numpy(float)
    train=d.month<=3; apr=d.month==4
    model=DecisionTreeClassifier(max_depth=4,min_samples_leaf=800,class_weight={0:1.0,1:1.0,2:1.5},random_state=17)
    model.fit(X[train],y[train])
    proba=model.predict_proba(X)
    classes=model.classes_
    # April-calibrated confidence threshold with density guards relative to unthresholded acted predictions.
    candidates=[]
    for th in [0.35,0.40,0.45,0.50,0.55,0.60]:
        pred=classes[np.argmax(proba,axis=1)]; conf=np.max(proba,axis=1)
        act=(pred!=2)&(conf>=th)
        chosen=np.where(pred==1,d.cont_pnl.values,d.fade_pnl.values)
        p=np.where(act,chosen,np.nan)
        ma=metrics(p[apr & np.isfinite(p)])
        # reference: no confidence filter but still model abstain
        act0=(classes[np.argmax(proba,axis=1)]!=2)
        p0=np.where(act0,np.where(classes[np.argmax(proba,axis=1)]==1,d.cont_pnl.values,d.fade_pnl.values),np.nan)
        ref=metrics(p0[apr & np.isfinite(p0)])
        trret=ma['trades']/max(1,ref['trades']); wret=ma['winners']/max(1,ref['winners'])
        eligible=(trret>=0.95 and wret>=0.97)
        candidates.append((eligible,ma['gl'],ma['net'],wret,trret,th,ma,ref))
    elig=[x for x in candidates if x[0]]
    pick=max(elig,key=lambda x:(x[1],x[2],x[3])) if elig else max(candidates,key=lambda x:(x[4]+x[3],x[1],x[2]))
    th=pick[5]
    pred=classes[np.argmax(proba,axis=1)]; conf=np.max(proba,axis=1); act=(pred!=2)&(conf>=th)
    chosen=np.where(pred==1,d.cont_pnl.values,d.fade_pnl.values); d['stageA_pnl']=np.where(act,chosen,np.nan); d['pred']=pred; d['conf']=conf
    periods={'jan_mar':d.month<=3,'april':d.month==4,'may_jun':d.month.isin([5,6]),'july':d.month==7,'jan_jul':d.month<=7,'may_jul':d.month>=5}
    out={k:metrics(d.loc[mask,'stageA_pnl'].dropna()) for k,mask in periods.items()}
    out['months']={str(m):metrics(d.loc[d.month==m,'stageA_pnl'].dropna()) for m in range(1,8)}
    out['teacher']={str(m):{'neither_rate':float((d.loc[d.month==m,'label']==2).mean()),'cont_rate':float((d.loc[d.month==m,'label']==1).mean()),'fade_rate':float((d.loc[d.month==m,'label']==0).mean())} for m in range(1,8)}
    out['selected_threshold']=th; out['april_calibration']={'eligible':bool(pick[0]),'winner_retention':pick[3],'trade_retention':pick[4],'candidate':pick[6],'reference':pick[7]}
    out['feature_importance']={f:float(v) for f,v in zip(feat,model.feature_importances_) if v>0}
    out['classes']=[int(x) for x in classes]
    return d,out

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--month',type=int); ap.add_argument('--fit',action='store_true'); a=ap.parse_args()
    if a.month:
        _,sm=month_cache(a.month); print(json.dumps(sm,indent=2,sort_keys=True)); return
    dfs=[]; sms=[]
    for m in range(1,8):
        d,sm=month_cache(m); dfs.append(d); sms.append(sm)
    all_df=pd.concat(dfs,ignore_index=True)
    scored,res=fit_eval(all_df)
    scored[['month','time_ms','side','cont_pnl','fade_pnl','label','pred','conf','stageA_pnl','owner_tf','owner_align','owner_dist','owner_age','owner_bos_age','owner_depth','lower_confirm','lower_conflict','struct_align_count','struct_conflict_count']].to_pickle(CACHE/'R9B_020A_SCORED.pkl.gz',compression='gzip')
    res.update({'unit':'R9B_GAMMA2_HIERARCHICAL_PATTERN_STATE_020_A_STRUCTURAL_OWNER','status':'COMPLETED_LOCAL_DIAGNOSTIC','source':'authoritative r9_research_v2 semantics independently reconstructed','august_accessed':False,'month_source_summaries':sms})
    json.dump(res,open(CACHE/'R9B_020A_RESULT.json','w'),indent=2,sort_keys=True)
    print(json.dumps(res,indent=2,sort_keys=True))

if __name__=='__main__': main()
