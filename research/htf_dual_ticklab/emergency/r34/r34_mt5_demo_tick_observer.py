#!/usr/bin/env python3
"""Windows Coinexx-DEMO native bid/ask tick observer; NEVER transmits an order.
Requires local Windows MetaTrader5 Python module and signed-in DEMO terminal.
This is a feed/forward telemetry collector ONLY, not whole-EA filtering.
"""
from __future__ import annotations
from datetime import datetime,timezone,timedelta
from pathlib import Path
from typing import Iterator
import argparse,hashlib,json,time

class DemoFeedError(RuntimeError):pass

class OrderedTickCollector:
    """Reconciliation-safe native (millisecond, within-ms occurrence) ticks.
    Replay inclusive last-millisecond entire API range every poll. Assumes
    MT5 preserves the order of previously returned same-ms ticks; otherwise stop.
    """
    def __init__(self):
        self.last_msc=-1
        self.last_same_ms=[]
        self.ordinal=-1
    def new_ticks(self, rows):
        # Returns (time_msc, locally observed ordinal, bid, ask, flags)
        at_prev=[]; earlier=[];out=[]; last_in_batch=(-1,-1)
        for row in rows:
            msc=int(row['time_msc']);bid=float(row['bid']);ask=float(row['ask']);flags=int(row['flags'])
            if not (msc>=0 and bid>0 and ask>=bid and ask-bid<100):
                raise DemoFeedError('invalid original tick bid-ask')
            identity=(msc,bid,ask,flags)
            if msc<self.last_msc:continue
            if msc==self.last_msc:at_prev.append(identity)
            else:earlier.append(identity)
            if msc < last_in_batch[0]:raise DemoFeedError('unordered provider ticks')
            last_in_batch=(msc,0)
        if self.last_msc>=0 and at_prev[:len(self.last_same_ms)]!=self.last_same_ms:
            raise DemoFeedError('MT5 provider revised same-ms quote history')
        delta=at_prev[len(self.last_same_ms):]+earlier
        # Preserve same-ms relative source order, ordinal is collector-local, NOT original historical ordinal.
        for msc,bid,ask,flags in delta:
            self.ordinal+=1
            if msc < self.last_msc:raise DemoFeedError('nonmonotonic UTC tick event')
            if msc==self.last_msc:self.last_same_ms.append((msc,bid,ask,flags))
            else:self.last_msc=msc;self.last_same_ms=[(msc,bid,ask,flags)]
            out.append({'time_msc':msc,'collector_ordinal':self.ordinal,
                        'bid':bid,'ask':ask,'flags':flags,'source':'MT5_COINEXX_DEMO_UTC'})
        return out

def collect(*,terminal_path:str|None,output:Path,server_substring='Coinexx',
            symbol='XAUUSD',poll_seconds=.25,max_polls:int=0):
    try:import MetaTrader5 as mt5
    except ImportError as e:raise DemoFeedError('Windows MetaTrader5 Python package is not installed') from e
    initialized=mt5.initialize(path=terminal_path) if terminal_path else mt5.initialize()
    if not initialized:raise DemoFeedError(f'MT5 initialize failed: {mt5.last_error()}')
    try:
        acc=mt5.account_info();terminal=mt5.terminal_info()
        if acc is None or terminal is None:raise DemoFeedError('missing signed-in MT5 account/terminal')
        if int(acc.trade_mode)!=int(mt5.ACCOUNT_TRADE_MODE_DEMO):
            raise DemoFeedError('REFUSE LIVE/CONTEST: observer requires DEMO account')
        if server_substring.lower() not in acc.server.lower():
            raise DemoFeedError('broker server string does not match configured Coinexx DEMO')
        si=mt5.symbol_info(symbol)
        if si is None:raise DemoFeedError('symbol absent')
        if not mt5.symbol_select(symbol,True):raise DemoFeedError('unable to subscribe to symbol')
        obs=OrderedTickCollector()
        output.parent.mkdir(parents=True,exist_ok=True)
        polls=0
        with output.open('w',encoding='utf-8') as f:
            f.write(json.dumps({'event':'HEADER','terminal_name':str(getattr(terminal,'name','')),
                    'server':acc.server,'account_mode':'DEMO','symbol':symbol,
                    'feed_clock':'MT5_NATIVE_UTC_TIME_MSC',
                    'source_quote_ordinals_are_collector_local':True,
                    'places_orders':False,'r24_model_scored':False})+'\n')
            while True:
                end=datetime.now(timezone.utc)
                begin=(datetime.fromtimestamp(obs.last_msc/1000,timezone.utc) if obs.last_msc>=0
                       else end-timedelta(seconds=5))
                rows=mt5.copy_ticks_range(symbol,begin,end,mt5.COPY_TICKS_INFO)
                if rows is None:raise DemoFeedError(f'copy_ticks_range failed: {mt5.last_error()}')
                for row in obs.new_ticks(rows):f.write(json.dumps(row,allow_nan=False)+'\n')
                f.flush();polls+=1
                if max_polls and polls>=max_polls:break
                time.sleep(poll_seconds)
        return {'output':str(output),'ticks':obs.ordinal+1,
                'sha256':hashlib.sha256(output.read_bytes()).hexdigest(),
                'demo_confirmed':True,'orders_sent':0}
    finally:mt5.shutdown()
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--terminal-path',default=None)
    p.add_argument('--out',required=True);p.add_argument('--server-contains',default='Coinexx')
    p.add_argument('--symbol',default='XAUUSD');p.add_argument('--poll',type=float,default=.25)
    p.add_argument('--max-polls',type=int,default=0)
    q=p.parse_args()
    if q.symbol!='XAUUSD':raise SystemExit('XAUUSD only')
    print(json.dumps(collect(terminal_path=q.terminal_path,output=Path(q.out),symbol=q.symbol,
          server_substring=q.server_contains,poll_seconds=q.poll,max_polls=q.max_polls),indent=2))
