# Baseline implementation audit

Checked 2026-11-09 against the papers and against every released codebase we could find:

- KnowNo: Ren et al. 2023, arXiv 2307.01928. Code: `google-research/google-research/language_model_uncertainty/` (`KnowNo_Demo.ipynb`, `KnowNo_MobileManipulation.ipynb`).
- LAP: Mullen and Manocha 2024, arXiv 2403.13198**v2**. No code from the authors. (arXiv v3 renames the paper to LBAP; cite v2, which is the version AmbiK cites.)
- LofreeCP: Su et al. 2024, arXiv 2403.01216. Code: `SU-JIAYUAN/LofreeCP`.
- AmbiK: `cog-model/AmbiK-dataset`, which reimplements all five baselines.

**Decision for this project: our baselines follow the papers, not AmbiK's reimplementation.** Our
research question is whether our dataset is harder, which needs one implementation run on both
datasets. We never use AmbiK's published figures, so nothing has to reproduce them. Every deviation
below is reported rather than replicated.

Our implementations are in places *stronger* than the released ones (real embeddings, a working
feasibility score, temperature scaling, 20 samples). That is the safe direction: a stronger baseline
makes "harder than AmbiK" harder to claim, not easier.

## No Help

Never asks, so its ask rate is 0 and balanced accuracy is 0.50 on any dataset. AmbiK generates
options and discards them; we skip the call. No behavioural difference.

## Binary

A KnowNo baseline (Ren et al. 2023), worded by AmbiK. Cite both.

| | AmbiK | Ours |
|---|---|---|
| Unit | two variants: `binary/` (one plan step) and `noplans_binary/` (whole instruction) | `--plan-steps` for the plan step, default whole instruction |
| Prompt | few-shot, then "You: I will \<action\>\nCertain/Uncertain:" | same, few-shot taken from AmbiK |
| Decision | Uncertain means ask | same |

AmbiK's plans variant substitutes the whole generated A-D option block into `<OPTIONS>`, where the
few-shot shows a single action. We substitute a single action, matching the few-shot.

**Use `--plan-steps`.** Without it, Binary reads the whole instruction while KnowNo, LAP and
LofreeCP each read one plan step, so Binary would not be comparable to the other three.

## KnowNo

| | Paper and authors' code | AmbiK | Ours (`run_knowno_v3.py`) |
|---|---|---|---|
| Options | 4 generated, plus "E) an option not listed here" | 4, **no E** | 4 plus E |
| Scoring | `logit_bias` forces A-E, read logprobs | same idea | same |
| Temperature | **softmax at temperature 5** | `temperature_scaling` defaults to 1 and 5 is never passed | 5, `--mc-temperature` to change |
| Nonconformity | `1 - max(p over true options)` | quantile of correct-option probs directly (the "released" variant) | `1 - max(p over true options)` |
| Quantile | `np.quantile(..., method='higher')` | `np.quantile(...)`, default interpolation | `method='higher'` |
| Prediction set | `p >= 1 - qhat` | `p >= qhat` | `p >= 1 - qhat` |
| True option | dataset's own label; several allowed, max taken | keyword patterns in AmbiK's `variants` column | judge model; several allowed, max taken |

Temperature 5 matters a great deal. At temperature 1 the nonconformity scores are bimodal, median
0.000, with the 81st percentile sitting on a cliff at 1.0, so the cutoff is decided by a handful of
items. At 5 the medians are 0.021 on AmbiK and 0.188 on own100, and our own100 qhat of 0.927 lands
almost exactly on the 0.928 the authors' demo hardcodes.

`src/run_knowno.py` is our earlier port of AmbiK's plan-step version and is kept only for an
"as released on AmbiK" row. Its released cutoff comes out at 1.0, so it never asks.

## LAP

No code from the authors, so AmbiK's is the only implementation, and it has three bugs that change
what the method computes.

```python
def context_based_affordance(self, objects, scene):
    for obj in scene:          # iterates scene
        if obj not in scene:   # tests membership in scene: always False
            return 0
    return 1                   # so a_c is always 1
```

```python
affordance_prompt = self.affordance_prompt.replace('<DESCRIPTION>', description)
affordance_prompt = self.affordance_prompt.replace('<TASK>', task)   # restarts from the template
```

The second line discards the first, so `<DESCRIPTION>` is never filled; `<TASK>` receives the
instruction rather than the candidate option; and the same value is reused for all four options.
Then `np.exp(sample['logits'][...])` exponentiates a value `filter_logits` has already softmaxed, so
the multiplier is `exp(p)`, not `p`. Net effect: AmbiK's LAP is KnowNo with a per-item rescaling.

| | Paper | AmbiK | Ours |
|---|---|---|---|
| `p(y)` | `p*(y) · a(y)` | `exp(p*) · a` | `p*(y) · a(y)`, `p*` temperature-scaled first |
| `a_c` | 1 if every object the option names is in the scene | always 1 | judge extracts the objects, membership test stays binary |
| `a_pr` | p(True) for "Is this possible and safe given the provided knowledge of the scene?" | one value for all options, scene placeholder unfilled | per option, scene filled |
| `a_perc` | CLIP or ViLD over camera images | not run | **cannot run**: text-only data |
| Option E | not discussed | absent | present, `a(E) = 1`, since E names no object |
| Calibration | "following KnowNo", no detail given | released-style quantile | KnowNo's textbook procedure |

The paper's own evaluation sweeps thresholds from 1e-7 to 0.7 and reports area under the
success-versus-help curve. We report a single conformal threshold instead.

## LofreeCP

