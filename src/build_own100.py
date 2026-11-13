"""Build own100 and its batch 2 from the scene and item definitions in items_a/b/c/d.

Kept in the repo so both datasets are reproducible from source rather than existing only as JSON.
Scenes and per-scene items: items_a.py (S1-S4), items_b.py (S5-S7), items_c.py (S8-S10).
Batch 2 (type A6): items_d.py.

Usage:  python src/build_own100.py            (writes data/own100/*.json)
"""
import json
from pathlib import Path

from items_a import S1, S2, S3, S4
from items_b import S5, S6, S7
from items_c import S8, S9, S10
from items_d import B2
from items_d_clear import B2_CLEAR
from intents_own import INTENTS

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "own100"
SC = {1: S1, 2: S2, 3: S3, 4: S4, 5: S5, 6: S6, 7: S7, 8: S8, 9: S9, 10: S10}
PREFIX = "You are a robot in a kitchen. The kitchen contains: "
A6_LABEL = "A6: hidden preference buried in a long instruction"


def scene_text(n):
    return PREFIX + SC[n]["objects"] + "."


def build_own100():
    """All 50 clear items first in scene order, then the ambiguous ones grouped by type and
    ordered by scene within each type. This is the order the committed JSON uses."""
    flat = [(n, it) for n in range(1, 11) for it in SC[n]["items"]]
    clears = [(n, it) for n, it in flat if it["cat"] != "Ambiguous"]
    ambs = sorted((x for x in flat if x[1]["cat"] == "Ambiguous"),
                  key=lambda x: (x[1]["typ"][:2], x[0]))
    out, n_clear, n_amb, pair_ids = [], 0, {}, {}
    for n, it in clears + ambs:
        amb = it["cat"] == "Ambiguous"
        ty = it["typ"][:2]
        if amb:
            n_amb[ty] = n_amb.get(ty, 0) + 1
            iid = f"amb_{ty.lower()}_{n_amb[ty]:03d}"
        else:
            n_clear += 1
            iid = f"unamb_v2_{n_clear:03d}"
        if it.get("pair"):
            pair_ids.setdefault(it["pair"], []).append(iid)
        out.append({
            "id": iid, "instruction": it["txt"],
            "category": "ambiguous" if amb else "unambiguous",
            "ambiguity_type": ty if amb else None, "instruction_type": it["typ"],
            "scene_context": scene_text(n), "paired_with": None,
            "why_ambiguous": it["why"], "candidate_readings": it["cands"],
            "ambik_type": "preferences" if amb else None, "ambik_should_ask": amb,
            "plan_steps": it["plan"], "ambiguity_step": it["step"] - 1,
            "user_intent": INTENTS[iid], "scene_id": f"S{n}",
        })
    by_id = {x["id"]: x for x in out}
    for ids in pair_ids.values():
        if len(ids) == 2:
            by_id[ids[0]]["paired_with"] = ids[1]
            by_id[ids[1]]["paired_with"] = ids[0]
    return out


def build_batch2():
    out = []
    for i, (n, txt, why, cands, plan, step) in enumerate(B2, 1):
        out.append({
            "id": f"amb_b2_{i:03d}", "instruction": txt, "category": "ambiguous",
            "ambiguity_type": "A6", "instruction_type": A6_LABEL,
            "scene_context": scene_text(n), "paired_with": None, "why_ambiguous": why,
            "candidate_readings": cands, "ambik_type": "preferences", "ambik_should_ask": True,
            "plan_steps": plan, "ambiguity_step": step,
            "user_intent": INTENTS[f"amb_b2_{i:03d}"], "scene_id": f"S{n}",
        })
    return out


def build_batch2_paired():
    """Batch 2 plus its 19 clear minimal-pair twins: 38 items, 19 clear and 19 ambiguous.

    Unlike own100_batch2_amb19.json this set can produce a balanced accuracy, because it has
    both halves. Each pair shares a scene, a sentence shape, a plan and a scored step, so the
    only difference between a clear item and its ambiguous twin is whether the one
    under-specified noun phrase is pinned to a single scene object.
    """
    amb = build_batch2()
    out = []
    for i, (n, txt, why, cands, plan, step) in enumerate(B2_CLEAR, 1):
        cid, aid = f"unamb_b2_{i:03d}", f"amb_b2_{i:03d}"
        out.append({
            "id": cid, "instruction": txt, "category": "unambiguous",
            "ambiguity_type": None, "instruction_type": "A6 clear twin (minimal pair)",
            "scene_context": scene_text(n), "paired_with": aid, "why_ambiguous": why,
            "candidate_readings": cands, "ambik_type": "unambiguous_direct",
            "ambik_should_ask": False, "plan_steps": plan, "ambiguity_step": step,
            "user_intent": INTENTS[cid], "scene_id": f"S{n}",
        })
    for x in amb:
        x["paired_with"] = x["id"].replace("amb_b2_", "unamb_b2_")
    return out + amb


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    a = build_own100()
    b = build_batch2()
    (OUT / "own100_instructions.json").write_text(json.dumps(a, indent=1), encoding="utf-8")
    (OUT / "own100_batch2_amb19.json").write_text(json.dumps(b, indent=1), encoding="utf-8")
    c = sum(1 for x in a if x["category"] == "unambiguous")
    print(f"own100: {len(a)} items ({c} clear, {len(a) - c} ambiguous)")
    print(f"batch2: {len(b)} items (all ambiguous, type A6)")
    d = build_batch2_paired()
    (OUT / "own100_batch2_paired38.json").write_text(json.dumps(d, indent=1), encoding="utf-8")
    cc = sum(1 for x in d if x["category"] == "unambiguous")
    print(f"batch2 paired: {len(d)} items ({cc} clear, {len(d) - cc} ambiguous)")
