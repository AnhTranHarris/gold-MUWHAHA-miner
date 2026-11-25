"""Compare native calendar arrays and actual HG5Clock against frozen Python and sealed fixtures."""
import argparse, gzip, json, zipfile, hashlib, re, subprocess, sys
from pathlib import Path
from frozen_clock_policy import ClockConfig,calendar_windows,action
p=argparse.ArgumentParser();p.add_argument('--base',type=Path,required=True);p.add_argument('--include',type=Path,required=True);p.add_argument('--work',type=Path,required=True);a=p.parse_args();a.work.mkdir(parents=True,exist_ok=False)
assert hashlib.sha256(Path(__file__).with_name('frozen_clock_policy.py').read_bytes()).hexdigest()=='efa96c14259d4425675017e2e0808d10329cbbbab64cc890181e43e6e1d30984'
assert hashlib.file_digest(a.base.open('rb'),'sha256').hexdigest()=='076c12a01b7f17561438186521156f009aeff379306e6747e3343f61be2c1ec0'
with zipfile.ZipFile(a.base) as z:j=json.loads(gzip.decompress(z.read('fixtures/transitions.json.gz')))
source=(a.include/'HG6Calendar.mqh').read_text();rows=[];codes={'BLOCK':0,'TRADE':1,'FLATTEN':2,'DRAIN':3,'DRAIN_CANCEL_PENDING':4}
for mode in ('daily','weekly'):
 cfg=ClockConfig(mode=mode);ws=calendar_windows(cfg);expected=[(w.open_ms,w.block_ms,w.flatten_ms,w.close_ms) for w in ws];needle=re.search(r'HG6_'+mode.upper()+r'\[\]\[4\]=\{(.*?)\};',source,re.S);assert needle
 actual=[tuple(map(int,x)) for x in re.findall(r'\{(\d+),(\d+),(\d+),(\d+)\}',needle[1])];assert actual==expected==[tuple(x[k] for k in ('open_ms','block_ms','flatten_ms','close_ms')) for x in j['calendar'][mode]]
 for x in j['clock_actions']:
  if x['mode']!=mode:continue
  exp=action(x['now_ms'],x['position'],x['pending'],x['broker_open'],x['clock_valid'],ws,cfg,x['overdue']);assert exp==x['expected'];rows.append([int(mode=='weekly'),x['now_ms'],int(x['position']),int(x['pending']),int(x['broker_open']),int(x['clock_valid']),1,int(x['overdue']),codes[exp]])
(a.work/'clock.txt').write_text(''.join(' '.join(map(str,x))+'\n' for x in rows))
(a.work/'clock.cpp').write_text("#include \"host_compat.hpp\"\n#include \"HG6Calendar.mqh\"\nint main(){std::vector<HG5Window>d,w;assert(HG6Windows(false,0,d)&&HG6Windows(true,0,w));long t;int m,p,q,b,v,e,o,c,n=0;while(std::cin>>m>>t>>p>>q>>b>>v>>e>>o>>c){auto &x=m?w:d;assert(HG5Clock(t,p,q,b,v,e,o,x,(int)x.size())==c);n++;}std::cout<<n<<\" exact clock actions\\n\";}\n")
subprocess.run(['g++','-std=c++17','-O2','-I'+str(a.include),str(a.work/'clock.cpp'),'-lcrypto','-o',str(a.work/'clock')],check=True)
with (a.work/'clock.txt').open() as f:subprocess.run([str(a.work/'clock')],stdin=f,check=True)
print('PASS 753 daily / 157 weekly windows and original sealed actions')
