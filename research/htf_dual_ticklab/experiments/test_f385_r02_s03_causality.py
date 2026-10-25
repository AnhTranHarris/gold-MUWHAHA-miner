"""F385-R02-S03 causal indexing fixtures. Independent of label fitting."""
import numpy as np

def marked_state(t,bid,ask,event_time):
 left=np.searchsorted(t,event_time,'left');right=np.searchsorted(t,event_time,'right')-1
 assert t[left]==event_time
 ix=left # earliest same-ms row; ambiguous rows must NEVER veto
 cb=np.r_[False,np.abs(np.diff(bid))>.001];ca=np.r_[False,np.abs(np.diff(ask))>.001]
 out=[]
 for w in (1000,5000,30000):
  lo=np.searchsorted(t,event_time-w,'left')
  out.extend((int(np.sum(cb[lo:ix+1]&~ca[lo:ix+1])),int(np.sum(ca[lo:ix+1]&~cb[lo:ix+1])),int(np.sum(cb[lo:ix+1]&ca[lo:ix+1]))))
 return (tuple(out),bool(right>left))

def completed_last(t,mid,event_time,tf):
 slot=t//tf;starts=np.r_[0,np.flatnonzero(np.diff(slot)!=0)+1];ends=(slot[starts]+1)*tf
 high=np.maximum.reduceat(mid,starts);low=np.minimum.reduceat(mid,starts)
 k=np.searchsorted(ends,event_time,'right')-1
 return None if k<0 else (float(high[k]),float(low[k]))

def run():
 t=np.array([0,500,1000,1200,2200,59000,59999,60000,60500,61000,120000,121000],dtype=np.int64)
 bid=np.array([100,100.01,100.01,100.02,100.02,100.1,100.12,100.15,100.18,100.21,100.3,100.4])
 ask=bid+np.array([.1,.1,.11,.11,.12,.1,.1,.1,.1,.1,.1,.1])
 event=60500
 a=marked_state(t,bid,ask,event)
 tt=np.r_[t,121500,122000,123000];bb=np.r_[bid,1000.,-1000.,2000.];aa=np.r_[ask,1001.,-999.,2001.]
 assert a==marked_state(tt,bb,aa,event),'future native quote changed past marked state'
 mid=(bid+ask)/2;past=completed_last(t,mid,event,60000)
 assert past==completed_last(tt,(bb+aa)/2,event,60000),'future candle changed completed-bar state'
 assert past[0]<100.3,'current incomplete 60s bar leaked'
 t2=np.array([0,500,1000,1000,1200]);b2=np.array([100.,100.1,100.2,200.,200.]);a2=b2+.1
 out,amb=marked_state(t2,b2,a2,1000);assert amb and out==marked_state(t2[:3],b2[:3],a2[:3],1000)[0]
 t0=100000;assert 131999<t0+32000 and 132001>=t0+32000
 print('PASS 4/4 causal fixtures: native quote prefix; completed HTF publication; same-ms no-future; mature-label lag')
if __name__=='__main__':run()
