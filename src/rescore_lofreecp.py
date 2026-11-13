"""Rebuild a LofreeCP summary from cached per-item files. No API calls.

The sampling and the ground-truth labels are the expensive part and they are already on disk, so
changing how the prediction set is scored never needs a paid rerun. Use this after any change to
summarize_lofreecp, and to rescore a run that died after its per-item files were written.

  python src/rescore_lofreecp.py --name own100 --calib <calib.jsonl> --test <test.jsonl> [--eps 0.2]
"""
import argparse, json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_knowno_v3 as K3
import run_lofreecp as L


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", required=True)
    ap.add_argument("--calib", required=True)
    ap.add_argument("--test", required=True)
    ap.add_argument("--eps", type=float, default=0.2)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()

    K3.EPS = L.EPS = a.eps
    rows = lambda p: [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]
    cal = [r for r in rows(a.calib) if not r["failed"]]
    test = rows(a.test)
    if len(cal) < 40:
        raise SystemExit(f"Only {len(cal)} usable calibration items.")
    half = len(cal) // 2
    l1, l2, qhat, val_size, val_cov = L.tune(cal[:half], cal[half:])
    print(f"lambda search: lambda1={l1} lambda2={l2} qhat={qhat:.6f} "
          f"(validation coverage {val_cov:.3f}, mean set size {val_size:.2f})")

    ok = [r for r in test if not r["failed"]]
    model = ok[0]["model"] if ok else "unknown"
    judge = ok[0].get("judge_model")
    backend = ok[0].get("embedder")
    summ = L.summarize_lofreecp(test, cal, qhat, l1, l2, half, model, judge,
                                a.name, Path(a.calib).stem, backend)
    out = Path(a.out) if a.out else Path(a.test).with_name(
        Path(a.test).name.replace("__test.jsonl", "__summary.json"))
    out.write_text(json.dumps(summ, indent=2), encoding="utf-8")
    print(json.dumps(summ, indent=2))
    print("Saved", out)


if __name__ == "__main__":
    main()
