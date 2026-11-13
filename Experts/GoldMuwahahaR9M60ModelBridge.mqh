#ifndef __GMM_R9_M60_155_SCORE_BRIDGE_MQH__
#define __GMM_R9_M60_155_SCORE_BRIDGE_MQH__
// R9 v1.94 — exact 155-feature archived LightGBM score consumption.
// Native EA does NOT reconstruct or fabricate the 155 feature vector.
// External scorer must apply frozen source-order feature contract, producing
// one quote/side-exact packet from a PAST-ONLY source (not future labels).
// File checks are nonblocking and default to SHADOW; never imply OOS P&L.
//
// Packet (single CSV record, comma delimiter, UTF-8/ANSI ASCII only):
// R9M60_155_V1,login,symbol,magic,time_msc,bid_cents,ask_cents,side,
// 155,model_sha256,model_id,feature_end_msc,source_ordinal,
// score,status,schema_id
// Authoritative protocol: research/.../m60_155_integration/README.md.

long g_r9M60Qualified=0;
long g_r9M60Matched=0;
long g_r9M60Missing=0;
long g_r9M60Rejected=0;
double g_r9M60ScoreSum=0.0;

string R9M60PacketPath()
{
   return StringFormat("R9_M60_155_%s_%I64d_%I64u.csv",
                       _Symbol,AccountInfoInteger(ACCOUNT_LOGIN),InpMagic);
}
bool R9M60GetScore(const MqlTick &tick,const int side,double &score)
{
   score=0.0;
   if(InpR9M60Mode==0) return false;
   if(!FileIsExist(R9M60PacketPath(),FILE_COMMON)) return false;
   const int fh=FileOpen(R9M60PacketPath(),
                         FILE_READ|FILE_CSV|FILE_ANSI|FILE_COMMON|
                         FILE_SHARE_READ|FILE_SHARE_WRITE,',');
   if(fh==INVALID_HANDLE) return false;
   // Reading all fields before accepting prevents partially published packets
   // from generating trades. The producer must atomically replace this file.
   const string tag=FileReadString(fh);
   const string login=FileReadString(fh);
   const string symbol=FileReadString(fh);
   const string magic=FileReadString(fh);
   const string stamp=FileReadString(fh);
   const string bid=FileReadString(fh);
   const string ask=FileReadString(fh);
   const string packetSide=FileReadString(fh);
   const string dimensions=FileReadString(fh);
   const string modelHash=FileReadString(fh);
   const string modelId=FileReadString(fh);
   const string featureEnd=FileReadString(fh);
   const string sourceOrdinal=FileReadString(fh);
   const string probability=FileReadString(fh);
   const string status=FileReadString(fh);
   const string schemaId=FileReadString(fh);
   const bool hasTail=!FileIsEnding(fh);
   FileClose(fh);
   if(hasTail || tag!="R9M60_155_V1" || symbol!=_Symbol ||
      schemaId!="R9_M60_155_20261113_V1" ||
      status!="ASOF_PINNED" ||
      StringToInteger(login)!=AccountInfoInteger(ACCOUNT_LOGIN) ||
      StringToInteger(magic)!=(long)InpMagic ||
      StringToInteger(stamp)!=(long)tick.time_msc ||
      StringToInteger(bid)!=(long)MathRound(tick.bid*100.0) ||
      StringToInteger(ask)!=(long)MathRound(tick.ask*100.0) ||
      StringToInteger(packetSide)!=(long)side ||
      StringToInteger(dimensions)!=155 ||
      StringToInteger(featureEnd)!=(long)tick.time_msc ||
      StringToInteger(sourceOrdinal)<=0 ||
      modelHash!=InpR9M60ExpectedModelSha ||
      StringLen(modelId)<4 || StringLen(probability)<1)
      return false;
   const double value=StringToDouble(probability);
   if(!MathIsValidNumber(value) || value<0.0 || value>1.0) return false;
   score=value;
   return true;
}
bool R9M60PermitOriginalEntry(const MqlTick &tick,const int side)
{
   if(InpR9M60Mode==0) return true;
   ++g_r9M60Qualified;
   double score=0.0;
   if(!R9M60GetScore(tick,side,score))
   {
      ++g_r9M60Missing;
      // SHADOW: no change to R9 fills. FILTER: fail closed, no fake score.
      return (InpR9M60Mode==1);
   }
   ++g_r9M60Matched;
   g_r9M60ScoreSum+=score;
   if(InpR9M60Mode==1) return true;
   if(score+1e-12<InpR9M60MinProbability)
   {
      ++g_r9M60Rejected;
      return false;
   }
   return true;
}
void R9M60ReportStats()
{
   if(InpR9M60Mode==0) return;
   PrintFormat("GM_R9: MODEL155 mode=%d qualified=%I64d exact_matches=%I64d missing_or_mismatch=%I64d model_veto=%I64d mean_score=%.6f",
               InpR9M60Mode,g_r9M60Qualified,g_r9M60Matched,
               g_r9M60Missing,g_r9M60Rejected,
               g_r9M60Matched>0?g_r9M60ScoreSum/(double)g_r9M60Matched:0.0);
}
#endif
