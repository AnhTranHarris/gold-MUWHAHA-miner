"""
BETA064 beta064_multidesk_loop.py — RECOVERY_UNCERTIFIED scaffold.

BETA ONLY. No Alpha/GAMMA dependencies. August sealed.
No MQL5 use. This is NOT certified as the lost source.

Historical left-edge state is allowed only for forensic reconstruction.
Corrected right-edge state is the only admissible future runtime semantics.

R11 correction:
The R9C universal FALSE->TRUE edge-emission hypothesis is rejected by independent
February/March selected-timestamp evidence. Base mechanism masks remain useful
forensics, but this scaffold MUST NOT claim exact candidates() identity.
In particular, E6 and E11 selected trades frequently occur inside persistent
active states rather than only at mask transitions.
"""
import numpy as np
import pandas as pd

FIT_END=pd.Timestamp("2026-01-09",tz="UTC")
CAL_END=pd.Timestamp("2026-01-11",tz="UTC")
RECOVERY_STATUS="RECOVERY_UNCERTIFIED_R11_UNIVERSAL_EDGE_REJECTED"
UNIVERSAL_EDGE_EMISSION_REJECTED=True
FROZEN_JAN_FIT_ROWS=30579

def eff(s,n):
    return (s-s.shift(n)).abs()/(s.diff().abs().rolling(n,n).sum()+1e-9)

def edge(mask):
    m=mask.fillna(False).astype(bool)
    return m & ~m.shift(1,fill_value=False)

def _emit(rows,b,mask,side,name,score,horizon,checkpoint,edge_only=True):
    m=edge(mask) if edge_only else mask.fillna(False).astype(bool)
    for i in np.flatnonzero(m.to_numpy()):
        sd=int(side.iloc[i] if hasattr(side,"iloc") else side)
        sc=float(score.iloc[i] if hasattr(score,"iloc") else score)
        rows.append((b.index[i],i,sd,name,sc,horizon,checkpoint))

