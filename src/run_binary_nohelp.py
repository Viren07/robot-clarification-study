"""
AmbiK-style Binary and No Help baselines, run with Groq on any instruction file
(default: data/own114/own114_instructions.json).

Why this file exists
  AmbiK (cog-model/AmbiK-dataset) releases code for Binary and No Help. That code
  is wired to the OpenAI API and to AmbiK's plan format, so this is a small
  re-implementation of the same two ideas for this repo's data. It keeps the
  few-shot examples from AmbiK's noplans_binary prompt, and the same decision
  rule: ask if the model says "Uncertain", act if it says "Certain".

Methods
  no_help  never asks. No model call is needed, so its ask rate is 0 by definition.
  binary   call 1: the model states the action it would take ("I will ...").
           call 2: the model labels that action Certain or Uncertain.
           Uncertain means ask. Certain means act.

Deviations from AmbiK's released code (report these in the paper)
  1. The unit is the whole instruction, not one plan step. AmbiK feeds the plan
     step where the ambiguity starts. This dataset has no plans.
  2. The scene is this dataset's prose scene_context, not an object list.
  3. The model is a chat model (Groq gpt-oss-120b), so the completion-style
     few-shot prompt is wrapped in a short instruction to continue the transcript
     and to answer with only the next piece of text.
  4. Few-shot examples are AmbiK's, unchanged. Only the final item's framing lines
     are adapted to non-kitchen scenes.

Scoring (against this dataset's own labels)
  category == ambiguous  -> asking is correct
  category == unambiguous -> acting is correct
  Items whose answer cannot be parsed are counted separately and left out of
  accuracy, the same way the pilot excluded its one malformed output.

Usage
  python src/run_binary_nohelp.py --dry-run --limit 6   # no API calls, tests the plumbing
  python src/run_binary_nohelp.py --limit 3             # three real items from own114
  python src/run_binary_nohelp.py                       # all 114 (own114)
  python src/run_binary_nohelp.py --data data/ambik/ambik_sample200_instructions.json

Output files are named from the data file, so datasets never overwrite each other:
  results/<dataset>__binary__per_item.jsonl        one row per instruction (resumes if rerun)
  results/<dataset>__nohelp_binary__summary.json   No Help and Binary summary
<dataset> is the data file name without "_instructions", e.g. own114, ambik_sample200.
Environment: GROQ_API_KEY (and optionally GROQ_MODEL) from .env, as in intervention.py.
"""
import os
import re
import json
import time
import argparse
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "own114" / "own114_instructions.json"
RESULTS = ROOT / "results"
INTERVENTION = RESULTS / "own114__planner__pilot_per_item.json"  # older planner run, own114 only

# Few-shot examples copied from AmbiK noplans_binary/prompts/uncertainty_detection.txt
FEWSHOT = """We: You are a robot operating in an office kitchen. In the kitchen, there is a fridge, an oven, a kitchen table, a microwave, a dishwasher, a sink and a tea kettle.

We: Apart from that, in the kitchen there is a frying pan, a grill pan, a sauce pan, a vegetable peeler, a potato masher, canned olives, a greek yogurt cup, a vanilla yogurt cup, a strawberry yogurt cup, cream cheese, cheddar cheese slices, mozzarella sticks and cottage cheese.
We: Take a package of cheese from the fridge.
You: I will pick up cheddar cheese slices from the fridge.
Certain/Uncertain: Uncertain

We: Apart from that, in the kitchen there is paper towels, a bottle opener, frozen mushroom pizza, frozen vegetable pizza, frozen pepperoni pizza, ginger biscuits, digestive biscuits, crackers, chocolate teacakes, honey, a vanilla yogurt cup and a greek yogurt cup.
We: Open the bottle of honey.
You: I will open the bottle of honey without any tools.
Certain/Uncertain: Certain

We: Apart from that, in the kitchen there is a bread knife, a paring knife, a butter knife, a cutting board, a vegetable peeler, a potato masher, a plastic food storage container, a glass food storage container, a lemon, a banana, grapes, an apple, an orange, a peach, canned olives and a peeler.
We: Take the lemon from the kitchen table.
You: I will pick up the lemon from the kitchen table.
Certain/Uncertain: Certain
"""

SYSTEM = ("You continue a transcript exactly as the pattern in the transcript shows. "
          "Reply with only the text that comes next, with no explanation.")

# Call 1 reuses the same examples but without the Certain/Uncertain lines.
FEWSHOT_NO_LABELS = "\n".join(
    line for line in FEWSHOT.splitlines() if not line.startswith("Certain/Uncertain:")
)


def item_block(scene, instruction):
    return (f"We: The scene is described as follows: {scene}\n"
            f"We: {instruction}\n")


