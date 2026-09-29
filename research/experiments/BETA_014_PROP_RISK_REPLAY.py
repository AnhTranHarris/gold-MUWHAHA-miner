#!/usr/bin/env python3
"""BETA014: source-reusing, original-tick, funded prop-risk replay of R9 control and BETA001.

Keeps the exact historical Dukascopy strategy geometry in BETA_009_JAN_JUL_ENTRY_CANDIDATE_VALIDATION.py
and applies the BETA013 house research risk overlay, with a static 0.01 lot.
Pure research simulator. NOT an MT5/broker certification. No August read.
"""
from __future__ import annotations
import sys, datetime, json, os, time, hashlib
from pathlib import Path
import numpy as np, pandas as pd
from numba import njit

HERE=Path('/mnt/data')
BASE_SOURCE=HERE/'BETA_009_JAN_JUL_ENTRY_CANDIDATE_VALIDATION.py'
sys.path.insert(0,str(HERE))
import BETA_009_JAN_JUL_ENTRY_CANDIDATE_VALIDATION as v
assert v.COMM==.20, 'source controls may have changed; check source version before reuse'
atr_min=v.atr_min

INITIAL=100000.0
LOTS=0.01
CONTRACT_OZ_PER_LOT=100.0
EXPOSURE_OZ=LOTS*CONTRACT_OZ_PER_LOT
assert EXPOSURE_OZ == 1.0
FEE_PER_SIDE=.01
ROUND_TRIP_COMMISSION=2*FEE_PER_SIDE
SOFT_DAILY_USD=4000.0
HARD_DAILY_USD=5000.0
OVERALL_FLOOR_USD=90000.0
MAX_PLANNED_RISK_FRACTION=.0025
ASSUMED_LEVERAGE=100.0
ASSUMED_MARGIN_STOPOUT_FRACTION=.5
# Pause NEW entries 16:55 through 17:05 local NY as a modeled rollover precaution.
# This is NOT an assertion about exact Coinexx metal sessions. Friday from 16:55 NY.
ROLLOVER_START_MINUTE=16*60+55
ROLLOVER_END_MINUTE=17*60+5


def calendar_by_tick(t):
    """New York 17:00 reset, DST aware, using the actual observed quote minute."""
    minute=t//60000
    starts=np.r_[0, np.flatnonzero(minute[1:]!=minute[:-1])+1]
    observed_minute=minute[starts]
    utc=pd.to_datetime(observed_minute*60000,unit='ms',utc=True)
    ny=utc.tz_convert('America/New_York')
    local_naive=ny.tz_localize(None)
    # At 17:00, risk day advances to following local calendar date.
    day=(local_naive-pd.Timedelta(hours=17)).normalize().to_numpy(dtype='datetime64[D]').astype(np.int32)
    minute_of_day=np.asarray(ny.hour,dtype=np.int16)*60+np.asarray(ny.minute,dtype=np.int16)
    dow=np.asarray(ny.dayofweek,dtype=np.int8)  # Friday=4
    blocked=((minute_of_day>=ROLLOVER_START_MINUTE)&(minute_of_day<ROLLOVER_END_MINUTE)) | ((dow==4)&(minute_of_day>=ROLLOVER_START_MINUTE)) | (dow>=5)
    repeat=np.diff(np.r_[starts,len(t)])
    return np.repeat(day,repeat).astype(np.int32),np.repeat(~blocked,repeat).astype(np.uint8)