def candidates_h1(b):
    """R9C historical edge-emission hypothesis. RETAINED FOR FORENSICS ONLY.

    R11 cross-month evidence rejects the universal edge() emission assumption.
    Do not use this function as recovered source or as a causal parent generator.
    """
    rows=[]

    # E3 generic UTC ORB accepted break — exact legacy gate still unresolved.
    lo=(b.orb_active==1)&(b.open<=b.orb_hi)&(b.mid>b.orb_hi)&(b.body>0)&(b.r15>0)
    sh=(b.orb_active==1)&(b.open>=b.orb_lo)&(b.mid<b.orb_lo)&(b.body<0)&(b.r15<0)
    sc=65+8*b.eff60.fillna(0)+4*b.tick_z.clip(-1,3)
    _emit(rows,b,lo,1,"E3_ORB",sc,300,30); _emit(rows,b,sh,-1,"E3_ORB",sc,300,30)

    # E5 daily VWAP/value reclaim. eff15>=.30 is R9C population-supported.
    pv=b.vwap_dist.shift(1)
    lo=(pv<0)&(b.vwap_dist>0)&(b.r15>0)&(b.eff15>=.30)
    sh=(pv>0)&(b.vwap_dist<0)&(b.r15<0)&(b.eff15>=.30)
    sc=60+8*b.eff60.fillna(0)
    _emit(rows,b,lo,1,"E5_VWAP_RECLAIM",sc,120,15); _emit(rows,b,sh,-1,"E5_VWAP_RECLAIM",sc,120,15)

    # E6 statistical return toward daily value.
    lo=(b.vwap_z<=-1.0)&(b.eff300<=.50)
    sh=(b.vwap_z>=1.0)&(b.eff300<=.50)
    sc=60+8*b.vwap_z.abs().fillna(0)+5*(1-b.eff300.fillna(1))
    _emit(rows,b,lo,1,"E6_VALUE_REVERSION",sc,180,20); _emit(rows,b,sh,-1,"E6_VALUE_REVERSION",sc,180,20)

    # E7 prior-5m liquidity sweep/reclaim.
    lo=(b.low<b.prior5_lo)&(b.mid>b.prior5_lo)&(b.body>0)
    sh=(b.high>b.prior5_hi)&(b.mid<b.prior5_hi)&(b.body<0)
    sc=67+8*b.eff15.fillna(0)+3*b.tick_z.clip(-1,3)
    _emit(rows,b,lo,1,"E7_SWEEP_RECLAIM",sc,120,15); _emit(rows,b,sh,-1,"E7_SWEEP_RECLAIM",sc,120,15)

    # E8 prior-15m rejection analogue — sparse evidence, exact boundary unresolved.
    lo=(b.low<=b.prior15_lo+.10*b.atr60)&(b.mid>b.prior15_lo+.05*b.atr60)&(b.body>0)
    sh=(b.high>=b.prior15_hi-.10*b.atr60)&(b.mid<b.prior15_hi-.05*b.atr60)&(b.body<0)
    sc=64+8*b.eff60.fillna(0)
    _emit(rows,b,lo,1,"E8_LEVEL_BOUNCE",sc,300,30); _emit(rows,b,sh,-1,"E8_LEVEL_BOUNCE",sc,300,30)

    # E9 prior-5m accepted level break. eff15>=.30 is R9C population-supported.
    lo=(b.open<=b.prior5_hi)&(b.mid>b.prior5_hi)&(b.body>0)&(b.eff15>=.30)
    sh=(b.open>=b.prior5_lo)&(b.mid<b.prior5_lo)&(b.body<0)&(b.eff15>=.30)
    sc=68+10*b.eff15.fillna(0)+8*(b.body.abs()/b.atr60.clip(lower=.05)).fillna(0)
    _emit(rows,b,lo,1,"E9_LEVEL_BREAK",sc,300,30); _emit(rows,b,sh,-1,"E9_LEVEL_BREAK",sc,300,30)

    # E10 previous compression -> directional release; tick_z>=.50 is R9C-supported.
    comp=b.range_ratio.shift(1)<=.30
    lo=comp&(b.body>0)&(b.r15>0)&(b.tick_z>=.50)
    sh=comp&(b.body<0)&(b.r15<0)&(b.tick_z>=.50)
    sc=64+7*b.tick_z.clip(0,4)
    _emit(rows,b,lo,1,"E10_COMPRESSION_RELEASE",sc,120,15); _emit(rows,b,sh,-1,"E10_COMPRESSION_RELEASE",sc,120,15)

    # E11 kinetic ignition — exact velocity/accel thresholds still unresolved.
    lo=(b.r15>0)&(b.eff15>=.55)&(b.tick_z>=.50)
    sh=(b.r15<0)&(b.eff15>=.55)&(b.tick_z>=.50)
    sc=72+10*b.eff15.fillna(0)+4*b.tick_z.clip(0,4)
    _emit(rows,b,lo,1,"E11_KINETIC_IGNITION",sc,45,10); _emit(rows,b,sh,-1,"E11_KINETIC_IGNITION",sc,45,10)

    # E12 failed expansion / recross.
    ph=b.prior5_hi.shift(1); pl=b.prior5_lo.shift(1)
    lo=(b.mid.shift(1)<pl)&(b.mid>b.prior5_lo)&(b.body>0)
    sh=(b.mid.shift(1)>ph)&(b.mid<b.prior5_hi)&(b.body<0)
    sc=66+6*b.tick_z.clip(-1,3)
    _emit(rows,b,lo,1,"E12_FAILED_EXPANSION",sc,120,15); _emit(rows,b,sh,-1,"E12_FAILED_EXPANSION",sc,120,15)

    c=pd.DataFrame(rows,columns=["time","i","side","specialist","raw_score","horizon","checkpoint"])
    return c.drop_duplicates(["time","side","specialist"]).sort_values("time").reset_index(drop=True)

def add_v2_exact_replacements(c,b):
    """Exact active E1/E2/E4 replacements preserved in beta064_multidesk_v2.py."""
    rows=[]
    side=pd.Series(np.where((b.r3600.fillna(0)+.35*b.r14400.fillna(0))>=0,1,-1),index=b.index)
    fresh=((side>0)&(b.mid>b.prior5_hi)&(b.r900*side>0))|((side<0)&(b.mid<b.prior5_lo)&(b.r900*side>0))
    _emit(rows,b,fresh&(b.eff3600>.14)&(b.eff900>.14),side,"E1_MACRO_TREND",62+18*b.eff3600.fillna(0)+12*b.eff900.fillna(0),900,60,False)

    side2=pd.Series(np.where(b.r3600>=0,1,-1),index=b.index)
    e2=(b.r3600*side2>0)&(b.r300*side2<0)&(b.r60*side2>0)&(b.r15*side2>0)&(b.eff3600>.12)
    _emit(rows,b,e2,side2,"E2_PULLBACK_REACCEL",60+15*b.eff3600.fillna(0)+10*b.eff60.fillna(0),300,30,False)

    near=b.vwap_dist.abs()<(0.75*b.atr60).fillna(0)
    e4=near&(b.r3600*side2>0)&(b.r60*side2>0)&(b.eff3600>.12)
    _emit(rows,b,e4,side2,"E4_VWAP_PULLBACK",58+15*b.eff3600.fillna(0)+8*b.eff60.fillna(0),300,30,False)

    x=pd.DataFrame(rows,columns=c.columns)
    c=c.loc[~c.specialist.isin(["E1_MACRO_TREND","E2_PULLBACK_REACCEL","E4_VWAP_PULLBACK"])]
    return pd.concat([c,x],ignore_index=True).drop_duplicates(["time","side","specialist"]).sort_values("time").reset_index(drop=True)

