"""Independent physical execution diagnostic on original Jan26/Feb17 observed ticks.

This is an intentionally bounded *research/idealized funded L7* counterfactual.
Original source E/S/D index files are used only for AFTER-run parity audits;
L7 receives source-generated raw quotes and source-defined lifecycle only.
Never treats the original X/P/H outcome tape as executable settlement.
"""
from __future__ import annotations
import hashlib,io,json,zipfile,time
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path
import sys
import numpy as np,pandas as pd
from dataclasses import asdict
sys.path.insert(0,str(Path(__file__).resolve().parent))
sys.path.insert(0,'/mnt/data/c2d3l_work/032_source')
import stmr_janjul as orig
from v1_funded_core_033c import FundedEngine, Limits, Quote, Structure
from original_50ms_funded_bridge_033 import OriginalJAN037L3QuoteBridge
from feb045_source_native_context_033 import FEB045NativeQualityL3
from original_jan039_source_owner_adapter_033 import exact_jan039_l3_chain

ROOT=Path('/mnt/data')
PARENT=Path(__file__).resolve().parent
RULES=PARENT/'verified_original_sources/JAN038/JAN038_SELECTED_EXACT.json'
EXPECT={'01':'d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5',
        '02':'ed3b3545c990c88d78519594c17c8915b0f679adcb0a94920ba7524f1f6d5c5d'}
WIDTHS=(14400000,3600000,900000,300000)

def timestamp(y,m,d,h=0):return int(datetime(y,m,d,h,tzinfo=timezone.utc).timestamp()*1000)

def exact_source_s26_indices(month_name:str,source_time):
    if month_name=='01':
        fn=ROOT/'bootstrap_inputs/JAN037_ITERATIVE_XAUUSD_TICK_RESEARCH_BUNDLE.zip';member='research/JAN037_EXPANDED_L3_50MS_PROPOSALS.npz';offset=0
    else:
        fn=ROOT/'feb_source_phase/FEB042_ITERATIVE_FEBRUARY_RESEARCH_BUNDLE.zip';member='FEB042/FEB042_JAN039_PREPARED_PROPOSALS.npz';offset=3900880
    with zipfile.ZipFile(fn) as z, np.load(io.BytesIO(z.read(member)),allow_pickle=False) as original:
        i=original['E'];s=original['S'];mask=(s==26)
        return i[mask]-offset


