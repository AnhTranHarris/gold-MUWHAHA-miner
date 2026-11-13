"""Post-holdout full nine-month refit for SHADOW-ONLY future observation.

MUST NOT run before the frozen P5 September evaluation has been written.
This is a sixth, deployment-unapproved refit for later unseen observations,
not a sixth evaluation or a claim of any out-of-sample profit.
"""
from __future__ import annotations
import argparse,hashlib,json,platform,sys
from pathlib import Path
import joblib,numpy as np,pandas as pd,sklearn
from train import RUNS,create_model,colnames,month_data


def main():
 p=argparse.ArgumentParser()
 p.add_argument('--input-dir',type=Path,default=Path('/mnt/data/r9_shadow_path_signatures/outputs'))
 p.add_argument('--output-dir',type=Path,default=Path('/mnt/data/r9_shadow_path_signatures/models'))
 args=p.parse_args()
 original=args.input_dir/'source_receipt.json'
 last=args.output_dir/'P5_receipt.json'
 for path in (original,last):
  if not path.is_file():raise FileNotFoundError(f'cannot refit before complete source/P5 holdout: {path}')
 receipt=json.loads(original.read_text())
 prev=json.loads(last.read_text())
 if receipt.get('completed_months') != [f'{m:02d}' for m in range(1,10)]:
  raise ValueError('not all nine raw Coinexx source months were completed')
 if prev.get('evaluation_month') != '2026-09':
  raise ValueError('P5 September holdout must be completed before full-fit')
 frames=[month_data(args.input_dir,f'{m:02d}') for m in range(1,10)]
 full=pd.concat(frames,ignore_index=True).sort_values('entry_time_msc',kind='stable')
 if len(full)!=receipt['candidate_rows'] or full.entry_ordinal.nunique()!=len(full):
  raise ValueError('full-month candidate cache not in one-to-one agreement with source receipt')
 spec=RUNS[-1]
 columns=colnames(spec['feature'])
 fee=int(prev['cost_per_trade_quoted_price_u'])
 X=full[columns].to_numpy(dtype=float)
 y=(full.net_price_u.to_numpy()>fee).astype(int)
 model=create_model(spec)
 model.fit(X,y)
 dest=args.output_dir/'FROZEN_ALL9_SHADOW_ONLY_UNAPPROVED.joblib'
 joblib.dump({'pipeline':model,'feature_names':columns,
  'training_months':[f'2026-{m:02d}' for m in range(1,10)],
  'evaluation_months_after_refit':[],
  'quote_price_cost_u':fee,
  'classification':'SHADOW_ONLY_UNAPPROVED_NO_UNSEEN_TEST_AFTER_REFIT',
  'r9_source_blob_sha':'7eecb5f1947017a01ce85b2520725de54749e523',
  'raw_coinexx_sha256':{k:v['source_sha256'] for k,v in receipt['source_months'].items()}},dest,compress=3)
 data={
  'kind':'post_september_full_nine_month_refit',
  'status':'UNAPPROVED_SHADOW_ONLY',
  'all_nine_months_only_training':True,
  'future_month_evaluation':'NOT_DONE',
  'source_raw_ticks':receipt['total_rows'],
  'baseline_entry_samples':len(full),
  'train_positive_fraction_after_modeled_cost':float(y.mean()),
  'features':columns,'feature_count':len(columns),
  'cost_per_trade_quote_price_u':fee,
  'model_sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),
  'model_filename':dest.name,
  'python':platform.python_version(),
  'numpy':np.__version__,'pandas':pd.__version__,'sklearn':sklearn.__version__,
  'source_receipt_sha256':hashlib.sha256(original.read_bytes()).hexdigest(),
  'five_pass_results_sha256':hashlib.sha256((args.output_dir/'five_pass_results.json').read_bytes()).hexdigest(),
  'warning':'This model has no later untouched holdout. Prior P1-P5 failed economic acceptance. No MT5 deployment.'}
 (args.output_dir/'FULL_NINE_REFIT_SHADOW_RECEIPT.json').write_text(json.dumps(data,indent=2)+'\n')
 print('FULL NINE-MONTH POST-HOLDOUT REFIT COMPLETED',len(full),dest.stat().st_size,flush=True)

if __name__=='__main__':main()
