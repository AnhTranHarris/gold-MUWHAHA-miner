"""R00-067 research candidate inputs: exact native-tick re-label and causal quote-innovation augmentation.
Only eight SHA-256 pinned originals. Historical exposed Jan/Feb/Jun/Jul.
Raw quote labels STRICTLY at first observed original quote >= event+30s and <event+32s.
No feature uses quote time later than decision. Existing event-engine, event indices and broker UTC policy unmodified.
"""
import sys,hashlib,json,zipfile,io,time
from pathlib import Path
import numpy as np
import pandas as pd
ROOT=Path('/mnt/data');BASE=ROOT/'xauusd_r00_continue';OUT=BASE/'runs'/'native_relabel';OUT.mkdir(parents=True,exist_ok=True)
Z=zipfile.ZipFile(ROOT/'R00_065_COMPLETE_NATIVE_QUOTE_RESEARCH_20261018.zip');PINS=json.loads(Z.read('APPROVED_SOURCE_PIN_MANIFEST.json'))


def load_raw(b,m):
    name=f'XAUUSD_DUKAS_2026_{m}_ticks.csv.gz' if b=='dukascopy' else f'XAUUSD_MT5_BROKER_2026_{m}_ticks_ALL.csv.gz'
    f=ROOT/name
    with f.open('rb') as h: sha=hashlib.file_digest(h,'sha256').hexdigest()
    assert sha==PINS[name]['sha256'] and f.stat().st_size==PINS[name]['bytes'],f'SOURCE UNAUTHORIZED {name}'
    if b=='dukascopy':
        d=pd.read_csv(f,usecols=['timestamp_ms_utc','bid_raw','ask_raw'],dtype={'timestamp_ms_utc':'int64','bid_raw':'int32','ask_raw':'int32'})
        t=d.timestamp_ms_utc.to_numpy(copy=True);bid=d.bid_raw.to_numpy(dtype=np.float64)/1000;ask=d.ask_raw.to_numpy(dtype=np.float64)/1000
    else:
        d=pd.read_csv(f,usecols=['time_msc','bid','ask'],dtype={'time_msc':'int64','bid':'float32','ask':'float32'})
        t=d.time_msc.to_numpy(copy=True)-(120 if m in ('01','02') else 180)*60000
        bid=d.bid.to_numpy(dtype=np.float64);ask=d.ask.to_numpy(dtype=np.float64)
    del d
    assert np.all(np.diff(t)>=0) and np.all(bid>0) and np.all(ask>=bid)
    return t,bid,ask,sha


