"""Unfundable diagnostic-capital throughput only. NEVER a $100 investor metric."""
import json,pandas as pd
from v2_f1_integrated import load_source,generate_sources,run_case,OUT

def run():
 d=load_source()
 ss=generate_sources(d['ts'],d['bid'][d['ix']].astype(float)*.001,d['qua'],d['imp'],d['eff'],d['acc'],d['span'],d['m1h'],d['m1l'],d['m1c'],d['m5c'],d['h1h'],d['h1l'],d['h1c'],d['m5dir'],d['h1dir'],d['h4dir'],d['m15dir'],d['atr5'])
 out=[]
 for mask in [1,254,255]:
  for spread in [1.2,2.0]:
   for ho in [18,45]:
    c={'mask':mask,'regime':0,'session':0,'exit':'ENGINE_OPPORTUNITY_TEST','stop':3.,'goal':8.,'arm':2.,'trail':1.,'hold':ho,'spreadcap':spread,'phase_start':0,'phase_end':59,'cooldown':250,'mode':0}
    l,z=run_case(d,ss,c,1_000_000.)
    out.append(dict(**c,**z,capital=1000000,account='UNFUNDED_THROUGHPUT_DIAGNOSTIC_NOT_R9_CASH'))
 p=pd.DataFrame(out);p.to_csv(OUT/'V2_DIAGNOSTIC_UNFUNDED_CAPACITY.csv',index=False)
 stats={'runs':len(out),'largest_trade_count':int(p.trades.max()),'funded_research_account_cash_certified':False,'same_100_USD_as_investor':False,'purpose':'Only bound how often causal software can process entry/exit events; no $100 profitability.'}
 (OUT/'V2_CAPACITY_ONLY_QA.json').write_text(json.dumps(stats,indent=2)+'\n')
 print('CAPACITY',stats)
if __name__=='__main__':run()
