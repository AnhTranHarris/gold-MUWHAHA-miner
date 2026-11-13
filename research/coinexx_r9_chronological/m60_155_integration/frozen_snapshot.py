"""Assemble ONE exact 155-feature snapshot from EXISTING frozen Coinexx caches.

Uses the original source-barrier formula code INSIDE the unchanged 155-feature
training ZIP; no independent feature reimplementation, no ticker rebuild.
This adapter works on already frozen R9 entry indices only; it is NOT a live
MQL5 feature producer, nor an order-occupancy backtest.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import zipfile
import zipimport
from pathlib import Path

import numpy as np
import pandas as pd

SCHEMA = "R9_M60_155_20261113_V1"
SOURCE_SIGNAL_SHA256 = "30ef24f0d8aea3dc21fcd13fec434cee86e80bac9783c454bc95c43be642096c"
OLD_HFT_IDX = list(range(14, 117, 6)) + list(range(117, 145, 4))


def source_barrier_features(archive_path: Path):
    """Reuse signed frozen source rather than copy or alter formulas."""
    with zipfile.ZipFile(archive_path) as z:
        original=z.read("frozen_priority/src/signal_features.py")
        if hashlib.sha256(original).hexdigest()!=SOURCE_SIGNAL_SHA256:
            raise ValueError("Original 11-feature barrier formula source SHA mismatch")
    module=zipimport.zipimporter(
        str(archive_path.resolve())+"/frozen_priority/src"
    ).load_module("signal_features")
    return module.action_barrier_features


def assemble_feature_vector(old_row, event_row, priority_row, side, spread, stop, target, barrier_fn):
    """Match run_train.read_month EXACT column order and np.float32 boundary."""
    old=np.asarray(old_row,dtype=np.float32)
    ev=np.asarray(event_row,dtype=np.float32)
    pr=np.asarray(priority_row,dtype=np.float32)
    if old.shape!=(145,) or ev.shape!=(77,) or pr.shape!=(23,):
        raise ValueError(f"Unexpected frozen feature lengths: {old.shape},{ev.shape},{pr.shape}")
    if side not in (1,-1) or spread<0 or stop<=0 or target<=0:
        raise ValueError("Frozen action metadata invalid")
    combined=np.concatenate([old,ev],axis=0).astype(np.float32)
    col=list(range(14))+OLD_HFT_IDX+list(range(145,145+len(ev)))
    b=combined[col]
    meta=np.asarray([side,1.0,stop,target,spread],dtype=np.float32)
    # Priority and analytic 11-feature exact order is source-pinned.
    analytical=barrier_fn(
        ev.reshape(1,-1),
        np.asarray([spread],np.float32),
        np.asarray([stop],np.float32),
        np.asarray([target],np.float32),
        np.asarray([side],np.float32)
    )[0]
    x=np.concatenate([b,pr,analytical,meta]).astype(np.float32)
    if x.shape!=(155,) or np.isinf(x).any():
        raise ValueError("Model feature contract has been violated")
    return x


def emit_snapshot(archive: Path, old_npz: Path, event_npz: Path,
                  priority_npz: Path, candidate_csv: Path,
                  index: int, account_login: int, magic: int = 5559):
    if index<0 or account_login<=0 or magic<0:
        raise ValueError("Invalid index/account/magic")
    barrier_fn=source_barrier_features(archive)
    with np.load(old_npz,allow_pickle=False) as old, \
         np.load(event_npz,allow_pickle=False) as ev, \
         np.load(priority_npz,allow_pickle=False) as pr:
        n=len(old["side"])
        if index>=n:
            raise IndexError("Frozen candidate index outside month")
        # Explicit cross-package identity checks, never join by rounded seconds.
        if (len(ev["entry"])!=n or len(pr["entry"])!=n or
            not np.array_equal(old["entry_times"],ev["entry"]) or
            not np.array_equal(ev["entry"],pr["entry"]) or
            not np.array_equal(old["entry_ordinals"],ev["ordinal"]) or
            not np.array_equal(ev["ordinal"],pr["ordinal"]) or
            not np.array_equal(old["side"],ev["r9_side"])):
            raise ValueError("Frozen Coinexx timestamp/ordinal/side parity failed")
        origside=int(old["side"][index])
        t=int(old["entry_times"][index])
        ordinal=int(old["entry_ordinals"][index])
        spread=int(ev["spread"][index])
        vector=assemble_feature_vector(
            old["features"][index],ev["features"][index],
            pr["features"][index],origside,spread,
            int(ev["stop"][index]),int(ev["target"][index]),
            barrier_fn,
        )

    # Existing candidate source has entry executable quote and spread. Read
    # only 3 columns, no copy of full ticker or feature cache.
    ref=pd.read_csv(candidate_csv,usecols=["entry_ordinal","entry_price_u","spread_u"])
    if len(ref)!=n or int(ref.iloc[index]["entry_ordinal"])!=ordinal:
        raise ValueError("Frozen candidate executable entry price ordinal mismatch")
    entry=int(ref.iloc[index]["entry_price_u"])
    if int(ref.iloc[index]["spread_u"])!=spread:
        raise ValueError("Frozen spread and reference price mismatch")
    bid=entry-spread if origside==1 else entry
    ask=entry if origside==1 else entry+spread
    if not 0<bid<=ask:
        raise ValueError("Bad executable quote")
    return {
        "schema_id":SCHEMA,"market_source":"Coinexx",
        "feature_origin":"FROZEN_EXACT_ASOF",
        "time_msc":t,"feature_end_time_msc":t,
        "source_ordinal":ordinal,"account_login":account_login,
        "symbol":"XAUUSD","magic":magic,"bid_cents":bid,
        "ask_cents":ask,"side":origside,
        "features":[None if np.isnan(v) else float(v) for v in vector],
    }


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for name in ("archive","old-npz","event-npz","priority-npz","candidate-csv"):
        ap.add_argument("--"+name,type=Path,required=True)
    ap.add_argument("--index",type=int,required=True)
    ap.add_argument("--account-login",type=int,required=True)
    ap.add_argument("--magic",type=int,default=5559)
    args=ap.parse_args()
    snapshot=emit_snapshot(args.archive,args.old_npz,args.event_npz,
                           args.priority_npz,args.candidate_csv,
                           args.index,args.account_login,args.magic)
    # One compact serialized decision only. No regenerated raw data.
    print(json.dumps(snapshot,separators=(",",":"),allow_nan=False))


if __name__=="__main__":
    main()
