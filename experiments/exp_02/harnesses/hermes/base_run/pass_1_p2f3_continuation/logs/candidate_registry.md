# Candidate Registry

| Candidate | Status | Formula change | Search | Official global Overall | Regional decision |
| --- | --- | --- | --- | ---: | --- |
| ED-ModelC-final | Baseline | Original Model C | Existing 2500-trial baseline; verified PASS | 0.671529 | Strong baseline but weak TENA/CEAM/EURO/MIDE/SEAS/EQAS |
| ED-wet-temp-grid | Rejected | Wet months raise ignition temperature threshold | 500 Optuna + grid | 0.674491 | Highest early global, but BONA and BOAS spatial collapse |
| ED-rain-pulse-grid | Rejected | Suppress anomalously rain-dominated months | 500 Optuna + grid | 0.671705 | Balanced but negligible gain |
| ED-warm-gate-c8 | Rejected | Wet-temperature shift gated by annual thermal regime | Targeted BONA/BOAS-preserving grid | 0.672605 | Preserves BONA/BOAS better, but global gain too small |
| ED-drymonth-norm | Rejected | Dry-month precipitation concentration gate | Distinct mechanism grid | 0.672018 | Some weak-region gains; global still small |
| ED-ann-wet | Rejected standalone | Persistent annual wet-canopy suppression | Distinct mechanism grid | 0.671188 | Big EQAS/SEAS gains but no global gain alone |
| ED-combo-warm-ann | Rejected | Warm-gated wet ignition + annual wet suppression | Combined grid | 0.672911 | Balanced but not material |
| ED-p2f3-opt2 | Rejected vs seed | Wet-canopy + two-threshold arid limiter, Optuna-refined | 600 Optuna trials | 0.676764 | Good, but below seed and worse several regional scores |
| ED-p2f3-nolow2 | Serious ablation | P2F3 without low/soft arid threshold | Deterministic ablation | 0.676981 | Better global Spatial and AUST/BONA than full, but weaker dryland target gains |
| ED-p2f3-nohigh2 | Rejected ablation | P2F3 without high/desert arid threshold | Deterministic ablation | 0.676040 | High threshold is important for best global/target behavior |
| ED-p2f3-seed2 | Accepted final | Original Model C annual rate × annual wet-canopy suppressor × two arid fuel-continuity thresholds | 600 Optuna seeded search + ablations + official global/regional + public | 0.677073 | Material global gain and broad weak-region improvements; BONA/AUST tradeoffs documented |

Final accepted artifact:
- `runs/candidates/p2f3_seed_current/params.json`
- `runs/candidates/p2f3_seed_current/burntArea.nc`
- Official global: `ilamb/output_candidates_p2f3_corrected_global/scalar_database.csv`
- Official regional: `ilamb/output_regions_ED-p2f3-seed2/scalar_database.csv`
- Public: `/Users/adithyasrinivasan/Projects/creativity-docs/trendy-v14-fire-benchmark-source/ilamb/output_with_ED-p2f3-current-final/scalar_database.csv`

Other continuation artifacts:
- `scripts/search_p2f3_continued.py`
- `runs/candidates/p2f3_optuna600_current/`
- `runs/candidates/p2f3_ablate_no_low_current/`
- `runs/candidates/p2f3_ablate_no_high_current/`
- `runs/candidates/warm_gate_c8_s5/`
- `runs/candidates/mech2_dry_month_norm/`
- `runs/candidates/mech2_ann_wet/`
- `runs/candidates/combo_warm_ann_1/`
