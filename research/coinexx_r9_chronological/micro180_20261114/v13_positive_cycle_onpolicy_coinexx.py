"""Micro180 V13: actual ordered Coinexx quote entry replay with independent
positive-cycle event-hazard heads. No teacher access during decisions.

USAGE: python micro180_v13_onpolicy_forward.py --source ORIGINAL.csv.gz --merged VERIFIED.csv.gz
       --model-dir EXISTING_FROZEN_MODELS --start-eval-row 900000 --max-rows 1800000

Existing ML inputs: online multi-horizon Bid/Ask features, 1-300s lookbacks,
completed 1s direction/efficiency, forming 5s/15s displacement, completed M5
ATR copied as-of from original R9 REAL TickLogger row, and session/price clock.
No logger 'event', teacher time, future quote, or cycle outcome is used for orders.
"""
from __future__ import annotations
import argparse,collections,csv,datetime,gzip,json,hashlib,math,time
from dataclasses import dataclass
from pathlib import Path
import numpy as np
import lightgbm as lgb

FIRST_FEATURES=['sec_of_minute','spread_u','atr_u','side_barrier_u','mid_change_since_minute','signed_s1_disp','s1_eff','s1_range','s1_turns','signed_ret1','signed_ret3','signed_ret5','signed_ret10','signed_ret15','signed_ret30','signed_ret60','signed_ret180','signed_ret300','signed_acc3','signed_basket5','signed_basket15','prior10_eff','prior30_eff','momentum_phase','hour']
SECOND_FEATURES=FIRST_FEATURES+['prior_reversal_3s_u','prior_reversal_5s_u','prior_reversal_15s_u','signed_minute_high_gap_u','signed_minute_low_gap_u','signed_prior30s_bias_u','signed_prior60s_bias_u','signed_cross_basket_5_15_u','spread_delta_prev_second_u','near_minute_end_indicator']

@dataclass
class Position:
    side:int
    entry_ms:int
    entry_minute:int
    entry_u:int
    sl_u:int
    peak_profit_u:int=0
    peak_loss_u:int=0

