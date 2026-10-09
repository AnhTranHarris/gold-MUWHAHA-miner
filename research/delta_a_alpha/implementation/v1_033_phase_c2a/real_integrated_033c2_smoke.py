"""C2 source-funded 049→075→119 diagnostic on genuine contiguous Feb Bid/Ask.
Not full 049 candidate-union parity or complete V1 funded portfolio performance.
"""
from __future__ import annotations
import hashlib,json
from pathlib import Path
import numpy as np,pandas as pd
from real_dukas_event_smoke_033 import orig_completed_state_fn,load_window,EXPECTED
from v1_funded_core_033 import Quote,Structure,Limits,FundedEngine,OriginalHourlyHeartbeatL3
from original_online_sources_033c import Original131DSessionL3
from original_funded_lineage_033c2 import (Original049OnlineSource,Original049FundedCapacity,Original049Settings,
                                           Original119FundedParentSource)

def run(root:Path,out:Path,max_quotes=250000,low_surge=False):
 for mm,tag in [('01','jan'),('02','feb')]:
    f=root/f'XAUUSD_DUKAS_2026_{mm}_ticks.csv(3).gz'
    h=hashlib.sha256()
    with f.open('rb') as fh:
        for b in iter(lambda:fh.read(4*1024*1024),b''):h.update(b)
    assert h.hexdigest()==EXPECTED[tag],f'{tag} SHA mismatch'
 ms=lambda ts:int(pd.Timestamp(ts,tz='UTC').value//1000000)
 jan=load_window(root/'XAUUSD_DUKAS_2026_01_ticks.csv(3).gz',ms('2026-01-22'),ms('2026-02-01'))
 feb=load_window(root/'XAUUSD_DUKAS_2026_02_ticks.csv(3).gz',ms('2026-02-02 06:30:00'),ms('2026-02-03 19:00:00')).iloc[:max_quotes]
 z=pd.concat((jan,feb),ignore_index=True)
 t=z.timestamp_ms_utc.to_numpy(np.int64);a=z.ask_raw.to_numpy(np.int32);b=z.bid_raw.to_numpy(np.int32)
 assert np.all(t[1:]>=t[:-1]); f=orig_completed_state_fn(root/'JAN037_ITERATIVE_XAUUSD_TICK_RESEARCH_BUNDLE.zip')
 states={};ends={}
 for n,tf in [('h4',14400000),('h1',3600000),('m15',900000),('m5',300000)]:
    states[n]=f(t,b,tf,8,21)
    buck=t//tf;starts=np.r_[0,np.flatnonzero(buck[1:]!=buck[:-1])+1];last=np.r_[starts[1:]-1,len(t)-1]
    prev=np.searchsorted(buck[starts],buck,side='left')-1
    en=np.full(len(t),-1,np.int64);valid=prev>=0;en[valid]=t[last[prev[valid]]]
    ends[n]=en
 quota=Original049FundedCapacity(Original049Settings(base_cap=2,base_step=1,base_unit=2500.,base_max=2,initial_surge=0,surge_step=0,surge_unit=2500.,max_surge=0,hard_max=2)) if low_surge else Original049FundedCapacity()
 wd=Original119FundedParentSource()
 hb=Original049OnlineSource(OriginalHourlyHeartbeatL3(50),quota);grid=Original131DSessionL3()
 eng=FundedEngine(Limits(max_open=32,max_layer_open=32,max_same_direction=32,max_per_source_open=32,
                 max_per_cell_side=16,max_orders_per_second=4,max_orders_per_tick=1,
                 max_underwater_open_usd=8000,max_spread_usd=3.0),
                 [hb,grid,wd],broker_contract_verified=True)
 for i in range(len(jan),len(t)):
    tm=int(t[i]);bar_ends=tuple(int(ends[k][i]) for k in ('h4','h1','m15','m5'))
    if all(x>0 for x in bar_ends):
        st=Structure('DIAGNOSTIC',*(int(states[k][i]) for k in ('h4','h1','m15','m5')),
             max(bar_ends),f'GRID:{tm//600000}',(tm//600000)%6,bar_ends)
    else:st=None
    eng.process_quote(Quote(tm,int(a[i]),int(b[i])),st)
 score=eng.score();doc={
    'status':'DIAGNOSTIC_SUBSET_ORIGINAL_019_NOT_FULL_049_CANDIDATE_UNION_OR_FULL_OWNER_V1',
    'february_dukascopy_contiguous_quotes':len(feb),'genuine_prior_january_context_quotes':len(jan),
    'source_historical_parent_union':'NOT_YET_PORTED_024_017_019_AND_GLOBAL_DEDUP',
    'first_touch_075':'PARENT_SELECTION_FROM_ACTUALLY_ACCEPTED_L3_ONLY__NOT_FULL_075_OPTIMIZATION',
    'source_049_surge_mode':'SOURCE_CAP_2_DIAGNOSTIC' if low_surge else 'ORIGINAL_049_051_FROZEN_CAP_GEOMETRY',
    'realized_049':round(quota.realized,6),'049_capacity_permitted_source_proposals':quota.eligible,
    '049_source_cap_denials':quota.denied,'049_allowed_last':quota.cap(),
    'actually_funded_119_cell_windows':wd.parent_funded,
    'eligible_funded_parent_candidates':wd.parent_candidates,
    'actually_funded_119_children':sum(x['event']=='FILL' and x.get('layer')=='L4' for x in eng.events),
    'source_119_rearm_denials':wd.renewal_rearm_rejects,
    'economics_diagnostic_only_not_month_performance':score,
    'original_full_L2_L5_L6_and_Coinexx_L7':'NOT_CERTIFIED',
    'original_frozen_V1_and_monthly_research':'UNMODIFIED','august':'SEALED','september':'RESERVED'}
 out.write_text(json.dumps(doc,indent=2)+'\n')
 print(json.dumps(doc));return doc

if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--root',default='/mnt/data');p.add_argument('--max-quotes',type=int,default=250000);p.add_argument('--low-surge',action='store_true');p.add_argument('--out',default='/mnt/data/DAA_033_phase_c2/REAL_INTEGRATED_033C2_SMOKE.json');args=p.parse_args()
 run(Path(args.root),Path(args.out),args.max_quotes,args.low_surge)