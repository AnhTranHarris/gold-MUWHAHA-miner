import os, glob, gzip, math, json, argparse, gc
import numpy as np
import pandas as pd
from numba import njit

DATA_DIR='/mnt/data'
OUT='/mnt/data/r9_research_v2'
os.makedirs(OUT,exist_ok=True)

MONTH_FILES={m:glob.glob(f'{DATA_DIR}/XAUUSD_DUKAS_2026_{m:02d}_ticks.csv*.gz')[0] for m in range(1,8)}

def load_ticks(month):
    f=MONTH_FILES[month]
    df=pd.read_csv(f,compression='gzip',dtype={'timestamp_ms_utc':'int64','ask_raw':'int64','bid_raw':'int64','ask_volume':'float64','bid_volume':'float64'})
    t=df.timestamp_ms_utc.to_numpy(np.int64)
    ask=df.ask_raw.to_numpy(np.float64)/1000.0
    bid=df.bid_raw.to_numpy(np.float64)/1000.0
    mid=(ask+bid)*0.5
    av=df.ask_volume.to_numpy(np.float64); bv=df.bid_volume.to_numpy(np.float64)
    del df
    return t,mid,av,bv

def aggregate_active_seconds(t,mid,av,bv):
    sec=t//1000
    ids, idx, cnt=np.unique(sec,return_index=True,return_counts=True)
    last=idx+cnt-1
    o=mid[idx]; c=mid[last]
    h=np.maximum.reduceat(mid,idx); l=np.minimum.reduceat(mid,idx)
    asum=np.add.reduceat(av,idx); bsum=np.add.reduceat(bv,idx)
    am=asum/cnt; bm=bsum/cnt
    return ids.astype(np.int64),o,h,l,c,cnt.astype(np.int64),am,bm

def build_s1(sec_ids,o,h,l,c,n,am,bm):
    N=len(sec_ids)
    disp=np.full(N,np.nan); eff=np.full(N,np.nan); rng=np.full(N,np.nan); turns=np.full(N,99.0)
    tickratio=np.full(N,np.nan); volimb=np.full(N,np.nan)
    for i in range(10,N):
        w=c[i-9:i+1]
        d=np.diff(w)
        travel=np.abs(d).sum()
        disp[i]=w[-1]-w[0]
        eff[i]=abs(disp[i])/(travel+1e-12)
        rng[i]=h[i-9:i+1].max()-l[i-9:i+1].min()
        nz=np.sign(d); nz=nz[nz!=0]
        turns[i]=np.sum(nz[1:]!=nz[:-1]) if len(nz)>1 else 0
        tickratio[i]=n[i]/(np.mean(n[max(0,i-10):i])+1e-9)
        volimb[i]=(bm[i]-am[i])/(bm[i]+am[i]+1e-12)
    return disp,eff,rng,turns,tickratio,volimb

def aggregate_tf(t,mid,tf_sec):
    bid=t//(tf_sec*1000)
    ids,idx,cnt=np.unique(bid,return_index=True,return_counts=True)
    last=idx+cnt-1
    o=mid[idx]; c=mid[last]; h=np.maximum.reduceat(mid,idx); l=np.minimum.reduceat(mid,idx)
    end=(ids+1)*tf_sec
    prev=np.r_[np.nan,c[:-1]]
    tr=np.maximum(h-l,np.maximum(np.abs(h-prev),np.abs(l-prev)))
    atr=np.full(len(tr),np.nan)
    e=np.nan
    for i,x in enumerate(tr):
        if not np.isfinite(x): continue
        if not np.isfinite(e): e=x
        else: e=(13/14)*e+(1/14)*x
        if i>=13: atr[i]=e
    prev3_hi=np.full(len(c),np.nan); prev3_lo=np.full(len(c),np.nan)
    pos20=np.full(len(c),np.nan); range_atr=np.full(len(c),np.nan)
    for i in range(len(c)):
        if i>=3:
            prev3_hi[i]=np.max(h[i-3:i]); prev3_lo[i]=np.min(l[i-3:i])
        if i>=20:
            hh=np.max(h[i-20:i]); ll=np.min(l[i-20:i]); pos20[i]=2*(c[i]-ll)/(hh-ll+1e-12)-1
        if np.isfinite(atr[i]): range_atr[i]=(h[i]-l[i])/(atr[i]+1e-12)
    ret=np.r_[np.nan,np.diff(c)]
    body=c-o
    return {'end':end.astype(np.int64),'o':o,'h':h,'l':l,'c':c,'atr':atr,'ret':ret,'body':body,'p3h':prev3_hi,'p3l':prev3_lo,'pos20':pos20,'range_atr':range_atr}

