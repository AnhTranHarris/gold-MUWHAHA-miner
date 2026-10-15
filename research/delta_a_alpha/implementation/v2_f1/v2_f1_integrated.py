"""V2 F1 integrated microgrid research chassis — January 2026 XAUUSD.
Rebuilt engine, NOT a V1 deployment or an MT5 certified clone.
L0 raw ordered Bid/Ask; L1 geographic sessions; L2 completed M1/M5/H1/H4;
L3 concurrent virtual structural sources; L4 fast quote/market regime arbitration;
L5 trend/continuation and re-entry gate; L6 stop/trail, no martingale;
L7 one physical 0.01-lot assumed 1oz, 1:500 research-funded account.
Original MQL5 R9 minute bracket inspiration; neither SYNTH generated ticks nor
hindsight teacher labels enter executable decisions. Full real tick execution.
Original V1 remains intact and unchanged. Strict January-only training/evaluation.
"""
from __future__ import annotations
import argparse,hashlib,json,time
from pathlib import Path
from datetime import timezone
import numpy as np,pandas as pd
from numba import njit

RAW=Path('/mnt/data/XAUUSD_DUKAS_2026_01_ticks.csv(3).gz')
PIN='d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5'
OUT=Path(__file__).parent
R9_MONTH={'net':41520.82,'trades':27980,'gross_loss':1827.87,'active_hours':480,'positive_active_hours':480,'active_days':21}
# Bit-coded virtual sources and regimes; all sources share L7. Source count is not physical position count.
SRC=('R9_MINUTE_BRACKET','MICRO_CONTINUATION','MICRO_REVERSAL','M1_RECLAIM','M5_PULLBACK','RANGE_ROTATION','ACTIVITY_EXPANSION','MULTISCALE_BREAKOUT')
REG=('ALL','M5_ACTIVE','H1_TREND','M5_H1_ALIGNED','M5_H1_OPPOSED','M5_LOWVOL','M5_HIGHVOL','M5_EXPANDING')

@njit(cache=True)
def prev_frames(ts,op,hi,lo,cl,width,atr_period=14):
    """As-of LAST COMPLETED bars only; no current full candle leakage."""
    n=len(ts); start=np.empty(n,np.int64); high=np.empty(n,np.float64);low=np.empty(n,np.float64);close=np.empty(n,np.float64);open_=np.empty(n,np.float64)
    count=0
    for i in range(n):
        if i==0 or ts[i]//width != ts[i-1]//width:
            start[count]=i;count+=1
    start=start[:count];h=np.empty(count);l=np.empty(count);c=np.empty(count);o=np.empty(count);atr=np.empty(count)
    atr[:]=np.nan
    for j in range(count):
        a=start[j];b=start[j+1] if j+1<count else n
        hh=-1e20;ll=1e20
        for k in range(a,b):
            if hi[k]>hh:hh=hi[k]
            if lo[k]<ll:ll=lo[k]
        h[j]=hh;l[j]=ll;o[j]=op[a];c[j]=cl[b-1]
    # Wilder ATR; width-dependent true-range, as-of completed bar.
    if count>atr_period:
        z=0.
        for j in range(1,atr_period+1):
            z+=max(h[j]-l[j],abs(h[j]-c[j-1]),abs(l[j]-c[j-1]))
        z/=atr_period;atr[atr_period]=z
        for j in range(atr_period+1,count):
            tr=max(h[j]-l[j],abs(h[j]-c[j-1]),abs(l[j]-c[j-1]))
            z=(z*(atr_period-1)+tr)/atr_period;atr[j]=z
    ptr=0
    for i in range(n):
        while ptr+1<count and start[ptr+1]<=i:ptr+=1
        k=ptr-1
        if k>=0:
            high[i]=h[k];low[i]=l[k];close[i]=c[k];open_[i]=o[k]
        else:
            high[i]=np.nan;low[i]=np.nan;close[i]=np.nan;open_[i]=np.nan
    outatr=np.empty(n);outatr[:]=np.nan
    ptr=0
    for i in range(n):
        while ptr+1<count and start[ptr+1]<=i:ptr+=1
        if ptr>=1:outatr[i]=atr[ptr-1]
    return open_,high,low,close,outatr

