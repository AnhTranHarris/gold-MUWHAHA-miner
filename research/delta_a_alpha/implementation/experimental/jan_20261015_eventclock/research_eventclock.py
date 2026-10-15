"""Independent January-only original Bid/Ask causal micro-event grid research.
All cases internal: ONLY >= 60% R9 source absolute H1+day may be described as a success.
New mechanistic sources: actual quote-change polarity; quote-update cadence acceleration;
event-clock acceleration; delayed sweep/reclaim; M1 live-so-far geometry; rolling efficiency.
No R9 after-trade labels in signal generation. Includes complete forensic failures.
"""
import numpy as np, pandas as pd, hashlib, json, time, sys, os
from pathlib import Path
from numba import njit
BASE=Path('/mnt/data'); DIR=Path(__file__).parent
PIN='d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5'
SRC=BASE/'XAUUSD_DUKAS_2026_01_ticks.csv(3).gz'

@njit(cache=True)
def replay(ms,bid,ask,sec_start,signals,attrs,stop,profit,trail_on,trail_gap,timeout,cap_spread,cap,session_mask,phase_lo,phase_hi):
  # signals pre-computed strictly from past completed seconds, every quote exit uses actual bid ask.
  led=np.empty((110000,9),np.float64);ln=0;bank=cap;peak_eq=cap;dd=0.;halt=0
  pos=0;entry=0.;entryms=0;stopprice=0.;favpeak=0.;last_close=-10**18; tradesminute=0;minu=-1
  pending=0;psig=0;pt=0;pbase=0.;pn_idx=-1;offers=0;fills=0;rejected=0;tick_index=0;openheat=0.
  # sec_start indices are first tick of each observed second
  for i in range(len(ms)):
    now=ms[i];sec=now//1000
    while tick_index+1<len(sec_start) and sec_start[tick_index+1]<=i:tick_index+=1
    minute=now//60000
    if minute!=minu:tradesminute=0;minu=minute
    bp=bid[i]*.001;ap=ask[i]*.001;spread=ap-bp
    eq=bank+((bp-entry) if pos==1 else (entry-ap))-.20 if pos else bank
    if eq>peak_eq:peak_eq=eq
    if peak_eq-eq>dd:dd=peak_eq-eq
    if eq<cap*.60:halt=1
    if pos:
      fave=bp-entry if pos==1 else entry-ap
      if fave>favpeak:favpeak=fave
      exitcode=0
      if (pos==1 and bp<=stopprice) or (pos==-1 and ap>=stopprice):exitcode=1
      elif fave>=profit:exitcode=2
      elif now-entryms>=timeout*1000:exitcode=3
      if exitcode:
        xp=bp if pos==1 else ap;pnl=(xp-entry)*pos-.20
        if ln<110000:
          led[ln,0]=entryms;led[ln,1]=now;led[ln,2]=pos;led[ln,3]=entry;led[ln,4]=xp;led[ln,5]=pnl;led[ln,6]=exitcode;led[ln,7]=favpeak;led[ln,8]=pn_idx
          ln+=1
        bank+=pnl;pos=0;pending=0;last_close=now;continue
      if favpeak>=trail_on:
        newstop=(max(entry+.20,bp-trail_gap) if pos==1 else min(entry-.20,ap+trail_gap))
        if (pos==1 and newstop>stopprice) or (pos==-1 and newstop<stopprice):stopprice=newstop
      continue
    if pending:
      if now-pt>4000:pending=0;rejected+=1
      elif now>=pt+250:
        ep=ap if pending==1 else bp
        if spread>cap_spread or abs(ep-pbase)>1.3 or ep/500.+spread+.20>bank*.80 or bank<cap*.60:
          pending=0;rejected+=1
        else:
          pos=pending;entry=ep;entryms=now;stopprice=bp-stop if pos==1 else ap+stop
          pending=0;favpeak=0.;fills+=1;tradesminute+=1;pn_idx=psig;continue
    if pending or pos or halt or now<last_close+500 or tradesminute>=5:continue
    if (sec%60)<phase_lo or (sec%60)>phase_hi:continue
    if (1<<((sec//3600)%24))&session_mask==0:continue
    if sec_start[tick_index]!=i:continue
    sv=signals[tick_index]
    if sv==0:continue
    pending=sv;psig=tick_index;pt=now;pbase=ap if sv==1 else bp;offers+=1
  return led[:ln],(bank-cap,dd,halt,offers,fills,rejected,pos)

def make_features(ms,bid,ask):
  s=ms//1000
  indices=np.r_[0,np.flatnonzero(s[1:]!=s[:-1])+1]
  boundaries=np.r_[indices,len(ms)]
  sec=s[indices];first=bid[indices];cl=bid[boundaries[1:]-1]
  hi=np.maximum.reduceat(bid,indices);lo=np.minimum.reduceat(bid,indices)
  qty=np.diff(boundaries).astype(np.float64)
  # Bid quote upward vs downward changes per actual second: genuine OTC quote flow, not exchange volume.
  deltas=np.diff(bid,prepend=bid[0]);up=np.add.reduceat((deltas>0).astype('int32'),indices).astype('float64')
  down=np.add.reduceat((deltas<0).astype('int32'),indices).astype('float64')
  # Use exact *past completed second* for each signal; can use cl[-1] / volumes of previous second.
  bp=cl.astype('float64')/1000
  x=pd.DataFrame({'cl':bp,'sec':sec,'vol':qty,'up':up,'down':down},index=pd.to_datetime(sec,unit='s',utc=True))
  # rolling by *observed-second count* plus abs gap control; no future inclusion.
  delta=x.cl.diff();x['d1']=delta.shift(1);x['d2']=x.cl.shift(1)-x.cl.shift(3)
  x['d5']=x.cl.shift(1)-x.cl.shift(6);x['d15']=x.cl.shift(1)-x.cl.shift(16)
  x['d60']=x.cl.shift(1)-x.cl.shift(61)
  x['vol5']=x.vol.shift(1).rolling(5,min_periods=5).sum()
  x['vol60']=x.vol.shift(1).rolling(60,min_periods=60).sum()
  x['imbal5']=(x.up.shift(1)-x.down.shift(1)).rolling(5,min_periods=5).sum()
  x['flow5']=x.imbal5/(x.vol5+1)
  x['flow20']=(x.up.shift(1)-x.down.shift(1)).rolling(20,min_periods=20).sum()/(x.vol.shift(1).rolling(20,min_periods=20).sum()+1)
  x['travel20']=delta.abs().shift(1).rolling(20,min_periods=20).sum()
  x['eff20']=abs(x.cl.shift(1)-x.cl.shift(21))/(x.travel20+1e-6)
  x['hi20']=x.cl.shift(1).rolling(20,min_periods=20).max()
  x['lo20']=x.cl.shift(1).rolling(20,min_periods=20).min()
  x['hi60']=x.cl.shift(1).rolling(60,min_periods=60).max()
  x['lo60']=x.cl.shift(1).rolling(60,min_periods=60).min()
  x['swing20']=(x.hi20-x.lo20)
  x['last']=x.cl.shift(1)
  x['previous']=x.cl.shift(2)
  x['wickgap']=x['last']-(x.hi20+x.lo20)*.5
  x['gap']=x.sec.diff().fillna(1).shift(1)
  # Last-completed M1 and M5 mean and range from observation (if not closed yet, never use current endpoint).
  frame60=x.groupby(x.index.floor('60s')).cl.last(); frame300=x.groupby(x.index.floor('300s')).cl.last()
  x['m1d']=frame60.diff().shift(1).reindex(x.index.floor('60s')).to_numpy()
  x['m5d']=frame300.diff().shift(1).reindex(x.index.floor('300s')).to_numpy()
  x['m5abs']=frame300.diff().abs().rolling(12,min_periods=12).mean().shift(1).reindex(x.index.floor('300s')).to_numpy()
  # intraminute elapsed phase from real time, as-of. Prev completed M1 level; current M1 open observed in past.
  x['prev_m1']=frame60.shift(1).reindex(x.index.floor('60s')).to_numpy()
  x['m1fromprev']=x['last']-x.prev_m1
  return indices,x

def signal_bank(x):
  # no R9 labels, only past quote updates. Sparse 1-second state changes can re-arm every time flat.
  f=lambda name:x[name].to_numpy(dtype='float64',na_value=np.nan)
  d1=f('d1');d2=f('d2');d5=f('d5');d15=f('d15');d60=f('d60')
  flow=f('flow5');flow20=f('flow20');eff=f('eff20');vol=f('vol5');oldvol=f('vol60')
  wig=f('wickgap');disp=f('m1fromprev');m5=f('m5d');m1=f('m1d');last=f('last');hi=f('hi20');lo=f('lo20');span=f('swing20');m5abs=f('m5abs');gap=f('gap')
  valid=np.isfinite(d60)&(gap<=5)&np.isfinite(m5abs)
  groups={}
  for t in (0.12,.30,.55,.95):
    for mode in ['TICK_FLOW_BREAK','SHOCK_REVERSAL','FLOW_DIVERGENCE','EVENT_ACCELERATION','M1_ORIGIN_ROTATION','EFFICIENCY_TREND','M5_OPPOSED_REIGNITE','SWING_REJECTION']:
      sig=np.zeros(len(x),np.int8)
      if mode=='TICK_FLOW_BREAK':
        ok=valid&(abs(d1)>t)&(abs(flow)>.35)&(np.sign(flow)==np.sign(d5))&(np.sign(d1)==np.sign(flow))
        sig[ok]=np.sign(flow[ok]).astype('int8')
      elif mode=='SHOCK_REVERSAL':
        ok=valid&(abs(d1)>t)&(abs(d2)>t*1.5)&(np.sign(d1)!=np.sign(d5))&(abs(flow20)<.4)
        sig[ok]=np.sign(d1[ok]).astype('int8')
      elif mode=='FLOW_DIVERGENCE':
        ok=valid&(abs(d5)>t)&(abs(flow)>.2)&(np.sign(d5)!=np.sign(flow))&(np.sign(d1)==np.sign(flow))
        sig[ok]=np.sign(flow[ok]).astype('int8')
      elif mode=='EVENT_ACCELERATION':
        ok=valid&(abs(d5)>t)&(vol>(oldvol/12)*1.8)&(np.sign(d5)==np.sign(flow))&(eff>.45)
        sig[ok]=np.sign(d5[ok]).astype('int8')
      elif mode=='M1_ORIGIN_ROTATION':
        ok=valid&(abs(disp)>t)&(np.sign(d1)!=np.sign(disp))&(span>2*t)&(eff<.5)
        sig[ok]=-np.sign(disp[ok]).astype('int8')
      elif mode=='EFFICIENCY_TREND':
        ok=valid&(abs(d15)>t*2)&(eff>.55)&(np.sign(d5)==np.sign(d15))&(np.sign(d1)==np.sign(d15))
        sig[ok]=np.sign(d15[ok]).astype('int8')
      elif mode=='M5_OPPOSED_REIGNITE':
        ok=valid&(abs(d5)>t)&(abs(m5)>t*2)&(np.sign(d5)!=np.sign(m5))&(np.sign(d1)==np.sign(d5))
        sig[ok]=np.sign(d5[ok]).astype('int8')
      elif mode=='SWING_REJECTION':
        ok=valid&(abs(d1)>t)&(last>hi-t)&(d1<0)
        sig[ok]=-1
        ok=valid&(abs(d1)>t)&(last<lo+t)&(d1>0)
        sig[ok]=1
      groups[(mode,t)]=sig
  regimes={'ALL':np.ones(len(x),bool),'QUIET':m5abs<4,'VOLATILE':m5abs>=4,'HIGH_VOL':m5abs>=8}
  return groups,regimes

if __name__=='__main__':
  st=time.time();digest=hashlib.sha256(SRC.read_bytes()).hexdigest();assert digest==PIN
  d=pd.read_csv(SRC,compression='gzip',usecols=['timestamp_ms_utc','bid_raw','ask_raw'],dtype={'timestamp_ms_utc':'int64','bid_raw':'int32','ask_raw':'int32'});ms=d.timestamp_ms_utc.to_numpy();bid=d.bid_raw.to_numpy();ask=d.ask_raw.to_numpy();del d
  ix,f=make_features(ms,bid,ask);print('FEATURES',len(ix),len(ms),time.time()-st,flush=True)
  bank,regimes=signal_bank(f)
  # 8 mechanistic families * 4 different amplitudes * 4 distinct regime owners * 4 session windows * 2 exits = 1024 new trials.
  sessions={'ALL':(1<<24)-1,'ASIA':sum(1<<h for h in range(0,8)),'LONDON':sum(1<<h for h in range(8,17)),'US':sum(1<<h for h in range(13,23))}
  exits={'FAST':(2.8,4.5,1.0,.8,35,.85),'SLOW':(5.,12.,3.,2.,180,.85)}
  out=[];best=(-1e20,None,None,None)
  start_id=int(os.environ.get("START_ID","0"));end_id=int(os.environ.get("END_ID","1024")); counter=0
  for mode in bank:
    for reg,allowed in regimes.items():
      sig=np.where(allowed,bank[mode],0).astype('int8')
      for session,session_bits in sessions.items():
        for exname,values in exits.items():
          if counter<start_id or counter>=end_id:
            counter+=1;continue
          led,stats=replay(ms,bid,ask,ix,sig,None,*values[:5],values[5],100.,session_bits,3,57)
          cash,dd,halt,offers,fills,reject,open_=stats
          pn=led[:,5] if len(led) else np.zeros(0)
          loss=np.minimum(pn,0).sum();win=np.maximum(pn,0).sum()
          row=dict(id=counter,source=mode[0],amp=mode[1],regime=reg,session=session,exits=exname,net=round(cash,4),trades=len(led),gross_loss=round(loss,4),gross_profit=round(win,4),pf=round(win/-loss,5) if loss else None,dd=round(dd,4),halt=int(halt),offers=offers,filled=fills,open=int(open_))
          out.append(row);counter+=1
          if cash>best[0] and not halt and not open_:best=(cash,row,led.copy(),sig.copy())
    if len(out)>0 and len(out)%128==0:
      pd.DataFrame(out).to_csv(DIR/'ALL_FULLTICK_EXPERIMENTS_PARTIAL.csv',index=False)
      print('STEPS',len(out),'elapsed',round(time.time()-st,1),'best_eligible',best[0],flush=True)
  p=pd.DataFrame(out);p.to_csv(DIR/f'CHUNK_{start_id:04d}_{end_id:04d}.csv',index=False)
  if best[1]:
    pd.DataFrame(best[2],columns=['entry_ms','exit_ms','side','entry','exit','net','exit_reason','max_favorable','proposal_i']).to_csv(DIR/'BEST_FULL_TICK_LEDGER.csv',index=False)
    ptime=pd.to_datetime(best[2][:,1],unit='ms',utc=True)
    hh=pd.DataFrame({'hour':ptime.floor('h'),'net':best[2][:,5]}).groupby('hour').net.agg(['sum','count']);hh.reindex(pd.date_range('2026-01-01','2026-01-31 23:00',freq='h',tz='UTC'),fill_value=0).to_csv(DIR/f'BEST_{start_id}_{end_id}_744_HOURS.csv')
    day=pd.DataFrame({'day':ptime.floor('D'),'net':best[2][:,5]}).groupby('day').net.agg(['sum','count']);day.reindex(pd.date_range('2026-01-01','2026-01-31',freq='D',tz='UTC'),fill_value=0).to_csv(DIR/f'BEST_{start_id}_{end_id}_31_DAYS.csv')
  summary={'research_only':True,'first_tick_original_SHA256':PIN,'quotes':len(ms),'trial_count':len(p),'start_id':start_id,'end_id':end_id,'distinct_mechanisms':8,'best_eligible':best[1],'r9_month_net':41520.82,'r9_60pct_month_floor':24912.492,'owner_success_floor_reached':bool(best[0]>=24912.492),'elapsed_s':round(time.time()-st,2)}
  (DIR/f'RESEARCH_QA_{start_id}_{end_id}.json').write_text(json.dumps(summary,indent=2));print('RESULT',summary,flush=True)