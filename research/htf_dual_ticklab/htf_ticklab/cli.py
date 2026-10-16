"""CLI: python -m htf_ticklab.cli --broker coinexx --input ... --output ..."""
from __future__ import annotations
import argparse
import csv
from dataclasses import asdict
import hashlib
import json
import os
from pathlib import Path
from .feeds import FeedQuality, read_ticks
from .engine import BrokerConfig, Replay
from .strategies import NoTrades, ClosedBarImpulseDemo
from .source_registry import verify


def sha256_file(file:Path)->str:
    h=hashlib.sha256()
    with file.open('rb') as fp:
        for block in iter(lambda:fp.read(4*1024*1024),b''):h.update(block)
    return h.hexdigest()

def atomic_json(path:Path,data:dict):
    path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_suffix(path.suffix+'.partial')
    with tmp.open('w',encoding='utf-8') as f:
        json.dump(data,f,indent=2,allow_nan=False)
        f.flush();os.fsync(f.fileno())
    os.replace(tmp,path)

def atomic_trades_csv(path:Path,trades:list[dict]):
    path.parent.mkdir(parents=True,exist_ok=True)
    temp=path.with_suffix(path.suffix+'.partial')
    fields=['entry_ms','exit_ms','side','lots','entry_price','exit_price','gross_pnl',
            'net_pnl','reason','entry_fee','exit_fee','broker']
    with temp.open('w',newline='',encoding='utf-8') as handle:
        writer=csv.DictWriter(handle,fieldnames=fields)
        writer.writeheader();writer.writerows(trades)
        handle.flush();os.fsync(handle.fileno())
    os.replace(temp,path)

def parse_args(argv=None):
    parser=argparse.ArgumentParser(description='Isolated XAUUSD tick-level broker replay (research only)')
    parser.add_argument('--broker',choices=['coinexx','dukascopy'],required=True)
    parser.add_argument('--input',type=Path,nargs='+',required=True,help='ONE OR MORE chronological authorized monthly .csv.gz files; continuous account state')
    parser.add_argument('--output',type=Path,required=True,help='JSON checkpoint (written atomically)')
    parser.add_argument('--no-trade-ledger',action='store_true',help='omit per-trade CSV output')
    parser.add_argument('--strategy',choices=['none','impulse-demo'],default='none')
    parser.add_argument('--initial-balance',type=float,default=100.0)
    parser.add_argument('--contract-size',type=float,default=100.0)
    parser.add_argument('--leverage',type=float,default=500.0)
    parser.add_argument('--latency-ms',type=int,default=250)
    parser.add_argument('--slippage-price',type=float,default=0.0)
    parser.add_argument('--commission-per-lot-side',type=float,default=0.0)
    parser.add_argument('--max-spread-price',type=float,default=2.0)
    parser.add_argument('--min-stop-price',type=float,default=0.0)
    parser.add_argument('--dukas-scale',type=float,default=1000.0)
    parser.add_argument('--allow-unregistered-input',action='store_true',
                        help='TEST FIXTURES ONLY: bypass approved-source allowlist')
    parser.add_argument('--force',action='store_true',help='overwrite an existing checkpoint')
    parser.add_argument('--checkpoint-each-input',action='store_true',help='write an atomic cumulative state report after each source (multi-input runs)')
    return parser.parse_args(argv)

def main(argv=None):
    a=parse_args(argv)
    inputs=a.input
    if len({str(p.resolve()) for p in inputs})!=len(inputs):
        raise SystemExit('duplicate source path in input sequence')
    if a.output.exists() and not a.force:
        raise SystemExit('output exists; use --force only for deliberate reruns')
    ledger=a.output.with_name(a.output.stem+'_trades.csv')
    if not a.no_trade_ledger and ledger.exists() and not a.force:
        raise SystemExit('trade ledger exists; use --force for a deliberate rerun')
    paths=[a.output.with_name(f'{a.output.stem}.part-{i:02}.checkpoint.json')
           for i in range(1,len(inputs)+1)] if a.checkpoint_each_input else []
    if not a.force and any(p.exists() for p in paths):
        raise SystemExit('monthly checkpoint exists; use --force only for deliberate reruns')
    # Preflight the WHOLE requested source sequence before processing any quotes.
    # A renamed or corrupt later month must not partially initialize the replay.
    prepared=[]
    for path in inputs:
        if not path.is_file():raise SystemExit(f'input not found: {path}')
        if not path.name.endswith('.csv.gz'):raise SystemExit('input must be a .csv.gz')
        digest=sha256_file(path)
        try: pin=verify(path.name,a.broker,digest,a.allow_unregistered_input)
        except ValueError as exc: raise SystemExit(str(exc)) from exc
        prepared.append((path,digest,pin))
    # For authorized months require explicitly chronological order; never sort
    # user input silently. UTC quote monotonicity is independently enforced.
    if all(pin is not None for _,_,pin in prepared):
        import re
        months=[]
        for path,_,_ in prepared:
            match=re.search(r'2026_(\d\d)_ticks',path.name)
            if match is None:raise SystemExit('registered month cannot be identified')
            months.append(int(match.group(1)))
        if months!=sorted(set(months)):
            raise SystemExit('authorized sources must be unique, chronological months')
    cfg=BrokerConfig(name=a.broker,initial_balance=a.initial_balance,contract_size=a.contract_size,
                     leverage=a.leverage,order_latency_ms=a.latency_ms,
                     adverse_slippage_price=a.slippage_price,
                     commission_per_lot_side=a.commission_per_lot_side,
                     max_spread_price=a.max_spread_price,min_stop_distance_price=a.min_stop_price)
    strategy=NoTrades() if a.strategy=='none' else ClosedBarImpulseDemo()
    sim=Replay(cfg,strategy)
    sources=[]
    for idx,(path,fingerprint,pin) in enumerate(prepared):
        quality=FeedQuality()
        for quote in read_ticks(path,a.broker,quality,dukas_scale=a.dukas_scale):
            sim.on_quote(quote)
        details={'filename':path.name,'sha256':fingerprint,
                 'allowlist_match':pin is not None,'source_verified':pin is not None,
                 'dukas_price_divisor':a.dukas_scale if a.broker=='dukascopy' else None,
                 'quality':asdict(quality),'month_end_open_positions_not_force_closed':True}
        sources.append(details)
        if paths:
            checkpoint=sim.snapshot()
            checkpoint.update({'source':details,'sources':list(sources),'strategy_id':a.strategy,
                               'partial_checkpoint':True,'completed_inputs':idx+1,
                               'total_inputs':len(prepared),
                               'resume_supported':False})
            atomic_json(paths[idx],checkpoint)
    report=sim.snapshot()
    report.update({'source':sources[0] if len(sources)==1 else None,
                   'sources':sources,'strategy_id':a.strategy,'partial_checkpoint':False,
                   'continuous_state_across_inputs':len(sources)>1})
    if not a.no_trade_ledger:
        atomic_trades_csv(ledger,sim.trades)
        report['trade_ledger_file']=ledger.name
        report['trade_ledger_sha256']=sha256_file(ledger)
    atomic_json(a.output,report)
    print(json.dumps({'broker':a.broker,'inputs':len(sources),
                      'quotes':sum(s['quality']['total'] for s in sources),
                      'trades':report['trades'],'net':report['net_realized'],
                      'checkpoint':str(a.output)},indent=2))

if __name__=='__main__':main()