def create(b,m):
    tt=time.time(); t,bid,ask,sha=load_raw(b,m)
    member=next(x for x in Z.namelist() if x.endswith(f'/native_{b}_{m}.npz'))
    original=np.load(io.BytesIO(Z.read(member)),allow_pickle=False)
    event_t=original['ts_ms']; j=original['quote_index']; assert np.array_equal(event_t,t[j]),'original event index / UTC mismatch'
    mid=(bid+ask)*.5;target=event_t+30000;fi=np.searchsorted(t,target,'left');exists=fi<len(t)
    future_t=t[np.minimum(fi,len(t)-1)]
    known=exists & (future_t>=target) & (future_t<target+2000)
    delta=mid[np.minimum(fi,len(t)-1)]-mid[j]
    y=np.where(known,np.where(delta>.10,1,np.where(delta<-.10,-1,0)),0).astype(np.int8)
    # At decision t, quote index j identifies last observed quote. No post-decision events enter X.
    def prior(ms):return np.maximum(np.searchsorted(t,event_t-ms,side='right')-1,0)
    past={w:prior(w) for w in (100,250,500,1000,2000,5000)}
    # Causal innovation features computed from original raw bid/ask quote chronology.
    # Updates are indicative dealer quote changes, not executable trade prints or order flow.
    db=np.empty(len(t),dtype=np.float32);da=np.empty(len(t),dtype=np.float32)
    db[0]=0.;da[0]=0.;db[1:]=np.diff(bid).astype(np.float32);da[1:]=np.diff(ask).astype(np.float32)
    bc=(abs(db)>0.0005);ac=(abs(da)>0.0005)
    count_bid=np.cumsum(bc,dtype=np.int64);count_ask=np.cumsum(ac,dtype=np.int64)
    c_up=np.cumsum(((db+da)>0.0005),dtype=np.int64);c_dn=np.cumsum(((db+da)<-0.0005),dtype=np.int64)
    arr=[];names=[]
    def append(label,v):names.append(label);arr.append(np.asarray(v,dtype=np.float32))
    append('last_quote_delta_bid',db[j]);append('last_quote_delta_ask',da[j]);append('last_quote_kind',bc[j].astype(np.int8)+2*ac[j].astype(np.int8))
    prev_j=np.maximum(j-1,0);append('last_quote_age_ms',t[j]-t[prev_j])
    for w,p in past.items():
        append(f'bid_delta_{w}ms',bid[j]-bid[p]);append(f'ask_delta_{w}ms',ask[j]-ask[p]);append(f'mid_delta_{w}ms',mid[j]-mid[p]);append(f'quote_count_{w}ms',j-p)
        append(f'bid_updates_{w}ms',count_bid[j]-count_bid[p]);append(f'ask_updates_{w}ms',count_ask[j]-count_ask[p]);append(f'up_updates_{w}ms',c_up[j]-c_up[p]);append(f'down_updates_{w}ms',c_dn[j]-c_dn[p]);
    # Arrival imbalances condition on past 0.5s versus preceding 0.5s (no future).
    p0=past[1000];p1=past[500]
    append('bid_acceleration_500ms',(bid[j]-bid[p1])-(bid[p1]-bid[p0]));append('ask_acceleration_500ms',(ask[j]-ask[p1])-(ask[p1]-ask[p0]))
    # independent one-sided latest quote updates / age for each side, causal only
    bid_changes=np.flatnonzero(bc); ask_changes=np.flatnonzero(ac)
    def last_side_age(changes):
        v=np.searchsorted(changes,j,side='right')-1;ok=v>=0;at=np.zeros(len(j),dtype=np.int64)
        at[ok]=t[j[ok]]-t[changes[v[ok]]];at[~ok]=-1
        return at
    append('last_bid_change_age_ms',last_side_age(bid_changes));append('last_ask_change_age_ms',last_side_age(ask_changes))
    xnew=np.column_stack(arr).astype(np.float32)
    X=np.column_stack([original['feature'],xnew]).astype(np.float32)
    # Cache 30-second source-native label; historical original y is NEVER overwritten.
    out=OUT/f'corrected_{b}_{m}.npz';np.savez_compressed(out,ts_ms=event_t,quote_index=j,feature=X,y=y,markout_30s=delta.astype(np.float32),known_30s=known,original_y=original['y'],expert_mask=original['expert_mask'],expert_votes=original['expert_votes'])
    with out.open('rb') as h:sha_out=hashlib.file_digest(h,'sha256').hexdigest()
    receipt={'broker':b,'month':m,'source':('XAUUSD_DUKAS_2026_'+m+'_ticks.csv.gz' if b=='dukascopy' else 'XAUUSD_MT5_BROKER_2026_'+m+'_ticks_ALL.csv.gz'),'source_sha256':sha,'original_member':member,'event_count':len(j),'real_ticks':len(t), 'features_original':int(original['feature'].shape[1]),'features_total':X.shape[1],'features_new':names,'unknown_30s':int(np.count_nonzero(~known)),'neutral_30s':int(np.count_nonzero(y==0)),'up_30s':int(np.count_nonzero(y==1)),'down_30s':int(np.count_nonzero(y==-1)),'old_y_30s_agreement_fraction':float((y==original['y']).mean()),'output_sha256':sha_out,'output_bytes':out.stat().st_size,'elapsed_s':round(time.time()-tt,3),'status':'CORRECTED_CAUSAL_LABEL_RESEARCH_NOT_PROFIT'}
    (OUT/f'corrected_{b}_{m}_receipt.json').write_text(json.dumps(receipt,indent=2))
    print(json.dumps({k:receipt[k] for k in ['broker','month','event_count','real_ticks','neutral_30s','up_30s','down_30s','old_y_30s_agreement_fraction','elapsed_s']}),flush=True)

if __name__=='__main__':
 for b,m in [tuple(s.split(':')) for s in sys.argv[1:]]:create(b,m)
