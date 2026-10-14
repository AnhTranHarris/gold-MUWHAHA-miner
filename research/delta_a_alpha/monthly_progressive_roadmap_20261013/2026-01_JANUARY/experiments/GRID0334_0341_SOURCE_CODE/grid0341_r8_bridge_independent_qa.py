"""Independent read-only integrity and acceptance boundary checks; no strategy calls."""
import json,zipfile,hashlib
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parent
jan=Path('/mnt/data/XAUUSD_DUKAS_2026_01_ticks.csv(3).gz')
source=Path('/mnt/data/R8_JAN_DUKAS_RESEARCH/r8_causal_tick_port.py')
assert hashlib.file_digest(jan.open('rb'),'sha256').hexdigest()=='d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5'
checks=1
j=json.loads((ROOT/'grid0335_r8_efficiency_source_confluence_results.json').read_text())
s=json.loads((ROOT/'grid0339_r8_strict_single_position_results.json').read_text())
c=json.loads((ROOT/'grid0337_r8_source_session_clock_stress_results.json').read_text())
assert len(j['date_cohort'])==10 and len(set(j['date_cohort']))==10;checks+=2
for name,summary in j['summary'].items():
 rows=[q for q in j['episodes'] if q['policy']==name]
 assert len(rows)==10;checks+=1
 assert sum(q['trades_closed'] for q in rows)==summary['trades'];checks+=1
 assert abs(min(q['final_cash'] for q in rows)-summary['final_min'])<1e-6;checks+=1
 assert abs(max(q['final_cash'] for q in rows)-summary['final_max'])<1e-6;checks+=1
 assert abs(max(q['worst_hour_drawdown'] for q in rows)-summary['worst_hour_dd'])<1e-6;checks+=1
 assert summary['10_starts']==10 and summary['10000_7day']==0;checks+=2
with zipfile.ZipFile('/mnt/data/GRID0320_0329_JANUARY_SOURCE_EXACT_ROUTING_AND_100USD_SURVIVAL_QC_UNPROMOTED.zip') as z:
 ref=json.loads(z.read('RESEARCH/grid0325_ten_start_source_conditioned_results.json'))['summary']['ALL_ORDINARY']
base=j['summary']['CONTROL']
assert base['trades']==ref['trade_total'] and abs(base['worst_hour_dd']-ref['worst_hour'])<1e-8 and base['no_stopout']==ref['no_stopout'];checks+=3
assert s['summary']['starts']==10 and s['summary']['max_positions']==1 and s['summary']['trade_count_total']==242;checks+=3
assert [p['date'] for p in s['episodes']]==j['date_cohort'];checks+=1
assert s['summary']['nonruin']==10 and s['summary']['no_stopout']==10 and s['summary']['positive']==10 and s['summary']['hit10000_7days']==0;checks+=4
assert len(c['variants'])==6;checks+=1
for spread in [.25,.50,.75]:
 q=[x for x in c['variants'] if x['spread_ceiling_usd']==spread]
 assert len(q)==2 and abs(q[0]['final_cash']-q[1]['final_cash'])<1e-6;checks+=2
pre=Path('/mnt/data/r8_followup_20261014/grid0338_runlog.txt').read_text();lines=[l for l in pre.splitlines() if l.startswith('QC ')]
assert len(lines)==8;checks+=1
assert lines[-1].endswith('checks 1624');checks+=1
# Fail-closed statuses: these cannot be labeled accepted or $100x100 achieved.
accepted=False
if any(x['10000_7day']!=0 for x in j['summary'].values()):accepted=True
assert not accepted;checks+=1
out={'status':'PASS_RESEARCH_ACCOUNTING_BOUNDARY_ONLY','checks_passed':checks,'orig_tick_gzip_sha256':'d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5','sample_size':10,'independent_full_deal_hourly_checks_finished_starts':8,'independent_full_deal_hourly_checks_missing_starts':2,'r8_singleton_10_runs':s['summary'],'control_10_runs':base,'clock_stress_complete':True,'retained_research_only':True,'important_limitations':['Historical selected original source candidate dates/exit schedules','Hypothetical broker margin contract/slippage','Ten selected windows overlap, so no 100 percent survival guarantee','GRID0336 and GRID0340 future-capacity attempts stopped by reproducibility stall, NOT accepted','GRID0338 rebooked and independently hourly marked only first eight of ten starts due reproducibility stall','No active engine update, no owner QC acceptance, J0183 unchanged']}
(ROOT/'grid0341_integrity_acceptance_qc.json').write_text(json.dumps(out,indent=2))
print('PASS',checks,'integrity boundary checks; 8/10 independent intratick ledger reconstructions, 10/10 research model source runs',flush=True)
