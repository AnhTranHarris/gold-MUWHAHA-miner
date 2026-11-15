"""Causal Fib/quote-time-equilibrium/EMA-SMA V9-signal cohort.

This is a candidate-signal counterfactual, not a full on-policy strategy test.
All features are available at the original V9 signal, with confirmed pivot
latency. Entries/exits after signal consume every original source quote in order.
No market trade-volume / hidden liquidity model. No position averaging.
"""
from __future__ import annotations
import argparse, hashlib, gzip, json, time, os
from dataclasses import dataclass,asdict
from pathlib import Path
import numpy as np
import pandas as pd
from collections import Counter

ROOT=Path(os.environ.get('COINEXX_DATA_ROOT','/mnt/data'))
# Source pins are imported from the frozen V12 source-exact audit below.
import sys
sys.path.insert(0,str(Path(os.environ.get('R9_V12_SOURCE_ROOT',str(ROOT/'r9_v12_recovered_source')))/'micro180_20261114'))
from micro180_exactms_v12 import SHA_2026,EXPECTED_2026

@dataclass(frozen=True)
class Config:
    name:str
    swing:str='M1'
    ema:int=20
    sma:int=20
    fib:float=.50
    expiry_ms:int=30000
    rebound_c:int=10
    max_zone_width_c:int=30
    max_dislocation_c:int=250
    min_swing_c:int=90
    target_cash:float=.10
    stop_c:int=30
    hold_ms:int=30000
    use_anchor:bool=True
    min_anchor_age_ms:int=300000
    lattice:str='classic'  # classic confirmed pivots; MICRO uses past-only 180s extremes
    trend_rule:str='hard'
    anchor_rule:str='none'

CONFIGS=[
 Config('A_fib50_ema20_sma20',swing='M1',ema=20,sma=20,fib=.50,expiry_ms=30000,rebound_c=10),
 Config('B_fib618_ema9_sma20',swing='M1',ema=9,sma=20,fib=.618,expiry_ms=30000,rebound_c=15),
 Config('C_fib382_M5_ema20_sma12',swing='M5',ema=20,sma=12,fib=.382,expiry_ms=60000,rebound_c=15),
 Config('D_equal_1third_control',swing='M1',ema=20,sma=20,fib=1/3,expiry_ms=30000,rebound_c=10),
 Config('E_micro180_fib236',swing='MICRO180',lattice='recent_extreme',ema=20,sma=20,fib=.236,expiry_ms=45000,rebound_c=10,trend_rule='soft',max_dislocation_c=500),
 Config('F_micro180_fib382',swing='MICRO180',lattice='recent_extreme',ema=20,sma=20,fib=.382,expiry_ms=45000,rebound_c=10,trend_rule='soft',max_dislocation_c=500),
 Config('G_signal_fib236_step',swing='MICRO180',lattice='signal_step',ema=20,sma=20,fib=.236,expiry_ms=45000,rebound_c=10,trend_rule='soft',max_dislocation_c=500),
 Config('H_equal_25c_step',swing='MICRO180',lattice='equal_step',ema=20,sma=20,fib=.236,expiry_ms=45000,rebound_c=10,trend_rule='soft',max_dislocation_c=500),
 Config('I_fib382_microTWAP_target35',swing='MICRO180',lattice='recent_extreme',ema=20,sma=20,fib=.382,expiry_ms=45000,rebound_c=10,trend_rule='soft',max_dislocation_c=500,anchor_rule='micro_discount',target_cash=.35),
 Config('J_fib382_microTWAP_target65',swing='MICRO180',lattice='recent_extreme',ema=20,sma=20,fib=.382,expiry_ms=45000,rebound_c=10,trend_rule='soft',max_dislocation_c=500,anchor_rule='micro_discount',target_cash=.65,hold_ms=60000),
 Config('K_signalStep_microTWAP_target65',swing='MICRO180',lattice='signal_step',ema=20,sma=20,fib=.236,expiry_ms=45000,rebound_c=10,trend_rule='soft',max_dislocation_c=500,anchor_rule='micro_discount',target_cash=.65,hold_ms=60000),
 Config('M_fib236_runner_R8_T2',swing='MICRO180',lattice='signal_step',ema=20,sma=20,fib=.236,expiry_ms=60000,rebound_c=15,trend_rule='soft',max_dislocation_c=500,stop_c=80,target_cash=2.,hold_ms=180000),
 Config('N_fib382_runner_R8_T2',swing='MICRO180',lattice='recent_extreme',ema=20,sma=20,fib=.382,expiry_ms=60000,rebound_c=15,trend_rule='soft',max_dislocation_c=500,stop_c=80,target_cash=2.,hold_ms=180000),
 Config('O_equal25_runner_R8_T2',swing='MICRO180',lattice='equal_step',ema=20,sma=20,fib=.236,expiry_ms=60000,rebound_c=15,trend_rule='soft',max_dislocation_c=500,stop_c=80,target_cash=2.,hold_ms=180000),
 Config('P_fib382_structural_R10_T3_10m',swing='MICRO180',lattice='recent_extreme',ema=20,sma=20,fib=.382,expiry_ms=60000,rebound_c=15,trend_rule='soft',max_dislocation_c=500,stop_c=100,target_cash=3.,hold_ms=600000),
 Config('Q_equal25_structural_R10_T3_10m',swing='MICRO180',lattice='equal_step',ema=20,sma=20,fib=.236,expiry_ms=60000,rebound_c=15,trend_rule='soft',max_dislocation_c=500,stop_c=100,target_cash=3.,hold_ms=600000),
]

