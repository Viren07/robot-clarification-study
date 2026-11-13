# What "harder than AmbiK" means in this project

Definition and metric written 2026-11-05, before any comparison numbers existed, so they cannot be
bent to fit the results. Everything below the rule line is a status log, updated as runs finish.

## Definition

A dataset of ours is harder than AmbiK if the SAME methods, on the SAME model, with the SAME metric,
do WORSE on it than on AmbiK.

## Metric (fixed, unchanged)

Balanced decision accuracy = (ask rate on ambiguous items + do-not-ask rate on clear items) / 2.
It does not depend on how many clear or ambiguous items a dataset holds. Also reported: each rate on
its own, and the AUROC of the uncertainty score, which needs no cutoff. Always with 95% intervals.

Ambiguous items counted as "should ask": all of them (our rule). AmbiK's own rule, that only
Preferences items should trigger a question, is reported as a second column.

## Decision rule

"Harder" is claimed only if our balanced accuracy is lower than AmbiK's, with the gap larger than
the 95% interval, for the methods that have room to fall. For methods already at the floor it must
be lower or equal.

No Help never asks, so it scores 0.50 on every dataset by construction. Binary and KnowNo sit near
chance on AmbiK already. Nothing can score meaningfully below a coin flip, so these are a floor and
cannot demonstrate "harder". A tie there is not evidence either way.

If the gap falls inside the interval, the paper says "different, not shown to be harder".

## Fairness conditions

1. One model for every method: gpt-4o-mini. The earlier Groq gpt-oss-120b runs are not mixed in;
   they sit in `results/_superseded/`.
2. AmbiK sample: the first 100 items of `ambik_sample200` (50 pairs, seeded), so 50 clear and 50
   ambiguous, matching our own100 composition exactly.
3. Prompts are not tuned on either dataset after seeing its results. The planner prompt is frozen
   at hash 555c8229896d.
4. Each dataset calibrates on its own held-out calibration set, because conformal prediction
   guarantees coverage only within one distribution.
5. Plan steps come from each dataset's own authored plans, and the true option comes from each
   dataset's own `user_intent` column matched with AmbiK's own `is_similar` matcher. Both datasets
   are therefore treated exactly as AmbiK treats itself. The model-written-plan variant
   (`src/regenerate_plans.py`) is kept as a robustness check, not as the headline.

## Status, 2026-11-09 (final KnowNo, intent-based ground truth)

| Method | AmbiK | own100 | Verdict |
|---|---|---|---|
| No Help | 0.50 | 0.50 | tie, floor |
| Binary, one plan step | 0.53 | 0.51 | lower on ours, but at the floor: see below |
| KnowNo, faithful (v3) | 0.53, AUROC 0.567 | 0.61, AUROC 0.654 | not harder; own100 is easier |
| LAP (super) | 0.55 [0.45, 0.64], AUROC 0.485 | 0.58 [0.49, 0.67], AUROC 0.542 | not harder; tied within the interval |
| LofreeCP, judge-labelled | 0.48, AUROC 0.580 | 0.54, AUROC 0.825 | not harder; own100 is easier |
| Intervention planner | 0.65 | 0.77 | not harder, easier |

KnowNo detail: AmbiK asks on 15/50 clear and 18/50 ambiguous, coverage 0.91, qhat 0.883. own100 asks
on 22/50 clear and 33/50 ambiguous, coverage 0.74, qhat 0.925. Under AmbiK's own labelling rule the
two are a dead tie: 0.6118 against 0.61. AUROC needs no cutoff and still favours own100, so the gap
is in the data and not in the calibration.

The earlier 0.57 against 0.60 row used a judge model for the true option, which returned "none of
the options is correct" on 38% of our calibration items against 26% of AmbiK's. Those items are the
only thing that makes KnowNo ask, so the asymmetry handed own100 a looser cutoff. Replacing the
judge with each dataset's own `user_intent` brought the rates to 33% (AmbiK) and 26% (ours) and
moved both numbers. The judge row is superseded, not an alternative result.

own114 is also not harder: the planner scores 0.905 on it, against 0.65 on AmbiK.

**Conclusion, now with all five baselines run: no dataset of ours is harder than AmbiK under this
definition.** own100 scores equal or higher on all five. The two methods with real headroom, KnowNo
and LofreeCP, both separate our ambiguous items from our clear ones better than they separate
AmbiK's (AUROC 0.654 against 0.567, and 0.811 against 0.569). The clear half
of own100 now matches AmbiK (the planner false-alarms on about 21 of 50 on both). The ambiguous half
is too easy: the planner catches 96% of own100's ambiguous items against 72% of AmbiK's.

