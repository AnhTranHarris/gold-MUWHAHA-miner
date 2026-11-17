"""Score a previously frozen positive-only MICRO180 entry model on later Coinexx ticks."""
from __future__ import annotations
import argparse,csv,gzip,hashlib,json,sys
from pathlib import Path
from positive_entry_model import SRC, load_targets,replay,evaluate_intents,sha256_file,input_files

def main():
 p=argparse.ArgumentParser()
 p.add_argument('--model',required=True,type=Path)
 p.add_argument('--month',required=True)
 p.add_argument('--days',type=int,default=2,help='bounded chronological prefix of later month')
 p.add_argument('--outdir',type=Path,required=True)
 a=p.parse_args()
 a.outdir.mkdir(parents=True,exist_ok=True)
 m=json.loads(a.model.read_text())
 t=load_targets(SRC/f'R9_POSITIVE_TARGET_ATLAS_{a.month}.zip')
 days=sorted(set(x['day'] for x in t))[:a.days]
 assert days,'empty later month'
 for month in (m.get('specialists') or [m]):
  assert max(month['date_window']) < min(days),'future or same-month model leaks into forward test'
 intents,trace=replay(m,days)
 match=evaluate_intents(intents,t,days)
 result={'version':'micro180-rb1-frozen-entry-forward','month':a.month,'days':days,
   'prior_model_path':a.model.name,'prior_model_sha256':sha256_file(a.model),
   'source_tick_shas':{p.name:sha256_file(p) for p in input_files(days)},
   'source_target_zip_sha256':sha256_file(SRC/f'R9_POSITIVE_TARGET_ATLAS_{a.month}.zip'),
   'entry_intent_replay':trace,'target_entry_concordance':match,
   'no_teacher_timestamps_in_replay':True,'no_exit_or_hold_model':True,
   'is_real_tick_source':True,'model_frozen_before_first_forward_day':True}
 (a.outdir/f'micro180_rb1_frozen_forward_{a.month}.json').write_text(json.dumps(result,indent=2,sort_keys=True))
 with gzip.open(a.outdir/f'micro180_rb1_forward_intents_{a.month}.csv.gz','wt',newline='') as f:
  writer=csv.DictWriter(f,fieldnames=list(intents[0]) if intents else ['sec']);writer.writeheader();writer.writerows(intents)
 print(json.dumps({'month':a.month,'days':days,'replay':trace,'entry_concordance':{k:v for k,v in match.items() if k!='per_atomic_family'}},indent=2))
if __name__=='__main__':main()