class Tape:
    def __init__(self,p:Path):
        df=pd.read_csv(p,usecols=['time_msc','bid','ask'],dtype={'time_msc':'int64','bid':'float64','ask':'float64'})
        self.ms=df.time_msc.to_numpy(dtype='int64');self.bid=np.rint(df.bid.to_numpy()*100).astype('int32');self.ask=np.rint(df.ask.to_numpy()*100).astype('int32');
        del df
        if np.any(np.diff(self.ms)<0):raise AssertionError('Source timestamps reordered')
        if np.any(self.ask<self.bid):raise AssertionError('Crossed quote')
        self.mid=(self.bid.astype('float64')+self.ask)/2
        self.bars={}
        self._bar(60_000,'M1')
        self._bar(300_000,'M5')
        self._twap()
        # First observation after last >2.5s discontinuity. No microextreme spans across it.
        d=np.diff(self.ms,prepend=self.ms[0]);breaks=np.where(d>2500,np.arange(len(d)),0)
        self.last_gap_start=np.maximum.accumulate(breaks)

    def _bar(self,tf,name):
        bucket=self.ms//tf
        starts=np.r_[0,np.flatnonzero(bucket[1:]!=bucket[:-1])+1]
        ends=np.r_[starts[1:]-1,len(self.ms)-1]
        # Completed only at observation of first quote in subsequent bucket.
        available=self.ms[starts[1:]]
        high=np.maximum.reduceat(self.mid,starts)
        low=np.minimum.reduceat(self.mid,starts)
        close=self.mid[ends]
        continuous=np.r_[False,np.diff(bucket[starts])==1]
        # calculated on complete source bars; first incomplete bar cannot be used.
        self.bars[name]=dict(starts=starts,ends=ends,bucket=bucket[starts],available=available,
            high=high,low=low,close=close,continuous=continuous)
        for span in (9,20):
            if name=='M1':
                self.bars[name][f'EMA{span}']=pd.Series(close).ewm(span=span,adjust=False).mean().to_numpy()
            if name=='M5':
                self.bars[name][f'SMA{span}']=pd.Series(close).rolling(span,min_periods=span).mean().to_numpy()
        if name=='M5':self.bars[name]['SMA12']=pd.Series(close).rolling(12,min_periods=12).mean().to_numpy()
        # Four consecutive observed neighbors required for pivot confirmation.
        # At index i+2, compare central pivot i. It becomes usable only at
        # first observed quote of next bar (index i+3).
        valid=np.array([np.all(np.diff(bucket[starts][i-2:i+3])==1) for i in range(2,len(starts)-2)],dtype=bool)
        piv_hi=[];piv_lo=[]
        for idx,i in enumerate(range(2,len(starts)-3)):
            if not valid[idx]:continue
            hs=high[i-2:i+3];ls=low[i-2:i+3]
            if high[i]>=np.max(hs) and np.argmax(hs)==2:piv_hi.append(i)
            if low[i]<=np.min(ls) and np.argmin(ls)==2:piv_lo.append(i)
        # A five-bar window ending at i+2 is known at start i+3.
        self.bars[name]['piv_hi']=np.array(piv_hi,dtype=np.int32)
        self.bars[name]['piv_lo']=np.array(piv_lo,dtype=np.int32)

    def _twap(self):
        # Time-weighted *midquote*, never trade-volume VWAP. Ignore stale intervals.
        ms=self.ms;mid=self.mid
        day=ms//86_400_000
        dt=np.diff(ms,prepend=ms[0]);dt[0]=0
        dt=np.where((dt>=0)&(dt<=2500)&(day==np.roll(day,1)),dt,0)
        # Prior mid persisted for observed interval; current tick has zero time contribution.
        prior=np.r_[mid[0],mid[:-1]]
        weights=np.cumsum(dt,dtype='float64');money=np.cumsum(prior*dt,dtype='float64')
        day_start=np.r_[0,np.flatnonzero(day[1:]!=day[:-1])+1]
        base_weight=np.r_[0,weights[day_start[1:]-1]]
        base_money=np.r_[0,money[day_start[1:]-1]]
        day_index=np.searchsorted(day_start,np.arange(len(ms)),side='right')-1
        w=weights-base_weight[day_index];v=money-base_money[day_index]
        self.twap=np.divide(v,w,out=np.full(len(ms),np.nan),where=w>=300_000)
        self.total_weight=weights;self.total_quote_value=money

    def feature(self,idx,cfg:Config,side:int):
        ts=int(self.ms[idx])
        m1=self.bars['M1'];m5=self.bars['M5']
        j=int(np.searchsorted(m1['available'],ts,side='right'))-1
        k=int(np.searchsorted(m5['available'],ts,side='right'))-1
        # available[j] is the first quote *after* bar j closed.
        if j<cfg.ema or k<cfg.sma or j<1 or k<1:return None
        e=m1[f'EMA{cfg.ema}'][j];ep=m1[f'EMA{cfg.ema}'][j-1]
        s=m5[f'SMA{cfg.sma}'][k];sp=m5[f'SMA{cfg.sma}'][k-1]
        tw=self.twap[idx]
        if not np.isfinite(tw) or not np.isfinite(s):return None
        mid=self.mid[idx]
        # Distinct 1-minute EMA drift and 5-minute SMA drift.
        if ts-int(m1['available'][j])>120_000 or ts-int(m5['available'][k])>600_000:return None
        if cfg.trend_rule=='hard':
            trend=side*(e-s)>0 and side*(e-ep)>0 and side*(s-sp)>=0
        else:
            trend=side*(e-s)>0 and side*(e-ep)>-10 and side*(s-sp)>-10
        if not trend:return None
        # Session price-duration-weighted anchor is an observed context, not VWAP.
        if cfg.use_anchor and cfg.lattice=='classic' and abs(mid-tw)>250:return None
        if cfg.lattice!='classic':
            left=int(np.searchsorted(self.ms,ts-180000,side='left'))
            left=max(left,int(self.last_gap_start[idx]))
            if left>=idx-3 or ts-int(self.ms[left])<20000:return None
            H=float(np.max(self.mid[left:idx+1]));L=float(np.min(self.mid[left:idx+1]))
            twap_micro=(self.total_quote_value[idx]-self.total_quote_value[left]) / max(1.,self.total_weight[idx]-self.total_weight[left])
            span=H-L
            if span<cfg.min_swing_c or span>4000:return None
            if cfg.lattice=='recent_extreme':
                rail=(H-cfg.fib*span) if side>0 else (L+cfg.fib*span)
            elif cfg.lattice=='signal_step':
                step=min(80.,max(22.,cfg.fib*span))
                rail=mid-side*step
            elif cfg.lattice=='equal_step':
                rail=mid-side*25.
            else:raise ValueError('Unknown experimental lattice')
            if side*(mid-rail)>cfg.max_dislocation_c:return None
            if cfg.anchor_rule=='micro_discount':
                # Choose a rail on the discounted side of observed 180s
                # price-duration equilibrium; exclude excessively distant tails.
                discount=side*(twap_micro-rail)
                if discount<5 or discount>160:return None
            return dict(rail=rail,mid=mid,tw=tw,twap_micro=twap_micro,ema=e,sma=s,span=span,
                        ema_slope=side*(e-ep),sma_slope=side*(s-sp),swing='MICRO180',
                        fib=cfg.fib,dislocation=side*(mid-rail),anchor_distance=side*(mid-tw))
        bar=self.bars[cfg.swing]
        cutoff=int(np.searchsorted(bar['available'],ts,side='right'))-1
        if cutoff<0:return None
        highs=bar['piv_hi'];lows=bar['piv_lo']
        # Confirmed pivots i require availability at start of bar i+3.
        hi=highs[(highs+2)<=cutoff]
        lo=lows[(lows+2)<=cutoff]
        if not len(hi) or not len(lo):return None
        hi=int(hi[-1]);lo=int(lo[-1])
        if abs(hi-lo)>(24 if cfg.swing=='M1' else 15):return None
        bull=hi>lo
        if (1 if bull else -1)!=side:return None
        H=float(bar['high'][hi]);L=float(bar['low'][lo])
        if H-L<cfg.min_swing_c:return None
        rail=(H-cfg.fib*(H-L)) if side>0 else (L+cfg.fib*(H-L))
        if side*(mid-rail)>cfg.max_dislocation_c or side*(mid-rail)<-cfg.max_zone_width_c:return None
        # Diagnostics are frozen at initial V9 signal time.
        return dict(rail=rail,mid=mid,tw=tw,ema=e,sma=s,span=H-L,
                    ema_slope=side*(e-ep),sma_slope=side*(s-sp),swing=cfg.swing,
                    fib=cfg.fib,dislocation=side*(mid-rail),anchor_distance=side*(mid-tw))


