# robot-clarification-study

This project studies how LLM-based robot task planners fail on ambiguous natural-language instructions. It uses a labeled dataset of 114 instructions (50 unambiguous and 64 ambiguous: referential 16, goal 13, spatial 13, implicit 12, mixed 10) and compares an intervention planner with the AmbiK baselines No Help and Binary.

The intervention planner lists every interpretation the scene supports. It acts if there is exactly one and asks if there are zero or several. All current runs use Groq `openai/gpt-oss-120b` at temperature 0.

Related work: KnowNo (Ren et al. 2023), Introspective Planning (Liang et al. 2024), AmbiK (cog-model/AmbiK-dataset)

Status: pilot study. Not yet done: full AmbiK comparison, dataset growth to about 300, AmbiK-type labels for the 114 instructions.

## Results so far (own114, one model, 114 items, margin about 7 points)

| Method | Correct | Asked on clear | Asked on ambiguous |
|---|---|---|---|
| No Help (never asks) | 50/114 = 43.9% | 0/50 | 0/64 |
| Binary (AmbiK-style) | 60/114 = 52.6% | 0/50 | 10/64 |
| Intervention planner, repeat 1 | 94/114 = 82.5% | 8/50 | 52/64 |

The planner has three saved scores: 84.07% (original file, not kept), 82.30% (pilot file) and 82.46% (repeat 1). Whether the gaps come from a prompt edit or from run-to-run variation is not yet settled; repeat runs are planned. Binary's asked items also changed between two runs even at temperature 0. Treat differences of 1 to 2 points as noise.

## Folder map

```
data/own114/       the 114-instruction dataset (own114_instructions.json) and its datasheet
data/ambik/        AmbiK files, NOT in git (see below)
results/           every result file, named  <dataset>__<method>__<what it holds>
src/               code
```

Results files:

| File | What it is |
|---|---|
| `own114__binary__per_item.jsonl` | Binary on own114: one row per instruction, raw model text, Certain or Uncertain |
| `own114__nohelp_binary__summary.json` | No Help and Binary summary on own114, plus the older planner pilot row for comparison |
| `own114__planner__pilot_per_item.json` | Older planner run (2026-09-29), 93/113 correct. Overwritten each time run_planner_pilot.py runs |
| `own114__planner__pilot_summary.json` | Summary of that older run |
| `own114__planner__repeat1_20261028T022249Z.json` | Planner repeat 1 with the current prompt, 94/114. Includes model and prompt hash |

Dataset names: `own114` is this project's dataset. `ambik_sample200` is a seeded sample of 100 AmbiK pairs (200 instructions).

## Code

| Script | What it does |
|---|---|
| `src/intervention.py` | The intervention planner and its prompt |
| `src/run_planner_pilot.py` | One planner run on own114 (overwrites its output) |
| `src/run_planner_repeats.py` | Several planner runs, each saved separately |
| `src/run_binary_nohelp.py` | AmbiK-style Binary and No Help on any instruction file |
| `src/build_ambik_data.py` | Converts AmbiK's CSV into this project's format |
| `src/planner.py` | Early baseline planner |

Output files are named from the data file, so runs on different datasets never overwrite each other.

## Running

Put `GROQ_API_KEY` in `.env` (never committed). Groq's free tier allows about 200,000 tokens per day.

```
python src/run_binary_nohelp.py                  # own114, Binary and No Help
python src/run_planner_repeats.py --runs 3       # own114, planner, 3 saved runs
python src/run_binary_nohelp.py --data data/ambik/ambik_sample200_instructions.json
```

Binary runs resume where they stopped if rerun.

## AmbiK data

AmbiK (https://github.com/cog-model/AmbiK-dataset) is not redistributed here because no license was found in its repository. To rebuild the files:

```
mkdir -p data/ambik
curl -o data/ambik/ambik_test900_raw.csv https://raw.githubusercontent.com/cog-model/AmbiK-dataset/main/ambik_dataset/ambik_test_900.csv
python src/build_ambik_data.py
```

Binary here is a re-implementation of AmbiK's Binary and No Help ideas for Groq and whole instructions, not AmbiK's released code. Deviations are listed at the top of `src/run_binary_nohelp.py`. The conformal methods (KnowNo, LAP, LofreeCP) need calibration data and token probabilities and were not run.
