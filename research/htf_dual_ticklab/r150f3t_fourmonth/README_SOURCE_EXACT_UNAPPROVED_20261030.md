# F401-R150F3T FOUR-MONTH EXPOSED RESEARCH — UNAPPROVED

Research continuation directly from R150F2 parent commit 51d416925fa941ee4f3a7ae407e46f9a5f9b3afb. R148B decisions frozen. PRIMARY read only and MT5_EXPAND /02 untouched. No G01–G09 cleared; M-DK-01 OPEN; 21/39 owner-approved historical research objectives.

Completed source-exact sample-limited training: 64,000 original R148B-vetoed events, eight Coinexx/Dukascopy Jan/Feb/June/July cells, 8,000/cell. Each broker's final source-only T0 fitted on all its four months (32,000 events). BayesianGaussianMixture state is a cross-sectional posterior on 23 original native quote-prefix features, not temporal BOCPD and not native R120 250ms–H1 geometry. Separate original CORRECT/OPPOSITE/NEUTRAL versus hypothetical action-time L1 FAVORABLE/ADVERSE/CENSORED training labels. No real LIMIT fills, no executable economics.

Hindsight teacher guided training only through historical original FILTER08 continuous-score July weights (7,786 Coinexx; 7,320 Dukascopy). No teacher source was available in January, February or June; these were not fabricated. The teacher, original class and future quote values are not inputs to runtime T0. Historical full source months are research-exposed.

Coinexx block original-class AUC base 0.596617, teacher-guided 0.599814; AP falls 0.029227 to 0.027205. Dukascopy AUC 0.581646 to 0.591174; AP falls 0.024191 to 0.023785. Bayesian GMM ablation mixed (CX .597912 to .593174 worse; DK .569908 to .581161 improved). One-shot 60%-FIT/15%-CAL/25%-TEST empirical NP cutoff with 60-second embargo and <=0.5 bad per correct rescues chooses ABSTAIN in both brokers. No rescued events, no approved filter change. 9/9 causal/runtime tests passed.

FULL EXECUTABLE SOURCE, MODEL WEIGHTS, SCORED SAMPLE MASKS, TESTS AND SHA MANIFEST: MT5_EXPAND /01 https://drive.google.com/file/d/1kN0jYNrGo2mgIpt1XiKQ7w5yFnDqhZqp/view , ZIP SHA256 b33662623f87e1930270954b4e21b7f1aa838a6c6dcd16f3c417b03f0af4e3d9, size 2,399,682, 30 members CRC and 29/29 member SHA passed.

FULL SCIENTIFIC REPORT: MT5_EXPAND /00 https://drive.google.com/file/d/1HG4ARQXaMVvsXK-0VjyzskCIN-fzCXt1/view , SHA256 38746b3e9f242c470bf095df95585f8585146a8d6ac23a0cb7ea16afe2ec46e0.

Original R148B input ZIP SHA256 5fd66ba3394b66160f0a951fbfd1a743b2511c4a164b5f947f8e10b95fb67554; original R150F2 ZIP SHA256 ed47b107c032ebff65436eb8844614e76b59c524721c270f11964f91cf221114.

SCOPED RESULT / NEXT UNRUN: F401-R150F3 full original-tape native tick build requires eight authorized raw quote tapes and existing R120/R147 250ms/500ms/1s/5s/15s/30s + completed M1/M5/M15/H1 state, real never-submitted LIMIT order intent and fill/expiry uncertainty before any temporal BOCPD + selective classwise NP / absolute-utility router. DO NOT present the 64k sample as the full 2,574,251 source population or hypothetical L1 marks as fills. No R150D/E/F1/F2 repetition. Original system not rebuilt. R148B stays active.