def candidate_trajectory(tape:Tape,entry_idx:int,side:int,feat:dict,cfg:Config):
    ms=tape.ms;bid=tape.bid;ask=tape.ask;mid=tape.mid
    now=int(ms[entry_idx]);stop_at=int(np.searchsorted(ms,now+cfg.expiry_ms,side='right'))
    rail=feat['rail'];touched=False;touch_idx=-1;extreme=0.
    # Future exact source rows only, do not backfill instantaneous limit executions.
    for j in range(entry_idx+1,min(len(ms),stop_at)):
        if ms[j]-ms[j-1]>2500:return None,'entry_gap'
        spread=int(ask[j]-bid[j]);
        if spread>25:return None,'spread_stress'
        current_exec=int(ask[j] if side>0 else bid[j])
        liq=int(bid[j] if side>0 else ask[j]);
        if not touched:
            # Explicit quote-side achievable market price. Must reach discounted rail.
            if side*(current_exec-rail)<=0:
                touched=True;touch_idx=j;extreme=float(liq)
            continue
        extreme=min(extreme,liq) if side>0 else max(extreme,liq)
        if ms[j]-ms[touch_idx]<250 or j-touch_idx<2:continue
        # After reaching rail, executable liquidation must rebound and still be
        # inside the predeclared rail neighborhood (no chasing extended bounce).
        if side*(liq-extreme)>=cfg.rebound_c and side*(current_exec-rail)<=cfg.max_zone_width_c:
            return j,'confirmed_market'
    return None,'no_touch_or_reclaim'


