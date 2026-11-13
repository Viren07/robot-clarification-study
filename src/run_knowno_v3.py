"""
KnowNo (Ren et al. 2023, "Robots That Ask For Help"), implemented faithfully and run the same way
on every dataset.

THE METHOD, exactly as in the paper
  1. Multiple-choice generation. Given the scene, the task and the plan so far, the LLM writes four
     candidate NEXT actions, A to D. A fifth option, "E) an option not listed here", is appended, as
     the paper does, so the true answer always exists in the option set.
  2. Scoring. A second call asks the LLM to answer with one letter. `logit_bias` restricts the next
     token to A, B, C, D, E, so the probabilities come from a genuine forced choice over the options,
     as in the paper. The five letter probabilities are read from the logprobs and normalized.
  3. Split conformal prediction. On a held-out calibration set from the same distribution, the
     nonconformity score of an item is 1 - f(true option). With n calibration scores and eps = 0.2,
     qhat is the ceil((n+1)(1-eps))/n empirical quantile. The prediction set for a test item is
     {y : f(y) > 1 - qhat}.
  4. Decision. Ask for help when the prediction set holds more than one option; otherwise act.
  Nothing in steps 1 to 4 differs between datasets.

WHAT IS OUTSIDE THE METHOD (bias controls; report these, they are not changes to KnowNo)
  a. Calibration data. The paper calibrates on a held-out set from the test distribution. So each
     dataset is calibrated on its OWN held-out set: AmbiK on AmbiK's calib_100, the own* family on
     own_calib100. Reusing one dataset's cutoff on another would break the method's own assumption.
  b. Calibration labels. The paper uses human labels for the true option. We have none, so one judge
     model with one prompt labels every dataset, and a hand-checked sample gives an agreement rate.
  c. Plan steps. KnowNo is shown one step of a plan. Plans written by different authors would favour
     their own dataset, so every dataset's plans come from src/regenerate_plans.py: one model, one
     prompt. Pass the __replanned.json files.
  d. Backbone model. gpt-4o-mini for the method everywhere (the paper used models of its own era).
     Logprobs are needed, which Groq's gpt-oss-120b does not return.

Usage (after regenerate_plans.py)
  python src/run_knowno_v3.py --dry-run --calib data/own100/own_calib100_instructions__replanned.json \
      --data data/own100/own100_instructions__replanned.json --name own100
  python src/run_knowno_v3.py --calib data/ambik/ambik_calib100_instructions__replanned.json \
      --data data/ambik/ambik_sample200_instructions__replanned.json --limit 100 --name ambik100
Outputs (results/): <name>__knowno_v3__<model>__{calib,test}.jsonl and __summary.json
"""
import os
import re
import json
import math
import time
import argparse
import random
from pathlib import Path

import numpy as np

from run_knowno import call, make_client, auroc, model_tag, is_similar

ROOT = Path(__file__).resolve().parent.parent
RESULTS = Path(os.environ.get("KNOWNO_RESULTS", ROOT / "results"))
EPS = 0.2
# KnowNo's released code softmaxes the option logprobs at temperature 5 before forming the
# prediction set (language_model_uncertainty/KnowNo_*.ipynb, temperature_scaling(..., 5)).
MC_TEMPERATURE = float(os.environ.get("MC_TEMPERATURE", 5.0))
JUDGE_MODEL = os.environ.get("JUDGE_MODEL", "gpt-4o")  # labels the true option; NOT part of KnowNo
PREFIX = "You are a robot in a kitchen. The kitchen contains: "
LETTERS = ["A", "B", "C", "D", "E"]
NOT_LISTED = "an option not listed here"

SYSTEM_GEN = ("You continue a transcript exactly as the pattern in the transcript shows. "
              "Write exactly four options for the next action, labelled A), B), C) and D), one per line. "
              "The options must be meaningfully different from each other. "
              "Write nothing else: no preamble, no explanation, no option E.")
RETRY_GEN = ("Write exactly four options, labelled A), B), C) and D), one per line, and nothing else. "
             "They must be four meaningfully different ways to carry out the next action.")
SYSTEM_ANS = "Follow the instruction in the transcript. Reply with a single capital letter only."
SYSTEM_JUDGE = "You are a careful judge. Reply with JSON only."

