# Assemble the complete single-file EA from the exact approved v3.00 source.
from pathlib import Path
import argparse,hashlib
p=argparse.ArgumentParser();p.add_argument('--base',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
b=a.base.read_bytes(); assert hashlib.sha256(b).hexdigest()=='4361dc87eff75c66c900530eba2bc1dc97efd6ba6a694d3d04dc185c6eaa96d3'
marker=b'// HG10 clean native terminal adapter.'
assert b.count(marker)==1
core=b[:b.index(marker)].replace(b'#property version "3.00"',b'#property version "3.10"',1).replace(b'#property description "HybridGate V1 standalone demo and Strategy Tester EA"',b'#property description "HybridGate v3.10 economic competence and capital protection (demo/tester)"',1)
out=core+Path(__file__).with_name('DemoController.mq5').read_bytes()
assert hashlib.sha256(out).hexdigest()=='555f78d2630da69147ccdde46b289145c108df9af92469784b426c39b7da22e3'
assert not a.out.exists();a.out.write_bytes(out)
