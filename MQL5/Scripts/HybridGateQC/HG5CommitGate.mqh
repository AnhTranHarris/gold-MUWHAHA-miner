#ifndef HG5_COMMIT_GATE
#define HG5_COMMIT_GATE
// Portable transaction ordering gate. Persistence and digest readback supplied by adapter.
// Failure is latched; no new trading intent can be authorized by this class.
class HG5CommitGate {
 long generation,cursor,target;int phase;bool failed;
 public:
 HG5CommitGate(){generation=-1;cursor=target=0;phase=0;failed=false;}
 bool Restore(long gen,long cur,bool verified){if(generation!=-1||!verified||gen<0||cur<0){failed=true;return false;}generation=gen;cursor=cur;return true;}
 bool Begin(long gen,long cur){if(failed||generation<0||phase!=0||gen<=generation||gen-generation!=1||cur<=cursor){failed=true;return false;}target=cur;phase=1;return true;}
 bool JournalDurable(bool verified){if(failed||phase!=1||!verified){failed=true;return false;}phase=2;return true;}
 bool CheckpointDurable(bool verified){if(failed||phase!=2||!verified){failed=true;return false;}phase=3;return true;}
 bool CommitPublished(bool verified){if(failed||phase!=3||!verified){failed=true;return false;}generation++;cursor=target;phase=0;return true;}
 bool Healthy()const{return !failed&&generation>=0&&phase==0;}
 long Cursor()const{return cursor;}
};
#endif