# Few-shot scenes deliberately outside every dataset's domain (a laundry room, an office, a garage),
# so the examples prime neither AmbiK nor the own* family.
GEN_FEWSHOT = (
    "We: You are a robot operating in a laundry room.\n"
    "We: In the room there is a washing machine, a dryer, a basket of white shirts, a basket of dark jeans, "
    "a bottle of detergent and a laundry hamper.\n"
    "We: You have received the task “Wash the white shirts.” You created a plan to complete the task. "
    "Your first action is:\n1. Take the white shirts to the washing machine.\nYou:\n"
    "A) pick up the basket of dark jeans\nB) pick up the basket of white shirts\n"
    "C) pick up the laundry hamper\nD) pick up the bottle of detergent\n\n"
    "We: You are a robot operating in an office.\n"
    "We: In the office there is a printer, a stack of letter paper, a stack of legal paper, a stapler, "
    "a budget report file and a schedule file.\n"
    "We: You have received the task “Print the budget report on letter paper and staple it.” You created a "
    "plan to complete the task. Your previous actions were:\n1. Load letter paper into the printer.\n"
    "2. Print the budget report.\nYour next action is:\n3. Staple the printed pages.\nYou:\n"
    "A) pick up the stapler and staple the schedule file\nB) put the printed pages on the stack of legal paper\n"
    "C) leave the printed pages unstapled\nD) pick up the stapler and staple the printed pages\n\n"
    "We: You are a robot operating in a garage.\n"
    "We: In the garage there is a bicycle, a hand pump, a wrench, a screwdriver and a helmet.\n"
    "We: You have received the task “Inflate the front tire of the bicycle.” You created a plan to complete "
    "the task. Your previous actions were:\n1. Take the hand pump from the shelf.\nYour next action is:\n"
    "2. Attach the pump to the front tire.\nYou:\n"
    "A) attach the hand pump to the front tire of the bicycle\n"
    "B) attach the hand pump to the rear tire of the bicycle\n"
    "C) attach the wrench to the front tire of the bicycle\n"
    "D) attach the screwdriver to the front tire of the bicycle\n\n"
)

GEN_TASK = ("We: You are a robot operating in a kitchen.\nWe: In the kitchen there is <ENV>.\n"
            "We: You have received the task “<TASK>” You created a plan to complete the task. "
            "<PREFIX>\n<ACT>\nYou:\n")

ANS_TEMPLATE = ("We: You are a robot operating in a kitchen.\nWe: In the kitchen there is <ENV>.\n"
                "We: You have received the task “<TASK>” You created a plan to complete the task. "
                "<PREFIX>\n<ACT>\n\nOptions:\n<OPTIONS>\n"
                "What will you do, A or B or C or D or E? Answer with a single capital letter.")

JUDGE_TEMPLATE = (
    "A robot is in a kitchen that contains: <ENV>.\n"
    "The robot received this instruction: “<TASK>”\n"
    "It has already done:\n<DONE>\n"
    "Its intended next step is: <ACT>\n\n"
    "Options for how to carry out that next step:\n<OPTIONS>\n"
    "E) " + NOT_LISTED + "\n\n"
    "Which options correctly carry out the intended next step in this kitchen? An option is correct if it "
    "performs that step, uses only objects present in the kitchen, and makes no choice the instruction "
    "rules out. Choose E if and only if no option A to D is correct.\n"
    "Reply with JSON only, for example {\"correct\": [\"A\", \"C\"]}.")

OPT_RE = re.compile(r"^\s*([A-D])\)\s*(.+?)\s*$", re.MULTILINE)


def env_of(scene):
    s = scene[len(PREFIX):] if scene.startswith(PREFIX) else scene
    return s.strip().rstrip(".")


def prefix_and_action(plan_steps, step):
    """As in KnowNo's multi-step setting: show the steps already done, ask about the next one."""
    step = max(0, min(int(step), len(plan_steps) - 1))
    if step == 0:
        return "Your first action is:", plan_steps[0], "nothing yet"
    done = "".join(f"{i + 1}. {a}\n" for i, a in enumerate(plan_steps[:step]))
    return "Your previous actions were:\n" + done + "Your next action is:", plan_steps[step], done.strip()


def parse_options(text):
    opts = {}
    for k, v in OPT_RE.findall(text or ""):
        opts.setdefault(k, v)
    return opts


def fmt(options):
    return "".join(f"{k}) {v}\n" for k, v in options.items())


