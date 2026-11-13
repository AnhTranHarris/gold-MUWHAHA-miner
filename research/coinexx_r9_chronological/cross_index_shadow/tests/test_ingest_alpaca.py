import csv,gzip,json,tempfile,unittest
from datetime import date
from pathlib import Path
from urllib.parse import parse_qs,urlparse
from ingest_alpaca import AlpacaHistoricalClient,fetch_partition,ingest,partitions

class TestPagedAlpacaIngest(unittest.TestCase):
    def test_monthly_bars_and_hourly_quotes_partitions(self):
        p=list(partitions(date(2026,1,31),date(2026,2,2),'bars'))
        self.assertEqual(len(p),2)
        self.assertEqual(p[0],('2026-01','2026-01-31T00:00:00Z','2026-02-01T00:00:00Z'))
        q=list(partitions(date(2026,1,31),date(2026,2,2),'quotes'))
        self.assertEqual(len(q),9)
    def test_paginate_duplicate_time_keep_both(self):
        calls=[]
        def fake(url,headers):
            params=parse_qs(urlparse(url).query);token=params.get('page_token',[None])[0]
            calls.append(token)
            a={'t':'2026-01-15T15:00:00.001Z','bp':100,'ap':100.01,'bs':100,'as':100,'c':['R']}
            b={'t':'2026-01-15T15:00:00.001Z','bp':100.01,'ap':100.02,'bs':100,'as':120,'c':['R']}
            if token is None:return {'quotes':{'QQQ':[a]},'next_page_token':'page2'}
            return {'quotes':{'QQQ':[b]},'next_page_token':None}
        cli=AlpacaHistoricalClient(api_key='TEST',api_secret='TEST',sleep_between_sec=0,http_get=fake)
        with tempfile.TemporaryDirectory() as tmp:
            r=fetch_partition(cli,mode='quotes',symbol='QQQ',part='2026-01-15_15',
                     start='2026-01-15T15:00:00Z',end='2026-01-15T16:00:00Z',out_dir=Path(tmp))
            self.assertEqual(r['rows'],2);self.assertEqual(r['pages'],2)
            self.assertTrue(r['complete_pagination'])
            with gzip.open(Path(tmp)/r['relative_path'],'rt') as f:
                rr=list(csv.DictReader(f))
            self.assertEqual(rr[0]['t'],rr[1]['t'])
            self.assertEqual(rr[1]['source_ordinal'],'1')
            self.assertEqual(calls,[None,'page2'])
    def test_page_loop_aborts_without_committing(self):
        def fake(url,headers):
            a={'t':'2026-01-15T15:00:01Z','bp':100,'ap':101,'bs':1,'as':1}
            return {'quotes':{'QQQ':[a]},'next_page_token':'same'}
        cli=AlpacaHistoricalClient(api_key='TEST',api_secret='TEST',sleep_between_sec=0,http_get=fake)
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(RuntimeError,'repeated page'):
                fetch_partition(cli,mode='quotes',symbol='QQQ',part='2026-01-15_15',
                     start='2026-01-15T15:00:00Z',end='2026-01-15T16:00:00Z',out_dir=Path(tmp))
            self.assertFalse(list(Path(tmp).rglob('*.gz')))
    def test_end_inclusive_provider_boundary_deduplicated(self):
        def fake(url,headers):
            def q(t):return {'t':t,'bp':100,'ap':100.01,'bs':100,'as':100}
            return {'quotes':{'QQQ':[q('2026-01-15T15:59:59.999999999Z'),
                                      q('2026-01-15T16:00:00Z')]},'next_page_token':None}
        cli=AlpacaHistoricalClient(api_key='TEST',api_secret='TEST',sleep_between_sec=0,http_get=fake)
        with tempfile.TemporaryDirectory() as tmp:
            r=fetch_partition(cli,mode='quotes',symbol='QQQ',part='2026-01-15_15',
                              start='2026-01-15T15:00:00Z',end='2026-01-15T16:00:00Z',out_dir=Path(tmp))
            self.assertEqual(r['rows'],1)
            self.assertEqual(r['last_timestamp'],'2026-01-15T15:59:59.999999999Z')
    def test_changed_partition_scope_fails(self):
        calls=[0]
        def fake(url,headers):
            calls[0]+=1
            return {'bars':{'QQQ':[]},'next_page_token':None}
        cli=AlpacaHistoricalClient(api_key='TEST',api_secret='TEST',sleep_between_sec=0,http_get=fake)
        with tempfile.TemporaryDirectory() as tmp:
            dst=Path(tmp)
            ingest(cli,start=date(2026,1,15),end=date(2026,1,15),mode='bars',out_dir=dst,symbols=['QQQ'])
            with self.assertRaisesRegex(RuntimeError,'scope changed'):
                ingest(cli,start=date(2026,1,1),end=date(2026,1,31),mode='bars',out_dir=dst,symbols=['QQQ'])

    def test_resume_sha_verification_no_requery(self):
        calls=[0]
        def fake(url,headers):
            calls[0]+=1
            return {'bars':{'QQQ':[{'t':'2026-01-15T15:00:00Z','o':1,'h':1,'l':1,'c':1,'v':100}]},'next_page_token':None}
        cli=AlpacaHistoricalClient(api_key='TEST',api_secret='TEST',sleep_between_sec=0,http_get=fake)
        with tempfile.TemporaryDirectory() as tmp:
            dst=Path(tmp)
            self.assertEqual(ingest(cli,start=date(2026,1,15),end=date(2026,1,15),mode='bars',out_dir=dst,symbols=['QQQ']),1)
            self.assertEqual(ingest(cli,start=date(2026,1,15),end=date(2026,1,15),mode='bars',out_dir=dst,symbols=['QQQ']),0)
            self.assertEqual(calls[0],1)
            p=next((dst/'bars'/'QQQ').glob('*.gz'))
            p.write_bytes(b'CORRUPTED')
            with self.assertRaisesRegex(RuntimeError,'mismatch'):
                ingest(cli,start=date(2026,1,15),end=date(2026,1,15),mode='bars',out_dir=dst,symbols=['QQQ'])

if __name__=='__main__':unittest.main()