@njit(cache=True)
def replay(t, askr, bidr, start_i, s1last,qd,qe,qr,qt,qspan,m5ids,m5atr,idx250,idx1,idx5,day_key,may_enter,mode, cap,ratio,d5min):
    """mode=0 feed-normalized R9; mode=1 BETA001.  Never deposit after initial $100k."""
    balance=INITIAL; equity=INITIAL;peak=INITIAL; min_equity=INITIAL;maxdd=0.;peak_balance=INITIAL;max_balance_dd=0.
    profit=0.;gross_profit=0.;gross_loss=0.;wins=0; trades=0; entries=0
    daily_key=-9999999;day_reference=INITIAL;soft_lock=False;hard_lock=False
    n_daily_soft=0;n_daily_hard=0;n_risk_veto=0;n_session_veto=0
    n_no_margin=0;n_rollover_veto=0
    last_soft_ts=-1;last_hard_ts=-1;last_overall_ts=-1;overall_breach_equity=np.nan;overall_breach_balance=np.nan
    forced_closes=0;last_close_reason=0;peak_trade_float=0.
    pos=0;entry=0.;sl=0.;entrysec=0;cycle=-1;buy=sell=0.;pending=0;had=False;lastpos=0;rearms=0;lastExit=-10**18
    m5p=0;atr=np.nan; stop_t=len(t); last_i=start_i
    daily_n=np.empty(260,np.int64);day_idx=0;day_record=np.empty((260,9),np.float64);day_record[:,:]=np.nan
    # columns: 0 day key 1 start equity ref 2 min equity 3 end balance 4 trades 5 wins 6 pnl 7 soft flag 8 hard flag
    def_unused=0
    for i in range(start_i,len(t)):
        last_i=i
        tm=t[i];ask=askr[i]/1000.;bid=bidr[i]/1000.;mid=.5*(ask+bid);sp=ask-bid
        if pos==1: floating=(bid-entry)*EXPOSURE_OZ
        elif pos==-1: floating=(entry-ask)*EXPOSURE_OZ
        else:floating=0.
        equity=balance+floating
        if equity>peak:peak=equity
        if equity<min_equity:min_equity=equity
        if peak-equity>maxdd:maxdd=peak-equity
        if balance>peak_balance:peak_balance=balance
        if peak_balance-balance>max_balance_dd:max_balance_dd=peak_balance-balance
        # We cannot retrospectively infer a max drawdown after an overall terminal stop.
        this_day=day_key[i]
        if this_day!=daily_key:
            if daily_key!=-9999999:
                day_record[day_idx,3]=balance
                day_idx+=1
            daily_key=this_day
            day_reference=balance if balance>equity else equity
            soft_lock=False;hard_lock=False
            day_record[day_idx,0]=float(this_day)
            day_record[day_idx,1]=day_reference
            day_record[day_idx,2]=equity
            day_record[day_idx,3]=balance
            day_record[day_idx,4]=0.
            day_record[day_idx,5]=0.
            day_record[day_idx,6]=0.
            day_record[day_idx,7]=0.
            day_record[day_idx,8]=0.
        if equity<day_record[day_idx,2]:day_record[day_idx,2]=equity
        # R9 minute cycle resets even if a position is already open.
        minute=tm//60000
        if minute!=cycle:
            cycle=minute;buy=mid+.15;sell=mid-.15;pending=2;rearms=0
        # Overall floor has priority, then daily hard breach, then soft. 
        breach_overall=equity<=OVERALL_FLOOR_USD+1e-9
        breach_day=(equity<=day_reference-HARD_DAILY_USD+1e-9)
        breach_soft=(equity<=day_reference-SOFT_DAILY_USD+1e-9)
        if breach_soft and not soft_lock:
            soft_lock=True;n_daily_soft+=1;last_soft_ts=tm;day_record[day_idx,7]=1.
        if breach_day and not hard_lock:
            hard_lock=True;n_daily_hard+=1;last_hard_ts=tm;day_record[day_idx,8]=1.
        if breach_overall or breach_day:
            if pos!=0:
                # True executable tick liquidation at bid for a long, ask for short.
                px=bid if pos==1 else ask
                gross_move=(px-entry)*EXPOSURE_OZ if pos==1 else (entry-px)*EXPOSURE_OZ
                trade_net=gross_move-ROUND_TRIP_COMMISSION
                balance+=gross_move-FEE_PER_SIDE   # entry fee was taken at opening
                profit+=trade_net;trades+=1;day_record[day_idx,4]+=1.;day_record[day_idx,6]+=trade_net
                if trade_net>0:wins+=1;gross_profit+=trade_net;day_record[day_idx,5]+=1.
                else:gross_loss+=trade_net
                forced_closes+=1;pos=0
                equity=balance
                if equity<min_equity:min_equity=equity
                if peak-equity>maxdd:maxdd=peak-equity
                if peak_balance-balance>max_balance_dd:max_balance_dd=peak_balance-balance
            if breach_overall or equity<=OVERALL_FLOOR_USD+1e-9:
                last_overall_ts=tm; overall_breach_equity=equity;overall_breach_balance=balance
                stop_t=i+1;last_close_reason=4
                break
            # Daily hard stop; next day restores ability to enter.
            last_close_reason=3
            continue
        if pos!=0:
            margin=(entry*EXPOSURE_OZ)/ASSUMED_LEVERAGE
            if equity<ASSUMED_MARGIN_STOPOUT_FRACTION*margin:
                n_no_margin+=1
                # practically unreachable before overall 90k floor at these inputs
            close=False;px=0.
            if pos==1:
                if bid<=sl or tm//1000-entrysec>=30:close=True;px=bid
                elif bid-entry>=.10:
                    cand_sl=bid-.03
                    if cand_sl>sl:sl=cand_sl
            else:
                if ask>=sl or tm//1000-entrysec>=30:close=True;px=ask
                elif entry-ask>=.10:
                    cand_sl=ask+.03
                    if cand_sl<sl:sl=cand_sl
            if close:
                gross_move=(px-entry)*EXPOSURE_OZ if pos==1 else (entry-px)*EXPOSURE_OZ
                trade_net=gross_move-ROUND_TRIP_COMMISSION
                balance+=gross_move-FEE_PER_SIDE
                profit+=trade_net;trades+=1;day_record[day_idx,4]+=1.;day_record[day_idx,6]+=trade_net
                if trade_net>0:wins+=1;gross_profit+=trade_net;day_record[day_idx,5]+=1.
                else:gross_loss+=trade_net
                if balance>peak_balance:peak_balance=balance
                if peak_balance-balance>max_balance_dd:max_balance_dd=peak_balance-balance
                if balance<min_equity:min_equity=balance
                if peak-balance>maxdd:maxdd=peak-balance
                lastpos=pos;pos=0;had=True;lastExit=tm
            continue
        if had:
            had=False
            if minute==cycle and rearms<3:rearms+=1;pending=-1 if lastpos==1 else 1
            else:pending=0
            continue
        if soft_lock or hard_lock:continue
        if not may_enter[i]:
            n_rollover_veto+=1
            continue
        if mode==1 and tm-lastExit<500:continue
        mb=tm//300000
        while m5p+1<len(m5ids) and m5ids[m5p+1]<mb:m5p+=1
        p=m5p
        if m5ids[p]>=mb:p-=1
        if p<0:continue
        atr=m5atr[p]
        qi=s1last[i]
        if qi<10 or np.isnan(atr) or atr+1e-12<atr_min(tm):continue
        if qe[qi]<.70 or qr[qi]<.50 or qt[qi]>9:continue
        qside=1 if qd[qi]>=.15 else (-1 if qd[qi]<=-.15 else 0)
        if qside==0:continue
        side=0
        if mode==0:
            if (pending==2 or pending==1) and ask>=buy and qside==1:side=1
            elif (pending==2 or pending==-1) and bid<=sell and qside==-1:side=-1
        else:
            if sp>cap or sp/(qr[qi]+1e-9)>ratio:continue
            j250=idx250[i];j1=idx1[i];j5=idx5[i]
            m250=(askr[j250]+bidr[j250])*.0005 if j250>=0 else mid
            m1=(askr[j1]+bidr[j1])*.0005 if j1>=0 else mid
            m5=(askr[j5]+bidr[j5])*.0005 if j5>=0 else mid
            d250=mid-m250;d1=mid-m1;d5=mid-m5
            if qside==1 and d250>0 and d1>.04 and d5>d5min and qspan[qi]<=12:side=1
            elif qside==-1 and d250<0 and d1<-.04 and d5<-d5min and qspan[qi]<=12:side=-1
        if side!=0:
            stop_loss=bid-.30 if side==1 else ask+.30
            planned_risk= (ask-stop_loss if side==1 else stop_loss-bid)*EXPOSURE_OZ+ROUND_TRIP_COMMISSION
            if planned_risk>MAX_PLANNED_RISK_FRACTION*equity:
                n_risk_veto+=1;continue
            margin=ask*EXPOSURE_OZ/ASSUMED_LEVERAGE
            if equity<margin:
                n_no_margin+=1;continue
            pos=side;entry=ask if side==1 else bid;entrysec=tm//1000;sl=stop_loss;pending=0
            balance-=FEE_PER_SIDE;entries+=1
            # monitor equity immediately on entry (includes price crossing spread plus entry fee)
            live_eq=balance+ ((bid-entry)*EXPOSURE_OZ if side==1 else (entry-ask)*EXPOSURE_OZ)
            if live_eq<min_equity:min_equity=live_eq
            if peak-live_eq>maxdd:maxdd=peak-live_eq
            if live_eq<day_record[day_idx,2]:day_record[day_idx,2]=live_eq
    if daily_key!=-9999999:day_record[day_idx,3]=balance;day_idx+=1
    return (trades,wins,profit,gross_profit,gross_loss,balance,min_equity,peak,maxdd,max_balance_dd,
            n_daily_soft,n_daily_hard,n_risk_veto,n_rollover_veto,n_no_margin,forced_closes,
            last_soft_ts,last_hard_ts,last_overall_ts,overall_breach_equity,overall_breach_balance,
            last_i,stop_t,last_close_reason,entries,day_record[:day_idx].copy())