def letter_probs_from(logprob_content, letters):
    """Normalized probabilities over the option letters. logit_bias makes these the whole mass."""
    acc = {k: 0.0 for k in letters}
    for t in logprob_content[0].top_logprobs:
        tok = t.token.strip().upper()
        if tok in acc:
            acc[tok] += math.exp(t.logprob)
    tot = sum(acc.values())
    return {k: v / tot for k, v in acc.items()} if tot > 0 else None


def options_matching_intent(options, user_intent):
    """The true options, from the dataset's own user_intent, using AmbiK's is_similar matcher:
    ", " means every keyword must appear, "|" means any of them, a leading "-" means it must not.
    Returns ["E"] when no generated option matches the intent, which is the correct reading of
    "an option not listed here". No model is involved, so this is identical on every dataset."""
    pats = [x.strip() for x in str(user_intent or "").split("\n") if x.strip() and x.strip() != "nan"]
    if not pats:
        return None
    hit = [k for k, v in options.items() if any(is_similar(v, p) for p in pats)]
    return hit or ["E"]


def run_item(client, model, judge_model, item, dry, truth="intent"):
    """Two calls with truth="intent" (generate, score). Three with truth="judge"."""
    env = env_of(item["scene_context"])
    task = item["instruction"]
    pfx, act, done = prefix_and_action(item["plan_steps"], item.get("ambiguity_step", 0))
    if dry:
        rnd = random.Random(len(task) * 13 + len(env))
        options = {k: f"option {k}" for k in "ABCD"}
        raw = [rnd.random() ** 3 for _ in LETTERS]
        s = sum(raw)
        return {"options": options, "probs": {k: v / s for k, v in zip(LETTERS, raw)},
                "true_options": [rnd.choice(LETTERS)], "raw_generation": "dry", "raw_judge": "dry",
                "judge_model": judge_model, "shown_step": act, "failed": False}

    g = GEN_TASK.replace("<ENV>", env).replace("<TASK>", task).replace("<PREFIX>", pfx).replace("<ACT>", act)
    r1 = call(client, model, SYSTEM_GEN, GEN_FEWSHOT + g, max_completion_tokens=400, stop=["We:"])
    text = r1.choices[0].message.content or ""
    options = parse_options(text)
    if len(options) < 2:  # KnowNo needs four candidates; re-ask once before giving up
        r1b = call(client, model, SYSTEM_GEN + " " + RETRY_GEN, GEN_FEWSHOT + g,
                   max_completion_tokens=400, stop=["We:"])
        t2 = r1b.choices[0].message.content or ""
        if len(parse_options(t2)) > len(options):
            text, options = t2, parse_options(t2)
        text = text + "\n<<retry>>"
    out = {"options": options, "probs": None, "true_options": None, "raw_generation": text,
           "raw_judge": None, "judge_model": judge_model, "shown_step": act, "failed": True}
    if len(options) < 2:
        out["failed"] = True
        return out
    # The generator writes its most plausible option first, so A would otherwise be the answer
    # almost every time. Shuffle which letter each option is shown under, deterministically per item.
    gen_order = [v for _, v in sorted(options.items())]
    perm = list(range(len(gen_order)))
    random.Random(f"knowno|{task}|{act}").shuffle(perm)
    options = {chr(65 + i): gen_order[perm[i]] for i in range(len(gen_order))}
    out["options"] = options
    out["generated_order"] = gen_order
    out["shown_letter_to_generated_index"] = perm
    full = dict(options)
    full["E"] = NOT_LISTED

    a = (ANS_TEMPLATE.replace("<ENV>", env).replace("<TASK>", task).replace("<PREFIX>", pfx)
         .replace("<ACT>", act).replace("<OPTIONS>", fmt(full)))
    # logit_bias forces the answer token to be one of the option letters, as the paper does.
    bias = {str(t): 100 for t in LETTER_TOKEN_IDS}
    r2 = call(client, model, SYSTEM_ANS, a, max_completion_tokens=1, logprobs=True, top_logprobs=20,
              logit_bias=bias)
    out["probs"] = letter_probs_from(r2.choices[0].logprobs.content, list(full.keys()))

    j = (JUDGE_TEMPLATE.replace("<ENV>", env).replace("<TASK>", task).replace("<DONE>", done)
         .replace("<ACT>", act).replace("<OPTIONS>", fmt(options)))
    r3 = call(client, judge_model, SYSTEM_JUDGE, j, max_completion_tokens=40)
    jt = r3.choices[0].message.content or ""
    out["raw_judge"] = jt
    m = re.search(r"\{.*\}", jt, re.DOTALL)
    try:
        v = json.loads(m.group(0))["correct"] if m else None
        v = [x for x in v if x in full] if isinstance(v, list) else None
        out["true_options"] = v if v else ["E"]
    except Exception:
        out["true_options"] = None
    out["failed"] = out["probs"] is None or out["true_options"] is None
    return out


