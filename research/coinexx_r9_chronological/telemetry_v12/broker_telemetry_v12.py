"""Read-only V12 MT5 DEMO deal/request telemetry validator.

This is not an execution engine. It NEVER submits orders or modifies positions.
Only observational records from the standalone MQL5 demo observer are accepted.
Request callback timestamps are *not* submit timestamps; price quotes at
callback are *not* fills. Order/deal event callback order is not guaranteed.
"""
from __future__ import annotations
import argparse
from collections import Counter,defaultdict
import csv
import json
from pathlib import Path
from statistics import median

COLUMNS=(
 'version','session','environment','event','callback_mono_ms',
 'callback_server_s','quote_time_msc','bid','ask','symbol','magic',
 'order_id','deal_id','position_id','request_side','retcode',
 'request_price','deal_time_msc','deal_price','volume','commission',
 'fee','swap','profit','deal_entry','deal_reason'
)
RETURNS={10004:'REQUOTE',10006:'REJECT',10008:'PLACED',10009:'DONE',
         10010:'DONE_PARTIAL',10012:'TIMEOUT',10015:'INVALID_PRICE',
         10016:'INVALID_STOPS',10018:'MARKET_CLOSED',10020:'PRICE_CHANGED',
         10021:'PRICE_OFF',10024:'TOO_MANY_REQUESTS',10029:'FROZEN',
         10030:'INVALID_FILL'}


def _num(value,field,cast=float):
    try:return cast(value)
    except (TypeError,ValueError) as e:
        raise ValueError(f'Bad {field}: {value!r}') from e


def _pct(values,p):
    if not values:return None
    v=sorted(values)
    return round(v[round((len(v)-1)*p)],6)


def audit(path:Path)->dict:
    counts=Counter();rets=Counter();entry=Counter();reason=Counter()
    sessions=set();symbols=set();requests=defaultdict(list);deals=[]
    seen_deals=set();issues=Counter();dropped=0
    with Path(path).open('r',encoding='utf-8-sig',newline='') as f:
        rd=csv.DictReader(f)
        if tuple(rd.fieldnames or ())!=COLUMNS:
            raise ValueError('Telemetry schema mismatch; cannot guess missing fields')
        for line,row in enumerate(rd,2):
            if None in row or any(x is None for x in row.values()):
                raise ValueError(f'Truncated telemetry line {line}')
            if row['version']!='V12' or row['environment']!='DEMO':
                raise ValueError('Non-DEMO or unexpected telemetry version')
            if not row['session'] or not row['symbol']:
                raise ValueError(f'Missing session/symbol at {line}')
            kind=row['event']
            if kind not in ('REQUEST','DEAL','LOSS_DIAGNOSTIC'):
                raise ValueError(f'Unsupported telemetry event {kind}')
            session=row['session'];sessions.add(session);symbols.add(row['symbol']);counts[kind]+=1
            _num(row['callback_mono_ms'],'callback_mono_ms',int)
            _num(row['callback_server_s'],'callback_server_s',int)
            if kind=='LOSS_DIAGNOSTIC':
                dropped+=_num(row['retcode'],'dropped rows',int)+_num(row['deal_reason'],'dropped deals',int)
                continue
            order=_num(row['order_id'],'order_id',int)
            if kind=='REQUEST':
                code=_num(row['retcode'],'retcode',int)
                rets[RETURNS.get(code,f'OTHER_{code}')]+=1
                if order:
                    requests[(session,order)].append(row)
            elif kind=='DEAL':
                deal_id=_num(row['deal_id'],'deal_id',int)
                if deal_id<=0:raise ValueError(f'Missing deal ticket at {line}')
                if (session,deal_id) in seen_deals:
                    issues['DUPLICATE_DEAL']+=1
                    continue
                seen_deals.add((session,deal_id))
                msc=_num(row['deal_time_msc'],'deal_time_msc',int)
                price=_num(row['deal_price'],'deal_price',float)
                vol=_num(row['volume'],'volume',float)
                if msc<=0 or price<=0 or vol<=0:
                    raise ValueError(f'Invalid server deal time/price/volume at {line}')
                ent=_num(row['deal_entry'],'deal_entry',int)
                rsn=_num(row['deal_reason'],'deal_reason',int)
                entry[str(ent)]+=1;reason[str(rsn)]+=1
                deals.append(row)
    observed=[];unmatched=0;ambiguous=0;volume_sum=0.
    for d in deals:
        order=int(d['order_id']); candidates=requests.get((d['session'],order),())
        # Only one uniquely-matched request with executable-type market side
        # and nonzero requested price yields conditional quote slippage.
        good=[r for r in candidates if int(r['request_side']) in (0,1)
                            and float(r['request_price'])>0]
        if len(good)!=1:
            ambiguous+=int(len(good)>1)
            unmatched+=int(len(good)==0)
            continue
        r=good[0]
        side=1 if int(r['request_side'])==0 else -1
        deviation=side*(float(d['deal_price'])-float(r['request_price']))
        vol=float(d['volume'])
        volume_sum+=vol
        observed.append((deviation,vol))
    deviations=[p for p,_ in observed]
    return {
      'source_name':Path(path).name,'schema':'R9_V12_DEMO_TRANSACTION_V1',
      'demo_only':True,'sessions':len(sessions),'symbols':sorted(symbols),
      'events':dict(counts),'unique_deals':len(deals),
      'retcodes':dict(rets),'deal_entry_types':dict(entry),
      'deal_reasons':dict(reason),
      'lost_event_rows_or_pending_deals':dropped,
      'data_quality_issues':dict(issues),
      'request_deal_unique_price_matches':len(observed),
      'request_deal_unmatched':unmatched,'request_deal_ambiguous':ambiguous,
      'conditional_requested_to_deal_price_adverse_units':{
         'n':len(deviations),'median':_pct(deviations,.5),
         'p90':_pct(deviations,.9),'p99':_pct(deviations,.99),
         'volume_weighted_mean':round(sum(p*v for p,v in observed)/volume_sum,6)
               if volume_sum else None},
      'latency_ms_request_to_fill':None,
      'latency_unavailable_reason':'Request send timestamp not captured; REQUEST callback is after trade-server response. Local monotonic callback clocks cannot be joined to server deal milliseconds without independent clock synchronization.',
      'callback_quote_not_authoritative_deal_quote':True,
      'actual_strategy_automation_not_enabled':True,
      'quality_pass_for_execution_inference':bool(deals and not dropped and not issues
                                         and not unmatched and not ambiguous
                                         and len(observed)==len(deals)),
      'not_financial_performance_or_order_execution':True,
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--input',required=True,type=Path)
    p.add_argument('--out',required=True,type=Path)
    a=p.parse_args()
    r=audit(a.input)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(r,sort_keys=True,indent=2)+'\n')
    print(json.dumps({'unique_deals':r['unique_deals'],'matchable':r['request_deal_unique_price_matches'],
                      'coverage_ok':r['quality_pass_for_execution_inference']}))

if __name__=='__main__':main()
