"""Timeout-safe atomic Jan032 sweep reconciliation; changes NO trading strategies."""
from pathlib import Path
import json, hashlib, os
P=Path(__file__).resolve().parent
O=P/'output'
results=[]
for q in (1250,1500,1800,2200,2800):
 f=O/f'JAN032_RAW_Q{q}_DAILY_WEEKLY.json'
 if not f.is_file(): raise SystemExit(f'UNFINISHED {q}: refuse to mark complete')
 d=json.loads(f.read_text())
 if d.get('q_raw')!=q or d.get('trades',0)<=0 or len(d.get('daily',{}))<20:
  raise SystemExit(f'INVALID {q}')
 if abs(d['net']-sum(x['net'] for x in d['daily'].values()))>.03:raise SystemExit('daily mismatch')
 results.append({k:d[k] for k in ('name','net','trades','gross_loss','gross_profit','pf','win','balance_dd','equity_dd','positive_days','beat_days','positive_weeks','beat_weeks','wd_net','wd_trades','q_raw')})
original=json.loads((O/'JAN032_ORIGINAL_RAW_L35_C640.json').read_text())
recovery={'unit':'JAN032_INTERRUPTED_SWEEP_RECOVERED','state':'COMPLETED_IN_SEPARATE_ATOMIC_CASES','original_source_rules_unmodified':True,'baseline':{k:original[k] for k in ('net','trades','gross_loss','pf','equity_dd')},'research_settings':results,'files':'JAN032_RAW_Q{1250,1500,1800,2200,2800}_DAILY_WEEKLY.json','limitations':'In-sample January 131E normalized-execution source family repriced with actual recorded Dukascopy Bid/Ask; source has unresolved funded-child cap genealogy and no later native/recovery/real margin. Not production V1 or blind proof.'}
tmp=O/'JAN032_TIMEOUT_RECOVERED_Q_SWEEP.json.tmp'
tmp.write_text(json.dumps(recovery,indent=2));os.replace(tmp,O/'JAN032_TIMEOUT_RECOVERED_Q_SWEEP.json')
report=O/'DAA_JANUARY_032_FULL_SOURCE_REPLAY_AND_R9_COMPARISON.md'
s=report.read_text()
append='''\n## 11. Delivery-timeout recovery / atomic checkpoint reconciliation\n\nA user-interface message delivery timeout interrupted the original monolithic six-setting renewal quantum sweep after the `q_2200` log line. **It did not interrupt the original P75 reproduction, the raw Bid/Ask replay, the quote-side ledgers, or the January comparison.** The remaining independent cases were re-executed using the unchanged original 131E source on actual Bid/Ask. Original P75 and raw baseline were retained without rerunning them.\n\n| Entry quantum raw units | Jan net | Tickets | Gross loss | PF | Floating DD |\n|---|---:|---:|---:|---:|---:|\n'''
for r in results:
 append+=f"| {r['q_raw']} | ${r['net']:,.2f} | {r['trades']:,} | -${abs(r['gross_loss']):,.2f} | {r['pf']:.3f} | ${r['equity_dd']:,.2f} |\n"
append+='''\nThese are **January-in-sample fixed renewal sensitivity** experiments only. No setting is promoted, because none resolves the original Watchdog physical-funding-credit defect or provides a complete independently executed L0–L7 portfolio. Every case is checkpointed in its own JSON, so a future timeout can resume from the first missing case instead of repeating 9.1 million ticks unnecessarily.\n'''
if '## 11. Delivery-timeout recovery' not in s:
 report.write_text(s+'\n'+append)
hand=O/'DAA_JAN_032_HANDOFF_READ_FIRST.md'
h=hand.read_text()
if 'Timeout recovery:' not in h:
 hand.write_text(h+'\n**Timeout recovery:** original P75 and raw Bid/Ask complete and validated; five independent quantum cases [1250,1500,1800,2200,2800] complete in `JAN032_TIMEOUT_RECOVERED_Q_SWEEP.json`. Do not rerun the abandoned monolith.\n')
print('RECOVERED_SETTINGS',len(results),'FIVE_PASS','REPORT',report.stat().st_size,'LATEST_RESULT',results[-1]['net'])