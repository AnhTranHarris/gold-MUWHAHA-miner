"""Aggregate only derived V16/previous V12 receipts. No original quotes read."""
from pathlib import Path
import collections,hashlib,json
ROOT=Path(__file__).resolve().parent
MONTHS=tuple(f'{m:02d}' for m in range(1,10))
harvest=[json.loads((ROOT/f'V16_HARVEST_{m}.json').read_text()) for m in MONTHS]
exit_only=[json.loads((ROOT/f'V16_{m}_PROSPECTIVE_EXIT.json').read_text()) for m in MONTHS]
sweep_dev=[json.loads((ROOT/f'V16_{m}_INDEPENDENT_1S.json').read_text()) for m in ('01','05','09')]
fade_dev=[json.loads((ROOT/f'V16_{m}_FADE_1S.json').read_text()) for m in ('01','05','09')]
assert all(x['source_sha256']==y['source_sha256'] for x,y in zip(harvest,exit_only))
assert sum(x['closed_trades'] for x in harvest)==338064
assert round(sum(x['baseline_net'] for x in harvest),2)==-135317.63
assert all(x['policies']['BASE']['net']==y['baseline_net'] for x,y in zip(exit_only,harvest))
models={}
for name in harvest[0]['policy']:
 a=[]
 for x in harvest:
  r=x['policy'][name]['rearmed_existing_signals'];fixed=x['policy'][name]['fixed_all']
  a.append({'month':x['month'],'trades':r['trades'],'wins':r['winners'],
    'retained_pct':round(100*r['trade_retention'],3),'net':r['net'],
    'incremental_net':r['delta_vs_all_original'],
    'fixed_entry_uplift':fixed['delta'],'fixed_entry_win_pct':round(100*fixed['win_rate'],3),
    'max_closed_trade_dd':r['max_closed_trade_dd'],'exit_changes':fixed['changed']})
 models[name]={'months':a,'trades':sum(q['trades'] for q in a),
 'win_rate_pct':round(100*sum(q['wins'] for q in a)/sum(q['trades'] for q in a),3),
 'retention_pct':round(100*sum(q['trades'] for q in a)/338064,3),
 'net':round(sum(q['net'] for q in a),2),'incremental_net':round(sum(q['incremental_net'] for q in a),2),
 'positive_increment_months':sum(q['incremental_net']>0 for q in a),
 'fixed_entry_uplift':round(sum(q['fixed_entry_uplift'] for q in a),2)}
moderate=[]
for variant in exit_only[0]['policies']:
 if variant=='BASE':continue
 v=[x['policies'][variant] for x in exit_only]
 moderate.append({'variant':variant,'net':round(sum(x['net'] for x in v),2),
   'delta':round(sum(x['net'] for x in v)+135317.63,2),'positive_months':sum(x['net']>y['baseline_net'] for x,y in zip(v,harvest)),
   'trades':sum(x['trades'] for x in v),'modified_exits':sum(x['exit_interventions'] for x in v)})
report={'version':'V16_PROFIT_FIRST','scope':'Jan-Sep 2026 original Coinexx source-exact, reused in-sample only',
 'baseline':{'entries':338065,'closed_trades':338064,'total_net':-135317.63,'winning_completed':128203,
             'win_rate_pct':round(100*128203/338064,3)},
 'tested_harvest_extensions':models,'tested_early_exit_policies':moderate,
 'one_second_independent_prototype_diagnostic':{
 'months':['01','05','09'],
 'research_only':True,
 'trades_by_month':[{ 'month':x['month'],'family':k,'trades':z['trades'],'positive':z['positive'],
 'net':z['net_cash']} for x in sweep_dev+fade_dev for k,z in x['models'].items()],
 'not_admitted_to_trading':True,
 },
 'out_of_sample_certified':False,'fully_rearmed_vs_changed_v9_signals':False,
 'native_mt5_parity_certified':False,'real_broker_fills':False,
 'high_trade_volume':{'baseline_closed_trades':338064,'full_capacity_replay_required':True},
 'raw_tick_files_copied':False,'source_pins_verified':True,
 'reproducibility_files':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(ROOT.glob('*.py'))}
}
(ROOT/'V16_FULL_NINE_MONTH_AGGREGATE.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
print(json.dumps({'baseline':report['baseline'],'extensions':{k:{key:z[key] for key in ('trades','win_rate_pct','retention_pct','net','incremental_net','positive_increment_months')} for k,z in models.items()},'early_exit':moderate},indent=2))
