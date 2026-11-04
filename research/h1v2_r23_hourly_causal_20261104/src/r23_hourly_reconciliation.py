"""Additive source-exact R23 hourly / quarter-hour preservation and diagnostic study.

Reads *unchanged* complete source-month R23 archives. Computes independently
reconciled month/day/hour/quarter case records and a NON-TRADABLE hindsight
best-scenario-per-hour / quarter diagnostic. It must not select scenarios using
future labels as if they were a causal BUY/SELL/WAIT policy. None of the outputs
are cash PnL. January raw feeds independently rehashed if mounted.

Usage:
  python src/r23_hourly_reconciliation.py \
    --dukas '/mnt/data/R23_DUKASCOPY_RAW_COMPLETE_FOUR_MONTH_ALL_SCENARIOS_QUARTER_HOUR_DAY_BIDASK_ORDINALS_20261103.zip' \
    --mt5 '/mnt/data/R23_MT5_BROKER_EXPORT_COMPLETE_FOUR_MONTH_ALL_SCENARIOS_QUARTER_HOUR_DAY_BIDASK_ORDINALS_20261103.zip' \
    --out results
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import io
import json
from pathlib import Path
from zoneinfo import ZoneInfo
from datetime import datetime, timezone
from collections import defaultdict
from zipfile import ZipFile

MONTHS = ('01','02','06','07')
SRC = ('DUKASCOPY_RAW','MT5_BROKER_EXPORT')
R9_UTC_REF = {'01':27980,'02':33523,'06':31758,'07':24324}
ACTIVE_UTC_QUARTERS = 7521
ACTIVE_UTC_HOURS = 1917
SOURCE_SHA = {
 'DUKASCOPY_RAW':{
   '01':'d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5',
   '02':'ed3b3545c990c88d78519594c17c8915b0f679adcb0a94920ba7524f1f6d5c5d',
   '06':'34686ce53ba992dfb83ea35d555b6a4947a9216635853857c8bf11ce70c00ae2',
   '07':'e171e8c2fb59f3f4147a6f845eb68e664fa9c0f4815caa33acdbb42cc2f768b7'},
 'MT5_BROKER_EXPORT':{'01':'1307a75df5d635678de7691908600090a552f38543e0512187dcd7b37fbc66b8'}
}

def sha(path):
    with open(path,'rb') as f: return hashlib.file_digest(f,'sha256').hexdigest()

def parse_csv(z, member):
    return list(csv.DictReader(io.StringIO(z.read(member).decode('utf-8-sig'))))

def actual_session(iso):
    """Observer-labeled sessions only, NOT broker/prop trading permission.

    As-of IANA local clocks support seasonal DST. Session windows are explicit
    research buckets, not verified actual opens/closes of spot XAUUSD.
    """
    u=datetime.fromisoformat(iso.replace('Z','+00:00')).astimezone(timezone.utc)
    clocks={zone:u.astimezone(ZoneInfo(zone)).strftime('%Y-%m-%d %H:%M %Z') for zone in
            ('Australia/Sydney','Asia/Tokyo','Europe/London','America/New_York')}
    # Coarse research labels, not operating-permission facts.
    hr={zone:u.astimezone(ZoneInfo(zone)).hour for zone in clocks}
    tokyo=9 <= hr['Asia/Tokyo'] < 18
    london=8 <= hr['Europe/London'] < 17
    newyork=8 <= hr['America/New_York'] < 17
    sydney=8 <= hr['Australia/Sydney'] < 17
    labels=[n for n,b in [('SYDNEY_NOMINAL',sydney),('TOKYO_NOMINAL',tokyo),
                          ('LONDON_NOMINAL',london),('NEW_YORK_NOMINAL',newyork)] if b]
    return {'nominal_session':'|'.join(labels) or 'UNCLASSIFIED',
            'utc_weekday':u.strftime('%A'),'utc_hour':u.hour,
            'broker_operating_permission':'UNKNOWN',
            'prop_firm_rule':'UNKNOWN',
            'mt5_medium_high_calendar_vintage':'UNKNOWN',
            'forexfactory_medium_high_calendar_vintage':'UNKNOWN',
            'clock_reference':'UTC_OBSERVED_IANA_NOMINAL_NOT_MARKET_CALENDAR',
            'local_clocks':clocks}

def put_csv(p,rows):
    if not rows:raise ValueError('empty rows')
    p.parent.mkdir(parents=True,exist_ok=True)
    with open(p,'w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def at_best(rows,ref_key,value_key,period_key):
    """Best original FUTURE-SELECTED scenario, per bucket (not a coherent global strategy)."""
    grouped=defaultdict(list)
    for row in rows: grouped[row[period_key]].append(row)
    out=[]
    for k,rr in sorted(grouped.items()):
        refs={int(x[ref_key]) for x in rr}
        if len(refs)!=1 or len(rr)!=12:raise AssertionError(('inconsistent-period',k,refs,len(rr)))
        r=int(rr[0][ref_key]); winner=max(rr,key=lambda x:(int(x[value_key])>=r,int(x[value_key])-r,int(x[value_key]),-len(x['scenario'])))
        counts=[int(x[value_key]) for x in rr]
        out.append({'utc_bucket':k,'R9_SYNTH_UTC_reference':r,
                    'best_hindsight_scenario':winner['scenario'],
                    'best_hindsight_selected':int(winner[value_key]),
                    'scenario_count':len(rr),'number_scenarios_meeting_count':sum(v>=r for v in counts) if r else None,
                    'best_hindsight_count_deficit':max(0,r-int(winner[value_key])),
                    'source':winner['source'],'month':winner['month'],
                    'selection_uses_future':1,
                    'bucket_switching_may_violate_cross_boundary_occupancy':1,
                    'causal_accuracy_demonstrated':0,
                    'cash_pnl_demonstrated':0,
                    **{k2:v2 for k2,v2 in actual_session(k).items() if k2!='local_clocks'}})
    return out

def process_one(zip_path,src,mon,outroot,raw_jan=None):
    base=f'results/R23_{src}_{mon}_'; dest=Path(outroot)/src/mon
    with ZipFile(zip_path) as z:
        members={k:base+k for k in ('CASES.csv','COMPLETE_DAYS.csv','COMPLETE_HOURS.csv','COMPLETE_QUARTERS.csv')}
        for n in members.values():
            if n not in z.namelist():raise FileNotFoundError(n)
        cases=parse_csv(z,members['CASES.csv'])
        days=parse_csv(z,members['COMPLETE_DAYS.csv'])
        hours=parse_csv(z,members['COMPLETE_HOURS.csv'])
        quarters=parse_csv(z,members['COMPLETE_QUARTERS.csv'])
        if len(cases)!=12:raise AssertionError('not 12 scenarios')
        scenarios={x['scenario'] for x in cases}
        if len(scenarios)!=12:raise AssertionError('duplicate case')
        if any(x['source']!=src or x['month']!=mon for x in cases+days+hours+quarters):raise AssertionError('source-month mismatch')
        if any(x['source_quote_SHA']!=SOURCE_SHA[src][mon] for x in cases) if mon in SOURCE_SHA[src] else False:
            raise AssertionError('source SHA mismatch')
        n_days={'01':31,'02':28,'06':30,'07':31}[mon]
        exp={'days':n_days*12,'hours':n_days*24*12,'quarters':n_days*96*12}
        for kind,rows in [('days',days),('hours',hours),('quarters',quarters)]:
            if len(rows)!=exp[kind]:raise AssertionError(f'expected {exp[kind]} {kind}, got {len(rows)}')
        for case in cases:
            scenario=case['scenario'];d=[x for x in days if x['scenario']==scenario]
            h=[x for x in hours if x['scenario']==scenario]
            q=[x for x in quarters if x['scenario']==scenario]
            if len({x['utc_day'] for x in d})!=n_days or len({x['utc_hour'] for x in h})!=n_days*24 or len({x['utc_quarter'] for x in q})!=n_days*96:
                raise AssertionError('missing/duplicate calendar buckets')
            count=sum(int(x['R9_SYNTH_day_reference']) for x in d)
            if not (count==sum(int(x['R9_SYNTH_hour_reference']) for x in h)==sum(int(x['original_R9_SYNTH_reference']) for x in q)==R9_UTC_REF[mon]):
                raise AssertionError(('UTC reference mismatch',src,mon,scenario))
            if not (sum(int(x['R23_hindsight_day_after']) for x in d)==sum(int(x['R23_hindsight_after']) for x in h)==sum(int(x['R23_after']) for x in q)==int(case['historical_future_selected_after_exchange'])):
                raise AssertionError(('selected count mismatch',src,mon,scenario))
            if int(case['active_quarters'])!=sum(int(x['original_R9_SYNTH_reference'])>0 for x in q):raise AssertionError('active quarters mismatch')
            if int(case['active_hours'])!=sum(int(x['R9_SYNTH_hour_reference'])>0 for x in h):raise AssertionError('active hours mismatch')
            if int(case['active_quarter_count_met'])!=sum(int(x['R23_after'])>=int(x['original_R9_SYNTH_reference']) for x in q if int(x['original_R9_SYNTH_reference'])>0):raise AssertionError('quarter passes mismatch')
            if int(case['active_hour_count_met'])!=sum(int(x['R23_hindsight_after'])>=int(x['R9_SYNTH_hour_reference']) for x in h if int(x['R9_SYNTH_hour_reference'])>0):raise AssertionError('hour passes mismatch')
    month_c=at_best(cases,'r9_ref_month','historical_future_selected_after_exchange','month') if False else []
    # Preserve full original source tables and additive detailed best-case diagnostics.
    for kind,rows in [('original_cases',cases),('original_days',days),('original_hours',hours),('original_quarters',quarters)]:
        put_csv(dest/f'{src}_{mon}_{kind}.csv',rows)
    bh=at_best(hours,'R9_SYNTH_hour_reference','R23_hindsight_after','utc_hour')
    bq=at_best(quarters,'original_R9_SYNTH_reference','R23_after','utc_quarter')
    put_csv(dest/f'{src}_{mon}_best_hour_DIAGNOSTIC_NOT_POLICY.csv',bh)
    put_csv(dest/f'{src}_{mon}_best_quarter_DIAGNOSTIC_NOT_POLICY.csv',bq)
    raw_state='NOT_MOUNTED';raw_digest=None
    if raw_jan is not None and mon=='01':
        raw_digest=sha(raw_jan)
        if raw_digest!=SOURCE_SHA[src]['01']:raise AssertionError('independent January SHA mismatch')
        raw_state='CURRENT_RUN_INDEPENDENT_SHA_VERIFIED'
    receipt={'status':'R23_COMPLETE_MONTH_DAY_HOUR_QUARTER_ARCHIVED_RECONCILIATION_PASS',
      'research_class':'ARCHIVED_R23_HINDSIGHT_REAUDIT_NO_NEW_MODEL_FIT_NO_RAW_REPLAY',
      'source':src,'month':mon,'original_R9_source_aligned_reference':R9_UTC_REF[mon],
      'source_raw_SHA_recorded_in_archive':cases[0]['source_quote_SHA'],
      'source_raw_sha_independent_check_status':raw_state,
      'source_raw_sha_independent_current':raw_digest,
      'original_R23_archive_sha256':sha(zip_path),
      'scenario_rows':12,'day_rows':len(days),'hour_rows':len(hours),'quarter_rows':len(quarters),
      'all_12_scenarios_reconciled':True,
      'calendar_hour_count':len(bh),'calendar_quarter_count':len(bq),
      'hour_best_case_reference_active':sum(int(x['R9_SYNTH_UTC_reference'])>0 for x in bh),
      'quarter_best_case_reference_active':sum(int(x['R9_SYNTH_UTC_reference'])>0 for x in bq),
      'hour_best_case_optimistic_count_meets':sum(int(x['best_hindsight_selected'])>=int(x['R9_SYNTH_UTC_reference']) for x in bh if int(x['R9_SYNTH_UTC_reference'])>0),
      'quarter_best_case_optimistic_count_meets':sum(int(x['best_hindsight_selected'])>=int(x['R9_SYNTH_UTC_reference']) for x in bq if int(x['R9_SYNTH_UTC_reference'])>0),
      'wrong_positives_and_stop_cases_PRESERVED_IN_ORIGINAL_R23_NPZ':True,
      'best_case_is_future_bucket_switching_unexecutable':True,
      'medium_high_news_point_in_time_vintage':'UNKNOWN',
      'broker_and_prop_hours_permission':'UNKNOWN',
      'no_new_tradable_hindsight_result':True}
    receipt['outputs']={p.name:{'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(dest.glob('*.csv'))}
    with open(dest/f'{src}_{mon}_ATOMIC_RECEIPT.json','w') as f:json.dump(receipt,f,indent=2)
    return receipt,bh,bq

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--dukas',required=True);p.add_argument('--mt5',required=True)
    p.add_argument('--out',required=True);p.add_argument('--dukas-jan');p.add_argument('--mt5-jan')
    args=p.parse_args();dst=Path(args.out);dst.mkdir(exist_ok=True,parents=True)
    allrec=[];bhall=[];bqall=[]
    for src,z,raw in [('DUKASCOPY_RAW',args.dukas,args.dukas_jan),('MT5_BROKER_EXPORT',args.mt5,args.mt5_jan)]:
        if ZipFile(z).testzip() is not None:raise ValueError('ZIP CRC FAILED')
        for mon in MONTHS:
            rec,bh,bq=process_one(z,src,mon,dst,raw)
            allrec.append(rec);bhall.extend(bh);bqall.extend(bq)
            print('ATOMIC_MONTH_PASS',src,mon,'hour',rec['hour_best_case_optimistic_count_meets'],'quarter',rec['quarter_best_case_optimistic_count_meets'],flush=True)
    for src in SRC:
        rr=[x for x in allrec if x['source']==src]
        if sum(x['hour_best_case_reference_active'] for x in rr)!=ACTIVE_UTC_HOURS:raise AssertionError('global hourly active mismatch')
        if sum(x['quarter_best_case_reference_active'] for x in rr)!=ACTIVE_UTC_QUARTERS:raise AssertionError('global quarter active mismatch')
        if sum(x['original_R9_source_aligned_reference'] for x in rr)!=117585:raise AssertionError('global UTC volume reference mismatch')
    put_csv(dst/'ALL_TWO_SOURCE_FOUR_MONTH_BEST_HOUR_DIAGNOSTIC.csv',bhall)
    put_csv(dst/'ALL_TWO_SOURCE_FOUR_MONTH_BEST_QUARTER_DIAGNOSTIC.csv',bqall)
    result={'classification':'HISTORICAL_R23_12_SCENARIO_REAUDIT_AND_OPTIMISTIC_PER_BUCKET_UPPER_ONLY','no_new_source_quote_engine_run':True,
      'no_model_fit':True,'no_causal_entry_accuracy':True,'all_wrong_negative_cases_retained_in_immutable_source_NPZ':True,
      'source_months':allrec,'tallies':{s:{'active_hours':ACTIVE_UTC_HOURS,'active_quarters':ACTIVE_UTC_QUARTERS,
      'hour_any_original_scenario_meets':sum(x['hour_best_case_optimistic_count_meets'] for x in allrec if x['source']==s),
      'quarter_any_original_scenario_meets':sum(x['quarter_best_case_optimistic_count_meets'] for x in allrec if x['source']==s)} for s in SRC}}
    f=dst/'R23_ALL_8_SOURCE_MONTHS_INDEPENDENT_AUDIT_MANIFEST.json';f.write_text(json.dumps(result,indent=2)+'\n')
    print('COMPLETE_EIGHT_MONTH_SCENARIO_AUDIT',json.dumps(result['tallies'],indent=2))

if __name__=='__main__':main()
