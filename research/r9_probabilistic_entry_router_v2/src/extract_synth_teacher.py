#!/usr/bin/env python3
"""Extract R9 SYNTH entry/outcome minute/side teacher; read-only source.
Report is huge UTF-16LE XML; stream row chunks, never load full sheet. Signals
are privileged OFFLINE labels only, never inference input.  Only Jan Feb Jun Jul.
"""
import csv,gzip,io,zipfile,xml.etree.ElementTree as ET,re,collections,datetime as dt,json,sys
from pathlib import Path
S='{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'
C=re.compile(r'<c r="([A-Z]+)\d+"([^>]*)>(.*?)</c>', re.S)
V=re.compile(r'<v>(.*?)</v>',re.S)
MONTHS={'01','02','06','07'}
def parse(path,out):
  shared=[]
  counters=collections.Counter();records=collections.defaultdict(lambda:[0,0,0.])
  with zipfile.ZipFile(path) as z:
    for _,e in ET.iterparse(z.open('xl/sharedStrings.xml'),events=('end',)):
      if e.tag==S+'si':
        shared.append(''.join(t.text or '' for t in e.iter(S+'t')));e.clear()
    with z.open('xl/worksheets/sheet1.xml') as f:
      tf=io.TextIOWrapper(f,encoding='utf-16le',errors='replace',newline='');carry='';in_deals=False;pending={}
      while True:
        chunk=tf.read(2_000_000)
        if not chunk:break
        pieces=(carry+chunk).split('</row>');carry=pieces.pop()
        for frag in pieces:
          i=frag.rfind('<row r="')
          if i<0:continue
          row=frag[i:]+'</row>'
          cells={}
          for cm in C.finditer(row):
            vm=V.search(cm.group(3))
            if vm:
              raw=vm.group(1);cells[cm.group(1)]=shared[int(raw)] if 't="s"' in cm.group(2) else raw
          a=cells.get('A','')
          if a=='Deals':in_deals=True;continue
          if not in_deals or not a.startswith('2026.') or a[5:7] not in MONTHS:continue
          action=cells.get('D','').lower();inout=cells.get('E','').lower()
          if action not in ('buy','sell') or inout not in ('in','out'):continue
          if inout=='in':
            pending=(a,1 if action=='buy' else -1,float(cells.get('I') or 0))
          elif pending:
            ts,side,entry_fee=pending; pending=None
            net=entry_fee+float(cells.get('I') or 0)+float(cells.get('J') or 0)+float(cells.get('K') or 0)
            # Date format 2026.01.02 01:00:54 -- broker native clock.
            ym=ts[:16]
            v=records[(ym,side)];v[0 if net>0 else 1]+=1;v[2]+=net
            counters['trades']+=1;counters['positive' if net>0 else 'nonpositive']+=1
  out=Path(out);out.parent.mkdir(parents=True,exist_ok=True)
  with out.open('w',newline='') as f:
    w=csv.writer(f);w.writerow(['native_minute','side','positive','nonpositive','net'])
    for (minute,side),(p,n,net) in sorted(records.items()):w.writerow([minute,side,p,n,round(net,5)])
  summary={'trades':counters['trades'],'positive':counters['positive'],'nonpositive':counters['nonpositive'],'minutes_side':len(records),'target_months':sorted(MONTHS)}
  out.with_suffix('.json').write_text(json.dumps(summary,indent=2))
  return summary
if __name__=='__main__':print(json.dumps(parse(sys.argv[1],sys.argv[2]),indent=2))
