# Experiment 03: ED Fire Structural Reframe

This experiment is a clean structural-reframe run on the ED autoresearch Model C fire benchmark.

The harness starts from original Model C under the fixed input contract and asks whether a unified, mechanistic, interpretable burned-area formula can improve global benchmark behavior and regional fire behavior without using external inputs, region routing, coordinate hacks, per-cell lookup tables, or residual correction maps.

## Current Recorded Run

- Harness: Hermes Agent
- Run: `harnesses/hermes/reframe_run/pass_1_cand5_public_leader_and_pareto`
- Prompt: `prompts/reframe_prompt_draft.md`
- Local full-workspace archive: `/Users/adithyasrinivasan/Projects/creativity-docs/_archive/2026-05-21__ed_fire_exp03_hermes_reframe_cand5_public_leader_and_pareto_final/full_workspace`

## Headline Outcome

The run produced a stronger Pareto frontier rather than one candidate that dominates on every criterion.

- Public/global leader: `ED-Cand5Abl-no_edge_mix`
  - Official diagnostic global: `0.688648`
  - Clean public TRENDY/firepipe Overall: `0.679633`
  - Public rank: `#1`
- Balanced regional/global compromise: `ED-Cand5Sweep-edgefrac_0p50`
  - Official diagnostic global: `0.688490`
  - Clean public TRENDY/firepipe Overall: `0.679346`
  - Improves `12/14` named non-global regions versus original Model C and `11/14` versus Cand3.
- Strongest broad weak-region repair: `ED-Cand5-mosaic_edge_release`
  - Improves `13/14` named non-global regions versus original Model C.

The important scientific signal is the edge-mix counterfactual sweep: increasing edge/mosaic physics repairs humid and monsoon weak regions, while decreasing it recovers public/global score and strong-belt fidelity.
