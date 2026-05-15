# Regional Analysis

## Current best-so-far before loop 13

`ED-next-curing-hotwet-1` improved global/public scores and several regions relative to P2F3:
- Official global 0.687626; public 0.687405.
- BONA/BOAS preserved near P2F3: 0.769133 / 0.729333.
- AUST 0.681726, TENA 0.419723, EURO 0.404197, NHAF 0.683038, SHAF 0.689496.

Remaining weaknesses against P2F3:
- CEAM -0.009901, NHSA -0.021675, SHSA -0.028208, MIDE -0.026021, SEAS -0.007160, EQAS -0.007943.
- BONA still below original Model C (0.789806).
- Spatial scores remain low in TENA/EURO/MIDE/CEAM.

## Loop 13 regional diagnostics

### Arid curing attenuation

Hypothesis: MIDE/CEAM regressions might be caused by over-broad curing enhancement in high-deficit cells. Attenuating curing at high arid deficit improved official global and some dryland weak regions:
- `ED-loop13-aridatt` global 0.690378.
- TENA 0.443947 vs hotwet-1 0.419723.
- EURO 0.435917 vs 0.404197.
- MIDE 0.417546 vs 0.392997.

But this family caused unacceptable boreal and AUST losses:
- BONA 0.695631 vs hotwet-1 0.769133.
- BOAS 0.693656 vs hotwet-1 0.729333.
- AUST 0.677449 vs hotwet-1 0.681726.

Interpretation: high-deficit attenuation plus broader wet compensation improves dryland allocation and scalar scores, but the same global changes remove too much boreal fire. This is another manifestation of the wet-compensation failure mode.

### Boreal protection for wet compensation

Hypothesis: the high-scalar wet-compensation family can be made regionally acceptable by attenuating it in cold/high-temperature-amplitude climates.

Results:
- `ED-loop13-borealdiag`: BONA 0.751941 and BOAS 0.729618, better than high-scalar failures but still BONA below hotwet-1; global only 0.688133.
- `ED-loop13-aridboreal-5`: BONA 0.729587, BOAS 0.720784, global 0.690073. Protection partially restored boreal behavior relative to aridatt but did not recover hotwet-1 levels.

Interpretation: climate-derived boreal protection is physically plausible and partially works, but within tested bounds it cannot preserve BONA/BOAS while keeping the arid/global gains.

### Wet/productive curing attenuation

Hypothesis: South American and wet-tropical regressions may come from over-amplifying curing in productive wet regimes.

Result:
- `ED-loop13-wetprodatt` global 0.688892, public-relevant scalar gain.
- EQAS 0.624751, slightly above hotwet-1 0.621145, but most other regressions were not solved.
- BONA/BOAS were damaged (0.705924/0.703660).

Interpretation: wet/productivity attenuation has some signal for EQAS, but the searched family still follows the same broad-wet-compensation path that damages boreal regions.

### Combined family

`ED-loop13-combined` was the highest official and public scalar candidate:
- Official global 0.690564.
- Public 0.690353.
- Improves TENA 0.441782, EURO 0.434032, MIDE 0.411305, NHAF 0.685483, SHAF 0.694028.

But it fails the regional acceptance test:
- BONA 0.703762.
- BOAS 0.701550.
- CEAM 0.392152, below hotwet-1 and P2F3.
- SEAS 0.503258 and EQAS 0.617358, below hotwet-1/P2F3.
- AUST 0.681661, essentially tied/slightly below hotwet-1.

## Final regional judgement after loop 13

No loop 13 candidate is accepted as a balanced replacement. ED-next-curing-hotwet-1 remains best balanced because it is the best candidate that simultaneously:
- beats P2F3 by a step globally/publicly,
- preserves BONA/BOAS near P2F3,
- materially improves AUST,
- improves TENA/EURO/NHAF/SHAF,
- avoids the repeated boreal-collapse failure mode.

The highest scalar candidates (`ED-loop13-combined`, `ED-loop13-aridatt`, arid+boreal grids) show that an additional ~0.0027-0.003 official global gain is available, but only by damaging BONA/BOAS and weakening several hotwet/P2F3 regional gains. Therefore the empirical ceiling under the fixed input contract appears to be a tradeoff surface rather than a strictly better unified formula.
