"""
Regenerate plan steps for ANY dataset with one model and one prompt.

Why: KnowNo is shown one step of a plan. AmbiK's plans were written by AmbiK's authors and our plans
were written by us, so a difference in KnowNo's score could come from who wrote the plans rather than
from the instructions. This script rewrites `plan_steps` and `ambiguity_step` for every dataset using
the SAME model and the SAME prompt, which removes that asymmetry. It touches no method code.

The originals are kept as `plan_steps_original` and `ambiguity_step_original`, so the run on AmbiK's
own plans stays available as a robustness check.

One call per item. Default generator: gpt-4o (set PLAN_MODEL to change). Temperature 0. Resumes.

Usage
  python src/regenerate_plans.py --dry-run --data data/own100/own100_instructions.json
  python src/regenerate_plans.py --data data/ambik/ambik_sample200_instructions.json --limit 100
  python src/regenerate_plans.py --data data/own100/own100_instructions.json
  python src/regenerate_plans.py --data data/own100/own100_batch2_amb19.json
  python src/regenerate_plans.py --data data/own114/own114_instructions.json
Output: <input>__replanned.json  next to the input file, plus a .jsonl cache of raw replies.
"""
import os
import json
import argparse
from pathlib import Path

from run_knowno import call, make_client

ROOT = Path(__file__).resolve().parent.parent
PLAN_MODEL = os.environ.get("PLAN_MODEL", "gpt-4o")
PREFIX = "You are a robot in a kitchen. The kitchen contains: "

SYSTEM = "You plan robot tasks. Reply with JSON only, no explanation and no code fences."

TEMPLATE = """A robot is in a kitchen that contains: <ENV>.

The robot received this instruction: "<TASK>"

Write the plan the robot would follow, as 3 to 8 short steps. Each step is one physical action in
plain English, for example "Take the red mug from the counter." Do not number the steps.

Then answer two questions about your plan.
1. choice_step: the number of the FIRST step that cannot be carried out without information the
   instruction does not give, counting from 1. Use 0 if every step is fully determined by the
   instruction and the kitchen.
2. main_step: the number of the step that carries out the main action of the instruction,
   counting from 1.

Reply with JSON only, in this exact shape:
{"plan": ["step one", "step two"], "choice_step": 0, "main_step": 2}"""


def env_of(scene):
    s = scene[len(PREFIX):] if scene.startswith(PREFIX) else scene
    return s.strip().rstrip(".")


def parse(txt):
    t = (txt or "").strip()
    if t.startswith("```"):
        t = t.strip("`")
        t = t[t.find("{"):] if "{" in t else t
    a, b = t.find("{"), t.rfind("}")
    if a < 0 or b < 0:
        return None
    try:
        d = json.loads(t[a:b + 1])
    except Exception:
        return None
    plan = [str(x).strip() for x in d.get("plan", []) if str(x).strip()]
    if not plan:
        return None
    try:
        choice = int(d.get("choice_step", 0))
        main = int(d.get("main_step", 1))
    except Exception:
        return None
    # the step KnowNo is shown: the first underdetermined step, else the main step. 0-based.
    one_based = choice if 1 <= choice <= len(plan) else (main if 1 <= main <= len(plan) else 1)
    return {"plan_steps": plan, "ambiguity_step": one_based - 1,
            "replan_choice_step": choice, "replan_main_step": main}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--model", default=PLAN_MODEL)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    src = ROOT / args.data
    items = json.loads(src.read_text(encoding="utf-8"))
    items = items if isinstance(items, list) else items["items"]
    if args.limit:
        items = items[:args.limit]

    if args.dry_run:
        client, model = None, "dry-run"
    else:
        client, model = make_client()
        model = args.model
    print(f"plan model: {model} | items: {len(items)}")

    sfx = "__DRYRUN" if args.dry_run else ""
    cache_path = src.with_name(src.stem + "__replan_raw" + sfx + ".jsonl")
    done = {}
    if cache_path.exists() and not args.dry_run:
        for line in cache_path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                r = json.loads(line)
                if r.get("parsed") and r.get("model") != "dry-run":
                    done[r["id"]] = r

    failed = []
    with cache_path.open("a" if not args.dry_run else "w", encoding="utf-8") as f:
        for i, it in enumerate(items):
            if it["id"] in done:
                continue
            if args.dry_run:
                p = {"plan_steps": [f"step {k} for {it['id']}" for k in range(1, 4)], "ambiguity_step": 0,
                     "replan_choice_step": 1, "replan_main_step": 2}
                raw = "dry"
            else:
                prompt = TEMPLATE.replace("<ENV>", env_of(it["scene_context"])).replace("<TASK>", it["instruction"])
                r = call(client, model, SYSTEM, prompt, max_completion_tokens=500)
                raw = r.choices[0].message.content or ""
                p = parse(raw)
            rec = {"id": it["id"], "model": model, "raw": raw, "parsed": p}
            f.write(json.dumps(rec) + "\n")
            f.flush()
            if p:
                done[it["id"]] = rec
            else:
                failed.append(it["id"])
            print(f"[{i + 1}/{len(items)}] {it['id']}: "
                  + (f"{len(p['plan_steps'])} steps, shown step {p['ambiguity_step'] + 1}" if p else "PARSE FAILED"))

    out = []
    for it in items:
        rec = done.get(it["id"])
        new = dict(it)
        if rec:
            new["plan_steps_original"] = it.get("plan_steps")
            new["ambiguity_step_original"] = it.get("ambiguity_step")
            new.update(rec["parsed"])
            new["plan_model"] = rec["model"]
        out.append(new)
    dst = src.with_name(src.stem + "__replanned" + sfx + ".json")
    dst.write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(f"\nreplanned {len(done)}/{len(items)}; failed: {failed}")
    print("Saved", dst)


if __name__ == "__main__":
    main()
