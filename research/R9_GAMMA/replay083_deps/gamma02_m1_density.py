import sys,time,json,numpy as np
from numba import njit
sys.path.insert(0,'/mnt/data')
import stmr_janjul as j, stmr_base as c
DAY=j.DAY

# session masks bit position equals c.sess_fixed code
SESSION_LON_OV_NY=(1<<2)|(1<<3)|(1<<4)
SESSION_LON_OV=(1<<2)|(1<<3)
SESSION_OV_NY=(1<<3)|(1<<4)
SESSION_OV=(1<<3)

@njit(cache=True)
def permit(mode,h4,h1,m15,m5):
    # returns direction -1/0/+1 using completed-bar states only
    if mode==0: # ALIGN4
        if h4!=0 and h4==h1 and h1==m15 and m15==m5:return h4
        return 0
    if mode==1: # MACRO3: H4=H1=M15, M5 free
        if h4!=0 and h4==h1 and h1==m15:return h4
        return 0
    if mode==2: # MACRO2: H4=H1, lower TFs timing only
        if h4!=0 and h4==h1:return h4
        return 0
    if mode==3: # 3-of-4 vote but require H4/H1 not directly opposed when both nonzero
        if h4!=0 and h1!=0 and h4==-h1:return 0
        s=h4+h1+m15+m5
        if s>=2:return 1
        if s<=-2:return -1
        return 0
    return 0

