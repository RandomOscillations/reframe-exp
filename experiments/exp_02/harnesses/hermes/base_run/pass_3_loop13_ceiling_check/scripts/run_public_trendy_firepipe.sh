#!/usr/bin/env bash
set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
BENCH="${TRENDY_BENCHMARK_ROOT:-/Users/adithyasrinivasan/Projects/creativity-docs/trendy-v14-fire-benchmark-source}"
MODEL_NAME="${MODEL_NAME:-ED-ModelC-formal-candidate}"
SRC="${SRC:-$REPO/ilamb/MODELS/ED-ModelC-final/burntArea.nc}"
OUT="${OUT:-$BENCH/ilamb/output_with_${MODEL_NAME}}"
export OUT

if [ ! -d "$BENCH" ]; then
  echo "FATAL: TRENDY benchmark root not found: $BENCH"
  exit 2
fi
if [ ! -f "$SRC" ]; then
  echo "FATAL: candidate burntArea.nc not found: $SRC"
  exit 2
fi

mkdir -p "$BENCH/ilamb/MODELS/$MODEL_NAME" "$OUT"
cp -f "$SRC" "$BENCH/ilamb/MODELS/$MODEL_NAME/burntArea.nc"

echo "Running public TRENDY/firepipe benchmark:"
echo "  benchmark:  $BENCH"
echo "  model:      $MODEL_NAME"
echo "  source:     $SRC"
echo "  copied to:  $BENCH/ilamb/MODELS/$MODEL_NAME/burntArea.nc"
echo "  build_dir:  $OUT"
echo

(
  cd "$BENCH"
  ILAMB_ROOT="$BENCH/ilamb" PATH="$BENCH/.venv/bin:$PATH" ilamb-run \
    --config ilamb/burntArea.cfg \
    --model_root ilamb/MODELS \
    --build_dir "$OUT" \
    --title "TRENDY v14 burntArea vs GFED4.1s + $MODEL_NAME"
)

echo
echo "Public benchmark score summary:"
python3 - <<'PY'
import os
from pathlib import Path

import pandas as pd

out = Path(os.environ["OUT"])
df = pd.read_csv(out / "scalar_database.csv")
metrics = [
    "Overall Score",
    "Bias Score",
    "RMSE Score",
    "Seasonal Cycle Score",
    "Spatial Distribution Score",
    "Period Mean (original grids)",
]
rows = []
for model in sorted(df["Model"].dropna().unique()):
    row = {"Model": model}
    for metric in metrics:
        r = df[(df["Model"] == model) & (df["Region"] == "global") & (df["ScalarName"] == metric)]["Data"]
        row[metric] = float(r.iloc[0]) if len(r) else None
    rows.append(row)
print(pd.DataFrame(rows).sort_values("Overall Score", ascending=False).to_string(index=False))
PY