## Correction, 2026-11-12: the KnowNo and LAP rows are JUDGE-labelled

Every KnowNo and LAP figure above was produced with judge labels, not the dataset's `user_intent`.
KnowNo's cache filename did not include the truth source and `pass_over` had no guard, so the
"final" `--truth intent` run silently reused rows cached during the earlier judge runs. The summary
field recorded the command-line flag rather than what the rows contained, which is what hid it.

Both are fixed: the cache refuses a row whose labelling differs from the requested one, each ground
truth writes its own files, and the summaries now report `truth_source_actually_used` derived from
the rows, with a `TRUTH_SOURCE_MISMATCH` field and a console warning when they disagree.

Rescored offline with `src/rescore_knowno.py`, which costs nothing because the options and
probabilities are cached:

| Dataset | labels | calib E | qhat | clear | amb | balanced | coverage |
|---|---|---|---|---|---|---|---|
| AmbiK | judge | 33/100 | 0.883 | 15/50 | 18/50 | **0.53** | 0.91 |
| AmbiK | intent | 39/100 | 0.968 | 19/50 | 29/50 | 0.60 | 0.67 |
| own100 | judge | 26/100 | 0.925 | 22/50 | 33/50 | **0.61** | 0.74 |
| own100 | intent | 29/100 | 0.978 | 31/50 | 43/50 | 0.62 | 0.71 |

**The judge stays the headline and intent goes in the appendix.** Three reasons. Coverage: under
intent labelling the conformal guarantee fails on BOTH datasets (0.67 and 0.71 against a 0.80
target), which indicts the labelling rather than the method. Symmetry: the intent no-match gap is
39 against 29, the judge's is 33 against 26, and AmbiK's patterns were authored by AmbiK for their
own option generator while ours were authored by us, an author asymmetry the judge does not have.
Coverage of all five methods: intent labelling makes LofreeCP degenerate (22 and 28 absent per 100,
qhat capped, prediction set keeps everything) while the judge gives 5 and 5.

Outstanding: the judge's agreement with a human is unmeasured. 25 items per dataset, hand-labelled,
is what turns this from a liability into standard practice.

Also fixed: AmbiK's `is_similar` lowercases the option text but not the pattern, so any intent
containing a capital can never match. Four of our own intents were affected (`Caesar` x3,
`French press`) and are now lowercased. AmbiK's 12 affected items are left as published, since that
is their data; they are reported, not patched.

## The screening metric was wrong, and the corrected one predicts exactly

An earlier screen selected items by the model's TOP option probability. KnowNo never reads that. It
keeps every option at or above `1 - qhat` and asks when more than one survives, so the deciding
number is the RUNNER-UP:

    A=0.907  B=0.038  ...  2nd below the cut -> one survives -> SILENT
    B=0.780  A=0.174  ...  2nd above the cut -> two survive  -> ASKS

The old metric ranked batch 2 best; the corrected arithmetic predicts batch 2 at 0.66 against
own100's measured 0.61, so it was optimising the wrong thing.

The corrected screen is validated: it predicts own100 at **0.6100** against a measured **0.6100**.

    balanced = 1 - (false_alarm_rate + miss_rate) / 2

| set | false alarms (clear) | misses (ambiguous) | sum | predicted | actual |
|---|---|---|---|---|---|
| AmbiK | 18/50 (36%) | 27/50 (54%) | 0.90 | 0.55 | 0.53 |
| own100 | 22/50 (44%) | 17/50 (34%) | 0.78 | 0.61 | **0.61** |
| batch 2 paired | 5/19 (26%) | 8/19 (42%) | 0.68 | 0.66 | not run |

**Both halves have opposite targets, which the earlier design got backwards.** An ambiguous item is
good when the method stays SILENT (runner-up below the cut). A clear item is good when the method
FALSELY ASKS (runner-up above the cut). The batch 2 minimal-pair twins are maximally clean, median
runner-up 0.0043, so the method correctly stays silent and banks free marks: 4 of 19 pass against
own100's 20 of 50. They are a controlled sub-study, not the basis for the clear half.

To beat AmbiK the two rates must sum above 0.90. Pooled over all 138 scored items we are at 0.75,
and the whole deficit is on the ambiguous half: 36% misses against AmbiK's 54%. Our clear half
already beats theirs, 39% against 36%.

