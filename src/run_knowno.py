"""
KnowNo-style conformal ambiguity detection on AmbiK, plan-step version, with the OpenAI API.

Scope: AmbiK data only. KnowNo is shown ONE step of a task's plan (AmbiK's `plans` setting),
and own114 has no plans, so this script refuses data files without `plan_steps`.

Why OpenAI: KnowNo needs the model's probability for each option letter (logprobs).
Groq's gpt-oss-120b does not return them (tested), gpt-4o-mini does.

How it works (per item, 2 calls)
  1. Generate: given the task and the plan up to the ambiguity step (`ambiguity_step`), the model
     writes options A to D for the NEXT action (AmbiK's generation few-shot prompt, unchanged).
  2. Score: the model answers with one letter. The probabilities of the letters A to D (first-token
     logprobs, renormalized over the options that exist) are the confidence in each option.
  3. A calibration cutoff turns probabilities into a prediction set. If the set has more than one
     option, the method asks. Otherwise it acts. If the model wrote only one option, it acts.

Two cutoffs come from the same calibration run on AmbiK's 100 calibration examples
  released   AmbiK's code as released: cutoff = (1-eps) quantile of the probabilities given to the
             CORRECT options; keep options with p > cutoff.
  standard   textbook KnowNo: score = 1 - p(correct option); q = conformal quantile; keep p >= 1 - q.
"Correct option" in calibration = a generated option matching AmbiK's keyword patterns in `variants`
(a port of AmbiK's filter_similar_sentences).

Deviations from AmbiK's released code (report these in the paper)
  1. OpenAI chat model with a short "continue the transcript" system message, not a completion
     model. AmbiK forced letter tokens with logit_bias; this reads the natural top logprobs.
  2. Probabilities are renormalized over the option letters that exist.
  3. A one-option answer counts as "act" (AmbiK would have a set of size 1 too).
  4. The raw generated text is saved for every item, so failures can be inspected.

Usage
  python src/run_knowno.py --dry-run --calibrate --limit 6
  python src/run_knowno.py --calibrate                                   # 100 items, ~200 calls
  python src/run_knowno.py --data data/ambik/ambik_sample200_instructions.json --limit 100
  python src/run_knowno.py --data data/ambik/ambik_sample200_instructions.json --limit 100 --retry-failed
Environment: OPENAI_API_KEY in .env; OPENAI_MODEL optional (default gpt-4o-mini).
Outputs (results/), <model> is the model name:
  ambik_calib100__knowno_steps__<model>__calibration_items.jsonl
  knowno_steps_calibration__<model>.json
  <dataset>__knowno_steps__<model>__per_item.jsonl       one row per item (resumes)
  <dataset>__knowno_steps__<model>__summary.json         both cutoffs + cutoff-free check (AUROC)
"""
import os
import re
import json
import math
import time
import argparse
import random
from pathlib import Path
from datetime import datetime, timezone

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results"
CALIB_CSV = ROOT / "data" / "ambik" / "ambik_calib100_raw.csv"
AMBIK_PREFIX = "You are a robot in a kitchen. The kitchen contains: "
EPS = 0.2  # target success 0.8, as in AmbiK's calibrate.py
KIND = "knowno_steps"

SYSTEM_GEN = ("You continue a transcript exactly as the pattern in the transcript shows. "
              "Reply with only the text that comes next, with no explanation.")
SYSTEM_ANS = "Follow the instruction in the transcript. Reply with a single capital letter only."