@njit(cache=True)
def micro_features(ts,open_,hi,lo,cl,upd):
    n=len(ts);quality=np.zeros(n,np.int8);impulse=np.zeros(n,np.float64);eff=np.zeros(n,np.float64);turns=np.zeros(n,np.int16)
    acceleration=np.zeros(n,np.float64);r20=np.zeros(n,np.float64)
    # Index i feature uses seconds [i-10, i-1]; never current-second closure.
    for i in range(24,n):
        if ts[i]-ts[i-10]>22:continue
        d=cl[i-1]-cl[i-10];travel=1e-9;sg0=0;nt=0
        hh=-1e20;ll=1e20;fast=0;slow=0
        for j in range(i-9,i):
            x=cl[j]-cl[j-1];travel+=abs(x)
            sg=1 if x>0 else (-1 if x<0 else 0)
            if sg and sg0 and sg!=sg0:nt+=1
            if sg:sg0=sg
        for j in range(i-10,i):
            if hi[j]>hh:hh=hi[j]
            if lo[j]<ll:ll=lo[j]
            if j>=i-5:fast+=upd[j]
            slow+=upd[j]
        e=abs(d)/travel
        impulse[i]=d;eff[i]=e;turns[i]=nt;r20[i]=hh-ll
        acceleration[i]=fast/(slow*.5+1e-9)
        if e>=.70 and nt<=9 and hh-ll>=.50:
            if d>=.15:quality[i]=1
            if d<=-.15:quality[i]=-1
    return quality,impulse,eff,turns,acceleration,r20

