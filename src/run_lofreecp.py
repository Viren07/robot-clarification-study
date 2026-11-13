"""
LofreeCP (Su et al. 2024, arXiv:2403.01216), "API Is Enough: Conformal Prediction for Large
Language Models Without Logit-Access".

THE METHOD, as in the paper
  1. Sample the model m times for the same prompt (m = 20 in the paper). Merge identical responses
     into a pool of distinct candidates. No logits are used anywhere.
  2. Score each distinct response with three signals:
       F  frequency, the share of the m samples equal to that response (coarse-grained).
       NE normalized entropy of the response-frequency distribution for the prompt, |H / log m|.
          Prompt-level, so it is the same for every response of that prompt.
       SS semantic similarity, the cosine similarity between a response's embedding and the
          embedding of the most frequent (top-1) response. Response-level.
  3. Nonconformity N = -F + lambda1 * NE - lambda2 * SS. Lower means more confident.
  4. lambda1 and lambda2 are searched on a validation split over a 0 to 2 grid in steps of 0.05.
  5. Split conformal: for each calibration prompt, the true answer's score if it is in the pool,
     otherwise infinity. qhat is the ceil((n+1)(1-eps))/n quantile of those scores.
  6. Prediction set = { y : N(y) <= qhat }. Act if it holds one response, otherwise ask.

OUTSIDE THE METHOD (bias controls, identical on every dataset; report these)
  a. Per-dataset calibration, split in half: 50 items set qhat, 50 tune lambda. The paper splits one
     pool 50/25/25 into calibration, validation and test; our test sets are separate files already,
     so the held-out calibration set plays the first two roles and the test set stays whole.
  b. The true answer is labelled by a judge model (gpt-4o), with the same prompt on every dataset,
     as for KnowNo and LAP. The paper's benchmarks ship gold answers; ours do not.
  c. The paper uses 200-dimensional FastText vectors for SS. --embedder fasttext reproduces that
     (300-dimensional wiki-news vectors via gensim, the closest readily available). The default,
     openai, uses text-embedding-3-small, which needs no multi-gigabyte download. State which was
     used; the same embedder runs on every dataset either way.
  d. lambda is tuned to the smallest mean prediction-set size among grid points whose validation
     coverage reaches 1 - eps. The paper does not state its tuning objective.
  e. Sampling temperature 1.0, which is what self-consistency sampling requires. Every other method
     here runs at temperature 0.

Per item: 3 calls (one sampling call returning m completions, one embedding call, one judge call).

Usage
  python src/run_lofreecp.py --name own100 \
    --calib data/own100/own_calib100_instructions__replanned.json \
    --data  data/own100/own100_instructions__replanned.json
Outputs (results/): <name>__lofreecp__<model>__{calib,test}.jsonl and __summary.json
"""
import os
import re
import json
import math
import random
import argparse
from pathlib import Path

import numpy as np

import time

from run_knowno import call, make_client, model_tag, is_similar
from run_knowno_v3 import EPS, JUDGE_MODEL, env_of, prefix_and_action, qhat_from, wilson, load
from run_knowno import auroc

ROOT = Path(__file__).resolve().parent.parent
RESULTS = Path(os.environ.get("KNOWNO_RESULTS", ROOT / "results"))
M_SAMPLES = 20
TEMP = 1.0
GRID = [round(x * 0.05, 2) for x in range(41)]  # 0.00 .. 2.00, the paper's grid
EMBED_MODEL = os.environ.get("EMBED_MODEL", "text-embedding-3-small")

SYSTEM_SAMPLE = ("You continue a transcript exactly as the pattern in the transcript shows. "
                 "Write only the single next action, on one line, and nothing else.")
SYSTEM_JUDGE = "You are a careful judge. Reply with JSON only."

