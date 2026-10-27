#property strict
#property version "0.1"
#property description "R38 Coinexx/Dukascopy demo-only quote recorder, research shadow: NO TRADING"
#include "R38_DemoShadowTickTap.mqh"
input string InpBroker="coinexx";
input string InpLogName="R38_MDK01_DEMO_SHADOW_QUOTES.jsonl";
CR38DemoShadowTickTap gTap;
int OnInit()
  {
   if(!gTap.Start(InpBroker,_Symbol,InpLogName))return INIT_FAILED;
   EventSetMillisecondTimer(250);
   return INIT_SUCCEEDED;
  }
void OnTick(){gTap.ObserveTicks();}
void OnTimer(){gTap.ObserveTicks();}
void OnDeinit(const int reason){EventKillTimer();gTap.Stop();}
// DEMO QUOTE LOGGER ONLY. To capture actual source R00 candidate intents, the
// existing EA must call gTap.RecordIntent() at the true pre-OrderSend boundary.
// This standalone logger does NOT generate intents, submit trades, or authorize vetoes.
