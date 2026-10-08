#!/usr/bin/env python3
"""Forensic arithmetic and static causal-counterexample. Jan 131E historical, Jan 024 raw.
Does NOT represent a certified re-execution of original 131E.
"""
import json, hashlib
from pathlib import Path
import pandas as pd, numpy as np
P=Path('/mnt/data/daa_january_full_execution_024')
ARCH=Path('/mnt/data/daa_jan_v1_reaudit_023')
old=json.loads((ARCH/'gamma02_jan_wd119_profit_per_heat_131e.json').read_text())
row=old['frontiers']['L35_C640']
cap512=json.loads((ARCH/'jan_profit_per_heat_atomic_131e.json').read_text())
cap512=next(x for x in cap512['rows'] if x['name']=='L35_C512')
jan30=cap512['daily']['2026-01-30']
history={
 'archive_label':'ORIGINAL_131E_HISTORICAL_NORMALIZED_SPREAD_NOT_RAW_EXECUTION',
 'net':row['net'],'trades':row['trades'],'watchdog_net':row['wd_net'],'watchdog_trades':row['wd_trades'],
 'watchdog_share_profit':row['wd_net']/row['net'],'watchdog_share_trades':row['wd_trades']/row['trades'],
 'supplementary_net':row['net']-row['wd_net'],'supplementary_trades':row['trades']-row['wd_trades'],
 'max_open':row['maxopen'],'floating_equity_dd':row['equity_dd'],
 'cap512_jan30_net_share':jan30['net']/cap512['net'],
 'cap512_jan30_trade_share':jan30['trades']/cap512['trades'],
 'cap512_net_excluding_jan30':cap512['net']-jan30['net'],
 'cap512_trades_excluding_jan30':cap512['trades']-jan30['trades'],
}
# Source 024 Watchdog q TP first-observed quote vs requested TP (stress, not broker fill truth)
over=[]
for cap in (16,64,128,256):
 d=pd.read_csv(P/f'baseline_cap{cap}_selected_trades.csv')
 q=d[(d.source==5)&(d.exit_reason==1)].copy()
 target=np.where(((q.entry_ms//60000)%60)//10==5,1.10,1.19)
 realized=(q.exit_quote_raw-q.entry_quote_raw)*q.direction/1000.
 excess=realized-target
 assert (excess>=-1e-9).all()
 origin_total=d[d.source==5].net.sum()
 over.append(dict(cap=cap,source5_watchdog_trades=int((d.source==5).sum()),tp_exits=int(len(q)),
  actual_quote_watchdog_net=float(origin_total),requested_target_stress_net=float(origin_total-excess.sum()),
  favorable_quote_tp_overshoot_usd=float(excess.sum()),positive_tp_profit=float(q.net.sum()),
  overshoot_fraction_of_tp_profit=float(excess.sum()/q.net.sum()),
  overshoot_median_usd=float(np.median(excess)),overshoot_p90_usd=float(np.quantile(excess,.9)),
  overshoot_max_usd=float(np.max(excess)),
  positive_profit_stress_semantics='clip favorable TP first quote to fixed requested TP, preserve all other entries/exit times and results; sensitivity only'))
# Minimal deterministic demonstration of the archive algorithm ordering problem.
# Pre-cap child outcomes are used to unlock parent; post-cap accepted subset may not contain those winners.
parent_child_exit_ms=np.array([10,20,30,40],np.int64)
precomputed_winning_exits=np.array([True,True,True,True],bool)
streak=0
for winner in precomputed_winning_exits:
 streak=streak+1 if winner else 0
precap_parent_unlock=streak>=4
# Counterfactual active higher-priority physical position consumes the only slot until ms50.
occupied_by_other_until=50
funded_children=np.array([not (x<occupied_by_other_until) for x in parent_child_exit_ms],bool)
funded_wins=precomputed_winning_exits & funded_children
funded_streak=0
for good in funded_wins:
 funded_streak=funded_streak+1 if good else 0
counterexample={'model':'toy example of static ordering bug, NOT measured Jan incidence',
  'parent_gate_uses_pre_cap_child_outcomes':bool(precap_parent_unlock),
  'funded_portfolio_child_wins':int(funded_wins.sum()),
  'parent_gate_if_only_funded_credit':bool(funded_streak>=4),
  'reason':'131E build_raw() evaluates prior child wins before capsel()/merge; a child rejected later by cap can still have its win counted for admission. Need single physical event scheduler to determine actual Jan incidence.'}
result={'study':'DAA_JAN_025_HIDDEN_MECHANISM_FORENSICS',
 'status':'historical decomposition and raw quote 024 sensitivity, plus synthetic causality counterexample',
 'input_sha256':hashlib.sha256(Path('/mnt/data/XAUUSD_DUKAS_2026_01_ticks.csv(3).gz').read_bytes()).hexdigest(),
 'history':history,'quote_tp_sensitivity':over,'funding_order_counterexample':counterexample,
 'source_notes':['131E original father 049/051 selector yields parent eligibility, but final 131E 131D portfolio merges children and supplementary tickets, not parent tickets. Parent credit/funding must be reconciled to final physical positions before parity can be claimed.','Requested-TP fill stress is not MT5 broker actual fill assumption; do not promote to actual result.']}
OUT=P/'DAA_JAN_025_HIDDEN_MECHANISM_FORENSICS.json'; OUT.write_text(json.dumps(result,indent=2))
print('ORIGINAL 131E WD net/trades',round(history['watchdog_net'],2),history['watchdog_trades'],'shares',round(history['watchdog_share_profit']*100,2),round(history['watchdog_share_trades']*100,2))
print('JAN30 >',round(history['cap512_jan30_net_share']*100,2),'% profit &',round(history['cap512_jan30_trade_share']*100,2),'% tickets of cap512 historical')
print('RAW 024 TP first-quote sensitivity:',[(x['cap'],x['tp_exits'],round(x['favorable_quote_tp_overshoot_usd'],3),round(x['requested_target_stress_net'],3)) for x in over])
print('GATE COUNTEREXAMPLE pre-cap unlock',precap_parent_unlock,'actual funded wins',funded_wins.sum(),'post-cap unlock',funded_streak>=4)
print('JSON',OUT)