def historical_left_edge_forensic(c_right_edge):
    """FOR FORENSICS ONLY. Never valid for MT5/runtime."""
    out=c_right_edge.copy(); out["time"]=out.time-pd.Timedelta(seconds=5); out["forensic_only"]=True
    return out

def certification_status():
    return {
      "status":RECOVERY_STATUS,
      "frozen_jan_fit_rows":FROZEN_JAN_FIT_ROWS,
      "mt5_parity_authorized":False,
      "historical_left_edge_production_allowed":False,
      "hard_gates":[
        "exact Jan FIT candidate identity",
        "candidate timestamp/side/specialist/raw_score/horizon/checkpoint parity",
        "quote_pressure/qv_imb parity",
        "frozen base-model probability parity",
        "session-router parity",
        "corrected-causal 5469-sequence replacement checkpoint"
      ]
    }


# ---------------------------------------------------------------------------
# R14 RIGHT-EDGE CAUSAL REBUILD APPENDIX
# Added 2026-10-01 after R13 archaeology.
#
# This appendix does NOT recover the lost historical source. It turns the R11
# forensic scaffold into a transparent new causal research helper. Historical
# Checkpoint 03 parity remains rejected/suspended.
# ---------------------------------------------------------------------------
from lightgbm import LGBMClassifier

R14_RECOVERY_STATUS="R14_COMPLETE_RIGHT_EDGE_REBUILD_REJECTED_FOR_PROMOTION"
R14_HISTORICAL_CHECKPOINT03_AUTHORIZED=False
R14_MQL5_AUTHORIZED=False
R14_AUGUST_SEALED=True

R14_BASE_FEATURES=[
    "spread","r15","r30","r60","r300","r900","r3600","r14400",
    "eff15","eff60","eff300","eff900","eff3600","vol60","vol300",
    "atr60","atr300","tick_z","qp","qv","vwap_z","range_ratio",
    "body","range"
]
R14_SPECIALISTS=[
    "E1_MACRO_TREND","E2_PULLBACK_REACCEL","E3_ORB","E4_VWAP_PULLBACK",
    "E5_VWAP_RECLAIM","E6_VALUE_REVERSION","E7_SWEEP_RECLAIM",
    "E8_LEVEL_BOUNCE","E9_LEVEL_BREAK","E10_COMPRESSION_RELEASE",
    "E11_KINETIC_IGNITION","E12_FAILED_EXPANSION"
]
R14_FEATURES=R14_BASE_FEATURES+["side","raw_score"]+[f"sp_{x}" for x in sorted(R14_SPECIALISTS)]

