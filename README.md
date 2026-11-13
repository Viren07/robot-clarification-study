# When Should a Robot Ask?

Characterizing failure modes of LLM-based task planners on ambiguous instructions.

Every number below comes from gpt-4o-mini. The metric is **balanced decision accuracy**: the average
of the ask rate on ambiguous instructions and the do-not-ask rate on clear ones. A method that never
asks scores 0.50 on any dataset, so 0.50 is the floor, not a result.

## Results

| Method | AmbiK (50 clear, 50 amb) | own114 (50 / 64) | own100 (50 / 50) | batch 2 (19 amb) |
|---|---|---|---|---|
| No Help | 0.50 | 0.50 | 0.50 | 0/19 asked |
| Binary | 0.52 | 0.5625 | 0.53 | 0/19 asked |
| KnowNo, faithful (v3) | 0.57 [0.49, 0.65] | not run | 0.60 [0.51, 0.69] | 14/19 asked |
| KnowNo, AmbiK plan-step port | 0.47 | not run | superseded | superseded |
| LAP | not run | not run | not run | not run |
| LofreeCP | not run | not run | not run | not run |
| Intervention planner (ours) | 0.65 | 0.905 | 0.77 (3 runs: 0.77, 0.76, 0.79) | 14/19 asked |

**No dataset of ours is harder than AmbiK yet.** Every method scores at or above its AmbiK level on
own100. Batch 2 (type A6: a hidden preference buried in a long, otherwise fully specified
instruction) is the only item type that has hurt more than one method, and is the current lead.

See `docs/harder_than_ambik.md` for the definition of "harder" and the decision rule.

## Datasets

| Folder | What it is |
|---|---|
| `data/ambik/` | AmbiK (not redistributed, gitignored). `src/build_ambik_data.py` builds the 100-pair sample; `src/build_ambik_calib.py` converts AmbiK's own calibration split. |
| `data/own114/` | First dataset. Easier than AmbiK for the planner (0.905). |
| `data/own100/own100_instructions.json` | Development set, 10 kitchen scenes x 10 items, 50 clear (U1 to U6) and 50 ambiguous (A1 to A5). |
| `data/own100/own100_batch2_amb19.json` | 19 ambiguous items of type A6. |
| `data/own100/own_calib100_instructions.json` | Held-out calibration set for the own\* family: same scenes and templates, different items, no overlap with any test set. KnowNo, LAP and LofreeCP all calibrate on it. |

`*__replanned.json` files carry model-written plan steps (see **Plan regeneration** below) and are
what the conformal methods consume. The originals stay in `plan_steps_original`.

Download AmbiK's raw CSVs into `data/ambik/` before anything else:

```
curl -o data/ambik/ambik_test900_raw.csv  https://raw.githubusercontent.com/cog-model/AmbiK-dataset/main/ambik_dataset/ambik_test_900.csv
curl -o data/ambik/ambik_calib100_raw.csv https://raw.githubusercontent.com/cog-model/AmbiK-dataset/main/ambik_dataset/ambik_calib_100.csv
```

## Code

| Script | What it does |
|---|---|
| `src/intervention.py` | The intervention planner: lists the scene-supported interpretations, acts on exactly one, asks on zero or two or more. |
| `src/run_planner_repeats.py` | Runs the planner several times, to measure run-to-run variation. |
| `src/run_binary_nohelp.py` | No Help and Binary, both KnowNo baselines (Binary's wording is AmbiK's). |
| `src/run_knowno_v3.py` | KnowNo (Ren et al. 2023) implemented faithfully. Use this one. |
| `src/run_knowno.py` | The earlier AmbiK plan-step port, kept only for the "as released" AmbiK row. |
| `src/run_lap.py` | LAP (Mullen and Manocha 2024, arXiv 2403.13198**v2**). Reuses the KnowNo generation, so both see identical options. |
| `src/run_lofreecp.py` | LofreeCP (Su et al. 2024, arXiv 2403.01216). Logit-free, samples 20 responses. |
| `src/regenerate_plans.py` | Rewrites every dataset's plan steps with one model and one prompt. |
| `src/organize_results.py` | Sorts `results/` into `results/<dataset>/<method>/`. Run after any batch of runs. |

`docs/implementation_audit.md` records, line by line, where each baseline differs from its paper and
from AmbiK's reimplementation. Read it before citing any of them.

## Running

Set `OPENAI_API_KEY` in `.env`. `OPENAI_MODEL` defaults to gpt-4o-mini. `pip install -r
requirements.txt`, plus `tiktoken` for the forced-letter scoring.

