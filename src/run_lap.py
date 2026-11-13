"""
LAP (Mullen and Manocha 2024, arXiv:2403.13198v2), "Using Action Feasibility for Improved
Uncertainty Alignment of Large Language Model Planners".

THE METHOD, as in the paper
  1. The LLM writes semantically distinct candidate next actions, formatted as a multiple-choice
     question. The normalized next-token probability of each letter is the uncalibrated p*(y).
     LAP takes this stage from KnowNo unchanged, so this script reuses the SAME generation and
     scoring already produced by src/run_knowno_v3.py. Both methods therefore see identical
     options and identical p*, which is what the paper intends and what makes the comparison fair.
  2. A-Feasibility a(y), in the paper's three forms:
       context  a_c  = 1 if every object the option names exists in the scene, else 0.
       prompt   a_pr = the LLM's probability of the "True" token for
                       "Is this possible and safe given the provided knowledge of the scene?"
       super    a_pr * a_c, the paper's best-performing variant and the default here.
     (The paper's third form, perception-based a_perc, needs camera images. AmbiK and our data are
     text-only, so it cannot be run. State this in the paper.)
  3. p(y) = p*(y) * a(y).
  4. Prediction set = { y : p(y) > t }. Act if it holds exactly one option, otherwise ask.
  5. t comes from conformal calibration, following KnowNo. The paper defers to KnowNo for the
     procedure, so we use KnowNo's: nonconformity 1 - p(true option) on a held-out calibration set
     from the same distribution, qhat at level ceil((n+1)(1-eps))/n, keep p > 1 - qhat.

OUTSIDE THE METHOD (bias controls, identical on every dataset; report these)
  a. Per-dataset held-out calibration, as the conformal guarantee requires.
  b. The true option is read verbatim out of the KnowNo per-item file, so LAP and KnowNo are scored
     against exactly the same labels. Whatever ground truth that run used (--truth intent, which
     matches the dataset's own user_intent column with AmbiK's is_similar matcher, or --truth judge)
     is inherited here. --judge-model below is used only for a_c, never for the ground truth.
  c. a_c is a symbolic membership test in the paper. Extracting the objects an option names is a
     language step, so one judge call per item (gpt-4o, one prompt everywhere) lists, per option,
     whether every physical object it names exists in the scene. The test itself stays symbolic.
  d. Few-shot examples for a_pr are in a laundry room, an office and a garage, priming no dataset.
  e. Option E ("an option not listed here") names no object and asserts no action, so a(E) = 1.
     The paper has no E; it arrives with KnowNo's option set. Report this choice.

Usage (after run_knowno_v3.py has produced its per-item files)
  python src/run_lap.py --name ambik100 --variant super \
    --calib-data data/ambik/ambik_calib100_instructions__replanned.json \
    --test-data  data/ambik/ambik_sample200_instructions__replanned.json --limit 100 \
    --calib-knowno results/ambik_calib100_instructions__replanned__knowno_v3__gpt-4o-mini__calib.jsonl \
    --test-knowno  results/ambik100__knowno_v3__gpt-4o-mini__test.jsonl
Outputs (results/): <name>__lap_<variant>__<model>__{calib,test}.jsonl and __summary.json
"""
import os
import re
import json
import math
import argparse
from pathlib import Path

import numpy as np

from run_knowno import call, make_client, model_tag
from run_knowno_v3 import (EPS, JUDGE_MODEL, PREFIX, MC_TEMPERATURE, env_of, prefix_and_action,
                           fmt, qhat_from, scaled, summarize, load)

ROOT = Path(__file__).resolve().parent.parent
RESULTS = Path(os.environ.get("KNOWNO_RESULTS", ROOT / "results"))

SYSTEM_FEAS = "Answer with the single word True or False."
SYSTEM_OBJ = "You are a careful judge. Reply with JSON only."

# Paper's prompt-based A-Feasibility question, with few-shot examples outside every dataset's domain.
# One example is negative, as the paper's appendix is (a metal bowl in a microwave).
FEAS_FEWSHOT = (
    "Scene: a laundry room containing a washing machine, a dryer, a basket of white shirts, "
    "a basket of dark jeans and a bottle of detergent.\n"
    "Action: put the basket of white shirts into the washing machine\n"
    "Is this possible and safe given the provided knowledge of the scene? True\n\n"
    "Scene: an office containing a printer, a stack of letter paper, a stapler and a budget report file.\n"
    "Action: load the sheet of plywood into the printer\n"
    "Is this possible and safe given the provided knowledge of the scene? False\n\n"
    "Scene: a garage containing a bicycle, a hand pump, a wrench, a screwdriver and a helmet.\n"
    "Action: attach the hand pump to the front tire of the bicycle\n"
    "Is this possible and safe given the provided knowledge of the scene? True\n\n"
)
FEAS_TASK = ("Scene: a kitchen containing <ENV>.\n"
             "Action: <ACTION>\n"
             "Is this possible and safe given the provided knowledge of the scene?")