def prompt_generate(scene, instruction):
    return FEWSHOT_NO_LABELS + "\n" + item_block(scene, instruction) + "You: I will"


def prompt_uncertainty(scene, instruction, action_text):
    return (FEWSHOT + "\n" + item_block(scene, instruction)
            + f"You: I will {action_text}\nCertain/Uncertain:")


LABEL_RE = re.compile(r"\b(uncertain|certain)\b", re.IGNORECASE)
# The model often repeats the prompt's label line, e.g. "Certain/Uncertain: Uncertain".
# That echo contains both words, so it is removed first, and the LAST label wins.
ECHO_RE = re.compile(r"certain\s*/\s*uncertain\s*:?", re.IGNORECASE)


def parse_label(text):
    cleaned = ECHO_RE.sub(" ", text or "")
    found = LABEL_RE.findall(cleaned)
    return found[-1].lower() if found else None


def make_client():
    from dotenv import load_dotenv
    from openai import OpenAI
    load_dotenv(ROOT / ".env")
    key = os.environ.get("GROQ_API_KEY")
    if not key:
        raise SystemExit("GROQ_API_KEY is not set (check .env).")
    client = OpenAI(api_key=key, base_url="https://api.groq.com/openai/v1")
    model = os.environ.get("GROQ_MODEL", "openai/gpt-oss-120b")
    return client, model


def chat(client, model, prompt, retries=6):
    delay = 2.0
    for attempt in range(retries):
        try:
            r = client.chat.completions.create(
                model=model,
                messages=[{"role": "system", "content": SYSTEM},
                          {"role": "user", "content": prompt}],
                temperature=0.0,
                max_completion_tokens=2048,
            )
            return (r.choices[0].message.content or "").strip()
        except Exception as e:  # rate limits and transient errors
            msg = str(e)
            if attempt == retries - 1:
                raise
            print(f"  API error, retrying in {delay:.0f}s: {msg[:120]}")
            time.sleep(delay)
            delay = min(delay * 2, 30)


def mock_chat(prompt):
    """Offline stand-in used by --dry-run. Deterministic, makes no network calls."""
    if prompt.rstrip().endswith("You: I will"):
        return "do what the instruction says."
    return "Uncertain" if (len(prompt) % 2 == 0) else "Certain"


def load_done(path):
    done = {}
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                r = json.loads(line)
                done[r["id"]] = r
    return done


def is_correct(category, asked):
    return asked if category == "ambiguous" else (not asked)