SAMPLE_FEWSHOT = (
    "We: You are a robot operating in a laundry room.\n"
    "We: In the room there is a washing machine, a dryer, a basket of white shirts, a basket of "
    "dark jeans, a bottle of detergent and a laundry hamper.\n"
    "We: You have received the task “Wash the white shirts.” You created a plan to complete the "
    "task. Your first action is:\n1. Take the white shirts to the washing machine.\n"
    "You: pick up the basket of white shirts\n\n"
    "We: You are a robot operating in an office.\n"
    "We: In the office there is a printer, a stack of letter paper, a stack of legal paper, a "
    "stapler, a budget report file and a schedule file.\n"
    "We: You have received the task “Print the budget report on letter paper and staple it.” You "
    "created a plan to complete the task. Your previous actions were:\n"
    "1. Load letter paper into the printer.\n2. Print the budget report.\nYour next action is:\n"
    "3. Staple the printed pages.\nYou: pick up the stapler and staple the printed pages\n\n"
    "We: You are a robot operating in a garage.\n"
    "We: In the garage there is a bicycle, a hand pump, a wrench, a screwdriver and a helmet.\n"
    "We: You have received the task “Inflate the front tire of the bicycle.” You created a plan to "
    "complete the task. Your previous actions were:\n1. Take the hand pump from the shelf.\n"
    "Your next action is:\n2. Attach the pump to the front tire.\n"
    "You: attach the hand pump to the front tire of the bicycle\n\n"
)
SAMPLE_TASK = ("We: You are a robot operating in a kitchen.\nWe: In the kitchen there is <ENV>.\n"
               "We: You have received the task “<TASK>” You created a plan to complete the task. "
               "<PREFIX>\n<ACT>\nYou:")

JUDGE_TEMPLATE = (
    "A robot is in a kitchen that contains: <ENV>.\n"
    "The robot received this instruction: “<TASK>”\n"
    "It has already done:\n<DONE>\n"
    "Its intended next step is: <ACT>\n\n"
    "Candidate actions:\n<OPTIONS>\n"
    "Which candidates correctly carry out the intended next step in this kitchen? A candidate is "
    "correct if it performs that step, uses only objects present in the kitchen, and makes no choice "
    "the instruction rules out.\n"
    "Reply with JSON only, for example {\"correct\": [1, 3]}, using the candidate numbers. "
    "Use an empty list if none is correct.")


def sample_call(client, model, system, user, retries=6, **kw):
    """Own wrapper: run_knowno.call fixes temperature=0, and LofreeCP must sample."""
    delay = 2.0
    for attempt in range(retries):
        try:
            return client.chat.completions.create(
                model=model, messages=[{"role": "system", "content": system},
                                       {"role": "user", "content": user}], **kw)
        except Exception as e:
            if attempt == retries - 1:
                raise
            print(f"  API error, retrying in {delay:.0f}s: {str(e)[:120]}")
            time.sleep(delay)
            delay = min(delay * 2, 30)


def norm(s):
    s = (s or "").strip().lower()
    s = re.sub(r"^\d+[.)]\s*", "", s)
    s = re.sub(r"\s+", " ", s).strip(" .\"'")
    return s


_FT = {"model": None}


def embed(client, texts, backend):
    if backend == "dry":
        import random as _r
        return [np.asarray([_r.Random(t).random() for _ in range(8)], dtype=float) for t in texts]
    if backend == "fasttext":
        if _FT["model"] is None:
            import gensim.downloader as api
            print("  loading FastText vectors (one-time download, about 1 GB) ...")
            _FT["model"] = api.load("fasttext-wiki-news-subwords-300")
        kv = _FT["model"]
        out = []
        for t in texts:
            ws = [w for w in re.findall(r"[a-z']+", t) if w in kv]
            out.append(np.mean([kv[w] for w in ws], axis=0) if ws else np.zeros(kv.vector_size))
        return [np.asarray(v, dtype=float) for v in out]
    r = client.embeddings.create(model=EMBED_MODEL, input=texts)
    return [np.asarray(d.embedding, dtype=float) for d in r.data]


def cos(a, b):
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    return float(np.dot(a, b) / (na * nb)) if na > 0 and nb > 0 else 0.0


def responses_matching_intent(responses, user_intent):
    """Indices of the sampled responses that carry out the user's actual intent, using AmbiK's
    is_similar matcher on the dataset's user_intent. Empty list means the true answer was not in
    the sampled pool, which is the paper's N = infinity case. None means the item has no intent."""
    pats = [x.strip() for x in str(user_intent or "").split("\n") if x.strip() and x.strip() != "nan"]
    if not pats:
        return None
    return [i for i, r in enumerate(responses) if any(is_similar(" " + r, p) for p in pats)]