# AmbiK knowno/prompts/generation.txt (plans version): few-shot part, then the task template
GEN_FEWSHOT = 'We: You are a robot operating in an office kitchen. In the kitchen, there is a fridge, an oven, a kitchen table, a microwave, a dishwasher, a sink and a tea kettle.\n\nWe: Apart from that, in the kitchen there is a frying pan, a grill pan, a sauce pan, a vegetable peeler, a potato masher, canned olives, a greek yogurt cup, a vanilla yogurt cup, a strawberry yogurt cup, cream cheese, cheddar cheese slices, mozarella sticks and cottage cheese.\nWe: You have received the task “Prepare a Cheesy Greek Yogurt Dip.” You created a plan to compete the task. Your previous actions were:\n1. Take a bowl from the kitchen table.\n2. Take a Greek yogurt cup from the fridge.\n3. Pour the Greek yogurt into the bowl.\nYour next action is:\n4. Take a package of cheese from the fridge.\nYou:\nA) pick up the greek yogurt cup from the fridge\nB) pick up cheddar cheese slices from the fridge\nC) pick up cottage cheese from the fridge\nD) pick up cream cheese from the fridge\n\nWe: Apart from that, in the kitchen there is paper towels, a bottle opener, frozen mushroom pizza, frozen vegetable pizza, frozen pepperoni pizza, ginger biscuits, digestive biscuits, crackers, chocolate teacakes, honey, a vanilla yogurt cup and a greek yogurt cup.\nWe: You have received the task “Add honey to vanilla yogurt.” You created a plan to compete the task. Your previous actions were:\nYou:\n1. Take the bottle of honey from the kitchen table.\n2. Place the bottle of honey on the kitchen table.\nYour next action is:\n3. Open the bottle of honey.\nYou:\nA) use the bottle opener to open the bottle of honey\nB) use paper towels to open the bottle of honey\nC) open the bottle of honey without any tools\nD) use crackers to open the bottle of honey\n\nWe: Apart from that, in the kitchen there is a bread knife, a paring knife, a butter knife, a cutting board, a vegetable peeler, a potato masher, a plastic food storage container, a glass food storage container, a lemon, a banana, grapes, an apple, an orange, a peach, canned olives and a peeler.\nWe: You have received the task “Kitchen Robot, please use the vegetable peeler to peel the skin off the lemon in one continuous spiral, creating a lemon peel garnish for a cocktail or dessert.” You created a plan to compete the task. Your first action is:\n1. Take the lemon from the kitchen table.\nYou:\nA) pick up the banana from the kitchen table\nB) pick up the lemon from the kitchen table\nC) pick up canned olives from the kitchen table\nD) pick up glass food storage container from the kitchen table\n\n'
GEN_TASK = '\nWe: Apart from that, in the kitchen there is <DESCRIPTION>.\nWe: You have received the task “<TASK>“ You created a plan to compete the task. <PREFIX>\nYour next action is:\n<ACT>\nYou: '

# AmbiK knowno/prompts/choising.txt
ANS_TEMPLATE = 'We: You are a robot operating in an office kitchen. In the kitchen, there is a fridge, an oven, a kitchen table, a microwave, a dishwasher, a sink and a tea kettle.\nWe: Apart from that, in the kitchen there is <DESCRIPTION>.\nWe: You have received the task “<TASK>“ You created a plan to compete the task. <PREFIX>\nYour next action is:\n<ACT>\n\nOptions:\n<OPTIONS>\nWhat you will do A or B or C or D? Answer with a single capital letter'


def env_of(scene):
    """AmbiK scene_context -> the environment description AmbiK puts after 'Apart from that'."""
    if not scene.startswith(AMBIK_PREFIX):
        raise ValueError("scene is not in AmbiK format")
    return scene[len(AMBIK_PREFIX):].rstrip().rstrip(".")


def prefix_and_action(plan_steps, step):
    """Same as AmbiK pipeline.py: show the steps before `step`, ask for the action at `step`."""
    if step == 0:
        prefix = "Your first action is:"
    else:
        prefix = "Your previous actions were:\n" + "".join(a + "\n" for a in plan_steps[:step])
    return prefix, plan_steps[step]


def gen_prompt(env, task, prefix, action):
    t = GEN_TASK.lstrip("\n").replace("<DESCRIPTION>", env).replace("<TASK>", task)
    return GEN_FEWSHOT + t.replace("<PREFIX>", prefix).replace("<ACT>", action)


def ans_prompt(env, task, prefix, action, options):
    opts = "".join(f"{k}) {v}\n" for k, v in options.items())
    t = ANS_TEMPLATE.replace("<OPTIONS>", opts).replace("<TASK>", task).replace("<PREFIX>", prefix)
    return t.replace("<ACT>", action).replace("<DESCRIPTION>", env)


OPT_RE = re.compile(r"^\s*([A-D])\)\s*(.+?)\s*$", re.MULTILINE)


def parse_options(text):
    opts = {}
    for k, v in OPT_RE.findall(text or ""):
        opts.setdefault(k, v)
    return opts


