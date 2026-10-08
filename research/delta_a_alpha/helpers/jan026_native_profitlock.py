#!/usr/bin/env python3
"""Jan-024 end-to-end *reconstructed* V1-L0..L8 research prototype, NOT exact legacy 131E parity.

INPUT: exact ordered Jan 2026 Dukascopy raw Bid/Ask ticks (integer price *1000).
Source historical mechanisms: hourly 019, Jan 131D session-specific native cells,
119/131E earned Watchdog child renewals.  Standalone engine differs from the
original legacy funding-parent and supplemental coverage V3 implementation.
Outputs are valid for THIS explicitly disclosed implementation, not as rerun of
original Gamma 131E. Forecaster uses completed M5 only; never future P/L.
"""
import os,json,hashlib,time,sys
from pathlib import Path
from collections import defaultdict
from datetime import datetime,timezone
import numpy as np,pandas as pd
from numba import njit

BASE=Path('/mnt/data/daa_january_full_execution_026');BASE.mkdir(exist_ok=True)
ROOT=Path('/mnt/data/XAUUSD_DUKAS_2026_01_ticks.csv(3).gz')
EXPECTED='d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5'
DAY=86400000
# Original 019 selected London long HTF cells in completed timeframes.
@njit
def london_hold(hr,h4,h1,m15,m5):
    if h4!=1 or h1!=1:return 0
    if hr==7 and m15==-1 and m5==-1:return 1800000
    if hr==8:
        if m15==-1 and m5==-1:return 300000
        if m15==-1 and m5==1:return 900000
    if hr==9 and ((m15==-1 and m5==-1) or (m15==1 and m5==-1)):return 1800000
    if hr==11:
        if m15==-1 and m5==-1:return 1800000
        if m15==-1 and m5==1:return 1800000
        if m15==1 and m5==-1:return 900000
    if hr==12:
        if m15==-1 and m5==-1:return 1800000
        if m15==-1 and m5==1:return 900000
        if m15==1 and m5==-1:return 1800000
    if hr==13 and (m15==-1 or (m15==1 and m5==-1)):return 1800000
    if hr==14:
        if m15==-1 and m5==-1:return 1800000
        if m15==-1 and m5==1:return 900000
    if hr==15 and (m15!=0 and m5!=0 and (m15==1 or m5==1)):return 1800000
    return 0

@njit
def ny_dir(hr,h4,h1,m15,m5):
    if hr==16:
        if h4==-1 and h1==-1 and m15==-1 and m5==-1:return -1
        if h4==1 and h1==1 and ((m15==1 and m5==-1) or (m15==-1 and m5==1)):return 1
    if hr==17:
        if h4==-1 and h1==-1 and m15==-1 and m5==-1:return -1
        if h4==1 and h1==1 and m15==-1 and m5==-1:return 1
    if hr==18 and h4==-1 and h1==-1 and m15==-1 and m5==-1:return -1
    return 0