def run_item(client, model, judge_model, item, backend, truth="intent", dry=False):
    env = env_of(item["scene_context"])
    task = item["instruction"]
    pfx, act, done = prefix_and_action(item["plan_steps"], item.get("ambiguity_step", 0))
    user = (SAMPLE_FEWSHOT + SAMPLE_TASK.replace("<ENV>", env).replace("<TASK>", task)
            .replace("<PREFIX>", pfx).replace("<ACT>", act))
    if dry:
        import random as _r
        rnd = _r.Random(item["id"])
        pool = [f"do variant {i} of {act[:18]}" for i in range(4)] + [act.lower().strip(" .")]
        samples = [norm(rnd.choice(pool)) for _ in range(M_SAMPLES)]
        backend = "dry"
    else:
        r = sample_call(client, model, SYSTEM_SAMPLE, user, max_completion_tokens=60, n=M_SAMPLES,
                        temperature=TEMP, stop=["We:"])
        samples = [norm(c.message.content) for c in r.choices]
    samples = [s for s in samples if s]
    out = {"n_samples": len(samples), "shown_step": act, "failed": True,
           "responses": None, "freq": None, "ne": None, "ss": None, "true_idx": None}
    if len(samples) < 2:
        return out

    counts = {}
    for s in samples:
        counts[s] = counts.get(s, 0) + 1
    resp = sorted(counts, key=lambda k: (-counts[k], k))
    m = len(samples)
    freq = {s: counts[s] / m for s in resp}
    p = np.array([freq[s] for s in resp])
    ne = abs(float(-(p * np.log(p)).sum() / math.log(m))) if m > 1 else 0.0

    vecs = embed(client, resp, backend)
    top = vecs[0]
    # The top-1 response gets no similarity term. The paper only says it "is not compared with
    # itself"; AmbiK's implementation sets it to 0 and the authors' own code gives it no usable
    # value either, so 0 is the reading both released versions agree on.
    ss = {s: (0.0 if i == 0 else cos(vecs[i], top)) for i, s in enumerate(resp)}

    if truth == "intent":
        true_idx = responses_matching_intent(resp, item.get("user_intent"))
        jt, src = None, "dataset user_intent (is_similar match)"
    else:
        opts = "".join(f"{i + 1}) {s}\n" for i, s in enumerate(resp))
        j = (JUDGE_TEMPLATE.replace("<ENV>", env).replace("<TASK>", task).replace("<DONE>", done)
             .replace("<ACT>", act).replace("<OPTIONS>", opts))
        rj = call(client, judge_model, SYSTEM_JUDGE, j, max_completion_tokens=60)
        jt = rj.choices[0].message.content or ""
        src = f"judge model {judge_model}"
        mm = re.search(r"\{.*\}", jt, re.DOTALL)
        true_idx = None
        if mm:
            try:
                v = json.loads(mm.group(0)).get("correct")
                if isinstance(v, list):
                    true_idx = [int(x) - 1 for x in v if isinstance(x, (int, float))
                                and 1 <= int(x) <= len(resp)]
            except Exception:
                true_idx = None
    out.update({"responses": resp, "freq": freq, "ne": ne, "ss": ss, "true_idx": true_idx,
                "raw_judge": jt, "judge_model": judge_model, "truth_source": src,
                "embedder": backend, "failed": true_idx is None})
    return out


FORMULA = "paper"


def scores_of(rec, l1, l2, formula=None):
    """Nonconformity per distinct response. Lower means more confident.

    paper    N = -F + l1*NE - l2*SS                 (arXiv:2403.01216, Eq. 8)
    released N = 10 - 10*F + (NE/2)*l1 - SS*l2      (the authors' run_cp.py, new_CP_score)
    The two are NOT equivalent: the released code scales F by 10 and halves NE, which changes how
    much each signal counts once a single quantile is applied. Both are provided so the paper can
    report either, and `--formula` selects one.
    """
    f = formula or FORMULA
    if f == "released":
        return {s: 10 - 10 * rec["freq"][s] + (rec["ne"] / 2) * l1 - rec["ss"][s] * l2
                for s in rec["responses"]}
    return {s: -rec["freq"][s] + l1 * rec["ne"] - l2 * rec["ss"][s] for s in rec["responses"]}


def true_score(rec, l1, l2):
    if not rec["true_idx"]:
        return math.inf
    sc = scores_of(rec, l1, l2)
    return min(sc[rec["responses"][i]] for i in rec["true_idx"])