# token ids for " A".."E" and "A".."E" are model-specific; resolved once with tiktoken when available.
LETTER_TOKEN_IDS = []


def resolve_letter_tokens(model):
    global LETTER_TOKEN_IDS
    try:
        import tiktoken
        enc = tiktoken.encoding_for_model(model)
    except Exception:
        try:
            import tiktoken
            enc = tiktoken.get_encoding("o200k_base")
        except Exception:
            print("  tiktoken unavailable: running without logit_bias (probabilities are renormalized "
                  "over the letters instead). Report this deviation.")
            return
    ids = set()
    for L in LETTERS:
        for form in (L, " " + L):
            t = enc.encode(form)
            if len(t) == 1:
                ids.add(t[0])
    LETTER_TOKEN_IDS = sorted(ids)
    print(f"  logit_bias on {len(LETTER_TOKEN_IDS)} letter tokens")


def scaled(probs, T=None):
    """Apply KnowNo's temperature scaling to the option distribution.

    Stored probs are softmax(logprob) at T=1. softmax(log p / T) equals softmax(logprob / T),
    because the additive constant normalization removed cancels, so no rerun is needed to
    change T.
    """
    T = MC_TEMPERATURE if T is None else T
    if T == 1.0:
        return dict(probs)
    ks = list(probs)
    l = np.array([math.log(max(float(probs[k]), 1e-12)) for k in ks]) / T
    l = l - l.max()
    e = np.exp(l)
    return {k: float(v) for k, v in zip(ks, e / e.sum())}


def nonconformity(rec):
    """1 - f(true option). With several true options, the most probable one, as the set must cover one."""
    p = scaled(rec["probs"])
    return 1.0 - max(p.get(k, 0.0) for k in rec["true_options"])


def qhat_from(scores):
    n = len(scores)
    level = min(1.0, math.ceil((n + 1) * (1 - EPS)) / n)
    return float(np.quantile(scores, level, method="higher")), n, level


def wilson(k, n):
    if not n:
        return None
    p, z = k / n, 1.96
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [round(c - h, 3), round(c + h, 3)]


def load(paths, limit=None):
    out = []
    for p in paths:
        d = json.loads((ROOT / p).read_text(encoding="utf-8"))
        out += d if isinstance(d, list) else d["items"]
    return out[:limit] if limit else out



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

def pass_over(client, model, judge, items, path, dry, retry_failed, label, fresh=False, truth="intent"):
    done = {}
    src = find_cache(path)
    if src.exists() and not dry and not fresh:
        for line in src.read_text(encoding="utf-8").splitlines():
            if line.strip():
                r = json.loads(line)
                if r.get("model") == "dry-run" or (retry_failed and r.get("failed")):
                    continue
                # true_options is BAKED INTO the cached row, so a row labelled by the judge must
                # never be reused for a --truth intent run, or the run silently reports one
                # ground truth while using the other. A judge row is identifiable by raw_judge.
                was_judge = bool(r.get("raw_judge"))
                if was_judge != (truth == "judge"):
                    continue
                done[r["id"]] = r
    for i, it in enumerate(items):
        if it["id"] in done:
            continue
        if "plan_steps" not in it or not it["plan_steps"]:
            raise SystemExit(f"{it['id']} has no plan_steps. Run src/regenerate_plans.py first and pass "
                             f"the __replanned.json file.")
        res = run_item(client, model, judge, it, dry, truth)
        rec = {"id": it["id"], "category": it["category"], "ambiguity_type": it.get("ambiguity_type"),
               "instruction": it["instruction"], "model": model, **res}
        if "ambik_should_ask" in it:
            rec["ambik_should_ask"] = it["ambik_should_ask"]
        done[it["id"]] = rec
        print(f"[{label} {i + 1}/{len(items)}] {it['id']}: opts={len(res['options'])} "
              f"true={res['true_options']} failed={res['failed']}")
    recs = [done[it["id"]] for it in items if it["id"] in done]
    with path.open("w", encoding="utf-8") as f:
        for r in recs:
            f.write(json.dumps(r) + "\n")
    return recs


