#ifndef HG6_JOURNAL_MQH
#define HG6_JOURNAL_MQH
#include "HG5StateCodec.mqh"
// J2: authoritative broker facts, in the same verified generation as intent/ledger.
// Logical append, bounded two-segment snapshot encoding; not an OS append/fsync claim.
#define HG6_JOURNAL_LIMIT 4096
#define HG6_JOURNAL_ROTATE 1024
#define HG6_JOURNAL_RESERVE 2112
#define HG6_J_INTENT 1
#define HG6_J_ACK 2
#define HG6_J_DEAL 3
#define HG6_J_RESOLVE 4
#define HG6_J_RELEASE 5
#define HG6_J_RESCUE 6
#define HG6_J_CANCEL 7
#define HG6_J_CANCEL_ACK 8
#define HG6_J_EXTERNAL_FLAT 9
#define HG6_J_PARTIAL 10
#define HG6_J_CORRELATE 11
#define HG6_J_RESCUE_RELEASE 12
#define HG6_J_EXTERNAL_RELEASE 13
#define HG6_J_EXTERNAL_RESCUE 14
struct HG6JournalRow {
 long number,sequence,proposal,ms,order,deal,position,generation;
 int type,action,side,units,retcode;
 double volume,price,profit,commission,swap,fee;
 bool Fields(HG5StateCodec &c){return c.I64(number)&&c.I64(sequence)&&c.I64(proposal)&&c.I64(ms)&&c.I64(order)&&c.I64(deal)&&c.I64(position)&&c.I64(generation)&&c.I32(type)&&c.I32(action)&&c.I32(side)&&c.I32(units)&&c.I32(retcode)&&c.F64(volume)&&c.F64(price)&&c.F64(profit)&&c.F64(commission)&&c.F64(swap)&&c.F64(fee)&&Valid();}
 bool Valid()const{return number>0&&sequence>=0&&ms>=0&&order>=0&&deal>=0&&position>=0&&generation>=0&&type>=1&&type<=14&&action>=0&&action<=2&&side>=-1&&side<=1&&units>=0&&MathIsValidNumber(volume)&&MathIsValidNumber(price)&&MathIsValidNumber(profit)&&MathIsValidNumber(commission)&&MathIsValidNumber(swap)&&MathIsValidNumber(fee)&&(type!=HG6_J_DEAL||(deal>0&&position>0&&order>0&&ms>0&&volume>0&&price>0&&(action==1||action==2)&&(side==1||side==-1)))&&((type!=HG6_J_RELEASE&&type!=HG6_J_EXTERNAL_RELEASE)||generation>0);}
 bool SameDeal(const HG6JournalRow &b)const{return type==HG6_J_DEAL&&b.type==HG6_J_DEAL&&deal==b.deal&&order==b.order&&position==b.position&&ms==b.ms&&action==b.action&&side==b.side&&volume==b.volume&&price==b.price&&profit==b.profit&&commission==b.commission&&swap==b.swap&&fee==b.fee;}
};
class HG6Journal {
 HG6JournalRow previous[],current[];long last,dropped,anchor_sequence,anchor_generation;
 bool Segment(HG5StateCodec &c,HG6JournalRow &rows[],long &expected){int n=ArraySize(rows);if(!c.I32(n)||n<0||n>HG6_JOURNAL_LIMIT)return false;if(c.Reading()&&ArrayResize(rows,n)!=n)return false;for(int i=0;i<n;i++){if(!rows[i].Fields(c)||rows[i].number!=++expected)return false;}return true;}
 public:
 HG6Journal(){last=dropped=anchor_sequence=anchor_generation=0;}
 long Last()const{return last;}
 long Dropped()const{return dropped;}
 long LastSequence()const{int n=ArraySize(current);if(n>0)return current[n-1].sequence;n=ArraySize(previous);return n>0?previous[n-1].sequence:0;}
 bool Read(long number,HG6JournalRow &row)const{if(number<=dropped||number>last)return false;long i=number-dropped-1;if(i<ArraySize(previous)){row=previous[(int)i];return true;}i-=ArraySize(previous);if(i<0||i>=ArraySize(current))return false;row=current[(int)i];return true;}
 int CurrentCount()const{return ArraySize(current);}
 int PreviousCount()const{return ArraySize(previous);}
 bool CanBegin()const{return ArraySize(current)<=HG6_JOURNAL_LIMIT-HG6_JOURNAL_RESERVE;}
 bool Append(HG6JournalRow &row){int n=ArraySize(current);if(n>=HG6_JOURNAL_LIMIT||last>=0x7ffffffffffffffe||(n>0&&row.sequence<current[n-1].sequence)||(n==0&&ArraySize(previous)>0&&row.sequence<previous[ArraySize(previous)-1].sequence))return false;row.number=last+1;if(!row.Valid()||ArrayResize(current,n+1)!=n+1)return false;current[n]=row;last++;return true;}
 bool Deal(HG6JournalRow &row){if(row.type!=HG6_J_DEAL||row.deal<=0)return false;for(int i=0;i<ArraySize(current);i++)if(current[i].type==HG6_J_DEAL&&current[i].deal==row.deal)return current[i].SameDeal(row);for(int i=0;i<ArraySize(previous);i++)if(previous[i].type==HG6_J_DEAL&&previous[i].deal==row.deal)return previous[i].SameDeal(row);return Append(row);}
 // Caller must have verified the core generation and committed the linked intent.
 // Rotation only at flat normal releases; never evict current in-flight evidence.
 bool Anchor(long sequence,long generation,bool flat,bool external=false){int n=ArraySize(current);int type=external?HG6_J_EXTERNAL_RELEASE:HG6_J_RELEASE;if(generation<=anchor_generation||sequence<=0||(external?sequence!=anchor_sequence:sequence<=anchor_sequence)||n==0||current[n-1].type!=type||current[n-1].sequence!=sequence||current[n-1].generation!=generation)return false;anchor_sequence=sequence;anchor_generation=generation;if(!flat||n<HG6_JOURNAL_ROTATE)return true;dropped+=ArraySize(previous);if(ArrayResize(previous,n)!=n)return false;for(int i=0;i<n;i++)previous[i]=current[i];return ArrayResize(current,0)==0;}
 bool Matches(long sequence,long generation,bool rescue)const{return anchor_generation==generation&&(rescue?anchor_sequence<=sequence:anchor_sequence==sequence);}
 bool StateFields(HG5StateCodec &c){if(!c.I64(last)||!c.I64(dropped)||!c.I64(anchor_sequence)||!c.I64(anchor_generation)||last<0||dropped<0||dropped>last||anchor_sequence<0||anchor_generation<0||(anchor_sequence==0)!=(anchor_generation==0))return false;long expected=dropped;if(!Segment(c,previous,expected)||!Segment(c,current,expected)||expected!=last)return false;long seq=0,ag=0,as=0;for(int k=0;k<2;k++){int n=k==0?ArraySize(previous):ArraySize(current);for(int i=0;i<n;i++){HG6JournalRow r;if(k==0)r=previous[i];else r=current[i];if(r.sequence<seq)return false;seq=r.sequence;if(r.type==HG6_J_RELEASE||r.type==HG6_J_EXTERNAL_RELEASE){if(r.generation<=ag||r.sequence<as)return false;ag=r.generation;as=r.sequence;}}}if(ArraySize(previous)>0){int n=ArraySize(previous);if(previous[n-1].type!=HG6_J_RELEASE&&previous[n-1].type!=HG6_J_EXTERNAL_RELEASE)return false;}return ag==anchor_generation&&as==anchor_sequence;}

};
#endif
