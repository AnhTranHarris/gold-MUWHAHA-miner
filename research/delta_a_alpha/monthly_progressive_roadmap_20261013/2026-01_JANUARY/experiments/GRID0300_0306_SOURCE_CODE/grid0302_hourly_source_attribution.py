"""GRID0302 independent original-tick *diagnostic* source attribution.
No trading decision uses ex-post worst hour; labels purely for research reporting.
"""
from __future__ import annotations
from pathlib import Path
import json,time
import numpy as np
from numba import njit
import grid0300_hourly_equity_governor as g
ROOT=Path(__file__).resolve().parent
modified=g.source.replace('    return r','    r["analysis_accepted_indices"]=idx.tolist()\n    return r')
assert modified!=g.source
ns=dict(g.ns)
exec(modified,ns)
select=ns['physical_replay']
@njit(cache=True)
def independent_equity_peaktrough(t,bid,ask,lc,sc,basis,cashdelta,cash,offset):
    hours=int(t[-1]//3600000)-offset+1
    max_dd=np.zeros(hours,np.float64);peak_idx=np.full(hours,-1,np.int64);peak_of_worst=np.full(hours,-1,np.int64);low_idx=np.full(hours,-1,np.int64)
    high=np.full(hours,-1e200,np.float64)
    lng=0;sho=0;cost=0.;booked=0.
    for i in range(len(t)):
        lng+=lc[i];sho+=sc[i];cost+=basis[i];booked+=cashdelta[i]
        h=int(t[i]//3600000)-offset
        eq=cash+booked+(lng*bid[i]-sho*ask[i])/1000.-cost-(lng+sho)*0.20
        if eq>high[h]:high[h]=eq;peak_idx[h]=i
        d=high[h]-eq
        if d>max_dd[h]:max_dd[h]=d;low_idx[h]=i;peak_of_worst[h]=peak_idx[h]
    return max_dd,peak_of_worst,low_idx

def run():
    t0=time.perf_counter();t,bid,ask,z,kind,owner,pgid,r9,origin=g.base.p.ancestor.base.materialize()
    cfg=dict(cash=100000.,cap=256,loss_pause_n=2,pause_ms=300000,native16_cap=2,earned_native_cap=32,
        earned_wins=7,earned_window=10,earned_edge=12,parent_cap=16,earned_parent_cap=192,parent_wins=4,parent_window=6,parent_edge=4,
        hourly_entry_lock_usd=0.,hourly_soft_parent_usd=400.,hourly_soft_parent_cap=64)
    r=select(t,bid,ask,z,kind,owner,pgid,r9,**cfg)
    idx=np.array(r.pop('analysis_accepted_indices'),np.int64);e=z['entry_idx'][idx];x=z['exit_idx'][idx]
    assert r['trades']==len(idx)
    n=len(t); dl=np.zeros(n,np.int32);ds=np.zeros(n,np.int32);db=np.zeros(n,np.float64);dc=np.zeros(n,np.float64)
    # Apply both CLOSE and ENTRY at identical observed quote index before snapshot.
    for j,k in enumerate(idx):
        side=int(z['direction'][k]);price=float(z['entry_price_raw'][k])/1000.;
        if side>0:dl[e[j]]+=1;dl[x[j]]-=1
        else:ds[e[j]]+=1;ds[x[j]]-=1
        db[e[j]]+=side*price;db[x[j]]-=side*price;dc[x[j]]+=float(z['net_cash'][k])
    offset=int(t[0]//3600000);dd,peak,low=independent_equity_peaktrough(t,bid,ask,dl,ds,db,dc,100000.,offset)
    active=np.flatnonzero(dd>0)
    worst=active[np.argsort(-dd[active])[:12]]
    def iso(ts):return str(np.datetime64(int(ts),'ms'))
    findings=[]
    for h in worst:
        endidx=int(low[h]);startidx=int(peak[h]); mask=(e<=endidx)&(x>endidx)
        sources={}
        positions=np.flatnonzero(mask)
        for j in positions:
            k=int(idx[j]);src=str(z['source'][k]);side=int(z['direction'][k]);mark=int(bid[endidx] if side>0 else ask[endidx]);px=float(z['entry_price_raw'][k]); pnl=(mark-px)*side/1000.-.2
            v=sources.setdefault(src,{'open':0,'mtm_pnl':0.,'longs':0,'shorts':0})
            v['open']+=1;v['mtm_pnl']+=pnl;v['longs']+=int(side>0);v['shorts']+=int(side<0)
        findings.append({'UTC_hour':iso((h+offset)*3600000),'hour_dd':float(dd[h]),'peak_utc':iso(t[startidx]),'trough_utc':iso(t[endidx]),'open_at_trough':int(len(positions)),
          'source_at_trough':sources})
    worst_day={}
    for h,v in enumerate(dd):
        day=iso((h+offset)*3600000)[:10]
        if day not in worst_day or v>worst_day[day]:worst_day[day]=float(v)
    result={'id':'GRID0302_INDEPENDENT_FULL_TICK_HOURLY_DRAWDOWN_SOURCE_ATTRIBUTION','status':'DIAGNOSTIC_ONLY_NOT_PROMOTED',
      'source_sha256':g.base.p.ancestor.base.back.SRC_SHA,'research_config':cfg,'net':r['net'],'trades':len(idx),
      'online_hourly_max':r['max_hourly_tick_equity_drawdown_usd'],'independently_rebuilt_hourly_max':float(np.max(dd)),
      'online_daily_worst_hourly':r['daily_worst_hourly_drawdown_usd'],'independent_daily_worst_hourly':worst_day,
      'worst_hours':findings,'seconds':time.perf_counter()-t0}
    path=ROOT/'grid0302_independent_hourly_source_attribution.json';path.write_text(json.dumps(result,indent=2))
    print('month net',r['net'],'N',len(idx),'onlineDD',r['max_hourly_tick_equity_drawdown_usd'],'independentDD',float(np.max(dd)),'sec',round(time.perf_counter()-t0,2),flush=True)
    for f in findings[:7]:print(f['UTC_hour'],round(f['hour_dd'],2),f['peak_utc'],f['trough_utc'],f['open_at_trough'],{k:(x['open'],round(x['mtm_pnl'],2)) for k,x in f['source_at_trough'].items()},flush=True)
    print('SAVED',path)
if __name__=='__main__':run()
