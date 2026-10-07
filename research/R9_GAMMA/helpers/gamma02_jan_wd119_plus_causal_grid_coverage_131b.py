import numpy as np, heapq, json, hashlib
from datetime import datetime, timezone
from pathlib import Path
import gamma02_jan_watchdog119_grid_layer_refinement_131a as wd131a
import gamma02_campaign_heartbeat_019 as hb
import gamma02_m1_density as gmd
import gamma02_funded_cap_equity_dd_028 as eq

OUT='/mnt/data/jan_wd119_plus_coverage_v3_131b.json'
MARKET=Path('/mnt/data/XAUUSD_DUKAS_2026_01_ticks.csv(3).gz')

def sha256_file(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for chunk in iter(lambda:f.read(8*1024*1024),b''): h.update(chunk)
    return h.hexdigest()

def cap_select_arrays(C, capn):
    et,xt,p,r,s=C; heap=[]; sel=[]; seq=0; sk=0; mo=0
    for k in range(len(et)):
        now=int(et[k])
        while heap and heap[0][0] <= now: heapq.heappop(heap)
        if len(heap) >= capn:
            sk += 1; continue
        sel.append(k); heapq.heappush(heap,(int(xt[k]),seq)); seq += 1; mo=max(mo,len(heap))
    return np.asarray(sel,np.int64),sk,mo

def summary(t, ex, X, P, H=None):
    o=np.argsort(X,kind='stable'); bal=peak=dd=gp=gl=0.; wk={}; days={}
    for k in o:
        v=float(P[k]); bal += v; peak=max(peak,bal); dd=max(dd,peak-bal); gp += max(v,0); gl += min(v,0)
        dt=datetime.fromtimestamp(int(t[int(X[k])])/1000,tz=timezone.utc)
        y,w,_=dt.isocalendar(); key=f'{y}-W{w:02d}'
        q=wk.setdefault(key,{'net':0.,'gp':0.,'gl':0.,'trades':0})
        q['net']+=v; q['gp']+=max(v,0); q['gl']+=min(v,0); q['trades']+=1
        dkey=dt.date().isoformat(); qd=days.setdefault(dkey,{'net':0.,'gp':0.,'gl':0.,'trades':0})
        qd['net']+=v; qd['gp']+=max(v,0); qd['gl']+=min(v,0); qd['trades']+=1
    for d in (wk,days):
        for q in d.values(): q['pf']=q['gp']/-q['gl'] if q['gl']<0 else 999.
    out={'net':float(P.sum()),'trades':int(len(P)),'gp':float(gp),'gl':float(gl),
         'pf':float(gp/-gl if gl<0 else 999.),'win':float(np.mean(P>0)) if len(P) else 0.,
         'expectancy':float(np.mean(P)) if len(P) else 0.,'balance_dd':float(dd),
         'equity_dd':float(ex[4]),'min_total_equity':float(100000+ex[5]),'maxopen_exact':int(ex[9]),
         'equity_dd_peak_time_utc':eq.iso(t,ex[7]),'equity_dd_trough_time_utc':eq.iso(t,ex[8]),
         'weeks':wk,'days':days}
    if H is not None and len(H): out['avg_hold_s']=float(np.mean(H))
    return out

def main():
    D=wd131a.wd.prep_month(1); t,a,b,mid,h4,h1,m15,m5=D[:8]; gmd.prep=lambda:D
    holder={}; orig=wd131a.cap.one
    def wrap(Q,capn):
        r,B=orig(Q,capn); holder['B']=B; return r,B
    wd131a.cap.one=wrap
    wr=wd131a.build([1190,1190,1190,1190,1190,1100],703)
    wd131a.cap.one=orig
    WE,WX,WR,WD,WP,WH,WS=holder['B']

    E=hb.heartbeat_events(D[:8],250,0); et,xt,pnl,reason,src=E
    idx=np.searchsorted(t,et); b10=((et//60000)%60)//10; j60=np.searchsorted(t,et-60000,side='left'); ticks60=idx-j60+1
    k=np.zeros(len(et),bool)
    k |= (src==9)&(b10==0)&(h4[idx]==1)&(h1[idx]==1)&(m15[idx]==1)&(m5[idx]==-1)
    k |= (src==11)&np.isin(b10,[2,3])&(h4[idx]==1)&(h1[idx]==1)&(m15[idx]==-1)&(m5[idx]==-1)
    k |= (src==11)&(b10==3)&(h4[idx]==1)&(h1[idx]==1)&(m15[idx]==1)&(m5[idx]==-1)
    k |= (src==12)&np.isin(b10,[0,1,2])&(h4[idx]==1)&(h1[idx]==1)&(m15[idx]==-1)&(m5[idx]==-1)
    k |= (src==12)&(b10==4)&(h4[idx]==1)&(h1[idx]==1)&(m15[idx]==1)&(m5[idx]==-1)&(ticks60<=210)
    k |= (src==13)&np.isin(b10,[2,3])&(h4[idx]==1)&(h1[idx]==1)&(m15[idx]==-1)&(m5[idx]==-1)
    k |= (src==14)&(b10==3)&(h4[idx]==1)&(h1[idx]==1)&(m15[idx]==-1)&(m5[idx]==1)
    k |= (src==15)&np.isin(b10,[2,3])&(h4[idx]==1)&(h1[idx]==1)&(m15[idx]==1)&(m5[idx]==1)
    A=tuple(x[k] for x in E)

    E16=hb.heartbeat_events(D[:8],250,2); e16,x16,p16,r16,s16=E16
    i16=np.searchsorted(t,e16); b16=((e16//60000)%60)//10
    k16=(s16==16)&(h4[i16]==1)&(h1[i16]==1)&(m15[i16]==1)&(m5[i16]==-1)&np.isin(b16,[0,3,4])
    B=tuple(x[k16] for x in E16)

    C=[np.concatenate([A[i],B[i]]) for i in range(5)]; o=np.argsort(C[0],kind='stable'); C=tuple(x[o] for x in C)
    sel,sk,cov_mo=cap_select_arrays(C,512)
    et,xt,pnl,reason,src=[x[sel] for x in C]
    SE=np.searchsorted(t,et).astype(np.int64); SX=np.searchsorted(t,xt).astype(np.int64)
    SD=np.ones(len(SE),np.int8); SR=a[SE].astype(np.int64)
    re=((b[SX].astype(np.int64)-SR)/1000.-0.02)
    err=float(np.max(np.abs(re-pnl))) if len(pnl) else 0.; assert err < 1e-9, err
    sex=eq.exact_equity_sweep(t,a,b,SE,SX,SR,SD,pnl)

    srcout={}
    for z in np.unique(src):
        p=pnl[src==z]; gp=float(p[p>0].sum()); gl=float(p[p<=0].sum())
        srcout[str(int(z))]={'net':float(p.sum()),'trades':int(len(p)),'gp':gp,'gl':gl,'pf':float(gp/-gl if gl<0 else 999.),'win':float(np.mean(p>0))}

    CE=np.concatenate([WE,SE]); CX=np.concatenate([WX,SX]); CR=np.concatenate([WR,SR]); CD=np.concatenate([WD,SD]); CP=np.concatenate([WP,pnl]); CH=np.concatenate([WH,(xt-et)/1000.])
    order=np.lexsort((np.arange(len(CE)),CE)); CE,CX,CR,CD,CP,CH=[z[order] for z in (CE,CX,CR,CD,CP,CH)]
    cex=eq.exact_equity_sweep(t,a,b,CE,CX,CR,CD,CP)

    events=[]
    for i in range(len(WE)): events.append((int(t[int(WE[i])]),1,'watchdog')); events.append((int(t[int(WX[i])]),-1,'watchdog'))
    for i in range(len(SE)): events.append((int(t[int(SE[i])]),1,'coverage')); events.append((int(t[int(SX[i])]),-1,'coverage'))
    events.sort(key=lambda z:(z[0],z[1]))
    counts={'watchdog':0,'coverage':0}; sys_mo=0; overlap_mo=0; overlap_ms_count=0
    for ts,delta,who in events:
        counts[who]+=delta
        cur=counts['watchdog']+counts['coverage']; sys_mo=max(sys_mo,cur)
        if counts['watchdog']>0 and counts['coverage']>0:
            overlap_mo=max(overlap_mo,cur); overlap_ms_count+=1

    ss=summary(t,sex,SX,pnl,(xt-et)/1000.); ss.update(cap=512,skips=int(sk),pnl_reconstruction_max_abs_err=err,sources=srcout,pre_cap_candidates=int(len(C[0])))
    cs=summary(t,cex,CX,CP,CH); cs.update(system_maxopen_event_sweep=int(sys_mo),cross_sleeve_overlap_maxopen=int(overlap_mo),cross_sleeve_overlap_event_count=int(overlap_ms_count))
    wsum={k:wr[k] for k in ['net','trades','gross_profit','gross_loss','pf','win','expectancy','avg_hold_s','balance_dd','equity_dd','minimum_total_equity','maxopen_exact']}
    out={
      'candidate':'GAMMA_02_JAN_WD119_PLUS_CAUSAL_GRID_COVERAGE_131B',
      'status':'JANUARY_COVERAGE_BREAKTHROUGH_PYTHON_RESEARCH_ONLY',
      'market_sha256':sha256_file(MARKET),
      'execution_surface':'Dukascopy midpoint + frozen session-P75 normalized spread from stmr_base.materialize; not raw-Dukascopy fill parity and not Coinexx MT5 certification',
      'watchdog_parent':'WD119_SUBPHASE_Q1190_Q1100_CAP703',
      'watchdog':wsum,'coverage_v3':ss,'combined':cs,
      'rules':{
        'month_or_week_feature':False,'coverage_interval_ms':250,'coverage_cap':512,
        'source9':'b10=0, H4/H1/M15/M5=+,+,+,-',
        'source11':'b10=2/3 +,+,-,-; plus b10=3 +,+,+,-',
        'source12':'b10=0/1/2 +,+,-,-; plus b10=4 +,+,+,- with previous-60s quote count<=210 strictly as-of',
        'source13':'b10=2/3 +,+,-,-','source14':'b10=3 +,+,-,+','source15':'b10=2/3 +,+,+,+',
        'source16':'b10=0/3/4 +,+,+,-; selected only after 250/500/1000/2000ms neighborhood robustness',
        'watchdog_logic_changed':False
      },
      'interpretation':[
        'Watchdog remains the January parent/high-renewal specialist; coverage is an earlier-session complementary grid/state sleeve.',
        'No calendar month/week/day identifier is an execution feature.',
        'Source16 short W5-only cells were deliberately excluded despite larger headline profit because they lacked comparable cross-week reliability.',
        'Combined result exceeds $200K without raising Watchdog max-open if exact overlap test remains zero/benign.',
        'Floating equity DD remains dominated by Watchdog synchronized inventory and is the next risk target.'
      ],
      'next':'GAMMA_02_JAN_WD119_EQUITY_HEAT_AND_W01_COLDSTART_131C',
      'august':'SEALED','mql5':'NOT_AUTHORIZED'
    }
    with open(OUT+'.partial','w') as f: json.dump(out,f,indent=2)
    with open(OUT,'w') as f: json.dump(out,f,indent=2)
    print(json.dumps(out,indent=2))

if __name__=='__main__': main()