def build_one_second_state(raw):
    """R14 supported-reconstruction one-second ledger from ordered Dukascopy ticks.

    Required columns:
      timestamp_ms_utc, ask_raw, bid_raw, ask_volume, bid_volume

    Evidence status:
      OHLC/Bid/Ask/spread/tick_count geometry = source-derived exact.
      quote_pressure and qv_imb formulas below = supported reconstruction,
      NOT historical Checkpoint-03 parity.
    """
    need={"timestamp_ms_utc","ask_raw","bid_raw","ask_volume","bid_volume"}
    missing=need.difference(raw.columns)
    if missing:
        raise ValueError(f"missing raw columns: {sorted(missing)}")
    d=raw.loc[:,["timestamp_ms_utc","ask_raw","bid_raw","ask_volume","bid_volume"]].copy()
    d=d.sort_values("timestamp_ms_utc",kind="stable")
    ts=d.timestamp_ms_utc.to_numpy(np.int64)
    ask=d.ask_raw.to_numpy(np.int64)
    bid=d.bid_raw.to_numpy(np.int64)
    av=d.ask_volume.to_numpy(np.float64)
    bv=d.bid_volume.to_numpy(np.float64)

    sec=ts//1000
    starts=np.r_[0,np.flatnonzero(sec[1:]!=sec[:-1])+1]
    ends=np.r_[starts[1:],len(d)]
    cnt=ends-starts

    mid2=ask+bid
    same=np.r_[False,sec[1:]==sec[:-1]]
    dm=np.zeros(len(d),dtype=np.int64)
    dm[1:]=mid2[1:]-mid2[:-1]
    dm[~same]=0
    up=np.add.reduceat((dm>0).astype(np.int32),starts)
    dn=np.add.reduceat((dm<0).astype(np.int32),starts)
    avs=np.add.reduceat(av,starts)
    bvs=np.add.reduceat(bv,starts)

    idx=pd.to_datetime(sec[starts]*1000,unit="ms",utc=True)
    out=pd.DataFrame(index=idx)
    out["open_mid"]=(mid2[starts]/2000.0).astype("float32")
    out["high_mid"]=(np.maximum.reduceat(mid2,starts)/2000.0).astype("float32")
    out["low_mid"]=(np.minimum.reduceat(mid2,starts)/2000.0).astype("float32")
    out["mid"]=(mid2[ends-1]/2000.0).astype("float32")
    out["bid"]=(bid[ends-1]/1000.0).astype("float32")
    out["ask"]=(ask[ends-1]/1000.0).astype("float32")
    out["spread"]=((ask[ends-1]-bid[ends-1])/1000.0).astype("float32")
    out["tick_count"]=cnt.astype("int32")

    # BETA026/BETA039 proves predecessor quote_pressure1 was already side-signed.
    # BETA064 cache exists before a candidate side exists; therefore R14 uses
    # the unsided market-direction form rather than double-signing it.
    den=(up+dn).astype(np.float64)
    out["quote_pressure"]=np.divide(
        up-dn,den,out=np.zeros(len(den),dtype=np.float64),where=den>0
    ).astype("float32")

    # qv_imb remained unrecoverable from historical source. R14 makes the
    # chosen semantics explicit and auditable instead of pretending parity.
    qden=avs+bvs
    out["qv_imb"]=np.divide(
        bvs-avs,qden,out=np.zeros(len(qden),dtype=np.float64),where=qden>0
    ).astype("float32")
    return out

def candidates(b):
    """New R14 candidate surface.

    E3/E5-E12 use the R11 source-supported mechanism masks with event-edge
    emission. E1/E2/E4 are then replaced by the exact preserved V2 rules.
    This is valid for new right-edge causal research only.
    """
    return add_v2_exact_replacements(candidates_h1(b),b)

