#!/usr/bin/env bash
# All five baselines on the 68-item paired pilot (34 clear + 34 ambiguous,
# preconditional and sequential, 17 pairs each).
#
# CALIBRATION CAVEAT: the conformal methods calibrate on own_calib100, which is NOT drawn from
# the same distribution as these 68 items. Conformal prediction guarantees coverage only within
# one distribution, so these three rows are EXPLORATORY until a matched calibration set exists.
# Reported anyway because the cut it produces (1 - qhat = 0.075) is the one the screen assumed,
# so this is the direct test of the screen's 0.3382 prediction.
# The calibration passes are already cached, so only the 68 test items cost anything.
set -e
D=data/paired/paired_pilot68.json

echo "########## 1/4  No Help + Binary, one plan step  (no calibration needed) ##########"
python src/run_binary_nohelp.py --data "$D" --tag pilot68 --plan-steps

echo "########## 2/4  KnowNo, judge-labelled ##########"
python src/run_knowno_v3.py --name pilot68 --truth judge \
  --calib data/own100/own_calib100_instructions.json --data "$D"

echo "########## 3/4  LAP (reuses the KnowNo generation and probabilities) ##########"
python src/run_lap.py --name pilot68 --variant super \
  --calib-data data/own100/own_calib100_instructions.json --test-data "$D" \
  --calib-knowno results/own100/knowno_v3/own_calib100_instructions__knowno_v3__gpt-4o-mini__truth-judge__calib.jsonl \
  --test-knowno  results/pilot68__knowno_v3__gpt-4o-mini__truth-judge__test.jsonl

echo "########## 4/4  LofreeCP, judge-labelled ##########"
python src/run_lofreecp.py --name pilot68 --truth judge \
  --calib data/own100/own_calib100_instructions.json --data "$D"

python src/organize_results.py
echo
echo "Done. Compare each row against AmbiK: No Help 0.50, Binary 0.53, KnowNo 0.53, LAP 0.55, LofreeCP 0.48."
