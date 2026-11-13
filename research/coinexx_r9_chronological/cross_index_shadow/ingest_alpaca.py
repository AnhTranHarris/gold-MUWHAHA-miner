"""Private, resumable Alpaca historical ETF data ingestion for R9 research.

Modes: `bars` (1-minute source bars, cheap screening), `quotes` (all native
IEX quote events in selected UTC-hour partitions). Both follow *all* Alpaca
page_token pages; nothing is silently sampled or backfilled. Raw market data
must remain private. API keys are read only from environment variables.

Important: A bar timestamp denotes BAR OPEN, and a bar is NOT usable for
R9 decisions until its close and a source-publication safety delay. Quote
source timestamps are also NOT measured cross-provider delivery timestamps.
No trading, API order placement, AUC fitting, or private data upload occurs.
"""
from __future__ import annotations
import argparse,csv,gzip,hashlib,json,os,random,re,time,urllib.error,urllib.parse,urllib.request
from calendar import monthrange
from datetime import date,datetime,timedelta,timezone
from pathlib import Path
from typing import Callable

SYMBOLS=('QQQ','SPY','DIA','EWJ','FEZ','VGK')
BASE='https://data.alpaca.markets/v2/stocks'
HEADERS={
  'quote':('t','bp','ap','bs','as','bx','ax','z','c'),
  'bar':('t','o','h','l','c','v','n','vw')
}


def _utc(value: date, hour:int=0) -> str:
    return f'{value.isoformat()}T{hour:02d}:00:00Z'


def _month_end(value: date) -> date:
    return date(value.year,value.month,monthrange(value.year,value.month)[1])


def _next_month(value:date) -> date:
    return _month_end(value)+timedelta(days=1)


def partitions(start:date,end:date,mode:str,*,utc_first_hour:int=13,utc_last_hour:int=22):
    if end<start:raise ValueError('end before start')
    if mode=='bars':
        d=start
        while d<=end:
            nxt=min(_month_end(d),end)
            yield (d.isoformat()[:7],_utc(d),_utc(nxt+timedelta(days=1)))
            d=nxt+timedelta(days=1)
    elif mode=='quotes':
        if not 0 <= utc_first_hour < utc_last_hour <= 24:
            raise ValueError('bad UTC hour bounds')
        d=start
        while d<=end:
            if d.weekday()<5:  # market holidays still recorded as zero-data partitions
                for h in range(utc_first_hour,utc_last_hour):
                    a=f'{d.isoformat()}T{h:02d}:00:00Z'
                    b=f'{d.isoformat()}T{h+1:02d}:00:00Z'
                    yield (f'{d.isoformat()}_{h:02d}',a,b)
            d+=timedelta(days=1)
    else:raise ValueError('unknown mode')


class AlpacaHistoricalClient:
    def __init__(self, *, api_key:str, api_secret:str, sleep_between_sec:float=0.35,
                 http_get:Callable|None=None):
        if not api_key or not api_secret:raise ValueError('missing Alpaca data credentials')
        self.headers={'APCA-API-KEY-ID':api_key,'APCA-API-SECRET-KEY':api_secret,
                      'Accept':'application/json'}
        self.sleep_between_sec=sleep_between_sec
        self.http_get=http_get

    def get_page(self,mode,symbol,start,end,page_token=None,limit=10000):
        if symbol not in SYMBOLS:raise ValueError('unsupported ETF symbol')
        if mode not in ('quotes','bars'):raise ValueError('unsupported mode')
        params={'symbols':symbol,'feed':'iex','start':start,'end':end,'sort':'asc','limit':limit}
        if mode=='bars':params['timeframe']='1Min'
        if page_token is not None:params['page_token']=page_token
        url=BASE+('/quotes' if mode=='quotes' else '/bars')+'?'+urllib.parse.urlencode(params)
        if self.http_get is not None:
            return self.http_get(url,self.headers)
        for attempt in range(7):
            if self.sleep_between_sec:time.sleep(self.sleep_between_sec)
            req=urllib.request.Request(url,headers=self.headers)
            try:
                with urllib.request.urlopen(req,timeout=35) as response:
                    return json.loads(response.read())
            except urllib.error.HTTPError as error:
                if error.code not in (429,500,502,503,504) or attempt>=6:
                    raise RuntimeError(f'Alpaca data response HTTP {error.code}; check source access') from error
                delay=min(35,2**attempt+random.random())
                time.sleep(delay)
            except (TimeoutError,ConnectionError) as error:
                if attempt>=6:raise
                time.sleep(min(35,2**attempt))
        raise RuntimeError('exhausted retries')


def _utc_nanos(stamp: str) -> int:
    """Exact provider timestamp ordering, including sub-microsecond revisions."""
    m=re.fullmatch(r'(\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d)(?:\.(\d{1,9}))?Z',stamp)
    if not m:raise ValueError('expected RFC3339 UTC with <=9 fractional digits')
    whole=datetime.fromisoformat(m.group(1)).replace(tzinfo=timezone.utc)
    return int(whole.timestamp())*1000000000 + int((m.group(2) or '').ljust(9,'0') or '0')