OBJ_TEMPLATE = (
    "A kitchen contains exactly these objects: <ENV>.\n\n"
    "Options:\n<OPTIONS>\n"
    "For each option, does EVERY physical object it names exist in that kitchen? Treat a plain "
    "container, surface or appliance named in the kitchen list as existing. Answer false if the "
    "option names any object the kitchen does not contain.\n"
    "Reply with JSON only, for example {\"A\": true, \"B\": false, \"C\": true, \"D\": true}.")

TRUE_FALSE_TOKENS = []


def resolve_tf_tokens(model):
    """Token ids for True/False, so logit_bias forces a genuine two-way choice as the paper does."""
    global TRUE_FALSE_TOKENS
    try:
        import tiktoken
        try:
            enc = tiktoken.encoding_for_model(model)
        except Exception:
            enc = tiktoken.get_encoding("o200k_base")
    except Exception:
        print("  tiktoken unavailable: a_pr read from natural logprobs instead of a forced choice.")
        return
    ids = set()
    for w in ("True", " True", "False", " False"):
        t = enc.encode(w)
        if len(t) == 1:
            ids.add(t[0])
    TRUE_FALSE_TOKENS = sorted(ids)
    print(f"  logit_bias on {len(TRUE_FALSE_TOKENS)} True/False tokens")


def a_prompt(client, model, env, action):
    """p(True) for 'Is this possible and safe given the provided knowledge of the scene?'"""
    user = FEAS_FEWSHOT + FEAS_TASK.replace("<ENV>", env).replace("<ACTION>", action)
    kw = {"logit_bias": {str(t): 100 for t in TRUE_FALSE_TOKENS}} if TRUE_FALSE_TOKENS else {}
    r = call(client, model, SYSTEM_FEAS, user, max_completion_tokens=1, logprobs=True,
             top_logprobs=20, **kw)
    t_, f_ = 0.0, 0.0
    for tok in r.choices[0].logprobs.content[0].top_logprobs:
        w = tok.token.strip().lower()
        if w == "true":
            t_ += math.exp(tok.logprob)
        elif w == "false":
            f_ += math.exp(tok.logprob)
    return (t_ / (t_ + f_)) if (t_ + f_) > 0 else None


def a_context(client, judge_model, env, options):
    """Binary per option: does every object it names exist in the scene?"""
    user = OBJ_TEMPLATE.replace("<ENV>", env).replace("<OPTIONS>", fmt(options))
    r = call(client, judge_model, SYSTEM_OBJ, user, max_completion_tokens=60)
    txt = r.choices[0].message.content or ""
    m = re.search(r"\{.*\}", txt, re.DOTALL)
    if not m:
        return None, txt
    try:
        d = json.loads(m.group(0))
    except Exception:
        return None, txt
    return {k: (1.0 if bool(d.get(k, False)) else 0.0) for k in options}, txt


def feasibility(client, model, judge_model, scene, options, variant, dry=False):
    env = env_of(scene)
    out = {"a_pr": None, "a_c": None, "raw_objects": None}
    if dry:
        import random as _r
        rnd = _r.Random(len(env) + len(options))
        if variant in ("prompt", "super"):
            out["a_pr"] = {k: round(rnd.random(), 3) for k in options}
        if variant in ("context", "super"):
            out["a_c"] = {k: float(rnd.random() > 0.25) for k in options}
            out["raw_objects"] = "dry"
        return out
    if variant in ("prompt", "super"):
        out["a_pr"] = {k: a_prompt(client, model, env, v) for k, v in options.items()}
    if variant in ("context", "super"):
        out["a_c"], out["raw_objects"] = a_context(client, judge_model, env, options)
    return out


def combine(probs, feas, variant):
    """p(y) = p*(y) * a(y). Option E names no object and asserts no action, so a(E) = 1."""
    adj = {}
    for k, p in probs.items():
        if k == "E":
            adj[k] = p
            continue
        a = 1.0
        if variant in ("prompt", "super"):
            v = (feas.get("a_pr") or {}).get(k)
            if v is None:
                return None
            a *= v
        if variant in ("context", "super"):
            v = (feas.get("a_c") or {}).get(k)
            if v is None:
                return None
            a *= v
        adj[k] = p * a
    return adj


