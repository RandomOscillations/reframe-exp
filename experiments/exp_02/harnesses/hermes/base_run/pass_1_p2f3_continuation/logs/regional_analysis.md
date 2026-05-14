# Regional Analysis

## Baseline failure pattern

Baseline `ED-ModelC-final` official regional ILAMB showed weak regions dominated by spatial/magnitude, not seasonal timing:
- TENA 0.381473, CEAM 0.376153, EURO 0.361128, MIDE 0.382769.
- SEAS 0.487193 and EQAS 0.507395 also weak, mostly spatial/bias/RMSE.
- Strong regions: BONA 0.789806, BOAS 0.728733, AUST 0.670219, CEAS 0.670499, NHAF/SHAF ~0.646.

## Early continuation lessons

Naive wet-temperature interaction improved many weak regions but severely damaged strong boreal spatial structure:
- BONA: 0.789806 -> 0.689878, spatial 0.654858 -> 0.127490.
- BOAS: 0.728733 -> 0.670265, spatial 0.767865 -> 0.286133.

BONA/BOAS therefore became an explicit design constraint: new mechanisms must keep weak-region gains without collapsing cold/boreal spatial patterns.

Warm-gated wet-temperature partially solved the boreal failure:
- `ED-warm-gate-c8`: BONA 0.786381 and BOAS 0.733066, but global Overall only 0.672605.

Annual wet-canopy suppression alone revealed useful weak-region signal:
- `ED-ann-wet`: EQAS 0.568840 vs baseline 0.507395; SEAS 0.504548 vs 0.487193.
- But global Overall was 0.671188, so annual wet suppression alone was not enough.

## Final accepted P2F3 regional behavior

`ED-p2f3-seed2` vs baseline:

| Region | Baseline Overall | P2F3 Overall | Delta | Interpretation |
| --- | ---: | ---: | ---: | --- |
| global | 0.671529 | 0.677073 | +0.005544 | Material global improvement |
| bona | 0.789806 | 0.771207 | -0.018599 | BONA tradeoff remains, but far smaller than wet-temp collapse |
| tena | 0.381473 | 0.414691 | +0.033218 | Major weak dryland gain |
| ceam | 0.376153 | 0.403716 | +0.027563 | Major weak-region gain |
| nhsa | 0.605824 | 0.606292 | +0.000468 | Preserved/slight gain |
| shsa | 0.507249 | 0.545642 | +0.038393 | Major gain |
| euro | 0.361128 | 0.385437 | +0.024309 | Weak-region gain |
| mide | 0.382769 | 0.419018 | +0.036249 | Major dryland gain |
| nhaf | 0.645855 | 0.653435 | +0.007580 | Gain |
| shaf | 0.646693 | 0.656661 | +0.009968 | Gain |
| boas | 0.728733 | 0.728730 | -0.000003 | BOAS preserved |
| ceas | 0.670499 | 0.679173 | +0.008674 | Gain |
| seas | 0.487193 | 0.511484 | +0.024291 | Weak-region gain |
| eqas | 0.507395 | 0.629088 | +0.121693 | Largest gain; annual wet-canopy/arid limiter fixes major bias/spatial issue |
| aust | 0.670219 | 0.667783 | -0.002436 | Slight loss; seasonal timing remains unresolved |

P2F3 improves 12 of 14 non-global regions materially or slightly, preserves BOAS, and keeps BONA loss far below the wet-temperature failure. Remaining tradeoffs: BONA spatial falls from 0.654858 to 0.566871; AUST seasonal falls from 0.579524 to 0.560839.

## Ablation regional interpretation

- `ED-p2f3-nolow2` global Overall 0.676981 and better global Spatial 0.777043. It improves BONA (0.776514 vs full 0.771207) and AUST (0.670770 vs full 0.667783), but gives weaker target dryland gains in TENA, EURO, MIDE and slightly lower global score.
- `ED-p2f3-nohigh2` global Overall 0.676040. It preserves BONA better but weakens TENA/MIDE and lowers global; high/desert threshold is therefore important.

Final regional judgement: full P2F3 is accepted because it gives the best global score and broad weak-region gains while only modestly damaging BONA/AUST. If strict parsimony/spatial preservation were prioritized, no-low P2F3 is a credible alternate.

## Remaining failures

- BONA still loses spatial skill under P2F3; this may require explicit boreal fuel/ignition/snow/lightning/management inputs not in the contract.
- AUST seasonal timing remains low and slightly worse; likely needs vegetation-specific curing, submonthly rainfall/ignition timing, or management information unavailable from monthly P/T/GPP/dbar.
- EURO/TENA/MIDE/CEAM spatial scores remain low even after gains, suggesting local land-use, cropland, fragmentation, suppression, and ignition drivers.