Selection pool, free because every item is already scored, with a margin so it survives a shift in
qhat (ambiguous runner-up < 0.04, clear runner-up >= 0.15): **24 clear and 19 ambiguous keepers**,
so the shortfall to a 50/50 set is 26 clear and 31 ambiguous.

Caveat to carry into the writeup: the runner-up criterion IS KnowNo's decision boundary, so this is
adversarial selection against KnowNo and LAP specifically. Whether it transfers to LofreeCP, which
uses sampling entropy, is unverified.

## Binary is the only row where our dataset scores lower, and it is not evidence

Scored on one plan step, the same unit the other three methods see, Binary comes out at 0.53 on
AmbiK and 0.51 on ours. That is the only row in the table where ours is lower.

It is not evidence of a harder dataset. Binary asks 9 times out of 100 on AmbiK (3 clear, 6
ambiguous) and 3 times out of 100 on ours (1 clear, 2 ambiguous). The whole 0.02 gap rests on four
ambiguous items. Binary sits at the floor on both datasets, and the decision rule above says a
method at the floor must be lower OR EQUAL to count, with the gap larger than the interval. Four
items does not clear that bar. Report it as a tie.

Binary's earlier 0.52 / 0.53 row used the whole instruction rather than one plan step and was
therefore not comparable to KnowNo, LAP or LofreeCP. Those numbers are superseded. Summaries now
record `scored_unit` so the two variants cannot be confused again.

## LofreeCP: the keyword matcher was the problem, not eps

Superseded section, kept because the diagnosis matters. The first LofreeCP runs labelled the true
response by matching the dataset's `user_intent` with AmbiK's `is_similar`. Those patterns were
authored to discriminate among four full option descriptions, and LofreeCP samples short free-form
responses, so the conjunctive AND semantics rejected obviously correct answers:

    intent:  'minutes, until, al dente|firm'
    step:    Cook pasta until done.
    sampled: cook pasta until al dente      <- correct, rejected for lacking "minutes"

That pushed the no-matching-response rate to 22/100 on AmbiK and 28/100 on ours. Those items have
infinite nonconformity, the 0.82 quantile landed in the infinite tail, qhat capped, and the
prediction set kept every response on both datasets.

Raising eps does not fix it. AmbiK goes finite at 0.3, ours needs 0.4, and both must use the same
value; by 0.4 the sets are down to about size 1 and empty sets appear, which is the opposite
degeneracy. The eps variants have been dropped.

Labelling with a judge model fixed it. The absent rate fell to **5/100 on both datasets**,
symmetric, the lambda search found real values, and qhat is finite:

| | AmbiK | own100 |
|---|---|---|
| lambda1, lambda2 | 0.3, 0.0 | 0.15, 0.1 |
| qhat | -0.0105 | -0.2192 |
| mean set size vs distinct responses | 1.73 vs 4.86 | 1.45 vs 4.24 |
| `prediction_set_collapsed` | false | false |

## Empty prediction sets follow AmbiK's precedent

With a finite qhat, empty prediction sets occur: 2 clear and 3 ambiguous on AmbiK, 0 clear and 8
ambiguous on ours. LofreeCP's paper defines no ask rule, so the empty case is undefined, and we take
AmbiK's own rules verbatim from their `metrics.py` rather than inventing one:

    help_rate(a)            -> 1 if len(a) > 1 else 0                   (metrics.py:224-227)
    correct_help_rate(a, t) -> unambiguous: correct iff len(a) == 1     (metrics.py:200-210)
                               ambiguous:   correct iff len(a) >  1

These are deliberately not mirror images. On a clear item AmbiK require EXACTLY one surviving
response, so an empty set is wrong on a clear item and wrong on an ambiguous one. Balanced accuracy
for LofreeCP is therefore not 1 minus the ask rate on the clear half, and the summary records this
under `decision_and_correctness_rule`.

This is why own100's ask rate on ambiguous items (25/50) is lower than its correct count would
suggest: all 8 of its empty sets are on ambiguous items, where the method was maximally uncertain
and AmbiK's rule credits it nowhere.

KnowNo needs no such decision: its help rule is in its own paper, and its prediction set can never
be empty, because the largest of five probabilities always exceeds 1 - qhat.

## Superseded: LofreeCP's decision rule was degenerate on both datasets

Reported for honesty, because the LofreeCP row above should not be read as a working conformal
predictor. The lambda search chose lambda1 = lambda2 = 0 and qhat capped at 1e6 on both datasets, so
the prediction set keeps every distinct response: mean set size equals mean distinct responses
exactly, 4.81 on AmbiK and 4.24 on own100.

