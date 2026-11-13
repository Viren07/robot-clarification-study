#!/usr/bin/env bash
# Makes all five baselines comparable and properly reported.
# Run from the project root in Git Bash. Stops at the first failure.
set -e

KN_A_CAL=results/ambik/knowno_v3/ambik_calib100_instructions__knowno_v3__gpt-4o-mini__calib.jsonl
KN_A_TST=results/ambik/knowno_v3/ambik100__knowno_v3__gpt-4o-mini__test.jsonl
KN_O_CAL=results/own100/knowno_v3/own_calib100_instructions__knowno_v3__gpt-4o-mini__calib.jsonl
KN_O_TST=results/own100/knowno_v3/own100__knowno_v3__gpt-4o-mini__test.jsonl

echo "########## 1/6  Binary on one plan step, AmbiK   (PAID, ~100 calls) ##########"
python src/run_binary_nohelp.py --data data/ambik/ambik_sample200_instructions.json \
  --limit 100 --tag ambik_sample200 --plan-steps

echo "########## 2/6  Binary on one plan step, own100  (PAID, ~100 calls) ##########"
python src/run_binary_nohelp.py --data data/own100/own100_instructions.json \
  --tag own100 --plan-steps

echo "########## 3/6  LofreeCP judge-labelled, AmbiK   (PAID, fresh sampling + judge) ##########"
python src/run_lofreecp.py --name ambik100 --truth judge \
  --calib data/ambik/ambik_calib100_instructions.json \
  --data  data/ambik/ambik_sample200_instructions.json --limit 100

echo "########## 4/6  LofreeCP judge-labelled, own100  (PAID) ##########"
python src/run_lofreecp.py --name own100 --truth judge \
  --calib data/own100/own_calib100_instructions.json \
  --data  data/own100/own100_instructions.json

echo "########## 5/6  LAP resummarised with the new diagnostics, both  (FREE) ##########"
python src/run_lap.py --name ambik100 --variant super \
  --calib-data data/ambik/ambik_calib100_instructions.json \
  --test-data  data/ambik/ambik_sample200_instructions.json --limit 100 \
  --calib-knowno "$KN_A_CAL" --test-knowno "$KN_A_TST"
python src/run_lap.py --name own100 --variant super \
  --calib-data data/own100/own_calib100_instructions.json \
  --test-data  data/own100/own100_instructions.json \
  --calib-knowno "$KN_O_CAL" --test-knowno "$KN_O_TST"

echo "########## 6/6  file everything ##########"
python src/organize_results.py
echo
echo "Done. Check: Binary summaries say scored_unit='one plan step';"
echo "the judge LofreeCP summaries say prediction_set_collapsed=false."
