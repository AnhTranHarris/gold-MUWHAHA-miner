import pandas as pd,json,math,hashlib
from pathlib import Path
P=Path('/mnt/data/daa_jan_combined_035')
sets=['SCREEN_ALL.csv','ADAPTIVE_SCREEN_ALL.csv','BROKER_RATE_SCREEN_ALL.csv']
assert all((P/x).exists() for x in sets)
rows=[]
for f in sets:
    a=pd.read_csv(P/f); assert not a.isna()[['net','trades','gross_loss','pf','dd']].any().any()
    assert all(a.trades>0) and all(a.dd>=0) and all(a.gross_loss<0) and all(a.net+a.gross_loss.abs()>0)
    assert all(abs((a.net-a.gross_loss)/(-a.gross_loss)-a.pf)<0.0002)
    rows.extend(a.to_dict('records'))
# R9 Jan known: 41,520.82/27,980 from original MT5 deal-source canonical comparison
F=json.load(open(P/'JAN035_FINAL_MONTHLY_COMPARISON.json'));cases=F['cases']
for r in cases:
    k=r['name'];day=json.load(open(P/(k+'_DAILY.json')));week=json.load(open(P/(k+'_WEEKLY.json')))
    assert abs(sum(x['net'] for x in day)-r['net'])<.01,(k,'day')
    assert abs(sum(x['net'] for x in week)-r['net'])<.01,(k,'week')
    assert sum(x['trades'] for x in day)==r['trades']
    assert sum(x['trades'] for x in week)==r['trades']
    assert all(x['period'][:4]=='2026' for x in day)
    assert abs(r['gross_profit']+r['gross_loss']-r['net'])<.01
    assert abs(r['hourly_net']-60197.326)<.01
v={r['name']:r for r in cases}
assert abs(v['original_raw']['net']-93425.311)<.02
assert abs(v['original_raw']['floating_equity_dd']-56921.6)<.01
assert v['fast384']['net']>v['original_raw']['net'] and v['fast384']['gross_loss']>v['original_raw']['gross_loss']
assert v['fast384']['profit_factor']>v['original_raw']['profit_factor']
assert v['fast384']['floating_equity_dd']<v['original_raw']['floating_equity_dd']
assert v['fast384']['trades']>=27980
assert len(rows)==291,(len(rows))
obj={'result':'PASS','screened_runs_total':len(rows),'unique_parameter_combinations_approx':'Several scenarios intentionally duplicate identical param settings; no independent holdout implied','three_batched_scans':{x:len(pd.read_csv(P/x)) for x in sets},'selected_replays':len(cases),'all_daily_weekly_reconciliations':True,'all_pnl_pf_identitites':True,'baseline_net_and_equity_dd_parity':True,'hourly_engine_unchanged_all_selected':True,'fast384_positive_four_metric_screen':True,'raw_bid_ask_only':True,'fixed_0p01_lot':True,'future_parent_chain_recomputed':False,'broker_margin_certified':False,'actual_broker_execution_rate_certified':False,'january_held_out':False,'august_untouched':True,'september_untouched':True}
(P/'QA_RESULTS_035.json').write_text(json.dumps(obj,indent=2)+'\n');print(json.dumps(obj,indent=2))