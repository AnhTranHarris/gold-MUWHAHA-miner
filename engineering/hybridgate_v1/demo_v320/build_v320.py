"""Reassemble exact v3.20 from the native-working v3.00 standalone source. No datasets or retraining."""
import argparse, hashlib
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--baseline',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
def sha(b):return hashlib.sha256(b).hexdigest()
b=a.baseline.read_bytes();assert sha(b)=='4361dc87eff75c66c900530eba2bc1dc97efd6ba6a694d3d04dc185c6eaa96d3'
controller=Path(__file__).with_name('DemoController.mq5').read_bytes();assert sha(controller)=='4d982e1e9e641dba5128d3637f550f8c4e9d4886ef320b0ec9478cf865bde55c'
marker=b'// HG10 clean native terminal adapter.';prefix=b[:b.index(marker)];needle=b' int ActualState()const{return actual_state;}'
assert prefix.count(needle)==1
prefix=prefix.replace(needle,b' // HG12 economic observations: exact original causal features and RX01 heads, read-only.\n bool EconomicCandles(float &c[],float &raw[])const{return valid&&started&&candles.Snapshot(1,c,raw);}\n bool EconomicPriors(int side,float &duration,float &value)const{if(!valid||!started||n<2)return false;float c[],raw[],rx[];float h4=0;if(!candles.Snapshot(side,c,raw)||!HG5RXFeatures(q,n,n-1,side,n-2,base,rx))return false;return HG5HoldingPriors(hold,rx,c,h4,value,duration);}\n'+needle,1).replace(b'#property version "3.00"',b'#property version "3.20"',1).replace(b'#property description "HybridGate V1 standalone demo and Strategy Tester EA"',b'#property description "HybridGate 3.20 causal forward-outcome intelligence and risk"',1)
result=prefix+controller;assert sha(result)=='f478df7b14317d421dbb7304edc5a45e29f6e8984ce8a9dba48d4d45cd4eeae2';assert len(result)==94145266
assert not a.out.exists(),'refuse to overwrite existing file';a.out.write_bytes(result);print(sha(result),len(result))
