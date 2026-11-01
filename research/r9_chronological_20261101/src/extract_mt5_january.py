#!/usr/bin/env python3
"""Stream the MT5 Excel-2006 report without loading 1+ GB of worksheet XML."""
import argparse,csv,io,json,re,zipfile,xml.etree.ElementTree as ET
from pathlib import Path
S='{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'
C=re.compile(r'<c r="([A-Z]+)\d+"([^>]*)>(.*?)</c>', re.S)
V=re.compile(r'<v>(.*?)</v>',re.S)
ROW=re.compile(r'<row r="(\d+)"')

def extract(path, dest, prefix='2026.01.', n_preview=20):
    dest=Path(dest);dest.mkdir(parents=True,exist_ok=True)
    shared=[]
    with zipfile.ZipFile(path) as z:
        for _,e in ET.iterparse(z.open('xl/sharedStrings.xml'),events=('end',)):
            if e.tag==S+'si':shared.append(''.join(t.text or '' for t in e.iter(S+'t')));e.clear()
        orders=[];deals=[];section=None;sheet_counts={'orders_total':0,'deals_total':0}
        with z.open('xl/worksheets/sheet1.xml') as f:
            tf=io.TextIOWrapper(f,encoding='utf-16le',errors='replace',newline='')
            carry=''
            while True:
                x=tf.read(2000000)
                if not x:break
                chunks=(carry+x).split('</row>');carry=chunks.pop()
                for frag in chunks:
                    k=frag.rfind('<row r="')
                    if k<0:continue
                    row=frag[k:]+'</row>'
                    cells={}
                    for m in C.finditer(row):
                        cm=V.search(m.group(3))
                        if not cm:continue
                        raw=cm.group(1)
                        cells[m.group(1)]=shared[int(raw)] if 't="s"' in m.group(2) else raw
                    a=cells.get('A','')
                    if a=='Orders':section='orders';continue
                    if a=='Deals':section='deals';continue
                    if not a.startswith('2026.'):
                        continue
                    if section=='orders':
                        sheet_counts['orders_total']+=1
                        if a.startswith(prefix):orders.append({k:cells.get(k,'') for k in 'ABCDEFGHIJKLM'})
                    if section=='deals':
                        sheet_counts['deals_total']+=1
                        if a.startswith(prefix):deals.append({k:cells.get(k,'') for k in 'ABCDEFGHIJKLM'})
    for name,rows in [('orders',orders),('deals',deals)]:
        with (dest/f'january_{name}.csv').open('w',newline='') as f:
            out=csv.DictWriter(f,fieldnames=list('ABCDEFGHIJKLM'));out.writeheader();out.writerows(rows)
    stats={**sheet_counts,'january_orders':len(orders),'january_deals':len(deals),'first_orders':orders[:n_preview],'first_deals':deals[:n_preview]}
    (dest/'reference_extract.json').write_text(json.dumps(stats,indent=2))
    return stats

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('report');ap.add_argument('--out',default='results/coinexx_reference');a=ap.parse_args()
    r=extract(a.report,a.out)
    print(json.dumps({k:v for k,v in r.items() if not k.startswith('first')},indent=2))
    print('FIRST DEALS',json.dumps(r['first_deals'][:5],indent=2))
