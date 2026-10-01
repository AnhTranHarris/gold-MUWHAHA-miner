"""
BETA064 beta064_multidesk_loop.py — RECOVERY_UNCERTIFIED scaffold.

BETA ONLY. No Alpha/GAMMA dependencies. August sealed.
No MQL5 use. This is NOT certified as the lost source.

Historical left-edge state is allowed only for forensic reconstruction.
Corrected right-edge state is the only admissible future runtime semantics.

R11-R18 correction:
The universal FALSE->TRUE broad-mask edge hypothesis is rejected by selected-timestamp
evidence for E6/E9/E11. R17 also rejects emitting every active broad-mask row as
exact source because it overproduces the frozen January FIT population by >68k.
R18 constrains the missing topology to a specialist-specific in-state finite-state
sub-clock (secondary transient state + persistence/retest/renewal + bounded
timer/counter/debounce + reset/rearm), but exact historical thresholds/raw_score
remain unrecovered.

Accordingly, the E6/E9/E11 persistent emissions below are FORENSIC UPPER BOUNDS
ONLY. This scaffold MUST NOT be used as historical candidate source, model-training
parent, MT5 parity source, or production logic.
"""
import numpy as np
import pandas as pd

FIT_END=pd.Timestamp("2026-01-09",tz="UTC")
CAL_END=pd.Timestamp("2026-01-11",tz="UTC")
RECOVERY_STATUS="RECOVERY_CLOSED_R18_FORENSIC_ONLY_EXACT_SOURCE_NOT_RECOVERED"
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
    _emit(rows,b,lo,1,"E6_VALUE_REVERSION",sc,180,20,edge_only=False); _emit(rows,b,sh,-1,"E6_VALUE_REVERSION",sc,180,20,edge_only=False)

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
    _emit(rows,b,lo,1,"E9_LEVEL_BREAK",sc,300,30,edge_only=False); _emit(rows,b,sh,-1,"E9_LEVEL_BREAK",sc,300,30,edge_only=False)

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
    _emit(rows,b,lo,1,"E11_KINETIC_IGNITION",sc,45,10,edge_only=False); _emit(rows,b,sh,-1,"E11_KINETIC_IGNITION",sc,45,10,edge_only=False)

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
      "exact_historical_helper_recovered":False,
      "recovery_closed":True,
      "safe_active_causal_base":"BETA063",
      "persistent_e6_e9_e11_emission":"FORENSIC_UPPER_BOUND_ONLY",
      "hard_gates":[
        "exact Jan FIT candidate identity",
        "candidate timestamp/side/specialist/raw_score/horizon/checkpoint parity",
        "quote_pressure/qv_imb parity",
        "frozen base-model probability parity",
        "session-router parity",
        "corrected-causal 5469-sequence replacement checkpoint"
      ]
    }
