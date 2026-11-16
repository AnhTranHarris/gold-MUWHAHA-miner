"""V16: source-ordinal, causal 250ms/1s exit specialists, frozen V9 entries.

Prospective intervention design: observe only trade's own original quote path;
if an adverse-first event survives to a decision landmark, choose an early
exit on the *next source quote* while original V9 position is still open.
No winner labels, future prices, hidden execution assumptions, data downloads.
Maintains all frozen entry opportunities; exit-shifted counterfactual is NOT a
fully rearmed strategy (does not create new entries in freed time).
"""
import argparse,csv,gzip,hashlib,json,time,os
from pathlib import Path
import numpy as np,pandas as pd
SRC=Path(os.environ.get('COINEXX_DATA_ROOT','/mnt/data'))
LEDGERS=Path(os.environ.get('V12_EVENT_LEDGER_ROOT',str(SRC/'r9_micro180_v12_results')))
DEST=Path(os.environ.get('V16_RESEARCH_OUT',str(SRC/'v16_profitfirst')))
expected={ '01':(7699274,35500,35500),'02':(7102818,42742,42742),
'03':(8859103,51841,51841),'04':(7831685,37341,37340),
'05':(8011360,32514,32514),'06':(9347508,37190,37190),
'07':(8075197,33758,33758),'08':(7468061,32896,32896),
'09':(7734341,34283,34283) }
# Frozen, small set of domain-proposed exit mechanisms (NOT fitted in this code).
POLICIES=(
 'BASE',
 'C250_CUT_ADVERSE_ONLY',   # negative-first, still negative at 250ms -> cut
 'R1000_ALLOW_RECOVERY',   # negative-first at 250ms -> allow 1s to recover, else cut
 'D250_1000_TWO_STAGE',  # negative-first + severe at 250ms -> cut; else await 1s
)

def _first_after(ts,start,elapsed_ms,exit_idx,max_landmark_delay_ms):
    end_idx=int(np.searchsorted(ts,int(ts[start])+elapsed_ms,side='left'))
    if end_idx>=exit_idx or end_idx<=start or end_idx+1>=exit_idx:
        return None
    if int(ts[end_idx]-ts[start])-elapsed_ms>max_landmark_delay_ms:return None
    if int(ts[end_idx+1]-ts[end_idx])>600:return None
    return end_idx,end_idx+1

def intervention(times,bids,asks,record,policy):
    i=int(record['entry_ordinal'])-1; end=int(record['exit_ordinal'])-1
    s=int(record['side']);origin=int(record['entry_liquidation_u']);start=int(times[i]);
    if end<=i+1:return None
    # Exit may not use any future tick beyond the original V9 exit.
    q=bids if s>0 else asks
    point250=_first_after(times,i,250,end,250)
    if point250 is None:return None
    mark,act=point250
    if np.any(np.diff(times[i:mark+1])>2500):return None
    forward=(s*(q[i+1:mark+1].astype('int32')-origin))
    adverse=np.flatnonzero(forward<=-10)
    favorable=np.flatnonzero(forward>=10)
    # Actionable adverse-FIRST (not a retrospectively labeled losing trade)
    if not adverse.size or (favorable.size and favorable[0]<adverse[0]):return None
    at250=int(forward[-1]);mismatch=int((s*(int(q[mark])-origin)))
    assert at250==mismatch
    if policy=='C250_CUT_ADVERSE_ONLY':
        if at250<=-5: return act,'ADVERSE_FIRST_250MS_CUT'
        return None
    if policy=='D250_1000_TWO_STAGE' and at250<=-20:
        return act,'ADVERSE_FIRST_SEVERE_250MS_CUT'
    point1000=_first_after(times,i,1000,end,250)
    if point1000 is None:return None
    observed,act1=point1000
    if np.any(np.diff(times[mark:observed+1])>2500):return None
    # A quote-side reclaim within first 1s is precisely what V14 recovery
    # winners often needed. If the observed quote has recovered, preserve V9.
    at1=int(s*(int(q[observed])-origin))
    if at1<=-5: return act1,'ADVERSE_FIRST_UNRECOVERED_1S_CUT'
    return None

