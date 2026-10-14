"""GRID0319 deterministic synthetic fault injection, not a substitute for real tick research.
Ensures forced closes settle against observed opposing quote exactly once, no future
profit credit, and gapped prices may bankrupt even an operational stopout executor.
"""
import numpy as np
import grid0312_tick_stopout_executable as m


def one(q_bids,ratio):
 t=np.asarray([1000*i for i in range(len(q_bids))],dtype=np.int64)
 bid=(np.asarray(q_bids)*1000).astype(np.int64);ask=bid+2000
 start=1;stop=len(t)-1
 en=int(ask[start]);close=int(bid[stop]);
 z={'entry_idx':np.asarray([start]),'exit_idx':np.asarray([stop]),'entry_price_raw':np.asarray([en]),
    'direction':np.asarray([1]),'net_cash':np.asarray([(close-en)/1000.-.20]),
    'source':np.asarray(['coverage_gc0'])}
 args=(t,bid,ask,z,np.asarray([0],np.int8),np.asarray([-1],np.int32),np.asarray([0],np.int32))
 r=m.run(*args,cash=100.,cap=1,initial_cap=1,earned_cash_tiers=(),
   admission_margin_fraction=.35,stopout_ratio=ratio,loss_pause_n=0,gc0_cap=1)
 return r

def main():
 # Healthy path with same scheduled positive close; should settle exactly once.
 bids=[5000,5000,4998,5002,5050,5050]
 x=one(bids,.5)
 assert x['forced_events']==0 and x['trades_closed']==1
 assert abs(x['final_cash']-147.8)<1e-6, x['final_cash']
 # Early observed intraquote stop-out at 600% when ratio crosses 600% at i=3.
 down=[5000,5000,4998,4950,5050,5050]
 y=one(down,6.)
 assert y['forced_events']==1 and y['forced_positions']==1 and y['trades_closed']==1
 assert y['booked_ledger'][0][3]=='forced' and y['booked_ledger'][0][0]==3
 assert abs(y['final_cash']-47.8)<1e-6, y['final_cash']
 assert y['accepted_indices']==[0]
 # A gap can jump across a stop-out threshold at the first tradable quote.
 # Liquidation at that observed quote can leave NEGATIVE equity. Never label
 # this policy "100% survival" just because a stopout callback fired.
 gap=[5000,5000,4998,4890,5050,5050]
 z=one(gap,.5)
 assert z['forced_events']==1 and z['final_cash']<0 and z['trades_closed']==1
 assert z['booked_ledger'][0][3]=='forced' and z['booked_ledger'][0][0]==3
 print('GRID0319_8_CHECKS_PASS')
 print('favorable scheduled positive:',x['final_cash'])
 print('stop-out at observed quote then no ghost scheduled profit:',y['final_cash'])
 print('adverse quote-gap produces negative cash despite liquidation:',z['final_cash'])
if __name__=='__main__':main()