def make_labels(c,b,raw):
    """Frozen offline Entry->Initial-Hold label geometry.

    Future ticks are used only here for training/evaluation labels. They are
    never features. BUY enters Ask/marks Bid; SELL enters Bid/marks Ask.
    """
    need={"timestamp_ms_utc","ask_raw","bid_raw"}
    missing=need.difference(raw.columns)
    if missing:
        raise ValueError(f"missing raw label columns: {sorted(missing)}")
    d=raw.loc[:,["timestamp_ms_utc","ask_raw","bid_raw"]].sort_values(
        "timestamp_ms_utc",kind="stable"
    )
    times=d.timestamp_ms_utc.to_numpy(np.int64)
    bid=d.bid_raw.to_numpy(np.float64)/1000.0
    ask=d.ask_raw.to_numpy(np.float64)/1000.0

    out=c.copy().reset_index(drop=True)
    state=b.reindex(out.time)
    out["spread"]=state.spread.to_numpy(float)
    out["atr60"]=state.atr60.fillna(state.spread*2).to_numpy(float)

    survive=np.zeros(len(out),float)
    fp=np.zeros(len(out),float)
    pnl=np.zeros(len(out),float)
    fav_bar=np.zeros(len(out),float)
    adv_bar=np.zeros(len(out),float)
    mfe=np.zeros(len(out),float)
    mae=np.zeros(len(out),float)
    ctime=out.time.astype("int64").to_numpy()//1_000_000

    for k in range(len(out)):
        i=int(np.searchsorted(times,ctime[k]))
        if i>=len(times):
            continue
        side=int(out.side.iloc[k])
        entry=ask[i] if side>0 else bid[i]
        sp=max(float(out.spread.iloc[k]),0.05)
        atr=max(float(out.atr60.iloc[k]),sp)
        fav=max(0.35,1.25*sp,0.30*atr)
        adv=max(0.30,1.00*sp,0.22*atr)
        checkpoint_ms=ctime[k]+int(out.checkpoint.iloc[k])*1000
        horizon_ms=ctime[k]+int(out.horizon.iloc[k])*1000

        first_fav=-1
        first_adv=-1
        j=i+1
        last=i
        best=-np.inf
        worst=np.inf
        while j<len(times) and times[j]<=horizon_ms:
            px=bid[j] if side>0 else ask[j]
            ex=(px-entry)*side
            best=max(best,ex)
            worst=min(worst,ex)
            last=j
            if first_fav<0 and ex>=fav:
                first_fav=j
            if first_adv<0 and ex<=-adv:
                first_adv=j
            if first_fav>=0 and first_adv>=0:
                break
            j+=1

        survive[k]=1.0 if first_adv<0 or times[first_adv]>checkpoint_ms else 0.0
        fp[k]=1.0 if first_fav>=0 and (first_adv<0 or first_fav<first_adv) else 0.0
        jj=first_fav if fp[k] else (first_adv if first_adv>=0 else last)
        px=bid[jj] if side>0 else ask[jj]
        pnl[k]=(px-entry)*side-0.02
        fav_bar[k]=fav
        adv_bar[k]=adv
        mfe[k]=best if np.isfinite(best) else 0.0
        mae[k]=worst if np.isfinite(worst) else 0.0

    out["survive"]=survive
    out["fp_win"]=fp
    out["resolved_pnl"]=pnl
    out["fav_bar"]=fav_bar
    out["adv_bar"]=adv_bar
    out["mfe"]=mfe
    out["mae"]=mae
    return out

def add_model_features(b,c,cols=None):
    X=b.reindex(c.time)[R14_BASE_FEATURES].reset_index(drop=True).astype("float32")
    X["side"]=c.side.to_numpy(np.float32)
    X["raw_score"]=c.raw_score.to_numpy(np.float32)
    X=pd.concat([
        X,
        pd.get_dummies(c.specialist.reset_index(drop=True),prefix="sp",dtype=np.int8)
    ],axis=1)
    use=R14_FEATURES if cols is None else cols
    return X.reindex(columns=use,fill_value=0)

def fit_models(X,c):
    fit=c.time<FIT_END
    cal=(c.time>=FIT_END)&(c.time<CAL_END)
    diag=c.time>=CAL_END
    kw=dict(
        n_estimators=180,num_leaves=23,learning_rate=0.045,
        subsample=0.8,colsample_bytree=0.8,reg_lambda=2,
        min_child_samples=80,n_jobs=4,verbosity=-1
    )
    ms=LGBMClassifier(**kw)
    mw=LGBMClassifier(**kw)
    ms.fit(X.loc[fit],c.loc[fit,"survive"].astype(int))
    mw.fit(X.loc[fit],c.loc[fit,"fp_win"].astype(int))
    out=c.copy()
    out["p_surv"]=ms.predict_proba(X)[:,1]
    out["p_win"]=mw.predict_proba(X)[:,1]
    out["entry_score"]=out.p_surv*out.p_win
    return out,fit,cal,diag,ms,mw,list(X.columns)

def r14_certification_status():
    return {
        "status":R14_RECOVERY_STATUS,
        "historical_checkpoint03_authorized":False,
        "mql5_authorized":False,
        "august_sealed":True,
        "frozen_historical_jan_fit_rows":FROZEN_JAN_FIT_ROWS,
        "right_edge_r14_jan_fit_rows":30616,
        "right_edge_r14_jan_cal_raw_survival":0.11567229083318838,
        "best_jan_cal_threshold_scan_min20_survival":0.5714285714285714,
        "best_jan_cal_threshold_scan_min20_net":-18.5529999999989,
        "historical_gate_088_030_selected_trades_janjul":0,
        "decision":"REJECT_NEW_MULTIDESK_PROMOTION_ROLL_BACK_TO_LAST_CAUSALLY_AUDITED_BETA_BASE",
        "hard_rule":"Historical Checkpoint 01/02/03 remain forensic only. Do not translate them to MT5."
    }