def run():
    start=time.monotonic()
    dfs={}
    for m in ('01','02'):
        f=ROOT/f'XAUUSD_DUKAS_2026_{m}_ticks.csv(3).gz'
        with f.open('rb') as fh:assert hashlib.file_digest(fh,'sha256').hexdigest()==EXPECT[m]
        dfs[m]=pd.read_csv(f,compression='gzip',usecols=['timestamp_ms_utc','ask_raw','bid_raw'],dtype={'timestamp_ms_utc':'i8','ask_raw':'i4','bid_raw':'i4'})
    jan=dfs['01'];warm=jan.iloc[-3900880:]
    both=pd.concat([warm,dfs['02']],ignore_index=True)
    output=[]
    for month_name,df,first,last,offset in [
        ('01',jan,timestamp(2026,1,26,16),timestamp(2026,1,26,17),0),
        ('02',both,timestamp(2026,2,17,16),timestamp(2026,2,17,17),0)]:
        t=df.timestamp_ms_utc.to_numpy(np.int64);a=df.ask_raw.to_numpy(np.int32);b=df.bid_raw.to_numpy(np.int32)
        states=orig.make_states(t,b,((8,21),(8,21),(8,21),(8,21)))
        startidx=int(np.searchsorted(t,first,'left'));endidx=int(np.searchsorted(t,last,'left'))
        # FEB042 source E indices are offsets in this same reconstructed combined tape.
        with zipfile.ZipFile((ROOT/'bootstrap_inputs/JAN037_ITERATIVE_XAUUSD_TICK_RESEARCH_BUNDLE.zip') if month_name=='01' else (ROOT/'feb_source_phase/FEB042_ITERATIVE_FEBRUARY_RESEARCH_BUNDLE.zip')) as z:
            memb='research/JAN037_EXPANDED_L3_50MS_PROPOSALS.npz' if month_name=='01' else 'FEB042/FEB042_JAN039_PREPARED_PROPOSALS.npz'
            with np.load(io.BytesIO(z.read(memb)),allow_pickle=False) as origfile:
                m=(origfile['S']==26)&(origfile['E']>=startidx)&(origfile['E']<endidx)
                original_indices=origfile['E'][m]
        for mode in ('JAN039_exact_S26_S27',):
            bridge=OriginalJAN037L3QuoteBridge(RULES,apply_jan038=True,label_family='F045' if mode=='FEB045_quality' else 'JAN037')
            adapter=exact_jan039_l3_chain(bridge)
            engine=FundedEngine(Limits(max_open=64,max_layer_open=64,max_per_source_open=64,
              max_same_direction=64,max_per_cell_side=64,max_spread_usd=5,
              max_orders_per_second=10,max_orders_per_tick=1,
              balance_usd=100000,max_equity_drawdown_usd=50000,
              max_underwater_open_usd=50000,max_margin_fraction_of_equity=0.9,
              reserve_stopout_fraction=0.9),[adapter],broker_contract_verified=True)
            sourced=[];no_context=0;last_bucket_ends=[0]*4
            for idx in range(startidx,endidx):
                now=int(t[idx]);q=Quote(now,int(a[idx]),int(b[idx]))
                h=tuple(int(x[idx]) for x in states)
                bridge.observe_raw_bidask(idx,q,h)
                if bridge._pending is not None:sourced.append(idx)
                ends=[]
                for k,w in enumerate(WIDTHS):
                    bucket=now//w
                    if bucket!=last_bucket_ends[k]:
                        z=int(np.searchsorted(t,bucket*w,'left'))-1
                        last_bucket_ends[k]=bucket
                    else:
                        z=int(np.searchsorted(t,bucket*w,'left'))-1
                    if z<0:ends=[];break
                    ends.append(int((t[z]//w+1)*w))
                structure=None
                if len(ends)==4 and all(0<v<now for v in ends):
                    structure=Structure('NY',*h,max(ends),f'ORIGINAL_JAN037_L3_SOURCE_HOUR_{(now//3600000)%24}',
                                        (now//600000)%6,tuple(ends))
                if structure is None:no_context+=1
                engine.process_quote(q,structure)
            mismatch=sum(x!=y for x,y in zip(sourced,original_indices))+abs(len(sourced)-len(original_indices))
            if mismatch:raise AssertionError(f'Source stage differs from original {month_name}/{mode}: {mismatch}')
            row={'evaluation_month':month_name,'policy_variant':mode,'start_utc_ms':first,'end_utc_ms':last,
                'quotes':endidx-startidx,'original_L3_s26_events':len(original_indices),
                'online_generated_source_events':len(sourced),'source_index_mismatches':mismatch,
                'original_JAN038_phase_excluded':bridge.excluded_by_jan038,'missing_ready_context_quotes':no_context,
                'real_funded_entry_callbacks':bridge.physical_callbacks,
                'research_idealized_funded':engine.score(),
                'broker_certified':False,'complete_optimized_economic_parity':False,
                'source_outcome_tape_not_read':True,
                'evaluation_month_never_passed_to_runtime':True}
            if mode=='FEB045_quality':row['feb045_denials']=adapter.denials
            output.append(row)
            print(json.dumps({'evaluation_month':month_name,'policy':mode,'source_events':len(sourced),
                  'funded_entries':bridge.physical_callbacks,'closed':len(engine.closed),
                  'pnl':engine.score()['net'],'sec':round(time.monotonic()-start,2)}),flush=True)
    dest=PARENT/'JAN_FEB_NATIVE_JAN039_L3_TO_FUNDED_L7_WINDOW_COUNTERFACTUAL_033.json'
    dest.write_text(json.dumps({'original_jan039_S26_S27_source_owner_quote_diagnostic':output,
         'original_event_generator_certification':'C2D3L FULL MONTH (separate)',
         'description':'bounded one-hour real-quote accounting test, not Jan/Feb optimized economic performance',
         'elapsed_s':round(time.monotonic()-start,2)},indent=2,default=lambda v:int(v) if isinstance(v,np.integer) else float(v))+'\n')
if __name__=='__main__':run()
