"""DELTA R037 full R032 specialist-parent parity reconstruction — Checkpoint 14A.

Bounded scheduler reconstruction only. Four specialist generators are frozen to their
best provenance-limited reconstructible surrogates. No generator or numeric threshold
is retuned. Only scheduler ordering between independent specialist signals and a fresh
ordinary R9 opportunity is tested.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path
import numpy as np
import pandas as pd
from numba import njit

import delta_r037_dh02_s08_cleanroom_parity as base
import delta_r037_dh02_s08_context_placement_parity as s08
import delta_r037_dh02_s11_armed_boundary_lifetime_rearm as s11
import delta_r037_dh03_s06_structure as d3struct
import delta_r037_dh03_s06_event_multiplicity_engine as d3engine
import delta_r037_dh05_conditional_failure_clock_challenger_replay as d5
import delta_r037_dh05_runtime_primitives as d5p
import delta_r037_r032_parent_backbone as parent
from research.delta.lab.coinexx_r9_adapter import _q_half_raw2_to_tick, _q_tick_raw, _session_2026

EVIDENCE_SCHEMA="delta-r037-r032-full-specialist-parent-parity-evidence-14a-v1"
CONFIGS=(("C00",1,1,0,0),("C01",1,1,1,0),("C02",1,1,0,1),("C03",1,1,1,1))
SCHEDULERS=("SPECIALIST_FIRST_FLAT_ONLY_CONFIG_ORDER","BACKBONE_FIRST_FLAT_ONLY_CONFIG_ORDER")
EXPECTED={"DH03_S06":1586,"DH05_S06":651,"DH02_S11":103,"DH02_S08":104}
SOURCE_NAMES=("ORDINARY","DH03_S06","DH05_S06","DH02_S11","DH02_S08")

def r2(x): return float(round(float(x),2))

@njit(cache=True)
def run_integrated(t,ask,bid,i250v,h1v,m30v,
                   d3t,d3s,d5t,d5s,s11t,s11s,s08t,s08s,
                   u3,u5,u11,u08,scheduler,price_scale=1000):
    tick=max(1,int(round(.01*price_scale))); half=int(round(.15*price_scale))
    stopd=int(round(.30*price_scale)); tact=int(round(.10*price_scale)); tdist=int(round(.03*price_scale))
    minrng=int(round(.50*price_scale)); mindisp=int(round(.15*price_scale))

    h=np.zeros(10,np.int64); l=np.zeros(10,np.int64); c=np.zeros(10,np.int64)
    scount=sptr=0; cursec=-1; sh=sl=sclose=0
    trs=np.zeros(14,np.int64); tcount=tptr=0; curm5=-1
    mh=ml=mclose=prevclose=0; haveprev=False
    minute=-1; cycle_buy=cycle_sell=0; pending=0; rearm=0
    pos=0; entry=stop=entrysec=0; had=False; last_side=0
    pos_owned=False; last_owned=False; pos_source=0
    p1=p2=p3=p4=0

    trades=raw_wins=official=losses=p01hits=m30hits=suppressed=ordinary_entries=0
    sentries=np.zeros(5,np.int64); swins=np.zeros(5,np.int64); snet=np.zeros(5,np.float64)
    gp=0.; gl=0.; bal=100000.; bpeak=bal; epeak=bal; maxbdd=0.; maxedd=0.; holdsum=0.

    for i in range(t.size):
        tm=np.int64(t[i]); a=np.int64(ask[i]); b=np.int64(bid[i]); sec=tm//1000

        av1=u3 and p1<d3t.size and d3t[p1]<=tm
        av2=u5 and p2<d5t.size and d5t[p2]<=tm
        av3=u11 and p3<s11t.size and s11t[p3]<=tm
        av4=u08 and p4<s08t.size and s08t[p4]<=tm
        sv1=int(d3s[p1]) if av1 else 0; sv2=int(d5s[p2]) if av2 else 0
        sv3=int(s11s[p3]) if av3 else 0; sv4=int(s08s[p4]) if av4 else 0

        # Protective stop first.
        exited_source=0
        if pos==1 and b<=stop:
            raw=(b-entry)/price_scale; deal=raw-.01; exited_source=pos_source
            if deal>1e-12:
                official+=1
                if pos_source>0: swins[pos_source]+=1
            if raw>0: gp+=deal; raw_wins+=1
            else: gl+=deal; losses+=1
            if pos_source>0: snet[pos_source]+=deal
            bal+=deal; trades+=1; holdsum+=sec-entrysec; pos=0; entry=stop=0
        elif pos==-1 and a>=stop:
            raw=(entry-a)/price_scale; deal=raw-.01; exited_source=pos_source
            if deal>1e-12:
                official+=1
                if pos_source>0: swins[pos_source]+=1
            if raw>0: gp+=deal; raw_wins+=1
            else: gl+=deal; losses+=1
            if pos_source>0: snet[pos_source]+=deal
            bal+=deal; trades+=1; holdsum+=sec-entrysec; pos=0; entry=stop=0

        # Completed-S1 ring.
        if cursec<0: cursec=sec; sh=sl=sclose=b
        elif sec!=cursec:
            h[sptr]=sh; l[sptr]=sl; c[sptr]=sclose; sptr=(sptr+1)%10; scount=min(10,scount+1)
            cursec=sec; sh=sl=sclose=b
        else:
            if b>sh: sh=b
            if b<sl: sl=b
            sclose=b

        disp=travel=rng=turns=0
        if scount==10:
            first=sptr; disp=c[(sptr+9)%10]-c[first]; maxh=h[first]; minl=l[first]; prev=c[first]; psign=0
            for k in range(1,10):
                q=(first+k)%10
                if h[q]>maxh: maxh=h[q]
                if l[q]<minl: minl=l[q]
                dd=c[q]-prev; travel+=abs(dd); sg=1 if dd>0 else -1 if dd<0 else 0
                if sg!=0:
                    if psign!=0 and sg!=psign: turns+=1
                    psign=sg
                prev=c[q]
            rng=maxh-minl
        eff=abs(disp)/travel if travel>0 else 0.

        # Completed-M5 ATR.
        m5=tm//300000
        if curm5<0: curm5=m5; mh=ml=mclose=b
        elif m5!=curm5:
            tr=mh-ml
            if haveprev: tr=max(tr,abs(mh-prevclose),abs(ml-prevclose))
            trs[tptr]=tr; tptr=(tptr+1)%14; tcount=min(14,tcount+1)
            prevclose=mclose; haveprev=True; curm5=m5; mh=ml=mclose=b
        else:
            if b>mh: mh=b
            if b<ml: ml=b
            mclose=b
        atrsum=0
        if tcount==14:
            for k in range(14): atrsum+=trs[k]
        sess=_session_2026(tm); floorp=2.5 if sess==0 else 2.0 if sess==1 else 1.75
        gate=tcount==14 and (a-b)<=25*tick and atrsum>=14*int(round(floorp*price_scale))

        mi=tm//60000
        if mi!=minute:
            minute=mi; pending=2; rearm=0
            cycle_buy=_q_half_raw2_to_tick(b+a+2*half,tick)
            cycle_sell=_q_half_raw2_to_tick(b+a-2*half,tick)

        if pos!=0:
            had=True; last_side=pos; last_owned=pos_owned
            if sec-entrysec>=30:
                raw=((b-entry) if pos==1 else (entry-a))/price_scale; deal=raw-.01
                if deal>1e-12:
                    official+=1
                    if pos_source>0: swins[pos_source]+=1
                if raw>0: gp+=deal; raw_wins+=1
                else: gl+=deal; losses+=1
                if pos_source>0: snet[pos_source]+=deal
                bal+=deal; trades+=1; holdsum+=sec-entrysec; pos=0; entry=stop=0
            else:
                fav=(b-entry) if pos==1 else (entry-a)
                if fav>=tact:
                    ns=_q_tick_raw(b-tdist if pos==1 else a+tdist,tick)
                    if (pos==1 and ns>stop) or (pos==-1 and ns<stop): stop=ns
        elif had:
            pending=0
            if last_owned: suppressed+=1
            had=False; last_side=0; last_owned=False
        else:
            spec=0; sside=0
            if av1: spec=1; sside=sv1
            elif av2: spec=2; sside=sv2
            elif av3: spec=3; sside=sv3
            elif av4: spec=4; sside=sv4
            opened=False

            if scheduler==0 and spec:
                pos=sside; pos_source=spec; pos_owned=True
                entry=a if pos==1 else b; entrysec=sec
                stop=_q_tick_raw(b-stopd if pos==1 else a+stopd,tick)
                pending=0; bal-=.01; gl-=.01; sentries[spec]+=1; snet[spec]-=.01; opened=True

            if (not opened) and gate:
                common=eff>.70 and rng>=minrng and turns<=9; intended=0
                if pending in (1,2) and a>=cycle_buy and common and disp>=mindisp: intended=1
                elif pending in (-1,2) and b<=cycle_sell and common and disp<=-mindisp: intended=-1
                if intended:
                    ii=float(i250v[i])*intended; hh=float(h1v[i])*intended; mm=float(m30v[i])*intended
                    p01=(ii<=-.55) or (not np.isnan(hh) and hh>.35)
                    m30only=(not p01) and (not np.isnan(mm)) and mm>.35
                    actual=-intended if p01 else intended; owned=p01 or m30only
                    if p01: p01hits+=1
                    if m30only: m30hits+=1
                    pos=actual; pos_source=0; pos_owned=owned
                    entry=a if pos==1 else b; entrysec=sec
                    stop=_q_tick_raw(b-stopd if pos==1 else a+stopd,tick)
                    pending=0; bal-=.01; gl-=.01; ordinary_entries+=1; opened=True

            if scheduler==1 and (not opened) and spec:
                pos=sside; pos_source=spec; pos_owned=True
                entry=a if pos==1 else b; entrysec=sec
                stop=_q_tick_raw(b-stopd if pos==1 else a+stopd,tick)
                pending=0; bal-=.01; gl-=.01; sentries[spec]+=1; snet[spec]-=.01

        # Never queue a specialist signal beyond its first causally visible tick.
        while p1<d3t.size and d3t[p1]<=tm: p1+=1
        while p2<d5t.size and d5t[p2]<=tm: p2+=1
        while p3<s11t.size and s11t[p3]<=tm: p3+=1
        while p4<s08t.size and s08t[p4]<=tm: p4+=1

        bpeak=max(bpeak,bal); maxbdd=max(maxbdd,bpeak-bal)
        equity=bal+(b-entry)/price_scale if pos==1 else bal+(entry-a)/price_scale if pos==-1 else bal
        epeak=max(epeak,equity); maxedd=max(maxedd,epeak-equity)

    ints=np.array([trades,raw_wins,official,losses,p01hits,m30hits,suppressed,ordinary_entries],np.int64)
    flt=np.array([gp,gl,gp+gl,maxbdd,maxedd,holdsum/trades if trades else 0.],np.float64)
    return ints,flt,sentries,swins,snet

def generate_streams(t,ask,bid):
    mid=ask+bid
    b1=base.bars(t,mid,1000); b5=base.bars(t,mid,5000); b15=base.bars(t,mid,15000)
    bm1=base.bars(t,mid,60000); bm5=base.bars(t,mid,300000)
    bm15=base.bars(t,mid,900000); bm30=base.bars(t,mid,1800000)
    bh1=base.bars(t,mid,3600000); bh4=base.bars(t,mid,14400000)

    b30=base.bars(t,mid,30000)
    e5=base.signed_eff(b5,4); e15=base.signed_eff(b15,4); e30=base.signed_eff(b30,4); a5=base.atr14(bm5)
    pe3,ps3,_,li3,si3=d3struct.parent_series(bm15,bm30)
    phi,plo,pht,plt=d3struct.latest_fast_pivots(b15)
    d3t,d3s,_,_=d3engine.detect(t,mid,b5["end_ms"],b5["close"],e5,
        b15["end_ms"],b15["high"],b15["low"],b15["close"],e15,b30["end_ms"],e30,
        bm5["end_ms"],a5,pe3,ps3,li3,si3,phi,plo,pht,plt,0,1)

    q1=d5p.bars(t,mid,1000); q5=d5p.bars(t,mid,5000); q15=d5p.bars(t,mid,15000); q300=d5p.bars(t,mid,300000)
    a1=d5p.atr14(q1); qa5=d5p.atr14(q5); a300=d5p.atr14(q300); swt,sws,swl=d5p.symmetric_swings(q300,2)
    v=next(x for x in d5p.VECTORS if x[0]=="S06"); _,ad,at,mf,mp,pex,rb,rd,em,rt=v
    _,d5i,d5s,ov=d5.detect_clock_router(t,mid,swt,sws,swl,q300["end_ms"],a300,
        q1["end_ms"],q1["open"],q1["close"],a1,q5["end_ms"],q5["open"],q5["close"],qa5,
        q15["end_ms"],q15["open"],q15["close"],ad,at,int(mf*1000),int(mp*1000),pex,rb,rd,em,rt,0)
    if ov: raise SystemExit("DH05-S06 signal overflow")
    d5t=t[d5i]

    s15atr=s11.atr14(b15); s5eff=s11.signed_eff(b5,4); xst,xss,xsl,xid=s11.symmetric_swings(bm5,2)
    d15=s11.directional_label(bm15,3,.3,.3); d30=s11.directional_label(bm30,3,.3,.3)
    dh1=s11.directional_label(bh1,3,.3,.3); dh4=s11.directional_label(bh4,3,.3,.3)
    s11t,s11s,_,_=s11.generate_signals(t,mid,xst,xss,xsl,xid,b1["end_ms"],b1["close"],
        b5["end_ms"],b5["close"],s5eff,b15["end_ms"],s15atr,bm15["end_ms"],d15,
        bm30["end_ms"],d30,bh1["end_ms"],dh1,bh4["end_ms"],dh4,1)

    s08atr=base.atr14(b15); s1eff=base.signed_eff(b1,4); yst,yss,ysl,yid=base.symmetric_swings(bm1,2)
    bd15=base.directional_label(bm15,3,.3,.3); bd30=base.directional_label(bm30,3,.3,.3); bdh1=base.directional_label(bh1,3,.3,.3)
    pe8,praw8,_=base.parent_direction_series(bm15["end_ms"],bd15,bm30["end_ms"],bd30,bh1["end_ms"],bdh1)
    s08t,s08s,_,_=s08.generate_signals(t,mid,yst,yss,ysl,yid,b1["end_ms"],b1["close"],s1eff,
        b5["end_ms"],b5["close"],b15["end_ms"],s08atr,pe8,praw8,2)

    out={"DH03_S06":(d3t.astype(np.int64),d3s.astype(np.int8)),
         "DH05_S06":(d5t.astype(np.int64),d5s.astype(np.int8)),
         "DH02_S11":(s11t.astype(np.int64),s11s.astype(np.int8)),
         "DH02_S08":(s08t.astype(np.int64),s08s.astype(np.int8))}
    for k,vv in out.items():
        if int(vv[0].size)!=EXPECTED[k]: raise SystemExit(f"{k} signal fingerprint mismatch: {vv[0].size} != {EXPECTED[k]}")
    return out

def pack(ret):
    ints,flt,ent,sw,snet=ret; src={}
    for i in range(1,5):
        src[SOURCE_NAMES[i]]={"entries":int(ent[i]),"official_wins":int(sw[i]),"net_profit":r2(snet[i])}
    return {"trades":int(ints[0]),"raw_positive_wins":int(ints[1]),"official_wins":int(ints[2]),
        "losses":int(ints[3]),"p01_hits":int(ints[4]),"m30_only_hits":int(ints[5]),
        "owned_exit_suppressed_rearms":int(ints[6]),"ordinary_entries":int(ints[7]),
        "gross_profit":r2(flt[0]),"gross_loss":r2(flt[1]),"net_profit":r2(flt[2]),
        "max_balance_drawdown":r2(flt[3]),"max_equity_drawdown":r2(flt[4]),
        "average_hold_seconds":float(flt[5]),"specialist_entries":int(np.sum(ent[1:])),
        "specialist_net":r2(np.sum(snet[1:])), "sources":src}

def err(a,t):
    return {"trades":abs(a["trades"]-t["trades"]),"official_wins":abs(a["official_wins"]-t["official_wins"]),
        "net_profit":abs(a["net_profit"]-t["net_profit"]),"specialist_entries":abs(a["specialist_entries"]-t["specialist_entries"]),
        "specialist_net":abs(a["specialist_net"]-t["specialist_net"])}

def score(e): return float(200*e["specialist_entries"]+100*e["trades"]+50*e["official_wins"]+e["net_profit"]+e["specialist_net"])

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--source",type=Path,required=True)
    ap.add_argument("--evidence",type=Path,required=True); ap.add_argument("--output",type=Path,required=True); a=ap.parse_args()
    ev=json.loads(a.evidence.read_text())
    if ev.get("schema")!=EVIDENCE_SCHEMA: raise SystemExit("14A evidence schema mismatch")
    sha=base.sha256_file(a.source)
    if sha!=base.CANONICAL_JAN_SHA256: raise SystemExit("canonical January SHA mismatch: "+sha)
    df=pd.read_csv(a.source,compression="gzip",usecols=["timestamp_ms_utc","ask_raw","bid_raw"],dtype=np.int64)
    df=df[df.timestamp_ms_utc<base.STAGE_A_END_MS]; t=df.timestamp_ms_utc.to_numpy(np.int64)
    if t.size!=4205709: raise SystemExit(f"Stage-A tick mismatch: {t.size}")
    if t.size and np.any(t[1:]<t[:-1]): raise SystemExit("non-monotonic Stage-A ticks")
    ask,bid=base.p75(t,df.ask_raw.to_numpy(np.int64),df.bid_raw.to_numpy(np.int64))
    feat=parent.build_parent_features(t,ask,bid); streams=generate_streams(t,ask,bid)
    zt=np.empty(0,np.int64); zs=np.empty(0,np.int8)
    ctrl=pack(run_integrated(t,ask,bid,feat["impulse250"],feat["h1_netatr"],feat["m30_netatr"],
        zt,zs,zt,zs,zt,zs,zt,zs,0,0,0,0,0))
    b=ev["exact_backbone"]
    if not (ctrl["trades"]==b["trades"] and ctrl["official_wins"]==b["official_wins"] and
            abs(ctrl["gross_profit"]-b["gross_profit"])<.011 and abs(ctrl["gross_loss"]-b["gross_loss"])<.011 and
            abs(ctrl["net_profit"]-b["net_profit"])<.011):
        raise SystemExit("integrated no-specialist backbone parity gate failed: "+json.dumps(ctrl,sort_keys=True))

    d3t,d3s=streams["DH03_S06"]; d5t,d5s=streams["DH05_S06"]; a11,a11s=streams["DH02_S11"]; a08,a08s=streams["DH02_S08"]
    results={}; rank=[]; targets=ev["historical_p75_targets"]
    for si,sname in enumerate(SCHEDULERS):
        cfg={}; joint=0.
        for cname,u3,u5,u11,u08 in CONFIGS:
            actual=pack(run_integrated(t,ask,bid,feat["impulse250"],feat["h1_netatr"],feat["m30_netatr"],
                d3t,d3s,d5t,d5s,a11,a11s,a08,a08s,u3,u5,u11,u08,si))
            ee=err(actual,targets[cname]); sc=score(ee); joint+=sc
            cfg[cname]={"actual":actual,"target":targets[cname],"abs_error":ee,"parity_score":sc}
        c0=cfg["C00"]["actual"]; c1=cfg["C01"]["actual"]; c2=cfg["C02"]["actual"]; c3=cfg["C03"]["actual"]
        inc={"c01_s11_incremental_specialist_entries":c1["specialist_entries"]-c0["specialist_entries"],
             "c02_s08_incremental_specialist_entries":c2["specialist_entries"]-c0["specialist_entries"],
             "c03_increment_vs_c00":c3["specialist_entries"]-c0["specialist_entries"]}
        it=ev["ownership_fingerprints"]; ie=sum(abs(inc[k]-it[k]) for k in inc); joint+=500*ie
        results[sname]={"configs":cfg,"ownership_increments":inc,"ownership_increment_abs_error_sum":int(ie),"joint_parity_score":float(joint)}
        rank.append((joint,sname))
    rank.sort(); lead=rank[0][1]; lr=results[lead]; exact=True
    for cname in ("C00","C01","C02","C03"):
        ee=lr["configs"][cname]["abs_error"]
        if ee["trades"] or ee["official_wins"] or ee["specialist_entries"] or ee["net_profit"]>=.011 or ee["specialist_net"]>=.011: exact=False
    out={"schema":"delta-r037-r032-full-specialist-parent-parity-14a-v1",
         "status":"COMPLETE_EXACT_PARENT_PARITY" if exact else "COMPLETE_SCHEDULER_LOCALIZATION_FULL_PARENT_PARITY_NOT_ACHIEVED",
         "unit":ev["unit"],"parent_checkpoint":ev["parent_checkpoint"],"source_sha256":sha,
         "stage_a_ticks":int(t.size),"surface":ev["surface"],"numeric_retuning":False,"august_accessed":False,
         "backbone_control":ctrl,"signal_fingerprints":{k:int(v[0].size) for k,v in streams.items()},
         "scheduler_results":results,"ranking":[n for _,n in rank],
         "finding":{"leading_scheduler":lead,"exact_historical_parent_parity":exact,
                    "ownership_increment_abs_error_sum":lr["ownership_increment_abs_error_sum"],
                    "next":ev["next_if_scheduler_localized"]},
         "sorb_integrated_replay_started":False,"mql5_authorized":False}
    base.atomic_write_json(a.output,out); print(json.dumps(out["finding"],separators=(",",":")))

if __name__=="__main__": main()