def run(month):
    t0=time.monotonic();raw=SRC/f'XAUUSD_MT5_BROKER_2026_{month}_ticks_ALL.csv.gz'
    if not raw.exists():raise FileNotFoundError(raw)
    # The original V12 receipt is authoritative for source hash.
    source_receipt=LEDGERS/'V12_MONTHLY_SOURCE_PROOF.csv'
    rows=pd.read_csv(source_receipt,dtype={'month':str})
    source_sha=rows.set_index('month').loc[month,'source_sha256']
    with raw.open('rb') as f:checksum=hashlib.file_digest(f,'sha256').hexdigest()
    assert checksum==source_sha, f'original source SHA mismatch {month}'
    # Important: no new / transformed market-data files are written.
    df=pd.read_csv(raw,compression='gzip',usecols=['time_msc','bid','ask'],dtype={'time_msc':'int64','bid':'float64','ask':'float64'})
    times=df.time_msc.to_numpy(dtype='int64');bids=np.rint(df.bid.to_numpy()*100).astype('int32');asks=np.rint(df.ask.to_numpy()*100).astype('int32');del df
    path=LEDGERS/f'2026-{month}_V12_exactms_micro180_events.csv.gz'
    cols=['entry_ordinal','exit_ordinal','entry_time_msc','exit_time_msc','entry_execution_u','entry_liquidation_u','exit_price_u','side','exit_reason']
    trades=pd.read_csv(path,compression='gzip',usecols=cols)
    assert len(times)==expected[month][0] and len(trades)==expected[month][1]
    closed=trades[trades.exit_ordinal.notna()].copy()
    assert len(closed)==expected[month][2]
    policies={p:[] for p in POLICIES};effects={p:0 for p in POLICIES}
    cases={p:[] for p in POLICIES if p!='BASE'}
    for trade in closed.itertuples(index=False):
        i=int(trade.entry_ordinal)-1;x=int(trade.exit_ordinal)-1
        assert 0<=i<x<len(times)
        assert times[i]==trade.entry_time_msc and times[x]==trade.exit_time_msc
        side=int(trade.side)
        old_px=int(trade.exit_price_u);open_px=int(trade.entry_execution_u)
        original_net=round(side*(old_px-open_px)/100.-.2,4)
        policies['BASE'].append(original_net)
        # Causal changes start only after a quote landmark, when position remains open.
        for policy in POLICIES[1:]:
            decision=intervention(times,bids,asks,trade._asdict(),policy)
            if decision is None:
                net=original_net
            else:
                j,reason=decision
                assert j<x and times[j]>=times[i] and j>i
                newpx=int(bids[j] if side>0 else asks[j])
                net=round(side*(newpx-open_px)/100.-.2,4)
                effects[policy]+=1
                cases[policy].append(dict(entry_ordinal=i+1,exit_original_ordinal=x+1,
                    exit_policy_ordinal=j+1,original_net=original_net,
                    policy_net=net,exit_reason=reason))
            policies[policy].append(net)
    result={'month':month,'source_sha256':checksum,'quotes':len(times),'entries':len(trades),
            'closed_trades':len(closed),'original_v9_entries_preserved':True,
            'not_fully_rearmed':True,'broker_slippage_unknown':True,'sample_research_only':True,'policies':{}}
    for name,values in policies.items():
        v=np.array(values,dtype=float);eq=np.cumsum(v);dd=float(np.max(np.maximum.accumulate(np.r_[0,eq])-np.r_[0,eq]))
        result['policies'][name]=dict(trades=len(v),net=round(float(v.sum()),2),mean_net=round(float(v.mean()),6),
            winners=int(np.sum(v>0)),win_rate=round(float(np.mean(v>0)),6),
            exit_interventions=effects.get(name,0),max_closed_trade_drawdown=round(dd,2))
    DEST.mkdir(parents=True,exist_ok=True)
    for policy,cases_rows in cases.items():
        file=DEST/f'V16_{month}_{policy}_changes.csv.gz'
        with gzip.open(file,'wt',newline='') as f:
            writer=csv.DictWriter(f,fieldnames=['entry_ordinal','exit_original_ordinal','exit_policy_ordinal','original_net','policy_net','exit_reason'])
            writer.writeheader();writer.writerows(cases_rows)
    out=DEST/f'V16_{month}_PROSPECTIVE_EXIT.json';out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'month':month,'sec':round(time.monotonic()-t0,2),
        'entries':len(trades),'baseline':result['policies']['BASE']['net'],
        'policies':{k:{'net':v['net'],'improvement':round(v['net']-result['policies']['BASE']['net'],2),'changed':v['exit_interventions']} for k,v in result['policies'].items() if k!='BASE'}}),flush=True)
    return result

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('months',nargs='*');x=p.parse_args()
 for month in x.months or ('01','05','09'):run(month)