def is_similar(option_text, pattern):
    """Port of AmbiK's is_similar: ', ' = AND, '|' = OR, leading '-' = must NOT appear.
    A keyword counts if ' ' + keyword occurs in the lowercased option text."""
    target = option_text.lower()
    parts = pattern.split(", ")
    right = 0
    for el in parts:
        if el.startswith("-"):
            hit = any((" " + v) in target for v in el.replace("-", "").split("|"))
            right += 0 if hit else 1
        else:
            hit = any((" " + v) in target for v in el.split("|"))
            right += 1 if hit else 0
    return right == len(parts)


def correct_letters(options, variants_str):
    pats = [p for p in str(variants_str).split("\n") if p.strip()]
    return [k for k, v in options.items() if any(is_similar(v, p) for p in pats)]


def letter_probs(top_logprobs, letters):
    acc = {k: 0.0 for k in letters}
    for t in top_logprobs:
        tok = t.token.strip().upper()
        if tok in acc:
            acc[tok] += math.exp(t.logprob)
    tot = sum(acc.values())
    return {k: v / tot for k, v in acc.items()} if tot > 0 else None


def auroc(pos, neg):
    """Share of (ambiguous, clear) pairs where the ambiguous one has the higher unsure score.
    Ties count half. 0.5 = no signal, 1.0 = perfect. No cutoff is involved."""
    if not pos or not neg:
        return None
    wins = sum(1.0 if a > c else 0.5 if a == c else 0.0 for a in pos for c in neg)
    return round(wins / (len(pos) * len(neg)), 4)


def cutoff_free_check(recs):
    """Unsure score = 1 - probability of the top option. Needs no calibration."""
    def unsure(r):
        return (1 - max(r["probs"].values())) if r.get("probs") else None
    clear = [u for r in recs if r["category"] == "unambiguous" and (u := unsure(r)) is not None]
    out = {"unsure_score": "1 - probability of the top option",
           "clear_instructions": len(clear), "auroc_ambiguous_vs_clear": {}}
    groups = {"all_ambiguous": [r for r in recs if r["category"] == "ambiguous"]}
    for r in groups["all_ambiguous"]:
        groups.setdefault(r.get("ambiguity_type") or "?", []).append(r)
    for name, rs in groups.items():
        pos = [u for r in rs if (u := unsure(r)) is not None]
        out["auroc_ambiguous_vs_clear"][name] = {"n": len(pos), "auroc": auroc(pos, clear)}
    return out


def make_client():
    from dotenv import load_dotenv
    from openai import OpenAI
    load_dotenv(ROOT / ".env")
    if not os.environ.get("OPENAI_API_KEY"):
        raise SystemExit("OPENAI_API_KEY is not set (add it to .env).")
    return OpenAI(), os.environ.get("OPENAI_MODEL", "gpt-4o-mini")


def call(client, model, system, user, retries=6, **kw):
    delay = 2.0
    for attempt in range(retries):
        try:
            return client.chat.completions.create(
                model=model, temperature=0.0,
                messages=[{"role": "system", "content": system}, {"role": "user", "content": user}], **kw)
        except Exception as e:
            if attempt == retries - 1:
                raise
            print(f"  API error, retrying in {delay:.0f}s: {str(e)[:120]}")
            time.sleep(delay)
            delay = min(delay * 2, 30)


def run_item(client, model, scene, task, plan_steps, step, dry):
    """Two calls. Returns dict: options, probs, raw_generation, failed."""
    env = env_of(scene)
    prefix, action = prefix_and_action(plan_steps, step)
    if dry:
        rnd = random.Random(len(task) + len(scene))
        options = {k: f"option {k} for {task[:20]}" for k in "ABCD"}
        raw = [rnd.random() ** 3 for _ in "ABCD"]
        s = sum(raw)
        return {"options": options, "probs": {k: v / s for k, v in zip("ABCD", raw)},
                "raw_generation": "dry", "failed": False}
    r1 = call(client, model, SYSTEM_GEN, gen_prompt(env, task, prefix, action),
              max_completion_tokens=256, stop=["We:"])
    text = r1.choices[0].message.content or ""
    options = parse_options(text)
    out = {"options": options, "probs": None, "raw_generation": text, "failed": False}
    if len(options) == 0:
        out["failed"] = True
        return out
    if len(options) == 1:  # nothing to choose between: the model is sure, so it acts
        out["probs"] = {k: 1.0 for k in options}
        return out
    r2 = call(client, model, SYSTEM_ANS, ans_prompt(env, task, prefix, action, options),
              max_completion_tokens=1, logprobs=True, top_logprobs=10)
    top = r2.choices[0].logprobs.content[0].top_logprobs
    out["probs"] = letter_probs(top, list(options.keys()))
    out["failed"] = out["probs"] is None
    return out


