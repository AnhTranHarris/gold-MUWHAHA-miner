"""New standalone, fully endogenous virtual liquidity grid candidate, research only.
No inherited preselected events and NO R8 MT5 times. Intent decided on completed
Bid-second buckets; only one physically funded position, 0.01 lot=1oz.
Two virtual levels per rolling window; only confirmed sweep/reclaim becomes a
physical order. Stops/TP/time/cooldown are as-of, all fills original Bid/Ask.
"""
from pathlib import Path
import json,sys,time
import numpy as np
from numba import njit
P=Path('/mnt/data/R8_JAN_DUKAS_RESEARCH');ROOT=Path(__file__).parent
@njit(cache=True)
def simulate(t,bid,ask,window=30,buff=.35,reclaim=.45,profit=2.,stop=2.5,
             spread_ceiling=1.25,expiry_sec=30,max_hold_sec=90,latency_ms=250,
             fee=.20,cash_start=100.,leverage=500.,cooldown_sec=2,loss_pause_min=5,mode=0):
    # mode=0 sweep-reclaim, mode=1 confirmed continuation on next test of virtual level
    hi_ring=np.zeros(300,np.float64);lo_ring=np.zeros(300,np.float64);count=0;head=0
    secprev=-1;sec_hi=sec_lo=0.
    state=0;level=0.;state_since=0;pending=0;fill_at=0
    position=0;open_px=0.;stop_px=0.;tp_px=0.;opened=0;last_close_sec=-1000000
    current_day=-1;trades=0;win=0;grossprofit=0.;grossloss=0.;min_eq=cash_start;peak=cash_start;maxdd=0.;worst_hour=0.;phour=cash_start;hour=-1
    cash=cash_start;forced=0;max_concur=0;prev_loss=0;pause_until=0;active_since=0;open_i=-1
    day_cash=np.zeros(31,np.float64);day_trades=np.zeros(31,np.int64);entry_log=np.empty(80000,np.int64);exit_log=np.empty(80000,np.int64);side_log=np.empty(80000,np.int8);pnls=np.empty(80000,np.float64)
    for i in range(len(t)):
        ms=int(t[i]);s=ms//1000;B=int(bid[i])/1000.;A=int(ask[i])/1000.;sp=A-B
        d=(ms//86400000) # absolute UTC day, converted later on Python side
        if position!=0:
            eq=cash+position*((B if position>0 else A)-open_px)-fee
        else:eq=cash
        if eq<min_eq:min_eq=eq
        if eq>peak:peak=eq
        if peak-eq>maxdd:maxdd=peak-eq
        h=ms//3600000
        if h!=hour:hour=h;phour=eq
        if eq>phour:phour=eq
        if phour-eq>worst_hour:worst_hour=phour-eq
        # settlement is actual quote tick, no future fill or exit.
        if position!=0:
            out=(B if position>0 else A)
            reason=0
            if eq<=0 or eq/(open_px/leverage)<.5:reason=3
            elif (position>0 and (B<=stop_px or B>=tp_px)) or (position<0 and (A>=stop_px or A<=tp_px)):reason=1
            elif s-opened>=max_hold_sec:reason=2
            if reason:
                p=position*(out-open_px)-fee
                cash+=p
                if trades<len(pnls):
                    entry_log[trades]=open_i;exit_log[trades]=i;side_log[trades]=position;pnls[trades]=p
                trades+=1
                if p>0:win+=1;grossprofit+=p;prev_loss=0
                else:grossloss+=p;prev_loss+=1
                # daily ledger is native UTC exit day by tick timestamp
                dayidx=int((ms-t[0])//86400000)
                if dayidx>=0 and dayidx<31:day_cash[dayidx]+=p;day_trades[dayidx]+=1
                if prev_loss>=2:pause_until=s+loss_pause_min*60;prev_loss=0
                if reason==3:forced+=1
                last_close_sec=s;position=0;state=0;pending=0
            # Update completed second ring even while position is funded.
        # do not permit new entry at same current tick
        if secprev<0:secprev=s;sec_hi=B;sec_lo=B
        elif s!=secprev:
            hi_ring[head]=sec_hi;lo_ring[head]=sec_lo;head=(head+1)%len(hi_ring);count=min(count+1,len(hi_ring))
            secprev=s;sec_hi=B;sec_lo=B
        else:
            if B>sec_hi:sec_hi=B
            if B<sec_lo:sec_lo=B
        if position!=0:continue
        if pending!=0:
            if ms<fill_at:continue
            direction=pending;pending=0
            px=A if direction>0 else B
            # Pre-position equity after immediate spread hit and fee plus stressed margin cap
            post=cash-sp-fee;margin=px/leverage
            if post<=0 or margin>post*.20 or post/margin<=2.:continue
            open_px=px;position=direction;open_i=i;opened=s
            stop_px=(B-stop if direction>0 else A+stop)
            tp_px=(A+profit if direction>0 else B-profit)
            max_concur=1;state=0;continue
        if s<=last_close_sec+cooldown_sec or s<pause_until or count<window or sp>spread_ceiling:continue
        upper=-1e99;lower=1e99
        for j in range(window):
            idx=(head-1-j)%len(hi_ring)
            if hi_ring[idx]>upper:upper=hi_ring[idx]
            if lo_ring[idx]<lower:lower=lo_ring[idx]
        if state==0:
            if A>upper+buff:state=1;level=upper;state_since=s
            elif B<lower-buff:state=-1;level=lower;state_since=s
        elif s-state_since>expiry_sec:state=0
        elif state==1:
            # bearish reclaim after sweeping upper historical 1s liquidity
            if mode==0 and B<level-reclaim:pending=-1;fill_at=ms+latency_ms;state=0
            elif mode==1 and B>level+reclaim and s-state_since>=2:pending=1;fill_at=ms+latency_ms;state=0
        elif state==-1:
            if mode==0 and A>level+reclaim:pending=1;fill_at=ms+latency_ms;state=0
            elif mode==1 and A<level-reclaim and s-state_since>=2:pending=-1;fill_at=ms+latency_ms;state=0
    if position!=0:
        i=len(t)-1;out=int(bid[i] if position>0 else ask[i])/1000.;p=position*(out-open_px)-fee;cash+=p
        if trades<len(pnls):entry_log[trades]=open_i;exit_log[trades]=i;side_log[trades]=position;pnls[trades]=p
        trades+=1
        if p>0:win+=1;grossprofit+=p
        else:grossloss+=p
    n=min(trades,len(pnls))
    return cash,trades,win,grossprofit,grossloss,min_eq,maxdd,worst_hour,forced,entry_log[:n],exit_log[:n],side_log[:n],pnls[:n],day_cash,day_trades

def main():
    t0=time.time();t=np.load(P/'ticks_t.npy',mmap_mode='r');b=np.load(P/'ticks_bid.npy',mmap_mode='r');a=np.load(P/'ticks_ask.npy',mmap_mode='r')
    configs=[('SWEEP_A',0,30,.35,.45,2.,2.5,1.25),('SWEEP_B',0,60,.60,.5,3.,2.,1.5),('CONT_A',1,30,.35,.45,2.,2.5,1.25),('CONT_B',1,60,.60,.5,3.,2.,1.5)]
    out={}
    for name,mode,w,buff,reclaim,profit,stop,spread in configs:
        cash,n,win,gp,gl,min_eq,dd,hd,forced,ei,xi,dr,p,dc,dn=simulate(t,b,a,w,buff,reclaim,profit,stop,spread,30,90,250,.20,100.,500.,2,5,mode)
        # Chronological each close independently matches original input sides.
        if n:
          calc=np.where(dr>0,b[xi].astype(np.float64)-a[ei].astype(np.float64),b[ei].astype(np.float64)-a[xi].astype(np.float64))/1000.-.20
          err=float(np.max(np.abs(calc-p)))
        else:err=0.
        assert err<1e-8,(name,err)
        v=dict(end_cash=float(cash),trades=int(n),wins=int(win),gross_profit=float(gp),gross_loss=float(gl),min_tick_equity=float(min_eq),max_tick_dd=float(dd),worst_hour_dd=float(hd),forced=int(forced),ledger_quote_error=err,elapsed_s=time.time()-t0,mode=name)
        out[name]=v
        np.savez_compressed(ROOT/(name+'_exact_quote_trade_ledger.npz'),entry_idx=ei,exit_idx=xi,side=dr,net=p)
        print(name,v,flush=True)
    (ROOT/'grid0344_fully_endogenous_results.json').write_text(json.dumps(out,indent=2))
if __name__=='__main__':main()
