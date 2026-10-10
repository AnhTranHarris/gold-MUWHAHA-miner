"""C2D3O resumable raw-tick source-native diagnostic funding, not MT5 certification.

Full ORIGINAL executable source authorities remain in verified_original_sources;
this script only composes already-source-parity-tested Python operators:
  JAN037 50ms L3 generator, JAN038 first-observed phase gate,
  JAN039 fixed source26/27 TP/caps, or FEB045 actual L3 quality+heat and FEB047
  physically funded profitable reduce queue, original completed STMR roles,
  existing single L7 portfolio. Fixed strategy mode is chosen *before* replay,
  never by inspecting a quote's month or future results. Rejected/shadow source
  events cannot open positions, earn watchdog/campaign credit or close profits.

Checkpoint is local trusted research data; NEVER deserialize an untrusted .pkl.
No March optimisation or owner approval is implied by this infrastructure.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime, timezone
from collections import defaultdict
import csv,gzip,hashlib,os,pickle,json,zlib,base64

from v1_funded_core_033c import Quote,Limits,FundedEngine
from original_50ms_funded_bridge_033 import OriginalJAN037L3QuoteBridge,OriginalSourceFeed033
from source_stmr_completed_ema_033 import SourceSTMRCompletedStack
from original_jan039_source_owner_adapter_033 import exact_jan039_l3_chain
from feb045_source_native_context_033 import FEB045NativeQualityL3
from feb045_physical_heat_feb047_queue_033 import (FEB045PhysicalHeatL3,
    PhysicalHeatConfig045,FEB047QueuedProfitReduceL7)

SCHEMA='DAA033-C2D3O-trusted-simulator-checkpoint-v1'
ALLOWED_MODES=frozenset(('JAN039_SOURCE_NATIVE','FEB045_SOURCE_NATIVE'))
PINNED_RUNTIME_FILES=('v1_funded_core_033c.py','original_jan037_heartbeat50_online_033.py',
    'source_jan038_feb042_online_033.py','source_stmr_completed_ema_033.py',
    'source_native_s26_s27_033.py','original_50ms_funded_bridge_033.py',
    'original_jan039_source_owner_adapter_033.py','feb045_source_native_context_033.py',
    'feb045_physical_heat_feb047_queue_033.py','original_monthblind_segmented_l7_replay_033.py')

def runtime_signature():
    base=Path(__file__).parent;h=hashlib.sha256()
    for name in PINNED_RUNTIME_FILES:
        f=base/name
        if not f.is_file():raise FileNotFoundError('Exact source engine missing: '+name)
        h.update(name.encode());h.update(bytes.fromhex(file_sha256(f)))
    return h.hexdigest()


def file_sha256(p):
    with open(p,'rb') as fh:return hashlib.file_digest(fh,'sha256').hexdigest()


@dataclass
class SegmentedRealQuoteResearch:
    """One deterministic source owner + one physically funded portfolio per run.

    Full proposed L1-L6 owner optimiser still incomplete; supported source is
    only the original JAN037 L3 family. Do not read frozen exit oracle tapes.
    """
    mode:str
    rules_sha256:str
    feed:OriginalSourceFeed033
    engine:FundedEngine
    verified_input_files:dict=field(default_factory=dict)
    read_rows:dict=field(default_factory=dict)
    total_quotes:int=0
    previous_input_name:str=''

    @classmethod
    def start(cls,mode:str,jan038_rules_path,*,funding:Limits|None=None):
        if mode not in ALLOWED_MODES:raise ValueError('Choose fixed original source family BEFORE any live quotes')
        rules=Path(jan038_rules_path)
        source=OriginalJAN037L3QuoteBridge(rules,apply_jan038=True,
                           label_family='JAN037' if mode=='JAN039_SOURCE_NATIVE' else 'F045')
        if mode=='JAN039_SOURCE_NATIVE':
            owners=[exact_jan039_l3_chain(source)]
        else:
            owners=[FEB045PhysicalHeatL3(FEB045NativeQualityL3(source),PhysicalHeatConfig045()),
                    FEB047QueuedProfitReduceL7()]
        limits=funding or Limits(balance_usd=100000.,max_orders_per_second=10,max_orders_per_tick=1)
        if limits.max_orders_per_tick!=1 or limits.max_orders_per_second>10:
            raise ValueError('The source-research L7 shares at most 1/tick and 10/second')
        # This is a quote-fill idealized diagnostic ONLY; flag does not verify Coinexx.
        simulated=FundedEngine(limits,owners,broker_contract_verified=True)
        feed=OriginalSourceFeed033(source,SourceSTMRCompletedStack())
        return cls(mode,file_sha256(rules),feed,simulated)

    def on_quote(self,t:int,ask_raw:int,bid_raw:int):
        q=Quote(int(t),int(ask_raw),int(bid_raw))
        s=self.feed.on_quote(q)
        self.engine.process_quote(q,s)
        self.total_quotes+=1

    def run_gzip_chunk(self,source_path, *,expected_sha256:str, max_new_quotes:int) -> int:
        """Read every original quote in order, including warmup and duplicate ms.

        Subsequent chunks safely skip previously read file rows; never count a
        skipped quote again. Format provenance + digests are input authority.
        """
        p=Path(source_path)
        if max_new_quotes<1:raise ValueError('Small bounded chunk required')
        if not (len(expected_sha256)==64 and all(c in '0123456789abcdef' for c in expected_sha256)):
            raise ValueError('Full verified original GZ SHA256 required')
        key=str(p.resolve())
        # Re-hash on EVERY entry to prevent an in-place file rewrite between
        # two separately resumed batches from silently changing the dataset.
        actual=file_sha256(p)
        if actual!=expected_sha256:
            raise ValueError('Original source GZ SHA256 mismatch')
        if key not in self.verified_input_files:
            self.verified_input_files[key]=actual
        elif self.verified_input_files[key]!=actual:
            raise ValueError('Cannot resume against altered source')
        done=self.read_rows.get(key,0)
        if self.previous_input_name and self.previous_input_name!=key and key in self.read_rows:
            raise ValueError('Cannot return to an already completed original input block')
        taken=0
        with gzip.open(p,'rt',newline='') as stream:
            rows=csv.DictReader(stream)
            need=('timestamp_ms_utc','ask_raw','bid_raw')
            if not all(x in (rows.fieldnames or []) for x in need):
                raise ValueError('Missing original raw executable BidAsk columns')
            for rowno,row in enumerate(rows):
                if rowno<done:continue
                self.on_quote(int(row['timestamp_ms_utc']),int(row['ask_raw']),int(row['bid_raw']))
                taken+=1
                if taken>=max_new_quotes:break
        self.read_rows[key]=done+taken
        self.previous_input_name=key
        return taken

    def funded_diagnostics(self)->dict:
        """Post-close evaluation buckets ONLY. None feeds back into decisions."""
        result={}
        by=defaultdict(lambda:dict(trades=0,realized_net=0.0))
        for x in self.engine.closed:
            when=datetime.fromtimestamp(x.time_ms/1000,timezone.utc)
            yearweek=when.isocalendar()
            parts={'daily':when.strftime('%Y-%m-%d'),
                   'weekly':f'{yearweek.year}-W{yearweek.week:02d}',
                   'monthly':when.strftime('%Y-%m')}
            for horizon,key in parts.items():
                k=(horizon,key)
                by[k]['trades']+=1
                by[k]['realized_net']+=x.net_usd
        for (h,key),data in sorted(by.items()):
            result.setdefault(h,{})[key]={'trades':data['trades'],'realized_net':round(data['realized_net'],5)}
        return {'mode':self.mode,'quotes_ingested':self.total_quotes,
            'original_source_offers':self.feed.bridge.source_events,
            'actually_paid_L3_entries':self.feed.bridge.physical_callbacks,
            'idealized_account_score':self.engine.score(),
            'realized_diagnostic_periods_only':result,
            'month_used_to_select_trades':False,'actual_broker_verified':False,
            'full_original_V1_economic_equivalence':False}

    def save_local_trusted_checkpoint(self,path):
        """Atomic local-only pickle + SHA integrity for own trusted research runs.
        This is not a safe general-purpose loader for externally supplied files.
        """
        dest=Path(path)
        dest.parent.mkdir(parents=True,exist_ok=True)
        data=zlib.compress(pickle.dumps(self,protocol=pickle.HIGHEST_PROTOCOL),level=6)
        obj={'schema':SCHEMA,'binary_sha256':hashlib.sha256(data).hexdigest(),
             'mode':self.mode,'source_rules_sha256':self.rules_sha256,
             'runtime_code_SHA256':runtime_signature(),
             'total_quotes':self.total_quotes,'payload_base85':base64.b85encode(data).decode('ascii')}
        tmp=dest.with_name(dest.name+'.part')
        with tmp.open('w') as fh:
            fh.write(json.dumps(obj,separators=(',',':'))+'\n')
            fh.flush();os.fsync(fh.fileno())
        os.replace(tmp,dest)

    @classmethod
    def resume_local_trusted_checkpoint(cls,path,*,expected_mode:str,source_rules_path):
        # Importing pickle is limited to this program's own previously created
        # local checkpoint. Never load user-uploaded / untrusted snapshots.
        obj=json.loads(Path(path).read_text())
        if obj.get('schema')!=SCHEMA or obj.get('mode')!=expected_mode:
            raise ValueError('Checkpoint schema/mode mismatch')
        if obj.get('source_rules_sha256')!=file_sha256(source_rules_path):
            raise ValueError('Original JAN038 source rules changed since checkpoint')
        if obj.get('runtime_code_SHA256')!=runtime_signature():
            raise ValueError('Runtime source files differ from trusted checkpoint')
        raw=base64.b85decode(obj['payload_base85'].encode('ascii'))
        if hashlib.sha256(raw).hexdigest()!=obj.get('binary_sha256'):
            raise ValueError('Checkpoint corrupt or incomplete')
        st=pickle.loads(zlib.decompress(raw))
        if not isinstance(st,cls) or st.mode!=expected_mode or st.total_quotes!=obj.get('total_quotes'):
            raise ValueError('Unexpected decoded quote-account state')
        return st
