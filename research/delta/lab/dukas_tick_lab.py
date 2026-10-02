from __future__ import annotations
import argparse, hashlib, json, time
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence
import numpy as np
import pandas as pd
from numba import njit

LAB_VERSION="delta-dukas-lab-v1"; PRICE_SCALE=1000
MONTHS={
1:("XAUUSD_DUKAS_2026_01_ticks.csv.gz",68690420,"d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5",9135062,4292059,1526214),
2:("XAUUSD_DUKAS_2026_02_ticks.csv.gz",59425317,"ed3b3545c990c88d78519594c17c8915b0f679adcb0a94920ba7524f1f6d5c5d",7538339,3587940,1360472),
3:("XAUUSD_DUKAS_2026_03_ticks.csv.gz",73441502,"814ba35e72f219a58badd806ed5c0f30ef0fb4ffe56a48205d873706513bd177",9433179,4524761,1612599),
4:("XAUUSD_DUKAS_2026_04_ticks.csv.gz",55259580,"30375098f62aed6cabc32ec6b67c57c20baec9b6d9be1ce0a204e09806c1ec0f",7470570,3897851,1493754),
5:("XAUUSD_DUKAS_2026_05_ticks.csv.gz",60157474,"3a50e0f1eba3076154238290ec02842cf3744ab192e5c9a2acc1cc07367c6a0d",8333165,4094677,1517044),
6:("XAUUSD_DUKAS_2026_06_ticks.csv.gz",60563202,"34686ce53ba992dfb83ea35d555b6a4947a9216635853857c8bf11ce70c00ae2",8201406,4206410,1593269),
7:("XAUUSD_DUKAS_2026_07_ticks.csv.gz",53057690,"e171e8c2fb59f3f4147a6f845eb68e664fa9c0f4815caa33acdbb42cc2f768b7",7415841,4093693,1593188)}
TF={"250ms":250,"1s":1000,"5s":5000,"15s":15000,"30s":30000,"45s":45000,"M1":60000,"M2":120000,"M3":180000,"M4":240000,"M5":300000,"M6":360000,"M10":600000,"M12":720000,"M15":900000,"M20":1200000,"M30":1800000,"H1":3600000,"H2":7200000,"H3":10800000,"H4":14400000,"H6":21600000,"H8":28800000,"H12":43200000,"D1":86400000}

def sha(path:Path):
 h=hashlib.sha256()
 with path.open("rb") as f:
  for b in iter(lambda:f.read(8<<20),b""): h.update(b)
 return h.hexdigest()

def spec(m):
 f,n,h,t,b250,b1=MONTHS[m]; return {"filename":f,"bytes":n,"sha256":h,"ticks":t,"bars_250ms":b250,"bars_1s":b1}

def resolve(src:Path,m:int):
 s=spec(m); p=src/s["filename"]
 if p.exists(): return p
 for q in sorted(src.glob(f"XAUUSD_DUKAS_2026_{m:02d}_ticks.csv*.gz")):
  if q.stat().st_size==s["bytes"] and sha(q)==s["sha256"]: return q
 raise FileNotFoundError(f"canonical month {m:02d} not found under {src}")

def paths(root:Path,m:int):
 d=root/f"2026_{m:02d}"; return d,d/"t_ms.npy",d/"ask_raw.npy",d/"bid_raw.npy",d/"ask_vol.npy",d/"bid_vol.npy",d/"meta.json"

def verify(src:Path,m:int):
 p=resolve(src,m); s=spec(m); dig=sha(p); return {"month":m,"path":str(p),"size_bytes":p.stat().st_size,"sha256":dig,"ok":p.stat().st_size==s["bytes"] and dig==s["sha256"]}