def model_tag(model):
    return model.replace("/", "-")


def calibrate(client, model, dry, limit):
    import pandas as pd
    d = pd.read_csv(CALIB_CSV)
    if limit:
        d = d.iloc[:limit]
    RESULTS.mkdir(exist_ok=True)
    suffix = "__DRYRUN" if dry else ""
    items_path = RESULTS / f"ambik_calib100__{KIND}__{model_tag(model)}__calibration_items{suffix}.jsonl"
    cal_path = RESULTS / f"{KIND}_calibration__{model_tag(model)}{suffix}.json"
    done = {}
    if items_path.exists() and not dry:
        for line in items_path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                r = json.loads(line)
                done[r["row"]] = r
    with items_path.open("a" if not dry else "w", encoding="utf-8") as f:
        for i in range(len(d)):
            if i in done:
                continue
            row = d.iloc[i]
            task = row["ambiguous_task"] if row["take_amb"] == 1 else row["unambiguous_direct"]
            scene = AMBIK_PREFIX + str(row["environment_full"]).rstrip().rstrip(".") + "."
            plan = row["plan_for_amb_task"] if row["take_amb"] == 1 else row["plan_for_clear_task"]
            plan_steps = [x.strip() for x in str(plan).split("\n") if x.strip()]
            res = run_item(client, model, scene, task, plan_steps, int(row["end_of_ambiguity"]), dry)
            options, probs = res["options"], res["probs"]
            ok = [] if not probs else (["A"] if dry else correct_letters(options, row["variants"]))
            rec = {"row": i, "id": str(row["id"]), "ambiguity_type": row["ambiguity_type"], "task": task,
                   "options": options, "probs": probs, "raw_generation": res["raw_generation"], "correct_letters": ok,
                   "success_probs": [probs[k] for k in ok] if probs else []}
            f.write(json.dumps(rec) + "\n")
            f.flush()
            done[i] = rec
            print(f"[calib {i + 1}/{len(d)}] correct options found: {len(ok)}")
    success = [p for r in done.values() for p in r["success_probs"]]
    n = len(success)
    if n < 5:
        raise SystemExit(f"Only {n} calibration probabilities. Not enough to calibrate.")
    q_level = min(1.0, math.ceil((n + 1) * (1 - EPS)) / n)
    released_cp = float(np.quantile(success, q_level))
    qhat = float(np.quantile([1 - p for p in success], q_level))
    cal = {"model": model, "utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
           "calibration_items": len(done), "items_without_correct_option": sum(1 for r in done.values() if not r["success_probs"]),
           "n_success_probs": n, "eps": EPS, "q_level": round(q_level, 4),
           "released_cp_keep_if_p_greater_than": released_cp,
           "standard_keep_if_p_at_least": 1 - qhat}
    cal_path.write_text(json.dumps(cal, indent=2), encoding="utf-8")
    print(json.dumps(cal, indent=2))
    print(f"Saved {cal_path}")