def _hash_file(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for piece in iter(lambda:f.read(1024*1024),b''):h.update(piece)
    return h.hexdigest()


def _record_path(out_dir:Path,mode:str,symbol:str,part:str) -> Path:
    return out_dir/mode/symbol/f'{part}_{symbol}_{mode}_iex.csv.gz'


def fetch_partition(client:AlpacaHistoricalClient,*,mode:str,symbol:str,part:str,
                    start:str,end:str,out_dir:Path,max_pages:int=20000) -> dict:
    """Commit one complete partition atomically; fail if paging incomplete."""
    kind='quote' if mode=='quotes' else 'bar'
    keys=HEADERS[kind]
    dst=_record_path(out_dir,mode,symbol,part)
    dst.parent.mkdir(parents=True,exist_ok=True)
    tmp=dst.with_suffix('.partial.gz')
    n=pages=0
    last_timestamp=None
    last_timestamp_ns=None
    first_timestamp=None
    start_ns=_utc_nanos(start)
    end_ns=_utc_nanos(end)
    seen_pages=set()
    token=None
    try:
        with gzip.open(tmp,'wt',encoding='utf-8',newline='') as f:
            w=csv.writer(f)
            w.writerow(['source_ordinal']+list(keys))
            while True:
                if pages>=max_pages:raise RuntimeError('partition exceeds page budget; no partial outputs accepted')
                payload=client.get_page(mode,symbol,start,end,page_token=token)
                if not isinstance(payload,dict):raise RuntimeError('invalid Alpaca response schema')
                rows=payload.get('quotes' if kind=='quote' else 'bars',{}).get(symbol,[])
                if not isinstance(rows,list):raise RuntimeError('invalid symbol records')
                pages+=1
                for row in rows:
                    ts=row.get('t')
                    if not isinstance(ts,str):
                        raise RuntimeError('missing event timestamp')
                    ts_ns=_utc_nanos(ts)
                    if last_timestamp_ns is not None and ts_ns < last_timestamp_ns:
                        raise RuntimeError('source time inversion')
                    if ts_ns < start_ns or ts_ns > end_ns:
                        raise RuntimeError('provider response contains out-of-partition event')
                    # Alpaca's end parameter is inclusive. The next partition
                    # owns exactly its own opening timestamp; skip this tie.
                    if ts_ns == end_ns:
                        continue
                    last_timestamp_ns=ts_ns
                    if first_timestamp is None:first_timestamp=ts
                    last_timestamp=ts
                    w.writerow([n]+[json.dumps(row.get(k),separators=(',',':')) if isinstance(row.get(k),(list,dict))
                                    else row.get(k) for k in keys])
                    n+=1
                nxt=payload.get('next_page_token')
                if not nxt:break
                if nxt in seen_pages:raise RuntimeError('repeated page token: cannot certify source completeness')
                if not rows:raise RuntimeError('empty page with pending token')
                seen_pages.add(nxt)
                token=nxt
        os.replace(tmp,dst)
    finally:
        if tmp.exists():tmp.unlink()
    return {'provider':'Alpaca','feed':'iex','mode':mode,'symbol':symbol,'partition':part,
            'start':start,'end_exclusive':end,'rows':n,'pages':pages,
            'first_timestamp':first_timestamp,'last_timestamp':last_timestamp,
            'sha256':_hash_file(dst),'relative_path':str(dst.relative_to(out_dir)),
            'complete_pagination':True}


def ingest(client:AlpacaHistoricalClient,*,start:date,end:date,mode:str,out_dir:Path,
           symbols=SYMBOLS,limit_partitions:int|None=None):
    out_dir.mkdir(parents=True,exist_ok=True)
    manifest=out_dir/f'{mode}_source_manifest.jsonl'
    prior={}
    if manifest.is_file():
        for line in manifest.read_text().splitlines():
            if line.strip():
                item=json.loads(line);prior[(item['symbol'],item['partition'])]=item
    completed=0
    for part,a,b in partitions(start,end,mode):
        for symbol in symbols:
            if symbol not in SYMBOLS:raise ValueError('unknown symbol')
            key=(symbol,part)
            previous=prior.get(key)
            if previous:
                if previous['start'] != a or previous['end_exclusive'] != b or previous['mode'] != mode:
                    raise RuntimeError(f'partition scope changed: {symbol} {part}; do not accept partial prior source')
                fp=out_dir/previous['relative_path']
                if fp.is_file() and _hash_file(fp)==previous['sha256']:
                    continue
                raise RuntimeError(f'archive/manifest mismatch: {fp}; do not overwrite automatically')
            if limit_partitions is not None and completed>=limit_partitions:
                return completed
            receipt=fetch_partition(client,mode=mode,symbol=symbol,part=part,
                                    start=a,end=b,out_dir=out_dir)
            with manifest.open('a',encoding='utf-8') as f:
                f.write(json.dumps(receipt,separators=(',',':'))+'\n')
                f.flush();os.fsync(f.fileno())
            completed+=1
            print(f'{symbol} {part}: {receipt["rows"]:,} {mode} events / {receipt["pages"]} pages',flush=True)
    return completed


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--mode',choices=['bars','quotes'],default='bars')
    ap.add_argument('--start',type=date.fromisoformat,default=date(2026,1,1))
    ap.add_argument('--end',type=date.fromisoformat,default=date(2026,9,30))
    ap.add_argument('--symbols',nargs='+',choices=SYMBOLS,default=list(SYMBOLS))
    ap.add_argument('--out-dir',type=Path,default=Path.home()/'r9_alpaca_private_data')
    ap.add_argument('--limit-partitions',type=int,default=None)
    args=ap.parse_args()
    api_key=os.environ.get('APCA_API_KEY_ID') or os.environ.get('ALPACA_API_KEY')
    api_secret=os.environ.get('APCA_API_SECRET_KEY') or os.environ.get('ALPACA_SECRET_KEY')
    if not api_key or not api_secret:
        ap.error('set APCA_API_KEY_ID and APCA_API_SECRET_KEY in local secure environment; never commit secrets')
    completed=ingest(AlpacaHistoricalClient(api_key=api_key,api_secret=api_secret),
                     start=args.start,end=args.end,mode=args.mode,out_dir=args.out_dir,
                     symbols=args.symbols,limit_partitions=args.limit_partitions)
    print(f'complete new source partitions={completed}',flush=True)

if __name__=='__main__':main()
