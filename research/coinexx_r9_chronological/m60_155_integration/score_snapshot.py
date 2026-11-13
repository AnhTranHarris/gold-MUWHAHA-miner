"""R9 v1.94 archived 155-feature DIRECT LightGBM score sender.

Consumes an EXACT precomputed as-of 155-float input vector via JSONL.
It DOES NOT invent 155 features from ATR/EMA or re-train any model.
Persistent process: model loaded ONCE and one atomic tiny score packet per
candidate. This is an integration test / shadow transport, NOT a live
feature-producer, strategy tester, or demonstrated profitable gate.

DO NOT unpickle an archive unless it is the trusted owner-pinned Drive ZIP.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import os
import re
import sys
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np

SCHEMA = "R9_M60_155_20261113_V1"
PACKET = "R9M60_155_V1"
EXPECTED = {
    "fold05": ("models/direct_test_05_shadow.joblib",
               "48c3e3898aab1a78cc5f3b0fec45137af23f2267a4ef665a73eb1e1c431ed661"),
    "fold06": ("models/direct_test_06_shadow.joblib",
               "bdeb8c4ccc8b6523c3c2cf1185104162c5bf2e3f45271c42c521e50e660ec121"),
    "fold07": ("models/direct_test_07_shadow.joblib",
               "bd4c886a470cecac663f5cb71889f195148fa2ef3da932cfce02c361c873e1c5"),
    "fold08": ("models/direct_test_08_shadow.joblib",
               "b23e84ed6d9d34b68e5496c71304b76c5db8be8b81be85975ea5dcd1f4df830f"),
    "fold09": ("models/direct_test_09_shadow.joblib",
               "8d6bb3c41741a2223494a8ec87314e9e8d7ea93634ab83498dd133fe7a187d06"),
    "final_is": ("models/direct_all_JanSep_IS_ONLY.joblib",
                 "09e1f1b9514dd18bbf6966055e2c277da3695d43cd4c861f997f5ad2c5d75b2f"),
}


def load_trusted_model(archive_path: Path, model_id: str):
    """Hash pin BEFORE trusted owner-only pickle load."""
    name, expected_hash = EXPECTED[model_id]
    with zipfile.ZipFile(archive_path) as z:
        if z.testzip() is not None:
            raise ValueError("Model ZIP CRC verification failed")
        data = z.read(name)
    digest = hashlib.sha256(data).hexdigest()
    if digest != expected_hash:
        raise ValueError("Model SHA256 does not match immutable original receipt")
    # joblib.load uses pickle; only a trusted, pinned owner archive is allowed.
    model_data = joblib.load(io.BytesIO(data))
    model = model_data["model"]
    if getattr(model, "n_features_in_", None) != 155:
        raise ValueError("Original model has wrong feature count")
    if list(model.classes_) != [0, 1]:
        raise ValueError("Original model has wrong class order")
    return model, digest


def _entry_month(time_msc: int) -> tuple[int, int]:
    dt = datetime.fromtimestamp(time_msc / 1000.0, tz=timezone.utc)
    return dt.year, dt.month


def validate_snapshot(s: dict, model_id: str) -> np.ndarray:
    if not isinstance(s, dict):
        raise ValueError("Snapshot must be a JSON object")
    if s.get("schema_id") != SCHEMA or s.get("market_source") != "Coinexx":
        raise ValueError("Only exact Coinexx 155-feature schema accepted")
    if s.get("feature_origin") != "FROZEN_EXACT_ASOF":
        raise ValueError("Feature vector provenance must be source-ordinal as-of")
    for field in ("time_msc", "feature_end_time_msc", "source_ordinal",
                  "account_login", "magic", "bid_cents", "ask_cents", "side"):
        if type(s.get(field)) is not int:
            raise ValueError(f"{field} must be integer")
    tm = s["time_msc"]
    if s["feature_end_time_msc"] != tm or tm<=0 or s["source_ordinal"]<=0:
        raise ValueError("Past-only feature/entry timestamp or ordinal invalid")
    if s["account_login"]<=0 or s["magic"]<0:
        raise ValueError("Account or magic invalid")
    if not re.fullmatch(r"[A-Za-z0-9_.-]{1,40}", str(s.get("symbol", ""))):
        raise ValueError("Symbol is invalid")
    if s["bid_cents"]<=0 or s["ask_cents"]<s["bid_cents"]:
        raise ValueError("Invalid executable-side quote")
    if s["side"] not in (-1,1):
        raise ValueError("Side must be original R9 +/-1")
    yyyy, mm = _entry_month(tm)
    if model_id == "final_is":
        if (yyyy, mm) <= (2026, 9):
            raise ValueError("Jan-Sep all-in-sample fit cannot score its OWN historical months as OOS")
    else:
        intended=int(model_id[-2:])
        if (yyyy,mm)!=(2026,intended):
            raise ValueError("Chronological fold model must score only its held-out historical month")
    values = s.get("features")
    if not isinstance(values,list) or len(values)!=155:
        raise ValueError("Must supply exactly 155 ordered model input columns")
    if any(x is not None and (isinstance(x,bool) or not isinstance(x,(int,float))) for x in values):
        raise ValueError("Features must be numerical or null for missing")
    x=np.asarray([np.nan if v is None else v for v in values],dtype=np.float32)
    if np.any(np.isinf(x)):
        raise ValueError("Infinite model features are invalid")
    return x.reshape(1,155)


def predict_one(model, model_sha: str, model_id: str, s: dict) -> tuple[float,list[str]]:
    x=validate_snapshot(s,model_id)
    p=float(model.predict_proba(x)[0,1])
    # Guard conversion and binary-class order; no arbitrary threshold here.
    if not math.isfinite(p) or not (0.0 <= p <=1.0):
        raise ValueError("Model inference returned non-finite probability")
    row=[
        PACKET,str(s["account_login"]),s["symbol"],str(s["magic"]),
        str(s["time_msc"]),str(s["bid_cents"]),str(s["ask_cents"]),
        str(s["side"]),"155",model_sha,
        ("direct_all_JanSep_IS_ONLY" if model_id=="final_is"
         else f"direct_test_{model_id[-2:]}_shadow"),
        str(s["feature_end_time_msc"]),str(s["source_ordinal"]),
        format(p,".12g"),"ASOF_PINNED",SCHEMA,
    ]
    return p,row


def packet_filename(s: dict) -> str:
    return f"R9_M60_155_{s['symbol']}_{s['account_login']}_{s['magic']}.csv"


def write_packet_atomic(out_dir: Path, filename: str, row: list[str]):
    """Replace ONE small current-score file, never append tick or score logs."""
    out_dir.mkdir(parents=True,exist_ok=True)
    tmp = None
    try:
        with tempfile.NamedTemporaryFile("w",newline="",encoding="ascii",
                                         dir=out_dir,prefix=".r9score-",
                                         suffix=".tmp",delete=False) as f:
            tmp=Path(f.name)
            writer=csv.writer(f,lineterminator="\n")
            writer.writerow(row)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp,out_dir/filename)
    finally:
        if tmp is not None and tmp.exists():
            tmp.unlink()


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--archive",type=Path,required=True,
                    help="Unmodified 155Features archived ZIP already on Google Drive")
    ap.add_argument("--model-id",choices=EXPECTED.keys(),required=True,
                    help="fold05..fold09 for exact held-out month, or final_is for post-Sep shadow ONLY")
    ap.add_argument("--packet-dir",type=Path,
                    help="MT5 Common/Files path, optional for integration shadow")
    ap.add_argument("--input",type=Path,
                    help="A JSONL file of exact, as-of 155-feature snapshots; default stdin")
    args=ap.parse_args()
    model,digest=load_trusted_model(args.archive,args.model_id)
    rows=0
    f=sys.stdin if args.input is None else args.input.open("r",encoding="utf-8")
    try:
        for line in f:
            if not line.strip():
                continue
            s=json.loads(line,parse_constant=lambda t: (_ for _ in ()).throw(
                ValueError(f"invalid numeric constant {t}")))
            p,row=predict_one(model,digest,args.model_id,s)
            if args.packet_dir is not None:
                write_packet_atomic(args.packet_dir,packet_filename(s),row)
            print(json.dumps({"time_msc":s["time_msc"],"side":s["side"],
                              "model_id":args.model_id,"model_sha256":digest,
                              "probability":p,"status":"SHADOW_SCORE_NOT_PNL"}),
                  flush=True)
            rows+=1
    finally:
        if f is not sys.stdin:
            f.close()
    print(f"R9_M60_COMPLETE snapshots={rows} no_model_training=true",
          file=sys.stderr)


if __name__=="__main__":
    main()