@njit
def run(t,a,b,h4,h1,m15,m5,m5_range,m5_start,m5_end,adaptive,cap,coverage_selected=1,spread_cap_raw=1300, trail_trigger_raw=0, trail_retrace_raw=0, trail_source=6):
    """All entries/exits and floating marks at actual quote tick. cap is GLOBAL across layers.
    One first funded order maximum per market tick. No re-use of shadow profits.
    original renewal effective q at NY bin5=1.10 vs other bins1.19;
    bounded deployment heat and finite lifecycle; risk limits are prototype not 131E.
    """
    n=len(t); MAX=cap
    active=np.zeros(MAX,np.uint8); typ=np.zeros(MAX,np.int8);dire=np.zeros(MAX,np.int8)
    ep=np.zeros(MAX,np.int32); eidx=np.zeros(MAX,np.int64); end=np.zeros(MAX,np.int64)
    best_favorable=np.zeros(MAX,np.int32); lock_exits=0
    target=np.zeros(MAX,np.int32);stop=np.zeros(MAX,np.int32);cid=np.zeros(MAX,np.int16)
    # ledger up to 1m tickets
    LIM=1300000; LE=np.empty(LIM,np.int64);LX=np.empty(LIM,np.int64);LP=np.empty(LIM,np.float64)
    LT=np.empty(LIM,np.int8);LD=np.empty(LIM,np.int8); LR=np.empty(LIM,np.int8)
    LW=np.empty(LIM,np.int16); LLC=np.empty(LIM,np.int32)
    k=0;opened=0; maxopen=0; skips=np.zeros(8,np.int64);attempt=np.zeros(8,np.int64)
    m1=-1; anchor=0; highstep=0; lowstep=0
    last_highvol=np.full(24,np.int64(-999999999999999),dtype=np.int64)
    last_allowed=np.zeros(24,np.int8)
    current_day=-1; ncell=6*243
    prior_cell=np.zeros(ncell,np.uint8);streak=np.zeros(ncell,np.int16);wd_until=np.zeros(ncell,np.int64)
    wd_closed=np.ones(ncell,np.uint8);wd_next=np.zeros(ncell,np.int64)
    wd_active=np.zeros(ncell,np.uint8);wd_parent_exit=np.zeros(ncell,np.int64)
    # distinct relative campaigns; close-existing-order on this tick before reentry.
    spent_tick=-1; bal=0.;peakbal=0.;balance_dd=0.;peakeq=100000.;equity_dd=0.;min_eq=100000.
    max_heat=0.; max_spread=0.; last_m5=-1; eligible5=0; first_entry=-1; first_eligible=-1
    costs=0.02
    # Original source starts 2026-01-01 23h UTC; prevent opening before 144 completed bars if no external prev history
    for i in range(n):
        ti=t[i];ask=int(a[i]);bid=int(b[i]);spread=ask-bid;mid=(ask+bid)//2
        if spread>max_spread:max_spread=spread
        # Up to 128 current positions per tick exact first-touch mark, not balance-only accounting.
        floating=0.
        for j in range(MAX):
            if active[j]==0:continue
            dd=int(dire[j]);ex=bid if dd>0 else ask
            exit_code=0
            fav=dd*(ex-int(ep[j]));
            if fav>best_favorable[j]:best_favorable[j]=fav
            if target[j]>0 and ((dd>0 and ex>=target[j]) or (dd<0 and ex<=target[j])):exit_code=1
            elif trail_trigger_raw>0 and typ[j]==trail_source and best_favorable[j]>=trail_trigger_raw and fav<=best_favorable[j]-trail_retrace_raw:exit_code=5
            elif stop[j]>0 and ((dd>0 and ex<=stop[j]) or (dd<0 and ex>=stop[j])):exit_code=2
            elif ti>=end[j]:exit_code=3
            if exit_code:
                prof=dd*(ex-int(ep[j]))/1000.-costs
                if k<LIM:
                    LE[k]=int(eidx[j]);LX[k]=i;LP[k]=prof;LT[k]=typ[j];LD[k]=dd;LR[k]=exit_code
                    LW[k]=int(cid[j]);LLC[k]=int(ep[j]);k+=1
                bal+=prof;active[j]=0;opened-=1
                if exit_code==5:lock_exits+=1
                # Watchdog transition based strictly on CLOSED FUNDED child.
                if typ[j]==5:
                    c=int(cid[j]);good=(prof>0 and ti-t[int(eidx[j])]<=60000)
                    streak[c]=min(32000,streak[c]+1) if good else 0
                    wd_closed[c]=1;wd_next[c]=ti
                # Bounded wrong-direction recovery opportunity from actually funded failed native/hourly order.
                # We log loss marker; independent recovery admission is handled on a subsequent tick.
                # Recovery is deliberately observe-only until original 131D causal activation is proven.
                # No naked loss-triggered reversal is allowed as a substitute for the V1 L7 contract.
            else:
                floating+=dd*(ex-int(ep[j]))/1000.-costs/2
        if bal>peakbal:peakbal=bal
        if peakbal-bal>balance_dd:balance_dd=peakbal-bal
        tot=100000.+bal+floating
        if tot>peakeq:peakeq=tot
        if peakeq-tot>equity_dd:equity_dd=peakeq-tot
        if tot<min_eq:min_eq=tot
        if -floating>max_heat:max_heat=-floating
        if opened>maxopen:maxopen=opened
        if first_eligible<0 and h4[i]!=0 and h1[i]!=0 and m15[i]!=0 and m5[i]!=0:first_eligible=i
        # Current tick contains no incomplete M5 future bar, market supply from completed bars only.
        mb=ti//300000
        if mb!=last_m5:
            last_m5=mb
            eligible5=0
            if i>0:
                x=np.searchsorted(m5_start,mb,side='left')-1
                if x>=143:
                    z=m5_range[x-143:x+1];r12=z[-12:];r48=z[-48:]
                    # only completed bars, no month number or hindsight class
                    eligible5=1 if (np.sum(r12>=10000)>=3 and np.sum(r48>=10000)>=8) else 0
        # intrinsic current-quote risk and margin proxy: cap, spread and floating heat. No broker certification.
        # Gate only renewal children: keep initial scouts available to preserve low-activity trade velocity.
        renew_ok=(not adaptive) or (spread<=spread_cap_raw and eligible5==1)
        hour=int((ti//3600000)%24); msec=int((ti//60000)%60);b10=msec//10
        day=ti//DAY
        if day!=current_day:
            prior_cell[:]=0;streak[:]=0;wd_until[:]=0;wd_closed[:]=1;wd_active[:]=0
            current_day=day
        minute=ti//60000
        if minute!=m1:
            m1=minute;anchor=mid;highstep=0;lowstep=0
        # 10 minute cell key from completed HTF signature + direction code
        code=int((h4[i]+1)*81+(h1[i]+1)*27+(m15[i]+1)*9+(m5[i]+1)*3+2)
        cell=b10*243+code
        # Candidate generation is priority based on session-specific original 019 layers:
        src=-1;dr=0;tp=0;sl=0;life=0
        # WATCHDOG renewal: a consecutive family of funded children per active parent campaign;
        # original 131E parent funding comes from profit-funded 049 stream; this prototype uses the causal
        # 17 UTC heartbeat in the same structural condition, so parity to 131E IS NOT CLAIMED.
        if wd_active[cell] and ti>=wd_until[cell]:wd_active[cell]=0
        if hour==17 and ny_dir(hour,h4[i],h1[i],m15[i],m5[i])!=0 and wd_active[cell] and wd_closed[cell] and ti>wd_next[cell] and renew_ok:
            src=5;dr=ny_dir(hour,h4[i],h1[i],m15[i],m5[i]);tp=1100 if b10==5 else 1190;sl=0;life=max(1,int(wd_until[cell]-ti))
        # first-parent scout based on an actual entry-known heartbeat, no prior funded wins required
        if src<0 and hour==17 and ny_dir(hour,h4[i],h1[i],m15[i],m5[i])!=0 and wd_active[cell]==0:
            if prior_cell[cell]==0:
                src=5;dr=ny_dir(hour,h4[i],h1[i],m15[i],m5[i]);tp=1100 if b10==5 else 1190;sl=0;life=1800000
                prior_cell[cell]=1;wd_active[cell]=1;wd_until[cell]=ti+life
        # NEW HIGHVOLUME hourly route candidates, separate from WD. Preserve original minute anchor and 019 direction
        if src<0 and 7<=hour<=18:
            d=0;life2=0;tp2=0;sl2=0;ok=0
            if hour<=15:
                life2=london_hold(hour,h4[i],h1[i],m15[i],m5[i]);d=1
                thr=1000 if hour==7 else (3000 if hour==8 else (2000 if hour==11 else (4000 if hour in (13,14) else 0)))
                if life2>0 and mid-anchor>=thr:ok=1
            else:
                d=ny_dir(hour,h4[i],h1[i],m15[i],m5[i])
                if d!=0:
                    disp=(mid-anchor)*d
                    if hour==16 and disp>=500:
                        ok=1;life2=1200000;tp2=40000;sl2=40000
                    if hour==17 and disp>=8000:
                        ok=1;life2=1800000;tp2=80000;sl2=40000
                    if hour==18 and disp>=500:
                        ok=1;life2=60000;tp2=12000;sl2=8000
            if ok and coverage_selected:
                # January 131D + recovered coverage V3 source-specific admission cells.
                m15s=int(m15[i]);m5s=int(m5[i]);h4s=int(h4[i]);h1s=int(h1[i]);
                # raw quote ticks in trailing minute, observed-only
                allow=False
                if hour==9 and b10==0 and h4s==1 and h1s==1 and m15s==1 and m5s==-1:allow=True
                if hour==11 and b10 in (2,3) and h4s==1 and h1s==1 and m15s==-1 and m5s==-1:allow=True
                if hour==11 and b10==3 and h4s==1 and h1s==1 and m15s==1 and m5s==-1:allow=True
                if hour==12 and b10 in (0,1,2) and h4s==1 and h1s==1 and m15s==-1 and m5s==-1:allow=True
                if hour==13 and b10 in (2,3) and h4s==1 and h1s==1 and m15s==-1 and m5s==-1:allow=True
                if hour==14 and b10==3 and h4s==1 and h1s==1 and m15s==-1 and m5s==1:allow=True
                if hour==15 and b10 in (2,3) and h4s==1 and h1s==1 and m15s==1 and m5s==1:allow=True
                if hour==16 and b10 in (0,3,4) and h4s==1 and h1s==1 and m15s==1 and m5s==-1:allow=True
                ok=1 if allow else 0
            if ok:
                if last_allowed[hour]==0 or ti-last_highvol[hour]>=250:
                    last_highvol[hour]=ti;last_allowed[hour]=1
                    src=2;dr=d;tp=tp2;sl=sl2;life=life2
            else:last_allowed[hour]=0
        # January 131D named session specialists, true independent L4 Asia and L6 native route.
        # Source 131D matching completed H4/H1/M15/M5 without month switching, per-minute range ladder.
        if src<0 and (hour==2 or hour==10 or hour==13 or hour==21):
            step=50
            ddir=0
            if mid-anchor>=highstep+step:
                highstep=((mid-anchor)//step)*step;ddir=1
            elif anchor-mid>=lowstep+step:
                lowstep=((anchor-mid)//step)*step;ddir=-1
            if ddir:
                if hour==2 and h4[i]==1 and h1[i]==1 and m15[i]==-1 and m5[i]==-1 and ddir==1:
                    src=4;dr=1;tp=12000;sl=4000;life=300000
                elif hour==10 and h4[i]==1 and h1[i]==-1 and m15[i]==-1 and m5[i]==-1 and ddir==1:
                    src=6;dr=1;tp=0;sl=0;life=120000
                elif hour==13 and h4[i]==1 and h1[i]==-1 and m15[i]==1 and m5[i]==-1 and ddir==-1:
                    src=6;dr=-1;tp=12000;sl=4000;life=300000
                elif hour==21 and h4[i]==1 and h1[i]==-1 and m15[i]==-1 and m5[i]==-1 and ddir==1:
                    src=6;dr=1;tp=0;sl=0;life=120000
        # Funded only, one physical order per observed tick. Mild physically executed recovery
        # (if no integrated source rule validated: stays shadow to avoid adding unproved alpha).
        if src<0:continue
        attempt[src]+=1
        if opened>=MAX:
            skips[src]+=1;continue
        # quote spread is not a forced full-system off gate: only adaptive children.
        if src==5 and adaptive and not renew_ok:
            skips[src]+=1;continue
        j=-1
        for s in range(MAX):
            if active[s]==0:j=s;break
        if j<0:skips[src]+=1;continue
        active[j]=1;typ[j]=src;dire[j]=dr;ep[j]=ask if dr>0 else bid;eidx[j]=i;best_favorable[j]=0
        target[j]=ep[j]+dr*tp if tp>0 else 0
        stop[j]=ep[j]-dr*sl if sl>0 else 0
        end[j]=ti+life;cid[j]=cell if src==5 else 0
        if src==5:wd_closed[cell]=0
        opened+=1
        if opened>maxopen:maxopen=opened
        if first_entry<0:first_entry=i
    # Close remaining opens, source raw quote at last tick.
    j=n-1
    for s in range(MAX):
        if active[s]:
            ex=int(b[-1] if dire[s]>0 else a[-1]);prof=int(dire[s])*(ex-int(ep[s]))/1000.-costs
            if k<LIM:
                LE[k]=eidx[s];LX[k]=j;LP[k]=prof;LT[k]=typ[s];LD[k]=dire[s];LR[k]=4;LW[k]=cid[s];LLC[k]=ep[s];k+=1
            bal+=prof
    return (LE[:k],LX[:k],LP[:k],LT[:k],LD[:k],LR[:k],LW[:k],LLC[:k],attempt,skips,
            maxopen,balance_dd,equity_dd,min_eq,max_heat,first_entry,first_eligible,lock_exits)


def completed_tf_state(t,b,tf_ms):
    key=t//tf_ms;starts=np.r_[0,np.flatnonzero(key[1:]!=key[:-1])+1];end=np.r_[starts[1:]-1,len(t)-1];close=b[end].astype(np.float64)
    e8=np.empty(len(end));e21=np.empty(len(end));e8[0]=close[0];e21[0]=close[0]
    for i in range(1,len(end)):
        e8[i]=e8[i-1]+(2/9)*(close[i]-e8[i-1]);e21[i]=e21[i-1]+(2/22)*(close[i]-e21[i-1])
    st=np.sign(e8-e21).astype(np.int8);ix=np.searchsorted(key[starts],key,side='left')-1
    out=np.zeros(len(t),np.int8);good=ix>=0;out[good]=st[ix[good]]
    return out


def m5_completed(t,a,b):
    key=t//300000;starts=np.r_[0,np.flatnonzero(key[1:]!=key[:-1])+1];ends=np.r_[starts[1:]-1,len(t)-1]
    # vectorized extrema via reduceat. M5 range in USD raw quote mid center to avoid spread noise.
    mid=(a.astype(np.int64)+b.astype(np.int64))//2
    hi=np.maximum.reduceat(mid,starts);lo=np.minimum.reduceat(mid,starts)
    return (key[starts],starts,ends,(hi-lo).astype(np.int32))


def summarize(entries,exits,pnl,typ,t,stats,dirs,raw_entry,reason,ask_quotes,bid_quotes):
    actual_time=t[exits]; order=np.argsort(actual_time,kind='stable'); p=pnl[order];ii=exits[order]
    bal=np.cumsum(p);bpeak=np.maximum.accumulate(np.r_[0.,bal[:-1]]); dd=float(np.max(bpeak-bal)) if len(p) else 0.
    gp=float(p[p>0].sum());gl=float(p[p<=0].sum())
    quote_exit=np.where(dirs>0,bid_quotes[exits],ask_quotes[exits])
    quote_entry=np.where(dirs>0,ask_quotes[entries],bid_quotes[entries])
    recon=(quote_exit-raw_entry)*dirs/1000.-0.02
    err=np.max(np.abs(recon-pnl)) if len(pnl) else 0.
    assert err<1e-9, f'raw executable quote parity failure {err}'
    assert np.array_equal(quote_entry,raw_entry), 'entry not actual bid/ask'
    assert np.all(exits>=entries), 'forward first-touch chronology'
    assert np.unique(entries).size==len(entries), 'more than one physical entry on same tick'
    base={'raw_quote_pnl_parity_max_abs':float(err),'unique_entry_ticks':int(np.unique(entries).size),'trades':int(len(p)),'net':float(p.sum()),'gross_profit':gp,'gross_loss':gl,'profit_factor':gp/-gl if gl<0 else None,'win_rate':float((p>0).mean()) if len(p) else None,'expectancy':float(p.mean()) if len(p) else None,'balance_drawdown_exact':dd,'full_tick_equity_dd':float(stats[12]),'min_total_equity':float(stats[13]),'max_open':int(stats[10]),'max_unrealized_heat':float(stats[14]),'sources':{}}
    tns= pd.to_datetime(t[exits],unit='ms',utc=True)
    rec=pd.DataFrame({'entry_idx':entries,'exit_idx':exits,'entry_ms':t[entries],'exit_ms':t[exits],'entry_quote_raw':raw_entry,'exit_quote_raw':quote_exit,'direction':dirs,'exit_reason':reason,'net':pnl,'source':typ,'day':tns.strftime('%Y-%m-%d'),'week':tns.strftime('%G-W%V')})
    for src in sorted(rec.source.unique()):
        q=rec.loc[rec.source==src,'net'].values;g=float(q[q>0].sum());l=float(q[q<=0].sum());base['sources'][str(src)]={'trades':len(q),'net':float(q.sum()),'gross_loss':l,'pf':g/-l if l<0 else None}
    def score(df):
        q=df.net.to_numpy();pos=q[q>0].sum();neg=q[q<=0].sum();return pd.Series({'trades':len(q),'net':q.sum(),'gross_profit':pos,'gross_loss':neg,'profit_factor':pos/-neg if neg<0 else np.nan,'win_rate':(q>0).mean(),'expectancy':q.mean()})
    daily=rec.groupby('day',sort=True).apply(score,include_groups=False).reset_index()
    weekly=rec.groupby('week',sort=True).apply(score,include_groups=False).reset_index()
    return base,rec,daily,weekly


def main():
    import argparse
    ap=argparse.ArgumentParser();ap.add_argument('--variants',choices=['both','baseline','aware'],default='both');ap.add_argument('--cap',type=int,default=64);ap.add_argument('--coverage',choices=['broad','selected'],default='selected');ap.add_argument('--trail-trigger',type=int,default=0);ap.add_argument('--trail-retrace',type=int,default=0);ap.add_argument('--trail-source',type=int,default=6);args=ap.parse_args()
    sha=hashlib.file_digest(open(ROOT,'rb'),'sha256').hexdigest();assert sha==EXPECTED,(sha,EXPECTED)
    df=pd.read_csv(ROOT,compression='gzip',usecols=['timestamp_ms_utc','ask_raw','bid_raw'],dtype={'timestamp_ms_utc':'i8','ask_raw':'i4','bid_raw':'i4'})
    t=df.timestamp_ms_utc.to_numpy();a=df.ask_raw.to_numpy();b=df.bid_raw.to_numpy();del df
    assert np.all(np.diff(t)>=0) and np.all(a>=b)
    print(json.dumps({'checkpoint':'source_loaded','ticks':len(t),'sha256':sha}),flush=True)
    states=[completed_tf_state(t,b,k) for k in (14400000,3600000,900000,300000)];print('states_completed',flush=True)
    key,starts,ends,rng=m5_completed(t,a,b);print('m5_complete',len(rng),flush=True)
    for tag,active in [('profitlock',0)]:
        if args.variants not in (tag,'both'):continue
        print('begin_variant',tag,flush=True)
        start=time.monotonic();res=run(t,a,b,*states,rng,key,ends,active,args.cap,1 if args.coverage=='selected' else 0,1300,args.trail_trigger,args.trail_retrace,args.trail_source)
        entry,exit,pnl,source,dire,reason,wdcell,raw,attempt,skips,*rest=res
        score,rec,daily,weekly=summarize(entry,exit,pnl,source,t,res,dire,raw,reason,a,b)
        score.update({'profit_lock_exits':int(rest[7]),'trail_trigger_raw':args.trail_trigger,'trail_retrace_raw':args.trail_retrace,'trail_source':args.trail_source,'variant':tag,'cap':args.cap,'coverage':args.coverage,'seconds':time.monotonic()-start,'assumptions':'reconstructed non-parity prototype, $0.02/trade plus actual quote spread; no Coinexx execution or margin','attempt_by_src':attempt.tolist(),'skip_by_src':skips.tolist(),'first_entry_utc':datetime.fromtimestamp(t[rest[5]]/1000,timezone.utc).isoformat() if rest[5]>=0 else None,'first_htf_eligible_utc':datetime.fromtimestamp(t[rest[6]]/1000,timezone.utc).isoformat() if rest[6]>=0 else None,'source_sha256':sha})
        rec.to_csv(BASE/f'{tag}_cap{args.cap}_T{args.trail_trigger}_R{args.trail_retrace}_S{args.trail_source}_trades.csv',index=False)
        daily.to_csv(BASE/f'{tag}_cap{args.cap}_T{args.trail_trigger}_R{args.trail_retrace}_S{args.trail_source}_daily.csv',index=False);weekly.to_csv(BASE/f'{tag}_cap{args.cap}_T{args.trail_trigger}_R{args.trail_retrace}_S{args.trail_source}_weekly.csv',index=False)
        (BASE/f'{tag}_cap{args.cap}_T{args.trail_trigger}_R{args.trail_retrace}_S{args.trail_source}_score.json').write_text(json.dumps(score,indent=2))
        print(json.dumps({'checkpoint':tag+'_complete','metrics':score}),flush=True)
    print(json.dumps({'status':'atomic_replay_completed'}),flush=True)

if __name__=='__main__':main()