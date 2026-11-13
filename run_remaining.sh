#!/usr/bin/env bash
# The last two baselines: LAP and LofreeCP, on AmbiK and own100.
# Run from the project root in Git Bash. Stops at the first failure.
set -e

KN_AMBIK_CAL=results/ambik/knowno_v3/ambik_calib100_instructions__knowno_v3__gpt-4o-mini__calib.jsonl
KN_AMBIK_TST=results/ambik/knowno_v3/ambik100__knowno_v3__gpt-4o-mini__test.jsonl
KN_OWN_CAL=results/own100/knowno_v3/own_calib100_instructions__knowno_v3__gpt-4o-mini__calib.jsonl
KN_OWN_TST=results/own100/knowno_v3/own100__knowno_v3__gpt-4o-mini__test.jsonl

echo "=============== 1/4  LAP, AmbiK ==============="
python src/run_lap.py --name ambik100 --variant super \
  --calib-data data/ambik/ambik_calib100_instructions.json \
  --test-data  data/ambik/ambik_sample200_instructions.json --limit 100 \
  --calib-knowno "$KN_AMBIK_CAL" --test-knowno "$KN_AMBIK_TST"

echo "=============== 2/4  LAP, own100 ==============="
python src/run_lap.py --name own100 --variant super \
  --calib-data data/own100/own_calib100_instructions.json \
  --test-data  data/own100/own100_instructions.json \
  --calib-knowno "$KN_OWN_CAL" --test-knowno "$KN_OWN_TST"

echo "=============== 3/4  LofreeCP, AmbiK ==============="
python src/run_lofreecp.py --name ambik100 \
  --calib data/ambik/ambik_calib100_instructions.json \
  --data  data/ambik/ambik_sample200_instructions.json --limit 100

echo "=============== 4/4  LofreeCP, own100 ==============="
python src/run_lofreecp.py --name own100 \
  --calib data/own100/own_calib100_instructions.json \
  --data  data/own100/own100_instructions.json

python src/organize_results.py
echo
echo "Done. Both LAP summaries should say true_options_source=... truth_source=intent."
