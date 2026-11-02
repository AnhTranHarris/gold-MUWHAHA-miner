"""Source/month/day-agnostic corrected R9 v2 research shard builder.

One invocation creates the direction-neutral observed-250ms teacher universe, the
228-column v5 causal feature matrix and the 213-column direct WAIT transition view
from the same source-exact raw feed. It supports Coinexx and Dukascopy without
renaming code or binding to a machine-specific path.
"""
from __future__ import annotations
import argparse,datetime as dt,hashlib,json,time
from pathlib import Path
import numpy as np
from build_repaired_matrix import load_raw
from full_250ms_universe import replay_candidate_pairs,timing_labels,FEE,HOLD_MS
from raw_repaired_features import candidate_indices_250ms,build_repaired_raw_features
from repaired_features import FEATURE_VERSION,REPAIRED_FEATURE_COUNT,REPAIRED_FEATURE_NAMES
from timing_transition_features import build_timing_features,wait_improves_target,TIMING_FEATURE_VERSION,TIMING_FEATURE_COUNT
from path_config import artifact_stem

def sha256(p:Path):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for c in iter(lambda:f.read(1<<20),b''):h.update(c)
 return h.hexdigest()

def day_bounds(day):
 d=dt.datetime.strptime(day,'%Y-%m-%d').replace(tzinfo=dt.timezone.utc);lo=int(d.timestamp()*1000);return lo,lo+86400000

def build(raw,source,month,day,out,warmup_ms=300000,max_spread=1.50,chunk_rows=25000):
 start=time.monotonic();raw=Path(raw);out=Path(out);out.mkdir(parents=True,exist_ok=True);source=source.lower();month=str(month).zfill(2);stem=artifact_stem(source,month,day)
 t,bid,ask=load_raw(raw,source,month);idx=candidate_indices_250ms(t,bid,ask,warmup_ms,max_spread);lo,hi=day_bounds(day);idx=idx[(t[idx]>=lo)&(t[idx]<hi)]
 if len(idx)==0:raise ValueError('no source candidates for requested day')
 net,good,neutral,cause,exit_ms,duration,mfe,mae,fg,fb=replay_candidate_pairs(t,bid,ask,idx,FEE,HOLD_MS);timing=timing_labels(t[idx],good,net)
 teacher=out/f'{stem}_250ms_universe.npz';np.savez_compressed(teacher,idx=idx,ts=t[idx],bid=bid[idx],ask=ask[idx],net=net,good=good,neutral=neutral,cause=cause,exit_ms=exit_ms,duration=duration,mfe=mfe,mae=mae,first_good_ms=fg,first_bad_ms=fb,**timing)
 valid=np.isfinite(net).all(axis=1);anygood=good.any(axis=1)
 X=build_repaired_raw_features(t,bid,ask,idx,chunk_rows);entry=out/f'{stem}_250ms_v5_X.npy';np.save(entry,X,allow_pickle=False)
 T=build_timing_features(X,t[idx]);wait=out/f'{stem}_wait_transition_X.npy';np.save(wait,T,allow_pickle=False);wy,wvalid=wait_improves_target({'good':good,'next_dt_ms':timing['next_dt_ms'],'next_any_good':timing['next_any_good']},1000)
 receipt=dict(source=source,month=month,day=day,raw_tick_sha256=sha256(raw),candidates=len(idx),valid_pair_outcomes=int(valid.sum()),buy_strict_good=int(good[:,0].sum()),sell_strict_good=int(good[:,1].sum()),any_strict_good=int(anygood.sum()),any_strict_good_rate=float(anygood.mean()),both_strict_good=int((good.sum(axis=1)==2).sum()),teacher_sha256=sha256(teacher),entry_feature_version=FEATURE_VERSION,entry_features=REPAIRED_FEATURE_COUNT,entry_sha256=sha256(entry),timing_feature_version=TIMING_FEATURE_VERSION,timing_features=TIMING_FEATURE_COUNT,timing_sha256=sha256(wait),direct_wait_improves_positive=int(wy.sum()),direct_wait_improves_rate=float(wy.mean()),next_within_1000ms=int(wvalid.sum()),historical_250ms_sell_bug_teacher_used=False,same_millisecond_later_source_records_used=True,old_specialist_direction_nomination_used=False,runtime_uses_future=False,overlapping_teacher_candidates_are_not_filled_trades=True,elapsed_sec=round(time.monotonic()-start,2))
 rp=out/f'{stem}_domain_shard_receipt.json';rp.write_text(json.dumps(receipt,indent=2));return receipt

def main(a):print(json.dumps(build(a.raw,a.source,a.month,a.day,a.out,a.warmup_ms,a.max_spread,a.chunk_rows),indent=2))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--source',choices=('coinexx','dukascopy'),required=True);p.add_argument('--month',required=True);p.add_argument('--day',required=True);p.add_argument('--raw',required=True);p.add_argument('--out',required=True);p.add_argument('--warmup-ms',type=int,default=300000);p.add_argument('--max-spread',type=float,default=1.50);p.add_argument('--chunk-rows',type=int,default=25000);main(p.parse_args())