def tune(cal, val):
    """Smallest mean set size among grid points whose validation coverage reaches 1 - EPS."""
    best = None
    for l1 in GRID:
        for l2 in GRID:
            s = [true_score(r, l1, l2) for r in cal]
            fin = [x for x in s if math.isfinite(x)]
            if len(fin) < 10:
                continue
            q, _, _ = qhat_from([min(x, 1e6) for x in s])
            sizes, cov = [], []
            for r in val:
                sc = scores_of(r, l1, l2)
                keep = [k for k, v in sc.items() if v <= q]
                sizes.append(len(keep))
                cov.append(bool(r["true_idx"]) and any(r["responses"][i] in keep for i in r["true_idx"]))
            c = float(np.mean(cov)) if cov else 0.0
            sz = float(np.mean(sizes)) if sizes else 1e9
            cand = (0 if c >= 1 - EPS else 1, sz, -c, l1, l2, q)
            if best is None or cand < best:
                best = cand
    if best is None:
        raise SystemExit("lambda search found no usable grid point.")
    _, sz, negc, l1, l2, q = best
    return l1, l2, q, sz, -negc



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

def pass_over(client, model, judge, items, path, backend, fresh, label, truth="intent", dry=False):
    done = {}
    src = find_cache(path)
    if src.exists() and not fresh:
        for line in src.read_text(encoding="utf-8").splitlines():
            if line.strip():
                r = json.loads(line)
                want = "dataset user_intent" if truth == "intent" else "judge model"
                if not str(r.get("truth_source") or "").startswith(want):
                    continue    # cached under a different ground truth; recompute instead
                if not r.get("failed"):
                    done[r["id"]] = r
    recs = []
    for i, it in enumerate(items):
        if it["id"] in done:
            recs.append(done[it["id"]])
            continue
        if not it.get("plan_steps"):
            raise SystemExit(f"{it['id']} has no plan_steps. Use the __replanned.json files.")
        res = run_item(client, model, judge, it, backend, truth, dry)
        rec = {"id": it["id"], "category": it["category"], "ambiguity_type": it.get("ambiguity_type"),
               "instruction": it["instruction"], "model": model, **res}
        if "ambik_should_ask" in it:
            rec["ambik_should_ask"] = it["ambik_should_ask"]
        recs.append(rec)
        done[it["id"]] = rec
        print(f"[{label} {i + 1}/{len(items)}] {it['id']}: distinct={len(res['responses'] or [])} "
              f"NE={res['ne'] if res['ne'] is None else round(res['ne'], 3)} true={res['true_idx']}")
    with path.open("w", encoding="utf-8") as f:
        for r in recs:
            f.write(json.dumps(r) + "\n")
    return recs


