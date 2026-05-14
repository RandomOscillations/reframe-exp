# Regional Analysis Pass 2

## Incumbent F3b remaining regional pattern

| Region | F3b Overall | Bias | RMSE | Seasonal | Spatial | Main issue |
|---|---:|---:|---:|---:|---:|---|
| euro | 0.376821 | 0.423902 | 0.280603 | 0.808049 | 0.090950 | Spatial and RMSE remain very low |
| ceam | 0.403003 | 0.374136 | 0.341767 | 0.843531 | 0.113815 | Spatial very low, amplitude still high |
| tena | 0.406672 | 0.483984 | 0.345280 | 0.691560 | 0.167254 | Spatial/RMSE/seasonal all weak |
| mide | 0.408459 | 0.486010 | 0.344764 | 0.761113 | 0.105643 | Spatial/RMSE weak despite arid limiter |
| seas | 0.509196 | 0.567961 | 0.404173 | 0.821611 | 0.348064 | Spatial/RMSE still low |
| aust | 0.670563 | 0.750721 | 0.655101 | 0.574376 | 0.717515 | Seasonal timing is main issue |
| bona | 0.777787 | 0.882768 | 0.741079 | 0.923853 | 0.600156 | High overall but spatial worsened vs baseline |
| nhsa | 0.602484 | 0.538300 | 0.500749 | 0.915313 | 0.557308 | Slight pass-1 tradeoff |

Pass-2 target:
- Do not undo F3b's amplitude gains.
- Test global seasonal synchronization / curing mechanisms that can shift or sharpen monthly fire timing using only current/antecedent allowed inputs.
- Prefer mechanisms that can improve AUST seasonal and weak-region RMSE without damaging EQAS gains or public rank.

## Loop 1: curing gate regional interpretation

P2F1 improved many weak-region Overalls by small amounts through Bias/RMSE/Seasonal improvements. It partially addressed timing in TENA/EURO and slightly improved EQAS/SEAS without erasing F3b's amplitude correction. However, the Spatial Distribution Score dropped globally and BONA lost additional spatial skill. AUST's seasonal score stayed near 0.574, so the monthly curing gate did not solve the principal Australian timing failure.

Interpretation: a global curing gate can make modest corrections but the optimizer keeps its amplitude small. This suggests Model C/F3b already encodes most of the globally useful monthly timing signal, while remaining spatial/timing errors require either a sharper but still physical conditional term or unavailable drivers.

## Loop 2: seasonal wet inhibition regional interpretation

P2F2 improved global Spatial and Seasonal scores, but the regional table showed a poor scientific trade:
- CEAM fell from 0.403003 to 0.398335.
- SHSA fell from 0.543078 to 0.535352.
- SEAS fell from 0.509196 to 0.507619.
- EQAS fell from 0.628943 to 0.619373.

The mechanism made high-rainfall inhibition too conditional on monthly rainfall. For places where persistent canopy/fuel moisture is the actual missing constraint, loosening the annual wet suppressor reintroduced pass-1 overprediction.

## Loop 3/final: two-threshold arid limiter regional interpretation

P2F3 improves the target dry/subtropical weak regions:

| Region | F3b | P2F3 | Delta | Interpretation |
|---|---:|---:|---:|---|
| TENA | 0.406672 | 0.414691 | +0.008019 | Improved dryland amplitude/RMSE; spatial still very low |
| EURO | 0.376821 | 0.385437 | +0.008616 | Improved bias/RMSE and slight spatial gain |
| MIDE | 0.408459 | 0.419018 | +0.010559 | Strongest dryland gain; desert cutoff improved |
| SHSA | 0.543078 | 0.545642 | +0.002564 | Slight amplitude/RMSE gain |
| SEAS | 0.509196 | 0.511484 | +0.002288 | Slight gain without losing F3b wet suppression |
| EQAS | 0.628943 | 0.629088 | +0.000145 | Essentially preserved |

Tradeoffs:
- BONA falls from 0.777787 to 0.771207, mainly spatial.
- AUST falls from 0.670563 to 0.667783; seasonal remains unresolved and even slightly lower.
- Global Spatial falls from 0.776393 to 0.772673, while Bias/RMSE/Seasonal improve.

Final regional judgement:
P2F3 is a defensible pass-2 improvement because it improves global score and several weak dryland regions with a coherent fuel-network mechanism. The cost is a modest spatial/BONA/AUST tradeoff. AUST seasonal failure remains unresolved under the current input contract; it likely needs vegetation/fuel type, lightning/ignition, land management, or submonthly monsoon timing not available here.
