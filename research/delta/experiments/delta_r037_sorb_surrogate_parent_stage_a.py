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
import delta_r037_sorb as sorb
import delta_r037_r032_parent_backbone as parent
from research.delta.lab.coinexx_r9_adapter import _q_half_raw2_to_tick, _q_tick_raw, _session_2026

EVIDENCE_SCHEMA="delta-r037-r032-full-specialist-parent-parity-evidence-14a-v1"
CONFIGS=(("C00",1,1,0,0),("C01",1,1,1,0),("C02",1,1,0,1),("C03",1,1,1,1))
SCHEDULERS=("SPECIALIST_FIRST_FLAT_ONLY_CONFIG_ORDER","BACKBONE_FIRST_FLAT_ONLY_CONFIG_ORDER")
EXPECTED={"DH03_S06":1586,"DH05_S06":651,"DH02_S11":103,"DH02_S08":104}
SOURCE_NAMES=("ORDINARY","DH03_S06","DH05_S06","DH02_S11","DH02_S08")

def r2(x): return float(round(float(x),2))

@njit(cache=True)
def run_integrated_sorb(t,ask,bid,i250v,h1v,m30v,
                   d3t,d3s,d5t,d5s,s11t,s11s,s08t,s08s,
                   sorbi,sorbs,sorbsess,u3,u5,u11,u08,scheduler,price_scale=1000):
    tick=max(1,int(round(.01*price_scale))); half=int(round(.15*price_scale))
    stopd=int(round(.30*price_scale)); tact=int(round(.10*price_scale)); tdist=int(round(.03*price_scale))
    minrng=int(round(.50*price_scale)); mindisp=int(round(.15*price_scale))

    h=np.zeros(10,np.int64); l=np.zeros(10,np.int64); c=np.zeros(10,np.int64)
    scount=sptr=0; cursec=-1; sh=sl=sclose=0
    trs=np.zeros(14,np.int64); tcount=tptr=0; curm5=-1
    mh=ml=mclose=prevclose=0; haveprev=False
    minute=-1; cycle_buy=cycle_sell=0; pending=0; rearm=0
    pos=0; entry=stop=entrysec=0; had=False; last_side=0
    pos_owned=False; last_owned=False; pos_source=0; pos_sess=0
    p1=p2=p3=p4=p5=0

    trades=raw_wins=official=losses=p01hits=m30hits=suppressed=ordinary_entries=0
    sentries=np.zeros(6,np.int64); swins=np.zeros(6,np.int64); snet=np.zeros(6,np.float64)
    gp=0.; gl=0.; bal=100000.; bpeak=bal; epeak=bal; maxbdd=0.; maxedd=0.; holdsum=0.
    outcomes=np.zeros(sorbi.size,np.int8); sess_ent=np.zeros(3,np.int64); sess_win=np.zeros(3,np.int64); sess_net=np.zeros(3,np.float64)

    for i in range(t.size):
        tm=np.int64(t[i]); a=np.int64(ask[i]); b=np.int64(bid[i]); sec=tm//1000
        occupied_start=pos!=0; sorb_evt=p5<sorbi.size and sorbi[p5]==i

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
            if pos_source==5 and pos_sess>0:
                sess_net[pos_sess]+=deal
                if deal>1e-12: sess_win[pos_sess]+=1
            bal+=deal; trades+=1; holdsum+=sec-entrysec; pos=0; entry=stop=0; pos_sess=0
        elif pos==-1 and a>=stop:
            raw=(entry-a)/price_scale; deal=raw-.01; exited_source=pos_source
            if deal>1e-12:
                official+=1
                if pos_source>0: swins[pos_source]+=1
            if raw>0: gp+=deal; raw_wins+=1
            else: gl+=deal; losses+=1
            if pos_source>0: snet[pos_source]+=deal
            if pos_source==5 and pos_sess>0:
                sess_net[pos_sess]+=deal
                if deal>1e-12: sess_win[pos_sess]+=1
            bal+=deal; trades+=1; holdsum+=sec-entrysec; pos=0; entry=stop=0; pos_sess=0

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
            if pos_source!=5:
                had=True; last_side=pos; last_owned=pos_owned
            else:
                had=False; last_side=0; last_owned=False
            if sec-entrysec>=30:
                raw=((b-entry) if pos==1 else (entry-a))/price_scale; deal=raw-.01
                if deal>1e-12:
                    official+=1
                    if pos_source>0: swins[pos_source]+=1
                if raw>0: gp+=deal; raw_wins+=1
                else: gl+=deal; losses+=1
                if pos_source>0: snet[pos_source]+=deal
            if pos_source==5 and pos_sess>0:
                sess_net[pos_sess]+=deal
                if deal>1e-12: sess_win[pos_sess]+=1
                bal+=deal; trades+=1; holdsum+=sec-entrysec; pos=0; entry=stop=0; pos_sess=0
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

        if sorb_evt:
            if occupied_start:
                outcomes[p5]=2
            elif pos!=0:
                outcomes[p5]=3
            else:
                pos=int(sorbs[p5]); pos_source=5; pos_owned=False; pos_sess=int(sorbsess[p5])
                entry=a if pos==1 else b; entrysec=sec
                stop=_q_tick_raw(b-stopd if pos==1 else a+stopd,tick)
                bal-=.01; gl-=.01; sentries[5]+=1; snet[5]-=.01
                if pos_sess>0: sess_ent[pos_sess]+=1; sess_net[pos_sess]-=.01
                outcomes[p5]=1
            p5+=1

        bpeak=max(bpeak,bal); maxbdd=max(maxbdd,bpeak-bal)
        equity=bal+(b-entry)/price_scale if pos==1 else bal+(entry-a)/price_scale if pos==-1 else bal
        epeak=max(epeak,equity); maxedd=max(maxedd,epeak-equity)

    ints=np.array([trades,raw_wins,official,losses,p01hits,m30hits,suppressed,ordinary_entries],np.int64)
    flt=np.array([gp,gl,gp+gl,maxbdd,maxedd,holdsum/trades if trades else 0.],np.float64)
    return ints,flt,sentries,swins,snet,outcomes,sess_ent,sess_win,sess_net

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

