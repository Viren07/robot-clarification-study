"""Rebuild a KnowNo summary from cached per-item files. No API calls.

The generation and the scoring are the expensive part and they are already on disk. Only the
LABELLING of the true option and the arithmetic downstream of it ever need redoing, so changing
ground truth, or correcting a mislabelled summary, costs nothing.

  --truth judge    keep the judge's labels stored in the rows (what the paid runs used)
  --truth intent   relabel offline from the dataset's user_intent with AmbiK's is_similar

The method is untouched: nonconformity, the quantile, the prediction set and the help rule are
all imported from run_knowno_v3 and run exactly as in the paper.

  python src/rescore_knowno.py --name ambik100 --truth judge \
      --calib-data data/ambik/ambik_calib100_instructions.json \
      --test-data  data/ambik/ambik_sample200_instructions.json --limit 100 \
      --calib <calib.jsonl> --test <test.jsonl>
"""
import argparse, json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_knowno_v3 as K3
from run_knowno_v3 import load, qhat_from, nonconformity, summarize, options_matching_intent


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", required=True)
    ap.add_argument("--truth", choices=["judge", "intent"], default="judge")
    ap.add_argument("--calib", required=True)
    ap.add_argument("--test", required=True)
    ap.add_argument("--calib-data", required=True)
    ap.add_argument("--test-data", required=True)
    ap.add_argument("--limit", type=int)
    ap.add_argument("--out")
    a = ap.parse_args()

    rows = lambda p: [json.loads(l) for l in Path(p).read_text(encoding="utf-8").splitlines() if l.strip()]
    CD = {x["id"]: x for x in load([a.calib_data], None)}
    TD = {x["id"]: x for x in load([a.test_data], a.limit)}
    cal, test = rows(a.calib), rows(a.test)

    if a.truth == "intent":
        for r, D in ((r, CD) for r in cal):
            if not r.get("failed"):
                r["true_options"] = options_matching_intent(r["options"], D[r["id"]].get("user_intent")) or ["E"]
        for r in test:
            if not r.get("failed"):
                r["true_options"] = options_matching_intent(r["options"], TD[r["id"]].get("user_intent")) or ["E"]

    ok = [r for r in cal if not r["failed"]]
    qhat, n_cal, level = qhat_from([nonconformity(r) for r in ok])
    print(f"calibration: n={n_cal} level={level:.4f} qhat={qhat:.6f} -> keep p >= {1 - qhat:.6f}")

    model = ok[0]["model"]
    judge = ok[0].get("judge_model")
    summ = summarize(test, qhat, n_cal, level, model, judge, a.name, Path(a.calib_data).stem)
    judged = sum(1 for r in ok if r.get("raw_judge"))
    summ["truth_source_requested"] = a.truth
    # With --truth intent the rows still CARRY raw_judge from the original run, but the labels
    # above have been replaced, so report the labelling in force, not the leftover field.
    summ["truth_source_actually_used"] = a.truth
    summ["rows_carry_a_judge_response"] = f"{judged}/{len(ok)}"
    summ["rescored_offline"] = "labels and arithmetic recomputed from cached options and probs; no API calls"
    n_e = sum(1 for r in ok if r["true_options"] == ["E"])
    summ["calibration_items_with_no_matching_option"] = f"{n_e}/{len(ok)}"
    summ["calibration_mean_true_options"] = round(sum(len(r["true_options"]) for r in ok) / max(1, len(ok)), 3)

    out = Path(a.out) if a.out else Path(a.test).with_name(
        Path(a.test).name.replace("__test.jsonl", "__summary.json"))
    out.write_text(json.dumps(summ, indent=2), encoding="utf-8")
    print(f"  balanced {summ.get('balanced_accuracy')}  clear {summ.get('asked_on_clear')}  "
          f"amb {summ.get('asked_on_ambiguous')}  coverage {summ.get('empirical_coverage_on_test')}")
    print("Saved", out)


if __name__ == "__main__":
    main()