def iso(t):
    if t<0:return None
    return datetime.datetime.fromtimestamp(int(t)/1000,datetime.timezone.utc).isoformat()


def result_to_dict(out, kind, month):
    (trades,wins,net,gp,gl,balance,minimum,peak,maxdd,max_balance_dd,soft,hard,veto,blocked,nmargin,forced,
     first_soft,first_hard,overall,breach_eq,breach_balance,last_i,stop_i,close_reason,entries,day_rows)=out
    days=[]
    for d in day_rows:
        if np.isnan(d[0]):continue
        day=datetime.datetime(1970,1,1)+datetime.timedelta(days=int(d[0]))
        days.append({'risk_day_ny':day.strftime('%Y-%m-%d'), 'day_reference_usd':round(float(d[1]),2),
                     'minimum_equity_usd':round(float(d[2]),2),'closing_balance_usd':round(float(d[3]),2),
                     'trades':int(d[4]),'wins':int(d[5]),'net_usd':round(float(d[6]),2),
                     'soft_locked':bool(d[7]),'hard_locked':bool(d[8])})
    assert trades==sum(d['trades'] for d in days),(trades,sum(d['trades'] for d in days))
    assert wins==sum(d['wins'] for d in days)
    assert abs(balance-INITIAL-net)<0.05,(balance,net)
    assert abs(net-gp-gl)<0.05
    return {'strategy':kind,'month':month,'trade_count':int(trades),'winning_trades':int(wins),'losing_trades':int(trades-wins),
            'win_rate_percent':round(100*wins/trades,4) if trades else 0,
            'net_profit_usd':round(float(net),2),'gross_profit_usd':round(float(gp),2),'gross_loss_usd':round(float(gl),2),
            'end_balance_usd':round(float(balance),2),'min_marked_equity_usd':round(float(minimum),2),
            'peak_marked_equity_usd':round(float(peak),2),'max_floating_equity_drawdown_usd':round(float(maxdd),2),
            'max_realized_balance_drawdown_usd':round(float(max_balance_dd),2),
            'daily_soft_lockouts':int(soft),'daily_hard_lockouts':int(hard),
            'planned_risk_vetos':int(veto),'rollover_session_tick_rejections':int(blocked),'margin_vetos':int(nmargin),
            'forced_risk_closures':int(forced),'first_or_last_soft_lock_utc':iso(first_soft),
            'first_or_last_hard_lock_utc':iso(first_hard), 'overall_floor_breach_utc':iso(overall),
            'overall_breach_marked_equity_usd':round(float(breach_eq),2) if not np.isnan(breach_eq) else None,
            'overall_breach_balance_usd':round(float(breach_balance),2) if not np.isnan(breach_balance) else None,
            'terminal_stop':bool(overall>=0), 'terminal_reason':int(close_reason),'last_tick_index':int(last_i),
            'daily_records':days}