def main():
    from run_binary_nohelp import summarize
    ap = argparse.ArgumentParser()
    ap.add_argument("--calibrate", action="store_true", help="run calibration on AmbiK's 100 examples and save the cutoffs")
    ap.add_argument("--data", required=False, default="data/ambik/ambik_sample200_instructions.json", help="AmbiK instruction file with plan_steps")
    ap.add_argument("--retry-failed", action="store_true", help="redo items that failed earlier (no options or no probabilities)")
    ap.add_argument("--tag", default="", help="dataset name for output files (default: from data file name)")
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--dry-run", action="store_true", help="no API calls; tests the plumbing")
    args = ap.parse_args()

    client = None
    model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
    if not args.dry_run:
        client, model = make_client()
    print(f"model: {model}{' (dry run)' if args.dry_run else ''}")

    if args.calibrate:
        calibrate(client, model, args.dry_run, args.limit)
        return

    suffix = "__DRYRUN" if args.dry_run else ""
    cal_name = f"{KIND}_calibration__{model_tag(model)}{suffix}.json"
    cal_path = next((c for c in (RESULTS / cal_name, RESULTS / "ambik" / KIND / cal_name,
                                 RESULTS / "ambik_dataset_knowno" / cal_name) if c.exists()), None)
    if cal_path is None:
        raise SystemExit(f"No calibration file {cal_name} in results/ or results/ambik/{KIND}/. "
                         f"Run with --calibrate first.")
    cal = json.loads(cal_path.read_text(encoding="utf-8"))
    cp_rel, p_std = cal["released_cp_keep_if_p_greater_than"], cal["standard_keep_if_p_at_least"]
    print(f"cutoffs: released p > {cp_rel:.6f} | standard p >= {p_std:.4f}")

    data_path = Path(args.data)
    tag = args.tag or data_path.stem.removesuffix("_instructions")
    data = json.loads(data_path.read_text(encoding="utf-8"))
    if args.limit:
        data = data[: args.limit]
    if not all("plan_steps" in x for x in data):
        raise SystemExit("This data has no plan_steps. KnowNo needs plan steps, so it cannot run on this file "
                         "(own114 has none). Use data/ambik/ambik_sample200_instructions.json.")
    RESULTS.mkdir(exist_ok=True)
    out_path = RESULTS / f"{tag}__{KIND}__{model_tag(model)}__per_item{suffix}.jsonl"
    sum_path = RESULTS / f"{tag}__{KIND}__{model_tag(model)}__summary{suffix}.json"
    done = {}
    if out_path.exists() and not args.dry_run:
        for line in out_path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                r = json.loads(line)
                done[r["id"]] = r
        if args.retry_failed:
            bad = [k for k, r in done.items() if r.get("failed")]
            for k in bad:
                del done[k]
            out_path.write_text("".join(json.dumps(r) + "\n" for r in done.values()), encoding="utf-8")
            print(f"retrying {len(bad)} failed items")

    with out_path.open("a" if not args.dry_run else "w", encoding="utf-8") as f:
        for i, item in enumerate(data, 1):
            if item["id"] in done:
                continue
            res = run_item(client, model, item["scene_context"], item["instruction"],
                           item["plan_steps"], item["ambiguity_step"], args.dry_run)
            options, probs = res["options"], res["probs"]
            rec = {"id": item["id"], "category": item["category"], "ambiguity_type": item.get("ambiguity_type"),
                   "ambik_type": item.get("ambik_type"), "should_ask": item.get("ambik_should_ask"),
                   "instruction": item["instruction"], "model": model, "failed": res["failed"], "ambiguity_step": item["ambiguity_step"],
                   "options": options, "probs": probs, "raw_generation": res["raw_generation"]}
            if probs:
                rec["set_released"] = [k for k, p in probs.items() if p > cp_rel]
                rec["set_standard"] = [k for k, p in probs.items() if p >= p_std]
                rec["asked_released"] = len(rec["set_released"]) > 1
                rec["asked_standard"] = len(rec["set_standard"]) > 1
            else:
                rec["asked_released"] = rec["asked_standard"] = None
            f.write(json.dumps(rec) + "\n")
            f.flush()
            done[item["id"]] = rec
            print(f"[{i}/{len(data)}] {item['id']}: released={rec['asked_released']} standard={rec['asked_standard']}")
            if not args.dry_run:
                time.sleep(0.2)

    recs = [done[x["id"]] for x in data if x["id"] in done]
    def rows(key):
        return [{"category": r["category"], "ambiguity_type": r["ambiguity_type"], "asked": r[key],
                 "ambik_type": r.get("ambik_type"), "should_ask": r.get("should_ask")} for r in recs]
    summaries = [summarize(rows("asked_released"), f"knowno, released cutoff ({model})"),
                 summarize(rows("asked_standard"), f"knowno, standard cutoff ({model})")]
    summaries.append({"failed_items": sum(1 for r in recs if r.get("failed")), "items": len(recs)})
    summaries.append({"cutoff_free_check": cutoff_free_check(recs)})
    summaries.append({"calibration": cal})
    print("\n" + json.dumps(summaries, indent=2))
    sum_path.write_text(json.dumps(summaries, indent=2), encoding="utf-8")
    print(f"\nSaved {sum_path}")


if __name__ == "__main__":
    main()