The cause is the absent-true-answer rate. When none of the 20 sampled responses carries out the
intent, the item is uncoverable and its nonconformity is infinite. That happened on 22/100 AmbiK
calibration items and 28/100 of ours. The quantile level is 0.82 on the 50 items the search holds
back for calibration, so in both cases the quantile lands in the infinite tail and is capped.

With the set always complete, `len(pred_set) != 1` reduces to "ask unless all 20 samples were
identical", which is self-consistency sampling, not conformal prediction. All 20 agreed on 14/100
AmbiK items and 18/100 of ours.

This is symmetric, so it does not bias the comparison, and the AUROC columns are unaffected because
they never use the cutoff. But the paper must either report LofreeCP as degenerate at eps = 0.2 on
text-only instruction data, or raise eps until the quantile is finite. Do not quietly present the
0.54 and 0.62 as conformal results.

Note that 9 of our items have intent `__none__` (type U6, no action can be correct), which are
absent by construction and which AmbiK has none of. That accounts for 9 of our 28 points. The
remaining asymmetry, 19 against 22, is small.

## LAP's affordance term does less work on our data

LAP multiplies the option probability by a feasibility score. On our dataset that score is closer to
1 than on AmbiK: mean a_pr 0.90 against 0.81, and the binary a_c zeroed 55 of 400 options against 89
of 400. Only 1 of our items had every option judged infeasible, against 4 of AmbiK's.

Our scenes name objects that actually exist and our options stay inside the scene, so the affordance
multiplier rarely fires and LAP collapses toward plain KnowNo. Some AmbiK options reference absent
objects, which is partly the labelling noise noted under "Still open". Making the affordance term
matter would need options that are plausible but physically blocked, which our scenes do not have.

## Current lead: type A6

Batch 2 (`data/own100/own100_batch2_amb19.json`) holds 19 items of type A6, a hidden preference
buried in a long, otherwise fully specified instruction, written to match the length of the AmbiK
items the planner misses (31 words against 32).

| Method | batch 2 (19 ambiguous) | same method on AmbiK's ambiguous half |
|---|---|---|
| Binary | 0/19 | 3/50 |
| KnowNo | 9/19 (47%) | 18/50 (36%) |
| Planner | 14/19 (74%), one run | 36/50 (72%) |

A6 is caught more often than AmbiK's own ambiguous items by every method that asks at all, so it is
NOT harder and NOT a KnowNo-proof type. Only Binary misses A6 entirely, and Binary is at the floor anyway. Four items fooled every method tested: a
choice of honey jar, of water source, of scrub tool, and of dishwasher cycle. Each is a process
parameter or a choice with a plausible default, which is the pattern to extend.

## Resolved

The earlier open problem, that KnowNo needs plan steps and own114 had none, is settled:
`src/regenerate_plans.py` writes plan steps for every dataset with one model and one prompt, so both
options A and B are moot.

Implementation questions are all settled; see `docs/implementation_audit.md`.


## Calibration composition, which limits the batch 2 number

Conformal prediction assumes the calibration and test items come from one distribution. The
ambiguity-type mix currently is:

| | A1 | A2 | A3 | A4 | A5 | A6 |
|---|---|---|---|---|---|---|
| own_calib100 | 20% | 20% | 20% | 20% | 8% | 12% |
| own100 test | 24% | 20% | 24% | 20% | 12% | 0% |
| batch 2 test | | | | | | 100% |

own100 against own_calib is a close enough match. **batch 2 is not**: it is entirely A6 while its
calibration set is 12% A6, so its KnowNo, LAP and LofreeCP numbers rest on a cutoff fitted to a
different mixture. Report batch 2 as exploratory only. If A6 becomes the backbone of the next
dataset version, that version needs a calibration set with the same type mix.

## Still open

- Our datasets were written after seeing where these methods fail, and AmbiK was not. The final
  claim needs a held-out set written before anyone looks at results. own100 is a development set.
- Our intent patterns are looser than AmbiK's. Mean number of options matching the intent is 1.69
  on our calibration set against 1.30 on AmbiK's, because AmbiK's patterns are often conjunctive
  (`cutting board, paring knife`) while ours are single keywords (`sponge`). A looser pattern lowers
  nonconformity, which makes our cutoff tighter and our dataset look easier, so this works against
  the claim rather than for it. Worth tightening before the paper.
- Some AmbiK items look mislabelled or reference absent objects (0458, 0880, 0138, 0117, 0252,
  0193, 0357) and have not been hand-checked.
