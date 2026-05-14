#!/usr/bin/env bash
set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
CFG="${ILAMB_CFG:-$REPO/ilamb/burntArea_official.cfg}"
MODEL_ROOT="${MODEL_ROOT:-$REPO/ilamb/MODELS}"
MODEL_NAME="${MODEL_NAME:-ED-ModelC-final}"
OUT="${OUT:-$REPO/ilamb/output_regions_official}"
REGIONS="${REGIONS:-global bona tena ceam nhsa shsa euro mide nhaf shaf boas ceas seas eqas aust}"
export OUT

mkdir -p "$OUT"

echo "Running official regional ILAMB:"
echo "  config:     $CFG"
echo "  model_root: $MODEL_ROOT"
echo "  model:      $MODEL_NAME"
echo "  regions:    $REGIONS"
echo "  build_dir:  $OUT"
echo

ILAMB_ROOT="${ILAMB_ROOT:-$REPO/ilamb}" ilamb-run \
  --config "$CFG" \
  --model_root "$MODEL_ROOT" \
  --models "$MODEL_NAME" \
  --regions $REGIONS \
  --build_dir "$OUT"

echo
echo "Regional score summary:"
python3 - <<'PY'
import os
from pathlib import Path

import pandas as pd

out = Path(os.environ.get("OUT", ""))
if not out:
    out = Path("ilamb/output_regions_official")
csv = out / "scalar_database.csv"
df = pd.read_csv(csv)
metrics = [
    "Overall Score",
    "Bias Score",
    "RMSE Score",
    "Seasonal Cycle Score",
    "Spatial Distribution Score",
    "Period Mean (original grids)",
]
rows = []
for region in df["Region"].drop_duplicates():
    row = {"Region": region}
    for metric in metrics:
        r = df[(df["Region"] == region) & (df["ScalarName"] == metric)]["Data"]
        row[metric] = float(r.iloc[0]) if len(r) else None
    rows.append(row)
print(pd.DataFrame(rows).to_string(index=False))
PY

