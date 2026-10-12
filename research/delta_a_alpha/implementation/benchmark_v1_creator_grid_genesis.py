"""Original Dukascopy tick replay, GRID GENESIS ONLY (ZERO funded trades).

The R9 original tester-clock daily date is not yet confirmed equal to raw
Dukascopy UTC day; this scoreboard compares VOLUMES BY DAY LABEL AS A
DIAGNOSTIC, NOT an aligned execution/financial acceptance test.
"""
import csv,gzip,sys,collections,json,statistics,hashlib,time
from datetime import datetime,timezone,time as dtime
from zoneinfo import ZoneInfo
from pathlib import Path
from v1_creator_grid_genesis import CreatorGridGenesis, GenesisSettings

HOUR=3_600_000
class Q:
    __slots__=('time_ms_utc','ask_raw','bid_raw')
    def __init__(self,ms,ask,bid):self.time_ms_utc=ms;self.ask_raw=ask;self.bid_raw=bid
class B:
    __slots__=('start_ms','end_ms','open_raw','high_raw','low_raw','close_raw')
    def __init__(self,s,v):self.start_ms=s;self.end_ms=s+HOUR;self.open_raw=v;self.high_raw=v;self.low_raw=v;self.close_raw=v
    def update(self,v):self.high_raw=max(self.high_raw,v);self.low_raw=min(self.low_raw,v);self.close_raw=v

ZONES={'SYDNEY':ZoneInfo('Australia/Sydney'),'TOKYO':ZoneInfo('Asia/Tokyo'),'LONDON':ZoneInfo('Europe/London'),'NEW_YORK':ZoneInfo('America/New_York')}
def geometry(ms):
    utc=datetime.fromtimestamp(ms/1000,timezone.utc)
    opens=[]
    for desk,z in ZONES.items():
        local=utc.astimezone(z)
        hour=local.hour
        if local.weekday()<5 and ((desk=='SYDNEY' and 8<=hour<17) or (desk=='TOKYO' and 9<=hour<18) or (desk=='LONDON' and 8<=hour<17) or (desk=='NEW_YORK' and 8<=hour<17)):
            opens.append(desk)
    if 'LONDON' in opens and 'NEW_YORK' in opens:return 'LONDON_NEW_YORK_OVERLAP'
    if 'SYDNEY' in opens and 'TOKYO' in opens:return 'SYDNEY_TOKYO_OVERLAP'
    if 'LONDON' in opens:return 'LONDON'
    if 'NEW_YORK' in opens:return 'NEW_YORK'
    if 'SYDNEY' in opens or 'TOKYO' in opens:return 'ASIA_PACIFIC'
    return 'TRANSITION_OR_CLOSED'

def bench(path,settings,limit_ticks=0):
    t0=time.monotonic()
    g=CreatorGridGenesis(settings)
    hour=None;current=None;last_closed=None;geo=None
    m5key=None;m5current=None;m5closed=None
    days=collections.Counter();sides=collections.Counter();sessions=collections.Counter();hours=collections.Counter();rungs=collections.Counter();spread=[]
    accepted=0;raw=0
    with gzip.open(path,'rt',newline='') as f:
        rd=csv.reader(f);header=next(rd)
        assert header[:3]==['timestamp_ms_utc','ask_raw','bid_raw'],header
        for v in rd:
            ms=int(v[0]);ask=int(v[1]);bid=int(v[2]);raw+=1
            if limit_ticks and raw>limit_ticks: break
            k=ms//HOUR
            if k!=hour:
                if current is not None:last_closed=current
                hour=k;current=B(hour*HOUR,bid);geo=geometry(ms)
            else:
                current.update(bid)
            mk=ms//300_000
            if mk!=m5key:
                if m5current is not None:m5closed=m5current
                m5key=mk;m5current=B(mk*300_000,bid)
                m5current.end_ms=m5current.start_ms+300_000
            else:
                m5current.update(bid)
            if raw%200==0:spread.append((ask-bid)/1000)
            if geo=='TRANSITION_OR_CLOSED':
                # Preserve transitions for prior tick but no physical opportunities.
                g.on_tick(Q(ms,ask,bid),last_closed,geo,last_completed_m5=m5closed,broker_tradable=False)
                continue
            ev=g.on_tick(Q(ms,ask,bid),last_closed,geo,last_completed_m5=m5closed,broker_tradable=True)
            if not ev:continue
            d=datetime.fromtimestamp(ms/1000,timezone.utc).date().isoformat()
            h=datetime.fromtimestamp(ms/1000,timezone.utc).strftime('%Y-%m-%dT%H')
            for x in ev:
                days[d]+=1;hours[h]+=1;sides['BUY' if x.side==1 else 'SELL']+=1
                sessions[geo]+=1;rungs[x.rung]+=1
                accepted+=1
    return {'month':path.name,'source_ticks':raw,'virtual_creator_events':accepted,'parent_events':g.parent_events,'child_events':g.m5_child_events,
            'daily_counts_UTC':dict(days),'hourly_counts_UTC':dict(hours),'sides':dict(sides),
            'sessions':dict(sessions),'rungs':dict(rungs),'spread_median_diagnostic':statistics.median(spread),
            'max_daily_events':max(days.values(),default=0),'elapsed_s':round(time.monotonic()-t0,2),
            'settings':vars(settings)}

if __name__=='__main__':
    month=sys.argv[1] if len(sys.argv)>1 else '01'
    settings=GenesisSettings()
    p=Path(f'/mnt/data/XAUUSD_DUKAS_2026_{month}_ticks.csv(3).gz')
    if month=='07':p=Path('/mnt/data/XAUUSD_DUKAS_2026_07_ticks.csv(2).gz')
    print('replaying '+p.name+'...',file=sys.stderr,flush=True)
    z=bench(p,settings,limit_ticks=int(sys.argv[2]) if len(sys.argv)>2 else 0)
    out=Path(__file__).parent/f'GRID0221_{month}_GENESIS_VS_R9_UTC_DIAGNOSTIC.json'
    r9={}
    with open('/mnt/data/grid0186_work/R9_SYNTH_REPORT_CLOCK_DAILY.csv') as f:
        for row in csv.DictReader(f):r9[row['tester_clock_bucket']]=int(row['completed_positions'])
    paired=[]
    for d,n in sorted(z['daily_counts_UTC'].items()):
        b=r9.get(d)
        paired.append({'UTC_date':d,'creator_raw_virtual_events':n,'R9_SYNTH_mt5_SERVER_clock_completed':b,
                       'raw_event_to_R9_exit_count_ratio_UNALIGNED':round(n/b,4) if b else None})
    z['R9_unverified_clock_daily_count_diagnostic']=paired
    z['WARNING']='Only raw virtual crossing events. Zero funded trades. R9 MT5 server-day vs Dukascopy UTC-day clock bridge NOT verified.'
    out.write_text(json.dumps(z,indent=2))
    csvpath=out.with_suffix('.csv')
    with csvpath.open('w',newline='') as f:
        keys=list(paired[0]) if paired else ['UTC_date','creator_virtual_qualified','R9_SYNTH_mt5_SERVER_clock_completed']
        w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows(paired)
    print(json.dumps({k:v for k,v in z.items() if k not in ('hourly_counts_UTC','daily_counts_UTC','rungs','R9_unverified_clock_daily_count_diagnostic')},indent=2),flush=True)
    print('paired days:',len(paired),'sum first 10',paired[:10],flush=True)