SOURCE_NAMES=("ORDINARY","DH03_S06","DH05_S06","DH02_S11","DH02_S08","SORB")
CONFIG_ORDER=("R037-C01_LONDON_15","R037-C02_COMEX_15","R037-C03_DUAL_15","R037-C04_DUAL_30","R037-C05_DUAL_15_CONFIRM2")
PARENT_EXPECTED={"trades":14034,"raw_positive_wins":6422,"official_wins":6349,"ordinary_entries":11916,"parent_specialist_entries":2118,"gross_profit":1357.26,"gross_loss":-4302.20,"net_profit":-2944.94,"max_balance_drawdown":2945.93,"max_equity_drawdown":2946.43}

def pack_sorb(ret):
    ints,flt,ent,sw,snet,outcomes,se,sv,sn=ret; src={}
    for i in range(1,6):
        src[SOURCE_NAMES[i]]={"entries":int(ent[i]),"official_wins":int(sw[i]),"net_profit":r2(snet[i])}
    return {"trades":int(ints[0]),"raw_positive_wins":int(ints[1]),"official_wins":int(ints[2]),"losses":int(ints[3]),
        "p01_hits":int(ints[4]),"m30_only_hits":int(ints[5]),"owned_exit_suppressed_rearms":int(ints[6]),"ordinary_entries":int(ints[7]),
        "gross_profit":r2(flt[0]),"gross_loss":r2(flt[1]),"net_profit":r2(flt[2]),"max_balance_drawdown":r2(flt[3]),"max_equity_drawdown":r2(flt[4]),
        "average_hold_seconds":float(flt[5]),"parent_specialist_entries":int(np.sum(ent[1:5])),"sorb_entries":int(ent[5]),
        "parent_specialist_net":r2(np.sum(snet[1:5])),"sorb_net":r2(snet[5]),"sources":src,
        "sorb_outcomes":{"ACCEPTED":int(np.sum(outcomes==1)),"POSITION_BLOCKED":int(np.sum(outcomes==2)),"PARENT_SAME_TICK_COLLISION":int(np.sum(outcomes==3)),"OTHER_BLOCKED":int(np.sum(outcomes==4))},
        "sorb_session_contribution":{"LONDON":{"entries":int(se[1]),"official_wins":int(sv[1]),"net_profit":r2(sn[1])},
        "COMEX_GOLD":{"entries":int(se[2]),"official_wins":int(sv[2]),"net_profit":r2(sn[2])}}}

