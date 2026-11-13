"""Build the batch 3 candidate set from src/items_e.py, for screening before anything is kept."""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from items_a import S1, S2, S3, S4
from items_b import S5, S6, S7
from items_c import S8, S9, S10
import importlib
MOD = importlib.import_module(__import__('os').environ.get('BATCH_MODULE', 'items_e'))
AMB, CLR = MOD.AMB, MOD.CLR

SC = {1: S1, 2: S2, 3: S3, 4: S4, 5: S5, 6: S6, 7: S7, 8: S8, 9: S9, 10: S10}
OUT = Path(__file__).resolve().parent.parent / "data" / "own100"


def scene_text(n):
    return "You are a robot in a kitchen. The kitchen contains: " + SC[n]["objects"] + "."


def build():
    out = []
    for tag, rows, cat in (("amb", AMB, "ambiguous"), ("unamb", CLR, "unambiguous")):
        if not rows:
            continue
        for i, (n, txt, why, cands, plan, step, intent) in enumerate(rows, 1):
            out.append({
                "id": f"{tag}_{__import__('os').environ.get('BATCH_ID','b3')}_{i:03d}", "instruction": txt, "category": cat,
                "ambiguity_type": "A7" if cat == "ambiguous" else None,
                "instruction_type": ("A7: generic term with a strong scene default, intent is the "
                                     "non-default" if cat == "ambiguous" else
                                     "C2: one of several interchangeable sub-actions"),
                "scene_context": scene_text(n), "paired_with": None, "why_ambiguous": why,
                "candidate_readings": cands,
                "ambik_type": "preferences" if cat == "ambiguous" else "unambiguous_direct",
                "ambik_should_ask": cat == "ambiguous",
                "plan_steps": plan, "ambiguity_step": step,
                "user_intent": intent, "scene_id": f"S{n}",
            })
    return out


if __name__ == "__main__":
    d = build()
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{__import__('os').environ.get('BATCH_TAG','batch3')}_candidates.json").write_text(json.dumps(d, indent=1), encoding="utf-8")
    c = sum(1 for x in d if x["category"] == "unambiguous")
    print(f"candidates: {len(d)} items ({c} clear, {len(d) - c} ambiguous)")
    print(f"saved to {OUT}")