def exit_trajectory(tape:Tape,fill_idx:int,side:int,cfg:Config):
    ms=tape.ms;bid=tape.bid;ask=tape.ask
    entry=int(ask[fill_idx] if side>0 else bid[fill_idx]);liq0=int(bid[fill_idx] if side>0 else ask[fill_idx]);
    stop=liq0-cfg.stop_c if side>0 else liq0+cfg.stop_c
    end_idx=int(np.searchsorted(ms,ms[fill_idx]+cfg.hold_ms,side='right'))
    for j in range(fill_idx+1,min(len(ms),end_idx+2)):
        liq=int(bid[j] if side>0 else ask[j]);net=side*(liq-entry)/100-.20
        if (side>0 and liq<=stop) or (side<0 and liq>=stop):return j,net,'stop'
        if net<=-2:return j,net,'risk'
        if net>=max(1.75,cfg.target_cash):return j,net,'preferred'
        if ms[j]-ms[fill_idx]>=cfg.hold_ms:return j,net,'timeout'
        if ms[j]-ms[j-1]>2500:return j,net,'gap'
        if net+1e-9>=cfg.target_cash:return j,net,'target'
    return None,None,'file_end'


def run_month(m:int,configs=CONFIGS,limit_signals=None):
    mon=f'{m:02d}'
    p=ROOT/f'XAUUSD_MT5_BROKER_2026_{mon}_ticks_ALL.csv.gz'
    with p.open('rb') as f:sha=hashlib.file_digest(f,'sha256').hexdigest()
    if sha!=SHA_2026[mon]:raise AssertionError('Original full source SHA mismatch')
    tape=Tape(p)
    events=pd.read_csv(ROOT/f'r9_micro180_v12_results/2026-{mon}_V12_exactms_micro180_events.csv.gz',usecols=['entry_ordinal','entry_time_msc','side','exit_price_u','entry_execution_u'])
    assert len(events)==EXPECTED_2026[mon][1],(m,len(events))
    if limit_signals:events=events.iloc[:limit_signals]
    original_wins=int(((events.side*(events.exit_price_u-events.entry_execution_u)/100-.2)>0).sum())
    outputs={}
    for cfg in configs:
        ctr=Counter();trades=[];last_exit=-10**20;fills_by_minute=Counter()
        for r in events.itertuples(index=False):
            i=int(r.entry_ordinal)-1;ms=int(tape.ms[i]);side=int(r.side)
            if ms!=int(r.entry_time_msc):raise AssertionError('Source ordinal event mismatch')
            if ms<last_exit+1500:ctr['locked']+=1;continue
            feat=tape.feature(i,cfg,side)
            if feat is None:ctr['no_causal_confluence']+=1;continue
            ctr['causal_location_candidates']+=1
            fi,reason=candidate_trajectory(tape,i,side,feat,cfg)
            if fi is None:ctr[reason]+=1;continue
            fill_minute=int(tape.ms[fi])//60_000
            if fills_by_minute[fill_minute]>=4:ctr['fill_minute_cap']+=1;continue
            j,net,ex=exit_trajectory(tape,fi,side,cfg)
            if j is None:ctr['file_end']+=1;continue
            fills_by_minute[fill_minute]+=1;last_exit=int(tape.ms[j]);ctr['completed']+=1
            ctr['wins']+=int(net>0);ctr['stops']+=int(ex=='stop');ctr['target']+=int(ex in ('target','preferred'))
            ctr['net_cents']+=int(round(net*100))
            trades.append((int(r.entry_time_msc),int(tape.ms[fi]),int(tape.ms[j]),int(r.side),round(net,2),ex,feat['rail'],feat['dislocation']))
        outputs[cfg.name]=dict(config=asdict(cfg),counts=dict(ctr),mean_net=round(ctr['net_cents']/100/max(1,ctr['completed']),5),net=round(ctr['net_cents']/100,2),win_fraction=round(ctr['wins']/max(1,ctr['completed']),6),trades=trades)
        print('MONTH',mon,cfg.name,ctr['causal_location_candidates'],'FILL',ctr['completed'],'NET',round(ctr['net_cents']/100,2),'WIN',round(ctr['wins']/max(1,ctr['completed']),3),flush=True)
    return dict(month=mon,source_sha=sha,quotes=len(tape.ms),V9_signals=len(events),V9_winning_signals=original_wins,models=outputs,
        important_scope='V9-on-policy signal cohort with alternate sequential entry/exit; not full independent on-policy alternate router',
        confirmed_bars_only=True)

if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--months',default='01,05,09');a.add_argument('--limit',type=int,default=0);args=a.parse_args()
 out=Path('/mnt/data/cfael_v13');out.mkdir(exist_ok=True)
 for m in args.months.split(','):
  t=time.monotonic();res=run_month(int(m),limit_signals=args.limit or None)
  (out/f'{m}_candidate_cohort.json').write_text(json.dumps(res,indent=2))
  print('RUNTIME',m,round(time.monotonic()-t,1),flush=True)
