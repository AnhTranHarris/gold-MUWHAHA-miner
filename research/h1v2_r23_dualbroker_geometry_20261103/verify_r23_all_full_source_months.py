"""Read-only R23 complete 8 source-month ×12 scenario / paired 9 quarter audit.

Validates archives and source SHA from original eight raw gzip bytes and joins
all quarter/hour/day reference calendars. Does not independently rerun every
million-quote first passage; prior source producer and tests remain required.
"""
from __future__ import annotations
import csv,hashlib,json
from pathlib import Path
from collections import defaultdict
import pandas as pd
import numpy as np
ROOT=Path('/mnt/data');R23=ROOT/'h1v2_r23_dualbroker';O=R23/'results'
SOURCES=['DUKASCOPY_RAW','MT5_BROKER_EXPORT'];MONTHS=['01','02','06','07']
ORIGINAL={'01':(27980,2976,744,31),'02':(33523,2688,672,28),'06':(31758,2880,720,30),'07':(24324,2976,744,31)}


def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for x in iter(lambda:f.read(1<<20),b''):h.update(x)
 return h.hexdigest()


def require(cond,description,checks):
 if not bool(cond):raise AssertionError(description)
 checks.append(description)


def run():
 checks=[];receipts=[];hashes={};allcases=[];pair=[]
 for src in SOURCES:
  for mon in MONTHS:
   ident=f'{src}_{mon}';f=O/f'R23_{ident}_FULL_SOURCE_EXACT_SHA_AND_SCIENCE_RECEIPT.json'
   require(f.is_file(),ident+' eight source receipt exists',checks)
   receipt=json.loads(f.read_text());receipts.append(receipt)
   path=ROOT/(f'XAUUSD_DUKAS_2026_{mon}_ticks.csv.gz' if src=='DUKASCOPY_RAW' else f'XAUUSD_MT5_BROKER_2026_{mon}_ticks_ALL.csv.gz')
   h=sha(path);require(h==receipt['verified_source_SHA'],ident+' source raw exact SHA',checks)
   hashes[path.name]={'bytes':path.stat().st_size,'sha256':h}
   expected,q,hours,days=ORIGINAL[mon]
   require(receipt['r22_C10_original_hindsight_count']>expected,ident+' frozen R22 future selected count exceeds monthly comparator',checks)
   require(receipt['completed_scenarios']==12,ident+' 12 H1V2 policy scenarios',checks)
   require(receipt['complete_month_quarters_per_scenario']==q,ident+' complete quarter count',checks)
   require(receipt['complete_month_hours_per_scenario']==hours,ident+' complete hour count',checks)
   for name,item in receipt['source_results'].items():
    output=O/name
    require(output.is_file() and output.stat().st_size==item['bytes'] and sha(output)==item['sha256'],ident+' SHA '+name,checks)
   cases=pd.read_csv(O/f'R23_{ident}_CASES.csv',keep_default_na=False)
   qdf=pd.read_csv(O/f'R23_{ident}_COMPLETE_QUARTERS.csv',keep_default_na=False)
   hdf=pd.read_csv(O/f'R23_{ident}_COMPLETE_HOURS.csv',keep_default_na=False)
   ddf=pd.read_csv(O/f'R23_{ident}_COMPLETE_DAYS.csv',keep_default_na=False)
   require(len(cases)==12,ident+' exact 12 scenario rows',checks)
   require(len(qdf)==12*q,ident+' all 12 × 15min rows',checks)
   require(len(hdf)==12*hours,ident+' all 12 × hourly rows',checks)
   require(len(ddf)==12*days,ident+' all 12 × daily rows',checks)
   for k,case in cases.iterrows():
    nm=case['scenario'];qa=qdf[qdf.scenario==nm];ha=hdf[hdf.scenario==nm];da=ddf[ddf.scenario==nm]
    require(len(qa)==q and len(ha)==hours and len(da)==days,ident+' '+nm+' every calendar slice',checks)
    require(qa.utc_quarter.is_unique and ha.utc_hour.is_unique and da.utc_day.is_unique,ident+' '+nm+' unique UTC keys',checks)
    require(int(qa.original_R9_SYNTH_reference.sum())==expected,ident+' '+nm+' R9 source reference monthly equality',checks)
    require(int(ha.R9_SYNTH_hour_reference.sum())==expected and int(da.R9_SYNTH_day_reference.sum())==expected,ident+' '+nm+' hour/day exact quota equality',checks)
    require(int(qa.R23_after.sum())==int(case.historical_future_selected_after_exchange),ident+' '+nm+' complete selected trade count',checks)
    require(int(ha.R23_hindsight_after.sum())==int(case.historical_future_selected_after_exchange),ident+' '+nm+' hourly trade count',checks)
    require(int(da.R23_hindsight_day_after.sum())==int(case.historical_future_selected_after_exchange),ident+' '+nm+' daily trade count',checks)
    require(int((qa.R23_after>=qa.original_R9_SYNTH_reference).where(qa.original_R9_SYNTH_reference>0,False).sum())==int(case.active_quarter_count_met),ident+' '+nm+' fulfilled actual active 15m quotas',checks)
    require(int((ha.R23_hindsight_after>=ha.R9_SYNTH_hour_reference).where(ha.R9_SYNTH_hour_reference>0,False).sum())==int(case.active_hour_count_met),ident+' '+nm+' fulfilled actual active hourly quotas',checks)
    require(int(qa.R23_quarter_deficit.sum())==int(case.quarter_deficit_slots),ident+' '+nm+' sum of all deficits',checks)
    require(np.all(qa.R23_after.to_numpy()>=qa.R22_C10_before.to_numpy()),ident+' '+nm+' no original quarter regression',checks)
    require(np.all(np.add.reduceat(qa.original_R9_SYNTH_reference.to_numpy(),np.arange(0,q,4))==ha.R9_SYNTH_hour_reference.to_numpy()),ident+' '+nm+' exact 15m->hour source clock join',checks)
    require(np.all(np.add.reduceat(qa.R23_after.to_numpy(),np.arange(0,q,4))==ha.R23_hindsight_after.to_numpy()),ident+' '+nm+' 15m->hour model output join',checks)
    require(np.all(np.add.reduceat(qa.R23_after.to_numpy(),np.arange(0,q,96))==da.R23_hindsight_day_after.to_numpy()),ident+' '+nm+' quarter->day source join',checks)
    require(np.all(np.add.reduceat(qa.original_R9_SYNTH_reference.to_numpy(),np.arange(0,q,96))==da.R9_SYNTH_day_reference.to_numpy()),ident+' '+nm+' original quota daily join',checks)
   allcases+=cases.to_dict('records')
   with np.load(O/f'R23_{ident}_ALL_12_CASES_SOURCE_ORDINAL_OUTCOMES_BOTH_SIDES_POSITIVE_NEGATIVE_CENSORED.npz',allow_pickle=False) as z:
    for case in cases.itertuples(index=False):
     nm=case.scenario
     code=z[nm+'__both_side_stop_target_timeout_censor_code'];ends=z[nm+'__both_side_actual_observed_exit_quote_ordinal'];nets=z[nm+'__both_side_quoted_price_net_after_entry_exit_slip_and_fee']
     fills=z[nm+'__actual_fill_quote_ordinal']
     require(code.shape==(len(fills),2) and ends.shape==code.shape and nets.shape==code.shape,ident+' '+nm+' full both-side ordinal source trace shape',checks)
     require(int((code==1).sum())==int(case.raw_two_sided_GOOD) and int((code==0).sum())==int(case.raw_two_sided_STOP) and int((code==2).sum())==int(case.raw_two_sided_TIMEOUT) and int((code==-3).sum())==int(case.raw_two_sided_CENSORED),ident+' '+nm+' all positive/negative/censored source labels',checks)
     require(np.all(np.isin(code,[-3,0,1,2])),ident+' '+nm+' all outcomes admissible',checks)
     require(np.all(ends[code==-3]==-1) and np.all(ends[code!=-3]>=0),ident+' '+nm+' no fake source-end fills',checks)
     require(int((code==1).sum())==int(case.future_good_interval_offline_count),ident+' '+nm+' future-winner enumeration matches labels',checks)
   # Paired source quarters exist only in original 02/06/07 R21 failure calendars.
   if mon!='01':
    p=O/f'R23_PAIRED_{ident}_RECEIPT.json';require(p.exists(),ident+' paired broker receipt exists',checks)
    pp=json.loads(p.read_text());n=pp['nine_source_quarter_subset_count']
    require(n=={'02':4,'06':1,'07':4}[mon],ident+' exact expected failing UTC matched periods',checks)
    for name,item in pp['outputs'].items():
     f=O/name;require(f.is_file() and f.stat().st_size==item['bytes'] and sha(f)==item['sha256'],ident+' paired actual SHA '+name,checks)
    matched=pd.read_csv(O/f'R23_PAIRED_{ident}_ALL_ORIGINAL_R21_DEFICIT_QUARTER_5_EXPERIMENTS.csv',keep_default_na=False)
    require(len(matched)==5*n,ident+' paired all matching 5 case rows',checks)
    require(set(matched.source)=={src} and set(matched.scenario)=={
       'STRICT_QUOTE_TP100_H60_CAP4000_LAG100','NEW_QUOTE_TP050_H90_CAP4000_LAG100',
       'NEW_QUOTE_TP050_H90_CAP8000_LAG100','NEW_QUOTE_TP050_H90_CAP4000_LAG500_SLIP20',
       'LOW_TARGET_Q1_TP025_H120_CAP4000_LAG100'},ident+' paired scenarios and source identity',checks)
    pair+=matched.to_dict('records')
 out={'validated_independent_result_checks':len(checks),'failures':0,'source_months':len(receipts),
  'exact_archived_raw_sha256':hashes,'full_source_scenario_rows':len(allcases),'paired_original_R21_quarter_scenario_rows':len(pair),
  'full_calendar_quarter_scenario_rows_per_broker':11520*12,'full_calendar_hour_scenario_rows_per_broker':2880*12,
  'full_calendar_day_scenario_rows_per_broker':120*12,'original_R9_synth_UTC_monthly_counts':{m:v[0] for m,v in ORIGINAL.items()},
  'one_position_asserted_by_producer':'r21 local_capacity and r23 producer',
  'full_raw_tick_first_passage_independently_recomputed_by_this_assembler':False,
  'confirmed_no_original_source_overwritten':True,
  'future_informed_retrospective_winners_are_not_causal':True,
  'pass_check_text_all':checks}
 outfile=R23/'R23_COMPLETE_EIGHT_SOURCE_INDEPENDENT_RECEIPT.json'
 outfile.write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps({'checks':len(checks),'source_months':len(receipts),'full_scenario_rows':len(allcases),'paired_rows':len(pair)},indent=2))
 return out

if __name__=='__main__':run()
