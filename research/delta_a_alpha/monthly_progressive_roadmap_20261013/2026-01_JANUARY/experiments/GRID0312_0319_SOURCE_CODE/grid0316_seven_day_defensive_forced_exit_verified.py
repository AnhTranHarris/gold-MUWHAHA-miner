"""GRID0316 original tick funded-account 7-day forced-liquidation scenarios + independent QC.
Ten fixed-seed starts picked BEFORE these experiments, 7 complete days each.
Full deal ledgers (in source-row IDs, original entry/exit indices, net, close reason)
retained as JSON.gz. No live trading, no broker-specific stopout certification.
"""
from __future__ import annotations
import gzip,json,time,hashlib
from pathlib import Path
import numpy as np
import grid0313_seven_day_ten_start_stopout_frontier as previous
import grid0315_independent_7day_margin_liquidation_qc as qc
from grid0307_random_start_lowcapital_original_tick import TICK_SOURCE
ROOT=Path(__file__).resolve().parent
POLICIES=[
 ('PREV_MARGIN20_NO_EARLY_EXIT',.20,.50,0.,'worst_first',0.),
 ('MARGIN35_DEFENSIVE400_WORST',.35,.50,4.,'worst_first',0.),
 ('MARGIN35_DEFENSIVE400_FLATTEN',.35,.50,4.,'flatten',0.),
 ('MARGIN35_DEFENSIVE600_WORST',.35,.50,6.,'worst_first',0.),
 ('MARGIN35_DEFENSIVE600_FLATTEN',.35,.50,6.,'flatten',0.),
 ('MARGIN20_ADVERSE_SLIP10',.20,.50,0.,'worst_first',.10),
]