def summarize_lofreecp(test, cal, qhat, l1, l2, n_cal, model, judge, name, calib_name, backend):
    """Everything computed from LofreeCP's own rule, N <= qhat. Nothing borrowed from KnowNo's."""
    ok = [r for r in test if not r["failed"]]
    for r in ok:
        sc = scores_of(r, l1, l2)
        r["nonconformity"] = sc
        r["true_responses"] = [r["responses"][i] for i in (r["true_idx"] or [])]
        r["pred_set"] = [resp for resp, v in sc.items() if v <= qhat]
        # AmbiK's own rules, copied from their metrics.py so the empty-set case follows their
        # precedent rather than our judgement (AmbiK-dataset @ cog-model, metrics.py):
        #
        #   help_rate(a)             -> 1 if len(a) > 1 else 0                      (lines 224-227)
        #   correct_help_rate(a, t)  -> unambiguous: correct iff len(a) == 1        (lines 200-210)
        #                               ambiguous:   correct iff len(a) >  1
        #
        # Note these are NOT mirror images. On a clear item AmbiK require EXACTLY one surviving
        # response, so an empty prediction set is wrong on a clear item AND wrong on an ambiguous
        # one. An empty set arises at maximum uncertainty (nothing cleared the threshold), and
        # AmbiK's rule credits it nowhere. We follow that.
        r["asked"] = len(r["pred_set"]) > 1
        r["correct"] = (len(r["pred_set"]) == 1 if r["category"] == "unambiguous"
                        else len(r["pred_set"]) > 1)
        r["covered"] = any(x in r["pred_set"] for x in r["true_responses"])
    clear = [r for r in ok if r["category"] == "unambiguous"]
    amb = [r for r in ok if r["category"] == "ambiguous"]
    ac, aa = sum(r["asked"] for r in clear), sum(r["asked"] for r in amb)
    absent = sum(1 for r in cal if not r["true_idx"])
    out = {"method": "LofreeCP (Su et al. 2024), split conformal",
           "backbone": model, "judge_model": judge, "embedder": backend,
           "dataset": name, "calibration_set": calib_name,
           "m_samples": M_SAMPLES, "temperature": TEMP, "eps": EPS, "formula": FORMULA,
           "truth_source": (ok[0].get("truth_source") if ok else None),
           "lambda1": l1, "lambda2": l2, "qhat": round(qhat, 6),
           "keep_if_nonconformity_at_most": round(qhat, 6),
           "calibration_items_used": n_cal,
           "calibration_items_whose_true_answer_was_absent": f"{absent}/{len(cal)}",
           "items": len(test), "failed": len(test) - len(ok),
           "mean_distinct_responses": round(float(np.mean([len(r["responses"]) for r in ok])), 2),
           "mean_prediction_set_size": round(float(np.mean([len(r["pred_set"]) for r in ok])), 2),
           "asked_on_clear": f"{ac}/{len(clear)}", "asked_on_clear_ci95": wilson(ac, len(clear)),
           "asked_on_ambiguous": f"{aa}/{len(amb)}", "asked_on_ambiguous_ci95": wilson(aa, len(amb)),
           "empirical_coverage_on_test": round(sum(bool(r["covered"]) for r in ok) / max(1, len(ok)), 3),
           "target_coverage": round(1 - EPS, 3)}
    out["prediction_set_collapsed"] = bool(
        abs(out["mean_prediction_set_size"] - out["mean_distinct_responses"]) < 1e-9)
    out["prediction_set_collapsed_note"] = (
        "DEGENERATE: qhat capped because the quantile landed in the infinite tail, so every "
        "response is kept and the rule reduces to 'ask unless all samples agree'. This is not a "
        "working conformal predictor; do not report it as one."
        if out["prediction_set_collapsed"] else
        "qhat finite; the prediction set is a genuine subset of the sampled responses.")
    out["test_items_whose_true_answer_was_absent"] = f"{sum(1 for r in ok if not r['true_idx'])}/{len(ok)}"
    out["empty_prediction_sets"] = (f"{sum(1 for r in clear if not r['pred_set'])} clear, "
                                    f"{sum(1 for r in amb if not r['pred_set'])} ambiguous")
    out["decision_and_correctness_rule"] = (
        "AmbiK's own metrics.py: help_rate = len(set) > 1; correct_help_rate = len(set) == 1 on a "
        "clear item and len(set) > 1 on an ambiguous one. An empty set is therefore scored wrong "
        "on both, which is why balanced accuracy is not simply 1 - ask rate on the clear half.")
    if clear and amb:
        out["correct_on_clear"] = f"{sum(r['correct'] for r in clear)}/{len(clear)}"
        out["correct_on_ambiguous"] = f"{sum(r['correct'] for r in amb)}/{len(amb)}"
        out["balanced_accuracy"] = round((sum(r["correct"] for r in clear) / len(clear)
                                          + sum(r["correct"] for r in amb) / len(amb)) / 2, 4)
        rnd = random.Random(1)
        bs = [((sum(rnd.choice(clear)["correct"] for _ in clear) / len(clear))
               + sum(rnd.choice(amb)["correct"] for _ in amb) / len(amb)) / 2 for _ in range(2000)]
        out["balanced_accuracy_ci95"] = [round(float(np.percentile(bs, 2.5)), 3),
                                         round(float(np.percentile(bs, 97.5)), 3)]
    by = {}
    for r in amb:
        t = r.get("ambiguity_type") or "?"
        by.setdefault(t, [0, 0])
        by[t][0] += r["asked"]
        by[t][1] += 1
    out["ask_rate_by_ambiguity_type"] = {t: f"{a}/{n}" for t, (a, n) in sorted(by.items())}
    if ok and all("ambik_should_ask" in r for r in ok):
        pos = [r for r in ok if r["ambik_should_ask"]]
        neg = [r for r in ok if not r["ambik_should_ask"]]
        if pos and neg:
            out["balanced_accuracy_ambik_rule"] = round(
                (sum(len(r["pred_set"]) > 1 for r in pos) / len(pos)
                 + sum(len(r["pred_set"]) == 1 for r in neg) / len(neg)) / 2, 4)
    # Cutoff-free checks. 1 - F(top-1) is the analogue of KnowNo's 1 - top probability;
    # NE is the paper's own prompt-level uncertainty signal.
    for label, fn in (("one_minus_top_frequency", lambda r: 1 - r["freq"][r["responses"][0]]),
                      ("normalized_entropy", lambda r: r["ne"])):
        cl = [fn(r) for r in clear]
        groups = {"all_ambiguous": amb}
        for r in amb:
            groups.setdefault(r.get("ambiguity_type") or "?", []).append(r)
        out[f"auroc_by_{label}"] = {g: {"n": len(rs), "auroc": auroc([fn(r) for r in rs], cl)}
                                    for g, rs in groups.items()}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", required=True)
    ap.add_argument("--calib", nargs="+", required=True)
    ap.add_argument("--data", nargs="+", required=True)
    ap.add_argument("--limit", type=int, default=None, help="limit on the TEST set only")
    ap.add_argument("--embedder", default="openai", choices=["openai", "fasttext"])
    ap.add_argument("--formula", default="paper", choices=["paper", "released"],
                    help="paper: Eq. 8. released: the authors' run_cp.py scaling.")
    ap.add_argument("--judge-model", default=JUDGE_MODEL)
    ap.add_argument("--truth", default="intent", choices=["intent", "judge"],
                    help="intent: the true answer comes from the dataset's user_intent (default). "
                         "judge: an LLM decides (kept only for comparison).")
    ap.add_argument("--eps", type=float, default=0.2,
                    help="miscoverage rate. The paper does not fix it; the authors' run_cp.py uses "
                         "0.3 and AmbiK uses 0.2. It is a user-chosen parameter, not part of the "
                         "method, so changing it is reported rather than hidden.")
    ap.add_argument("--fresh", action="store_true")
    ap.add_argument("--dry-run", action="store_true",
                    help="no API calls; exercises sampling, scoring, lambda search and calibration")
    args = ap.parse_args()

    global FORMULA, EPS
    FORMULA = args.formula
    EPS = args.eps
    import run_knowno_v3 as _k3
    _k3.EPS = args.eps          # qhat_from reads the constant from its own module
    client, model = (None, "dry-run") if args.dry_run else make_client()
    print(f"LofreeCP m={M_SAMPLES} | backbone: {model} | judge: {args.judge_model} "
          f"| embedder: {args.embedder} | formula: {args.formula} | truth: {args.truth}")

    cal_items = load(args.calib)
    test_items = load(args.data, args.limit)
    if args.truth == "intent":
        missing = [n for n, it in (("calibration", cal_items), ("test", test_items))
                   if not any(x.get("user_intent") for x in it)]
        if missing:
            raise SystemExit(f"--truth intent needs user_intent on every item; the "
                             f"{' and '.join(missing)} set has none. Pass --truth judge instead.")
    RESULTS.mkdir(exist_ok=True)
    # Each ground truth gets its own cache files: true_idx is baked into the per-item records, so
    # sharing one file between --truth intent and --truth judge would overwrite one with the other.
    tsfx = "" if args.truth == "intent" else f"__truth-{args.truth}"
    tag = f"{args.name}__lofreecp__{model_tag(model)}{tsfx}"
    out_tag = tag if abs(args.eps - 0.2) < 1e-9 else f"{tag}__eps{args.eps:g}"
    cal_tag = Path(args.calib[0]).stem

    cal = [r for r in pass_over(client, model, args.judge_model, cal_items,
                                RESULTS / f"{cal_tag}__lofreecp__{model_tag(model)}{tsfx}__calib.jsonl",
                                args.embedder, args.fresh, "calib", args.truth, args.dry_run)
           if not r["failed"]]
    if len(cal) < 40:
        raise SystemExit(f"Only {len(cal)} usable calibration items.")
    half = len(cal) // 2
    l1, l2, qhat, val_size, val_cov = tune(cal[:half], cal[half:])
    print(f"\nlambda search: lambda1={l1} lambda2={l2} qhat={qhat:.6f} "
          f"(validation coverage {val_cov:.3f}, mean set size {val_size:.2f})\n")

    test = pass_over(client, model, args.judge_model, test_items,
                     RESULTS / f"{tag}__test.jsonl", args.embedder, args.fresh, "test",
                     args.truth, args.dry_run)
    summ = summarize_lofreecp(test, cal, qhat, l1, l2, half, model, args.judge_model,
                              args.name, cal_tag, args.embedder)
    (RESULTS / f"{out_tag}__summary.json").write_text(json.dumps(summ, indent=2), encoding="utf-8")
    print(json.dumps(summ, indent=2))
    print("Saved", RESULTS / f"{out_tag}__summary.json")


if __name__ == "__main__":
    main()