class CausalTwoHead:
    def __init__(self,model_dir:Path,first_threshold=.60,second_threshold=.50,max_spread_u=25):
        self.first=lgb.Booster(model_file=str(model_dir/'micro180_positive_first_hazard_model.txt'))
        self.second=lgb.Booster(model_file=str(model_dir/'micro180_positive_second_hazard_model.txt'))
        self.t1=float(first_threshold);self.t2=float(second_threshold)
        self.max_spread_u=max_spread_u
        self.hist={};self.histq=collections.deque()
        self.bars=collections.deque(maxlen=305)
        self.minute=None;self.minute_first=None;self.minute_hi=0.;self.minute_lo=0.
        self.b5=None;self.b15=None;self.mid5=0.;self.mid15=0.
        self.last_sec=None;self.last_mid=None;self.cur_hi=self.cur_lo=self.cur_close=None
        self.last_spread=None;self.prior_spread=0
        self.position:Position|None=None
        self.first_done=False;self.rearm_ready=False;self.rearm_side=0
        self.scheduled=None;self.entries=[];self.close_records=[]
        self.stats=collections.Counter()
        self.last_first_close=None;self.first_exit_ms=None
        self.last_processed_ms=-1

    def past(self,sec,age):
        for delay in (0,1,2):
            v=self.hist.get(sec-age-delay)
            if v is not None:return v
        return None
    def efficiency(self,sec,span):
        vals=[self.hist[sec-j] for j in range(span,0,-1) if sec-j in self.hist]
        if len(vals)<max(3,span//2):return 0.
        return abs(vals[-1]-vals[0])/(sum(abs(b-a) for a,b in zip(vals,vals[1:]))+1e-6)

    def close(self,ms,bid,ask,reason):
        p=self.position
        if p is None:return
        exit_u=bid if p.side==1 else ask
        pnl_u=p.side*(exit_u-p.entry_u)
        result={'minute':p.entry_minute,'side':p.side,'entry_ms':p.entry_ms,'exit_ms':ms,
                'entry_price_u':p.entry_u,'exit_price_u':exit_u,'net_price_u':pnl_u,
                'reason':reason,'mfe_u':p.peak_profit_u,'mae_u':p.peak_loss_u}
        self.close_records.append(result)
        if self.first_done and not self.rearm_ready and self.last_first_close is None:
            # First entry can close even when the next observed quote belongs
            # to a new minute; only same-minute opposite rearm is legal.
            self.last_first_close=result
            self.first_exit_ms=ms
            if ms//60000==p.entry_minute:
                self.rearm_ready=True
                self.rearm_side=-p.side
                self.stats['rearm_available']+=1
        else:
            self.rearm_ready=False
        self.position=None
        self.stats['closed_'+reason]+=1

    def manage(self,ms,bid,ask):
        p=self.position
        if p is None:return
        exe=bid if p.side==1 else ask
        signed=p.side*(exe-p.entry_u)
        p.peak_profit_u=max(p.peak_profit_u,signed)
        p.peak_loss_u=max(p.peak_loss_u,-signed)
        if (p.side==1 and exe<=p.sl_u) or (p.side==-1 and exe>=p.sl_u):
            self.close(ms,bid,ask,'stop');return
        if (ms//1000)-(p.entry_ms//1000)>=30:
            self.close(ms,bid,ask,'timeout');return
        if signed>=10:
            if p.side==1:p.sl_u=max(p.sl_u,bid-3)
            else:p.sl_u=min(p.sl_u,ask+3)

    def _enter(self,ms,minute,side,bid,ask,kind,prob,origin_ms):
        if self.position is not None:return
        entry=ask if side==1 else bid
        sl=(bid-30) if side==1 else ask+30
        self.position=Position(side,ms,minute,entry,sl)
        self.entries.append({'minute':minute,'time_msc':ms,'side':side,'price_u':entry,
                             'leg':1 if kind=='first' else 2,'entry_probability':round(prob,6),
                             'entry_signal_msc':origin_ms,'signal_to_entry_ms':ms-origin_ms})
        self.stats['entry_'+kind]+=1
        if kind=='first':
            self.first_done=True;self.last_first_close=None;self.rearm_ready=False
        else:
            self.rearm_ready=False

    def on_quote(self,ms,bid,ask,atr):
        if ms < self.last_processed_ms:raise ValueError('Source tick timestamps nonmonotonic')
        self.last_processed_ms=ms
        sec=ms//1000; minute=sec//60;mid=(bid+ask)/2.;spread=ask-bid
        if spread<0:raise ValueError('Crossed quote')
        if minute!=self.minute:
            self.minute=minute;self.minute_first=mid;self.minute_hi=mid;self.minute_lo=mid
            self.first_done=False;self.rearm_ready=False;self.rearm_side=0
            self.last_first_close=None;self.first_exit_ms=None
            self.scheduled=None
            self.stats['minute_seen']+=1
        self.minute_hi=max(self.minute_hi,mid);self.minute_lo=min(self.minute_lo,mid)
        if self.b5!=sec//5:self.b5=sec//5;self.mid5=mid
        if self.b15!=sec//15:self.b15=sec//15;self.mid15=mid
        # Every source quote updates the single inventory first, including
        # spread changes within an observed second.
        self.manage(ms,bid,ask)
        if sec==self.last_sec:
            self.last_mid=mid
            self.cur_hi=max(self.cur_hi,bid);self.cur_lo=min(self.cur_lo,bid)
            self.cur_close=bid
            return
        if self.last_sec is not None:
            self.bars.append((self.last_sec,self.cur_close,self.cur_hi,self.cur_lo))
            self.hist[self.last_sec]=self.last_mid
            self.histq.append(self.last_sec)
            while self.histq and self.histq[0]<sec-305:
                del self.hist[self.histq.popleft()]
        self.last_sec=sec;self.last_mid=mid
        self.cur_hi=self.cur_lo=self.cur_close=bid
        self.last_spread=spread
        # Zero lookahead: scheduled entry uses first quote from the *next*
        # observed second; stale >2s or wrong-minute orders are abandoned.
        if self.scheduled is not None:
            sig,side,kind,prob,t0=self.scheduled
            self.scheduled=None
            if (ms>=sig and ms<=sig+2000 and ms//60000==self.minute
                and self.position is None and spread<=self.max_spread_u
                and (kind=='first' and not self.first_done or
                     kind=='second' and self.rearm_ready and self.rearm_side==side)):
                self._enter(ms,minute,side,bid,ask,kind,prob,t0)
            else:self.stats['scheduled_rejected']+=1
        if self.position is not None or spread>self.max_spread_u:return
        kind='second' if self.first_done and self.rearm_ready else 'first' if not self.first_done else None
        if kind is None:return
        # Original positive model's completed-second feature geometry,
        # reproduced independently from real quote history.
        disp=ef=rng=turns=0.
        if len(self.bars)>=11:
            bars=list(self.bars)[-10:]
            closes=[x[1] for x in bars]
            diff=[b-a for a,b in zip(closes,closes[1:])]
            disp=closes[-1]-closes[0]
            ef=abs(disp)/(sum(abs(x) for x in diff)+1e-9)
            rng=max(x[2] for x in bars)-min(x[3] for x in bars)
            signs=[1 if x>0 else -1 for x in diff if x]
            turns=sum(a!=b for a,b in zip(signs,signs[1:]))
        changes=[mid-p if p is not None else 0. for p in
                 (self.past(sec,h) for h in (1,3,5,10,15,30,60,180,300))]
        p6=self.past(sec,6);acc=2*changes[1]-(mid-(mid if p6 is None else p6))
        eff10=self.efficiency(sec,10);eff30=self.efficiency(sec,30)
        # Runtime never accesses merged rows, logger event labels, position
        # annotations or original R9 positive cycle outcomes.
        available_sides=(self.rearm_side,) if kind=='second' else (1,-1)
        options=[]
        for side in available_sides:
            px=ask if side==1 else bid
            barrier=side*(px-(self.minute_first+side*15))
            f=[sec%60,spread,atr,barrier,side*(mid-self.minute_first),side*disp,ef,rng,turns]
            f.extend(side*x for x in changes)
            f.extend([side*acc,side*(mid-self.mid5),side*(mid-self.mid15),eff10,eff30,
                     side*changes[3]/max(10,math.sqrt(max(1,atr))), (sec//3600)%24])
            if kind=='second':
                p3=self.past(sec,3);p5=self.past(sec,5);p15=self.past(sec,15)
                p30=self.past(sec,30);p60=self.past(sec,60)
                f.extend([side*(mid-(mid if p3 is None else p3)),
                          side*(mid-(mid if p5 is None else p5)),
                          side*(mid-(mid if p15 is None else p15)),
                          side*(mid-self.minute_hi),side*(mid-self.minute_lo),
                          side*(mid-(mid if p30 is None else p30)),
                          side*(mid-(mid if p60 is None else p60)),
                          side*(self.mid5-self.mid15),0.,float(sec%60>=45)])
            model=self.second if kind=='second' else self.first
            score=float(model.predict(np.asarray(f,dtype=np.float32).reshape(1,-1),num_threads=1)[0])
            options.append((score,side))
        prob,chosen=max(options,key=lambda x:x[0])
        limit=self.t2 if kind=='second' else self.t1
        if prob>=limit:
            self.scheduled=((sec+1)*1000,chosen,kind,prob,ms)
            self.stats['scheduled_'+kind]+=1


def teacher_positive(merged:Path):
    grouped=collections.defaultdict(dict)
    with gzip.open(merged,'rt',encoding='utf-8-sig') as f:
        for r in csv.DictReader(f):
            dt=datetime.datetime.strptime(r['entry_time_broker'],'%Y-%m-%d %H:%M:%S').replace(tzinfo=datetime.timezone.utc)
            minute=int(dt.timestamp())//60
            grouped[minute][int(r['leg'])]=(int(dt.timestamp())*1000,1 if r['side']=='buy' else -1,
                int(r['equote_ms']),int(r['q_entry_u']),float(r['net_usd']),
                float(r['quote_net']) if r['quote_net'].strip() else float('nan'),
                0<=int(r['elag_ms'])<=2000 and 0<=int(r['xlag_ms'])<=2000)
    refs={};family={};totals=collections.Counter()
    for m,legs in grouped.items():
        a=legs.get(1);b=legs.get(2)
        if a is None:continue
        fam='A' if b is None else 'B' if a[4]>0 and b[4]>0 else 'C' if a[4]<=0 and b[4]>0 else 'other'
        if fam not in ('A','B','C'):continue
        rows=list(legs.values())
        if not all(x[6] and math.isfinite(x[5]) for x in rows):continue
        if sum(x[4] for x in rows)<=0 or sum(x[5] for x in rows)<=0:continue
        for i,entry in legs.items():refs[(m,i)]=entry;family[(m,i)]=fam
        totals[fam]+=1
    return refs,family,totals


def score(entries,refs,family,start_ms,end_ms):
    targets={k:r for k,r in refs.items() if start_ms<=r[0]<=end_ms}
    pred={ (r['minute'],r['leg']):r for r in entries if start_ms<=r['time_msc']<=end_ms }
    by=collections.defaultdict(collections.Counter)
    stats=collections.Counter(); abs_ts=[];abs_prices=[]
    for k,r in targets.items():
        fam=family[k];c=by[fam];c['reference']+=1;stats['reference']+=1
        p=pred.get(k)
        if p is None:continue
        c['same_minute_leg']+=1;stats['same_minute_leg']+=1
        if p['side']!=r[1]:continue
        c['correct_side']+=1;stats['correct_side']+=1
        dt=p['time_msc']-r[0];dq=p['price_u']-r[3];dm=p['time_msc']-r[2]
        abs_ts.append(abs(dt));abs_prices.append(abs(dq))
        if abs(dt)<=1000:c['within_1sec']+=1;stats['within_1sec']+=1
        if abs(dt)<=2000:c['within_2sec']+=1;stats['within_2sec']+=1
        if abs(dq)<=5:c['mapped_quote_within_5c']+=1;stats['mapped_quote_within_5c']+=1
        if abs(dm)<=2000 and abs(dq)<=5:
            c['mapped_quote_within_2sec_5c']+=1;stats['mapped_quote_within_2sec_5c']+=1
        if dm==0 and dq==0:c['exact_mapped_quote']+=1;stats['exact_mapped_quote']+=1
    # Teacher-positive precision uses positive targets as the desired class;
    # this does not establish profitability of unmatched student trades.
    stats['predicted']=len(pred)
    stats['extra_not_in_positive_targets']=sum(k not in targets for k in pred)
    metrics={'counts':dict(stats),'by_family':{f:dict(c) for f,c in sorted(by.items())},
             'median_abs_teacher_ms':float(np.median(abs_ts)) if abs_ts else None,
             'median_abs_quote_price_u':float(np.median(abs_prices)) if abs_prices else None,
             'positive_target_side_recall':round(stats['correct_side']/max(1,stats['reference']),6),
             'positive_target_side_precision_proxy':round(stats['correct_side']/max(1,stats['predicted']),6)}
    return metrics


def run(args):
    model_dir=Path(args.model_dir)
    model_hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in model_dir.glob('micro180_positive_*_hazard_model.txt')}
    engine=CausalTwoHead(model_dir,args.first_threshold,args.second_threshold,args.max_spread_u)
    start=time.time(); end_ms=None;first_ms=None
    idx=None
    with gzip.open(args.source,'rt',newline='') as f:
        rr=csv.reader(f);header=next(rr);idx={v:i for i,v in enumerate(header)}
        required={'time_msc','bid','ask','atr'}
        if not required.issubset(idx):raise ValueError('Original source TickLogger schema missing: '+repr(required-set(idx)))
        for n,r in enumerate(rr,1):
            if args.max_rows and n>args.max_rows:break
            ms=int(r[idx['time_msc']]); bid=round(float(r[idx['bid']])*100);ask=round(float(r[idx['ask']])*100)
            atr=float(r[idx['atr']])*100
            if first_ms is None:first_ms=ms
            end_ms=ms
            engine.on_quote(ms,bid,ask,atr)
            if n%args.chunk_rows==0:
                checkpoint={'rows':n,'last_tick_ms':ms,'entries':len(engine.entries),
                            'closes':len(engine.close_records),'elapsed_s':round(time.time()-start,2),
                            'last_source_span_minute':ms//60000,'model_hashes':model_hashes}
                Path(args.checkpoint).write_text(json.dumps(checkpoint,indent=2))
                print('CHUNK_CHECKPOINT',json.dumps(checkpoint),flush=True)
    print("DEBUG before_target_parse",round(time.time()-start,2),flush=True)
    refs,family,target_totals=teacher_positive(Path(args.merged))
    print("DEBUG after_target_parse",len(refs),round(time.time()-start,2),flush=True)
    print("DEBUG before_scoring",round(time.time()-start,2),flush=True)
    result={'source':str(args.source),'merged':str(args.merged),'source_rows':n-1 if args.max_rows and n>args.max_rows else n,
            'source_tick_first_msc':first_ms,'source_tick_last_msc':end_ms,
            'model_hashes':model_hashes,'full_positive_target_cycles':dict(target_totals),
            'positive_target_label_is_not_online_feature':True,
            'source_logger_event_is_not_online_feature':True,
            'independent_first_and_actual_own_rearm':True,
            'completed_second_virtual_clock_decision_to_next_second_first_quote':True,
            'source_quote_prices_are_not_broker_fills':True,
            'only_original_part_01_loaded':True,
            'first_entry_probability_threshold':args.first_threshold,
            'second_reentry_probability_threshold':args.second_threshold,
            'max_spread_cents':args.max_spread_u,
            'entry_records_total':len(engine.entries),'close_records_total':len(engine.close_records),
            'engine_counters':dict(engine.stats),'elapsed_s':round(time.time()-start,2),
            'metrics_after_frozen_model_train_source':score(engine.entries,refs,family,max(args.eval_start_ms,first_ms),end_ms),
            'limit_note':'Full 9-month match NOT measured; this reads one original Coinexx ticklogger part, not the full ten.'}
    Path(args.out).write_text(json.dumps(result,indent=2))
    print('FINAL',json.dumps({k:result[k] for k in ('source_rows','entry_records_total','close_records_total','metrics_after_frozen_model_train_source','elapsed_s')},indent=2),flush=True)
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--source',default='/mnt/data/GoldMuwahaha_R9_TickLog_REAL_TESTER_20260101_000000_part01_of_10.csv.gz')
    p.add_argument('--merged',default='/mnt/data/r9_synthetic_teacher_to_original_REAL_TickLogger_9m_trade_marks.csv.gz.csv')
    p.add_argument('--model-dir',default='/mnt/data/micro180_positive_entry_rebuild/positive_cycle_model')
    p.add_argument('--first-threshold',type=float,default=.60)
    p.add_argument('--second-threshold',type=float,default=.50)
    p.add_argument('--max-spread-u',type=int,default=25)
    p.add_argument('--max-rows',type=int,default=1800000)
    p.add_argument('--chunk-rows',type=int,default=300000)
    p.add_argument('--eval-start-ms',type=int,default=1767704914412)
    p.add_argument('--checkpoint',default='/mnt/data/micro180_positive_entry_rebuild/v13_current_checkpoint.json')
    p.add_argument('--out',default='/mnt/data/micro180_positive_entry_rebuild/v13_forward_positive_entry_metrics.json')
    run(p.parse_args())