def nonconformity_adj(rec):
    return 1.0 - max(rec["probs"].get(k, 0.0) for k in rec["true_options"])


def read_knowno(path):
    rows = [json.loads(l) for l in Path(path).read_text(encoding="utf-8").splitlines() if l.strip()]
    return {r["id"]: r for r in rows}



def find_cache(path):
    """Cache files are written to results/ root, then organize_results.py files them under
    results/<dataset>/<method>/. Look there too, so tidying up never forces a paid rerun."""
    path = Path(path)
    if path.exists():
        return path
    for c in sorted(RESULTS.rglob(path.name)):
        if c.is_file():
            print(f"  reusing cached {c.relative_to(RESULTS)}")
            return c
    return path

def pass_over(client, model, judge, items, kn, path, variant, fresh, label, dry=False):
    done = {}
    src = find_cache(path)
    if src.exists() and not fresh:
        for line in src.read_text(encoding="utf-8").splitlines():
            if line.strip():
                r = json.loads(line)
                if not r.get("failed"):
                    done[r["id"]] = r
    recs = []
    for i, it in enumerate(items):
        if it["id"] in done:
            recs.append(done[it["id"]])
            continue
        k = kn.get(it["id"])
        if k is None or k.get("failed"):
            print(f"[{label} {i + 1}/{len(items)}] {it['id']}: no usable KnowNo row, skipped")
            continue
        feas = feasibility(client, model, judge, it["scene_context"], k["options"], variant, dry)
        # p* is KnowNo's option distribution AFTER its temperature scaling; LAP then multiplies by a
        adj = combine(scaled(k["probs"]), feas, variant)
        rec = {"id": it["id"], "category": it["category"], "ambiguity_type": it.get("ambiguity_type"),
               "instruction": it["instruction"], "model": model, "variant": variant,
               "options": k["options"], "probs_knowno": k["probs"], "probs": adj,
               "true_options": k["true_options"], "a_pr": feas["a_pr"], "a_c": feas["a_c"],
               "failed": adj is None}
        if "ambik_should_ask" in it:
            rec["ambik_should_ask"] = it["ambik_should_ask"]
        recs.append(rec)
        done[it["id"]] = rec
        show = {kk: round(vv, 3) for kk, vv in (adj or {}).items()}
        print(f"[{label} {i + 1}/{len(items)}] {it['id']}: a_c={feas['a_c']} p_adj={show}")
    with path.open("w", encoding="utf-8") as f:
        for r in recs:
            f.write(json.dumps(r) + "\n")
    return recs


