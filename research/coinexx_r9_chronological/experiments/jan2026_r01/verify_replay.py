"""Source-exact January full replay parity and causality acceptance tests."""
import gzip
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from score_alignment import match_batch
import numpy as np
import pandas as pd

HERE=Path(__file__).parent
RAW=Path(os.environ.get('R9_REAL_TICKS','/mnt/data/XAUUSD_MT5_BROKER_2026_01_ticks_ALL.csv.gz'))
PIN='1307a75df5d635678de7691908600090a552f38543e0512187dcd7b37fbc66b8'
EXPECTED={'ticks':7699274,'same_ms':413,'entries':32179,'stop':31498,'timeout':681,
 'rearmed':31487,'trail_updates':39540,'gate_spread':967760,'gate_no_atr':9945,'gate_low_atr':7450,'gate_s1':2402389}

class SourceExactFullReplay(unittest.TestCase):
    def test_original_source_hash(self):
        h=hashlib.sha256()
        with RAW.open('rb') as source:
            while piece:=source.read(1024*1024):h.update(piece)
        self.assertEqual(h.hexdigest(),PIN)
    def test_january_full_replay_pinned_python_receipt(self):
        with tempfile.TemporaryDirectory(prefix='r9_replay_') as tmp:
            output=Path(tmp)/'trades.csv'
            r=subprocess.run([str(HERE/'r9_real_replay'),str(RAW),str(output)],capture_output=True,text=True,check=True,timeout=25)
            j=json.loads(r.stderr.strip().splitlines()[-1]);trades=pd.read_csv(output)
            for name,value in EXPECTED.items():self.assertEqual(j[name],value,name)
            self.assertEqual(len(trades),j['entries'])
            self.assertEqual(int(trades.net_quote_cents.sum()),j['net_quote_cents'])
            self.assertEqual(int((trades.net_quote_cents>0).sum()),j['positive'])
            self.assertEqual(int((trades.net_quote_cents<0).sum()),j['negative'])
            self.assertTrue((trades.exit_time_msc>=trades.entry_time_msc).all())
            self.assertTrue((trades.entry_ordinal.diff().dropna()>0).all())
            self.assertEqual(j['entries'],j['stop']+j['timeout'])
    def test_exact_one_to_one_alignment(self):
        # Two original references compete for ONE generated trade; only one can match.
        refs=(np.array([100,100],dtype=np.int64),np.array([110,110],dtype=np.int64),np.array([1,1],dtype=np.int8))
        got=(np.array([100],dtype=np.int64),np.array([110],dtype=np.int64),np.array([1],dtype=np.int8),np.array([30],dtype=np.int64))
        assert match_batch(refs,got,0,'joint')['matched']==1
        # Matching is direction-sensitive.
        other=(got[0],got[1],np.array([-1],dtype=np.int8),got[3])
        assert match_batch(refs,other,0,'joint')['matched']==0
    def test_future_suffix_cannot_mutate_past_entry_or_exit(self):
        with tempfile.TemporaryDirectory(prefix='r9_future_') as tmp:
            start=1767315620
            first=[(start+k, start*1000+k*1000,4000+k*.2,4000.02+k*.2) for k in range(25)]
            # Future ticks AFTER first source prefix are intentionally dissimilar.
            def write(name,tail_delta):
                p=Path(tmp)/name
                with gzip.open(p,'wt') as f:
                    f.write('time,time_msc,bid,ask,last,volume,volume_real,flags\n')
                    for s,ms,b,a in first:f.write(f'{s},{ms},{b:.2f},{a:.2f},0,1,0,0\n')
                    for k in range(25,40):
                        sec=start+k;b=4000+k*.2+tail_delta
                        f.write(f'{sec},{start*1000+k*1000},{b:.2f},{b+.02:.2f},0,1,0,0\n')
                return p
            outs=[]
            for i,delta in enumerate([0,20]):
                raw=write(f'fake{i}.csv.gz',delta);out=Path(tmp)/f'out{i}.csv'
                subprocess.run([str(HERE/'r9_real_replay'),str(raw),str(out),'--no_atr','--vel=2','--range=2','--minvel=0','--minrange=0','--eff=0','--stop=10','--hold=3','--no_trail'],capture_output=True,text=True,check=True,timeout=5)
                df=pd.read_csv(out)
                outs.append(df[df.exit_time_msc<(start+25)*1000].to_csv(index=False))
            self.assertEqual(outs[0],outs[1])
if __name__=='__main__':unittest.main(verbosity=2)
