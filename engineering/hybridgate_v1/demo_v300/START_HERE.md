# Gold MUWHAHA Miner — HybridGate Demo v3.00

This is a new terminal integration from the preserved v2.06 strategy source and original model archive. The failed v2.07–v2.09 controller is not used. All 88 models are embedded in one MQ5.

**The delivered MQ5 is a source candidate, NOT a native-certified release.** Real-money trading is forbidden. Demo trading and Strategy Tester simulation are enabled by default when terminal/account permissions and broker compatibility permit.

## Actual single-file deliverable

[GoldMuwahahaMiner_HybridGate_Demo_v300.mq5 — MT5_EXPAND](https://drive.google.com/file/d/1an_MCs-ogqvGRzCgZJRXZsXD1bYGd1pX/view)

- Exact size: 94,127,324 bytes; Drive metadata size verified.
- SHA-256 of the assembled file: `4361dc87eff75c66c900530eba2bc1dc97efd6ba6a694d3d04dc185c6eaa96d3`.
- GitHub connector does not accept a local file reference for this large Git blob; the full assembled file is preserved in Drive, not committed as a Git blob. The small controller, standalone builder and complete model/readback receipt are here.
- Copy only the assembled MQ5 into the MT5 Experts directory. Open it in MetaEditor and compile; no separately installed header, model, resource, Python, or DLL is required. Do not compile the engineering controller fragment alone.

## Broker and operating conditions

XAUUSD, USD account, 100-ounce contract, cent price grid, 0.01-lot support, hedging, FOK, and compatible margin/stop-out facts. Demo uses the validated current broker clock offset and 120-minute requested warmup; historical warmup does not submit orders. Tester uses a fixed offset input, default zero; nonzero offset must match its historical clock. Original 2026–2028 frozen clock coverage is retained. A broker offset change requires a flat restart after validation. Original lot ladder remains optional and disabled by default.

Only one owned exposure at a time. A durable order intent precedes submission; an unresolved outcome is never resent blindly. Restart with a known owned exposure but no restored holding model triggers protective closure, not invented historical inference. Unknown/mismatched ownership or an unconfirmed order may require manual reconciliation. No software exit can be guaranteed during disconnection or unavailable market conditions.

## Independent reproducibility

From this branch's checkout, with the exact original Stage5 portable archive:
```powershell
py -3 engineering/hybridgate_v1/demo_v300/build_demo_v300.py --archive C:\HybridGate\assets\R9_HYBRIDGATE_V1_STAGE5_PORTABLE_ENGINEERING_20261125.zip --out C:\HybridGate\GoldMuwahahaMiner_HybridGate_Demo_v300.mq5
```

The source builder verifies 39 source pins, the original archive SHA-256 and 88 model hashes. It performs a complete readback of the embedded bank. See BUILD_RECEIPT.json. The host_test_source.py is retained as the actual test-source record with workspace-specific paths; it is not a portable Windows runbook or a native compiler test.

## Acceptance boundary

The host test completed 21/21 reference trades in both tester and simulated demo mode, recovered from one definitive order rejection with 20 completed trades, and refused a real-money account. The extended test had 440 proposals, 428 entries, 427 closures and 425 exact closed net matches. A burst scenario still completed 10 of 21 reference trades, with only 3 exact exits/net matches. No historical replay of stale entries. Native inference, all MetaEditor warnings, actual broker behavior, throughput, long-run trade parity and forward demo acceptance remain unverified. The prior supplied warning list informed explicit assignment-boundary type conversions and explicit Boolean comparisons; zero native warnings are not established.

Do not deploy on real funds or interpret mock fills as actual returns. No source strategy retraining, dataset reconstruction, or modifications to the protected v2.06 branch.
