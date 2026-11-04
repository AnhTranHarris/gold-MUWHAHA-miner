#!/usr/bin/env python3
"""Independent preserved-output eight-source/calendar verifier. No trade profitability."""
from __future__ import annotations
import csv,hashlib,json,sys
from pathlib import Path
from collections import Counter,defaultdict
import numpy as np
ROOT=Path('/mnt/data'); LAB=ROOT/'h1v2_r22_nine_residual'; OUT=LAB/'results_v2'
MON={'01':(2976,744,31,27980),'02':(2688,672,28,33523),'06':(2880,720,30,31758),'07':(2976,744,31,24324)}
SOURCES=('DUKASCOPY_RAW','MT5_BROKER_EXPORT')

def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for ch in iter(lambda:f.read(1<<20),b''):h.update(ch)
 return h.hexdigest()

def read(p):return list(csv.DictReader(open(p,newline='')))

def run():
 checks=[];rows=[];filepins={};fail=[]
 for s in SOURCES:
  for mon,(nq,nh,nd,benchmark) in MON.items():
   pre=f'R22V2_{s}_{mon}'
   per=[OUT/(pre+'_'+label+'.csv') for label in ['ALL_SCENARIOS','ALL_UTC_QUARTERS','ALL_UTC_HOURS','ALL_UTC_DAYS']]
   npz=OUT/(pre+'_ALL_12_CASES_FULL_QUOTE_ORDINAL_POSITIVE_NEGATIVE_AND_CENSORED.npz')
   rec=OUT/(pre+'_SOURCE_EXACT_EXECUTION_RECEIPT.json')
   obj=json.loads(rec.read_text())
   scenarios=read(per[0]);quarters=read(per[1]);hours=read(per[2]);days=read(per[3]);names=[r['scenario'] for r in scenarios]
   checks.append([s,mon,'scenario_count',len(scenarios)==12])
   checks.append([s,mon,'no_duplicate_names',len(set(names))==12])
   checks.append([s,mon,'all_calendar_rows',len(quarters)==nq*12 and len(hours)==nh*12 and len(days)==nd*12])
   checks.append([s,mon,'scenario_receipt_reconcile',len(obj['scenarios'])==12 and obj['source']==s and obj['month']==mon])
   checks.append([s,mon,'reference_hash',all(p.exists() for p in per) and npz.exists()])
   for f in [*per,npz]:
    pin=obj['outputs'].get(f.name,{})
    okay=(f.stat().st_size==int(pin.get('bytes',-1)) and sha(f)==pin.get('sha256'))
    checks.append([s,mon,'member_sha_'+f.name,okay]);filepins[f.name]=pin
   with np.load(npz,allow_pickle=False) as z:
    for sce in scenarios:
     name=sce['scenario'];q=[r for r in quarters if r['scenario']==name];h=[r for r in hours if r['scenario']==name];d=[r for r in days if r['scenario']==name]
     qq=np.array([int(r['R9_SYNTH_reference']) for r in q]);qh=np.array([int(r['R22_hindsight_selected_count']) for r in q]);
     hr=np.array([int(r['R9_SYNTH_hour_reference']) for r in h]);hc=np.array([int(r['R22_hour_count']) for r in h]);
     dr=np.array([int(r['R9_SYNTH_day_reference']) for r in d]);dc=np.array([int(r['R22_day_count']) for r in d]);
     checks.append([s,mon,name+'_full_clock_quota',len(q)==nq and len(h)==nh and len(d)==nd and int(qq.sum())==benchmark])
     checks.append([s,mon,name+'_hour_day_exact_aggregation',np.array_equal(qq.reshape(-1,4).sum(axis=1),hr) and np.array_equal(qh.reshape(-1,4).sum(axis=1),hc) and np.array_equal(qq.reshape(-1,96).sum(axis=1),dr) and np.array_equal(qh.reshape(-1,96).sum(axis=1),dc)])
     c=int(((qq>0)&(qh>=qq)).sum());b=int(((hr>0)&(hc>=hr)).sum())
     checks.append([s,mon,name+'_quota_and_total',c==int(sce['active_quarter_quota_met']) and b==int(sce['active_hour_quota_met']) and sum(qh)==int(sce['future_known_monthly_selection'])])
     gf=z[name+'__source_exact_hindsight_final_fill'];ge=z[name+'__source_exact_hindsight_final_exit'];
     cf=z[name+'__fill'];codes=z[name+'__code_2side'];good=z[name+'__future_good_fill']
     checks.append([s,mon,name+'_source_ordinal_shapes',len(gf)==len(ge)==int(sce['future_known_monthly_selection']) and np.all(np.diff(gf)>0) and len(cf)==len(codes) and len(good)==int(sce['new_hindsight_winner_intervals'])])
     checks.append([s,mon,name+'_truth_partition',codes.shape==(len(cf),2) and sum(int((codes==k).sum()) for k in (1,0,2,-3))==2*len(cf) and (codes==1).sum()==int(sce['future_GOOD_two_sided']) and (codes==0).sum()==int(sce['observed_STOP_two_sided']) and (codes==2).sum()==int(sce['observed_TIMEOUT_two_sided']) and (codes==-3).sum()==int(sce['source_CENSORED_two_sided'])])
     if s=='MT5_BROKER_EXPORT':
      checks.append([s,mon,name+'_no_deficit_accounting',int(sce['active_quarter_quota_met'])==int(sce['active_quarters']) and len(cf)==0])
     if name.startswith('C00'):
      old=ROOT/'h1v2_r21_dualbroker/results'/f'R21E_{s}_{mon}_SCENARIOS.csv'
      original=next(r for r in read(old) if r['case']=='EVENT30_8_QUOTES_CAP4000')
      checks.append([s,mon,'frozen_R21_control',int(sce['active_quarter_quota_met'])==int(original['quarter_quota_met_after']) and int(sce['future_known_monthly_selection'])==int(original['future_selected_monthly_trade_count'])])
     rows.append({'source':s,'month':mon,'scenario':name,'R9_SYNTH_ref':benchmark,'future_hindsight_total':int(sce['future_known_monthly_selection']),
       'quarter_hit':c,'quarter_active':int(sce['active_quarters']),'hour_hit':b,'hour_active':int(sce['active_hours']),
       'day_hit':int(sum(int(r['R22_DAY_PASS']) for r in d if r['R22_DAY_PASS']!='')),
       'day_active':int(sum(int(r['R9_SYNTH_day_reference'])>0 for r in d)),
       'candidate_GOOD':int(sce['future_GOOD_two_sided']),'candidate_STOP':int(sce['observed_STOP_two_sided']),
       'candidate_TIMEOUT':int(sce['observed_TIMEOUT_two_sided']),'candidate_CENSORED':int(sce['source_CENSORED_two_sided']),
       'research_only_future_oracle':True})
 for c in checks:
  if not c[-1]:fail.append(c)
 result={'classification':'ARCHIVED_SOURCE_ROW_RECONCILIATION_NO_RAW_TICK_RECOMPUTE_IN_THIS_VERIFIER',
   'count_checks':len(checks),'passed':len(checks)-len(fail),'failed':len(fail),'fail_examples':fail[:25],
   'all_eight_raw_verified_separately':json.loads((LAB/'R22_EIGHT_RAW_SHA_VERIFICATION.json').read_text()),
   'eight_source_months':8,'full_two_broker_UTC_quarters':23040,'full_two_broker_UTC_hours':5760,
   'full_two_broker_UTC_days':240,'scenarios_per_source_month':12,
   'sum_not_identical_to_broker_account_PNL':True,'no_OOS_model_trained':True}
 output=LAB/'R22V2_INDEPENDENT_8_SOURCE_FULL_CALENDAR_AND_SHA_VERIFICATION.json'
 output.write_text(json.dumps(result,indent=2)+'\n');
 with (LAB/'R22V2_ALL_96_MONTH_SOURCE_SCENARIOS_AND_DAY_OUTCOMES.csv').open('w',newline='') as fp:
  w=csv.DictWriter(fp,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 print(json.dumps({'checks':len(checks),'pass':len(checks)-len(fail),'failed':len(fail),'all_raw_pins':sum(x['PASS'] for x in result['all_eight_raw_verified_separately'])},indent=2))
 if fail:sys.exit(3)
if __name__=='__main__':run()
