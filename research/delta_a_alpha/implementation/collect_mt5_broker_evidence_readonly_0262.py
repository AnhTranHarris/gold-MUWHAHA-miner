"""Read-only broker metadata collection for local Windows MT5 Python 3.11.

No order_send, no account mutation, no broker fee/session certification.
Intended ONLY for optional OWNER-side capture before any EA translation.
Never infers broker permission from Dukascopy UTC hours.
"""
from __future__ import annotations
import argparse,json
from datetime import datetime, timezone
from pathlib import Path

SYMBOL_FIELDS=(
 'name','digits','point','trade_tick_size','trade_tick_value',
 'trade_tick_value_profit','trade_tick_value_loss','trade_contract_size',
 'volume_min','volume_max','volume_step','volume_limit',
 'trade_stops_level','trade_freeze_level','trade_mode','trade_exemode',
 'filling_mode','order_mode','margin_initial','margin_maintenance',
 'swap_mode','swap_long','swap_short')
ACCOUNT_FIELDS=('currency','leverage','margin_mode')
TERMINAL_FIELDS=('build','connected','trade_allowed')

def fields(obj,names):
    return {name:getattr(obj,name,None) for name in names}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--symbol',default='XAUUSD')
    ap.add_argument('--output',default='mt5_xauusd_broker_metadata_readonly.json')
    args=ap.parse_args()
    import MetaTrader5 as mt5  # only import on user's local MT5 machine
    if not mt5.initialize():
        raise RuntimeError('Could not initialize existing MT5 terminal; no changes made')
    try:
        symbol=mt5.symbol_info(args.symbol)
        account=mt5.account_info()
        terminal=mt5.terminal_info()
        if symbol is None or account is None or terminal is None:
            raise RuntimeError('MT5 symbol/account/terminal metadata missing')
        record={
          'source':'READ_ONLY_LOCAL_MT5_SYMBOL_INFO',
          'observed_at_utc':datetime.now(timezone.utc).isoformat(),
          'requested_symbol':args.symbol,
          'symbol':fields(symbol,SYMBOL_FIELDS),
          'account_nonidentifying':fields(account,ACCOUNT_FIELDS),
          'terminal_nonidentifying':fields(terminal,TERMINAL_FIELDS),
          'fee_schedule_verified':False,
          'fill_latency_verified':False,
          'server_calendar_dst_2026_verified':False,
          'broker_execution_parity_certified':False,
          'note':'metadata only; no order placed; no account ID/password exported',
        }
        Path(args.output).write_text(json.dumps(record,indent=2,default=str)+'\n',encoding='utf-8')
        print('Wrote read-only metadata:',args.output)
    finally:
        mt5.shutdown()
if __name__=='__main__':main()
