#!/usr/bin/env bash
# How much does the score move when NOTHING changes?
#
# Two runs of the same 18 group 3 pairs already gave 0.3889 and 0.4722 under an identical
# threshold, because the option generator writes different options each time even at
# temperature 0. That swing is as large as the binomial interval, so every single-run number
# in this repo carries an uncertainty it does not report. This measures it.
#
# Design: each repeat passes a different --name, so the TEST pass has no cache and regenerates
# from scratch. The --calib file is the same every time, and its cache path is keyed on the
# calibration file's stem rather than on --name, so the calibration pass is reused for free and
# qhat stays fixed at 0.838241. What is left is pure test-side generation noise, which is the
# quantity we want. Varying the calibration too would confound it with qhat movement.
#
# LAP is included because it costs almost nothing extra: it inherits each repeat's KnowNo
# generation and only adds its affordance calls. LofreeCP is left out on purpose, since it
# samples 20 times per item and already averages internally; add it later if KnowNo's spread
# turns out to matter.
#
# Cost per repeat: 108 generations + 108 judge calls for KnowNo, plus LAP's affordance calls.
set -e
D=data/paired/optionB_54.json
C=data/paired/optionB_calib27.json
CK=results/optionB_calib27__knowno_v3__gpt-4o-mini__truth-judge__calib.jsonl
REPEATS="${REPEATS:-3}"

if [ ! -f "$CK" ]; then
  echo "Calibration cache missing: $CK"
  echo "Run run_optionB.sh first, or this script will pay for the calibration pass each repeat."
  exit 1
fi

for i in $(seq 2 $((REPEATS + 1))); do
  echo "########## repeat r$i  KnowNo ##########"
  python src/run_knowno_v3.py --name "optionB54_r$i" --truth judge --calib "$C" --data "$D"

  echo "########## repeat r$i  LAP (reuses r$i's generation) ##########"
  python src/run_lap.py --name "optionB54_r$i" --variant super \
    --calib-data "$C" --test-data "$D" \
    --calib-knowno "$CK" \
    --test-knowno "results/optionB54_r${i}__knowno_v3__gpt-4o-mini__truth-judge__test.jsonl"
done

echo
echo "########## spread across repeats ##########"
python src/report_repeats.py