@njit(cache=True)
def sim_ladder(t,a,b,mid,h4,h1,m15,m5,es,ee,perm_mode,session_mask,
               step_raw,tp_raw,sl_raw,hold_ms,maxpos,max_events_minute,
               require_favorable_open=1):
    # fresh M1 anchor + one-shot favorable boundary ladder
    act=np.zeros(32,np.uint8); dr=np.zeros(32,np.int8); ent=np.zeros(32,np.int32); et=np.zeros(32,np.int64); stp=np.zeros(32,np.int32); tgt=np.zeros(32,np.int32)
    R=np.zeros(18,np.float64)
    bal=0.;peak=0.;open_n=0; cur_min=np.int64(-1);anchor=0;last_level=0;events=0
    for i in range(t.size):
        ti=t[i];ask=int(a[i]);bid=int(b[i]);midx=int(mid[i]);floating=0.
        # exits
        for z in range(32):
            if not act[z]:continue
            dd=int(dr[z]);e=int(ent[z]);reason=0;ex=0
            if dd>0:
                if bid>=tgt[z]:reason=1;ex=bid
                elif bid<=stp[z]:reason=2;ex=bid
                elif ti-et[z]>=hold_ms:reason=3;ex=bid
                else:floating+=(bid-e)/1000.-.01
            else:
                if ask<=tgt[z]:reason=1;ex=ask
                elif ask>=stp[z]:reason=2;ex=ask
                elif ti-et[z]>=hold_ms:reason=3;ex=ask
                else:floating+=(e-ask)/1000.-.01
            if reason:
                pnl=((ex-e) if dd>0 else (e-ex))/1000.-.02
                bal+=pnl;R[0]+=pnl;R[3]+=1
                if pnl>0:R[1]+=pnl;R[4]+=1
                else:R[2]+=pnl
                R[7+reason]+=1;act[z]=0;open_n-=1
        if bal>peak:peak=bal
        bdd=peak-bal
        if bdd>R[12]:R[12]=bdd
        eq=bal+floating;edd=peak-eq
        if edd>R[13]:R[13]=edd
        if eq<R[14]:R[14]=eq
        minute=(ti//60000)*60000
        if minute!=cur_min:
            cur_min=minute;anchor=midx;last_level=0;events=0;continue
        if ti<es or ti>=ee:continue
        s=c.sess_fixed(ti)
        if ((session_mask>>s)&1)==0:continue
        d=permit(perm_mode,h4[i],h1[i],m15[i],m5[i])
        if d==0:continue
        # current favorable displacement in raw units
        disp=(midx-anchor)*d
        if require_favorable_open and disp<=0:continue
        level=disp//step_raw
        if level<=last_level:continue
        # each newly crossed level can create at most one event; catch up but cap/minute
        target_level=level
        while last_level<target_level and events<max_events_minute:
            last_level+=1;events+=1;R[5]+=1
            if open_n>=maxpos:R[6]+=1;continue
            q=-1
            for z in range(32):
                if not act[z]:q=z;break
            if q<0:R[6]+=1;continue
            e=ask if d>0 else bid
            act[q]=1;dr[q]=d;ent[q]=e;et[q]=ti;open_n+=1
            stp[q]=e-sl_raw if d>0 else e+sl_raw
            tgt[q]=e+tp_raw if d>0 else e-tp_raw
            if open_n>R[11]:R[11]=open_n
    if t.size:
        ask=int(a[-1]);bid=int(b[-1])
        for z in range(32):
            if act[z]:
                dd=int(dr[z]);e=int(ent[z]);ex=bid if dd>0 else ask
                pnl=((ex-e) if dd>0 else (e-ex))/1000.-.02;bal+=pnl;R[0]+=pnl;R[3]+=1
                if pnl>0:R[1]+=pnl;R[4]+=1
                else:R[2]+=pnl
                R[15]+=1
    return R

@njit(cache=True)
def sim_rebreak(t,a,b,mid,h4,h1,m15,m5,es,ee,perm_mode,session_mask,
                trigger_raw,reset_raw,tp_raw,sl_raw,hold_ms,maxpos,max_events_minute):
    # fresh M1 trigger; re-arm only after explicit pullback inside trigger by reset_raw
    act=np.zeros(32,np.uint8); dr=np.zeros(32,np.int8); ent=np.zeros(32,np.int32); et=np.zeros(32,np.int64); stp=np.zeros(32,np.int32); tgt=np.zeros(32,np.int32)
    R=np.zeros(18,np.float64);bal=0.;peak=0.;open_n=0;cur_min=np.int64(-1);anchor=0;armed=1;events=0;lastd=0
    for i in range(t.size):
        ti=t[i];ask=int(a[i]);bid=int(b[i]);midx=int(mid[i]);floating=0.
        for z in range(32):
            if not act[z]:continue
            dd=int(dr[z]);e=int(ent[z]);reason=0;ex=0
            if dd>0:
                if bid>=tgt[z]:reason=1;ex=bid
                elif bid<=stp[z]:reason=2;ex=bid
                elif ti-et[z]>=hold_ms:reason=3;ex=bid
                else:floating+=(bid-e)/1000.-.01
            else:
                if ask<=tgt[z]:reason=1;ex=ask
                elif ask>=stp[z]:reason=2;ex=ask
                elif ti-et[z]>=hold_ms:reason=3;ex=ask
                else:floating+=(e-ask)/1000.-.01
            if reason:
                pnl=((ex-e) if dd>0 else (e-ex))/1000.-.02;bal+=pnl;R[0]+=pnl;R[3]+=1
                if pnl>0:R[1]+=pnl;R[4]+=1
                else:R[2]+=pnl
                R[7+reason]+=1;act[z]=0;open_n-=1
        if bal>peak:peak=bal
        bdd=peak-bal
        if bdd>R[12]:R[12]=bdd
        eq=bal+floating;edd=peak-eq
        if edd>R[13]:R[13]=edd
        if eq<R[14]:R[14]=eq
        minute=(ti//60000)*60000
        if minute!=cur_min:
            cur_min=minute;anchor=midx;armed=1;events=0;lastd=0;continue
        if ti<es or ti>=ee:continue
        s=c.sess_fixed(ti)
        if ((session_mask>>s)&1)==0:continue
        d=permit(perm_mode,h4[i],h1[i],m15[i],m5[i])
        if d==0:continue
        # if HTF direction flips intraminute, reset rebreak state to new direction
        if lastd!=0 and d!=lastd: armed=1;anchor=midx;events=0
        lastd=d
        disp=(midx-anchor)*d
        if not armed and disp<=trigger_raw-reset_raw:armed=1
        if not armed or disp<trigger_raw or events>=max_events_minute:continue
        armed=0;events+=1;R[5]+=1
        if open_n>=maxpos:R[6]+=1;continue
        q=-1
        for z in range(32):
            if not act[z]:q=z;break
        if q<0:R[6]+=1;continue
        e=ask if d>0 else bid;act[q]=1;dr[q]=d;ent[q]=e;et[q]=ti;open_n+=1
        stp[q]=e-sl_raw if d>0 else e+sl_raw;tgt[q]=e+tp_raw if d>0 else e-tp_raw
        if open_n>R[11]:R[11]=open_n
    return R

@njit(cache=True)
def sim_stair(t,a,b,mid,h4,h1,m15,m5,es,ee,perm_mode,session_mask,
              step_raw,tp_raw,sl_raw,hold_ms,maxpos,max_events_minute):
    # favorable extreme stair: add only after a NEW favorable extreme by step_raw
    act=np.zeros(32,np.uint8); dr=np.zeros(32,np.int8); ent=np.zeros(32,np.int32); et=np.zeros(32,np.int64); stp=np.zeros(32,np.int32); tgt=np.zeros(32,np.int32)
    R=np.zeros(18,np.float64);bal=0.;peak=0.;open_n=0;cur_min=np.int64(-1);anchor=0;last_ext=0;events=0;lastd=0
    for i in range(t.size):
        ti=t[i];ask=int(a[i]);bid=int(b[i]);midx=int(mid[i]);floating=0.
        for z in range(32):
            if not act[z]:continue
            dd=int(dr[z]);e=int(ent[z]);reason=0;ex=0
            if dd>0:
                if bid>=tgt[z]:reason=1;ex=bid
                elif bid<=stp[z]:reason=2;ex=bid
                elif ti-et[z]>=hold_ms:reason=3;ex=bid
                else:floating+=(bid-e)/1000.-.01
            else:
                if ask<=tgt[z]:reason=1;ex=ask
                elif ask>=stp[z]:reason=2;ex=ask
                elif ti-et[z]>=hold_ms:reason=3;ex=ask
                else:floating+=(e-ask)/1000.-.01
            if reason:
                pnl=((ex-e) if dd>0 else (e-ex))/1000.-.02;bal+=pnl;R[0]+=pnl;R[3]+=1
                if pnl>0:R[1]+=pnl;R[4]+=1
                else:R[2]+=pnl
                R[7+reason]+=1;act[z]=0;open_n-=1
        if bal>peak:peak=bal
        bdd=peak-bal
        if bdd>R[12]:R[12]=bdd
        eq=bal+floating;edd=peak-eq
        if edd>R[13]:R[13]=edd
        if eq<R[14]:R[14]=eq
        minute=(ti//60000)*60000
        if minute!=cur_min:
            cur_min=minute;anchor=midx;last_ext=0;events=0;lastd=0;continue
        if ti<es or ti>=ee:continue
        s=c.sess_fixed(ti)
        if ((session_mask>>s)&1)==0:continue
        d=permit(perm_mode,h4[i],h1[i],m15[i],m5[i])
        if d==0:continue
        if lastd!=0 and d!=lastd:anchor=midx;last_ext=0;events=0
        lastd=d
        disp=(midx-anchor)*d
        if disp<=last_ext or events>=max_events_minute:continue
        # create events for each newly exceeded stair step
        next_step=((last_ext//step_raw)+1)*step_raw
        while disp>=next_step and events<max_events_minute:
            last_ext=next_step;next_step+=step_raw;events+=1;R[5]+=1
            if open_n>=maxpos:R[6]+=1;continue
            q=-1
            for z in range(32):
                if not act[z]:q=z;break
            if q<0:R[6]+=1;continue
            e=ask if d>0 else bid;act[q]=1;dr[q]=d;ent[q]=e;et[q]=ti;open_n+=1
            stp[q]=e-sl_raw if d>0 else e+sl_raw;tgt[q]=e+tp_raw if d>0 else e-tp_raw
            if open_n>R[11]:R[11]=open_n
    return R

def pack(R):
    return dict(net=float(R[0]),gp=float(R[1]),gl=float(R[2]),trades=int(R[3]),wins=int(R[4]),events=int(R[5]),skips=int(R[6]),tp_exits=int(R[8]),sl_exits=int(R[9]),age_exits=int(R[10]),maxopen=int(R[11]),bdd=float(R[12]),edd=float(R[13]),mineq=float(R[14]),forced=int(R[15]),pf=float(R[1]/-R[2] if R[2]<0 else 999),exp=float(R[0]/R[3] if R[3] else 0),win=float(R[4]/R[3] if R[3] else 0))

def prep():
    st=time.time();t,sa,sb,start,end=j.load_month(1,10);a,b=c.materialize(t,sa,sb);mid=((a.astype(np.int64)+b.astype(np.int64))//2).astype(np.int32);states=j.make_states(t,b,((8,21),(8,21),(8,21),(8,21)));print('prep',len(t),round(time.time()-st,2),flush=True);return t,a,b,mid,*states,max(start,c.ENTRY_START),end

if __name__=='__main__':
    import argparse
    ap=argparse.ArgumentParser();ap.add_argument('--family',choices=['ladder','rebreak','stair'],required=True);ap.add_argument('--out',required=True);ap.add_argument('--perm',type=int,default=-1);args=ap.parse_args()
    d=prep();rows=[];st=time.time();n=0
    # Bounded discovery grid, London+Overlap+NY only.
    if args.family=='ladder':
      for pm in ([args.perm] if args.perm>=0 else [0,1,2,3]):
       for step in [200,300,500,750,1000]:
        for tp,sl,hold in [(2000,1500,10000),(3000,1500,10000),(4000,2000,15000),(6000,2000,15000),(8000,2000,10000),(8000,3000,15000)]:
         R=sim_ladder(*d,pm,SESSION_LON_OV_NY,step,tp,sl,hold,8,8,1);r=dict(family='ladder',perm=pm,step=step,tp=tp,sl=sl,hold=hold,session='LON_OV_NY',**pack(R));rows.append(r);n+=1
    elif args.family=='rebreak':
      for pm in ([args.perm] if args.perm>=0 else [0,1,2,3]):
       for trig in [300,500,750,1000,1500]:
        for reset in [100,200,300,500]:
         if reset>=trig:continue
         for tp,sl,hold in [(2000,1500,10000),(3000,1500,10000),(4000,2000,15000),(6000,2000,15000),(8000,2000,10000)]:
          R=sim_rebreak(*d,pm,SESSION_LON_OV_NY,trig,reset,tp,sl,hold,8,8);r=dict(family='rebreak',perm=pm,trigger=trig,reset=reset,tp=tp,sl=sl,hold=hold,session='LON_OV_NY',**pack(R));rows.append(r);n+=1
    else:
      for pm in ([args.perm] if args.perm>=0 else [0,1,2,3]):
       for step in [200,300,500,750,1000,1500]:
        for tp,sl,hold in [(2000,1500,10000),(3000,1500,10000),(4000,2000,15000),(6000,2000,15000),(8000,2000,10000),(8000,3000,15000)]:
         R=sim_stair(*d,pm,SESSION_LON_OV_NY,step,tp,sl,hold,8,8);r=dict(family='stair',perm=pm,step=step,tp=tp,sl=sl,hold=hold,session='LON_OV_NY',**pack(R));rows.append(r);n+=1
    rows.sort(key=lambda x:x['net'],reverse=True);json.dump(rows,open(args.out,'w'),indent=2)
    print('family',args.family,'n',n,'elapsed',round(time.time()-st,1),'best',json.dumps(rows[0]),flush=True)
    print('TOP10')
    for r in rows[:10]:print(json.dumps(r),flush=True)