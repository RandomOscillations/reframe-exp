# Regional Analysis

## Baseline and P2F3 context

Original Model C official regional ILAMB showed weak regions dominated by spatial/magnitude, not seasonal timing:
- TENA 0.381473, CEAM 0.376153, EURO 0.361128, MIDE 0.382769.
- SEAS 0.487193 and EQAS 0.507395 also weak.
- Strong regions included BONA 0.789806, BOAS 0.728733, AUST 0.670219, CEAS 0.670499, NHAF/SHAF ~0.646.

P2F3 (`ED-p2f3-seed2`) became the previous best-so-far:
- Global Overall 0.677073; public 0.676846.
- Broad weak-region gains vs Model C: TENA +0.033218, CEAM +0.027563, SHSA +0.038393, EURO +0.024309, MIDE +0.036249, SEAS +0.024291, EQAS +0.121693.
- Remaining issues: BONA Overall -0.018599 vs Model C, AUST slight loss and weak seasonality, and low spatial scores in TENA/CEAM/EURO/MIDE.

## New continuation regional results

### Cold/low-arid relaxation

Cold continental relax improved BONA vs P2F3 (0.777749 vs 0.771207) and BOAS (0.730364 vs 0.728730), but global Overall was 0.676930, below P2F3. This showed the BONA spatial issue could be partially relieved by climate-derived gates, but the mechanism did not buy enough global or weak-region performance.

### Curing-phase enhancement

Pure curing phase (`ED-next-curing`) produced a large global step: 0.684534. It preserved BONA (0.771410) and BOAS (0.728402) near P2F3 and materially improved AUST (0.678597), NHAF (0.676733), and SHAF (0.681162). It also raised global Spatial to 0.797406.

Tradeoff: it eroded P2F3 gains in several weak regions: TENA 0.401813, CEAM 0.393015, EURO 0.372465, MIDE 0.397982, SEAS 0.499428, EQAS 0.615726. These mostly remain above original Model C, but below P2F3.

Curing amplitude scan:
- 0.35x: global 0.680952, more conservative; BONA/BOAS preserved; smaller AUST/NHAF/SHAF gains.
- 1.0x: global 0.684534.
- 1.25x: global 0.684994, but weak-region regressions grow; no clear regional justification for pushing amplitude further.

### Curing plus wet-month compensation

Ungated/weakly gated warmwet variants achieved the highest global scores but reintroduced the earlier wet-suppression failure mode:
- `ED-next-curing-warmwet-nowarmgate`: global 0.688603 and public 0.688384, but BONA 0.702599 and BOAS 0.701577. Rejected as a scalar overfit/tradeoff.
- `ED-next-curing-warmwet`: global 0.688292, but BONA 0.730040 and BOAS 0.721548. Rejected as still too damaging.

Hot/warm-gated grid improved this tradeoff. The accepted balanced model is `ED-next-curing-hotwet-1`:
- Global 0.687626 vs P2F3 0.677073 (+0.010553).
- Public 0.687405 vs P2F3 0.676846 (+0.010559).
- BONA 0.769133 vs P2F3 0.771207 (-0.002074), no spatial collapse.
- BOAS 0.729333 vs P2F3 0.728730 (+0.000603).
- AUST 0.681726 vs P2F3 0.667783 (+0.013943), Seasonal +0.027789 and Spatial +0.039177.
- TENA 0.419723 vs P2F3 0.414691 (+0.005032).
- EURO 0.404197 vs P2F3 0.385437 (+0.018760).
- NHAF/SHAF large gains (+0.029603/+0.032835), mostly from spatial improvements.

Regressions vs P2F3:
- CEAM -0.009901, NHSA -0.021675, SHSA -0.028208, MIDE -0.026021, SEAS -0.007160, EQAS -0.007943.
- Most of these remain above original Model C except NHSA/SHSA relative to their original baselines; MIDE remains above Model C but loses much of the P2F3 increment.

## Final regional judgement

There is no strict region-by-region dominance over P2F3. P2F3 remains the broadest weak-region-improvement model, especially for MIDE/CEAM/EQAS and South America. However, `ED-next-curing-hotwet-1` is the best balanced continuation model because it:
- produces a step global/public improvement over P2F3,
- improves all global components, especially Spatial and Seasonal,
- materially improves the previously unresolved AUST seasonality problem,
- preserves BONA/BOAS near P2F3 rather than repeating wet-temperature collapse,
- improves TENA and EURO weak regions beyond P2F3,
- gives large NHAF/SHAF spatial gains.

The remaining unresolved failures are now sharper:
- MIDE/CEAM/TENA/EURO spatial scores remain low even when Overall improves, suggesting missing land-use, cropland, suppression, ignition, or fragmentation inputs.
- South American regressions under curing indicate the allowed monthly climate/GPP variables cannot robustly distinguish productive burning from over-broad curing amplification.
- BONA remains below original Model C; full recovery likely needs boreal ignition/snow/lightning/fuel-structure information unavailable under the fixed contract.
