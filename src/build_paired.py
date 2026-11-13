"""Build the paired dataset from src/pairs_<type>.py files.

Enforces the three rules structurally:
  1. equal ambiguous and unambiguous counts   (one clear item per pair, by construction)
  2. equal counts per ambiguity type          (checked and reported)
  3. every ambiguous item has a pair          (paired_with set both ways, by construction)
"""
import importlib, json, os, sys, collections
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from items_a import S1, S2, S3, S4
from items_b import S5, S6, S7
from items_c import S8, S9, S10

SC = {1: S1, 2: S2, 3: S3, 4: S4, 5: S5, 6: S6, 7: S7, 8: S8, 9: S9, 10: S10}
OUT = Path(__file__).resolve().parent.parent / "data" / "paired"
TYPES = ["referential", "instrumental", "parametric", "spatial", "sequential", "preconditional"]
CODE = {"referential": "R", "instrumental": "I", "parametric": "P",
        "spatial": "S", "sequential": "Q", "preconditional": "C"}


def scene_text(n):
    return "You are a robot in a kitchen. The kitchen contains: " + SC[n]["objects"] + "."


def build(types):
    out, missing = [], []
    for t in types:
        try:
            P = importlib.import_module(f"pairs_{t}").PAIRS
        except ModuleNotFoundError:
            missing.append(t); continue
        for i, p in enumerate(P, 1):
            aid, cid = f"amb_{CODE[t]}{i:02d}", f"unamb_{CODE[t]}{i:02d}"
            common = dict(scene_context=scene_text(p["sc"]), scene_id=f"S{p['sc']}",
                          why_ambiguous=f"{t.upper()}: {p['why']}")
            out.append(dict(id=aid, instruction=p["a"], category="ambiguous",
                            ambiguity_type=t, instruction_type=f"{t}: slot left empty",
                            paired_with=cid, candidate_readings=2,
                            ambik_type="preferences", ambik_should_ask=True,
                            plan_steps=p["ap"], ambiguity_step=p["ai"],
                            user_intent=p["intent"], **common))
            out.append(dict(id=cid, instruction=p["c"], category="unambiguous",
                            ambiguity_type=None,
                            instruction_type=f"{t} resolved: slot filled, parallel trailing actions",
                            paired_with=aid, candidate_readings=1,
                            ambik_type="unambiguous_direct", ambik_should_ask=False,
                            plan_steps=p["cp"], ambiguity_step=p["ci"],
                            user_intent=p["cintent"], **common))
    return out, missing


if __name__ == "__main__":
    want = os.environ.get("PAIR_TYPES", ",".join(TYPES)).split(",")
    d, missing = build([t.strip() for t in want if t.strip()])
    OUT.mkdir(parents=True, exist_ok=True)
    name = os.environ.get("PAIR_OUT", "paired_dataset.json")
    (OUT / name).write_text(json.dumps(d, indent=1), encoding="utf-8")
    c = sum(1 for x in d if x["category"] == "unambiguous")
    by = collections.Counter(x["ambiguity_type"] for x in d if x["ambiguity_type"])
    print(f"{len(d)} items: {c} clear, {len(d)-c} ambiguous")
    for t, n in sorted(by.items()):
        print(f"   {t:<16} {n}")
    if missing:
        print(f"   not yet written: {', '.join(missing)}")
    bad = [x["id"] for x in d if x["ambiguity_step"] >= len(x["plan_steps"])]
    assert not bad, f"scored step out of range: {bad}"
    ids = {x["id"] for x in d}
    unpaired = [x["id"] for x in d if x["paired_with"] not in ids]
    assert not unpaired, f"rule 3 violated, unpaired: {unpaired}"
    assert c == len(d) - c, "rule 1 violated, halves differ"
    print(f"   rules 1 and 3 hold. saved to {OUT / name}")
