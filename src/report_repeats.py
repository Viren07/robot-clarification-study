"""Report how much the score moves across repeat runs of an identical configuration.

The original optionB54 run counts as repeat r1. run_repeats.sh adds r2, r3, ... Each repeat
regenerates the test options from scratch while reusing one calibration pass, so qhat is
fixed and the spread reported here is pure generation noise.

Two numbers matter:
  between-run spread   how far the score moves when nothing changes
  combined interval    the binomial interval widened by that spread, which is the honest
                       uncertainty on a single reported number

Usage:  python src/report_repeats.py [--prefix optionB54] [--data data/paired/optionB_54.json]
"""
import argparse, json, math, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results"
sys.path.insert(0, str(Path(__file__).resolve().parent))


def knowno_decisions(test_path, cut):
    """Rebuild KnowNo's ask decision from cached rows. Verified to reproduce its own summary."""
    from run_knowno_v3 import scaled
    out = {}
    for line in open(test_path, encoding="utf-8"):
        if not line.strip():
            continue
        r = json.loads(line)
        if r.get("failed"):
            continue
        p = scaled(r["probs"])
        keep = [k for k, v in p.items() if v >= cut]
        out[r["id"]] = dict(asked=(len(keep) != 1) or ("E" in keep), category=r["category"])
    return out


def balanced(dec, ids=None):
    rows = [v for k, v in dec.items() if ids is None or k in ids]
    amb = [r for r in rows if r["category"] == "ambiguous"]
    clr = [r for r in rows if r["category"] == "unambiguous"]
    if not amb or not clr:
        return None
    ct = sum(r["asked"] for r in amb) / len(amb)
    fa = sum(r["asked"] for r in clr) / len(clr)
    se = math.sqrt(0.25 * (ct * (1 - ct) / len(amb) + fa * (1 - fa) / len(clr)))
    return dict(bal=(ct + (1 - fa)) / 2, catch=ct, fa=fa, se=se, n_amb=len(amb), n_clr=len(clr))


def spread(vals):
    n = len(vals)
    m = sum(vals) / n
    sd = math.sqrt(sum((v - m) ** 2 for v in vals) / (n - 1)) if n > 1 else 0.0
    return m, sd, min(vals), max(vals)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prefix", default="optionB54")
    ap.add_argument("--data", default="data/paired/optionB_54.json")
    a = ap.parse_args()

    grp = {x["id"]: x["group"] for x in json.load(open(ROOT / a.data, encoding="utf-8"))}

    # r1 is the original run (no _rN suffix); r2.. come from run_repeats.sh
    runs = []
    for s in RESULTS.glob(f"{a.prefix}*__knowno_v3__*__truth-judge__summary.json"):
        name = s.name.split("__knowno_v3")[0]
        m = re.fullmatch(rf"{re.escape(a.prefix)}(?:_r(\d+))?", name)
        if not m:
            continue
        test = s.with_name(s.name.replace("__summary.json", "__test.jsonl"))
        if test.exists():
            runs.append((int(m.group(1) or 1), name, json.load(open(s, encoding="utf-8")), test))
    runs.sort()
    if not runs:
        raise SystemExit(f"No runs found for prefix {a.prefix!r}.")

    print(f"KnowNo, {len(runs)} run(s) of an identical configuration\n")
    print(f"{'run':<16}{'qhat':>10}{'cut':>9}{'catches':>9}{'false al':>10}{'balanced':>10}")
    print("-" * 64)
    per_run, decs = [], {}
    for idx, name, summ, test in runs:
        cut = summ["keep_if_p_at_least"]
        d = knowno_decisions(test, cut)
        decs[idx] = d
        st = balanced(d)
        per_run.append(st["bal"])
        print(f"{'r'+str(idx)+' '+name[:11]:<16}{summ['qhat']:>10.4f}{cut:>9.4f}"
              f"{st['catch']:>8.0%}{st['fa']:>10.0%}{st['bal']:>10.4f}")

    if len(per_run) < 2:
        print("\nOnly one run. Run run_repeats.sh to measure the spread.")
        return

    m, sd, lo, hi = spread(per_run)
    binom = 1.96 * balanced(decs[runs[0][0]])["se"]
    combined = 1.96 * math.sqrt((binom / 1.96) ** 2 + sd ** 2)
    print(f"\nmean {m:.4f}   between-run sd {sd:.4f}   range {lo:.4f} to {hi:.4f} (spread {hi-lo:.4f})")
    print(f"binomial interval alone        +/-{binom:.4f}")
    print(f"binomial widened by run noise  +/-{combined:.4f}   ->  [{m-combined:.3f}, {m+combined:.3f}]")
    print(f"  {'clears' if m + combined < 0.5 else 'TOUCHES'} the 0.50 never-ask bar")

    # how unstable is an individual item?
    ids = set.intersection(*(set(d) for d in decs.values()))
    flips = [i for i in ids if len({decs[k][i]["asked"] for k in decs}) > 1]
    print(f"\nper-item stability: {len(flips)}/{len(ids)} items changed their ask decision "
          f"between runs ({len(flips)/len(ids):.0%})")

    print("\nper group, mean over runs:")
    for g in sorted(set(grp.values())):
        gid = {i for i in ids if grp.get(i) == g}
        vals = [balanced(decs[k], gid)["bal"] for k in sorted(decs)]
        gm, gsd, glo, ghi = spread(vals)
        print(f"   {g}  mean {gm:.4f}  sd {gsd:.4f}  range {glo:.4f} to {ghi:.4f}")


if __name__ == "__main__":
    main()
