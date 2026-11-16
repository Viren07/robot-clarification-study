#!/usr/bin/env bash
# Four KnowNo runs on AmbiK's 200-item sample, to make the AUROC comparison significant.
#
# WHY THIS RUN. Our AUROC is 0.4405 over four runs with sd 0.0101, which is already tight.
# AmbiK's is a single run on 100 items, and that one number contributes most of the +/-0.1405
# interval on a gap of 0.1261. Doubling AmbiK to 100 items per half drops the interval to
# +/-0.1157, which the gap clears. These runs also MEASURE AmbiK's generation spread, which is
# currently an assumption scaled from our side.
#
#   data/ambik/ambik_sample200_instructions.json   200 items, 100 ambiguous + 100 clear,
#                                                  plan_steps present on all 200
#   calibration: AmbiK's own 100 held-out items, cache already on disk and judge-labelled,
#                so the calibration pass costs nothing. Each dataset calibrates on its own
#                held-out set, which is what keeps the comparison fair.
#
# NOTE on the data file: ambik_sample200_instructions__replanned.json holds only 100 items
# despite the name. Use the non-replanned file, which has plan_steps on all 200.
#
# Each repeat gets a fresh --name so the test pass regenerates while the calibration cache is
# reused, pinning qhat and isolating generation noise. Same design as run_repeats.sh.
#
# Cost: 4 x 200 generations + 4 x 200 judge calls. No calibration spend.
set -e
D=data/ambik/ambik_sample200_instructions.json
C=data/ambik/ambik_calib100_instructions.json
CACHE=results/ambik/knowno_v3/ambik_calib100_instructions__knowno_v3__gpt-4o-mini__truth-judge__calib.jsonl

if [ ! -f "$CACHE" ]; then
  echo "Calibration cache missing: $CACHE"
  echo "The run will pay for AmbiK's 100 calibration items once, then reuse them."
fi

for i in 1 2 3 4; do
  TAG=ambik200
  [ "$i" -gt 1 ] && TAG="ambik200_r$i"
  echo "########## AmbiK 200, KnowNo run $i of 4  ($TAG) ##########"
  python src/run_knowno_v3.py --name "$TAG" --truth judge --calib "$C" --data "$D"
done

echo
echo "########## spread across the four AmbiK runs ##########"
python src/report_repeats.py --prefix ambik200 --data "$D" || true

echo
echo "Then the comparison that matters:"
echo "   ours   AUROC 0.4405  (4 runs, 204 items, sd 0.0101)"
echo "   AmbiK  AUROC 0.5666  (was 1 run on 100 items; now 4 runs on 200)"
echo "   gap    0.1261, needs a CI below that to be significant"