def main():
    start=time.time(); outputs={}; source=[]; loaded_months=[]
    for month, fname, expected in v.FILES:
        if month!='2026-01' and all(x.get('terminal_stop') for x in outputs.values()):
            break
        p=HERE/fname
        print('READ',month,p.name,flush=True)
        t,a,b,sha,problem=v.load_month(p)
        assert sha==expected and not problem,(month,sha,problem)
        source.append({'month':month,'file':fname,'ticks':len(t),'sha256':sha,'gzip_eof_crc_passed':True,'problems':problem})
        loaded_months.append(month)
        prep=v.prep(t,a,b)
        day_key,may_enter=calendar_by_tick(t)
        for name,mode,cap,ratio,d5 in [('R9_FEED_NORMALIZED',0,0.,0.,0.),('R09_BETA_001_ADAPTIVE_IGNITION_ENTRY',1,1.,.65,.18)]:
            r=replay(t,a,b,0,*prep,day_key,may_enter,mode,cap,ratio,d5)
            res=result_to_dict(r,name,month)
            outputs[name]=res
            print('RESULT',name,{k:res[k] for k in ['trade_count','winning_trades','win_rate_percent','net_profit_usd','gross_profit_usd','gross_loss_usd','end_balance_usd','max_floating_equity_drawdown_usd','overall_floor_breach_utc','daily_soft_lockouts','daily_hard_lockouts']},flush=True)
    result={'id':'BETA_014_PROP_001LOT_FUNDED_RERUN','status':'REPLAYED_ORIGINAL_DUKASCOPY_QUOTES_FUNDING_CAPPED',
            'strategy_source':str(BASE_SOURCE.name),'benchmark':'R9 feed-normalized Python control; NOT original Coinexx MT5',
            'settings':{'starting_balance_usd':INITIAL,'fixed_lots':LOTS,'contract_oz_per_lot':CONTRACT_OZ_PER_LOT,
                'exposure_oz':EXPOSURE_OZ,'commission_per_entry_usd':FEE_PER_SIDE,'commission_per_exit_usd':FEE_PER_SIDE,
                'daily_soft_loss_usd':SOFT_DAILY_USD,'daily_hard_loss_usd':HARD_DAILY_USD,
                'overall_equity_floor_usd':OVERALL_FLOOR_USD,'risk_day':'17:00 America/New_York, DST-aware',
                'day_reference':'higher of balance and marked equity at first available quote of new NY 17:00-anchored trading day',
                'planned_per_trade_risk_cap_percent_current_equity':MAX_PLANNED_RISK_FRACTION*100.,
                'one_position_max':True,'margin_model':'illustrative 100:1, 50pct maintenance stopout; broker unverified',
                'rollover_entry_pause':'16:55-17:05 New York local, Fridays from 16:55 New York local; observed quote gaps respected',
                'news_filter':'NOT EVALUATED; no verified point-in-time calendar','slippage':'0 hypothetical; does not claim broker execution parity',
                'bid_ask':'observed Dukascopy quote-side fills, no average-spread shortcut',
                'stop_price_usd':.30,'trail_activation_usd':.10,'trail_distance_usd':.03,'max_hold_seconds':30},
            'sources_scanned_this_replay':source,'market_test_scope':'Jan-Jul 2026, terminal-capped; later months zero funded trades after terminal stop',
            'strategy_results':outputs,'elapsed_sec':round(time.time()-start,2),
            'limitations':['no Coinexx actual session/margin/stop-level/slippage parity','direct model preserves source R9-like one-second bar logic rather than exact Coinexx spread point gate','no verified news calendar so blackout NOT EVALUATED','month-specific bars only if trading survived','no owner-authorized MQL5','August SEALED']}
    path=HERE/'BETA_014_PROP_001LOT_FUNDED_RERUN.json'
    temp=path.with_suffix('.json.tmp');temp.write_text(json.dumps(result,indent=2,sort_keys=True));os.replace(temp,path)
    print('OUTPUT',str(path),'SEC',result['elapsed_sec'],flush=True)

if __name__=='__main__':main()