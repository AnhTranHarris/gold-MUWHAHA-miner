"""Source-exact calendar coverage: no missing active days hidden by groupby.

Ranks no models, uses only complete R11 eligible source timestamps and full
position traces. All future-selected oracle schedules remain future privileged.
"""
from __future__ import annotations
import argparse,hashlib,json,pathlib
import numpy as np
from entry_contract import MONTHS,PINNED,candidate_v5,verify_file_sha
from fullmonth_oracle_optimization import EXPERIMENTS
from h1v2_teacher import read_ticks
from preserve_month import ROOT,EXPECTED_ORIGINAL,sha

def _iso(day_number):
    from datetime import datetime,timezone
    d=datetime.fromtimestamp(int(day_number)*86400,timezone.utc)
    year,week,_=d.isocalendar()
    return f'{year}-W{week:02d}'

def coverage(mon):
    raw=pathlib.Path('/mnt/data')/f'XAUUSD_DUKAS_2026_{mon}_ticks.csv.gz'
    label=ROOT/'rebuilt_teacher'/f'h1v2_dukascopy_{mon}_oracle_labels.npz'
    verify_file_sha(raw,PINNED[mon]);verify_file_sha(label,EXPECTED_ORIGINAL[mon])
    t,b,a=read_ticks(raw);v5=candidate_v5(t,b,a)
    days,day_eligible=np.unique(t[v5]//86400000,return_counts=True)
    srcdays={int(d):int(c) for d,c in zip(days,day_eligible)}
    weekcounts={}
    for d,c in srcdays.items():weekcounts[_iso(d)]=weekcounts.get(_iso(d),0)+c
    report={'month':mon,'source_raw_sha256':PINNED[mon],
      'source_original_label_sha256':EXPECTED_ORIGINAL[mon],
      'source_eligible_days_UTC':[{'utc_day':str(np.datetime64(int(d)*86400000000,'ms'))[:10],
                                   'raw_day_integer':d,'source_v5_candidate_count':n} for d,n in srcdays.items()],
      'source_v5_candidate_active_day_count':len(srcdays),
      'source_v5_candidate_active_week_count':len(weekcounts),
      'source_v5_candidate_week_counts':weekcounts,
      'coverage_by_variant':{}}
    for spec in EXPERIMENTS:
        selected=ROOT/'optimization'/f'month_{mon}'/f'{spec.id}_SELECTED_FULL_SOURCE_TRACE.npz'
        with np.load(selected,allow_pickle=False) as z:
            stamp=z['entry_utc_ms']
            first=z['first_favorable_elapsed_ms'];pnl=z['research_net_after_incremental_cost']
        d,counts=np.unique(stamp//86400000,return_counts=True)
        got={int(k):int(v) for k,v in zip(d,counts)}
        weeks={}
        for x,c in got.items():weeks[_iso(x)]=weeks.get(_iso(x),0)+c
        missing=sorted(set(srcdays)-set(got))
        report['coverage_by_variant'][spec.id]={
          'source_active_days':len(srcdays),
          'traded_days':len(got),
          'candidate_active_days_with_zero_selected_positions':[str(np.datetime64(int(k)*86400000000,'ms'))[:10] for k in missing],
          'candidate_active_weeks_with_zero_selected_positions':sorted(set(weekcounts)-set(weeks)),
          'all_source_active_day_coverage':len(missing)==0,
          'every_source_active_week_covered':set(weekcounts)==set(weeks),
          'total_nonoverlapping_selected_positions':int(len(stamp)),
          'every_source_active_day_first15_80pct': all((int((first[stamp//86400000==day]<=15000).sum())/count)>=.80 for day,count in got.items()) and not missing,
          'all_24_UTC_hour_selected_counts':{str(h):int(((stamp//3600000)%24==h).sum()) for h in range(24)},
          'full_source_active_daily_counts':[{'utc_day':str(np.datetime64(int(day)*86400000000,'ms'))[:10],
                                              'eligible_source_candidates':srcdays[day],
                                              'selected_positions':got.get(day,0),
                                              'no_trade_failure':day not in got} for day in srcdays],
          'full_source_active_weekly_counts':[{'iso_week':k,'eligible_source_candidates':n,
                                               'selected_positions':weeks.get(k,0),
                                               'no_trade_failure':k not in weeks} for k,n in sorted(weekcounts.items())]
        }
    path=ROOT/'optimization'/f'month_{mon}'/f'R11_{mon}_COMPLETE_SOURCE_ACTIVE_CALENDAR_NO_ZERO_DAY_OMISSIONS.json'
    path.write_text(json.dumps(report,indent=2))
    return {'month':mon,'source_active_days':len(srcdays),'source_active_weeks':len(weekcounts),
            'all_experiments':{k:{'selected':v['total_nonoverlapping_selected_positions'],
                'no_trade_source_days':len(v['candidate_active_days_with_zero_selected_positions']),
                'first15_all_active_days_80':v['every_source_active_day_first15_80pct']} for k,v in report['coverage_by_variant'].items()},
            'complete_calendar_receipt':str(path),'complete_calendar_receipt_sha256':sha(path)}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--month',required=True,choices=MONTHS);z=p.parse_args()
    print(json.dumps(coverage(z.month),indent=2),flush=True)
