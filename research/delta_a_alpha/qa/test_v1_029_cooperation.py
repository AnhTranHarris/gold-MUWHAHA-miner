#!/usr/bin/env python3
"""Audit of real executed February record + independent parallel source contracts."""
import ast,hashlib,json
from pathlib import Path
import numpy as np,pandas as pd
p=Path(__file__).resolve().parent
src=(p/'v1_029_cooperative_vertical_grid.py').read_text()
tree=ast.parse(src)
run=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='run')
assert 'for k in range(j):' in src, 'candidate multi-source loop missing'
assert 'if sr==0' not in src, 'legacy first-winner branch recovered'
assert 'qactive' in src and 'qexpire' in src, 'no proposal queue'
assert 'wd_streak[c]>=4' in src, 'unearned Watchdog unlock'
assert 'rec_valid=1' in src and 'typ[z] in (3,4,6)' in src, 'no funded recovery after loss'
assert 'if ti<emit_from:continue' in src, 'deployment leakage guard missing'
assert 'mbrange' in src and 'mbkey[bar_cursor]<m5bucket' in src, 'completed M5 boundary missing'
assert 'if h==17' in src and 'london_hold' in src, 'L3 hourly source missing'
assert 'if s==0 and cross' in src, 'separate Asia missing'
assert 'ss[j]=6' in src and 'native_ladder' in src, 'L6 trend within trend missing'
assert 'open_count[3]+open_count[8]' in src, 'L3 branches do not share governor budget'
m=json.loads((p/'coop029_cap128_a1_h0_d28_metrics.json').read_text())
f=pd.read_csv(p/'coop029_cap128_a1_h0_d28_trades.csv')
assert len(f)==m['trades'] and abs(f.net.sum()-m['net'])<1e-7
assert f.entry_idx.nunique()==len(f)
assert (f.exit_idx>=f.entry_idx).all()
assert max(abs((f.exit_raw-f.entry_raw)*f.direction/1000-.02-f.net))<1e-9
assert 0<m['max_open']<=m['position_cap']
assert set(f.layer.unique())=={3,4,5,6,7},'five funded sources did not execute'
assert m['first_state_ready_utc']==m['first_quote_utc']
assert m['stopout_events']==0
assert not np.isnan(f.net).any()
print(json.dumps({'source_sha256':hashlib.sha256(src.encode()).hexdigest(),
  'full_feb_trades':int(len(f)),'pnl_recon_max_error':float(max(abs((f.exit_raw-f.entry_raw)*f.direction/1000-.02-f.net))),
  'distinct_funded_families':list(map(int,sorted(f.layer.unique()))),'one_ticket_per_tick':True,
  'all_structural_assertions_passed':True,'status':'PASS_EXACT_RECONSTRUCTED_ENGINE_ONLY_NOT_134K_PARITY'},indent=2))