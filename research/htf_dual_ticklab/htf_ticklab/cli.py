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
    parser.add_argument('--input',type=Path,required=True,help='ONE authorized monthly .csv.gz file')
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
    return parser.parse_args(argv)

def main(argv=None):
    a=parse_args(argv)
    if not a.input.is_file():raise SystemExit(f'input not found: {a.input}')
    if not a.input.name.endswith('.csv.gz'):raise SystemExit('input must be a .csv.gz')
    if a.output.exists() and not a.force:raise SystemExit('output exists; use --force only for deliberate reruns')
    fingerprint=sha256_file(a.input)
    try:
        pin=verify(a.input.name,a.broker,fingerprint,a.allow_unregistered_input)
    except ValueError as exc: raise SystemExit(str(exc)) from exc
    cfg=BrokerConfig(name=a.broker,initial_balance=a.initial_balance,contract_size=a.contract_size,
                     leverage=a.leverage,order_latency_ms=a.latency_ms,
                     adverse_slippage_price=a.slippage_price,
                     commission_per_lot_side=a.commission_per_lot_side,
                     max_spread_price=a.max_spread_price,min_stop_distance_price=a.min_stop_price)
    strategy=NoTrades() if a.strategy=='none' else ClosedBarImpulseDemo()
    sim=Replay(cfg,strategy);quality=FeedQuality()
    for quote in read_ticks(a.input,a.broker,quality,dukas_scale=a.dukas_scale):sim.on_quote(quote)
    report=sim.snapshot()
    report['source']={'filename':a.input.name,'sha256':fingerprint,'allowlist_match':pin is not None,
                      'source_verified':pin is not None,
                      'dukas_price_divisor':a.dukas_scale if a.broker=='dukascopy' else None,
                      'quality':asdict(quality), 'month_end_open_positions_not_force_closed':True}
    report['strategy_id']=a.strategy
    ledger=a.output.with_name(a.output.stem+'_trades.csv')
    if not a.no_trade_ledger:
        if ledger.exists() and not a.force:raise SystemExit('trade ledger exists; use --force for a deliberate rerun')
        atomic_trades_csv(ledger,sim.trades)
        report['trade_ledger_file']=ledger.name
        report['trade_ledger_sha256']=sha256_file(ledger)
    atomic_json(a.output,report)
    print(json.dumps({'broker':a.broker,'quotes':quality.total,'trades':report['trades'],
                      'net':report['net_realized'],'checkpoint':str(a.output)},indent=2))

if __name__=='__main__':main()
