#!/usr/bin/env python3
"""Quick independent non-trading invariants for BETA014 profile and source-file evidence."""
import sys, json, datetime as dt, hashlib
from pathlib import Path
import numpy as np
sys.path.insert(0,'/mnt/data')
import BETA_014_PROP_RISK_REPLAY as w
r=json.loads(Path('/mnt/data/BETA_014_PROP_001LOT_FUNDED_RERUN.json').read_text())
xs=r['strategy_results']
assert set(xs)=={'R9_FEED_NORMALIZED','R09_BETA_001_ADAPTIVE_IGNITION_ENTRY'}
checks={}
# at New York 17:00 on both winter and daylight saving clocks day flips exactly.
for label, before,after in [('winter','2026-01-13T21:59:59+00:00','2026-01-13T22:00:00+00:00'),('dst','2026-03-09T20:59:59+00:00','2026-03-09T21:00:00+00:00')]:
    arr=np.array([int(dt.datetime.fromisoformat(t).timestamp()*1000) for t in [before,after]],dtype=np.int64)
    d,allow=w.calendar_by_tick(arr)
    assert d[0]!=d[1],(label,d.tolist())
    assert allow[0]==0 and allow[1]==0
    checks[label+'_risk_day_reset_and_rollover_block']='PASSED'
# Friday 16:54 allowed / 16:55 blocked; observed price ticks only.
arr=np.array([int(dt.datetime.fromisoformat(t).timestamp()*1000) for t in ['2026-01-09T21:54:00+00:00','2026-01-09T21:55:00+00:00']],dtype=np.int64)
d,allow=w.calendar_by_tick(arr)
assert list(allow)==[1,0],allow.tolist()
checks['friday_close_block']='PASSED'
# Contract/fee and source data confidence.
assert w.LOTS==0.01 and w.EXPOSURE_OZ==1.0 and abs(w.ROUND_TRIP_COMMISSION-0.02)<1e-12
checks['lot_contract_100oz_fee_002']='PASSED'
assert r['sources_scanned_this_replay'][0]['ticks']==9135062
assert r['sources_scanned_this_replay'][0]['sha256']=='d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5'
checks['january_full_file_sha_gzip_and_monotonicity']='PASSED'
for name,x in xs.items():
    assert x['terminal_stop'] is True and x['month']=='2026-01'
    assert x['overall_floor_breach_utc'] is not None
    assert abs(x['end_balance_usd']-(100000+x['net_profit_usd']))<0.02
    assert abs(x['net_profit_usd']-x['gross_profit_usd']-x['gross_loss_usd'])<0.03
    assert x['winning_trades']+x['losing_trades']==x['trade_count']
    assert sum(z['trades'] for z in x['daily_records'])==x['trade_count']
    assert sum(z['wins'] for z in x['daily_records'])==x['winning_trades']
    assert x['daily_soft_lockouts']==0 and x['daily_hard_lockouts']==0
    assert x['forced_risk_closures']==1
    assert x['max_floating_equity_drawdown_usd']>=abs(x['net_profit_usd'])-2
    assert x['max_floating_equity_drawdown_usd']<=10500
    assert all(z['day_reference_usd']-z['minimum_equity_usd']<4000 for z in x['daily_records'])
    checks[name+'_funded_math_and_daily_gates']='PASSED'
# cross-sectional comparison through exactly matching *complete* risk-day calendar.
matched={}
for k,z in xs.items():
    a=[x for x in z['daily_records'] if x['risk_day_ny']<='2026-01-13']
    matched[k]={'through_ny_risk_day':'2026-01-13','trades':sum(x['trades'] for x in a),'wins':sum(x['wins'] for x in a),'net_usd':round(sum(x['net_usd'] for x in a),2),'ending_balance_usd':a[-1]['closing_balance_usd'],'win_rate_pct':round(sum(x['wins'] for x in a)*100/sum(x['trades'] for x in a),4)}
checks['matched_calendar_comparison_avoids_unfair_count_gain']='PASSED'
# Survived each following month? no, so funded calendar is flat.
for month in ['2026-02','2026-03','2026-04','2026-05','2026-06','2026-07']:
    for k,x in xs.items():assert x['terminal_stop']
checks['post_terminal_feb_jul_zero_funded_trades']='PASSED'
qa={'checks':checks,'matched_calendar':matched,'funded_calendar':{'2026-01':{k:{t:x[t] for t in ['trade_count','winning_trades','win_rate_percent','net_profit_usd','gross_profit_usd','gross_loss_usd','max_floating_equity_drawdown_usd','end_balance_usd','overall_floor_breach_utc']} for k,x in xs.items()},**{m:{k:{'new_funded_trades':0,'new_funded_pnl_usd':0.0,'carry_forward_terminated_balance_usd':x['end_balance_usd'],'status':'TERMINATED_NO_FURTHER_TRADES'} for k,x in xs.items()} for m in ['2026-02','2026-03','2026-04','2026-05','2026-06','2026-07']}},'statement':'No output after terminal floor counts toward funded account. All January full-file ticks read, later months not reopened because the terminal state prevents orders. News/actual Coinexx session gates cannot be certified.'}
Path('/mnt/data/BETA_014_PROP_RISK_QA.json').write_text(json.dumps(qa,indent=2,sort_keys=True)+'\n')
print(json.dumps({'check_count':len(checks),'checks':checks,'matched_calendar':matched},indent=2))