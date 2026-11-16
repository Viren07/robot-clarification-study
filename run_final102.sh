#!/usr/bin/env bash
# The headline run: all five methods on the full 204-instruction dataset, with repeats.
#
# Test set   data/paired/final_102.json       204 items, 102 ambiguous + 102 clear, 34 pairs/group
# Calib set  data/paired/final_calib27.json    54 items, held out, no instruction shared
#
# ORDERED BY VALUE PER CREDIT, because the last attempt hit the credit wall mid-run. Each stage
# is useful on its own, so stopping between stages loses nothing:
#
#   stage 1  No Help + Binary + KnowNo r1 + LAP r1   the main result, one draw
#   stage 2  KnowNo and LAP repeats r2..r4           the noise-corrected mean, which is what
#                                                    makes the result reportable
#   stage 3  LofreeCP r1                             the expensive one, ~5,000 calls, and the
#                                                    method the dataset provably does not move
#
# Run a single stage with:  STAGE=1 bash run_final102.sh
# Default runs all three in order.
#
# What to expect. Four runs on the 54-pair version gave KnowNo a mean of 0.4167 with sd 0.0378.
# Combining that measured half with the screen's estimate of the new half predicts 0.4804 for
# the 204, with the interval still touching 0.50. The bar is 0.50, since a method that never
# asks scores exactly that.
set -e
D=data/paired/final_102.json
C=data/paired/final_calib27.json
CK=results/final_calib27__knowno_v3__gpt-4o-mini__truth-judge__calib.jsonl
STAGE="${STAGE:-all}"
T=referential,instrumental,parametric,spatial,sequential,preconditional

echo "########## 0  rebuild both halves so disk matches the pair modules ##########"
PAIR_TYPES=$T PAIR_GROUP_N=34 PAIR_OUT=final_102.json python src/build_paired.py
PAIR_SPLIT=calib PAIR_TYPES=$T PAIR_GROUP_N=9 PAIR_OUT=final_calib27.json python src/build_paired.py

if [ "$STAGE" = "all" ] || [ "$STAGE" = "1" ]; then
  echo "########## stage 1a  No Help + Binary (no calibration needed) ##########"
  python src/run_binary_nohelp.py --data "$D" --tag final102 --plan-steps

  echo "########## stage 1b  KnowNo r1, judge-labelled, matched calibration ##########"
  python src/run_knowno_v3.py --name final102 --truth judge --calib "$C" --data "$D"

  echo "########## stage 1c  LAP r1 (reuses KnowNo's generation) ##########"
  python src/run_lap.py --name final102 --variant super \
    --calib-data "$C" --test-data "$D" \
    --calib-knowno "$CK" \
    --test-knowno results/final102__knowno_v3__gpt-4o-mini__truth-judge__test.jsonl
fi

if [ "$STAGE" = "all" ] || [ "$STAGE" = "2" ]; then
  for i in 2 3 4; do
    echo "########## stage 2  repeat r$i  KnowNo ##########"
    python src/run_knowno_v3.py --name "final102_r$i" --truth judge --calib "$C" --data "$D"
    echo "########## stage 2  repeat r$i  LAP ##########"
    python src/run_lap.py --name "final102_r$i" --variant super \
      --calib-data "$C" --test-data "$D" \
      --calib-knowno "$CK" \
      --test-knowno "results/final102_r${i}__knowno_v3__gpt-4o-mini__truth-judge__test.jsonl"
  done
  echo "########## spread across repeats ##########"
  python src/report_repeats.py --prefix final102 --data data/paired/final_102.json
fi

if [ "$STAGE" = "all" ] || [ "$STAGE" = "3" ]; then
  echo "########## stage 3  LofreeCP r1 (the expensive one, ~5,000 calls) ##########"
  python src/run_lofreecp.py --name final102 --truth judge --calib "$C" --data "$D"
fi

echo
echo "The bar is 0.50. On the 54-pair version: KnowNo 0.4167, LAP 0.4491 (means of 4 runs)."
echo "For reference on AmbiK: No Help 0.50, Binary 0.52, KnowNo 0.53, LAP 0.55, LofreeCP 0.48."
