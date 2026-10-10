#!/bin/zsh
# usage: gen.sh image|video MODEL OUTFILE LABEL [atlas args...]
# Estimates cost first, refuses if the ledger would exceed $25, then runs and logs.
kind=$1; model=$2; out=$3; label=$4; shift 4
A=${ATLAS_CLI:-atlas}
cd "${0:A:h}"
est=$($A generate cost $kind $model "$@" --json 2>/dev/null | python3 -c "import json,sys;print(json.load(sys.stdin)['price'])")
spent=$(awk -F'\t' '{s+=$3} END{printf "%.4f", s+0}' spend_ledger.tsv 2>/dev/null || echo 0)
python3 -c "import sys; sys.exit(0 if float('$spent')+float('$est')<=float('${ATLAS_BUDGET:-25}') else 1)" || { echo "BUDGET STOP: spent $spent + $est > 25"; exit 2; }
res=$($A generate $kind $model "$@" -o "$out" --overwrite --json 2>&1)
rc=$?
id=$(echo "$res" | python3 -c "import json,sys
try:
  d=json.load(sys.stdin); print(d.get('id') or d.get('prediction_id') or d.get('data',{}).get('id',''))
except Exception: print('')" 2>/dev/null)
if [ $rc -eq 0 ] && [ -f "$out" ]; then
  printf "%s\t%s\t%s\t%s\t%s\t%s\n" "$(date '+%F %T')" "$label" "$est" "$model" "$out" "$id" >> spend_ledger.tsv
  echo "OK $label \$$est -> $out (total now $(awk -F'\t' '{s+=$3} END{printf "%.3f", s}' spend_ledger.tsv))"
else
  echo "FAILED rc=$rc"; echo "$res" | tail -20
fi
