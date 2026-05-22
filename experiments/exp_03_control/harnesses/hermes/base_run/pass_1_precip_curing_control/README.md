# Exp 03 Control Base Pass 1: Precipitation/Curing Mechanism Search

This is the first non-reframed Hermes control pass for `exp_03_control`, run from a clean isolated Model C workspace.

## Run Summary

- Harness: Hermes Agent
- Branch: base/control
- Starting point: original Model C
- Prompt: `prompt/control_prompt.md`
- Local workspace snapshot: `_archive/2026-05-21__ed_fire_exp03_control_base_pass1_precip_curing`
- Final decision: retain original Model C

## Main Outcome

The agent explored three precipitation/curing-oriented mechanism families:

1. H1 annual humid suppression / precipitation upper limb
2. H2 wet-month logistic suppression
3. H3 seasonal contrast / curing gate

All candidates improved several weak regional scores, but none beat original Model C on official global ILAMB or clean public TRENDY/firepipe. The run is clean as a control artifact but was judged operationally premature as a ceiling search because it did not explore broader second-order or non-precipitation mechanism families.

## Key Scores

| Model | Official Overall | Public Overall | Decision |
|---|---:|---:|---|
| C0 original Model C | 0.671529 | 0.671274 | Retained |
| H1 annual humid suppression | 0.638442 | Not run | Rejected |
| H1m mild humid suppression | 0.653770 | Not run | Rejected |
| H2 wet-month logistic | 0.653397 | Not run | Rejected |
| H3 seasonal contrast | 0.665444 | 0.665210 | Rejected |

## Important Files

- Logs: `logs/`
- Candidate params: `model/`
- Candidate JSON/tables: `candidates/`, `artifacts/`
- Official ILAMB score outputs: `official_ilamb/`
- Clean public TRENDY/firepipe score outputs: `public_trendy/`
- Helper scripts written or used by the agent: `scripts/`
- Checksum manifest: `ARTIFACT_MANIFEST.sha256`