def parent_gate(a):
    for k,v in PARENT_EXPECTED.items():
        if abs(float(a[k])-float(v))>.011:
            raise SystemExit(f"14A surrogate parent gate failed {k}: {a[k]} != {v}")

def supply(props):
    return {"proposals":len(props),"source_eligible":sum(p.eligible for p in props),"distinct_days":len({p.utc_day_ms for p in props}),
        "source_rejections":{"REENTERED_RANGE":sum(p.reason=="REENTERED_RANGE" for p in props),"SPREAD_GATE":sum(p.reason=="SPREAD_GATE" for p in props)},
        "proposal_long":sum(p.side>0 for p in props),"proposal_short":sum(p.side<0 for p in props),
        "sessions":{"LONDON":sum(p.session=="LONDON" for p in props),"COMEX_GOLD":sum(p.session=="COMEX_GOLD" for p in props)}}

def decision(p,c,s):
    nd=r2(c["net_profit"]-p["net_profit"]); gd=r2(c["gross_profit"]-p["gross_profit"]); ld=r2(c["gross_loss"]-p["gross_loss"])
    td=c["trades"]-p["trades"]; wd=c["official_wins"]-p["official_wins"]
    bd=100*(c["max_balance_drawdown"]-p["max_balance_drawdown"])/p["max_balance_drawdown"]
    ed=100*(c["max_equity_drawdown"]-p["max_equity_drawdown"])/p["max_equity_drawdown"]
    q=s["proposals"]>=8 and s["distinct_days"]>=4; a=c["sorb_entries"]>=5; tc=td>=0
    w=wd>=0 or (nd>0 and ld>0); n=nd>=-2; dd=bd<=1+1e-12 and ed<=1+1e-12; ok=q and a and tc and w and n and dd
    return {"proposal_supply_ok":q,"incremental_entry_floor_ok":a,"combined_trade_count_not_lower":tc,"winner_or_quality_gate_ok":w,
        "net_not_worse_than_2usd":n,"drawdown_deterioration_within_1pct":dd,"screen_pass":ok,"strong_screen_pass":ok and nd>=0,
        "trade_delta":int(td),"official_win_delta":int(wd),"gross_profit_delta":gd,"gross_loss_delta":ld,"net_delta":nd,
        "max_balance_dd_delta_pct":float(bd),"max_equity_dd_delta_pct":float(ed),
        "incremental_net_per_sorb_entry":r2(nd/c["sorb_entries"]) if c["sorb_entries"] else None}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--source",type=Path,required=True); ap.add_argument("--output",type=Path,required=True); a=ap.parse_args()
    sha=base.sha256_file(a.source)
    if sha!=base.CANONICAL_JAN_SHA256: raise SystemExit("canonical January SHA mismatch: "+sha)
    df=pd.read_csv(a.source,compression="gzip",usecols=["timestamp_ms_utc","ask_raw","bid_raw"],dtype=np.int64)
    df=df[(df.timestamp_ms_utc>=sorb.STAGE_A_START_MS)&(df.timestamp_ms_utc<base.STAGE_A_END_MS)]; t=df.timestamp_ms_utc.to_numpy(np.int64)
    if t.size!=4205709 or (t.size and np.any(t[1:]<t[:-1])): raise SystemExit(f"Stage-A chronology mismatch: {t.size}")
    ask,bid=base.p75(t,df.ask_raw.to_numpy(np.int64),df.bid_raw.to_numpy(np.int64))
    feat=parent.build_parent_features(t,ask,bid); streams=generate_streams(t,ask,bid)
    d3t,d3s=streams["DH03_S06"]; d5t,d5s=streams["DH05_S06"]; s11t,s11s=streams["DH02_S11"]; s08t,s08s=streams["DH02_S08"]
    zi=np.empty(0,np.int64); zs=np.empty(0,np.int8)
    p=pack_sorb(run_integrated_sorb(t,ask,bid,feat["impulse250"],feat["h1_netatr"],feat["m30_netatr"],d3t,d3s,d5t,d5s,s11t,s11s,s08t,s08s,zi,zs,zs,1,1,1,1,1)); parent_gate(p)
    results={}; rank=[]
    for cid in CONFIG_ORDER:
        props=sorb.generate_proposals(t,ask,bid,cid); sp=supply(props); ep=[x for x in props if x.eligible]
        ii=np.asarray([x.decision_index for x in ep],np.int64); ss=np.asarray([x.side for x in ep],np.int8)
        se=np.asarray([1 if x.session=="LONDON" else 2 for x in ep],np.int8)
        c=pack_sorb(run_integrated_sorb(t,ask,bid,feat["impulse250"],feat["h1_netatr"],feat["m30_netatr"],d3t,d3s,d5t,d5s,s11t,s11s,s08t,s08s,ii,ss,se,1,1,1,1,1))
        d=decision(p,c,sp); results[cid]={"supply":sp,"combined":c,"decision":d}
        rank.append((int(d["strong_screen_pass"]),int(d["screen_pass"]),d["net_delta"],c["sorb_entries"],-d["max_equity_dd_delta_pct"],cid))
    rank.sort(reverse=True); order=[x[-1] for x in rank]
    leaders=[{"config_id":cid,"screen_pass":results[cid]["decision"]["screen_pass"],"strong_screen_pass":results[cid]["decision"]["strong_screen_pass"],
        "accepted_entries":results[cid]["combined"]["sorb_entries"],"trade_delta":results[cid]["decision"]["trade_delta"],
        "official_win_delta":results[cid]["decision"]["official_win_delta"],"net_delta":results[cid]["decision"]["net_delta"],
        "max_equity_dd_delta_pct":results[cid]["decision"]["max_equity_dd_delta_pct"]} for cid in order]
    anypass=any(results[c]["decision"]["screen_pass"] for c in CONFIG_ORDER); anystrong=any(results[c]["decision"]["strong_screen_pass"] for c in CONFIG_ORDER)
    out={"schema":"delta-r037-sorb-surrogate-parent-stage-a-screen-v1","status":"COMPLETE_NON_PROMOTING_SURROGATE_PARENT_STAGE_A_SCREEN",
        "unit":"R037_SORB_SURROGATE_PARENT_STAGE_A_SCREEN","parent_checkpoint":"R037_R032_SPECIALIST_PARENT_PROVENANCE_SORB_READINESS_CHECKPOINT_14B",
        "surrogate_parent":"14A_BACKBONE_FIRST_C03_WITH_FROZEN_PROVENANCE_LIMITED_SPECIALISTS","promotable":False,"source_sha256":sha,
        "stage_a_ticks":int(t.size),"surface":"DUKAS_COINEXX_LIKE_P75","numeric_retuning":False,"august_accessed":False,"parent_control":p,
        "configs":results,"ranking":leaders,"finding":{"leading_config":order[0],"any_screen_pass":anypass,"any_strong_screen_pass":anystrong,
        "next":"R037_SORB_C04_DUAL30_INDEPENDENT_VALIDATION" if anystrong else "R037_SORB_SURROGATE_REFINEMENT_OR_NEXT_SOURCE"},"mql5_authorized":False}
    base.atomic_write_json(a.output,out)
    print(json.dumps({"ranking":leaders,"finding":out["finding"]},separators=(",",":")))

if __name__=="__main__": main()