def summarize(test, qhat, n_cal, level, model, judge, name, calib_name, scale=True):
    ok = [r for r in test if not r["failed"]]
    for r in ok:
        p = scaled(r["probs"]) if scale else dict(r["probs"])
        r["probs_scaled"] = p
        r["pred_set"] = [k for k, v in p.items() if v >= 1 - qhat]
        # KnowNo's own rule (KnowNo_MobileManipulation.ipynb):
        #   flag_help = len(prediction_set) != 1 or add_mc_prefix in prediction_set
        # so help is triggered when the set is not exactly one option, OR when it contains
        # option E at all. A lone E means the model's best guess is "none of these", which is
        # not something it can act on.
        r["asked"] = len(r["pred_set"]) != 1 or "E" in r["pred_set"]
        r["covered"] = any(k in r["pred_set"] for k in r["true_options"])
    clear = [r for r in ok if r["category"] == "unambiguous"]
    amb = [r for r in ok if r["category"] == "ambiguous"]
    ac, aa = sum(r["asked"] for r in clear), sum(r["asked"] for r in amb)
    out = {"method": "knowno (Ren et al. 2023), split conformal", "backbone": model, "judge_model": judge,
           "dataset": name, "calibration_set": calib_name, "eps": EPS, "calibration_items_used": n_cal,
           "quantile_level": round(level, 4), "qhat": round(qhat, 6),
           "keep_if_p_at_least": round(1 - qhat, 6), "mc_temperature": (MC_TEMPERATURE if scale else "pre-scaled by caller"),
           "items": len(test), "failed": len(test) - len(ok),
           "asked_on_clear": f"{ac}/{len(clear)}", "asked_on_clear_ci95": wilson(ac, len(clear)),
           "asked_on_ambiguous": f"{aa}/{len(amb)}", "asked_on_ambiguous_ci95": wilson(aa, len(amb)),
           "empirical_coverage_on_test": round(sum(bool(r["covered"]) for r in ok) / max(1, len(ok)), 3),
           "target_coverage": round(1 - EPS, 3)}
    if clear and amb:
        out["balanced_accuracy"] = round(((1 - ac / len(clear)) + aa / len(amb)) / 2, 4)
        rnd = random.Random(1)
        bs = [((1 - sum(rnd.choice(clear)["asked"] for _ in clear) / len(clear))
               + sum(rnd.choice(amb)["asked"] for _ in amb) / len(amb)) / 2 for _ in range(2000)]
        out["balanced_accuracy_ci95"] = [round(float(np.percentile(bs, 2.5)), 3),
                                         round(float(np.percentile(bs, 97.5)), 3)]
    by = {}
    for r in amb:
        by.setdefault(r.get("ambiguity_type") or "?", [0, 0])
        by[r.get("ambiguity_type") or "?"][0] += r["asked"]
        by[r.get("ambiguity_type") or "?"][1] += 1
    out["ask_rate_by_ambiguity_type"] = {t: f"{a}/{n}" for t, (a, n) in sorted(by.items())}
    if ok and all("ambik_should_ask" in r for r in ok):
        pos = [r for r in ok if r["ambik_should_ask"]]
        neg = [r for r in ok if not r["ambik_should_ask"]]
        if pos and neg:
            out["balanced_accuracy_ambik_rule"] = round(
                (sum(r["asked"] for r in pos) / len(pos) + sum(not r["asked"] for r in neg) / len(neg)) / 2, 4)
    uns = lambda r: 1 - max((scaled(r["probs"]) if scale else r["probs"]).values())
    cl = [uns(r) for r in clear]
    groups = {"all_ambiguous": amb}
    for r in amb:
        groups.setdefault(r.get("ambiguity_type") or "?", []).append(r)
    out["auroc_ambiguous_vs_clear"] = {g: {"n": len(rs), "auroc": auroc([uns(r) for r in rs], cl)}
                                       for g, rs in groups.items()}
    return out