```
# 1. plans, one model and one prompt for every dataset
python src/regenerate_plans.py --data data/ambik/ambik_calib100_instructions.json
python src/regenerate_plans.py --data data/ambik/ambik_sample200_instructions.json --limit 100
python src/regenerate_plans.py --data data/own100/own_calib100_instructions.json
python src/regenerate_plans.py --data data/own100/own100_instructions.json
python src/regenerate_plans.py --data data/own100/own100_batch2_amb19.json

# 2. the cheap baselines
python src/run_binary_nohelp.py --plan-steps --data data/own100/own100_instructions__replanned.json
python src/run_planner_repeats.py --data data/own100/own100_instructions.json --runs 3

# 3. the conformal methods (--fresh discards cached per-item results)
python src/run_knowno_v3.py --name own100 \
  --calib data/own100/own_calib100_instructions__replanned.json \
  --data data/own100/own100_instructions__replanned.json

python src/run_lap.py --name own100 --variant super \
  --calib-data data/own100/own_calib100_instructions__replanned.json \
  --test-data data/own100/own100_instructions__replanned.json \
  --calib-knowno results/own100/knowno_v3/own_calib100_instructions__replanned__knowno_v3__gpt-4o-mini__calib.jsonl \
  --test-knowno results/own100/knowno_v3/own100__knowno_v3__gpt-4o-mini__test.jsonl

python src/run_lofreecp.py --name own100 \
  --calib data/own100/own_calib100_instructions__replanned.json \
  --data data/own100/own100_instructions__replanned.json

# 4. tidy up
python src/organize_results.py
```

Every script resumes if interrupted, and `--dry-run` works without an API key.

## Results folders

`results/<dataset>/<method>/`, with datasets `ambik`, `own114`, `own100`, `batch2` and methods
`binary_nohelp`, `planner`, `knowno_v3`, `knowno_steps`, `lap`, `lofreecp`. A calibration file sits
with the dataset it calibrates. `results/_superseded/` holds output that is no longer comparable:
the Groq gpt-oss-120b runs, the old planner pilot format, and the KnowNo plan-step runs on our data
whose cutoff came from AmbiK's calibration split.

## Bias controls

The three published methods are unchanged. Everything below sits outside them and is applied
identically to every dataset.

1. **Per-dataset calibration.** Conformal prediction only guarantees coverage when the calibration
   and test data come from one distribution, so AmbiK calibrates on AmbiK's `calib_100` and the
   own\* family on `own_calib100`. Reusing one dataset's cutoff on another breaks the method's own
   assumption.
2. **Plan regeneration.** KnowNo, LAP and LofreeCP are each shown one step of a plan. AmbiK's plans
   were written by its authors and ours by us, so one model (gpt-4o) and one prompt now write every
   plan and mark which step is shown.
3. **One judge for the true answer.** Neither our data nor AmbiK's ships a gold next action in a
   usable common form, so gpt-4o labels which generated options correctly carry out the step, with
   the same prompt on every dataset. The methods themselves run on gpt-4o-mini.
4. **Neutral few-shot examples.** A laundry room, an office and a garage, so they prime neither
   dataset, with the correct option at B, D and A rather than always A.
5. **Shuffled option letters.** The generator writes its most plausible option first, which made A
   the answer 88% of the time. Letters are permuted per item with a fixed seed.
6. **Matched composition.** The headline comparison is 50 clear and 50 ambiguous on both sides.
7. **Intervals on everything.** Wilson intervals on ask rates, bootstrap intervals on balanced
   accuracy.
8. **KnowNo's own temperature.** Its released code softmaxes the option logprobs at temperature 5.
   At 1 the nonconformity scores are bimodal and the cutoff lands on a cliff.
9. **One input unit for every method.** Binary is run with `--plan-steps`, so it reads the same plan
   step KnowNo, LAP and LofreeCP read.

## Known limitations

- **Our datasets were written after seeing where these methods fail. AmbiK was not.** No code change
  fixes this. The final claim needs a held-out set written before anyone looks at results.
- The true-answer judge is a model. Its agreement with a human on a sample still needs measuring.
- For a genuinely ambiguous instruction there is no single correct action, so the nonconformity score
  uses the most probable valid option. The papers assume one correct answer.
- LAP's perception-based feasibility variant needs camera images and cannot run on text-only data.
- LofreeCP uses OpenAI embeddings for its similarity term by default; `--embedder fasttext` matches
  the paper's FastText.
- AmbiK's "ambiguous" label covers Common Sense and Safety items where asking is not expected, so
  AmbiK's own rule (only Preferences should trigger a question) is reported alongside.
- Some AmbiK items look mislabelled or reference absent objects (0458, 0880, 0138, 0117, 0252, 0193,
  0357) and have not been hand-checked.
- About 50 items per half, so intervals run to roughly plus or minus 7 to 9 points.
