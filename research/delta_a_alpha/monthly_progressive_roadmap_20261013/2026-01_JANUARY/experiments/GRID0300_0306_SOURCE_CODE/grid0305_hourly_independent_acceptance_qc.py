"""GRID0305 read-only independent source-exact January QC for GRID0304 Pareto.
No live engine writes, no owner acceptance; two original-tick reproducibility
cases + negative low-capital diagnostic + independent tick-by-tick equity path.
"""
from __future__ import annotations
import hashlib,json,math
from pathlib import Path
from collections import Counter
import numpy as np,pandas as pd
import grid0303_causal_coverage_source_caps as g
from grid0302_hourly_source_attribution import independent_equity_peaktrough
ROOT=Path(__file__).resolve().parent
RAW=Path('/mnt/data/XAUUSD_DUKAS_2026_01_ticks.csv(3).gz')
TARGET_SHA='d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5'
CHECKS=[]

def check(note,condition):
    CHECKS.append({'test':note,'passed':bool(condition)})
    if not condition:raise AssertionError(note)

# This local-only injection exposes selected row identities for INDEPENDENT
# verification; does not change strategy admission, source or timing.
source=g.source
needle='    return r'
assert source.count(needle)==1
source=source.replace(needle,'    r["exact_accepted_indices_qc_only"]=idx.tolist()\n    return r')
namespace=dict(g.ns)
exec(source,namespace)
replay=namespace['physical_replay']

def params(usd,cap0,cap2):
 return dict(cash=usd,cap=256,loss_pause_n=2,pause_ms=300000,native16_cap=2,
 earned_native_cap=32,earned_wins=7,earned_window=10,earned_edge=12,parent_cap=16,
 earned_parent_cap=192,parent_wins=4,parent_window=6,parent_edge=4,
 hourly_entry_lock_usd=0.,hourly_soft_parent_usd=400.,hourly_soft_parent_cap=64,
 gc0_cap=cap0,gc2_cap=cap2)

