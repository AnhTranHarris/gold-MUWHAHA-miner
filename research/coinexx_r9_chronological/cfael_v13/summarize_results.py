import json,sys,math
from pathlib import Path
P=Path('/mnt/data/cfael_v13')
refs=[json.loads((P/f'{i:02d}_small_confirm.json').read_text()) for i in range(1,10)]
models=list(refs[0]['models'])
summ={}
for key in models:
 vals=[x['models'][key] for x in refs]
 n=sum(v['counts']['completed'] for v in vals)
 w=sum(v['counts']['wins'] for v in vals)
 net=round(sum(v['net'] for v in vals),2)
 summ[key]=dict(n=n,winners=w,win_fraction=round(w/n,6),net=net,mean=round(net/n,6),
             positive_months=sum(v['net']>0 for v in vals),
             months={d['month']:{'trades':v['counts']['completed'],'net':v['net'],'mean':v['mean_net'],'win':v['win_fraction']} for d,v in zip(refs,vals)},
             config=vals[0]['config'])
mapresult=json.loads((P/'V13_PROFIT_MAP_CHRONOLOGICAL_RESULT.json').read_text())
geom=json.loads((P/'V13_NINE_MONTH_PROFITABLE_TRADE_GEOMETRY.json').read_text())
report=dict(scope='Profit-first experimental V13, full source exact quote observation, original on-policy V9 signal cohort only, not full independent strategy signal simulation',
            data_months='2026-01 through 2026-09',original_pinned_quotes=sum(x['quotes'] for x in refs),
            baseline_winners=geom['winning_entries'],baseline_completed=geom['completed'],baseline_mean=geom['baseline']['net_per_trade'],
            primary_lattice_results=summ,
            profitable_trade_map=geom,
            chronological_statistical_map=mapresult,
            spread_and_additional_cash_cost_mode='BUY at observed Ask, SELL at observed Bid, exit using liquidation side, extra fixed $0.20 roundtrip cash (k=1)',
            no_broker_fill_or_slippage_model=True,
            no_new_market_data_created=True,
            qualification='Alternative fills and exits applied only to historical V9 on-policy signal cohort; a changed entry/exit policy changes future signals and rearming. NO production performance claims.',
            parameter_selection='No candidate passed positive net expectancy across the nine months; none authorized for MT5 trading')
(P/'V13_FULL_NINE_MONTH_PROFIT_FIRST_REPORT.json').write_text(json.dumps(report,indent=2))
for k,v in summ.items():print(k,v['n'],v['winners'],v['win_fraction'],v['net'],v['mean'],v['positive_months'])
print('SOURCE QUOTES',report['original_pinned_quotes'],'BASELINE',report['baseline_completed'],report['baseline_winners'])
