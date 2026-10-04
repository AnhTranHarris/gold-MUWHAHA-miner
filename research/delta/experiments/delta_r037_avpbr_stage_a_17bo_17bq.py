"""DELTA R037 Accumulation Volume-Profile Breakout -> POC Retest continuation screen.

Preregistered unit:
R037_ACCUMULATION_VOLUME_PROFILE_BREAKOUT_RETEST_STAGE_A_SCREEN_CHECKPOINT_17BO_17BQ

The public source exposes the causal state-machine grammar but not indexed numeric
defaults. Numeric fixtures are therefore explicit project research fixtures from
the preregistration, not claimed source defaults.

Research only. August sealed. MQL5 not authorized.
"""
from __future__ import annotations

import argparse, hashlib, json, os, tempfile
from pathlib import Path
import numpy as np
import pandas as pd
from numba import njit

DAY=86_400_000; HOUR=3_600_000; TICK=10; SCALE=1000
END=1_768_737_600_000
US_DST=1_772_953_200_000; UK_DST=1_774_746_000_000
P75_POINTS=np.asarray([20,20,21,21],np.int64)
CANONICAL_SHA="d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5"
PREREG_COMMIT="1c522c43631d9c11792673df07269a5c4b1f35cc"

ATR_LEN=14; LOOKBACK=20; COMP=1.5; MIN_BOX=5; MAX_BOX=40; ABANDON=2.0
ROWS=24; VA_FRAC=0.70; POC_ZONE_FRAC=0.10; MAX_WAIT=20; EMA_LEN=20
MAX_SPREAD=250; STOP=300; TRAIL_ACT=100; TRAIL_DIST=30; MAX_HOLD=30

CONFIGS=(
 ("17BO_C01_AVPBR_M1_CORE",60_000,False),
 ("17BP_C02_AVPBR_M5_CORE",300_000,False),
 ("17BQ_C03_AVPBR_M1_H1_EMA_BIAS",60_000,True),
)

def sha256_file(path:Path)->str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda:f.read(1<<20),b""): h.update(block)
    return h.hexdigest()

def atomic_json(path:Path,payload:dict)->None:
    path.parent.mkdir(parents=True,exist_ok=True)
    tmp_name=None
    try:
        with tempfile.NamedTemporaryFile("w",encoding="utf-8",newline="\n",dir=path.parent,
                                         prefix=f".{path.name}.",suffix=".tmp",delete=False) as tmp:
            tmp_name=tmp.name
            json.dump(payload,tmp,indent=2); tmp.write("\n"); tmp.flush(); os.fsync(tmp.fileno())
        os.replace(tmp_name,path); tmp_name=None
    finally:
        if tmp_name is not None:
            try: os.unlink(tmp_name)
            except FileNotFoundError: pass

def session_code(t):
    tod=t%DAY
    ls=np.where(t>=UK_DST,7,8)*HOUR; le=ls+30_600_000
    ns=np.where(t>=US_DST,12,13)*HOUR; ne=ns+32_400_000
    il=(tod>=ls)&(tod<le); iny=(tod>=ns)&(tod<ne)
    return np.where(il&iny,2,np.where(il,1,np.where(iny,3,0))).astype(np.int8)

