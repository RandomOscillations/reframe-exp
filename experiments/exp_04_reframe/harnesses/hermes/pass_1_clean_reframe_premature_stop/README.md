# Pass 1: Clean Reframe Premature Stop

Final retained model: original Model C.

The agent completed a clean but shallow reframe pass:

- reproduced original Model C,
- ran official global ILAMB,
- ran official regional ILAMB,
- searched three simple mechanism families with Optuna,
- evaluated serious candidates with official global/regional ILAMB,
- ran clean public TRENDY/firepipe for the near-baseline candidate,
- wrote all required logs and `final_report.md`.

Main result:

- Original Model C official global Overall: `0.671529`
- Best near-candidate `ED-ModelC-curing_ratio-g700` official global Overall: `0.669741`
- `ED-ModelC-curing_ratio-g700` public TRENDY/firepipe Overall: `0.669487`
- Regenerated C0 public TRENDY/firepipe Overall: `0.671274`

Reason this pass is marked premature:

The prompt required repeated outer and inner loops and warned against treating one search as exhaustion. The agent only performed one substantive outer loop across `wet_firebreak`, `gpp_asym`, and `curing_ratio`, then concluded the empirical ceiling was reached. It did not carry the first-loop failures into deeper second-order combinations or additional structurally reframed mechanism families.

