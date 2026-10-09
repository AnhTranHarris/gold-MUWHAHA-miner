from pathlib import Path
import json,hashlib,datetime
import numpy as np
root=Path('/mnt/data/feb042');b=Path('/mnt/data/feb041')
expected={'feb':'ed3b3545c990c88d78519594c17c8915b0f679adcb0a94920ba7524f1f6d5c5d','jan':'d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5'}
def digest(path):
 h=hashlib.sha256()
 with open(path,'rb') as f:
  for c in iter(lambda:f.read(4*1024*1024),b''):h.update(c)
 return h.hexdigest()
paths={'feb':Path('/mnt/data/XAUUSD_DUKAS_2026_02_ticks.csv(3).gz'),'jan':Path('/mnt/data/XAUUSD_DUKAS_2026_01_ticks.csv(3).gz')}
verified={k:digest(v) for k,v in paths.items()}
assert all(verified[k]==expected[k] for k in paths)
import os,sys
os.environ['DAA_JAN039_RESEARCH_DIR']=str(b);sys.path[:0]=[str(b),str(b/'original/source')]
import feb041_legacy_engine as m
out={'data_sha256':verified,'development_replays':{},'screen_ledger_counts':{},'execution_model':'fixed historical source proposal tape with actual Feb quote first-touch; not true funded V1 broker','whitepaper':'literal owner 14232-char from GitHub freeze 030; 8-stage L0-L7', 'sealed_august_read':False}
for label,filename in [('high_ceiling','FEB042_EXPLORATORY_200K_LEDGER.npz'),('bounded_rate5','FEB042_RATE5_LEDGER.npz'),('bounded_rate6','FEB042_RATE6_LEDGER.npz'),('bounded_rate7','FEB042_RATE7_LEDGER.npz')]:
 z=np.load(root/filename);L={k:z[k].copy() for k in z.files};z.close();t=m.t[L['E']];n=len(t)
 assert len(np.unique(L['E']))==n and np.all(L['X']>L['E']);assert np.all(t>=1769904000000)&np.all(t<1772323200000)
 sec=t//1000;unique,cc=np.unique(sec,return_counts=True);maxsec=int(cc.max())
 recon=(np.where(L['D']>0,m.b[L['X']],m.a[L['X']])-L['R'])*L['D']/1000.-.02
 err=float(np.max(np.abs(recon-L['P'])));assert err<1e-10
 j=json.load(open(root/('FEB042_EXPLORATORY_200K_EXACT.json' if label=='high_ceiling' else 'FEB042_RATE'+label.split('rate')[-1]+'_EXACT.json')))
 maxrate=10 if label=='high_ceiling' else int(label.split('rate')[-1]);assert maxsec<=maxrate
 assert abs(j['metric']['net']-L['P'].sum())<=.002
 out['development_replays'][label]={'trades':n,'net':float(L['P'].sum()),'gross_loss':float(L['P'][L['P']<0].sum()),'pf':float(L['P'][L['P']>0].sum()/-L['P'][L['P']<0].sum()),'exact_dd':j['exact_tick_equity_dd'],'max_open':j['maxopen_exact'],'max_per_tick':1,'max_per_second':maxsec,'pnl_error':err,'positive_days':sum(v['net']>0 for v in j['daily'].values()),'active_days':len(j['daily']),'positive_weeks':sum(v['net']>0 for v in j['weekly'].values()),'active_weeks':len(j['weekly']),'extra_cost_0_20_net':float(L['P'].sum()-.2*n),'extra_cost_0_50_net':float(L['P'].sum()-.5*n),'extra_cost_1_net':float(L['P'].sum()-1*n)}
for p in root.glob('*SCREEN*.json'):
 try:out['screen_ledger_counts'][p.name]=len(json.load(open(p)))
 except:pass
out['total_logged_scenarios']=sum(out['screen_ledger_counts'].values())
(root/'FEB042_FINAL_QA.json').write_text(json.dumps(out,indent=2))
print('DATA_SHA',json.dumps(verified));print('SCREEN_COUNT',out['total_logged_scenarios'])
for k,v in out['development_replays'].items():print('QA',k,json.dumps(v))