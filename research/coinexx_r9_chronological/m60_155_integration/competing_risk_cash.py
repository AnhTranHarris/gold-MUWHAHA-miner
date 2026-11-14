"""Coinexx-only 155-feature competing-risk, account-currency shadow scenarios.

Reuses original 75-tree at-risk LightGBM model. NO new training, tick rebuild,
or claim of executable profitability. Hypothetical barriers are originally
frozen label geometry, NOT MT5's path-dependent trailing stop.

A positive utility is NOT a production eligibility condition until Coinexx
whole-system trade/portfolio results are independently validated.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import os
from pathlib import Path
import sys
import tempfile
import zipfile

import numpy as np
import joblib

from score_snapshot import validate_snapshot, SCHEMA as SNAPSHOT_SCHEMA

MODEL_BYTES = {
    "fold05": "dd0df03628ef8cd3cb82a25e561bd0194570d23ffae2a357f1cff55f2e3a96a8",
    "fold06": "07579a99eb16c634e45f6d22d59ee0e939872f1176379a778139f5933aab50e7",
    "fold07": "7e02c1defdc10e327e00a32af4b1ac05db265804dfa63a087faee032cdc444b0",
    "fold08": "e886d848ae9b15a2556608c1f884d39c41b3224c4f72a701fb0c7502ed798a18",
    "fold09": "f121f4ce75b35cc79bf4d25a5ade4cd183aa9f1e5d1f42d1431ccc464c9584e7",
    "final_is": "717829da94b15af27f244b51ea22458319470052471b9f3ca65dd51501daa1a3",
}
BIN_END_MS = (250, 1000, 3000, 5000, 15000)
PACKET_TAG = "R9_CRISK155_V1"
PACKET_SCHEMA = "R9_CRISK_155_20261113_V1"


def load_hazard(archive: Path, model_id: str):
    """Verify archived original model hash before deserializing owner-trusted joblib."""
    name = ("hazard_all_JanSep_IS_ONLY" if model_id=="final_is"
            else f"hazard_test_{model_id[-2:]}_shadow")
    with zipfile.ZipFile(archive) as z:
        if z.testzip() is not None:
            raise ValueError("Original Coinexx model archive fails CRC")
        data = z.read("models/"+name+".joblib")
    digest = hashlib.sha256(data).hexdigest()
    if digest != MODEL_BYTES[model_id]:
        raise ValueError(f"Original frozen hazard model hash changed: {model_id}")
    archived = joblib.load(io.BytesIO(data))
    model = archived["model"]
    if (model.n_features_in_ != 156 or model.n_estimators != 75 or
        list(model.classes_) != [0,1,2]):
        raise ValueError("Wrong 155 market features + 1 time-bin/three-class hazard model")
    return model, digest, name


def cumulative_risks(model, features: np.ndarray) -> dict[int,dict[str,float]]:
    """Exactly mirror original run_train.py cumulative_incidence at 5s and 15s.

    Each bin's multiclass outputs are conditional on still being in the risk set:
      event=1 favorable, event=2 adverse, event=0 survive this bin.
    Unconditional cumulative incidence is weighted by survival BEFORE that bin.
    """
    x = np.asarray(features,dtype=np.float32)
    if x.shape != (1,155) or np.isinf(x).any():
        raise ValueError("Expected one exact as-of 155-feature float32 row")
    xf = np.concatenate([np.repeat(x,5,axis=0),
                         np.arange(5,dtype=np.float32).reshape(5,1)],axis=1)
    prob = np.asarray(model.predict_proba(xf),dtype=np.float64)
    if prob.shape!=(5,3) or not np.isfinite(prob).all():
        raise ValueError("Wrong hazard model output")
    if np.any(prob<0) or np.any(prob>1) or np.any(abs(prob.sum(axis=1)-1)>1e-6):
        raise ValueError("Multiclass conditional hazard probabilities invalid")
    survival=1.0
    favored=adverse=0.0
    results={}
    for k,t in enumerate(BIN_END_MS):
        pf=float(prob[k,1]);pa=float(prob[k,2])
        favored+=survival*pf
        adverse+=survival*pa
        survival*=max(0.0,1.0-pf-pa)
        if t in (5000,15000):
            if abs(favored+adverse+survival-1)>1e-6:
                raise ValueError("Cumulative risk normalization failed")
            results[t]={"p_fav":favored,"p_adv":adverse,"p_alive":survival}
    return results


def scenario_ev(p_fav: float,p_adv:float,p_alive:float,
                gross_win_cash:float,gross_loss_cash:float,
                roundtrip_cost_cash:float,timeout_gross_cash:float=0.0,
                risk_weight:float=0.0) -> dict[str,float]:
    """Cash-valued 3-state payoff scenario and exact discrete downside CVaR95.

    Gross win/loss magnitudes are calculated by MT5 OrderCalcProfit (account
    currency); spread is already included in BUY Ask / SELL Bid fills and
    liquidation prices. Cost is charged EXACTLY ONCE to all three outcomes.
    """
    probs=(float(p_fav),float(p_adv),float(p_alive))
    nums=(*probs,gross_win_cash,gross_loss_cash,roundtrip_cost_cash,timeout_gross_cash,risk_weight)
    if not all(math.isfinite(float(v)) for v in nums):
        raise ValueError("All probabilities, economics and risk weight must be finite")
    if (any(p < 0 or p > 1 for p in probs) or
        abs(sum(probs)-1.0)>1e-6 or
        gross_win_cash <= 0 or gross_loss_cash <= 0 or
        roundtrip_cost_cash < 0 or risk_weight < 0):
        raise ValueError("Competing risks or account-currency scenario invalid")
    outcomes=(gross_win_cash-roundtrip_cost_cash,
              -gross_loss_cash-roundtrip_cost_cash,
              timeout_gross_cash-roundtrip_cost_cash)
    ev=sum(p*x for p,x in zip(probs,outcomes))
    # Positive-loss tail (CVaR of loss, not negative return); tie-safe sort.
    outstanding=.05
    tail=0.0
    for loss,weight in sorted([(max(0.0,-val),pr)
                                for pr,val in zip(probs,outcomes)],reverse=True):
        take=min(outstanding,weight)
        tail+=take*loss
        outstanding-=take
    cvar=tail/.05
    return {"expected_net_account_cash":ev,
            "loss_cvar95_account_cash":cvar,
            "risk_adjusted_net_account_cash":ev-risk_weight*cvar,
            "lower_timeout_bound_account_cash":
                ev+probs[2]*(-gross_loss_cash-timeout_gross_cash),
            "upper_timeout_bound_account_cash":
                ev+probs[2]*(gross_win_cash-timeout_gross_cash)}


def snapshot_geometry(s:dict) -> tuple[int,int]:
    """Only original frozen model barrier cents, never assume real R9 SL match."""
    x=s["features"]
    if len(x)!=155:
        raise ValueError("Wrong 155-schema")
    side=float(x[-5]);origin=float(x[-4])
    stop=float(x[-3]);target=float(x[-2]);spread=float(x[-1])
    if (not all(math.isfinite(v) for v in (side,origin,stop,target,spread))
        or side != s["side"] or origin != 1.0
        or int(stop)!=stop or stop <= 0 or
        int(target)!=target or target <= 0 or
        int(spread)!=spread or spread != s["ask_cents"]-s["bid_cents"]):
        raise ValueError("Original action side and quote/barrier geometry mismatch")
    return int(stop),int(target)


def packet_filename(s:dict) -> str:
    return f"R9_CRISK155_{s['symbol']}_{s['account_login']}_{s['magic']}.csv"


def score_packet(model,digest:str,name:str,model_id:str,s:dict):
    """Validate archived timestamp, source ordinal and exact model features."""
    features=validate_snapshot(s,model_id)
    stop,target=snapshot_geometry(s)
    prob=cumulative_risks(model,features)
    fmt=lambda x: format(x,".15g")
    p5=prob[5000];p15=prob[15000]
    packet=[
        PACKET_TAG,str(s["account_login"]),s["symbol"],str(s["magic"]),
        str(s["time_msc"]),str(s["bid_cents"]),str(s["ask_cents"]),
        str(s["side"]),"155",digest,name,
        str(s["feature_end_time_msc"]),str(s["source_ordinal"]),
        str(stop),str(target),
        fmt(p5["p_fav"]),fmt(p5["p_adv"]),fmt(p5["p_alive"]),
        fmt(p15["p_fav"]),fmt(p15["p_adv"]),fmt(p15["p_alive"]),
        "ASOF_PINNED",PACKET_SCHEMA,
    ]
    if len(packet)!=23:
        raise AssertionError("Exact MQL5 23-field packet contract broken")
    return prob,packet


def publish_packet(directory:Path,name:str,fields:list[str]):
    """One tiny atomic file per symbol/account/magic, no growing log/cache."""
    directory.mkdir(parents=True,exist_ok=True)
    tmp=None
    try:
        with tempfile.NamedTemporaryFile("w",encoding="ascii",newline="",
                                         prefix=".r9crisk_",suffix=".tmp",
                                         dir=directory,delete=False) as file:
            tmp=Path(file.name)
            csv.writer(file,lineterminator="\n").writerow(fields)
            file.flush()
            os.fsync(file.fileno())
        os.replace(tmp,directory/name)
    finally:
        if tmp is not None and tmp.exists():
            tmp.unlink()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive",type=Path,required=True)
    parser.add_argument("--model-id",choices=MODEL_BYTES,required=True)
    parser.add_argument("--input",type=Path)
    parser.add_argument("--packet-dir",type=Path)
    args=parser.parse_args()
    model,digest,name=load_hazard(args.archive,args.model_id)
    stream=sys.stdin if args.input is None else args.input.open("r",encoding="utf-8")
    try:
        for line in stream:
            if not line.strip():
                continue
            s=json.loads(line,parse_constant=lambda v: (_ for _ in ()).throw(ValueError(v)))
            prob,row=score_packet(model,digest,name,args.model_id,s)
            if args.packet_dir:
                publish_packet(args.packet_dir,packet_filename(s),row)
            print(json.dumps({"time_msc":s["time_msc"],"side":s["side"],
                              "model_hash":digest,"source_ordinal":s["source_ordinal"],
                              "p5":prob[5000],"p15":prob[15000],
                              "status":"RESEARCH_COMPETING_RISKS_NOT_ACTUAL_R9_PNL"}),
                  flush=True)
    finally:
        if stream is not sys.stdin:
            stream.close()


if __name__=="__main__":
    main()
