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
| ED-p2f3-seed2 | Previous best / regional-broad alternate | Original Model C annual rate × annual wet-canopy suppressor × two arid fuel-continuity thresholds | 600 Optuna seeded search + ablations + official global/regional + public | 0.677073 | Broadest weak-region gains vs Model C; remaining BONA/AUST tradeoffs; no longer best global/public after continuation |
| ED-next-low-arid-warm-gate | Rejected | P2F3 low/soft arid threshold attenuated by warm-climate gate | 500 Optuna trials | not official (collapsed to identity proxy) | Rejected before official because optimum was effectively P2F3 |
| ED-next-coldrelax | Rejected | Cold continental climates relax a fraction of P2F3 suppression | 500 Optuna trials + official global/regional | 0.676930 | Slight BONA/BOAS help but below P2F3 globally; not enough |
| ED-next-curing | Serious mechanism | P2F3 × drying-phase curing enhancement from dbar tendency, precipitation concentration, and T_air | 500 Optuna trials | 0.684534 | Step global/AUST/spatial gain; preserves BONA/BOAS; erodes some P2F3 dryland/wet weak-region gains |
| ED-next-curing-scale-0p35 | Conservative ablation | Same curing mechanism at 0.35x amplitude | Deterministic amplitude scan | 0.680952 | More conservative; BONA preserved; smaller global gain; still weak drylands vs full P2F3 |
| ED-next-curing-scale-1p25 | Strong curing ablation | Same curing mechanism at 1.25x amplitude | Deterministic amplitude scan | 0.684994 | Highest pure-curing global; BONA/BOAS preserved; dryland/wet weak-region regressions grow |
| ED-next-curing-warmwet-nowarmgate | Rejected top-scalar | Curing enhancement plus ungated wet-month compensation | 700 Optuna + ablation | 0.688603 | Highest official/public scalar, but severe BONA/BOAS spatial damage; not acceptable final |
| ED-next-curing-warmwet | Rejected | Curing enhancement plus weak warm-gated wet-month compensation | 700 Optuna | 0.688292 | Strong global but BONA/BOAS damage remains |
| ED-next-curing-hotwet-1 | Accepted final balanced continuation | P2F3 × drying-phase curing enhancement × hot/warm-climate wet-month compensation | 700 Optuna + hotwet deterministic grid + official global/regional + public | 0.687626 | Beats P2F3 globally/publicly; preserves BONA/BOAS near P2F3; fixes AUST; improves TENA/EURO/NHAF/SHAF; regresses CEAM/MIDE/SEAS/EQAS vs P2F3 |

Final accepted continuation artifact:
- `runs/candidates/p2f3_curing_hotwet_final/params.json`
- `runs/candidates/p2f3_curing_hotwet_final/burntArea.nc`
- Source diagnostic artifact: `runs/candidates/next_curing_hotwet_grid_1/`
- Official global: `ilamb/output_candidates_curing_hotwet_global/scalar_database.csv`
- Official regional: `ilamb/output_regions_ED-next-curing-hotwet-1/scalar_database.csv`
- Public: `/Users/adithyasrinivasan/Projects/creativity-docs/trendy-v14-fire-benchmark-source/ilamb/output_with_ED-next-curing-hotwet-1/scalar_database.csv`

Important alternate artifacts:
- Broad regional/P2F3 alternate: `runs/candidates/p2f3_seed_current/`
- Highest scalar but rejected: `runs/candidates/next_curing_warmwet_no_warmgate_ablation/`
- Pure curing mechanism: `runs/candidates/next_curing_phase_opt500/`
- Pure curing amplitude scans: `runs/candidates/next_curing_phase_scale_*`
- New scripts: `scripts/search_p2f3_next.py`, `scripts/search_p2f3_curing_refine.py`
