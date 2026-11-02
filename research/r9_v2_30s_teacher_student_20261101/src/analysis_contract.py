#!/usr/bin/env python3
import json,math,glob
from pathlib import Path
import numpy as np,pandas as pd
R=Path('/mnt/data/v2_30s_teacher_training/results')
F={'01':23783,'02':28495,'06':27031,'07':20725}
output=[]
for source in ('coinexx','dukascopy'):
 for m in ('01','02','06','07'):
  d=pd.read_pickle(R/f'{source}_{m}_raw.pkl')
  f=json.loads((R/f'fold_{source}_{m}_summary.json').read_text())
  v=json.loads((R/f'volume_{source}_{m}_summary.json').read_text())
  duration=(d.exit_ms-d.entry_ms).to_numpy()
  byday=d.groupby('day_id').agg(n=('target','size'),quality=('target','mean'),pos=('target','sum'))
  high=d.nlargest(F[m],'net')
  oracle_quality=float(((high.net>.1)&(high.mfe>=.12)).mean())
  out={'source':source,'month':m,'population':len(d),'r9_synth_volume_floor':F[m],
       'source_candidate_quality':float(d.target.mean()),'source_candidate_win':float(d.win.mean()),
       'neutral_fraction':float(d.neutral.mean()),'entry_lifecycle_median_ms':int(np.median(duration)),
       'entry_lifecycle_p95_ms':int(np.quantile(duration,.95)),
       'fraction_exit_under_30s':float((duration<=30000).mean()),
       'oracle_best_floor_quality':oracle_quality,
       'oracle_best_floor_net':round(float(high.net.sum()),2),
       'teacher_max_available_good':int(d.target.sum()),
       'days_with_quality_ge_80_unfiltered':int((byday.quality>=.8).sum()),
       'days_in_source':len(byday),'prospective_fold_auc':f['test_auc_quality'],
       'prospective_strict_selected':f['selected_trades'],
       'prospective_volume_selected':v['selected_trades'],
       'prospective_volume_quality':v['quality_rate'],
       'prospective_volume_net':v['net'],
       'prospective_volume_pass':v['volume_pass'],
       'prospective_daily_pass':v['daily_80pct_pass'],
       'prospective_weekly_pass':v['weekly_80pct_pass'],
       'prospective_monthly_pass':v['monthly_80pct_pass'],
       'teacher_weight_used':v['calibration_teacher_weight'] if 'calibration_teacher_weight' in v else v['calibration']['teacher_weight']}
  output.append(out)
  print(source,m,'quality',round(d.target.mean(),3),'oracle',round(oracle_quality,3), 'volumeSel',v['selected_trades'],'selectedPrecision',round(v['quality_rate'],3),flush=True)
(R/'ALL_EIGHT_30S_SURVIVAL_AUDIT.json').write_text(json.dumps({'classification':'research_full_baseline_and_chronological_transfer_not_approved','result':output},indent=2))
pd.DataFrame(output).to_csv(R/'ALL_EIGHT_30S_SURVIVAL_AUDIT.csv',index=False)