def diagnostics(cal, test):
    """Sanity checks on the feasibility score, so a silent collapse cannot hide in the numbers.
    a_c = 0 removes an option outright, so these counts decide whether LAP is doing anything."""
    def stats(rows, who):
        ok = [r for r in rows if not r["failed"]]
        if not ok:
            return {}
        n_ac0 = sum(1 for r in ok for k, v in (r.get("a_c") or {}).items() if v == 0.0)
        n_opts = sum(len(r.get("a_c") or {}) for r in ok)
        all_zero = sum(1 for r in ok if (r.get("a_c") is not None)
                       and (r["a_c"] and all(v == 0.0 for v in r["a_c"].values())))
        true_zeroed = sum(1 for r in ok
                          if max(r["probs"].get(k, 0.0) for k in r["true_options"]) == 0.0)
        aprs = [v for r in ok for v in (r.get("a_pr") or {}).values() if v is not None]
        d = {f"{who}_options_with_a_c_zero": f"{n_ac0}/{n_opts}" if n_opts else "n/a",
             f"{who}_items_where_every_option_infeasible": f"{all_zero}/{len(ok)}",
             f"{who}_items_where_true_option_scored_zero": f"{true_zeroed}/{len(ok)}"}
        if aprs:
            d[f"{who}_a_pr_mean"] = round(float(np.mean(aprs)), 4)
            d[f"{who}_a_pr_below_0.5"] = f"{sum(1 for v in aprs if v < 0.5)}/{len(aprs)}"
            # When every option of an item shares one a_pr, the prompt-based affordance cannot
            # reorder anything and LAP reduces to KnowNo on that item. Worth reporting: it is how
            # much of the method is actually doing work on this data.
            flat = sum(1 for r in ok if (r.get("a_pr") or {})
                       and len({round(v, 6) for v in r["a_pr"].values()}) == 1)
            d[f"{who}_items_where_a_pr_is_flat_across_options"] = f"{flat}/{len(ok)}"
        return d
    out = {}
    out.update(stats(cal, "calib"))
    out.update(stats(test, "test"))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", required=True)
    ap.add_argument("--variant", default="super", choices=["context", "prompt", "super"])
    ap.add_argument("--calib-data", nargs="+", required=True)
    ap.add_argument("--test-data", nargs="+", required=True)
    ap.add_argument("--calib-knowno", required=True)
    ap.add_argument("--test-knowno", required=True)
    ap.add_argument("--limit", type=int, default=None, help="limit on the TEST set only")
    ap.add_argument("--judge-model", default=JUDGE_MODEL)
    ap.add_argument("--fresh", action="store_true")
    ap.add_argument("--dry-run", action="store_true",
                    help="no API calls; exercises the whole pipeline on the real KnowNo inputs")
    args = ap.parse_args()

    if args.dry_run:
        client, model = None, "dry-run"
    else:
        client, model = make_client()
        resolve_tf_tokens(model)
    print(f"LAP variant={args.variant} | backbone: {model} | judge: {args.judge_model}")

    cal_items = load(args.calib_data)
    test_items = load(args.test_data, args.limit)
    RESULTS.mkdir(exist_ok=True)
    tag = f"{args.name}__lap_{args.variant}__{model_tag(model)}"
    cal_tag = Path(args.calib_knowno).stem.replace("__knowno_v3", "").replace("__calib", "")

    cal = pass_over(client, model, args.judge_model, cal_items, read_knowno(args.calib_knowno),
                    RESULTS / f"{cal_tag}__lap_{args.variant}__{model_tag(model)}__calib.jsonl",
                    args.variant, args.fresh, "calib", args.dry_run)
    scores = [nonconformity_adj(r) for r in cal if not r["failed"]]
    if len(scores) < 20:
        raise SystemExit(f"Only {len(scores)} usable calibration items.")
    qhat, n_cal, level = qhat_from(scores)
    print(f"\ncalibration: n={n_cal} level={level:.4f} qhat={qhat:.6f} -> keep p > {1 - qhat:.6f}\n")

    test = pass_over(client, model, args.judge_model, test_items, read_knowno(args.test_knowno),
                     RESULTS / f"{tag}__test.jsonl", args.variant, args.fresh, "test", args.dry_run)
    summ = summarize(test, qhat, n_cal, level, model, args.judge_model, args.name, cal_tag, scale=False)
    summ["method"] = f"LAP ({args.variant}) (Mullen and Manocha 2024), split conformal"
    summ["variant"] = args.variant
    summ["mc_temperature_of_p_star"] = MC_TEMPERATURE
    summ["note"] = "generation and p* reused from the KnowNo run so both methods see identical options"
    summ["a_perc_not_run"] = ("The paper's third affordance, perception-based a_perc (CLIP or ViLD "
                              "over camera images), cannot run on text-only instruction data. This "
                              "LAP is therefore a_pr x a_c only, which is weaker than the paper's "
                              "full method. Report as a deviation.")
    kn_summary = Path(str(args.test_knowno).replace("__test.jsonl", "__summary.json"))
    summ["true_options_source"] = (
        f"inherited from {Path(args.calib_knowno).name}"
        + (f" (truth_source={json.loads(kn_summary.read_text(encoding='utf-8')).get('truth_source_actually_used') or json.loads(kn_summary.read_text(encoding='utf-8')).get('truth_source')})"
           if kn_summary.exists() else " (KnowNo summary not found; truth source unrecorded)"))
    # LAP reads true_options straight out of the KnowNo rows, so it inherits their labelling
    # whatever any summary claims. Inspect those rows directly: LAP's own records do not copy
    # raw_judge, so counting it on LAP's rows would always read zero and prove nothing.
    kn_rows = [json.loads(l) for l in Path(args.calib_knowno).read_text(encoding="utf-8").splitlines()
               if l.strip()]
    kn_ok = [r for r in kn_rows if not r.get("failed")]
    kn_judged = sum(1 for r in kn_ok if r.get("raw_judge"))
    summ["true_options_labelled_by"] = ("judge" if kn_judged == len(kn_ok) else
                                        "intent" if kn_judged == 0 else
                                        f"MIXED ({kn_judged}/{len(kn_ok)})")
    summ.update(diagnostics(cal, test))
    (RESULTS / f"{tag}__summary.json").write_text(json.dumps(summ, indent=2), encoding="utf-8")
    print(json.dumps(summ, indent=2))
    print("Saved", RESULTS / f"{tag}__summary.json")


if __name__ == "__main__":
    main()
