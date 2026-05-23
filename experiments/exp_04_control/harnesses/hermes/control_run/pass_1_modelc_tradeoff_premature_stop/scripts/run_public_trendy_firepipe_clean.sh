#!/usr/bin/env bash
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BENCH="${TRENDY_BENCHMARK_ROOT:-$REPO/public_benchmark_clean}"
MODEL_NAME="${MODEL_NAME:-ED-ModelC-candidate}"
SRC="${SRC:-$REPO/ilamb/MODELS/ED-ModelC-final/burntArea.nc}"
OUT="${OUT:-$BENCH/ilamb/output_with_${MODEL_NAME}}"
ILAMB_RUN="${ILAMB_RUN:-$REPO/.venv/bin/ilamb-run}"

if [[ ! -f "$SRC" ]]; then
  echo "candidate NetCDF not found: $SRC" >&2
  exit 2
fi

if [[ ! -d "$BENCH/ilamb/MODELS" ]]; then
  echo "clean benchmark root not found: $BENCH" >&2
  exit 2
fi

case "$BENCH" in
  "$REPO"/public_benchmark_clean|"$REPO"/public_benchmark_clean/*) ;;
  *)
    echo "Refusing to run against a non-local benchmark root: $BENCH" >&2
    echo "Use this script only with this workspace's isolated public_benchmark_clean directory." >&2
    exit 2
    ;;
esac

mkdir -p "$BENCH/ilamb/MODELS/$MODEL_NAME"
cp -f "$SRC" "$BENCH/ilamb/MODELS/$MODEL_NAME/burntArea.nc"
rm -rf "$OUT"

cd "$BENCH"
export ILAMB_ROOT="$BENCH/ilamb"
"$ILAMB_RUN" \
  --config ilamb/burntArea.cfg \
  --model_root ilamb/MODELS \
  --build_dir "$OUT" \
  --title "TRENDY v14 burntArea vs GFED4.1s"

echo "wrote $OUT"
