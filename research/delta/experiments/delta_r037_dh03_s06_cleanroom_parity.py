"""DELTA R037 DH03-S06 clean-room parity reconstruction — Checkpoint 13A."""
from __future__ import annotations
import argparse,json
from pathlib import Path
import numpy as np,pandas as pd
import delta_r037_dh02_s08_cleanroom_parity as base
import delta_r037_dh03_s06_structure as structure
import delta_r037_dh03_s06_engine as engine

FP="a3a086b7344c"
TARGET={"trades":1563,"raw_positive_wins":690,"gross_profit":151.82,"gross_loss":-490.75,"net_profit":-338.93,"max_balance_drawdown":339.25}
PROFILES=("STRUCTURAL_PRIORITY_SWING_PARENT_S15_SWING_RECLAIM","STRUCTURAL_PRIORITY_SWING_PARENT_S15_EITHER_DECLINE","DIRECTIONAL_CONFLUENCE_PARENT_S15_SWING_RECLAIM","STRUCTURAL_PRIORITY_SWING_PARENT_RECLAIM_LAST_PIVOT")

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--source",type=Path,required=True);ap.add_argument("--evidence",type=Path,required=True);ap.add_argument("--output",type=Path,required=True)
    a=ap.parse_args();ev=json.loads(a.evidence.read_text())
    if ev.get("schema")!="delta-r037-dh03-s06-cleanroom-parity-evidence-13a-v1" or ev["vector"]["fingerprint"]!=FP:raise SystemExit("13A evidence mismatch")
    sh=base.sha256_file(a.source)
    if sh!=base.CANONICAL_JAN_SHA256:raise SystemExit("canonical January SHA mismatch")
    df=pd.read_csv(a.source,compression="gzip",usecols=["timestamp_ms_utc","ask_raw","bid_raw"],dtype=np.int64)
    df=df[df.timestamp_ms_utc<base.STAGE_A_END_MS];t=df.timestamp_ms_utc.to_numpy(np.int64)
    if len(t)!=4205709:raise SystemExit("Stage-A tick mismatch")
    ask,bid=base.p75(t,df.ask_raw.to_numpy(np.int64),df.bid_raw.to_numpy(np.int64));mid=ask+bid
    b5=base.bars(t,mid,5000);b15=base.bars(t,mid,15000);b30=base.bars(t,mid,30000)
    m5=base.bars(t,mid,300000);m15=base.bars(t,mid,900000);m30=base.bars(t,mid,1800000)
    e5=base.signed_eff(b5,4);e15=base.signed_eff(b15,4);e30=base.signed_eff(b30,4);a5=base.atr14(m5)
    pe,ps,pd,li,si=structure.parent_series(m15,m30);phi,plo,pht,plt=structure.latest_fast_pivots(b15)
    profiles={}
    for k,name in enumerate(PROFILES):
        st,ss,se,c=engine.detect(t,mid,b5["end_ms"],b5["close"],e5,b15["end_ms"],b15["high"],b15["low"],b15["close"],e15,b30["end_ms"],e30,m5["end_ms"],a5,pe,ps,pd,li,si,phi,plo,pht,plt,k)
        x=base.execute_r9_lifecycle(t,ask,bid,st,ss)
        act={"signals":int(len(st)),"signal_sha256":base.signal_sha(st,ss,se),"pullbacks":int(c[0]),"exhaustion":int(c[1]),"reclaim":int(c[2]),"reacceleration_signal":int(c[3]),"parent_invalid":int(c[4]),"structural_invalid":int(c[5]),"expired":int(c[6]),"depth_ready_observations":int(c[7]),"countereff_ready_observations":int(c[8]),"no_new_extreme_ready_observations":int(c[9]),"pivot_unavailable_observations":int(c[10]),"trades":int(x[0]),"raw_positive_wins":int(x[1]),"official_wins":int(x[2]),"gross_profit":float(x[3]),"gross_loss":float(x[4]),"net_profit":float(x[5]),"max_balance_drawdown":float(x[6])}
        er={q:abs(act[q]-TARGET[q]) for q in TARGET}
        score=100*er["trades"]+25*er["raw_positive_wins"]+er["gross_profit"]+er["gross_loss"]+er["net_profit"]+er["max_balance_drawdown"]
        profiles[name]={"actual":act,"abs_error":er,"parity_score":float(score)}
    order=sorted(PROFILES,key=lambda z:profiles[z]["parity_score"]);lead=order[0];q=profiles[lead]["actual"]
    exact=q["trades"]==TARGET["trades"] and q["raw_positive_wins"]==TARGET["raw_positive_wins"] and all(abs(q[x]-TARGET[x])<.011 for x in ("gross_profit","gross_loss","net_profit","max_balance_drawdown"))
    out={"schema":"delta-r037-dh03-s06-cleanroom-parity-13a-v1","status":"COMPLETE_EXACT_PARITY" if exact else "COMPLETE_CLEANROOM_PARITY_FAIL_LOCALIZED","unit":"R037_DH03_S06_CLEANROOM_PARITY_RECONSTRUCTION","source_sha256":sh,"stage_a_ticks":int(len(t)),"surface":"DUKAS_COINEXX_LIKE_P75","vector_fingerprint":FP,"numeric_vector_retune":False,"august_accessed":False,"profiles":profiles,"ranking":order,"finding":{"leading_profile":lead,"exact_historical_parity":exact,"target":TARGET,"next":ev["next_if_exact"] if exact else ev["next_if_nonexact_localized"]},"mql5_authorized":False}
    base.atomic_write_json(a.output,out);print(json.dumps(out["finding"],separators=(",",":")))
if __name__=="__main__":main()
