// Storage-only comparison; neither model inference nor terminal latency benchmark.
#include "host_compat.hpp"
#include "HG6Storage.mqh"
int main(){
 std::vector<uchar> id,payload(4*1024*1024),out;for(size_t k=0;k<payload.size();++k)payload[k]=(uchar)((k*131u+k/257u)%256u);
 assert(HG6TextDigest("bench",id));HG6Store s;assert(s.Init("bench_state",id)&&s.Load(out)==0);std::vector<ulong> us;
 for(int k=0;k<21;k++){payload[0]=(uchar)k;ulong begin=GetMicrosecondCount();assert(s.Save(payload));ulong elapsed=GetMicrosecondCount()-begin;if(k)us.push_back(elapsed);}
 HG6Store r;assert(r.Init("bench_state",id)&&r.Load(out)==1&&r.Healthy()&&r.Generation()==21&&out==payload);std::sort(us.begin(),us.end());std::cout<<"payload_bytes="<<payload.size()<<" runs="<<us.size()<<" median_us="<<(us[9]+us[10])/2<<" p95_us="<<us[18]<<" max_us="<<us[19]<<" readback=exact\n";
}