def load_source():
    t0=time.time();sha=hashlib.file_digest(RAW.open('rb'),'sha256').hexdigest()
    if sha!=PIN:raise RuntimeError('Input January source SHA changed')
    d=pd.read_csv(RAW,compression='gzip',usecols=['timestamp_ms_utc','bid_raw','ask_raw'],dtype={'timestamp_ms_utc':'int64','bid_raw':'int32','ask_raw':'int32'})
    ms=d.timestamp_ms_utc.to_numpy();bid=d.bid_raw.to_numpy();ask=d.ask_raw.to_numpy();del d
    if not np.all(ms[1:]>=ms[:-1]) or np.any(ask<bid):raise AssertionError('tick ordering or crossed quotes')
    seconds=ms//1000;ix=np.r_[0,np.flatnonzero(seconds[1:]!=seconds[:-1])+1];n=len(ix);ts=seconds[ix]
    ends=np.r_[ix[1:]-1,len(ms)-1]
    op=bid[ix].astype(np.float64)*.001;cl=bid[ends].astype(np.float64)*.001
    hi=np.maximum.reduceat(bid,ix).astype(np.float64)*.001
    lo=np.minimum.reduceat(bid,ix).astype(np.float64)*.001
    upd=np.diff(np.r_[ix,len(ms)]).astype(np.int32)
    f1=prev_frames(ts,op,hi,lo,cl,60);f5=prev_frames(ts,op,hi,lo,cl,300)
    f15=prev_frames(ts,op,hi,lo,cl,900);f1h=prev_frames(ts,op,hi,lo,cl,3600);f4h=prev_frames(ts,op,hi,lo,cl,14400)
    qua,imp,eff,turn,acc,span=micro_features(ts,op,hi,lo,cl,upd)
    # First observed tick of each minute establishes bracket; same for original R9 logic.
    firstmin=np.r_[0,np.flatnonzero(ts[1:]//60!=ts[:-1]//60)+1]
    mn_mid=((ask[ix[firstmin]].astype(float)+bid[ix[firstmin]].astype(float))*.0005)
    midanchor=mn_mid[np.searchsorted(firstmin,np.arange(n),side='right')-1]
    # As-of last completed M1, M5, H1 and H4 signals. No market period flags learned from R9.
    m5dir=np.sign(np.nan_to_num(f5[3]-f5[0],nan=0.)).astype(np.int8)
    h1dir=np.sign(np.nan_to_num(f1h[3]-f1h[0],nan=0.)).astype(np.int8)
    h4dir=np.sign(np.nan_to_num(f4h[3]-f4h[0],nan=0.)).astype(np.int8)
    m15dir=np.sign(np.nan_to_num(f15[3]-f15[0],nan=0.)).astype(np.int8)
    # Jan 2026 local sessions, calendar obtained using IANA zones, no broker UTC assumption.
    z=pd.to_datetime(ts,unit='s',utc=True)
    def win(zone,st,en):
        q=z.tz_convert(zone);hr=q.hour.to_numpy();minute=q.minute.to_numpy();weekday=q.dayofweek.to_numpy()
        return ((hr*60+minute>=st)&(hr*60+minute<en)&(weekday<5))
    sess=(win('Australia/Sydney',480,1020).astype(np.uint8)
       +2*win('Asia/Tokyo',540,1080).astype(np.uint8)
       +4*win('Europe/London',480,1020).astype(np.uint8)
       +8*win('America/New_York',480,1020).astype(np.uint8)).astype(np.uint8)
    print('PRECOMPUTE',json.dumps({'ticks':len(ms),'observed_seconds':n,'seconds_span':int(ts[-1]-ts[0]),'median_raw_spread':float(np.median((ask-bid)*.001)),'sec':round(time.time()-t0,1)}),flush=True)
    return dict(ms=ms,bid=bid,ask=ask,ix=ix,ts=ts,qua=qua,imp=imp,eff=eff,acc=acc,span=span,upds=upd,midanchor=midanchor,
       m1o=f1[0],m1h=f1[1],m1l=f1[2],m1c=f1[3],m5o=f5[0],m5h=f5[1],m5l=f5[2],m5c=f5[3],atr5=f5[4],
       h1o=f1h[0],h1h=f1h[1],h1l=f1h[2],h1c=f1h[3],h4o=f4h[0],h4h=f4h[1],h4l=f4h[2],h4c=f4h[3],sess=sess,
       m5dir=m5dir,h1dir=h1dir,h4dir=h4dir,m15dir=m15dir)

@njit(cache=True)
def generate_sources(ts,cl,qua,imp,eff,acc,span,m1h,m1l,m1c,m5c,h1h,h1l,h1c,m5dir,h1dir,h4dir,m15dir,atr5):
    """Virtual sources: decisions only from previously completed bars/observed seconds.
       Bracket candidate is handled at tick-time with frozen current M1 open.
    """
    n=len(ts);sig=np.zeros((8,n),np.int8)
    for i in range(25,n):
        if not np.isfinite(atr5[i]) or not np.isfinite(h1c[i]):continue
        q=qua[i]; d=imp[i];e=eff[i];a=acc[i];span_=span[i];a5=atr5[i]
        if q!=0:
            # src 0 at actual bracket cross only
            if q==m5dir[i] and (q==h1dir[i] or h1dir[i]==0) and a>.80:sig[1,i]=q
            if q!=m5dir[i] and e>.78 and span_>=1.2:sig[2,i]=q
            if (q==m5dir[i] and q==h1dir[i] and a>1.15 and a5>2.0):sig[6,i]=q
            if q==h1dir[i] and q==h4dir[i] and q==m15dir[i] and a5>=3.5 and span_>=1.5:sig[7,i]=q
        # M1 reclaim of last finished M1 boundary after a reversal from recently moved quotes
        if np.isfinite(m1h[i]) and np.isfinite(m1l[i]):
            recent=cl[i-1];prev=cl[i-2];swing=cl[i-1]-cl[i-8]
            if prev<m1l[i] and recent>m1l[i] and swing>0 and abs(swing)>.45:sig[3,i]=1
            elif prev>m1h[i] and recent<m1h[i] and swing<0 and abs(swing)>.45:sig[3,i]=-1
        if q!=0 and q==h1dir[i] and q!=m5dir[i] and a5>=2.0:sig[4,i]=q
        if q!=0 and q!=h1dir[i] and a5<4.0 and span_>=.9:sig[5,i]=q
    return sig

@njit(cache=True)
def _permit(regime,atr5,m5dir,h1dir,h4dir):
    if regime==0:return True
    if regime==1:return atr5>=1.5
    if regime==2:return h1dir!=0
    if regime==3:return m5dir!=0 and m5dir==h1dir
    if regime==4:return m5dir!=0 and h1dir!=0 and m5dir!=h1dir
    if regime==5:return atr5<4.0
    if regime==6:return atr5>=4.0
    return atr5>=6.0

@njit(cache=True)
def _session_policy(policy,flags):
    if policy==0:return flags!=0
    if policy==1:return flags&3!=0
    if policy==2:return flags&4!=0
    if policy==3:return flags&8!=0
    if policy==4:return flags&12!=0
    if policy==5:return flags&15!=0
    return bool((flags&4)!=0 and (flags&8)!=0)

@njit(cache=True)
def execute(ms,bid,ask,ix,ts,sig,qua,midanchor,atr5,m5dir,h1dir,h4dir,m15dir,sess,
            srcmask,regime,session_policy,exit_policy,cap,spreadcap,stop,goal,arm,trail_gap,hold_seconds,cooldown_ms,phase_start,phase_end,mode):
    """All-L0-L7 funded chronological whole-book simulation. One open, one pending max.
       Input quote time strictly ordered, never virtual side fills, no future outcome labels.
       Pending latency 250ms and 4-second timeout; caps assumed, not Coinexx certified.
    """
    ledger=np.empty((90000,12),np.float64);count=0
    cash=cap;eq_peak=cap;drawdown=0.;halt=0;pos=0;entry=0.;et=0;sl=0.;favmax=0.;own=0;sigms=0
    pending=0;pt=0;signal_quote=0.;source_idx=0;last_exit=-1e16
    lastmin=-1;rearms=0;lastside=0; last_sec=-1;si=-1
    offers=0;fills=0;spread_rej=0;cap_rej=0;source_eligible=0;quality_rej=0
    for i in range(len(ms)):
        now=ms[i];sec=now//1000
        if sec!=last_sec:
            si+=1;last_sec=sec
        if si>=len(ts) or ts[si]!=sec:break
        bp=bid[i]*.001;ap=ask[i]*.001;spread=ap-bp
        minute=sec//60
        if minute!=lastmin:
            lastmin=minute;rearms=0;lastside=0
        eq=cash + ((bp-entry) if pos==1 else (entry-ap)) - .20 if pos else cash
        if eq>eq_peak:eq_peak=eq
        if eq_peak-eq>drawdown:drawdown=eq_peak-eq
        # stop opening new positions when original equity enters catastrophic risk band
        if eq<cap*.60:halt=1
        if halt and pos==0 and pending==0:break
        # exits get priority over entries; actual opposing quote used
        if pos:
            favorable=(bp-entry) if pos==1 else (entry-ap)
            if favorable>favmax:favmax=favorable
            ex=0
            if (pos==1 and bp<=sl) or (pos==-1 and ap>=sl):ex=1
            elif favorable>=goal:ex=2
            elif now-et>=hold_seconds*1000:ex=3
            if ex:
                px=bp if pos==1 else ap;pnl=(px-entry)*pos-.20
                if count<len(ledger):
                    ledger[count,0]=et;ledger[count,1]=now;ledger[count,2]=pos;ledger[count,3]=entry;ledger[count,4]=px;ledger[count,5]=pnl;ledger[count,6]=own;ledger[count,7]=ex;ledger[count,8]=sigms;ledger[count,9]=favmax;ledger[count,10]=cash+pnl;ledger[count,11]=spread
                    count+=1
                cash+=pnl;last_exit=now;lastside=pos;pos=0;favmax=0.;pending=0;rearms+=1
                continue
            if favmax>=arm:
                cand=max(entry+.20,bp-trail_gap) if pos==1 else min(entry-.20,ap+trail_gap)
                if (pos==1 and cand>sl) or (pos==-1 and cand<sl):sl=cand
            continue
        if pending:
            if now-pt>4000:
                pending=0;cap_rej+=1
            elif now-pt>=250:
                px=ap if pending==1 else bp
                required=px/500. +spread+.20
                if spread>spreadcap or abs(px-signal_quote)>1.25 or required>cash*.65 or cash<cap*.60:
                    pending=0;cap_rej+=1
                else:
                    pos=pending;entry=px;et=now;sl=bp-stop if pos==1 else ap+stop;own=source_idx
                    fills+=1;pending=0;continue
        if pos or pending or halt or now<last_exit+cooldown_ms:continue
        if spread>spreadcap:spread_rej+=1;continue
        phase=sec%60
        if phase<phase_start or phase>phase_end:continue
        if not _session_policy(session_policy,sess[si]):continue
        if not _permit(regime,atr5[si],m5dir[si],h1dir[si],h4dir[si]):continue
        if i!=ix[si] and not (srcmask&1):continue
        # R9 native minute-bracket: bid/ask crossing frozen M1 anchor; completed S1 quality.
        selected=0;side=0
        if srcmask&1 and qua[si]!=0 and rearms<=3:
            bid_level=midanchor[si]+.15; sell_level=midanchor[si]-.15
            if rearms==0:
                if ap>=bid_level and qua[si]==1:side=1
                elif bp<=sell_level and qua[si]==-1:side=-1
            elif lastside==-1 and ap>=bid_level and qua[si]==1:side=1
            elif lastside==1 and bp<=sell_level and qua[si]==-1:side=-1
            if side!=0:selected=1
        if selected==0 and i==ix[si]:
            # Router has one proposal per observed quote, with deterministic lineage.
            # Mutually competing virtual sources share a single L7 physical slot.
            if (mode&2)!=0: # optional H1/M15 owner on supplemental sources
                allow_htf=h1dir[si]!=0 and m15dir[si]!=0
            else:allow_htf=True
            if allow_htf:
                for k in range(1,8):
                    if srcmask&(1<<k):
                        want=sig[k,si]
                        if want==0:continue
                        if mode&4 and want!=h1dir[si]:continue
                        if mode&8 and want==h1dir[si]:continue
                        side=want;selected=k+1;break
        if selected==0:continue
        source_eligible+=1
        # No hidden R9 label or oracle timing; refuse extra same-minute funded proposals.
        if rearms>=4:quality_rej+=1;continue
        if (mode&16) and selected!=1 and not (qua[si]==side):quality_rej+=1;continue
        # True execution only after at least 250ms and at first observed quote satisfying conditions.
        pending=side;pt=now;sigms=now;signal_quote=ap if side==1 else bp
        source_idx=selected;offers+=1
    return ledger[:count],np.array([cash-cap,drawdown,halt,offers,fills,spread_rej,cap_rej,source_eligible,quality_rej],np.float64)

SCHEMA=['entry_ms','exit_ms','side','entry_price','exit_price','net_usd','source_id','exit_reason','signal_ms','max_favorable_usd','closing_cash','exit_spread_usd']

def controls():
    # Structural alternatives, not trivial 1-point threshold tuning.
    patterns=[1,2,4,8,16,32,64,128,1|2,1|8,1|16,1|64,2|8|16,4|32,8|64|128,255]
    exits=[('SCALP',1.3,2.7,1.3,.6,18),('SPRINT',2.4,5.0,2.0,1.2,45),('CYCLE',4.0,8.0,3.0,2.0,120)]
    for mask in patterns:
      for reg in range(8):
        for session in (0,1,2,3,4):
          for x,stop,goal,arm,trail,hold in exits:
            yield dict(mask=mask,regime=reg,session=session,exit=x,stop=stop,goal=goal,arm=arm,trail=trail,hold=hold,
                       spreadcap=1.20,phase_start=1,phase_end=58,cooldown=250,mode=0)

def run_case(d,signals,c,cap=100.0):
    ledger,stats=execute(d['ms'],d['bid'],d['ask'],d['ix'],d['ts'],signals,d['qua'],d['midanchor'],d['atr5'],d['m5dir'],d['h1dir'],d['h4dir'],d['m15dir'],d['sess'],
       c['mask'],c['regime'],c['session'],0,cap,c['spreadcap'],c['stop'],c['goal'],c['arm'],c['trail'],c['hold'],c['cooldown'],c['phase_start'],c['phase_end'],c['mode'])
    arr=ledger[:,5];gp=arr[arr>0].sum();gl=-arr[arr<0].sum()
    return ledger,dict(net=float(stats[0]),max_tick_marked_dd=float(stats[1]),halt=bool(stats[2]),offers=int(stats[3]),filled=int(stats[4]),spread_rejected=int(stats[5]),funding_rejected=int(stats[6]),source_eligible=int(stats[7]),quality_rejected=int(stats[8]),trades=len(ledger),gross_winners=float(gp),gross_losers=float(gl),pf=float(gp/gl) if gl>0 else None,unclosed_fills=int(stats[4])-len(ledger))

def output_ledgers(d,c,led,stats,prefix):
    OUT.mkdir(exist_ok=True,parents=True)
    pd.DataFrame(led,columns=SCHEMA).to_csv(OUT/(prefix+'_TRADES.csv'),index=False)
    ex=pd.to_datetime(led[:,1],unit='ms',utc=True) if len(led) else pd.DatetimeIndex([],tz='UTC')
    cash=pd.DataFrame({'exit_ts':ex,'net':led[:,5]}) if len(led) else pd.DataFrame({'exit_ts':pd.DatetimeIndex([],tz='UTC'),'net':[]})
    for label,freq,n in [('HOUR','h',744),('DAY','D',31)]:
        frames=(cash.groupby(cash.exit_ts.dt.floor(freq)).net.agg(['sum','count']) if len(cash) else pd.DataFrame(columns=['sum','count']))
        end='2026-01-31 23:00' if freq=='h' else '2026-01-31'
        idx=pd.date_range('2026-01-01',end,freq=freq,tz='UTC')
        frames=frames.reindex(idx,fill_value=0);frames.to_csv(OUT/(prefix+'_'+label+'.csv'))
        assert len(frames)==n
    with (OUT/(prefix+'_SUMMARY.json')).open('w') as f:json.dump({'case':c,'account':stats,'benchmark':R9_MONTH,'no_live_claim':True},f,indent=2)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--smoke',action='store_true');parser.add_argument('--limit',type=int,default=0);parser.add_argument('--offset',type=int,default=0)
    args=parser.parse_args();OUT.mkdir(parents=True,exist_ok=True)
    d=load_source();ss=generate_sources(d['ts'],d['bid'][d['ix']].astype(float)*.001,d['qua'],d['imp'],d['eff'],d['acc'],d['span'],d['m1h'],d['m1l'],d['m1c'],d['m5c'],d['h1h'],d['h1l'],d['h1c'],d['m5dir'],d['h1dir'],d['h4dir'],d['m15dir'],d['atr5'])
    # Control run equivalent to V2 multi-session native R9 core, no simplification of integrated driver.
    base={'mask':1,'regime':0,'session':0,'exit':'R9_ACCEL','stop':.30,'goal':100.,'arm':.10,'trail':.03,'hold':30,'spreadcap':1.2,'phase_start':0,'phase_end':59,'cooldown':0,'mode':0}
    cases=[base]+list(controls())
    if args.smoke:cases=cases[:3]
    if args.offset:cases=cases[args.offset:]
    if args.limit:cases=cases[:args.limit]
    rows=[];best=None;best_score=-1e18;best_ledger=None
    t0=time.time()
    for ix,c in enumerate(cases):
        ledger,z=run_case(d,ss,c,100.0)
        row={'id':args.offset+ix,**c,**z};rows.append(row)
        # Eligible means not halted, cash > initial, and all positions closed.
        qualified=not z['halt'] and z['unclosed_fills']==0
        if qualified and z['net']>best_score:
            best_score=z['net'];best=row;best_ledger=ledger.copy()
        if ix==0 or (ix+1)%64==0:print('RUN',ix+1,'/',len(cases),'elapsed_s',round(time.time()-t0,1),'current_net',round(z['net'],2),'best_eligible',round(best_score,2),flush=True)
        if args.smoke and ix==0:output_ledgers(d,c,ledger,z,'V2_NATIVE_CONTROL_SMOKE')
    df=pd.DataFrame(rows)
    df.to_csv(OUT/f'V2_INTEGRATED_ALL_{args.offset}_{args.offset+len(rows)}_TRIALS.csv',index=False)
    if best is not None:
        output_ledgers(d,best,best_ledger,{k:best[k] for k in ['net','max_tick_marked_dd','halt','offers','filled','trades','gross_winners','gross_losers','pf','unclosed_fills']},'V2_BEST_ELIGIBLE')
    meta={'january_only':True,'source_sha256':PIN,'market_ticks':len(d['ms']),'number_cases':len(rows),'regime_source_names':REG,'specialist_names':SRC,'strategy_status':'UNPROMOTED_INTEGRATED_V2_RESEARCH','under60pct_research_only':True,'r9_generated_ideal':R9_MONTH,'r9_min_net_60pct':round(R9_MONTH['net']*.60,3),'r9_min_trades_60pct':int(np.ceil(R9_MONTH['trades']*.60)),'best_nonhalting':best,'cases_reaching_60pct_net':int(((df.net>=R9_MONTH['net']*.6)&(df.halt==False)).sum()),'cases_reaching_60pct_trades':int(((df.trades>=R9_MONTH['trades']*.6)&(df.halt==False)).sum()),'elapsed_seconds':time.time()-t0,'caveats':['January in-sample','raw Dukascopy Bid/Ask vs Coinexx generated ticks','lot 0.01 assumed 1oz','leverage 1:500 assumed, $0.20 fee assumed','no MT5 real tick certification','V2 new chassis retains V1 layer semantics but does not replace protected V1']}
    (OUT/'V2_JAN2026_INTEGRATED_QA.json').write_text(json.dumps(meta,indent=2,default=lambda o:float(o) if np.isscalar(o) else str(o))+'\n');print('DONE',json.dumps({'cases':len(rows),'best_eligible_net':None if best is None else best['net'],'cases60':meta['cases_reaching_60pct_net'],'seconds':round(time.time()-t0,1)}),flush=True)

if __name__=='__main__':main()
