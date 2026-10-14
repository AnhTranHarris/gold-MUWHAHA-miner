"""GRID0292 read-only independent ledger checks; no source rerun/research promotion."""
import json,hashlib,math
from pathlib import Path
ROOT=Path(__file__).resolve().parent
A=json.loads((ROOT/'grid0283_raw_funded_watchdog_combined_results.json').read_text())['results'][0]
B=json.loads((ROOT/'grid0291_combined_heat_paid_loss_full_tick_results.json').read_text())['results']
B=next(x for x in B if x['name']=='CAP2_PAUSE2_5MIN')
checks=[]
def check(cond,message):
 assert cond,message
 checks.append(message)
for x in (A,B):
 check(abs(x['net']-(x['gross_profit']+x['gross_loss']))<1e-6,'cash equals gross win plus gross loss for '+x['name'])
 check(abs(x['net']-sum(y['net'] for y in x['daily'].values()))<1e-6,'21 settled daily net sum equals month '+x['name'])
 check(abs(x['net']-sum(y['net'] for y in x['weekly'].values()))<1e-6,'5 settled ISO-week sums equal month '+x['name'])
 check(x['trades']==sum(y['trades'] for y in x['daily'].values()),'21 daily completed-trade counts equal month '+x['name'])
 check(x['trades']==sum(y['trades'] for y in x['weekly'].values()),'5 weekly completed-trade counts equal month '+x['name'])
 check(x['r9_synth_days_net_met']==sum(y['net']>=y['r9_synth_net'] for y in x['daily'].values()),'source-matched R9 daily net QC '+x['name'])
 check(x['r9_synth_weeks_net_met']==sum(y['net']>=y['r9_synth_net'] for y in x['weekly'].values()),'source-matched R9 week net QC '+x['name'])
 check(x['ending_open']==0,'no open end-month portfolio '+x['name'])
check(len(B['daily'])==21 and all(y['net']>0 for y in B['daily'].values()),'new variant: 21/21 positive book net')
check(len(B['weekly'])==5 and all(y['net']>0 for y in B['weekly'].values()),'new variant: 5/5 positive booked net')
check(B['net']>=B['r9_synth_month_target'],'new variant net beats reference monthly net')
check(B['r9_synth_days_net_met']<21,'NOT a complete 100% R9 daily target')
check(B['r9_synth_weeks_net_met']<5,'NOT a complete 100% R9 weekly target')
check(B['trades']<B['r9_synth_month_trades'],'NOT 100% R9 trade volume')
check(B['gross_loss']<-1827.87,'Gross loss worse than R9 synth 1827.87')
check(B['max_all_tick_floating_equity_dd']>1000,'Floating equity DD materially greater than $1000')
check(B['verified_parent']>0 and B['verified_child']>0,'physically modeled paid-parent source and child still present')
check(B['request_denials'].get('asof_source_simultaneous_cap',0)>0,'L7 source cap operated')
check(B['online_source_pause_activations']>0,'Previously realized closed loss pause operated')
file=ROOT/'grid0292_january_qc_results.json'
file.write_text(json.dumps({'status':'RESEARCH_ONLY_INDEPENDENT_ACCOUNTING_QC_NOT_QC_CERTIFIED',
  'checks':checks,'count':len(checks),'baseline_net':A['net'],'new_net':B['net'],
  'baseline_positive_days':sum(v['net']>0 for v in A['daily'].values()),
  'new_positive_days':sum(v['net']>0 for v in B['daily'].values()),
  'new_positive_weeks':sum(v['net']>0 for v in B['weekly'].values()),
  'new_r9_day_targets':B['r9_synth_days_net_met'],'new_r9_week_targets':B['r9_synth_weeks_net_met'],
  'reason_not_promoted':'in-sample; incomplete month/day/week targets, trade velocity, cost risk, small-cap survival, teacher scores, Feb-Jul, exact end-to-end source regeneration, owner QC',
 },indent=2))
print('QC PASSED:',len(checks),'checks; new positive days',sum(v['net']>0 for v in B['daily'].values()),'weeks',sum(v['net']>0 for v in B['weekly'].values()))
