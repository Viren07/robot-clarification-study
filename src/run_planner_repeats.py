"""
Runs the intervention planner several times on an instruction file and keeps
every run in its own file, so run-to-run variation can be measured and reported.

Why: a single planner run cannot show run-to-run variation, so this
file on disk is only the latest run. Two saved runs of this planner disagreed
(95/113 = 84.07% vs 93/113 = 82.30%) and there was no record of which was which.
This script never overwrites an earlier run.

What it saves, under results/ (<dataset> comes from the data file name, e.g. own114)
  <dataset>__planner__repeat<k>_<UTC timestamp>.json   metadata + one row per instruction
  <dataset>__planner__repeats_summary.json             accuracy per run, mean, range, items that flipped

Each run file records the provider, model, temperature, and a short hash of the
system prompt, so a later reader can tell which prompt version produced it.

Scoring is the same as evaluate.py: ambiguous + clarify is correct, unambiguous +
execute is correct, malformed outputs are excluded from the denominator.

Usage
  python src/run_planner_repeats.py --dry-run --runs 2   # no API calls
  python src/run_planner_repeats.py --runs 3             # 3 x 114 real calls on own114
  python src/run_planner_repeats.py --data data/ambik/ambik_sample200_instructions.json --runs 1
Environment: same .env as intervention.py (LLM_PROVIDER=groq, GROQ_API_KEY).
"""
import json
import time
import hashlib
import argparse
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "own114" / "own114_instructions.json"
RESULTS = ROOT / "results"


def fake_plan(instruction, scene_context):
    """Offline stand-in for --dry-run. Deterministic, no network."""
    n = len(instruction) % 3
    return {"interpretations": ["x"] * n, "num_interpretations": n,
            "action": "execute" if n == 1 else "clarify",
            "plan": None, "clarifying_question": None, "raw": "fake", "parsed": True}


def score(rows):
    scored = [r for r in rows if r["parsed"]]
    correct = sum(
        (r["action"] == "clarify") == (r["category"] == "ambiguous") for r in scored)
    clear = [r for r in scored if r["category"] == "unambiguous"]
    amb = [r for r in scored if r["category"] == "ambiguous"]
    return {
        "total": len(rows),
        "malformed": len(rows) - len(scored),
        "correct": correct,
        "scored": len(scored),
        "accuracy": round(correct / len(scored), 4) if scored else None,
        "asked_on_clear": f"{sum(r['action'] == 'clarify' for r in clear)}/{len(clear)}",
        "asked_on_ambiguous": f"{sum(r['action'] == 'clarify' for r in amb)}/{len(amb)}",
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", type=int, default=3)
    ap.add_argument("--delay", type=float, default=1.0, help="seconds between calls")
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--data", default=None, help="instruction file (default: own114)")
    ap.add_argument("--tag", default="", help="dataset name for output files (default: from data file name)")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    data_path = Path(args.data) if args.data else DATA
    tag = args.tag or data_path.stem.removesuffix("_instructions")
    data = json.loads(data_path.read_text(encoding="utf-8"))
    if args.limit:
        data = data[: args.limit]

    if args.dry_run:
        plan, provider, model, prompt_hash = fake_plan, "dry-run", "fake", "n/a"
        retry = lambda i, s: fake_plan(i, s)
        out_dir = RESULTS / "DRYRUN"
    else:
        import intervention
        from intervention import plan_task

        def call_with_retry(instruction, scene_context, max_retries=3):
            """Was in run_planner_pilot.py, which is gone; same behaviour, same backoff."""
            for attempt in range(1, max_retries + 1):
                try:
                    return plan_task(instruction, scene_context)
                except Exception as e:
                    print(f"  ! Error on attempt {attempt}/{max_retries}: {e}")
                    if attempt == max_retries:
                        return {"interpretations": [], "num_interpretations": None, "action": None,
                                "plan": None, "clarifying_question": None,
                                "raw": f"EXCEPTION: {e}", "parsed": False}
                    time.sleep(5 * attempt)
        provider, model = intervention.LLM_PROVIDER, intervention.MODEL_NAME
        if provider == "openai":  # keep OpenAI runs apart from the Groq runs
            tag += "__" + model.replace("/", "-")
        prompt_hash = hashlib.sha256(intervention.SYSTEM_PROMPT.encode("utf-8")).hexdigest()[:12]
        retry = call_with_retry
        out_dir = RESULTS
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"provider={provider} model={model} prompt_hash={prompt_hash} "
          f"runs={args.runs} items={len(data)}")

    all_runs = []
    for k in range(1, args.runs + 1):
        rows = []
        for i, item in enumerate(data, 1):
            r = retry(item["instruction"], item["scene_context"])
            rows.append({
                "id": item["id"], "category": item["category"],
                "ambiguity_type": item.get("ambiguity_type"),
                "parsed": r["parsed"], "action": r["action"],
                "num_interpretations": r["num_interpretations"],
            })
            if not args.dry_run:
                time.sleep(args.delay)
            if i % 20 == 0:
                print(f"  run {k}: {i}/{len(data)}")
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        path = out_dir / f"{tag}__planner__repeat{k}_{stamp}.json"
        meta = {"provider": provider, "model": model, "temperature": 0.0,
                "system_prompt_sha256_12": prompt_hash, "utc": stamp}
        s = score(rows)
        path.write_text(json.dumps({"meta": meta, "summary": s, "rows": rows}, indent=2),
                        encoding="utf-8")
        print(f"run {k}: {s['correct']}/{s['scored']} = {s['accuracy']} "
              f"(clear asked {s['asked_on_clear']}, ambiguous asked {s['asked_on_ambiguous']}) -> {path.name}")
        all_runs.append((rows, s))

    accs = [s["accuracy"] for _, s in all_runs if s["accuracy"] is not None]
    flips = []
    for idx in range(len(data)):
        decisions = {rows[idx]["action"] for rows, _ in all_runs}
        if len(decisions) > 1:
            flips.append(data[idx]["id"])
    summary = {
        "meta": {"provider": provider, "model": model, "prompt_sha256_12": prompt_hash},
        "runs": [s for _, s in all_runs],
        "accuracy_mean": round(sum(accs) / len(accs), 4) if accs else None,
        "accuracy_min": min(accs) if accs else None,
        "accuracy_max": max(accs) if accs else None,
        "items_whose_decision_changed_between_runs": len(flips),
        "changed_ids": flips,
    }
    (out_dir / f"{tag}__planner__repeats_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print("\n" + json.dumps({k: v for k, v in summary.items() if k != "runs"}, indent=2))


if __name__ == "__main__":
    main()