def main():
    global MC_TEMPERATURE
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", nargs="+", required=True, help="test instructions (__replanned.json)")
    ap.add_argument("--calib", nargs="+", required=True, help="held-out calibration instructions (__replanned.json)")
    ap.add_argument("--name", required=True)
    ap.add_argument("--limit", type=int, default=None, help="limit on the TEST set only")
    ap.add_argument("--judge-model", default=JUDGE_MODEL)
    ap.add_argument("--truth", default="intent", choices=["intent", "judge"],
                    help="intent: the true option comes from the dataset's user_intent, matched with "
                         "AmbiK's is_similar. judge: an LLM decides (kept only for comparison; it "
                         "returns E on about a third of items, which drives the cutoff).")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--retry-failed", action="store_true")
    ap.add_argument("--fresh", action="store_true", help="ignore cached per-item results and re-run")
    ap.add_argument("--mc-temperature", type=float, default=MC_TEMPERATURE,
                    help="softmax temperature over the option letters; KnowNo's released code uses 5")
    args = ap.parse_args()
    MC_TEMPERATURE = args.mc_temperature

    if args.dry_run:
        client, model = None, "dry-run"
    else:
        client, model = make_client()
        resolve_letter_tokens(model)
    print(f"backbone: {model} | truth: {args.truth} | option temperature: {MC_TEMPERATURE}")

    cal_items = load(args.calib)
    test_items = load(args.data, args.limit)
    if args.truth == "intent":
        missing = [n for n, items in (("calibration", cal_items), ("test", test_items))
                   if not any(x.get("user_intent") for x in items)]
        if missing:
            raise SystemExit(
                f"--truth intent needs a user_intent on every item, and the {' and '.join(missing)} set "
                f"has none.\nAmbiK ships user_intent; our datasets do not yet have intents written.\n"
                f"Either run on the AmbiK files, or pass --truth judge and read the caveat in "
                f"docs/implementation_audit.md (the judge returns 'no matching option' on roughly a "
                f"third of items, and that is what sets the cutoff).")
    RESULTS.mkdir(exist_ok=True)
    tsfx = "" if args.truth == "intent" else f"__truth-{args.truth}"
    tag = (f"{args.name}__knowno_v3__{model_tag(model)}{tsfx}"
           + ("__DRYRUN" if args.dry_run else ""))
    cal_name = Path(args.calib[0]).stem

    cal = pass_over(client, model, args.judge_model, cal_items,
                    RESULTS / f"{cal_name}__knowno_v3__{model_tag(model)}{tsfx}__calib.jsonl", args.dry_run,
                    args.retry_failed, "calib", args.fresh, args.truth)
    scores = [nonconformity(r) for r in cal if not r["failed"]]
    if len(scores) < 20:
        raise SystemExit(f"Only {len(scores)} usable calibration items.")
    qhat, n_cal, level = qhat_from(scores)
    print(f"\ncalibration: n={n_cal} level={level:.4f} qhat={qhat:.6f} -> keep options with p > {1 - qhat:.6f}\n")

    test = pass_over(client, model, args.judge_model, test_items,
                     RESULTS / f"{tag}__test.jsonl", args.dry_run, args.retry_failed, "test",
                     args.fresh, args.truth)
    summ = summarize(test, qhat, n_cal, level, model, args.judge_model, args.name, cal_name)
    # Report what the rows were ACTUALLY labelled with, not what was asked for on the command
    # line. Recording the flag is what let a stale judge-labelled cache be reported as
    # intent-labelled: the flag said "intent" while every row carried a judge answer.
    usable = [r for r in cal if not r["failed"]]
    judged = sum(1 for r in usable if r.get("raw_judge"))
    actual = ("judge" if judged == len(usable) else
              "intent" if judged == 0 else f"MIXED ({judged}/{len(usable)} judge-labelled)")
    summ["truth_source_requested"] = args.truth
    summ["truth_source_actually_used"] = actual
    if actual != args.truth:
        summ["TRUTH_SOURCE_MISMATCH"] = (
            f"asked for {args.truth} but the calibration rows are {actual}. A stale cache was "
            f"reused. Delete the cache files for this dataset and rerun with --fresh.")
        print(f"\n*** WARNING: {summ['TRUTH_SOURCE_MISMATCH']}\n")
    n_e = sum(1 for r in usable if r["true_options"] == ["E"])
    # The share of calibration items where no generated option matched the user's intent. These
    # items get a nonconformity near 1 and so they are what sets the cutoff. Watch it: if it
    # differs a lot between datasets, the comparison is being driven by the matcher, not the data.
    summ["calibration_items_with_no_matching_option"] = f"{n_e}/{len(usable)}"
    summ["calibration_mean_true_options"] = round(
        sum(len(r["true_options"]) for r in usable) / max(1, len(usable)), 3)
    (RESULTS / f"{tag}__summary.json").write_text(json.dumps(summ, indent=2), encoding="utf-8")
    print(json.dumps(summ, indent=2))
    print("Saved", RESULTS / f"{tag}__summary.json")


if __name__ == "__main__":
    main()
