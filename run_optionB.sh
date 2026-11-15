#!/usr/bin/env bash
# All five baselines on the option B test set, with a MATCHED calibration set.
#
# Test set   data/paired/optionB_54.json      108 items, 54 clear + 54 ambiguous, 18 pairs per group
# Calib set  data/paired/optionB_calib27.json  54 items, 27 clear + 27 ambiguous,  9 pairs per group
#
# This is the first run where the conformal rows are NOT exploratory. The calibration items come
# from the same three groups, built to the same recipes, with zero instructions shared with the
# test set. Exchangeability holds, so coverage and qhat mean what the papers say they mean.
#
# Nothing here is cached, so the calibration passes cost API calls this time, unlike the pilot.
# Rough volume: Binary/No Help 108 calls, KnowNo 162 generations + 162 judge calls, LAP reuses
# KnowNo's generations and adds its affordance calls, LofreeCP samples 20 times per item for
# 162 items. LofreeCP is the bulk of the spend.
#
# Rebuild both halves first so the files on disk match the pair modules.
set -e
T=referential,instrumental,parametric,spatial,sequential,preconditional
D=data/paired/optionB_54.json
C=data/paired/optionB_calib27.json

echo "########## 0/5  rebuild both halves ##########"
PAIR_TYPES=$T PAIR_GROUP_N=18 PAIR_OUT=optionB_54.json python src/build_paired.py
PAIR_SPLIT=calib PAIR_TYPES=$T PAIR_GROUP_N=9 PAIR_OUT=optionB_calib27.json python src/build_paired.py

echo "########## 1/4  No Help + Binary, one plan step (no calibration needed) ##########"
python src/run_binary_nohelp.py --data "$D" --tag optionB54 --plan-steps

echo "########## 2/4  KnowNo, judge-labelled, matched calibration ##########"
python src/run_knowno_v3.py --name optionB54 --truth judge --calib "$C" --data "$D"

echo "########## 3/4  LAP (reuses KnowNo's generation and probabilities) ##########"
python src/run_lap.py --name optionB54 --variant super \
  --calib-data "$C" --test-data "$D" \
  --calib-knowno results/optionB_calib27__knowno_v3__gpt-4o-mini__truth-judge__calib.jsonl \
  --test-knowno  results/optionB54__knowno_v3__gpt-4o-mini__truth-judge__test.jsonl

echo "########## 4/4  LofreeCP, judge-labelled, matched calibration ##########"
python src/run_lofreecp.py --name optionB54 --truth judge --calib "$C" --data "$D"

echo
echo "The bar is 0.50: a method that never asks scores exactly that."
echo "Screen predicted 0.4263 for the combined 54 pairs."
echo "Per group the screen said: G1 0.4722, G2 0.4167, G3 0.3900 (G3 measured)."
echo "For reference on AmbiK: No Help 0.50, Binary 0.52, KnowNo 0.53, LAP 0.55, LofreeCP 0.48."
