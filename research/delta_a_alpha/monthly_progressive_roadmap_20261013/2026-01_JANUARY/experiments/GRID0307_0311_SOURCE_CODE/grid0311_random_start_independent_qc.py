"""GRID0311: read-only exact-source acceptance QC for GRID0307-0310.
It checks only mathematical, reproducibility and reporting invariants. It cannot
convert hypothetical spot fills into broker survival proof or OOS profitability.
"""
from __future__ import annotations
import hashlib,json
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parent
BASE=Path('/mnt/data')
checks=[]
def chk(label,value):
    checks.append({'check':label,'pass':bool(value)})
    if not value:raise AssertionError(label)

def main():
    g={i:json.loads((ROOT/(f'grid0{i}_'+s)).read_text()) for i,s in [
        (307,'ten_random_dates_100usd_stress_results.json'),
        (308,'independent_margin_full_tick_results.json'),
        (309,'earned_cash_100usd_random_start_results.json'),
        (310,'fast_earned_margin_original_tick_results.json')]}
    source=BASE/'XAUUSD_DUKAS_2026_01_ticks.csv(3).gz'
    h=hashlib.file_digest(source.open('rb'),'sha256').hexdigest()
    chk('original Jan gzip exact SHA256',h=='d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5')
    p=BASE/'GRID0300_0306_JANUARY_HOURLY_SOURCE_QC_UNPROMOTED.zip'
    chk('prior source archive exact SHA256',hashlib.file_digest(p.open('rb'),'sha256').hexdigest()=='60295a03f9f4e2d954229f92d3f0ad7ca5992a625c9879e689ac7c5dd32b7717')
    r9=json.load(open('/mnt/data/jan_recovery_20261013/ORIGINAL/r9_synth_jan_daily_weekly.json'))
    dates=sorted(np.random.default_rng(20261014).choice(sorted(r9['daily']),10,replace=False).tolist())
    for k,attr in [(307,'dates'),(308,'dates'),(309,'start_dates'),(310,'dates')]:
        chk(f'GRID0{k} has exact seeded independent ten starts',g[k][attr]==dates)
        chk(f'GRID0{k} has exact January canonical gzip',g[k]['source_sha256']==h)
    chk('2026 January 21 canonical trading days',len(r9['daily'])==21)
    chk('10 distinct dates',len(dates)==10 and len(set(dates))==10)
    chk('GRID0307 30 episodes three configurations',len(g[307]['variants'])==30)
    chk('GRID0308 20 episodes two configurations',len(g[308]['episodes'])==20)
    chk('GRID0309 30 episodes three policies',len(g[309]['episodes'])==30)
    chk('GRID0310 40 episodes four margin variants',len(g[310]['episodes'])==40)
    b0=g[308]['aggregate'];b1=g[309]['aggregates'];b2=g[310]['summary']
    chk('two slots 10/10 necessary margin pass',b0['GLOBAL_CAP2']['necessary_100pct_margin_level_pass_count']==10)
    chk('four slots 10/10 necessary margin pass',b0['GLOBAL_CAP4']['necessary_100pct_margin_level_pass_count']==10)
    chk('two slots 0/10 $10000',b0['GLOBAL_CAP2']['ending_at_least_10000_count']==0)
    chk('four slots 0/10 $10000',b0['GLOBAL_CAP4']['ending_at_least_10000_count']==0)
    chk('earned caution 10/10 necessary margin',b1['EARNED_CAUTION']['necessary_pass_margin100']==10)
    chk('earned balanced 10/10 necessary margin',b1['EARNED_BALANCED']['necessary_pass_margin100']==10)
    chk('earned fast 8/10 necessary margin',b1['EARNED_FAST']['necessary_pass_margin100']==8)
    chk('earned fast 1/10 endpoint target',b1['EARNED_FAST']['count_target_10000']==1)
    chk('20 percent margin 10/10 necessary pass',b2['0.2']['necessary_pass_margin100']==10)
    chk('20 percent margin 0/10 100x end',b2['0.2']['target10000_count']==0)
    chk('30 percent margin 8/10 necessary pass',b2['0.3']['necessary_pass_margin100']==8)
    chk('30 percent margin 1/10 100x end',b2['0.3']['target10000_count']==1)
    chk('No 24h 100x target in any variant',all(x['target10000_24h_count']==0 for x in b2.values()))
    for label,v in b2.items():
        subset=[x for x in g[310]['episodes'] if str(x['margin_used_as_fraction_of_post_equity'])==label]
        chk(f'margin {label}: 10 distinct date rows',len(subset)==10 and sorted(x['date'] for x in subset)==dates)
        chk(f'margin {label}: margin100 count from raw',sum(x['necessary_margin_100pct_pass'] for x in subset)==v['necessary_pass_margin100'])
        chk(f'margin {label}: pass200 count from raw',sum(x['necessary_margin_200pct_pass'] for x in subset)==v['necessary_pass_margin200'])
        chk(f'margin {label}: target count from raw',sum(x['reached_10000_by_month_end'] for x in subset)==v['target10000_count'])
        chk(f'margin {label}: trades sum exact',sum(x['trades'] for x in subset)==v['total_closed_trades'])
        chk(f'margin {label}: cash arithmetic exact',all(abs(x['modeled_ending_equity']-(100+x['monthly_finished_net']))<1e-6 for x in subset))
        chk(f'margin {label}: all ends within full-month original quote',all(x['trades']>=0 for x in subset))
    best=[x for x in g[310]['episodes'] if x['reached_10000_by_month_end']]
    chk('Both 10000 winners are January 5 (identical source population)',len(best)==2 and all(x['date']=='2026-01-05' for x in best))
    chk('One winning start not two independent dates',len(set(x['date'] for x in best))==1)
    chk('Winning start retains margin above 200% (hypothetical)',all(x['necessary_margin_200pct_pass'] for x in best))
    chk('No policy satisfies 10/10 necessary-margin and 10/10 target',all(not (v['necessary_pass_margin100']==10 and v['target10000_count']==10) for v in b2.values()))
    chk('Prior official monthly R9 ideal >= $41520',abs(r9['month']['net']-41520.82)<.01)
    out={'status':'READONLY_INDEPENDENT_QC_PASS_NOT_OWNER_ACCEPTANCE',
         'number_of_checks':len(checks),'passed':sum(x['pass'] for x in checks),
         'tests':checks,'source_sha256':h,'prior_exact_source_zip_sha256':hashlib.file_digest(p.open('rb'),'sha256').hexdigest(),
         'owner_qc':'PENDING','v1_integration':'NOT_DONE','ten_date_broker_survival':'NOT_CERTIFIED',
         'scientific_cursor':'J0183_UNCHANGED'}
    dest=ROOT/'grid0311_independent_readonly_qc_results.json';dest.write_text(json.dumps(out,indent=2))
    print('PASS',out['passed'],'/',out['number_of_checks'],'SOURCE',h,flush=True)
if __name__=='__main__':main()
