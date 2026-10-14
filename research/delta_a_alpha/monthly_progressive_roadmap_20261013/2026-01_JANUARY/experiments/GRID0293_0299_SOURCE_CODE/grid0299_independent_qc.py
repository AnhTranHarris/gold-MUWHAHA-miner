"""GRID0299 independent read-only reproducibility/QC of 0293-0298 research.
Audits full original January original Bid/Ask source and independent scoring.
Never promotes, authorizes deployment, or writes active FourSessionV1.
"""
from __future__ import annotations
from pathlib import Path
import hashlib,json,math
import grid0296_parent_earned_exposure as p
ROOT=Path(__file__).resolve().parent
RAW=Path('/mnt/data/XAUUSD_DUKAS_2026_01_ticks.csv(3).gz')
SHA='d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5'
checks=[]
def check(name,yes):
 checks.append({'name':name,'passed':bool(yes)});
 if not yes:raise AssertionError(name)

def main():
 h=hashlib.sha256()
 with RAW.open('rb') as f:
  while data:=f.read(4*1024*1024):h.update(data)
 check('original gzip SHA256 unchanged',h.hexdigest()==SHA)
 t,bid,ask,z,kind,owner,pgid,r9,origin=p.p.ancestor.base.materialize()
 check('original full month 9,135,062 ordered quotes',len(t)==9135062)
 check('source individual Bid <= Ask',bool((bid<=ask).all()))
 check('source owner candidate quote equality',origin['child_quote_error']==0.0)
 j=json.loads((ROOT/'grid0297_earned_parent_robustness_frontier_full_results.json').read_text())
 o={r['name']:r for r in j['variants']}
 verify_names=['RAISE128_3of5_2','RAISE192_4of6_4','RAISE256_4of6_4']
 for name in verify_names:
  result=o[name]
  replay=p.physical_replay(t,bid,ask,z,kind,owner,pgid,r9,cash=100000.,cap=256,loss_pause_n=2,pause_ms=300000,native16_cap=2,earned_native_cap=32,earned_wins=7,earned_window=10,earned_edge=12,parent_cap=16,earned_parent_cap=int(result['earned_parent_cap']),parent_wins=(3 if name=='RAISE128_3of5_2' else 4),parent_window=(5 if name=='RAISE128_3of5_2' else 6),parent_edge=(2 if name=='RAISE128_3of5_2' else 4))
  for fld in ['net','gross_profit','gross_loss','max_all_tick_floating_equity_dd','trades','verified_parent','verified_child','r9_synth_days_net_met','r9_synth_weeks_net_met']:
   check(f'{name} stable {fld}',math.isclose(float(replay[fld]),float(result[fld]),abs_tol=1e-6,rel_tol=1e-9))
  check(f'{name} day cash reconciles',math.isclose(sum(v['net'] for v in replay['daily'].values()),replay['net'],rel_tol=1e-9,abs_tol=1e-5))
  check(f'{name} week cash reconciles',math.isclose(sum(v['net'] for v in replay['weekly'].values()),replay['net'],rel_tol=1e-9,abs_tol=1e-5))
  check(f'{name} all 21 trading days net positive',len(replay['daily'])==21 and all(v['net']>0 for v in replay['daily'].values()))
  check(f'{name} all 5 ISO week segments net positive',len(replay['weekly'])==5 and all(v['net']>0 for v in replay['weekly'].values()))
  check(f'{name} monthly R9 target exceeded',replay['net']>replay['r9_synth_month_target'])
  check(f'{name} fails to reach monthly R9 completed velocity',replay['trades']<replay['r9_synth_month_trades'])
  check(f'{name} fails full daily target acceptance',replay['r9_synth_days_net_met']<21)
  check(f'{name} fails full weekly target acceptance',replay['r9_synth_weeks_net_met']<5)
  check(f'{name} actually funded WD positive only via children',replay['verified_parent']>0 and replay['verified_child']>0)
 report={'id':'GRID0299_JAN_RESEARCH_CROSSREPRO_QC','source_sha256':h.hexdigest(),'checks_passed':len(checks),'checks':checks,'status':'RESEARCH_ONLY_NO_QC_PROMOTION','tested_reference_ids':verify_names,'not_tested':['broker execution','small account','February-July independent replay','unselected historical source candidate populations','R9 OVERFIT 75% six teacher scores']}
 out=ROOT/'grid0299_independent_jan_qc_results.json';out.write_text(json.dumps(report,indent=2));print('SUCCESS',len(checks),'checks',out)
if __name__=='__main__':main()
