"""R18-S2 v1 non-destructive source receipt archives and complete SHA inventory."""
from pathlib import Path
import hashlib,json,zipfile
LAB=Path('/mnt/data/h1v2_r18_dualbroker')
P=LAB/'results_r18_S2_LATENCY_FRONTIER'
D=LAB/'archives_r18_s2_v1';D.mkdir(exist_ok=True)
def sha(x):
 h=hashlib.sha256()
 with x.open('rb') as f:
  for b in iter(lambda:f.read(4<<20),b''):h.update(b)
 return h.hexdigest()
def zipper(name,files):
 dest=D/name
 assert all(x.exists() for x in files)
 with zipfile.ZipFile(dest,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=4) as z:
  for f in files:z.write(f,arcname=f.name)
 with zipfile.ZipFile(dest) as z:
  assert z.testzip() is None
  assert set(z.namelist())=={f.name for f in files}
 return {'filename':dest.name,'size':dest.stat().st_size,'sha256':sha(dest),
         'members':{f.name:{'size':f.stat().st_size,'sha256':sha(f)} for f in files}}
res=[]
for src in ('DUKASCOPY_RAW','MT5_BROKER_EXPORT'):
 for mon in ('01','02','06','07'):
  tag=f'R18_S2_{src}_{mon}'
  f=[P/f'{tag}_12_RESEARCH_SCENARIO_ROWS.csv',P/f'{tag}_ALL_UTC_15MIN_12_SCENARIOS.csv',
     P/f'{tag}_ALL_UTC_HOURS_12_SCENARIOS.csv',P/f'{tag}_COMPLETE_REPACKED_SOURCE_SIGNAL_QUOTE_ORDINALS.npz',
     P/f'{tag}_SOURCE_AND_OUTPUT_SHA_RECEIPT.json',P/f'{tag}_INDEPENDENT_SOURCE_12_SCENARIOS_VERIFIED_V1.json']
  out=zipper(f'{tag}_COMPLETE_12_CASE_15MIN_HOURS_SELECTTRACE_VERIFIED_V1_20261103.zip',f)
  res.append(out);print('DONE',src,mon,out['size'],flush=True)
core=zipper('R18_S2_V1_EXECUTABLE_SOURCE_AND_INDEPENDENT_8_MONTH_VERIFIER_20261103.zip',
 [LAB/'src/r18_s2_latency_frontier.py',LAB/'verify_r18_s2_v1_repacked_source.py',
  LAB/'results_r18_S2_DUKAS_JAN_01.log',LAB/'results_r18_S2_DUKAS_FEB_02.log',
  LAB/'results_r18_S2_DUKAS_JUN_06.log',LAB/'results_r18_S2_DUKAS_JUL_07.log',
  LAB/'results_r18_S2_MT5_JAN_01.log',LAB/'results_r18_S2_MT5_FEB_02.log',
  LAB/'results_r18_S2_MT5_JUN_06.log',LAB/'results_r18_S2_MT5_JUL_07.log'])
man=D/'R18_S2_V1_8_MONTH_96_SCENARIO_COMPLETE_SHA256_MANIFEST.json'
man.write_text(json.dumps({'source_month_case_archives':res,'source_verification_code_log_bundle':core,
 'prior_R18_and_R18S1_untouched':True,'SOURCE_SELECTED_DELAY_REPACK_V1_COMPLETE_96_CASES':True,
 'v1_missing_full_independent_failed_source_trial_arrays':True,
 'all_15min_hour_rows_preserved':True,'offline_future_privileged_not_predictive':True},indent=2)+'\n')
print('SOURCE_EXACT_MANIFEST',man,sha(man),flush=True)