def compile_month(src:Path,root:Path,m:int,vol=False,force=False,chunks=1_000_000):
 p=resolve(src,m); s=spec(m); v=verify(src,m)
 if not v["ok"]: raise RuntimeError(v)
 d,tp,ap,bp,avp,bvp,mp=paths(root,m); d.mkdir(parents=True,exist_ok=True)
 if mp.exists() and not force:
  meta=json.loads(mp.read_text())
  if meta.get("source_sha256")==s["sha256"] and meta.get("row_count")==s["ticks"]: return meta
 n=s["ticks"]; t=np.lib.format.open_memmap(tp,"w+",dtype="i8",shape=(n,)); a=np.lib.format.open_memmap(ap,"w+",dtype="i4",shape=(n,)); b=np.lib.format.open_memmap(bp,"w+",dtype="i4",shape=(n,))
 av=np.lib.format.open_memmap(avp,"w+",dtype="f4",shape=(n,)) if vol else None; bv=np.lib.format.open_memmap(bvp,"w+",dtype="f4",shape=(n,)) if vol else None
 use=["timestamp_ms_utc","ask_raw","bid_raw"]+(["ask_volume","bid_volume"] if vol else []); dt={"timestamp_ms_utc":"i8","ask_raw":"i4","bid_raw":"i4","ask_volume":"f4","bid_volume":"f4"}
 pos=0; prev=None; mono=True; ageb=True; same=0; mins=2**31-1; maxs=-1; t0=time.perf_counter()
 for df in pd.read_csv(p,compression="gzip",usecols=use,dtype=dt,chunksize=chunks):
  x=df.timestamp_ms_utc.to_numpy(False); aa=df.ask_raw.to_numpy(False); bb=df.bid_raw.to_numpy(False); k=len(df)
  if pos+k>n: raise RuntimeError("row overflow")
  if prev is not None and x[0]<prev: mono=False
  if k>1:
   z=np.diff(x); mono=mono and not np.any(z<0); same+=int(np.count_nonzero(z==0))
  ageb=ageb and not np.any(aa<bb); sp=aa.astype("i8")-bb.astype("i8"); mins=min(mins,int(sp.min())); maxs=max(maxs,int(sp.max()))
  t[pos:pos+k]=x; a[pos:pos+k]=aa; b[pos:pos+k]=bb
  if vol: av[pos:pos+k]=df.ask_volume.to_numpy(False); bv[pos:pos+k]=df.bid_volume.to_numpy(False)
  prev=int(x[-1]); pos+=k
 if pos!=n: raise RuntimeError(f"row mismatch {pos}!={n}")
 for x in (t,a,b,av,bv):
  if x is not None: x.flush()
 meta={"lab_version":LAB_VERSION,"month":m,"source_file":p.name,"source_sha256":s["sha256"],"source_size_bytes":s["bytes"],"row_count":n,"price_scale":PRICE_SCALE,"first_timestamp_ms":int(t[0]),"last_timestamp_ms":int(t[-1]),"first_ask_raw":int(a[0]),"first_bid_raw":int(b[0]),"last_ask_raw":int(a[-1]),"last_bid_raw":int(b[-1]),"timestamps_monotonic_non_decreasing":bool(mono),"ask_ge_bid":bool(ageb),"same_ms_adjacent_pairs":same,"min_spread_raw":mins,"max_spread_raw":maxs,"with_volume":vol,"compile_seconds":time.perf_counter()-t0,"core_cache_bytes":tp.stat().st_size+ap.stat().st_size+bp.stat().st_size}
 mp.write_text(json.dumps(meta,indent=2)+"\n"); return meta

def load(root:Path,m:int):
 d,tp,ap,bp,_,_,mp=paths(root,m); return json.loads(mp.read_text()),np.load(tp,mmap_mode="r"),np.load(ap,mmap_mode="r"),np.load(bp,mmap_mode="r")

@njit(cache=True)
def count_bars(t,d):
 if t.size==0:return 0
 n=1; q=t[0]//d
 for i in range(1,t.size):
  z=t[i]//d
  if z!=q:n+=1;q=z
 return n

@njit(cache=True)
def bars(t,a,b,d):
 n=count_bars(t,d); st=np.empty(n,"i8"); en=np.empty(n,"i8"); fi=np.empty(n,"i8"); li=np.empty(n,"i8"); ct=np.empty(n,"i4"); ao=np.empty(n,"i4"); ah=np.empty(n,"i4"); al=np.empty(n,"i4"); ac=np.empty(n,"i4"); bo=np.empty(n,"i4"); bh=np.empty(n,"i4"); bl=np.empty(n,"i4"); bc=np.empty(n,"i4")
 k=-1;q=-1
 for i in range(t.size):
  z=t[i]//d
  if z!=q:
   k+=1;q=z;st[k]=z*d;en[k]=(z+1)*d;fi[k]=li[k]=i;ct[k]=1;ao[k]=ah[k]=al[k]=ac[k]=a[i];bo[k]=bh[k]=bl[k]=bc[k]=b[i]
  else:
   li[k]=i;ct[k]+=1;ah[k]=max(ah[k],a[i]);al[k]=min(al[k],a[i]);ac[k]=a[i];bh[k]=max(bh[k],b[i]);bl[k]=min(bl[k],b[i]);bc[k]=b[i]
 return st,en,fi,li,ct,ao,ah,al,ac,bo,bh,bl,bc

def save_bars(root:Path,m:int,tf:str,force=False):
 if tf not in TF: raise KeyError(tf)
 _,t,a,b=load(root,m); out=paths(root,m)[0]/f"bars_{tf}.npz"
 if out.exists() and not force:
  z=np.load(out); return {"month":m,"timeframe":tf,"bars":int(z["start_ms"].size),"path":str(out)}
 vals=bars(t,a,b,TF[tf]); keys=("start_ms","end_ms","first_idx","last_idx","tick_count","ask_open","ask_high","ask_low","ask_close","bid_open","bid_high","bid_low","bid_close"); np.savez(out,**dict(zip(keys,vals))); return {"month":m,"timeframe":tf,"bars":len(vals[0]),"path":str(out),"bytes":out.stat().st_size}

