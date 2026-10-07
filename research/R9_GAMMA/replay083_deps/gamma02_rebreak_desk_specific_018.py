import sys,json,numpy as np
sys.path.insert(0,'/mnt/data')
import gamma02_m1_density as gmd
import gamma02_ny_campaign_inventory_portfolio_001 as g
import gamma02_one_event_per_tick_audit_014 as base
import gamma02_rebreak_latency_017 as lat


def union_dedup(primary,extra): return lat.union_dedup(primary,extra)

def prep_all():
    t,a,b,mid,h4,h1,m15,m5,es,ee=gmd.prep()
    Plo=base.build_lo(t,a,b,mid,h4,h1,m15,m5); Pny=base.build_ny(t,a,b,mid,h4,h1,m15,m5)
    return (t,a,b,mid,h4,h1,m15,m5),Plo,Pny

def eval_config(data,Plo,Pny,lo_reset,lo_lat,ny_reset,ny_lat,cap):
    t,a,b,mid,h4,h1,m15,m5=data
    L=Plo if lo_reset<=0 else union_dedup(Plo,lat.rb_lo(t,a,b,mid,h4,h1,m15,m5,lo_reset,lo_lat))
    N=Pny if ny_reset<=0 else union_dedup(Pny,lat.rb_ny17(t,a,b,mid,h4,h1,m15,m5,ny_reset,ny_lat))
    arr=[np.concatenate((L[k],N[k])) for k in range(5)]; o=np.argsort(arr[0],kind='stable'); arr=[x[o] for x in arr]
    ae,ap,asrc,ar,sk,mo=g.cap_select(*arr,cap); r=g.summarize(ae,ap,asrc,ar,sk,mo)
    r.update(lo_reset_raw=lo_reset,lo_latency_ms=lo_lat,ny17_reset_raw=ny_reset,ny17_latency_ms=ny_lat,cap=cap,candidate_events=len(arr[0]))
    return r

def run(mode,cap,out,fix_lo_reset=100,fix_lo_lat=500,fix_ny_reset=100,fix_ny_lat=500):
    data,Plo,Pny=prep_all(); rows=[]
    if mode=='london':
        for rr in (50,100,150,200,300,500,750,1000):
            for ll in (0,250,500,1000,2000):
                rows.append(eval_config(data,Plo,Pny,rr,ll,fix_ny_reset,fix_ny_lat,cap))
    elif mode=='ny17':
        for rr in (50,100,150,200,300,500,750,1000,1500,2000):
            for ll in (0,250,500,1000,2000,3000,5000):
                rows.append(eval_config(data,Plo,Pny,fix_lo_reset,fix_lo_lat,rr,ll,cap))
    else: raise ValueError(mode)
    rows.sort(key=lambda x:x['net'],reverse=True)
    json.dump({'candidate':'GAMMA02_REBREAK_DESK_SPECIFIC_018','mode':mode,'cap':cap,'rows':rows},open(out,'w'),indent=2)
    for r in rows[:20]: print(json.dumps({k:r[k] for k in ['net','trades','pf','exp','balance_dd','lo_reset_raw','lo_latency_ms','ny17_reset_raw','ny17_latency_ms','sources']}),flush=True)

if __name__=='__main__':
 import argparse
 ap=argparse.ArgumentParser();ap.add_argument('--mode',choices=['london','ny17'],required=True);ap.add_argument('--cap',type=int,default=128);ap.add_argument('--out',required=True);ap.add_argument('--fix-lo-reset',type=int,default=100);ap.add_argument('--fix-lo-lat',type=int,default=500);ap.add_argument('--fix-ny-reset',type=int,default=100);ap.add_argument('--fix-ny-lat',type=int,default=500);z=ap.parse_args()
 run(z.mode,z.cap,z.out,z.fix_lo_reset,z.fix_lo_lat,z.fix_ny_reset,z.fix_ny_lat)