Three sources, three different formulas.

| | Paper (Eq. 8) | Authors' `run_cp.py` | AmbiK | Ours |
|---|---|---|---|---|
| Score | `-F + λ₁·NE - λ₂·SS` | `10 - 10F + (NE/2)λ₁ - SS·λ₂` | `1 - F + λ₁·NE - λ₂·SS` | Eq. 8, or `--formula released` |
| Samples | 20 | 20 | **8** (2 calls x 4 options) | 20 |
| Entropy | divided by `log m` | divided by `log(total)` | divided by **`log(2)`** | divided by `log m` |
| SS model | FastText, 200-dim | FastText trained on gensim's 9-sentence `common_texts` | same toy corpus | OpenAI embeddings, `--embedder fasttext` available |
| SS of top-1 | "not compared with itself" | compared against `""`: `if rank == 1` fires on the second response | 0 | 0 |
| λ search | grid 0 to 2, step 0.05 | grid step 0.2 | **fixed at 0.1, no search** | grid step 0.05 |
| Error rate | not fixed | 0.3 | 0.2 | 0.2 |
| Prediction set | `N <= qhat` | `N <= qhat` | **`N >= qhat`: inverted** | `N <= qhat` |

AmbiK keeps the options whose nonconformity is at or above the cutoff, which selects the least
confident options rather than the most. The toy FastText corpus means the similarity term is close
to noise in both released versions, which is why ours uses real embeddings.

## Prediction set to robot decision: each method keeps its own rule

The papers' decision rules are left exactly as published and are deliberately NOT aligned with each
other:

| Method | Rule | Source |
|---|---|---|
| KnowNo | `len(pred_set) != 1 or 'E' in pred_set` | the paper's own help rule |
| LAP | KnowNo's, since the paper defers to KnowNo for calibration | the paper |
| LofreeCP | `len(pred_set) > 1` | our harness; the paper defines no ask rule |

These differ, and that is correct. The comparison this project makes is one method's score on our
dataset against the SAME method's score on AmbiK. Methods are never compared with each other, so
there is no reason to make their decision rules match, and forcing them to match would misreport
what each published method does.

One case `> 1` cannot express is an EMPTY prediction set: nothing met the threshold, so there is no
response to execute, yet `> 1` scores it as "act". Rather than silently assign that, the run now
stops and says so. At eps 0.2, AmbiK's value and the one behind every reported number, zero items
are empty on either dataset, so the guard never fires and no reported figure depends on it. Empty
sets only appear at eps >= 0.4, a setting no paper uses (the LofreeCP authors' code uses 0.3, AmbiK
uses 0.2), and that variant has been dropped.

For the record, had the rule been changed to `!= 1`, own100 at eps 0.4 would move from 0.5500 to
0.6500 and AmbiK from 0.4800 to 0.4700. This is noted only to show the eps 0.4 variant is
rule-sensitive and therefore not reportable, not as an alternative result.

## Bias audit, 2026-11-10

Checked mechanically, not by eye:

1. **No scoring path branches on dataset identity.** The only `ambik_*` conditionals are on
   `ambik_should_ask`, which feeds the separately reported `balanced_accuracy_ambik_rule` column and
   never the `asked` decision.
2. **Every method constant is a module-level global**, identical for both datasets: EPS 0.2,
   MC_TEMPERATURE 5, M_SAMPLES 20, TEMP 1.0, the full 0 to 2 step-0.05 lambda grid, one judge model,
   one embedding model, one backbone.
3. **Few-shot neutrality.** KnowNo's and LofreeCP's few-shot examples are a laundry room, an office
   and a garage, priming neither kitchen dataset. Binary's is AmbiK's own and is kitchen-based, but
   both datasets are kitchen scenes so it is in-domain for both equally.
4. **No few-shot leakage.** Maximum similarity between any few-shot line and any dataset
   instruction is 0.67 on AmbiK test, 0.62 on AmbiK calib, 0.63 on own100 test and 0.64 on own
   calib. Near-identical across all four, and driven by the shared phrase "kitchen table".
5. **Option position carries no signal.** Letters are reshuffled per item under a fixed seed, and
   the generation few-shot shows option lists without answers, so it cannot teach a letter.

### Residual asymmetries, and which way each one pushes

| Asymmetry | Direction |
|---|---|
| Our intent patterns are single keywords, AmbiK's are conjunctive (mean true options 1.69 vs 1.30) | makes ours look EASIER |
| Our 9 `__none__` items are uncoverable by construction; AmbiK has none | makes ours look HARDER |
| Our datasets were written after seeing where these methods fail; AmbiK was not | makes ours look HARDER |
| LofreeCP's strict matcher rejects more AmbiK responses (35/100 vs 32/100 absent) | makes AmbiK look WORSE |
| LAP's a_perc cannot run on either dataset | neutral |
| Binary's kitchen few-shot | neutral, both datasets are kitchens |

Two of these favour our claim and two work against it, so no single correction flips the result. The
AUROC columns are immune to all of the labelling items, because they never read the true answer.

## What this means for the paper

1. Cite Binary as a KnowNo baseline as implemented by AmbiK.
2. Cite LAP from arXiv 2403.13198v2, and say no author code exists.
3. State plainly that we reimplemented LAP and LofreeCP from the papers, and that our numbers for
   them are therefore not comparable to AmbiK's published figures for those methods. Our comparison
   is between datasets under one implementation, which is what the claim needs.
4. Report the deviations we could not avoid: gpt-4o-mini backbone, a judge model for the true
   option, no perception-based feasibility, and OpenAI embeddings in place of FastText.