@dataclass(frozen=True)
class BrokerConfig:
 price_scale:int=PRICE_SCALE; contract_size_oz_per_lot:float=100.; lot:float=.01; commission_roundtrip_usd:float=0.; slippage_raw:int=0; latency_ms:int=0
 @property
 def usd_per_raw(self): return self.contract_size_oz_per_lot*self.lot/self.price_scale

@njit(cache=True)
def roundtrip(side,ea,eb,xa,xb,slip,usd_per_raw,fee):
 return ((xb-slip)-(ea+slip))*usd_per_raw-fee if side>0 else ((eb-slip)-(xa+slip))*usd_per_raw-fee

@njit(cache=True)
def protective(side,bid,ask,sl,tp,slip):
 if side>0:
  if sl>0 and bid<=sl:return 1,bid-slip
  if tp>0 and bid>=tp:return 2,bid-slip
 else:
  if sl>0 and ask>=sl:return 1,ask+slip
  if tp>0 and ask<=tp:return 2,ask+slip
 return 0,0

@njit(cache=True)
def mtm(side,entry,bid,ask,usd): return (bid-entry)*usd if side>0 else ((entry-ask)*usd if side<0 else 0.)

@njit(cache=True)
def noop(t,a,b):
 s=np.int64(0);c=np.int64(0)
 for i in range(t.size):s+=np.int64(a[i])-np.int64(b[i]);c^=np.int64(t[i])^(np.int64(a[i])<<1)^(np.int64(b[i])<<2)
 return s,c

def benchmark(root:Path,m:int):
 _,t,a,b=load(root,m);noop(t[:8],a[:8],b[:8]);z=time.perf_counter();s,c=noop(t,a,b);sec=time.perf_counter()-z;return {"month":m,"ticks":len(t),"seconds":sec,"million_ticks_per_sec":len(t)/sec/1e6,"spread_sum_raw":int(s),"checksum":int(c)}

def qa(root:Path,m:int):
 meta,t,a,b=load(root,m);s=spec(m); ck={"row_count":len(t)==s["ticks"],"monotonic":bool(np.all(t[1:]>=t[:-1])),"ask_ge_bid":bool(np.all(a>=b)),"bars_250ms_count":count_bars(t,250)==s["bars_250ms"],"bars_1s_count":count_bars(t,1000)==s["bars_1s"]}
 ft=np.array([999,1000,1000,1999,2000],"i8");fa=np.array([10,11,12,13,14],"i4");fb=fa-1;x=bars(ft,fa,fb,1000);ck["right_edge_fixture"]=bool(np.array_equal(x[0],np.array([0,1000,2000])) and np.array_equal(x[4],np.array([1,3,1])));ck["same_ms_fixture"]=bool(x[2][1]==1 and x[3][1]==3);cfg=BrokerConfig();ck["buy_ask_exit_bid"]=abs(roundtrip(1,100100,100000,100200,100100,0,cfg.usd_per_raw,0))<1e-12;ck["sell_bid_exit_ask"]=abs(roundtrip(-1,100100,100000,100000,99900,0,cfg.usd_per_raw,0))<1e-12;return {"month":m,"checks":ck,"pass":all(ck.values())}

def main(argv:Sequence[str]|None=None):
 p=argparse.ArgumentParser();sub=p.add_subparsers(dest="cmd",required=True)
 for n in ("verify","compile","qa","benchmark"):
  q=sub.add_parser(n);q.add_argument("--month",type=int,choices=range(1,8),required=True)
  if n in ("verify","compile"):q.add_argument("--source-dir",type=Path,required=True)
  if n in ("compile","qa","benchmark"):q.add_argument("--cache-root",type=Path,required=True)
  if n=="compile":q.add_argument("--with-volume",action="store_true");q.add_argument("--force",action="store_true")
 q=sub.add_parser("bars");q.add_argument("--month",type=int,choices=range(1,8),required=True);q.add_argument("--cache-root",type=Path,required=True);q.add_argument("--timeframe",choices=TF,required=True);q.add_argument("--force",action="store_true")
 sub.add_parser("catalog");a=p.parse_args(argv)
 if a.cmd=="catalog":print(json.dumps({"version":LAB_VERSION,"price_scale":PRICE_SCALE,"months":{m:spec(m) for m in MONTHS},"timeframes_ms":TF},indent=2))
 elif a.cmd=="verify":print(json.dumps(verify(a.source_dir,a.month),indent=2))
 elif a.cmd=="compile":print(json.dumps(compile_month(a.source_dir,a.cache_root,a.month,a.with_volume,a.force),indent=2))
 elif a.cmd=="qa":print(json.dumps(qa(a.cache_root,a.month),indent=2))
 elif a.cmd=="benchmark":print(json.dumps(benchmark(a.cache_root,a.month),indent=2))
 elif a.cmd=="bars":print(json.dumps(save_bars(a.cache_root,a.month,a.timeframe,a.force),indent=2))
 return 0
if __name__=="__main__":raise SystemExit(main())