def summarize(rows, name):
    """rows: dicts with category, ambiguity_type, asked (True/False/None)."""
    scored = [r for r in rows if r["asked"] is not None]
    clear = [r for r in scored if r["category"] == "unambiguous"]
    amb = [r for r in scored if r["category"] == "ambiguous"]
    correct = sum(is_correct(r["category"], r["asked"]) for r in scored)
    by_type = defaultdict(lambda: [0, 0])
    for r in amb:
        by_type[r["ambiguity_type"]][1] += 1
        by_type[r["ambiguity_type"]][0] += int(r["asked"])
    extra = {}
    if any(r.get("should_ask") is not None for r in scored):
        # AmbiK rule: only Preferences ambiguity should trigger a question.
        t = defaultdict(lambda: [0, 0, 0])  # asked, total, matches should_ask
        for r in scored:
            k = r.get("ambik_type") or "?"
            t[k][1] += 1
            t[k][0] += int(r["asked"])
            t[k][2] += int(bool(r["asked"]) == bool(r["should_ask"]))
        extra["by_ambik_type_asked_total_correct"] = {k: f"{v[0]}/{v[1]} asked, {v[2]}/{v[1]} right" for k, v in sorted(t.items())}
        extra["correct_help_rate"] = round(sum(v[2] for v in t.values()) / len(scored), 4)
    return {
        **extra,
        "method": name,
        "total": len(rows),
        "unparsed": len(rows) - len(scored),
        "scored": len(scored),
        "accuracy": round(correct / len(scored), 4) if scored else None,
        "correct": correct,
        "ask_rate_on_clear": round(sum(r["asked"] for r in clear) / len(clear), 4) if clear else None,
        "asked_on_clear": f"{sum(r['asked'] for r in clear)}/{len(clear)}",
        "ask_rate_on_ambiguous": round(sum(r["asked"] for r in amb) / len(amb), 4) if amb else None,
        "asked_on_ambiguous": f"{sum(r['asked'] for r in amb)}/{len(amb)}",
        "ask_rate_by_ambiguity_type": {k: f"{v[0]}/{v[1]}" for k, v in sorted(by_type.items())},
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--dry-run", action="store_true", help="no API calls; tests the pipeline")
    ap.add_argument("--fresh", action="store_true", help="ignore saved results and start over")
    ap.add_argument("--rescore", action="store_true",
                    help="re-parse the saved raw answers and rebuild the summary; no API calls")
    ap.add_argument("--data", default=None,
                    help="instruction file to run, e.g. data/ambik/ambik_sample200_instructions.json")
    ap.add_argument("--tag", default="",
                    help="dataset name used in output file names (default: taken from the data file name)")
    args = ap.parse_args()

    data_path = Path(args.data) if args.data else DATA
    tag = args.tag or data_path.stem.removesuffix("_instructions")
    RESULTS.mkdir(exist_ok=True)
    out_jsonl = RESULTS / f"{tag}__binary__per_item.jsonl"
    out_summary = RESULTS / f"{tag}__nohelp_binary__summary.json"
    data = json.loads(data_path.read_text(encoding="utf-8"))
    if args.limit:
        data = data[: args.limit]

    out_path = out_jsonl if not args.dry_run else out_jsonl.with_name(f"{tag}__binary__DRYRUN.jsonl")
    if args.fresh and out_path.exists():
        out_path.unlink()
    done = load_done(out_path)

    if args.rescore:
        # Re-parse saved raw answers. The original file is left untouched.
        if not done:
            raise SystemExit(f"Nothing to rescore: {out_path} is missing or empty.")
        for r in done.values():
            lab = parse_label(r["binary_raw_label"])
            r["binary_label"] = lab
            r["binary_asked"] = None if lab is None else (lab == "uncertain")
        rescored_path = out_path.with_name(f"{tag}__binary__per_item_rescored.jsonl")
        rescored_path.write_text(
            "\n".join(json.dumps(r) for r in done.values()) + "\n", encoding="utf-8")
        print(f"Rescored {len(done)} saved items -> {rescored_path}")

    client = model = None
    if not args.dry_run and not args.rescore:
        client, model = make_client()
        print(f"Using Groq model: {model}")

    with out_path.open("a", encoding="utf-8") as f:
        for i, item in enumerate(data, 1):
            if args.rescore:
                break
            if item["id"] in done:
                continue
            scene, instr = item["scene_context"], item["instruction"]
            p1 = prompt_generate(scene, instr)
            a = mock_chat(p1) if args.dry_run else chat(client, model, p1)
            action_text = a.strip().split("\n")[0].strip()
            action_text = re.sub(r"^(you:\s*)?(i will\s*)", "", action_text, flags=re.IGNORECASE)
            p2 = prompt_uncertainty(scene, instr, action_text)
            raw = mock_chat(p2) if args.dry_run else chat(client, model, p2)
            label = parse_label(raw)
            rec = {
                "id": item["id"],
                "category": item["category"],
                "ambiguity_type": item.get("ambiguity_type"),
                "instruction": instr,
                "binary_action_text": action_text,
                "binary_raw_label": raw,
                "binary_label": label,
                "binary_asked": None if label is None else (label == "uncertain"),
                "ambik_type": item.get("ambik_type"),
                "should_ask": item.get("ambik_should_ask"),
            }
            f.write(json.dumps(rec) + "\n")
            f.flush()
            print(f"[{i}/{len(data)}] {item['id']}: {label}")
            done[item["id"]] = rec

    recs = [done[x["id"]] for x in data if x["id"] in done]
    summaries = []
    summaries.append(summarize(
        [{"category": r["category"], "ambiguity_type": r["ambiguity_type"], "asked": False,
          "ambik_type": r.get("ambik_type"), "should_ask": r.get("should_ask")} for r in recs],
        "no_help (never asks; no model call)"))
    summaries.append(summarize(
        [{"category": r["category"], "ambiguity_type": r["ambiguity_type"], "asked": r["binary_asked"],
          "ambik_type": r.get("ambik_type"), "should_ask": r.get("should_ask")} for r in recs],
        "binary (AmbiK-style, Groq)"))

    if INTERVENTION.exists() and tag == "own114":
        iv = {r["id"]: r for r in json.loads(INTERVENTION.read_text(encoding="utf-8"))}
        rows = []
        for r in recs:
            a = iv.get(r["id"], {}).get("action")
            rows.append({"category": r["category"], "ambiguity_type": r["ambiguity_type"],
                         "asked": None if a not in ("clarify", "execute") else (a == "clarify")})
        summaries.append(summarize(rows, "intervention planner (saved pilot run)"))

    print("\n" + json.dumps(summaries, indent=2))
    if not args.dry_run:
        out_summary.write_text(json.dumps(summaries, indent=2), encoding="utf-8")
        print(f"\nSaved {out_summary}")


if __name__ == "__main__":
    main()
