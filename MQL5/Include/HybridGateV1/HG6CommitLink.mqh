#ifndef HG6_COMMIT_LINK_MQH
#define HG6_COMMIT_LINK_MQH
#include "HG5StateCodec.mqh"
// SECTION J1: bounded transaction watermark; no unbounded event history in memory.
// A broker outcome is persisted BEFORE the core applies it. A release is legal
// only after that sequence is in a verified core generation. Rescue is a separate
// durable quarantine domain, never eligible to resume ordinary admissions.
class HG6CommitLink {
 long released,min_generation;bool rescue;
 public:
 HG6CommitLink(){released=min_generation=0;rescue=false;}
 bool StateFields(HG5StateCodec &c){return c.I64(released)&&c.I64(min_generation)&&c.Flag(rescue)&&released>=0&&min_generation>=0&&(released==0||min_generation>0||rescue);}
 bool Check(long sequence,bool outstanding,bool resolved,long applied,long generation)const{
  if(rescue||sequence<0||applied<0||generation<min_generation||released>sequence)return false;
  if(!outstanding)return sequence==released&&applied==released;
  if(sequence!=released+1)return false;
  return applied==released||(resolved&&applied==sequence&&generation>min_generation);
 }
 bool Commit(long sequence,long applied,long generation){
  if(rescue||sequence!=released+1||sequence!=applied||generation<=min_generation)return false;
  released=sequence;min_generation=generation;return true;
 }
 void Quarantine(){rescue=true;}
 bool Rescue()const{return rescue;}
 bool RescueRelease(long sequence){if(!rescue||sequence!=released+1)return false;released=sequence;return true;}
};
#endif