def p75_surface(t,ask_raw,bid_raw):
    spread=P75_POINTS[session_code(t)]*TICK
    mid2=ask_raw.astype(np.int64)+bid_raw.astype(np.int64)
    bid=((mid2-spread+TICK)//(2*TICK))*TICK
    return (bid+spread).astype(np.int64),bid.astype(np.int64)

def quantize_mid(ask_raw,bid_raw):
    mid=(ask_raw.astype(np.int64)+bid_raw.astype(np.int64))//2
    return ((mid+TICK//2)//TICK)*TICK

def make_bars(t,mid,tf_ms):
    bucket=t//tf_ms
    st=np.r_[0,np.flatnonzero(bucket[1:]!=bucket[:-1])+1]
    en=np.r_[st[1:],len(t)]
    return dict(
      end_ms=((bucket[st]+1)*tf_ms).astype(np.int64),
      open=mid[st].astype(np.int64),
      high=np.maximum.reduceat(mid,st).astype(np.int64),
      low=np.minimum.reduceat(mid,st).astype(np.int64),
      close=mid[en-1].astype(np.int64),
      ticks=(en-st).astype(np.int64),
    )

def atr14(b):
    h,l,c=b["high"],b["low"],b["close"]
    tr=(h-l).astype(np.float64)
    if len(tr)>1:
        tr[1:]=np.maximum(tr[1:],np.maximum(np.abs(h[1:]-c[:-1]),np.abs(l[1:]-c[:-1])))
    out=np.full(len(tr),np.nan,np.float64)
    if len(tr)>=ATR_LEN:
        cs=np.r_[0.0,np.cumsum(tr)]
        out[ATR_LEN-1:]=(cs[ATR_LEN:]-cs[:-ATR_LEN])/ATR_LEN
    return out

def ema(x,n):
    out=np.full(len(x),np.nan,np.float64)
    if not len(x): return out
    a=2.0/(n+1.0); v=float(x[0]); out[0]=v
    for i in range(1,len(x)):
        v=a*float(x[i])+(1-a)*v; out[i]=v
    return out

def h1_bias_at(bar_end,h1):
    # Prior completed H1 only. bidx equivalent: last H1 end strictly <= current bar start/end.
    j=np.searchsorted(h1["end_ms"],bar_end,side="left")-1
    if j<EMA_LEN: return 0
    e=h1["ema"][j]
    if not np.isfinite(e): return 0
    c=float(h1["close"][j])
    return 1 if c>e else (-1 if c<e else 0)

def volume_profile_from_bars(b,start,end_exclusive,box_lo,box_hi):
    if end_exclusive<=start or box_hi<=box_lo: return None
    edges=np.linspace(float(box_lo),float(box_hi),ROWS+1)
    counts=np.zeros(ROWS,np.float64)
    for i in range(start,end_exclusive):
        lo=float(max(int(b["low"][i]),box_lo)); hi=float(min(int(b["high"][i]),box_hi))
        vol=float(b["ticks"][i])
        if hi<lo or vol<=0: continue
        if hi==lo:
            r=int(np.searchsorted(edges,lo,side="right")-1); r=min(max(r,0),ROWS-1); counts[r]+=vol
            continue
        first=max(0,min(ROWS-1,int(np.searchsorted(edges,lo,side="right")-1)))
        last=max(0,min(ROWS-1,int(np.searchsorted(edges,hi,side="left"))))
        spans=[]
        total=0.0
        for r in range(first,last+1):
            ov=max(0.0,min(hi,edges[r+1])-max(lo,edges[r]))
            if ov>0: spans.append((r,ov)); total+=ov
        if total<=0: continue
        for r,ov in spans: counts[r]+=vol*(ov/total)
    poc=int(np.argmax(counts))
    target=VA_FRAC*float(counts.sum()); included=float(counts[poc]); lo=poc; hi=poc
    while included<target and (lo>0 or hi+1<ROWS):
        below=counts[lo-1] if lo>0 else -1.0
        above=counts[hi+1] if hi+1<ROWS else -1.0
        if below>=above:
            if lo>0: lo-=1; included+=counts[lo]
            else: hi+=1; included+=counts[hi]
        else:
            if hi+1<ROWS: hi+=1; included+=counts[hi]
            else: lo-=1; included+=counts[lo]
    poc_px=(edges[poc]+edges[poc+1])/2.0
    return int(round(poc_px/TICK)*TICK),int(round(edges[lo]/TICK)*TICK),int(round(edges[hi+1]/TICK)*TICK)

def signals_for_config(t,b,h1,use_htf):
    atr=atr14(b)
    idx=[]; sides=[]; days=[]
    diag={k:0 for k in ("compression_starts","abandoned","breakouts","htf_rejects","pullback_touches","far_edge_invalidations","wait_expiries","signals_long","signals_short")}
    state=0
    box_start=-1; box_lo=0; box_hi=0; box_atr=0.0
    direction=0; poc=val=vah=0; zone=0; wait=0; touched=False
    i=max(LOOKBACK-1,ATR_LEN-1)
    while i<len(b["end_ms"]):
        a=float(atr[i])
        if not np.isfinite(a) or a<=0: i+=1; continue
        o=int(b["open"][i]); hi=int(b["high"][i]); lo=int(b["low"][i]); c=int(b["close"][i]); end=int(b["end_ms"][i])
        if state==0:
            s=i-LOOKBACK+1
            rhi=int(np.max(b["high"][s:i+1])); rlo=int(np.min(b["low"][s:i+1]))
            if rhi-rlo<=COMP*a:
                state=1; box_start=s; box_lo=rlo; box_hi=rhi; box_atr=a; diag["compression_starts"]+=1
            i+=1; continue
        if state==1:
            age=i-box_start
            # Breakout is tested against the previously established box before incorporating this bar.
            breakout=1 if c>box_hi else (-1 if c<box_lo else 0)
            if breakout!=0 and age>=MIN_BOX:
                if use_htf:
                    hb=h1_bias_at(end,h1)
                    if hb!=breakout:
                        diag["htf_rejects"]+=1; state=0; i+=1; continue
                vp=volume_profile_from_bars(b,box_start,i,box_lo,box_hi)
                if vp is None: state=0; i+=1; continue
                poc,val,vah=vp; direction=breakout
                zone=max(TICK,int(round((POC_ZONE_FRAC*(box_hi-box_lo))/TICK))*TICK)
                state=2; wait=0; touched=False; diag["breakouts"]+=1
                i+=1; continue
            nlo=min(box_lo,lo); nhi=max(box_hi,hi)
            if nhi-nlo>ABANDON*a or age>=MAX_BOX:
                diag["abandoned"]+=1; state=0; i+=1; continue
            box_lo=nlo; box_hi=nhi
            i+=1; continue
        # state 2: wait for POC pullback, invalidation, then continuation reclaim.
        wait+=1
        if direction>0 and c<val:
            diag["far_edge_invalidations"]+=1; state=0; i+=1; continue
        if direction<0 and c>vah:
            diag["far_edge_invalidations"]+=1; state=0; i+=1; continue
        if wait>MAX_WAIT:
            diag["wait_expiries"]+=1; state=0; i+=1; continue
        if not touched and lo<=poc+zone and hi>=poc-zone:
            touched=True; diag["pullback_touches"]+=1
        if touched:
            q=(direction>0 and c>poc and c>o) or (direction<0 and c<poc and c<o)
            if q:
                j=int(np.searchsorted(t,end,side="left"))
                if j<len(t):
                    idx.append(j); sides.append(direction); days.append((end-1)//DAY)
                    if direction>0: diag["signals_long"]+=1
                    else: diag["signals_short"]+=1
                state=0
        i+=1
    if not idx:
        return np.empty(0,np.int64),np.empty(0,np.int8),np.empty(0,np.int64),diag
    return np.asarray(idx,np.int64),np.asarray(sides,np.int8),np.asarray(days,np.int64),diag

@njit(cache=True)
def quote_tick(x): return ((int(x)+5)//10)*10

@njit(cache=True)
def evaluate(idx,side,sig_day,t,ask,bid):
    busy=-1; trades=skips=spread_rej=0; longs=shorts=wins=0; gp=gl=net=0.0
    stopx=holdx=endx=0; td=np.empty(idx.size,np.int64); n=0
    for z in range(idx.size):
        i=int(idx[z]); s=int(side[z]); day=int(sig_day[z])
        if i<=busy: skips+=1; continue
        if int(ask[i]-bid[i])>MAX_SPREAD: spread_rej+=1; continue
        trades+=1; longs+=s>0; shorts+=s<0; td[n]=day; n+=1
        entry=int(ask[i]) if s>0 else int(bid[i])
        stop=quote_tick(int(bid[i])-STOP if s>0 else int(ask[i])+STOP)
        sec0=int(t[i])//1000; raw=0.0; reason=2; last=i
        for k in range(i+1,t.size):
            aa=int(ask[k]); bb=int(bid[k]); sec=int(t[k])//1000; last=k
            if s>0 and bb<=stop: raw=(bb-entry)/SCALE; reason=0; break
            if s<0 and aa>=stop: raw=(entry-aa)/SCALE; reason=0; break
            if sec-sec0>=MAX_HOLD: raw=((bb-entry) if s>0 else (entry-aa))/SCALE; reason=1; break
            fav=(bb-entry) if s>0 else (entry-aa)
            if fav>=TRAIL_ACT:
                ns=quote_tick(bb-TRAIL_DIST if s>0 else aa+TRAIL_DIST)
                if (s>0 and ns>stop) or (s<0 and ns<stop): stop=ns
        else:
            aa=int(ask[last]); bb=int(bid[last]); raw=((bb-entry) if s>0 else (entry-aa))/SCALE
        ex=raw-0.01; net+=ex-0.01; wins+=ex>1e-12
        if raw>0: gp+=ex
        else: gl+=ex
        if reason==0: stopx+=1
        elif reason==1: holdx+=1
        else: endx+=1
        busy=last
    distinct=0
    if n:
        x=np.sort(td[:n]); distinct=1
        for k in range(1,x.size): distinct+=x[k]!=x[k-1]
    return trades,skips,spread_rej,distinct,longs,shorts,wins,gp,gl,net,stopx,holdx,endx

def metrics(idx,side,days,t,ask,bid):
    tr,bs,sr,nd,lg,sh,w,gp,gl,net,st,mh,en=evaluate(idx,side,days,t,ask,bid)
    m={"signals":int(idx.size),"busy_skips":int(bs),"spread_rejects":int(sr),"trades":int(tr),"distinct_days":int(nd),"long":int(lg),"short":int(sh),"official_wins":int(w),"gross_profit":round(float(gp),2),"gross_loss":round(float(gl),2),"direct_net_usd":round(float(net),2),"exit_reasons":{"STOP":int(st),"MAX_HOLD":int(mh),"END":int(en)}}
    g={"minimum_trades_20":tr>=20,"minimum_distinct_days_5":nd>=5,"nonnegative_direct_net":m["direct_net_usd"]>=0}
    g["screen_pass"]=bool(g["minimum_trades_20"] and g["minimum_distinct_days_5"] and g["nonnegative_direct_net"])
    return m,g

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--source",type=Path,required=True); ap.add_argument("--output",type=Path,required=True); args=ap.parse_args()
    source_sha=sha256_file(args.source)
    if source_sha!=CANONICAL_SHA: raise SystemExit("canonical January SHA mismatch: "+source_sha)
    d=pd.read_csv(args.source,compression="gzip",usecols=["timestamp_ms_utc","ask_raw","bid_raw"],dtype=np.int64)
    d=d[d.timestamp_ms_utc<END]; t=d.timestamp_ms_utc.to_numpy(np.int64)
    if len(t)!=4_205_709 or np.any(t[1:]<t[:-1]): raise SystemExit("Stage-A chronology/tick mismatch")
    ar=d.ask_raw.to_numpy(np.int64); br=d.bid_raw.to_numpy(np.int64)
    mid=quantize_mid(ar,br); ask,bid=p75_surface(t,ar,br)
    h1=make_bars(t,mid,3_600_000); h1["ema"]=ema(h1["close"].astype(np.float64),EMA_LEN)
    bars={60_000:make_bars(t,mid,60_000),300_000:make_bars(t,mid,300_000)}
    configs={}; survivors=[]
    for name,tf,use_htf in CONFIGS:
        idx,side,days,diag=signals_for_config(t,bars[tf],h1,use_htf)
        m,g=metrics(idx,side,days,t,ask,bid)
        configs[name]={"timeframe_ms":tf,"htf_bias":use_htf,"metrics":m,"gate":g,"event_diagnostics":diag}
        if g["screen_pass"]: survivors.append(name)
    out={
      "schema":"delta-r037-avpbr-stage-a-17bo-17bq-v1","status":"COMPLETE_FAST_CAUSAL_PRESCREEN",
      "unit":"R037_ACCUMULATION_VOLUME_PROFILE_BREAKOUT_RETEST_STAGE_A_SCREEN_CHECKPOINT_17BO_17BQ",
      "parent_checkpoint":"R037_PVACVD_FAILED_AUCTION_STAGE_A_SCREEN_CHECKPOINT_17BL_17BN",
      "prereg_commit":PREREG_COMMIT,"source_sha256":source_sha,"stage_a_ticks":int(len(t)),
      "signal_surface":"NATIVE_DUKAS_M1_M5_ACCUMULATION_PROFILE","execution_surface":"DUKAS_COINEXX_LIKE_P75",
      "numeric_retuning":False,"source_defaults_claimed":False,"august_accessed":False,
      "fixtures":{"atr_length":ATR_LEN,"lookback":LOOKBACK,"compression_multiple":COMP,"min_box_bars":MIN_BOX,"max_box_bars":MAX_BOX,"abandon_multiple":ABANDON,"profile_rows":ROWS,"value_area_fraction":VA_FRAC,"poc_zone_fraction":POC_ZONE_FRAC,"max_wait_bars":MAX_WAIT},
      "configs":configs,
      "finding":{"survivors":survivors,"decision":"ADVANCE_SURVIVORS_INDEPENDENT_LATER_JAN_VALIDATION" if survivors else "RETIRE_AVPBR_NO_STAGE_A_SURVIVOR","next":"R037_AVPBR_SURVIVOR_INDEPENDENT_LATER_JAN_VALIDATION" if survivors else "R037_NEXT_HIGH_VALUE_ENTRY_SOURCE_HARVEST"},
      "mql5_authorized":False
    }
    atomic_json(args.output,out)
    print(json.dumps({"configs":{k:{"signals":v["metrics"]["signals"],"trades":v["metrics"]["trades"],"days":v["metrics"]["distinct_days"],"wins":v["metrics"]["official_wins"],"net":v["metrics"]["direct_net_usd"],"pass":v["gate"]["screen_pass"],"diag":v["event_diagnostics"]} for k,v in configs.items()},"finding":out["finding"]},separators=(",",":")))

if __name__=="__main__": main()
