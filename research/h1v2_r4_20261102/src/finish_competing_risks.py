"""Resume full-model R4 without repeating three already fitted July-withheld controls."""
import json,time
from pathlib import Path
import lightgbm as lgb
from four_month_competing_risks import load,score,fit,calibrate_threshold,MONTHS
ROOT=Path('/mnt/data/h1v2_r4/results')
def run():
 data=load(ROOT)
 record={'scope':'H1V2 R4 six quote mark side-independent strict first-three-sec teacher; no policy qualification','models':{},'scientific_status':'HINDSIGHT_TEACHER_CONTAMINATED_FIT_SEPARATE_FROM_JULY_UNSEEN'}
 for variant in ('baseline','counts','ordered'):
  model=lgb.Booster(model_file=str(ROOT/f'R4_{variant}_JULY_UNSEEN_model.txt'))
  scores={m:score(model,data[m],variant,m) for m in MONTHS}
  record['models'][f'{variant}_train_01_02_06_test_07']={'train_months':['01','02','06'],'july':scores['07'],'months':scores}
  (ROOT/'R4_HOLDOUT_COMPARISON.json').write_text(json.dumps(record,indent=2))
 model,elapsed=fit(data,('01','02'),'ordered',rounds=95,leaves=31)
 threshold,cal=calibrate_threshold(model,data,'ordered','06')
 july=score(model,data['07'],'ordered','07',threshold)
 model.save_model(str(ROOT/'R4_ordered_JANFEB_JUNE_CAL_model.txt'))
 record['models']['ordered_janfeb_june_cal_july_untouched']={'train_months':['01','02'],'calibration_month':'06','calibration':cal,'threshold':threshold,'july':july,'elapsed_seconds':elapsed}
 print('STRICT JUNE',cal,'threshold',threshold,'JULY',july['threshold_admitted'],flush=True)
 (ROOT/'R4_HOLDOUT_COMPARISON.json').write_text(json.dumps(record,indent=2))
 model,elapsed=fit(data,MONTHS,'ordered',rounds=160,leaves=63,learning=.12)
 insample={m:score(model,data[m],'ordered',m) for m in MONTHS}
 model.save_model(str(ROOT/'R4_ordered_ALL4_CONTAMINATED_MODEL.txt'))
 record['models']['ordered_all_4_contaminated_resubstitution']={'train_months':list(MONTHS),'elapsed_seconds':elapsed,'months':insample}
 (ROOT/'R4_HOLDOUT_COMPARISON.json').write_text(json.dumps(record,indent=2))
 print('ALL4 contaminated',[(m,insample[m]['top_rankings'][1]['strict_precision']) for m in MONTHS],flush=True)
if __name__=='__main__':run()
