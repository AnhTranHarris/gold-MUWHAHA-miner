"""R037 Sweep->FVG->IFVG->retest Stage-A screen 17BX-17BY.

Source-anchored clean-room approximation. Two fixed lanes only: M1 and M5.
No parameter sweep, no August, no MQL5.
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
P75=np.asarray([20,20,21,21],np.int64)
SHA="d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5"
PREREG="8ce37fe1d54fddf62145e4edfa699deab4d1b79f"

EXTREME_LOOKBACK=50
SWEEP_VALID=50
MIN_GAP_RAW=30*TICK
INVERSION_GRACE=50
RETEST_VALID=50

MAX_SPREAD=250; STOP=300; TRAIL_ACT=100; TRAIL_DIST=30; MAX_HOLD=30

def sha256_file(p:Path)->str:
    h=hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda:f.read(1<<20),b""): h.update(b)
    return h.hexdigest()

def atomic_json(p:Path,obj:dict)->None:
    p.parent.mkdir(parents=True,exist_ok=True); tmp=None
    try:
        with tempfile.NamedTemporaryFile("w",encoding="utf-8",newline="\n",dir=p.parent,
                                         prefix="."+p.name+".",suffix=".tmp",delete=False) as f:
            tmp=f.name; json.dump(obj,f,indent=2); f.write("\n"); f.flush(); os.fsync(f.fileno())
        os.replace(tmp,p); tmp=None
    finally:
        if tmp:
            try: os.unlink(tmp)
            except FileNotFoundError: pass

def session_code(t):
    tod=t%DAY
    ls=np.where(t>=UK_DST,7,8)*HOUR; le=ls+30_600_000
    ns=np.where(t>=US_DST,12,13)*HOUR; ne=ns+32_400_000
    il=(tod>=ls)&(tod<le); iny=(tod>=ns)&(tod<ne)
    return np.where(il&iny,2,np.where(il,1,np.where(iny,3,0))).astype(np.int8)

def p75_surface(t,a,b):
    sp=P75[session_code(t)]*TICK
    m2=a.astype(np.int64)+b.astype(np.int64)
    bid=((m2-sp+TICK)//(2*TICK))*TICK
    return (bid+sp).astype(np.int64),bid.astype(np.int64)

def bars(t,a,b,tf):
    mid=(a.astype(np.int64)+b.astype(np.int64))//2
    mid=((mid+5)//10)*10
    buck=t//tf
    st=np.r_[0,np.flatnonzero(buck[1:]!=buck[:-1])+1]
    en=np.r_[st[1:],len(t)]
    return {
        "end":((buck[st]+1)*tf).astype(np.int64),
        "o":mid[st].astype(np.int64),
        "h":np.maximum.reduceat(mid,st).astype(np.int64),
        "l":np.minimum.reduceat(mid,st).astype(np.int64),
        "c":mid[en-1].astype(np.int64),
    }

def lane_signals(t,b,tf):
    e,o,h,l,c=b["end"],b["o"],b["h"],b["l"],b["c"]
    n=len(c)
    latest_hi=None; latest_lo=None
    hi_live=False; lo_live=False
    seq={1:None,-1:None}
    idx=[]; side=[]; days=[]
    d={
        "bars":n,"confirmed_extreme_highs":0,"confirmed_extreme_lows":0,
        "buyside_sweeps":0,"sellside_sweeps":0,
        "candidate_bull_fvg":0,"candidate_bear_fvg":0,
        "inversions_bullish":0,"inversions_bearish":0,
        "retests_bullish":0,"retests_bearish":0,
        "sweep_expired":0,"candidate_expired":0,"retest_expired":0
    }

    def new_seq(reaction,sweep_i):
        return {"reaction":reaction,"sweep_i":sweep_i,"fvg_i":None,
                "lo":None,"hi":None,"inv_i":None,"idir":None}

    for i in range(2,n):
        # A 3-candle swing centered at i-1 becomes knowable only when bar i closes.
        k=i-1
        if k>=1:
            ph=int(h[k])>int(h[k-1]) and int(h[k])>int(h[k+1])
            pl=int(l[k])<int(l[k-1]) and int(l[k])<int(l[k+1])
            left=max(0,k-EXTREME_LOOKBACK+1)
            if ph and int(h[k])>=int(np.max(h[left:k+1])):
                latest_hi=int(h[k]); hi_live=True; d["confirmed_extreme_highs"]+=1
            if pl and int(l[k])<=int(np.min(l[left:k+1])):
                latest_lo=int(l[k]); lo_live=True; d["confirmed_extreme_lows"]+=1

        # Sweep consumes the currently eligible liquidity level and supersedes
        # any unfinished sequence in the same implied reaction direction.
        if hi_live and latest_hi is not None and int(h[i])>latest_hi and int(c[i])<latest_hi:
            seq[-1]=new_seq(-1,i); hi_live=False; d["buyside_sweeps"]+=1
        if lo_live and latest_lo is not None and int(l[i])<latest_lo and int(c[i])>latest_lo:
            seq[1]=new_seq(1,i); lo_live=False; d["sellside_sweeps"]+=1

        # Process bullish-reaction and bearish-reaction sequences independently.
        for reaction in (1,-1):
            s=seq[reaction]
            if s is None: continue

            if s["fvg_i"] is None:
                if i-s["sweep_i"]>SWEEP_VALID:
                    seq[reaction]=None; d["sweep_expired"]+=1; continue
                # Require consecutive chart bars so weekend/session discontinuities
                # cannot manufacture an imbalance.
                if i<2 or int(e[i]-e[i-1])!=tf or int(e[i-1]-e[i-2])!=tf:
                    continue
                if reaction==1:
                    gap=int(l[i])-int(h[i-2])
                    if gap>=MIN_GAP_RAW:
                        s["fvg_i"]=i; s["lo"]=int(h[i-2]); s["hi"]=int(l[i]); d["candidate_bull_fvg"]+=1
                else:
                    gap=int(l[i-2])-int(h[i])
                    if gap>=MIN_GAP_RAW:
                        s["fvg_i"]=i; s["lo"]=int(h[i]); s["hi"]=int(l[i-2]); d["candidate_bear_fvg"]+=1
                continue

            if s["inv_i"] is None:
                if i-s["fvg_i"]>INVERSION_GRACE:
                    seq[reaction]=None; d["candidate_expired"]+=1; continue
                # Clean body crossing through the far side; wick-only probes do not invert.
                if reaction==1:
                    if int(o[i])>=s["lo"] and int(c[i])<s["lo"]:
                        s["inv_i"]=i; s["idir"]=-1; d["inversions_bearish"]+=1
                else:
                    if int(o[i])<=s["hi"] and int(c[i])>s["hi"]:
                        s["inv_i"]=i; s["idir"]=1; d["inversions_bullish"]+=1
                continue

            if i<=s["inv_i"]: continue
            if i-s["inv_i"]>RETEST_VALID:
                seq[reaction]=None; d["retest_expired"]+=1; continue

            overlap=int(h[i])>=s["lo"] and int(l[i])<=s["hi"]
            if not overlap: continue

            idir=s["idir"]
            ok=False
            if idir==-1:
                ok=int(c[i])<s["lo"] and int(c[i])<int(o[i])
            else:
                ok=int(c[i])>s["hi"] and int(c[i])>int(o[i])
            if ok:
                j=int(np.searchsorted(t,int(e[i]),side="left"))
                if j<len(t):
                    idx.append(j); side.append(idir); days.append((int(e[i])-1)//DAY)
                    if idir>0:d["retests_bullish"]+=1
                    else:d["retests_bearish"]+=1
                seq[reaction]=None

    return np.asarray(idx,np.int64),np.asarray(side,np.int8),np.asarray(days,np.int64),d

@njit(cache=True)
def qt(x): return ((int(x)+5)//10)*10

@njit(cache=True)
def evaluate(idx,side,days,t,ask,bid):
    busy=-1;tr=bs=sr=nd=lg=sh=w=0;gp=gl=net=0.;st=mh=en=0;u=0
    used=np.empty(idx.size,np.int64)
    for z in range(idx.size):
        i=int(idx[z]); s=int(side[z])
        if i<=busy: bs+=1; continue
        if int(ask[i]-bid[i])>MAX_SPREAD: sr+=1; continue
        tr+=1; lg+=s>0; sh+=s<0; used[u]=days[z]; u+=1
        entry=int(ask[i]) if s>0 else int(bid[i])
        stop=qt(int(bid[i])-STOP if s>0 else int(ask[i])+STOP)
        sec0=int(t[i])//1000; raw=0.; reason=2; last=i
        for k in range(i+1,t.size):
            aa=int(ask[k]); bb=int(bid[k]); last=k
            if s>0 and bb<=stop: raw=(bb-entry)/SCALE; reason=0; break
            if s<0 and aa>=stop: raw=(entry-aa)/SCALE; reason=0; break
            if int(t[k])//1000-sec0>=MAX_HOLD:
                raw=((bb-entry) if s>0 else (entry-aa))/SCALE; reason=1; break
            fav=(bb-entry) if s>0 else (entry-aa)
            if fav>=TRAIL_ACT:
                ns=qt(bb-TRAIL_DIST if s>0 else aa+TRAIL_DIST)
                if (s>0 and ns>stop) or (s<0 and ns<stop): stop=ns
        ex=raw-.01; net+=ex-.01; w+=ex>1e-12
        if raw>0: gp+=ex
        else: gl+=ex
        if reason==0: st+=1
        elif reason==1: mh+=1
        else: en+=1
        busy=last
    if u:
        x=np.sort(used[:u]); nd=1
        for k in range(1,x.size): nd+=x[k]!=x[k-1]
    return tr,bs,sr,nd,lg,sh,w,gp,gl,net,st,mh,en

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--source",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    a=ap.parse_args()

    hs=sha256_file(a.source)
    if hs!=SHA: raise SystemExit("canonical January SHA mismatch: "+hs)

    d=pd.read_csv(a.source,compression="gzip",
                  usecols=["timestamp_ms_utc","ask_raw","bid_raw"],dtype=np.int64)
    d=d[d.timestamp_ms_utc<END]
    t=d.timestamp_ms_utc.to_numpy(np.int64)
    if len(t)!=4_205_709 or np.any(t[1:]<t[:-1]):
        raise SystemExit("Stage-A chronology/tick mismatch")

    ar=d.ask_raw.to_numpy(np.int64); br=d.bid_raw.to_numpy(np.int64)
    ask,bid=p75_surface(t,ar,br)
    configs={}
    for name,tf in (("17BX_M1_SWEEP_IFVG_RETEST",60_000),("17BY_M5_SWEEP_IFVG_RETEST",300_000)):
        ix,sd,dy,diag=lane_signals(t,bars(t,ar,br,tf),tf)
        q=evaluate(ix,sd,dy,t,ask,bid)
        m={"signals":int(ix.size),"busy_skips":int(q[1]),"spread_rejects":int(q[2]),
           "trades":int(q[0]),"distinct_days":int(q[3]),"long":int(q[4]),"short":int(q[5]),
           "official_wins":int(q[6]),"gross_profit":round(float(q[7]),2),
           "gross_loss":round(float(q[8]),2),"direct_net_usd":round(float(q[9]),2),
           "exit_reasons":{"STOP":int(q[10]),"MAX_HOLD":int(q[11]),"END":int(q[12])}}
        gate={"minimum_trades_20":m["trades"]>=20,
              "minimum_distinct_days_5":m["distinct_days"]>=5,
              "nonnegative_direct_net":m["direct_net_usd"]>=0}
        gate["screen_pass"]=all(gate.values())
        configs[name]={"timeframe_ms":tf,"metrics":m,"gate":gate,"diagnostics":diag}

    survivors=[k for k,v in configs.items() if v["gate"]["screen_pass"]]
    out={
      "schema":"delta-r037-sweep-ifvg-retest-stage-a-17bx-17by-v1",
      "status":"COMPLETE_FAST_CAUSAL_PRESCREEN",
      "unit":"R037_SWEEP_IFVG_RETEST_STAGE_A_SCREEN_CHECKPOINT_17BX_17BY",
      "family":"R037-SIFVG-v1",
      "parent_checkpoint":"R037_FIB_GOLDEN_POCKET_IMPULSE_RETRACE_STAGE_A_SCREEN_CHECKPOINT_17BW",
      "prereg_commit":PREREG,
      "source_sha256":hs,"stage_a_ticks":int(len(t)),
      "signal_surface":"NATIVE_DUKAS_COMPLETED_BAR_MID",
      "execution_surface":"DUKAS_COINEXX_LIKE_P75",
      "source_anchored_defaults":{"extreme_lookback_bars":EXTREME_LOOKBACK,
          "sweep_validity_bars":SWEEP_VALID,"minimum_gap_ticks":30},
      "fixed_cleanroom_approximations":{"inversion_grace_bars":INVERSION_GRACE,
          "retest_validity_bars":RETEST_VALID},
      "configs":configs,
      "finding":{"survivors":survivors,
          "decision":"ADVANCE_SIFVG_SURVIVOR" if survivors else "RETIRE_SIFVG_NO_STAGE_A_SURVIVOR",
          "next":"R037_SWEEP_IFVG_INDEPENDENT_LATER_JAN_VALIDATION" if survivors else "R037_NEXT_HIGH_VALUE_ENTRY_SOURCE_HARVEST"},
      "numeric_retuning":False,"august_accessed":False,"mql5_authorized":False
    }
    atomic_json(a.output,out)
    compact={k:{"trades":v["metrics"]["trades"],"days":v["metrics"]["distinct_days"],
                "wins":v["metrics"]["official_wins"],"net":v["metrics"]["direct_net_usd"],
                "pass":v["gate"]["screen_pass"]} for k,v in configs.items()}
    print(json.dumps({"configs":compact,"finding":out["finding"]},separators=(",",":")))

if __name__=="__main__":
    main()
