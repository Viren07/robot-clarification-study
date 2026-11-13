"""Screen candidate dataset items against the decision the baseline actually makes.

WHY THE SECOND-HIGHEST PROBABILITY

KnowNo does not look at how confident the top answer is. It keeps every option scoring at or
above 1 - qhat (about 0.075 in our runs) and asks a question when more than one survives. So the
number that decides an item is the RUNNER-UP, not the winner:

    A=0.907  B=0.038  C=0.028  ...   2nd below the cut  -> one option survives -> SILENT
    B=0.780  A=0.174  C=0.025  ...   2nd above the cut  -> two survive         -> ASKS

An earlier version of this script measured the top probability. That is a different quantity, and
optimising it made the dataset LOOK better while predicting worse: batch 2 scored best on the old
metric and comes out at 0.66 under the real rule, against own100's measured 0.61.

WHAT A HARD DATASET NEEDS

Balanced accuracy = (fraction of clear NOT asked + fraction of ambiguous asked) / 2, which is the
same as 1 - (false_alarm_rate + miss_rate) / 2. So a method is hurt by failures in BOTH
directions, and the two halves have OPPOSITE targets:

    ambiguous item is good when the method stays silent  -> want 2nd BELOW the cut
    clear item     is good when the method falsely asks  -> want 2nd ABOVE the cut

Making clear items maximally clean is therefore counterproductive: it hands the method free marks.

Measured reference points, gpt-4o-mini:
    AmbiK   false alarms 18/50 (36%)   misses 27/50 (54%)   -> predicted 0.55, actual 0.53
    own100  false alarms 22/50 (44%)   misses 17/50 (34%)   -> predicted 0.61, actual 0.61
To beat AmbiK the two rates must sum above about 0.90.

USAGE

    # score new candidates (one generation + one scoring call per item)
    python src/screen_items.py --data data/own100/own100_batch2_paired38.json

    # re-screen anything already run, with no API calls at all
    python src/screen_items.py --from results/own100/knowno_v3/own100__*__test.jsonl
"""
import argparse, glob, json, statistics as st, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from run_knowno_v3 import RESULTS, load, run_item, scaled, options_matching_intent, find_cache, JUDGE_MODEL

# The cut is 1 - qhat. Measured qhat was 0.883 (AmbiK) and 0.925 (own100), so the cut sits near
# 0.075. The margins keep a selection valid if qhat shifts when the calibration set changes.
CUT = 0.075
AMB_MAX = 0.040   # ambiguous passes when its runner-up is below this
CLR_MIN = 0.150   # clear passes when its runner-up is at or above this


def runner_up(probs):
    v = sorted(scaled(probs).values(), reverse=True)
    return v[1] if len(v) > 1 else 0.0


def verdict(cat, second):
    """Would the baseline fail on this item, and does it clear the margin?"""
    if cat == "ambiguous":
        if second < AMB_MAX: return "PASS", "method stays silent, a miss"
        if second < CUT:     return "weak", "misses, but only just"
        return "fail", "method asks, item is caught"
    if second >= CLR_MIN:    return "PASS", "method falsely asks"
    if second >= CUT:        return "weak", "falsely asks, but only just"
    return "fail", "method correctly stays silent"


def report(recs, title):
    ok = [r for r in recs if not r.get("failed") and r.get("probs")]
    for r in ok:
        r["second"] = round(runner_up(r["probs"]), 4)
        r["verdict"], r["why"] = verdict(r["category"], r["second"])
    cl = [r for r in ok if r["category"] == "unambiguous"]
    am = [r for r in ok if r["category"] == "ambiguous"]
    print(f"\n{'='*86}\n{title}   ({len(ok)} scored: {len(cl)} clear, {len(am)} ambiguous)\n{'='*86}")
    for cat, G, want in (("clear", cl, f"runner-up >= {CLR_MIN}"), ("ambiguous", am, f"runner-up < {AMB_MAX}")):
        if not G:
            continue
        p = [r for r in G if r["verdict"] == "PASS"]
        print(f"\n{cat}: {len(G)} items, median runner-up {st.median(r['second'] for r in G):.4f}"
              f"   want {want}   ->  {len(p)}/{len(G)} pass")
        for r in sorted(G, key=lambda x: -x["second"]):
            print(f"    {r['second']:.4f}  {r['id']:<18} {r['verdict']:<5} {r['why']}")
    if cl and am:
        fa = sum(1 for r in cl if r["second"] >= CUT) / len(cl)
        ms = sum(1 for r in am if r["second"] < CUT) / len(am)
        print(f"\n  at the real cut {CUT}:  false alarms {fa:.0%}   misses {ms:.0%}   sum {fa+ms:.2f}")
        print(f"  predicted balanced accuracy = 1 - (sum)/2 = {1-(fa+ms)/2:.4f}"
              f"   (AmbiK measured 0.5300; lower is harder)")
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", nargs="+", help="dataset json: scores new items (costs API calls)")
    ap.add_argument("--from", dest="src", nargs="+", help="per-item jsonl already run: FREE, no API calls")
    ap.add_argument("--limit", type=int)
    ap.add_argument("--tag", default="screen")
    ap.add_argument("--fresh", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    if not a.data and not a.src:
        raise SystemExit("pass --data (to score new items) or --from (to re-screen existing ones)")

    if a.src:
        paths = [Path(q) for pat in a.src for q in sorted(glob.glob(pat, recursive=True))]
        if not paths:
            raise SystemExit(f"no files matched {a.src}")
        allrecs = []
        for p in paths:
            recs = [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]
            allrecs += report(recs, f"re-screened (free): {p.name}")
        if len(paths) > 1:
            report(allrecs, "POOLED ACROSS ALL FILES")
        return

    from run_knowno import make_client, model_tag
    client, model = (None, "dry-run") if a.dry_run else make_client()
    items = load(a.data, a.limit)
    RESULTS.mkdir(exist_ok=True)
    path = RESULTS / f"{a.tag}__screen__{model_tag(model)}.jsonl"
    done = {}
    src = find_cache(path)
    if src.exists() and not a.fresh:
        for line in src.read_text(encoding="utf-8").splitlines():
            if line.strip():
                r = json.loads(line)
                if not r.get("failed"):
                    done[r["id"]] = r
    recs = []
    for i, it in enumerate(items, 1):
        if it["id"] in done:
            recs.append(done[it["id"]]); continue
        res = run_item(client, model, JUDGE_MODEL, it, a.dry_run, truth="intent")
        rec = {"id": it["id"], "category": it["category"], "instruction": it["instruction"],
               "user_intent": it.get("user_intent"), "model": model, **res}
        if not rec.get("failed"):
            p = scaled(rec["probs"])
            top = max(p, key=p.get)
            true = options_matching_intent(rec["options"], it.get("user_intent")) or []
            rec["top_option"], rec["top_text"] = top, rec["options"].get(top, "")
            rec["top_correct"] = top in true
            rec["second"] = round(runner_up(rec["probs"]), 4)
        recs.append(rec)
        print(f"[{i}/{len(items)}] {it['id']}: 2nd={rec.get('second')} top_correct={rec.get('top_correct')}")
    with path.open("w", encoding="utf-8") as f:
        for r in recs:
            f.write(json.dumps(r) + "\n")
    report(recs, f"screened: {a.tag}")
    print("\nSaved", path)


if __name__ == "__main__":
    main()
