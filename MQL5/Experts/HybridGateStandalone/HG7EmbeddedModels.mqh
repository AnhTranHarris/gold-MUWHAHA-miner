#ifndef HG7_EMBEDDED_MODELS_MQH
#define HG7_EMBEDDED_MODELS_MQH
// Exact frozen HG5 model order; build_standalone.py verifies aliases and bytes.
// Resource variables are read-only; only the current model is copied to the
// existing parser, then released. The SHA-256 check precedes every Load().
#define HG7_BUILD_ID "HG7-embedded-699da4f68239b8029a9e61e272e650f90c365de5-v1"
#resource "\\Files\\HG7EM\\000.bin" as uchar HG7M000[] // 000_first_in_sample_entry_router
#resource "\\Files\\HG7EM\\001.bin" as uchar HG7M001[] // 001_rearm_in_sample_entry_router
#resource "\\Files\\HG7EM\\002.bin" as uchar HG7M002[] // 002_v15_rank1_hazard_IS
#resource "\\Files\\HG7EM\\003.bin" as uchar HG7M003[] // 003_v15_rank2_hazard_IS
#resource "\\Files\\HG7EM\\004.bin" as uchar HG7M004[] // 004_v15f_first_side_IS
#resource "\\Files\\HG7EM\\005.bin" as uchar HG7M005[] // 005_v15f_rearm_side_IS
#resource "\\Files\\HG7EM\\006.bin" as uchar HG7M006[] // 006_v16_event_hazard_0
#resource "\\Files\\HG7EM\\007.bin" as uchar HG7M007[] // 007_v16_event_hazard_1
#resource "\\Files\\HG7EM\\008.bin" as uchar HG7M008[] // 008_v16_event_side_IS
#resource "\\Files\\HG7EM\\009.bin" as uchar HG7M009[] // 009_v17_hazard_0
#resource "\\Files\\HG7EM\\010.bin" as uchar HG7M010[] // 010_v17_hazard_1
#resource "\\Files\\HG7EM\\011.bin" as uchar HG7M011[] // 011_v20_action_role0
#resource "\\Files\\HG7EM\\012.bin" as uchar HG7M012[] // 012_v20_action_role1
#resource "\\Files\\HG7EM\\013.bin" as uchar HG7M013[] // 013_v20_advantage_role0
#resource "\\Files\\HG7EM\\014.bin" as uchar HG7M014[] // 014_v20_advantage_role1
#resource "\\Files\\HG7EM\\015.bin" as uchar HG7M015[] // 015_v20_entry_confidence
#resource "\\Files\\HG7EM\\016.bin" as uchar HG7M016[] // 016_v22_wide
#resource "\\Files\\HG7EM\\017.bin" as uchar HG7M017[] // 017_v22_tight
#resource "\\Files\\HG7EM\\018.bin" as uchar HG7M018[] // 018_v22_marginal
#resource "\\Files\\HG7EM\\019.bin" as uchar HG7M019[] // 019_struct_gain
#resource "\\Files\\HG7EM\\020.bin" as uchar HG7M020[] // 020_struct_loss
#resource "\\Files\\HG7EM\\021.bin" as uchar HG7M021[] // 021_flip_gain
#resource "\\Files\\HG7EM\\022.bin" as uchar HG7M022[] // 022_flip_loss
#resource "\\Files\\HG7EM\\023.bin" as uchar HG7M023[] // 023_rg
#resource "\\Files\\HG7EM\\024.bin" as uchar HG7M024[] // 024_rl
#resource "\\Files\\HG7EM\\025.bin" as uchar HG7M025[] // 025_g
#resource "\\Files\\HG7EM\\026.bin" as uchar HG7M026[] // 026_l
#resource "\\Files\\HG7EM\\027.bin" as uchar HG7M027[] // 027_cont_gain
#resource "\\Files\\HG7EM\\028.bin" as uchar HG7M028[] // 028_cont_loss
#resource "\\Files\\HG7EM\\029.bin" as uchar HG7M029[] // 029_base_gain
#resource "\\Files\\HG7EM\\030.bin" as uchar HG7M030[] // 030_base_loss
#resource "\\Files\\HG7EM\\031.bin" as uchar HG7M031[] // 031_base_cont_gain
#resource "\\Files\\HG7EM\\032.bin" as uchar HG7M032[] // 032_base_cont_loss
#resource "\\Files\\HG7EM\\033.bin" as uchar HG7M033[] // 033_proxy_gain
#resource "\\Files\\HG7EM\\034.bin" as uchar HG7M034[] // 034_proxy_loss
#resource "\\Files\\HG7EM\\035.bin" as uchar HG7M035[] // 035_discount_gain
#resource "\\Files\\HG7EM\\036.bin" as uchar HG7M036[] // 036_discount_loss
#resource "\\Files\\HG7EM\\037.bin" as uchar HG7M037[] // 037_anchor_gain
#resource "\\Files\\HG7EM\\038.bin" as uchar HG7M038[] // 038_anchor_loss
#resource "\\Files\\HG7EM\\039.bin" as uchar HG7M039[] // 039_stack_gain
#resource "\\Files\\HG7EM\\040.bin" as uchar HG7M040[] // 040_stack_loss
#resource "\\Files\\HG7EM\\041.bin" as uchar HG7M041[] // 041_wide_15
#resource "\\Files\\HG7EM\\042.bin" as uchar HG7M042[] // 042_wide_30
#resource "\\Files\\HG7EM\\043.bin" as uchar HG7M043[] // 043_rev_g
#resource "\\Files\\HG7EM\\044.bin" as uchar HG7M044[] // 044_rev_l
#resource "\\Files\\HG7EM\\045.bin" as uchar HG7M045[] // 045_rev_w
#resource "\\Files\\HG7EM\\046.bin" as uchar HG7M046[] // 046_disc_g
#resource "\\Files\\HG7EM\\047.bin" as uchar HG7M047[] // 047_disc_l
#resource "\\Files\\HG7EM\\048.bin" as uchar HG7M048[] // 048_disc_w
#resource "\\Files\\HG7EM\\049.bin" as uchar HG7M049[] // 049_meta_g
#resource "\\Files\\HG7EM\\050.bin" as uchar HG7M050[] // 050_meta_l
#resource "\\Files\\HG7EM\\051.bin" as uchar HG7M051[] // 051_meta_w
#resource "\\Files\\HG7EM\\052.bin" as uchar HG7M052[] // 052_anchor_g
#resource "\\Files\\HG7EM\\053.bin" as uchar HG7M053[] // 053_anchor_l
#resource "\\Files\\HG7EM\\054.bin" as uchar HG7M054[] // 054_anchor_w
#resource "\\Files\\HG7EM\\055.bin" as uchar HG7M055[] // 055_option_g
#resource "\\Files\\HG7EM\\056.bin" as uchar HG7M056[] // 056_option_l
#resource "\\Files\\HG7EM\\057.bin" as uchar HG7M057[] // 057_option_w
#resource "\\Files\\HG7EM\\058.bin" as uchar HG7M058[] // 058_stack_g
#resource "\\Files\\HG7EM\\059.bin" as uchar HG7M059[] // 059_stack_l
#resource "\\Files\\HG7EM\\060.bin" as uchar HG7M060[] // 060_stack_w
#resource "\\Files\\HG7EM\\061.bin" as uchar HG7M061[] // 061_duration
#resource "\\Files\\HG7EM\\062.bin" as uchar HG7M062[] // 062_value
#resource "\\Files\\HG7EM\\063.bin" as uchar HG7M063[] // 063_duration_residual
#resource "\\Files\\HG7EM\\064.bin" as uchar HG7M064[] // 064_value_residual
#resource "\\Files\\HG7EM\\065.bin" as uchar HG7M065[] // 065_stack_duration
#resource "\\Files\\HG7EM\\066.bin" as uchar HG7M066[] // 066_stack_value
#resource "\\Files\\HG7EM\\067.bin" as uchar HG7M067[] // 067_micro_duration_residual
#resource "\\Files\\HG7EM\\068.bin" as uchar HG7M068[] // 068_micro_value_residual
#resource "\\Files\\HG7EM\\069.bin" as uchar HG7M069[] // 069_duration_residual_1
#resource "\\Files\\HG7EM\\070.bin" as uchar HG7M070[] // 070_value_residual_1
#resource "\\Files\\HG7EM\\071.bin" as uchar HG7M071[] // 071_duration_residual_2
#resource "\\Files\\HG7EM\\072.bin" as uchar HG7M072[] // 072_value_residual_2
#resource "\\Files\\HG7EM\\073.bin" as uchar HG7M073[] // 073_duration_residual_3
#resource "\\Files\\HG7EM\\074.bin" as uchar HG7M074[] // 074_value_residual_3
#resource "\\Files\\HG7EM\\075.bin" as uchar HG7M075[] // 075_duration_residual_4
#resource "\\Files\\HG7EM\\076.bin" as uchar HG7M076[] // 076_value_residual_4
#resource "\\Files\\HG7EM\\077.bin" as uchar HG7M077[] // 077_duration_residual_5
#resource "\\Files\\HG7EM\\078.bin" as uchar HG7M078[] // 078_continuation_gain
#resource "\\Files\\HG7EM\\079.bin" as uchar HG7M079[] // 079_continuation_risk
#resource "\\Files\\HG7EM\\080.bin" as uchar HG7M080[] // 080_exit_actor
#resource "\\Files\\HG7EM\\081.bin" as uchar HG7M081[] // 081_fill_premium
#resource "\\Files\\HG7EM\\082.bin" as uchar HG7M082[] // 082_future_gain
#resource "\\Files\\HG7EM\\083.bin" as uchar HG7M083[] // 083_local_downside
#resource "\\Files\\HG7EM\\084.bin" as uchar HG7M084[] // 085_actor_1_1
#resource "\\Files\\HG7EM\\085.bin" as uchar HG7M085[] // 086_renewal_gate
#resource "\\Files\\HG7EM\\086.bin" as uchar HG7M086[] // 087_precision_actor
#resource "\\Files\\HG7EM\\087.bin" as uchar HG7M087[] // 088_regret_head
bool HG7CopyVerified(const uchar &source[],const string expected,uchar &data[]){
 ArrayFree(data);
 int n=ArraySize(source);
 if(n<=0||n>67108864||ArrayResize(data,n)!=n)return false;
 if(ArrayCopy(data,source,0,0,n)!=n){ArrayFree(data);return false;}
 uchar key[],digest[];
 if(CryptEncode(CRYPT_HASH_SHA256,data,key,digest)!=32){ArrayFree(data);return false;}
 string hex="";for(int i=0;i<32;i++)hex+=StringFormat("%02x",(uint)digest[i]);
 if(hex!=expected){ArrayFree(data);return false;}
 return true;
}
bool HG7ReadEmbedded(const int index,const string expected,uchar &data[]){
 switch(index){
  case 0: return HG7CopyVerified(HG7M000,expected,data);
  case 1: return HG7CopyVerified(HG7M001,expected,data);
  case 2: return HG7CopyVerified(HG7M002,expected,data);
  case 3: return HG7CopyVerified(HG7M003,expected,data);
  case 4: return HG7CopyVerified(HG7M004,expected,data);
  case 5: return HG7CopyVerified(HG7M005,expected,data);
  case 6: return HG7CopyVerified(HG7M006,expected,data);
  case 7: return HG7CopyVerified(HG7M007,expected,data);
  case 8: return HG7CopyVerified(HG7M008,expected,data);
  case 9: return HG7CopyVerified(HG7M009,expected,data);
  case 10: return HG7CopyVerified(HG7M010,expected,data);
  case 11: return HG7CopyVerified(HG7M011,expected,data);
  case 12: return HG7CopyVerified(HG7M012,expected,data);
  case 13: return HG7CopyVerified(HG7M013,expected,data);
  case 14: return HG7CopyVerified(HG7M014,expected,data);
  case 15: return HG7CopyVerified(HG7M015,expected,data);
  case 16: return HG7CopyVerified(HG7M016,expected,data);
  case 17: return HG7CopyVerified(HG7M017,expected,data);
  case 18: return HG7CopyVerified(HG7M018,expected,data);
  case 19: return HG7CopyVerified(HG7M019,expected,data);
  case 20: return HG7CopyVerified(HG7M020,expected,data);
  case 21: return HG7CopyVerified(HG7M021,expected,data);
  case 22: return HG7CopyVerified(HG7M022,expected,data);
  case 23: return HG7CopyVerified(HG7M023,expected,data);
  case 24: return HG7CopyVerified(HG7M024,expected,data);
  case 25: return HG7CopyVerified(HG7M025,expected,data);
  case 26: return HG7CopyVerified(HG7M026,expected,data);
  case 27: return HG7CopyVerified(HG7M027,expected,data);
  case 28: return HG7CopyVerified(HG7M028,expected,data);
  case 29: return HG7CopyVerified(HG7M029,expected,data);
  case 30: return HG7CopyVerified(HG7M030,expected,data);
  case 31: return HG7CopyVerified(HG7M031,expected,data);
  case 32: return HG7CopyVerified(HG7M032,expected,data);
  case 33: return HG7CopyVerified(HG7M033,expected,data);
  case 34: return HG7CopyVerified(HG7M034,expected,data);
  case 35: return HG7CopyVerified(HG7M035,expected,data);
  case 36: return HG7CopyVerified(HG7M036,expected,data);
  case 37: return HG7CopyVerified(HG7M037,expected,data);
  case 38: return HG7CopyVerified(HG7M038,expected,data);
  case 39: return HG7CopyVerified(HG7M039,expected,data);
  case 40: return HG7CopyVerified(HG7M040,expected,data);
  case 41: return HG7CopyVerified(HG7M041,expected,data);
  case 42: return HG7CopyVerified(HG7M042,expected,data);
  case 43: return HG7CopyVerified(HG7M043,expected,data);
  case 44: return HG7CopyVerified(HG7M044,expected,data);
  case 45: return HG7CopyVerified(HG7M045,expected,data);
  case 46: return HG7CopyVerified(HG7M046,expected,data);
  case 47: return HG7CopyVerified(HG7M047,expected,data);
  case 48: return HG7CopyVerified(HG7M048,expected,data);
  case 49: return HG7CopyVerified(HG7M049,expected,data);
  case 50: return HG7CopyVerified(HG7M050,expected,data);
  case 51: return HG7CopyVerified(HG7M051,expected,data);
  case 52: return HG7CopyVerified(HG7M052,expected,data);
  case 53: return HG7CopyVerified(HG7M053,expected,data);
  case 54: return HG7CopyVerified(HG7M054,expected,data);
  case 55: return HG7CopyVerified(HG7M055,expected,data);
  case 56: return HG7CopyVerified(HG7M056,expected,data);
  case 57: return HG7CopyVerified(HG7M057,expected,data);
  case 58: return HG7CopyVerified(HG7M058,expected,data);
  case 59: return HG7CopyVerified(HG7M059,expected,data);
  case 60: return HG7CopyVerified(HG7M060,expected,data);
  case 61: return HG7CopyVerified(HG7M061,expected,data);
  case 62: return HG7CopyVerified(HG7M062,expected,data);
  case 63: return HG7CopyVerified(HG7M063,expected,data);
  case 64: return HG7CopyVerified(HG7M064,expected,data);
  case 65: return HG7CopyVerified(HG7M065,expected,data);
  case 66: return HG7CopyVerified(HG7M066,expected,data);
  case 67: return HG7CopyVerified(HG7M067,expected,data);
  case 68: return HG7CopyVerified(HG7M068,expected,data);
  case 69: return HG7CopyVerified(HG7M069,expected,data);
  case 70: return HG7CopyVerified(HG7M070,expected,data);
  case 71: return HG7CopyVerified(HG7M071,expected,data);
  case 72: return HG7CopyVerified(HG7M072,expected,data);
  case 73: return HG7CopyVerified(HG7M073,expected,data);
  case 74: return HG7CopyVerified(HG7M074,expected,data);
  case 75: return HG7CopyVerified(HG7M075,expected,data);
  case 76: return HG7CopyVerified(HG7M076,expected,data);
  case 77: return HG7CopyVerified(HG7M077,expected,data);
  case 78: return HG7CopyVerified(HG7M078,expected,data);
  case 79: return HG7CopyVerified(HG7M079,expected,data);
  case 80: return HG7CopyVerified(HG7M080,expected,data);
  case 81: return HG7CopyVerified(HG7M081,expected,data);
  case 82: return HG7CopyVerified(HG7M082,expected,data);
  case 83: return HG7CopyVerified(HG7M083,expected,data);
  case 84: return HG7CopyVerified(HG7M084,expected,data);
  case 85: return HG7CopyVerified(HG7M085,expected,data);
  case 86: return HG7CopyVerified(HG7M086,expected,data);
  case 87: return HG7CopyVerified(HG7M087,expected,data);
  default: ArrayFree(data);return false;
 }
}
#endif
