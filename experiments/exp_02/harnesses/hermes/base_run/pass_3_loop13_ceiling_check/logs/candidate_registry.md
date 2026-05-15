# Candidate Registry

| Candidate | Status | Formula change | Search | Official global Overall | Regional decision |
| --- | --- | --- | --- | ---: | --- |
| ED-ModelC-final | Baseline | Original Model C | Existing 2500-trial baseline; verified PASS | 0.671529 | Strong baseline but weak TENA/CEAM/EURO/MIDE/SEAS/EQAS |
| ED-p2f3-seed2 | Regional-broad alternate | Original Model C annual rate × annual wet-canopy suppressor × two arid fuel-continuity thresholds | 600 Optuna seeded search + ablations + official global/regional + public | 0.677073 | Broadest weak-region gains vs Model C; BONA/AUST tradeoffs; no longer best global/public |
| ED-next-curing-hotwet-1 | Accepted final balanced model | P2F3 × drying-phase curing enhancement × hot/warm-climate wet-month compensation | 700 Optuna + hotwet deterministic grid + official global/regional + public | 0.687626 | Best balanced model: step over P2F3, preserves BONA/BOAS near P2F3, fixes AUST, improves TENA/EURO/NHAF/SHAF; some P2F3 weak-region regressions |
| ED-next-curing-warmwet-nowarmgate | Rejected high scalar | Curing enhancement plus ungated wet-month compensation | 700 Optuna + ablation + public | 0.688603 | Higher scalar than hotwet-1 but severe BONA/BOAS spatial damage |
| ED-loop13-borealprotect | Rejected | High wet compensation with cold/high-amplitude protection | 500 Optuna + official regional | 0.688726 | Global gain over hotwet-1 small; BONA/BOAS still damaged (0.699840/0.698280) |
| ED-loop13-wetprodatt | Rejected | Attenuate curing in wet/productive regimes | 500 Optuna + official regional | 0.688892 | Slight scalar gain; BONA/BOAS damaged; no broad regional recovery |
| ED-loop13-aridatt | Rejected high scalar/public | Attenuate curing in high arid-deficit regimes while broadening wet compensation | 500 Optuna + official global/regional + public | 0.690378 | Improves TENA/EURO/MIDE and public 0.690170, but BONA/BOAS collapse (0.695631/0.693656) and AUST regresses |
| ED-loop13-combined | Rejected highest scalar/public | Combined boreal protection, arid curing attenuation, wet-climate curing attenuation | 300 Optuna after timeout + official global/regional + public | 0.690564 | Highest official/public scalar (public 0.690353), but BONA/BOAS collapse (0.703762/0.701550); rejected |
| ED-loop13-aridboreal-5 | Rejected partial recovery | Arid curing attenuation + deterministic boreal protection | Deterministic grid + official global/regional + public | 0.690073 | Partial BONA/BOAS recovery vs aridatt, but still below hotwet-1 and worsens AUST/CEAM/SEAS/EQAS; not balanced |
| ED-loop13-borealdiag | Rejected marginal | High wet compensation with stronger boreal protection diagnostic | Deterministic diagnostic + official global/regional | 0.688133 | BOAS preserved and BONA better than high-scalar failures, but global gain is tiny and BONA remains below hotwet-1 |

Older rejected mechanisms are documented in prior versions and `research_log.md`: wet-temperature, rain-pulse, warm-gated wet-temperature, annual wet, dry-month, P2F3 no-low/no-high, cold-relax, pure curing, and curing ablations.

Final accepted balanced artifact remains:
- `runs/candidates/p2f3_curing_hotwet_final/params.json`
- `runs/candidates/p2f3_curing_hotwet_final/burntArea.nc`
- Official global: `ilamb/output_candidates_curing_hotwet_global/scalar_database.csv`
- Official regional: `ilamb/output_regions_ED-next-curing-hotwet-1/scalar_database.csv`
- Public: `/Users/adithyasrinivasan/Projects/creativity-docs/trendy-v14-fire-benchmark-source/ilamb/output_with_ED-next-curing-hotwet-1/scalar_database.csv`

Highest scalar/public rejected artifact:
- `runs/candidates/loop13_combined_protect_attenuate_opt300/params.json`
- `runs/candidates/loop13_combined_protect_attenuate_opt300/burntArea.nc`
- Official global: `ilamb/output_candidates_loop13_global/scalar_database.csv`
- Official regional: `ilamb/output_regions_ED-loop13-combined/scalar_database.csv`
- Public: `/Users/adithyasrinivasan/Projects/creativity-docs/trendy-v14-fire-benchmark-source/ilamb/output_with_ED-loop13-combined/scalar_database.csv`

Other loop 13 artifacts:
- `scripts/search_hotwet_next.py`
- `runs/candidates/loop13_arid_curing_attenuation_opt500/`
- `runs/candidates/loop13_wet_productivity_curing_attenuation_opt500/`
- `runs/candidates/loop13_boreal_protected_wetcomp_opt500/`
- `runs/candidates/loop13_arid_boreal_grid_*/`
