import json,numpy as np
from numba import njit
import gamma02_m1_density as gmd
import gamma02_intrinsic_cusum_pulse_024 as ip
import gamma02_campaign_heartbeat_019 as hb
import gamma02_rebreak_latency_017 as lat
import gamma02_ny_campaign_inventory_portfolio_001 as g

@njit(cache=True)
def select_funded_surge(et,xt,pnl,source,base_cap,base_step,base_unit,base_max,initial_surge,surge_step,surge_unit,max_surge,hard_max):
    active=np.zeros(hard_max,np.uint8);aend=np.zeros(hard_max,np.int64);apnl=np.zeros(hard_max,np.float64)
    ox=np.empty(et.size,np.int64);op=np.empty(et.size,np.float64);os=np.empty(et.size,np.int16);orr=np.empty(et.size,np.int8)
    accepted=0;skips=0;maxopen=0;realized=0.;max_allowed=base_cap;max_surge_seen=initial_surge
    unlock_t=np.full(32,np.int64(-1));unlock_cap=np.zeros(32,np.int32);nu=0;last_allowed=-1
    for k in range(et.size):
        now=et[k];open_n=0
        for z in range(hard_max):
            if active[z]:
                if aend[z]<=now:
                    realized+=apnl[z];active[z]=0
                else:open_n+=1
        base_allowed=base_cap+int(max(0.,realized)//base_unit)*base_step
        if base_allowed>base_max:base_allowed=base_max
        if base_allowed<base_cap:base_allowed=base_cap
        surge=initial_surge+int(max(0.,realized)//surge_unit)*surge_step
        if surge>max_surge:surge=max_surge
        if surge<0:surge=0
        allowed=base_allowed+surge
        if allowed>hard_max:allowed=hard_max
        if allowed!=last_allowed and nu<32:
            unlock_t[nu]=now;unlock_cap[nu]=allowed;nu+=1;last_allowed=allowed
        if allowed>max_allowed:max_allowed=allowed
        if surge>max_surge_seen:max_surge_seen=surge
        if open_n>=allowed:
            skips+=1;continue
        q=-1
        for z in range(hard_max):
            if not active[z]:q=z;break
        if q<0:
            skips+=1;continue
        active[q]=1;aend[q]=xt[k];apnl[q]=pnl[k]
        ox[accepted]=xt[k];op[accepted]=pnl[k];os[accepted]=source[k];orr[accepted]=0;accepted+=1
        if open_n+1>maxopen:maxopen=open_n+1
    return ox[:accepted],op[:accepted],os[:accepted],orr[:accepted],skips,maxopen,max_allowed,max_surge_seen,unlock_t[:nu],unlock_cap[:nu]

def build(ms=120):
    D=gmd.prep();data=D[:8];base=ip.heartbeat_frontier(data);m=np.isin(base[4],[16,17]);A=tuple(x[m] for x in base)
    A=lat.union_dedup(A,hb.heartbeat_events(data,ms,2));A=lat.union_dedup(A,hb.heartbeat_events(data,ms,1));m=np.isin(A[4],[16,17]);return D,tuple(x[m] for x in A)

def run():
    D,A=build(120);hard=2304;max_surge=2048
    cfgs=[]
    for init in (0,256,512,1024):
      for step,unit in ((256,1000.),(256,2500.),(256,5000.),(512,2500.)):
        cfgs.append((init,step,unit))
    rows=[]
    # warm
    select_funded_surge(A[0],A[1],A[2],A[4],64,64,2500.,256,*cfgs[0],max_surge,hard)
    for init,step,unit in cfgs:
      x,p,s,r,sk,mo,ma,msu,ut,uc=select_funded_surge(A[0],A[1],A[2],A[4],64,64,2500.,256,init,step,unit,max_surge,hard)
      o=g.summarize(x,p,s,r,sk,mo);o.update(initial_surge=init,surge_step=step,surge_profit_unit=unit,max_surge=max_surge,hard_cap=hard,max_allowed=int(ma),max_surge_seen=int(msu),candidate_events=len(A[0]),unlock_times_ms=[int(v) for v in ut],unlock_caps=[int(v) for v in uc]);rows.append(o)
      print(json.dumps({k:o[k] for k in ['initial_surge','surge_step','surge_profit_unit','net','trades','pf','exp','win','balance_dd','maxopen','skips','max_allowed']}),flush=True)
      json.dump({'candidate':'GAMMA02_PROFIT_FUNDED_SURGE_049','rows':rows},open('/mnt/data/gamma02_profit_funded_surge_049.partial.json','w'),indent=2)
    rows.sort(key=lambda q:q['net'],reverse=True)
    obj={'candidate':'GAMMA02_PROFIT_FUNDED_SURGE_049','rows':rows};json.dump(obj,open('/mnt/data/gamma02_profit_funded_surge_049.json','w'),indent=2)
if __name__=='__main__':run()