def build_m5_atr_by_sec(sec_ids,t,mid):
    tf=aggregate_tf(t,mid,300)
    j=np.searchsorted(tf['end'],sec_ids,side='right')-1
    out=np.full(len(sec_ids),np.nan)
    ok=j>=0; out[ok]=tf['atr'][j[ok]]
    return out,tf

@njit
def session_for_sec(sec):
    lon_off=60 if (sec>=1774746000 and sec<1792890000) else 0
    ny_off=-240 if (sec>=1772953200 and sec<1793512800) else -300
    lm=((sec+lon_off*60)%86400)//60
    nm=((sec+ny_off*60)%86400)//60
    l=(lm>=480 and lm<990)
    n=(nm>=480 and nm<1020)
    if l and n: return 2
    if l: return 1
    if n: return 3
    return 0

@njit
def r9_baseline_events(t,mid,sec_ids,s1_disp,s1_eff,s1_rng,s1_turns,atr_by_sec):
    maxtr=max(50000,len(t)//20)
    ev_i=np.empty(maxtr,np.int64); ev_secidx=np.empty(maxtr,np.int64); ev_side=np.empty(maxtr,np.int8); ev_rearm=np.empty(maxtr,np.int8)
    pnl=np.empty(maxtr,np.float64); hold=np.empty(maxtr,np.float64); mfe=np.empty(maxtr,np.float64); mae=np.empty(maxtr,np.float64)
    ntr=0; sec_idx=-1; last_sec=-1
    minute=-1; buy_lvl=0.; sell_lvl=0.; pending=0; rearms=0
    pos=0; entry=0.; stop=0.; opent=0; maxfav=0.; maxadv=0.; last_pos=0; rearm_pending=0
    for i in range(len(t)):
        tt=t[i]; p=mid[i]; sec=tt//1000
        if sec!=last_sec:
            while sec_idx+1<len(sec_ids) and sec_ids[sec_idx+1] < sec:
                sec_idx+=1
            last_sec=sec
        mn=tt//60000
        if mn!=minute:
            minute=mn; rearms=0; pending=2
            buy_lvl=round((p+.15)*100.)/100.; sell_lvl=round((p-.15)*100.)/100.
        bid=p-.10; ask=p+.10
        if pos!=0:
            fav=(bid-entry) if pos>0 else (entry-ask)
            adv=(entry-bid) if pos>0 else (ask-entry)
            if fav>maxfav: maxfav=fav
            if adv>maxadv: maxadv=adv
            exited=False; ex=0.
            if (pos>0 and bid<=stop) or (pos<0 and ask>=stop):
                ex=bid if pos>0 else ask; exited=True
            elif tt-opent>=30000:
                ex=bid if pos>0 else ask; exited=True
            else:
                if pos>0 and bid-entry>=.10:
                    cand=bid-.03
                    if cand>stop+.005: stop=cand
                elif pos<0 and entry-ask>=.10:
                    cand=ask+.03
                    if cand<stop-.005: stop=cand
            if exited:
                pnl[ntr-1]=(ex-entry)*pos; hold[ntr-1]=(tt-opent)/1000.; mfe[ntr-1]=maxfav; mae[ntr-1]=maxadv
                last_pos=pos; pos=0; rearm_pending=1
            continue
        if rearm_pending:
            rearm_pending=0
            if tt//60000==minute and rearms<3:
                rearms+=1; pending=-last_pos
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
        ev_i[ntr]=i; ev_secidx[ntr]=sec_idx; ev_side[ntr]=side; ev_rearm[ntr]=rearms
        entry=ask if side>0 else bid; stop=bid-.30 if side>0 else ask+.30; pos=side; opent=tt; pending=0; maxfav=0.; maxadv=0.
        pnl[ntr]=np.nan; hold[ntr]=np.nan; mfe[ntr]=np.nan; mae[ntr]=np.nan; ntr+=1
    return ev_i[:ntr],ev_secidx[:ntr],ev_side[:ntr],ev_rearm[:ntr],pnl[:ntr],hold[:ntr],mfe[:ntr],mae[:ntr]

@njit
def cf_trade(t,mid,start_i,side,stopdist,activation,trail,maxhold_ms):
    p=mid[start_i]; entry=(p+.10) if side>0 else (p-.10)
    stop=(p-.10-stopdist) if side>0 else (p+.10+stopdist)
    opent=t[start_i]; mfe=0.; mae=0.; armed=0; end_i=start_i
    for i in range(start_i+1,len(t)):
        tt=t[i]
        if tt-opent>maxhold_ms+2000: break
        p=mid[i]; bid=p-.10; ask=p+.10
        fav=(bid-entry) if side>0 else (entry-ask)
        adv=(entry-bid) if side>0 else (ask-entry)
        if fav>mfe: mfe=fav
        if adv>mae: mae=adv
        if (side>0 and bid<=stop) or (side<0 and ask>=stop):
            ex=bid if side>0 else ask; return (ex-entry)*side,(tt-opent)/1000.,mfe,mae,armed
        if tt-opent>=maxhold_ms:
            ex=bid if side>0 else ask; return (ex-entry)*side,(tt-opent)/1000.,mfe,mae,armed
        if side>0 and bid-entry>=activation:
            armed=1; cand=bid-trail
            if cand>stop+.005: stop=cand
        elif side<0 and entry-ask>=activation:
            armed=1; cand=ask+trail
            if cand<stop-.005: stop=cand
        end_i=i
    p=mid[end_i]; ex=(p-.10) if side>0 else (p+.10)
    return (ex-entry)*side,(t[end_i]-opent)/1000.,mfe,mae,armed

@njit
def counterfactuals(t,mid,ev_i,ev_side):
    n=len(ev_i); out=np.empty((n,12),np.float64)
    for k in range(n):
        i=ev_i[k]; s=ev_side[k]
        a=cf_trade(t,mid,i,s,.30,.10,.03,30000)
        b=cf_trade(t,mid,i,-s,.30,.10,.03,30000)
        c=cf_trade(t,mid,i,s,5.00,.03,.02,90000)
        d=cf_trade(t,mid,i,-s,5.00,.03,.02,90000)
        for j,x in enumerate((a,b,c,d)):
            out[k,j*3]=x[0]; out[k,j*3+1]=x[2]; out[k,j*3+2]=x[3]
    return out

def event_multiscale_features(ev_t,side,t,mid,tfs=(60,180,300,600,1200,3600,14400)):
    feats={}; align=[]
    for tfsec in tfs:
        z=aggregate_tf(t,mid,tfsec)
        es=ev_t//1000; j=np.searchsorted(z['end'],es,side='right')-1
        ok=j>=0; jj=np.clip(j,0,len(z['end'])-1)
        atr=z['atr'][jj]; ret=z['ret'][jj]; body=z['body'][jj]; pos=z['pos20'][jj]; rat=z['range_atr'][jj]
        p3h=z['p3h'][jj]; p3l=z['p3l'][jj]; close=z['c'][jj]
        salign=side*ret/(atr+1e-12); balign=side*body/(atr+1e-12); palign=side*pos
        br=np.where(side>0,(close>p3h).astype(float),(close<p3l).astype(float))
        salign[~ok]=np.nan; balign[~ok]=np.nan; palign[~ok]=np.nan; rat[~ok]=np.nan; br[~ok]=np.nan
        tag=f'tf{tfsec}'
        feats[tag+'_retatr']=salign; feats[tag+'_bodyatr']=balign; feats[tag+'_pos20']=palign; feats[tag+'_rangeatr']=rat; feats[tag+'_break3']=br
        align.append(salign)
    A=np.column_stack(align)
    feats['align_pos_count']=np.sum(A>0,axis=1); feats['align_strong_count']=np.sum(A>.15,axis=1)
    feats['align_min']=np.nanmin(A,axis=1); feats['align_mean']=np.nanmean(A,axis=1); feats['align_max']=np.nanmax(A,axis=1)
    return feats

def recent_second_features(ev_secidx,side,sec_ids,o,h,l,c,n,am,bm):
    m=len(ev_secidx); out={}
    for w in [1,2,5,10,15,30]:
        disp=np.full(m,np.nan); eff=np.full(m,np.nan); rng=np.full(m,np.nan); turns=np.full(m,np.nan); ticks=np.full(m,np.nan); imb=np.full(m,np.nan)
        for k,ii in enumerate(ev_secidx):
            if ii-w+1<0: continue
            sl=slice(ii-w+1,ii+1); cs=c[sl]; d=np.diff(cs); travel=np.abs(d).sum()
            disp[k]=(cs[-1]-cs[0])*side[k]; eff[k]=abs(cs[-1]-cs[0])/(travel+1e-12)
            rng[k]=h[sl].max()-l[sl].min()
            nz=np.sign(d); nz=nz[nz!=0]; turns[k]=np.sum(nz[1:]!=nz[:-1]) if len(nz)>1 else 0
            ticks[k]=n[sl].sum(); imb[k]=np.mean((bm[sl]-am[sl])/(bm[sl]+am[sl]+1e-12))*side[k]
        out[f's{w}_disp_al']=disp; out[f's{w}_eff']=eff; out[f's{w}_range']=rng; out[f's{w}_turns']=turns; out[f's{w}_ticks']=ticks; out[f's{w}_volimb_al']=imb
    out['compress5_30']=out['s5_range']/(out['s30_range']+1e-9)
    out['compress15_30']=out['s15_range']/(out['s30_range']+1e-9)
    out['tick5_30']=out['s5_ticks']/(out['s30_ticks']/6+1e-9)
    return out

@njit
def dc_features_at_events(t,mid,ev_i,ev_side,ths):
    n=len(ev_i); m=len(ths)
    pol=np.zeros((n,m)); age=np.zeros((n,m)); osx=np.zeros((n,m)); rate=np.zeros((n,m))
    direction=np.zeros(m,np.int8); hi=np.full(m,mid[0]); lo=np.full(m,mid[0]); evt=np.full(m,t[0]); conf=np.full(m,mid[0])
    k=0
    for i in range(len(t)):
        p=mid[i]; tt=t[i]
        for j in range(m):
            th=ths[j]
            if direction[j]>=0:
                if p>hi[j]: hi[j]=p
                if hi[j]-p>=th:
                    direction[j]=-1; lo[j]=p; evt[j]=tt; conf[j]=p
            if direction[j]<=0:
                if p<lo[j]: lo[j]=p
                if p-lo[j]>=th:
                    direction[j]=1; hi[j]=p; evt[j]=tt; conf[j]=p
        if k<n and i==ev_i[k]:
            for j in range(m):
                pol[k,j]=direction[j]*ev_side[k]; age[k,j]=(tt-evt[j])/1000.0
                if direction[j]>0: ovs=p-conf[j]
                elif direction[j]<0: ovs=conf[j]-p
                else: ovs=0.
                osx[k,j]=ovs/ths[j]; rate[k,j]=1.0/(age[k,j]+1.0)
            k+=1
            if k>=n: break
    return pol,age,osx,rate

def build_month(month):
    outp=f'{OUT}/events_{month:02d}.parquet'; sump=f'{OUT}/summary_{month:02d}.json'
    if os.path.exists(outp) and os.path.exists(sump): print('EXISTS',month,flush=True); return
    t,mid,av,bv=load_ticks(month); print('loaded',month,len(t),flush=True)
    sec_ids,o,h,l,c,n,am,bm=aggregate_active_seconds(t,mid,av,bv)
    s1_disp,s1_eff,s1_rng,s1_turns,tickratio,volimb=build_s1(sec_ids,o,h,l,c,n,am,bm)
    atrsec,_=build_m5_atr_by_sec(sec_ids,t,mid)
    ev_i,ev_si,side,rearm,pnl,hold,mfe,mae=r9_baseline_events(t,mid,sec_ids,s1_disp,s1_eff,s1_rng,s1_turns,atrsec)
    good=np.isfinite(pnl); ev_i=ev_i[good]; ev_si=ev_si[good]; side=side[good]; rearm=rearm[good]; pnl=pnl[good]; hold=hold[good]; mfe=mfe[good]; mae=mae[good]
    cf=counterfactuals(t,mid,ev_i,side)
    data={'month':np.full(len(ev_i),month,np.int16),'time_ms':t[ev_i],'side':side,'rearm':rearm,'base_pnl':pnl,'base_hold':hold,'base_mfe':mfe,'base_mae':mae,
          's1_disp_al':s1_disp[ev_si]*side,'s1_eff':s1_eff[ev_si],'s1_range':s1_rng[ev_si],'s1_turns':s1_turns[ev_si],
          's1_tickratio':tickratio[ev_si],'s1_volimb_al':volimb[ev_si],'atr_m5':atrsec[ev_si]}
    data.update(recent_second_features(ev_si,side,sec_ids,o,h,l,c,n,am,bm))
    data.update(event_multiscale_features(t[ev_i],side,t,mid))
    ths=np.array([.15,.30,.50,1.00],np.float64); pol,age,ovs,rate=dc_features_at_events(t,mid,ev_i,side,ths)
    for j,th in enumerate(ths):
        tag=str(th).replace('.','p'); data[f'dc{tag}_pol_al']=pol[:,j]; data[f'dc{tag}_age']=age[:,j]; data[f'dc{tag}_overshoot']=ovs[:,j]; data[f'dc{tag}_fresh']=rate[:,j]
    names=['cont_r9','fade_r9','cont_harv','fade_harv']
    for j,name in enumerate(names):
        data[name+'_pnl']=cf[:,j*3]; data[name+'_mfe']=cf[:,j*3+1]; data[name+'_mae']=cf[:,j*3+2]
    pd.DataFrame(data).to_parquet(outp,index=False)
    gp=pnl[pnl>0].sum(); gl=pnl[pnl<0].sum()
    sm={'month':month,'ticks':int(len(t)),'trades':int(len(pnl)),'net':float(pnl.sum()),'gp':float(gp),'gl':float(gl),'pf':float(gp/(-gl)),'win':float((pnl>0).mean()),'avg_hold':float(hold.mean())}
    with open(sump,'w') as f: json.dump(sm,f,indent=2)
    print('SUMMARY',sm,flush=True)

if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('--month',type=int); a=ap.parse_args()
    if a.month: build_month(a.month)
    else:
        for m in range(1,8): build_month(m)