def main():
 st=time.time();t,bid,ask,z,kind,owner,pgid,r9,origin=previous.sim.prior.g.g.base.p.ancestor.base.materialize()
 eligible,days=previous.select_days(r9,t)
 assert days==json.load(open(ROOT/'grid0313_seven_day_100usd_stopout_froniter.json'))['sample_dates']
 outputs=[];qc_pass=0;detail_file=ROOT/'grid0316_all_booked_deals_original_tick.json.gz'
 with gzip.open(detail_file,'wt',encoding='utf-8',compresslevel=6) as led:
  for day in days:
   d=int(np.datetime64(day+'T00:00:00','ms').astype('int64'));lo=int(np.searchsorted(t,d,'left'));hi=int(np.searchsorted(t,d+7*86400000,'left'))
   ix=(z['entry_idx']>=lo)&(z['entry_idx']<hi)
   zz={k:v[ix].copy() for k,v in z.items()};kk=kind[ix];oo=owner[ix]
   zz['entry_idx']-=lo
   trunc=zz['exit_idx']>=hi;zz['exit_idx']=np.minimum(zz['exit_idx']-lo,hi-lo-1)
   keep=zz['entry_idx']<zz['exit_idx'];zz={k:v[keep] for k,v in zz.items()};kk=kk[keep];oo=oo[keep];trunc=trunc[keep]
   et=t[lo:hi];eb=bid[lo:hi];ea=ask[lo:hi]
   for j in np.flatnonzero(trunc):
    x=int(zz['exit_idx'][j]);di=int(zz['direction'][j]);zz['net_cash'][j]=di*(int(eb[x] if di>0 else ea[x])-int(zz['entry_price_raw'][j]))/1000.-.20
   for policy in POLICIES:
    r=previous.sim.run(et,eb,ea,zz,kk,oo,pgid,cash=100.,admission_margin_fraction=policy[1],stopout_ratio=policy[2],defensive_ratio=policy[3],liquidation_style=policy[4],defensive_flatten=policy[4]=='flatten',max_tick_slippage_usd=policy[5])
    deals=r.pop('booked_ledger');adm=r.pop('accepted_indices')
    truth=qc.reconstruct(et,eb,ea,zz,adm,deals,slippage_per_close=policy[5]);qc_pass+=7
    assert abs(truth['close_cash']-r['final_cash'])<1e-5,(day,policy,'cash',truth,r['final_cash'])
    assert abs(truth['min_equity']-r['min_tick_equity'])<1e-5,(day,policy,'minimum',truth,r['min_tick_equity'])
    assert abs(truth['max_equity_dd']-r['max_tick_drawdown'])<1e-5,(day,policy,'max dd',truth,r['max_tick_drawdown'])
    assert abs(truth['worst_hour_dd']-r['worst_hour_drawdown'])<1e-5,(day,policy,'hour dd',truth,r['worst_hour_drawdown'])
    r.update(date=day,policy=policy[0],seven_day_target_met=r['final_cash']>=10000.,model_nonruin=r['min_tick_equity']>0.,
             broker_stopout_free=r['forced_events']==0,independent_quote_qc=truth,quotes=len(et),
             window_end_utc_ms=int(et[-1]),booked_ledger_count=len(deals))
    outputs.append(r)
    led.write(json.dumps({'date':day,'policy':policy[0],'entry_candidate_idx':adm,'closed_deal_records':deals},separators=(',',':'))+'\n')
    print(day,policy[0],'end',round(r['final_cash'],2),'minE',round(r['min_tick_equity'],2),
     'trades',r['trades_closed'],'forced',r['forced_events'],'early',r['defensive_events'], 'DD',round(r['worst_hour_drawdown'],2),flush=True)
 summary={}
 for name,*_ in POLICIES:
  q=[x for x in outputs if x['policy']==name]
  summary[name]={'episodes':len(q),'nonruin':sum(x['model_nonruin'] for x in q),
                 'no_forced_broker_stopout':sum(x['broker_stopout_free'] for x in q),
                 'seven_day_100x':sum(x['seven_day_target_met'] for x in q),
                 'ending_min':min(x['final_cash'] for x in q),'ending_max':max(x['final_cash'] for x in q),
                 'min_intraday_equity':min(x['min_tick_equity'] for x in q),
                 'worst_hour_dd':max(x['worst_hour_drawdown'] for x in q),
                 'trades':sum(x['trades_closed'] for x in q),
                 'forced_liquidation_events':sum(x['forced_events'] for x in q),
                 'defensive_liquidation_events':sum(x['defensive_events'] for x in q)}
 result={'id':'GRID0316_SEVEN_DAY_ORIGINAL_TICK_EARLY_EXIT_LIQUIDATION_VERIFIED',
       'status':'UNPROMOTED_RESEARCH_NONBROKER_MARGIN_UNDER_HISTORICALLY_SELECTED_CANDIDATES',
       'source_sha256':hashlib.file_digest(TICK_SOURCE.open('rb'),'sha256').hexdigest(),
       'seed':previous.SEED,'start_days':days,'eligible_starts':eligible,'policies':POLICIES,
       'units':'0.01lot assumed 1oz, $0.20 commission, 500:1 notional margin, 250ms inherited entry delay, bid/ask execution',
       'full_deal_ledger_file':detail_file.name,'independent_checks':qc_pass,'full_model_limits':[
          'Broker margin details, 500x leverage, hedged margin, real stops and slippage unverified',
          'Actual Coinexx liquidation order, margin rules, per-position queue and execution delays unknown',
          'Historical selected source candidates and precomputed trade exit schedule are not an endogenous V1 engine',
          'Seven-calendar-day outcomes for historical starts do not guarantee survival in new months or live markets',
          'The full after-cost booked deal ledger was independently priced from original entry/exit Bid/Ask'],
       'summary':summary,'all_episodes':outputs,'elapsed_s':round(time.time()-st,2)}
 out=ROOT/'grid0316_seven_day_defensive_liquidation_independent_qc.json';out.write_text(json.dumps(result,indent=2))
 print('SAVED',out,detail_file,'checks',qc_pass,'elapsed',time.time()-st,flush=True)
if __name__=='__main__':main()