def independent(t,bid,ask,z,idx,cash):
 ei=z['entry_idx'][idx];xi=z['exit_idx'][idx];dire=z['direction'][idx];net=z['net_cash'][idx];px=z['entry_price_raw'][idx]
 n=len(t)
 dl=np.zeros(n,np.int32);ds=np.zeros(n,np.int32);db=np.zeros(n,np.float64);dc=np.zeros(n,np.float64)
 for j,k in enumerate(idx):
  i=int(ei[j]);x=int(xi[j]);d=int(dire[j]);entry=int(px[j])/1000.
  if d>0:dl[i]+=1;dl[x]-=1
  else:ds[i]+=1;ds[x]-=1
  db[i]+=d*entry;db[x]-=d*entry;dc[x]+=float(net[j])
 first=int(t[0]//3600000)
 hourly,peaks,lows=independent_equity_peaktrough(t,bid,ask,dl,ds,db,dc,cash,first)
 return hourly,peaks,lows

def main():
 h=hashlib.sha256()
 with RAW.open('rb') as f:
  while b:=f.read(4*1024*1024):h.update(b)
 check('original gzip SHA256 matches owner immutable source',h.hexdigest()==TARGET_SHA)
 t,bid,ask,z,kind,owner,pgid,r9,origin=g.g.base.p.ancestor.base.materialize()
 check('original 9,135,062 January quote rows',len(t)==9135062)
 check('original quotes ordered',bool(np.all(np.diff(t)>=0)))
 check('original executable quotes ordered bid<=ask',bool(np.all(bid<=ask)))
 check('original child quote settlement reconstructed exactly',origin['child_quote_error']==0.0)
 archived=json.loads((ROOT/'grid0304_coverage_hourly_pareto_full_january.json').read_text())
 records={r['name']:r for r in archived['variants']}
 tested=[('G0216_G2216_PARENT_PRESSURE400',216,216,100000.),
         ('G0256_G2224_PARENT_PRESSURE400',256,224,100000.),
         ('G0256_G2224_PARENT_PRESSURE400_LOW_CASH300_DIAGNOSTIC',256,224,300.)]
 outputs=[]
 for name,gc0,gc2,cash in tested:
  r=replay(t,bid,ask,z,kind,owner,pgid,r9,**params(cash,gc0,gc2))
  ix=np.asarray(r.pop('exact_accepted_indices_qc_only'),np.int64)
  check(name+' trade source count match',len(ix)==r['trades'])
  check(name+' one entry per quote index',len(np.unique(z['entry_idx'][ix]))==len(ix))
  check(name+' no future exit before entry',bool(np.all(z['exit_idx'][ix]>=z['entry_idx'][ix])))
  check(name+' entry tick ask/bid exact',bool(np.all(z['entry_price_raw'][ix]==np.where(z['direction'][ix]>0,ask[z['entry_idx'][ix]],bid[z['entry_idx'][ix]]))))
  expected=((np.where(z['direction'][ix]>0,bid[z['exit_idx'][ix]],ask[z['exit_idx'][ix]]).astype('float64') -z['entry_price_raw'][ix].astype('float64'))*z['direction'][ix]/1000.-.20)
  check(name+' every cash settlement is exact opposite executable quote minus fee',bool(np.allclose(expected,z['net_cash'][ix],atol=1e-9,rtol=0)))
  check(name+' closed settlement sum',math.isclose(float(expected.sum()),r['net'],abs_tol=1e-5,rel_tol=1e-10))
  check(name+' daily cash reconciliation',math.isclose(sum(x['net'] for x in r['daily'].values()),r['net'],abs_tol=1e-5))
  check(name+' weekly cash reconciliation',math.isclose(sum(x['net'] for x in r['weekly'].values()),r['net'],abs_tol=1e-5))
  hh,pidx,lidx=independent(t,bid,ask,z,ix,cash)
  check(name+' completely independent all-quote hourly floating equity drawdown',math.isclose(float(hh.max()),r['max_hourly_tick_equity_drawdown_usd'],abs_tol=1e-5))
  offset=int(t[0]//3600000);dindex=pd.to_datetime((np.arange(len(hh))+offset)*3600000,unit='ms',utc=True).strftime('%Y-%m-%d')
  day_impact={}
  for d,v in zip(dindex,hh):day_impact[d]=max(day_impact.get(d,0.),float(v))
  check(name+' all 31 UTC calendar day hourly-risk reports independently matched',all(math.isclose(v,day_impact.get(k,0.),abs_tol=1e-5) for k,v in r['daily_worst_hourly_drawdown_usd'].items()))
  if cash>=100000:
   ref=records[name]
   for field in ['net','gross_profit','gross_loss','trades','max_all_tick_floating_equity_dd','max_hourly_tick_equity_drawdown_usd','r9_synth_days_net_met','r9_synth_weeks_net_met']:
    check(name+' source locked replay matches preserved '+field,math.isclose(r[field],ref[field],abs_tol=1e-5,rel_tol=1e-10))
   check(name+' 21 positive cash days',len(r['daily'])==21 and all(v['net']>0 for v in r['daily'].values()))
   check(name+' 5 positive cash weeks',len(r['weekly'])==5 and all(v['net']>0 for v in r['weekly'].values()))
   check(name+' R9 SYNTH January monthly NET target',r['net']>=41520.82)
   check(name+' cannot claim monthly R9 trade target',r['trades']<27980)
   check(name+' cannot claim all 21 R9 daily net targets',r['r9_synth_days_net_met']<21)
   check(name+' cannot claim all 5 R9 weekly net targets',r['r9_synth_weeks_net_met']<5)
  else:
   check(name+' low-capital source replay is research-only',cash==300.)
  worstidx=int(np.argmax(hh));vday=str(pd.to_datetime((worstidx+offset)*3600000,unit='ms',utc=True).date())
  out={'name':name,'starting_cash':cash,'net':r['net'],'trades':r['trades'],'gross_loss':r['gross_loss'],
       'all_tick_dd':r['max_all_tick_floating_equity_dd'],'hourly_dd':r['max_hourly_tick_equity_drawdown_usd'],
       'worst_utc_day':vday,'worst_hour_utc':str(pd.to_datetime((worstidx+offset)*3600000,unit='ms',utc=True)),
       'worst_hour_peak_tick_index':int(pidx[worstidx]),'worst_hour_trough_tick_index':int(lidx[worstidx]),
       'daily_worst_hourly_dd':r['daily_worst_hourly_drawdown_usd'],
       'days_positive':sum(v['net']>0 for v in r['daily'].values()),'weeks_positive':sum(v['net']>0 for v in r['weekly'].values()),
       'r9_daily_net_met':r['r9_synth_days_net_met'],'r9_weekly_net_met':r['r9_synth_weeks_net_met'],
       'r9_daily_velocity_met':r['r9_synth_days_trades_met'],'r9_weekly_velocity_met':r['r9_synth_weeks_trades_met'],
       'open_max':r['max_funded_positions'],'min_equity':r['min_actual_tick_equity'],
       'ending_equity':r['ending_equity'],'hour_online_block_count':r['online_hourly_blocks']}
  outputs.append(out)
  print(name, 'net',round(r['net'],2),'N',r['trades'],'hourDD',round(r['max_hourly_tick_equity_drawdown_usd'],2),
     'minEQ',round(r['min_actual_tick_equity'],2),'positive days',out['days_positive'],'weeks',out['weeks_positive'],flush=True)
 report={'id':'GRID0305_SOURCE_EXACT_HOURLY_DD_AND_PERIOD_INDEPENDENT_READONLY_QC',
   'source_sha256':h.hexdigest(),'status':'RESEARCH_ONLY_NO_ENGINE_INTEGRATION_NO_OWNER_ACCEPTANCE',
   'checks_passed':len(CHECKS),'checks':CHECKS,'profiles':outputs,
   'limits':['Original event universe contains historical pre-selection, not an endogenous Python L0-L7 generator.',
             'Saved after-cost closes are used only at the observed closing tick for future admission, not as future PnL features.',
             'Two fixed-lot simulated actions per source family are not independent Coinexx execution evidence.',
             'All profiles are in-sample January; this does not establish survivability or forward profitability.',
             'R9 OVERFIT teacher is not scored; per-day/week R9 cash/velocity acceptance remains incomplete.']}
 f=ROOT/'grid0305_hourly_independent_qc_results.json';f.write_text(json.dumps(report,indent=2))
 print('PASS',len(CHECKS),'source-exact independent QC checks; file',f)
if __name__=='__main__':main()
