"""Append-only MICRO180 positive-entry specialists, one chronologically complete month at a time.

No cross-month re-fitting, no result reclassification, no transferred V28 weights.
Each specialist retains its own robust scales/centroids, regime/phase hours,
and historical source hashes. Forward evaluation must happen BEFORE append.
"""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
from positive_entry_model import FEATURE_KEYS,sha256_file

def append(previous:list[dict],new:dict,forward_receipt:dict|None):
 if new['input_features']!=list(FEATURE_KEYS):raise ValueError('feature schema drift')
 if not new['uses_R9_entry_timestamp_at_inference'] is False:raise ValueError('teacher time leak')
 if not new['uses_R9_exit_at_inference'] is False:raise ValueError('exit leak')
 start=min(new['date_window']);stop=max(new['date_window'])
 if previous and max(max(x['date_window']) for x in previous)>=start:
  raise ValueError('append chronological order wrong or overlapping')
 if previous and forward_receipt is None:raise ValueError('forward receipt required before adding later month')
 if forward_receipt is not None:
  if min(forward_receipt['days'])<start or max(forward_receipt['days'])>stop:raise ValueError('forward month mismatch')
  if not forward_receipt['model_frozen_before_first_forward_day']:raise ValueError('forward test not frozen')
  if not forward_receipt['no_teacher_timestamps_in_replay']:raise ValueError('leaking forward method')
 return {'version':'micro180-rb1-append-only-positive-entry','input_features':list(FEATURE_KEYS),
   'specialists':previous+[new],
   'retrospective_positive_families':23,'non_additive_parent_rollups':4,
   'uses_historical_profit_in_entry_policy':False,'holds_and_exits_implemented':False,
   'same_second_r9_teacher_concordance_is_only_scoring_goal':True}

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--prior',type=Path,required=True)
 ap.add_argument('--new',type=Path,required=True);ap.add_argument('--forward',type=Path,required=True)
 ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
 pri=json.loads(a.prior.read_text());new=json.loads(a.new.read_text())
 f=json.loads(a.forward.read_text())
 if f['prior_model_sha256']!=sha256_file(a.prior):raise ValueError('forward test model hash does not match existing frozen prior')
 previous=pri['specialists'] if 'specialists' in pri else [pri]
 x=append(previous,new,f)
 x['lineage']={'prior_model_sha256':sha256_file(a.prior),'new_model_sha256':sha256_file(a.new),
   'forward_receipt_sha256':sha256_file(a.forward),'months':[m['date_window'][0][:7] for m in x['specialists']]}
 a.out.parent.mkdir(parents=True,exist_ok=True)
 a.out.write_text(json.dumps(x,separators=(',',':'),sort_keys=True))
 print(json.dumps({'merged_months':x['lineage']['months'],'independent_atomic_side_experts':sum(len(m['models']) for m in x['specialists']),
 'prior_checksum':x['lineage']['prior_model_sha256'],'merged_checksum':sha256_file(a.out)}))
if __name__=='__main__':main()
