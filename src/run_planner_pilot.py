"""
Runs intervention.py's plan_task across all 114 instructions in
data/own114/own114_instructions.json and scores it using a fully automated
confusion matrix:

    category=ambiguous   + action=clarify  -> correct  (TP: caught the ambiguity)
    category=ambiguous   + action=execute  -> incorrect (FN: silent failure, missed it)
    category=unambiguous + action=execute  -> correct  (TN: no unnecessary question)
    category=unambiguous + action=clarify  -> incorrect (FP: asked when it didn't need to)

Malformed JSON (parsed=False) is tracked separately and excluded from
the confusion matrix, since it reflects an output-formatting failure,
not an ambiguity-detection failure.

The baseline (planner.py) is intentionally left out of this script for
now -- it never asks, so scoring it needs a different approach (parse
rate + a sampled qualitative review), decided separately later.
"""

import json
import time
from pathlib import Path
from collections import defaultdict

from intervention import plan_task, LLM_PROVIDER, MODEL_NAME

REPO_ROOT = Path(__file__).resolve().parent.parent
INSTRUCTIONS_PATH = REPO_ROOT / "data" / "own114" / "own114_instructions.json"
# NOTE: both output files are overwritten on every run. To keep several runs, use run_planner_repeats.py.
OUTPUT_PATH = REPO_ROOT / "results" / "own114__planner__pilot_per_item.json"
SUMMARY_PATH = REPO_ROOT / "results" / "own114__planner__pilot_summary.json"

# Small delay between calls to stay under free-tier rate limits
# (Groq) or just be polite to the API in general.
DELAY_SECONDS = 1.0
MAX_RETRIES = 3


def call_with_retry(instruction, scene_context):
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            return plan_task(instruction, scene_context)
        except Exception as e:
            print(f"  ! Error on attempt {attempt}/{MAX_RETRIES}: {e}")
            if attempt == MAX_RETRIES:
                return {
                    "interpretations": [], "num_interpretations": None,
                    "action": None, "plan": None, "clarifying_question": None,
                    "raw": f"EXCEPTION: {e}", "parsed": False
                }
            time.sleep(5 * attempt)  # backoff


def expected_action(category):
    return "clarify" if category == "ambiguous" else "execute"


def outcome_label(category, action):
    exp = expected_action(category)
    if action == exp:
        return "correct"
    return "incorrect"


def main():
    with open(INSTRUCTIONS_PATH) as f:
        instructions = json.load(f)

    print(f"Loaded {len(instructions)} instructions.")
    print(f"Using provider: {LLM_PROVIDER} (model: {MODEL_NAME})\n")

    results = []
    for i, item in enumerate(instructions, 1):
        print(f"[{i}/{len(instructions)}] {item['id']}: {item['instruction'][:60]}...")

        result = call_with_retry(item["instruction"], item["scene_context"])

        row = {
            "id": item["id"],
            "instruction": item["instruction"],
            "category": item["category"],
            "ambiguity_type": item["ambiguity_type"],
            "parsed": result["parsed"],
            "action": result["action"],
            "num_interpretations": result["num_interpretations"],
            "interpretations": result["interpretations"],
            "clarifying_question": result["clarifying_question"],
            "plan": result["plan"],
        }

        if result["parsed"]:
            row["outcome"] = outcome_label(item["category"], result["action"])
        else:
            row["outcome"] = "malformed"

        results.append(row)
        time.sleep(DELAY_SECONDS)

    with open(OUTPUT_PATH, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nFull results saved to {OUTPUT_PATH}")

    # ---- Build the confusion matrix + per-category breakdown ----
    summary = {
        "total": len(results),
        "malformed_count": sum(1 for r in results if r["outcome"] == "malformed"),
        "confusion_matrix": {
            "true_positive_caught_ambiguity": 0,   # ambiguous -> clarify
            "false_negative_missed_ambiguity": 0,  # ambiguous -> execute
            "true_negative_correct_execute": 0,    # unambiguous -> execute
            "false_positive_unnecessary_ask": 0,   # unambiguous -> clarify
        },
        "by_ambiguity_type": defaultdict(lambda: {"total": 0, "correct": 0, "incorrect": 0, "malformed": 0}),
    }

    for r in results:
        atype = r["ambiguity_type"] or "unambiguous"
        summary["by_ambiguity_type"][atype]["total"] += 1

        if r["outcome"] == "malformed":
            summary["by_ambiguity_type"][atype]["malformed"] += 1
            continue

        cat, action = r["category"], r["action"]
        if cat == "ambiguous" and action == "clarify":
            summary["confusion_matrix"]["true_positive_caught_ambiguity"] += 1
        elif cat == "ambiguous" and action == "execute":
            summary["confusion_matrix"]["false_negative_missed_ambiguity"] += 1
        elif cat == "unambiguous" and action == "execute":
            summary["confusion_matrix"]["true_negative_correct_execute"] += 1
        elif cat == "unambiguous" and action == "clarify":
            summary["confusion_matrix"]["false_positive_unnecessary_ask"] += 1

        if r["outcome"] == "correct":
            summary["by_ambiguity_type"][atype]["correct"] += 1
        else:
            summary["by_ambiguity_type"][atype]["incorrect"] += 1

    summary["by_ambiguity_type"] = dict(summary["by_ambiguity_type"])

    # Overall accuracy, excluding malformed outputs from the denominator
    scored = summary["total"] - summary["malformed_count"]
    correct = (summary["confusion_matrix"]["true_positive_caught_ambiguity"]
               + summary["confusion_matrix"]["true_negative_correct_execute"])
    summary["overall_accuracy"] = round(correct / scored, 4) if scored else None

    with open(SUMMARY_PATH, "w") as f:
        json.dump(summary, f, indent=2)

    print(f"Summary saved to {SUMMARY_PATH}\n")
    print("=" * 60)
    print(f"Total instructions: {summary['total']}")
    print(f"Malformed (excluded from scoring): {summary['malformed_count']}")
    print(f"Overall accuracy: {summary['overall_accuracy']}")
    print("\nConfusion matrix:")
    for k, v in summary["confusion_matrix"].items():
        print(f"  {k}: {v}")
    print("\nBy ambiguity type:")
    for atype, stats in summary["by_ambiguity_type"].items():
        acc = round(stats["correct"] / stats["total"], 4) if stats["total"] else None
        print(f"  {atype}: {stats} (accuracy: {acc})")
    print("=" * 60)


if __name__ == "__main__":
    main()
