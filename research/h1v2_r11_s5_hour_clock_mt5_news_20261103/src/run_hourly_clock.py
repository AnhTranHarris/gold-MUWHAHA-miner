"""R11S5 full-source hour/day/month calendar-native research process.

Individually checkpoints each UTC date, then 2026-01 / -02 / -06 / -07.
Read-only original 2880 row R11S4 oracle results; no re-fitting/claimed trading.
All source columns retained and exact count identities checked. Calendar UNKNOWN
unless a verified historical MT5 export and broker UTC offset map are supplied.
Do not count absent news as zero or nominal FX sessions as broker permission.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,os,sys,tempfile
from collections import defaultdict
from datetime import datetime,timezone
from pathlib import Path
from market_clock import clock_hour,utc_hour
from mt5_news import load_events,load_server_intervals,hourly_event_features

DEFAULT_HOUR='/mnt/data/R11S4_ALL_2880_COMPLETE_UTC_HOURLY_SOURCE_QUOTA_RESULTS.csv'
DEFAULT_DAY='/mnt/data/R11S4_ALL_120_COMPLETE_UTC_DAILY_SOURCE_QUOTA_RESULTS.csv'
EXPECTED_HOUR='cfabfecd9ea57d05d806eb16922f20789e0ea75a77111785d0de565fc6c64542'
EXPECTED_DAY='300fddb83b563e439b2006957513242c3b732ba60495d176222b001475e6557a'
MONTHS=('2026-01','2026-02','2026-06','2026-07')
SESSION_NAMES=('SYDNEY','TOKYO','LONDON','NEW_YORK')
SCRIPT_VERSION='r11s5_20261103_full2880_hour_clock_v1'

def hash_file(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
    return h.hexdigest()

def save_text_atomic(path,text):
    p=Path(path);p.parent.mkdir(parents=True,exist_ok=True)
    fd,tmp=tempfile.mkstemp(prefix='.r11s5_',dir=str(p.parent))
    try:
        with os.fdopen(fd,'w',encoding='utf-8',newline='') as f:
            f.write(text);f.flush();os.fsync(f.fileno())
        os.replace(tmp,p)
    finally:
        if os.path.exists(tmp):os.unlink(tmp)

def save_csv(path,rows,header):
    import io
    buf=io.StringIO(newline='')
    w=csv.DictWriter(buf,fieldnames=header,extrasaction='raise',lineterminator='\n')
    w.writeheader()
    for r in rows:w.writerow(r)
    save_text_atomic(path,buf.getvalue())

def read_csv(path):
    with open(path,encoding='utf-8-sig',newline='') as f:
        return list(csv.DictReader(f))

def int_field(row,key):return int(row[key])

def _safe_int(v):
    if v is None or str(v).strip()=='':return None
    return int(float(v))

def validate_inputs(hours,days):
    if len(hours)!=2880 or len(days)!=120:
        raise ValueError(f'full source population missing: {len(hours)} hours, {len(days)} days')
    byhour={(r['month'],r['utc_hour']):r for r in hours}
    if len(byhour)!=2880:raise ValueError('duplicate UTC hour or month mismatch')
    daylookup={(r['month'],r['utc_day']):r for r in days}
    if len(daylookup)!=120:raise ValueError('duplicate UTC day')
    for m in MONTHS:
        hs=sorted([r for r in hours if r['month']==m],key=lambda r:r['utc_hour'])
        ds=[r for r in days if r['month']==m]
        expected={'2026-01':744,'2026-02':672,'2026-06':720,'2026-07':744}[m]
        if len(hs)!=expected or len(ds)!=expected//24:
            raise ValueError(f'calendar missing source hour/day {m}')
        for h in hs:
            dt=utc_hour(h['utc_hour'])
            if dt.strftime('%Y-%m')!=m or h['utc_day']!=dt.strftime('%Y-%m-%d') or int(h['hour_utc'])!=dt.hour:
                raise ValueError('misaligned UTC source time')
            r9=int_field(h,'R9_SYNTH_UTC')
            got=int_field(h,'R11S4_HOUR_QUOTA_BEAM_ENTRIES')
            ub=int_field(h,'R11S3_INDEPENDENT_HOUR_CROSSING_UPPER')
            imp=int_field(h,'hour_mathematically_impossible')
            if got>ub or (r9>0 and imp!=(ub<r9)):
                raise ValueError(f'invalid hour arithmetic {m} {h["utc_hour"]}')
        for day in ds:
            block=[h for h in hs if h['utc_day']==day['utc_day']]
            if len(block)!=24 or sum(int(x['R9_SYNTH_UTC']) for x in block)!=int(day['R9_SYNTH_UTC']):
                raise ValueError(f'UTC daily reference mismatch {day["utc_day"]}')
            if sum(int(x['R11S4_HOUR_QUOTA_BEAM_ENTRIES']) for x in block)!=int(day['R11S4_HINDSIGHT_ENTRIES']):
                raise ValueError(f'UTC day source selected mismatch {day["utc_day"]}')
    return daylookup

def summarize_block(block,month):
    refs=sum(int(x['R9_SYNTH_UTC']) for x in block)
    selected=sum(int(x['R11S4_HOUR_QUOTA_BEAM_ENTRIES']) for x in block)
    active=[x for x in block if int(x['R9_SYNTH_UTC'])>0]
    attained=sum(int(x['R11S4_HOUR_QUOTA_BEAM_ENTRIES'])>=int(x['R9_SYNTH_UTC']) for x in active)
    impossible=sum(int(x['hour_mathematically_impossible']) for x in active)
    deficits=sum(max(0,int(x['R9_SYNTH_UTC'])-int(x['R11S3_INDEPENDENT_HOUR_CROSSING_UPPER'])) for x in active)
    if attained+impossible!=len(active):
        raise ValueError('S4 did not attain all individually theoretically feasible hourly quotas')
    state_counts=defaultdict(lambda:{'calendar_hours':0,'r9_active_hours':0,'quota_hours_pass':0,
                                   'hours_proven_impossible':0,'reference_trades':0,'strict_selected_trades':0,
                                   'unavoidable_hour_deficit_lower_sum':0})
    for x in block:
        grp=x['nominal_session_names']
        stat=state_counts[grp];stat['calendar_hours']+=1
        ref=int(x['R9_SYNTH_UTC']);sel=int(x['R11S4_HOUR_QUOTA_BEAM_ENTRIES'])
        stat['reference_trades']+=ref;stat['strict_selected_trades']+=sel
        if ref:
            stat['r9_active_hours']+=1
            stat['quota_hours_pass']+=int(sel>=ref)
            stat['hours_proven_impossible']+=int(x['hour_mathematically_impossible'])
            stat['unavoidable_hour_deficit_lower_sum']+=max(0,ref-int(x['R11S3_INDEPENDENT_HOUR_CROSSING_UPPER']))
    utc_stats=[]
    for hr in range(24):
        band=[x for x in block if int(x['hour_utc'])==hr]
        a=[x for x in band if int(x['R9_SYNTH_UTC'])>0]
        utc_stats.append({'hour_utc':hr,'total_calendar_hours':len(band), 'r9_active_hours':len(a),
            'strict_30sec_future_selected':sum(int(x['R11S4_HOUR_QUOTA_BEAM_ENTRIES']) for x in band),
            'r9_synth_reference':sum(int(x['R9_SYNTH_UTC']) for x in band),
            'r9_quota_hours_pass':sum(int(x['R11S4_HOUR_QUOTA_BEAM_ENTRIES'])>=int(x['R9_SYNTH_UTC']) for x in a),
            'mathematically_impossible_hours':sum(int(x['hour_mathematically_impossible']) for x in a),
            'min_unavoidable_hour_count_deficit':sum(max(0,int(x['R9_SYNTH_UTC'])-int(x['R11S3_INDEPENDENT_HOUR_CROSSING_UPPER'])) for x in a)})
    return {'month':month,'hour_rows':len(block),'ref_synth':refs,'strict_future_15fav30safe_count':selected,
        'r9_active_hours':len(active),'attainable_hourly_quotas_met':attained,
        'mathematically_impossible_hourly_quotas':impossible,
        'min_unavoidable_hourly_count_shortage_sum':deficits,
        'nominal_session_conditional_research_groups':dict(sorted(state_counts.items())),
        'all_24_utc_hour_conditions':utc_stats,
        'scientific_boundary':'FUTURE_PRIVILEGED_HINDSIGHT_LABELS_DO_NOT_CERTIFY_ASOF_ENTRY_OR_REAL_BROKER_OPEN'}

def run(hour_path,day_path,out,months,news_path=None,offsets_path=None,calendar_complete=False):
    hsha=hash_file(hour_path);dsha=hash_file(day_path)
    if hsha!=EXPECTED_HOUR or dsha!=EXPECTED_DAY:
        raise ValueError('R11S4 source SHA mismatch, no optimization on mutated source')
    hours=read_csv(hour_path);days=read_csv(day_path)
    validate_inputs(hours,days)
    if news_path is None:
        if offsets_path is not None or calendar_complete:
            raise ValueError('incomplete news arguments')
        events=None
    else:
        if offsets_path is None or not calendar_complete:
            raise ValueError('MT5 event completeness + server UTC offset evidence required')
        events=load_events(news_path,load_server_intervals(offsets_path))
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    meta={'job':SCRIPT_VERSION,'input_hour_sha256':hsha,'input_day_sha256':dsha,
          'news_export_state':'NO_MT5_EXPORT_UNKNOWN' if events is None else 'RETROSPECTIVE_SOURCE_NOT_ASOF',
          'execution':'READ_ONLY_EXISTING_SOURCE_HINDSIGHT_PLUS_CAUSAL_CLOCK_NO_NEW_FORECAST_FIT',
          'month_results':[]}
    for month in months:
        if month not in MONTHS:raise ValueError(month)
        subset=sorted([x for x in hours if x['month']==month],key=lambda x:x['utc_hour'])
        outrows=[]
        for orig in subset:
            c=clock_hour(orig['utc_hour'])
            news=hourly_event_features(utc_hour(orig['utc_hour']),events,complete=calendar_complete)
            r={**orig,**c,**news}
            r['hourly_strict_quota_attainability']='SOURCE_IMPOSSIBLE' if int(orig['hour_mathematically_impossible']) else ('SOURCE_ATTAINED' if int(orig['R9_SYNTH_UTC']) else 'NO_R9_REFERENCE')
            r['eligibility_for_causal_training']='ASOF_CLOCK_ONLY__OMIT_ALL_R11S4_ORACLE_AND_R9_FUTURE_LABEL_COLUMNS'
            outrows.append(r)
        keys=list(outrows[0].keys())
        mdir=out/month
        chunkmeta=[]
        for day in sorted({x['utc_day'] for x in subset}):
            dayrows=[x for x in outrows if x['utc_day']==day]
            p=mdir/'days'/f'{day}_ALL_24_HOURS.csv'
            save_csv(p,dayrows,keys)
            if len(read_csv(p))!=24:raise RuntimeError('non-atomic day chunk failure')
            chunkmeta.append({'utc_day':day,'hour_rows':24,'sha256':hash_file(p),
                              'synth_source_count':sum(int(x['R9_SYNTH_UTC']) for x in dayrows),
                              'future_selected':sum(int(x['R11S4_HOUR_QUOTA_BEAM_ENTRIES']) for x in dayrows),
                              'impossible_hour_count':sum(int(x['hour_mathematically_impossible']) for x in dayrows)})
        full=mdir/f'{month}_ALL_HOURS_R11S5_CLOCK_AND_NEWS.csv'
        save_csv(full,outrows,keys)
        assert len(read_csv(full))==len(subset)
        report=summarize_block(outrows,month)
        report['source_hour_sha256']=hsha
        report['source_day_sha256']=dsha
        report['full_hour_overlay_sha256']=hash_file(full)
        report['per_day_chunk_files']=chunkmeta
        report['data_annotation_state']=meta['news_export_state']
        rpt=mdir/f'{month}_COMPLETE_CLOCK_REGIME_AND_QUOTA_EXPERIMENT.json'
        save_text_atomic(rpt,json.dumps(report,indent=2,sort_keys=True)+'\n')
        print(json.dumps({'month':month,'hours':report['hour_rows'],'days':len(chunkmeta),
              'selected':report['strict_future_15fav30safe_count'],'impossible_hours':report['mathematically_impossible_hourly_quotas'],
              'hour_sha256':report['full_hour_overlay_sha256'],'report_sha256':hash_file(rpt)},sort_keys=True),flush=True)
        meta['month_results'].append({'month':month,'hours':report['hour_rows'], 'days':len(chunkmeta),
              'report_sha256':hash_file(rpt),'hour_csv_sha256':hash_file(full),
              'actual_broker_session_status':'UNKNOWN','news_status':meta['news_export_state']})
    save_text_atomic(out/'R11S5_COMPLETION_AND_SOURCE_PROVENANCE.json',json.dumps(meta,indent=2,sort_keys=True)+'\n')
    return meta

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--source-hour',default=DEFAULT_HOUR)
    p.add_argument('--source-day',default=DEFAULT_DAY)
    p.add_argument('--out',default='/mnt/data/r11s5_work/outputs')
    p.add_argument('--months',nargs='+',default=list(MONTHS))
    p.add_argument('--mt5-news-tsv')
    p.add_argument('--verified-server-offset-map')
    p.add_argument('--mt5-export-complete',action='store_true')
    a=p.parse_args()
    run(a.source_hour,a.source_day,a.out,a.months,
       a.mt5_news_tsv,a.verified_server_offset_map,a.mt5_export_complete)
