"""Sort everything in results/ into results/<dataset>/<method>/.

The run scripts all write into results/ root, so this is run after any batch of runs instead of
moving files by hand. It is idempotent: files already in the right place stay put.

Datasets: ambik, own114, own100, batch2
Methods:  binary_nohelp, planner, knowno_steps (the AmbiK plan-step port, "as released"),
          knowno_v3 (faithful KnowNo), lap, lofreecp
A calibration file lives with the dataset it calibrates, in that method's folder.
Superseded or not-comparable output goes to results/_superseded/ rather than being deleted.

Usage:  python src/organize_results.py [--dry-run]
"""
import argparse
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results"
KEEP_DIRS = {"_superseded", "DRYRUN"}

# (substring, dataset). First match wins, so the more specific patterns come first.
DATASETS = [
    ("knowno_steps_calibration", "ambik"),   # v1 calibrated only on AmbiK's calib_100
    ("own100_batch2", "batch2"), ("batch2__", "batch2"),
    ("own_calib100", "own100"), ("own100", "own100"),
    ("own114", "own114"),
    ("ambik_calib100", "ambik"), ("ambik_sample200", "ambik"), ("ambik100", "ambik"), ("ambik", "ambik"),
]
METHODS = [
    ("knowno_steps_calibration", "knowno_steps"),
    ("knowno_v3", "knowno_v3"), ("knowno_steps", "knowno_steps"),
    ("__lap_", "lap"), ("lofreecp", "lofreecp"),
    ("planner", "planner"),
    ("nohelp_binary", "binary_nohelp"), ("binary", "binary_nohelp"), ("nohelp", "binary_nohelp"),
]
# Output no longer comparable to anything current, kept for the record only.
SUPERSEDED = [
    "gpt-oss-120b",                 # Groq backbone, a different model from every current run
    "planner__pilot",               # older single-run planner format
    "own100__knowno_steps",         # cutoff calibrated on AmbiK, superseded by knowno_v3
    "own100_batch2_amb19__knowno_steps",
]


def classify(name):
    if any(s in name for s in SUPERSEDED):
        return "_superseded", None
    ds = next((d for s, d in DATASETS if s in name), None)
    me = next((m for s, m in METHODS if s in name), None)
    return ds, me


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    moves, skipped = [], []
    files = [p for p in RESULTS.rglob("*") if p.is_file()]
    for p in files:
        rel = p.relative_to(RESULTS)
        if rel.parts and rel.parts[0] in KEEP_DIRS:
            continue
        if "DRYRUN" in str(rel):          # dry-run output, never a result
            continue
        ds, me = classify(p.name)
        if ds == "_superseded":
            dst = RESULTS / "_superseded" / p.name
        elif ds and me:
            dst = RESULTS / ds / me / p.name
        else:
            skipped.append(str(rel))
            continue
        if p.resolve() == dst.resolve():
            continue
        moves.append((p, dst))

    for src, dst in moves:
        print(f"{src.relative_to(RESULTS)}  ->  {dst.relative_to(RESULTS)}")
        if not args.dry_run:
            dst.parent.mkdir(parents=True, exist_ok=True)
            if dst.exists():
                dst.unlink()
            shutil.move(str(src), str(dst))

    if skipped:
        print("\nnot classified, left where they are:")
        for s in skipped:
            print("  " + s)

    if not args.dry_run:
        for d in sorted((p for p in RESULTS.rglob("*") if p.is_dir()), reverse=True):
            if not any(d.iterdir()):
                print(f"removing empty folder {d.relative_to(RESULTS)}")
                d.rmdir()
    print(f"\n{len(moves)} file(s) {'would move' if args.dry_run else 'moved'}")


if __name__ == "__main__":
    main()
