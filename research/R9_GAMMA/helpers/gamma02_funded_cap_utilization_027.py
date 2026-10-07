import sys,json,numpy as np
from datetime import datetime, timezone
sys.path.insert(0,'/mnt/data')
import gamma02_m1_density as gmd
import gamma02_intrinsic_cusum_pulse_024 as ip
import gamma02_ny_campaign_inventory_portfolio_001 as g

def funded_utilization(A,base_cap=64,step_slots=64,profit_unit=2500.,max_cap=256):
    ev_times,exit_t,pnl,reason,source=A
    active=np.zeros(max_cap,np.uint8);aend=np.zeros(max_cap,np.int64);apnl=np.zeros(max_cap,np.float64)
    accepted_exit=[];accepted_pnl=[];accepted_src=[];accepted_reason=[]
    realized=0.;skips=0;maxopen=0;transitions=[];stats={};samples={}
    prev_allowed=None;prev_time=None
    for k in range(ev_times.size):
        now=int(ev_times[k]);open_n=0
        for z in range(max_cap):
            if active[z]:
                if int(aend[z])<=now:
                    realized+=float(apnl[z]);active[z]=0
                else:open_n+=1
        fund=max(0.,realized)
        allowed=base_cap+int(fund//profit_unit)*step_slots
        allowed=min(max_cap,max(base_cap,allowed))
        if allowed not in stats:
            stats[allowed]=dict(candidate_events=0,accepted=0,skipped=0,calendar_ms=0,sum_open=0.,sum_util=0.,max_open=0,first_ms=now,last_ms=now)
            samples[allowed]=[]
        if prev_time is not None:stats[prev_allowed]['calendar_ms']+=max(0,now-prev_time)
        if prev_allowed is None or allowed!=prev_allowed:
            transitions.append(dict(candidate_index=int(k),time_ms=now,time_utc=datetime.fromtimestamp(now/1000,tz=timezone.utc).isoformat(),
                                    from_cap=None if prev_allowed is None else int(prev_allowed),to_cap=int(allowed),
                                    realized_profit=round(realized,2),funding_value=round(fund,2),open_positions=int(open_n)))
        st=stats[allowed];st['candidate_events']+=1;st['sum_open']+=open_n
        u=open_n/allowed;st['sum_util']+=u;st['max_open']=max(st['max_open'],open_n);st['last_ms']=now;samples[allowed].append(u)
        if open_n>=allowed:
            skips+=1;st['skipped']+=1
        else:
            q=-1
            for z in range(max_cap):
                if not active[z]:q=z;break
            if q<0:
                skips+=1;st['skipped']+=1
            else:
                active[q]=1;aend[q]=int(exit_t[k]);apnl[q]=float(pnl[k])
                accepted_exit.append(int(exit_t[k]));accepted_pnl.append(float(pnl[k]))
                accepted_src.append(int(source[k]));accepted_reason.append(int(reason[k]))
                st['accepted']+=1;maxopen=max(maxopen,open_n+1)
        prev_allowed=allowed;prev_time=now
    x=np.asarray(accepted_exit,np.int64);p=np.asarray(accepted_pnl,np.float64);s=np.asarray(accepted_src,np.int16);r=np.asarray(accepted_reason,np.int8)
    econ=g.summarize(x,p,s,r,skips,maxopen)
    total_span=sum(v['calendar_ms'] for v in stats.values())
    outstats={}
    for cap,st in sorted(stats.items()):
        n=st['candidate_events'];arr=np.asarray(samples[cap],np.float64)
        outstats[str(cap)]=dict(
            candidate_events=int(n),candidate_share=float(n/ev_times.size),accepted=int(st['accepted']),skipped=int(st['skipped']),
            skip_rate=float(st['skipped']/n if n else 0),calendar_ms=int(st['calendar_ms']),calendar_hours=float(st['calendar_ms']/3600000),
            calendar_share=float(st['calendar_ms']/total_span if total_span else 0),mean_open_before_entry=float(st['sum_open']/n if n else 0),
            mean_utilization=float(st['sum_util']/n if n else 0),p50_utilization=float(np.quantile(arr,.5)),p90_utilization=float(np.quantile(arr,.9)),
            p99_utilization=float(np.quantile(arr,.99)),max_open_before_entry=int(st['max_open']),
            first_utc=datetime.fromtimestamp(st['first_ms']/1000,tz=timezone.utc).isoformat(),
            last_utc=datetime.fromtimestamp(st['last_ms']/1000,tz=timezone.utc).isoformat())
    return dict(candidate='GAMMA02_FUNDED_CAP_UTILIZATION_027',
                config=dict(base_cap=base_cap,step_slots=step_slots,profit_unit=profit_unit,max_cap=max_cap,mode='cumulative'),
                economics=econ,candidate_events=int(ev_times.size),transitions=transitions,cap_stats=outstats,
                total_transitions=len(transitions),cap_levels_seen=sorted([int(k) for k in stats]))

if __name__=='__main__':
    import argparse
    ap=argparse.ArgumentParser();ap.add_argument('--out',required=True);z=ap.parse_args()
    t,a,b,mid,h4,h1,m15,m5,es,ee=gmd.prep();A=ip.heartbeat_frontier((t,a,b,mid,h4,h1,m15,m5))
    obj=funded_utilization(A)
    with open(z.out,'w') as f:json.dump(obj,f,indent=2)
    print(json.dumps(dict(economics={k:obj['economics'][k] for k in ['net','trades','pf','exp','balance_dd','maxopen','skips']},
                          transitions=obj['transitions'],cap_stats=obj['cap_stats']),indent=2))
