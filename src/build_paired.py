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
# Option B: the six sub-types merge into three groups. Items keep their sub-type label so the
# same dataset can be read either way, but rule 2 (equal counts) is enforced per group.
GROUPS = {"referential": "G1", "instrumental": "G1", "parametric": "G2",
          "spatial": "G2", "sequential": "G3", "preconditional": "G3"}


def scene_text(n):
    return "You are a robot in a kitchen. The kitchen contains: " + SC[n]["objects"] + "."


def select(types, per_group):
    """Cap each GROUP at per_group pairs, spread as evenly as possible over its sub-types.

    Pairs are taken in file order, never by screened outcome, so this cannot select for
    difficulty. With per_group=None every pair is used.
    """
    split = os.environ.get("PAIR_SPLIT", "test")
    loaded, missing = {}, []
    for t in types:
        try:
            P = importlib.import_module(f"pairs_{t}").PAIRS
        except ModuleNotFoundError:
            missing.append(t); continue
        if split == "test":
            P = [x for x in P if not x.get("calib")]
        elif split == "calib":
            P = [x for x in P if x.get("calib")]
        loaded[t] = P
    if per_group is None:
        return loaded, missing
    bygrp = collections.defaultdict(list)
    for t in loaded:
        bygrp[GROUPS[t]].append(t)
    keep = {}
    for g, ts in bygrp.items():
        quota = {t: 0 for t in ts}
        i = 0
        while sum(quota.values()) < per_group:
            t = ts[i % len(ts)]
            if quota[t] < len(loaded[t]):
                quota[t] += 1
            elif all(quota[x] >= len(loaded[x]) for x in ts):
                break
            i += 1
        for t in ts:
            keep[t] = loaded[t][:quota[t]]
    return keep, missing


def build(types, per_group=None):
    out, missing = [], []
    selected, missing = select(types, per_group)
    for t in types:
        if t not in selected:
            continue
        P = selected[t]
        for i, p in enumerate(P, 1):
            aid, cid = f"amb_{CODE[t]}{i:02d}", f"unamb_{CODE[t]}{i:02d}"
            common = dict(scene_context=scene_text(p["sc"]), scene_id=f"S{p['sc']}",
                          group=GROUPS[t],
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
    n = os.environ.get("PAIR_GROUP_N")
    d, missing = build([t.strip() for t in want if t.strip()],
                       per_group=int(n) if n else None)
    name = os.environ.get("PAIR_OUT", "paired_dataset.json")
    c = sum(1 for x in d if x["category"] == "unambiguous")
    by = collections.Counter(x["ambiguity_type"] for x in d if x["ambiguity_type"])
    print(f"{len(d)} items: {c} clear, {len(d)-c} ambiguous")
    bygrp = collections.Counter(x["group"] for x in d if x["ambiguity_type"])
    for t, n in sorted(by.items()):
        print(f"   {t:<16} {n}  ({GROUPS[t]})")
    print("   per group (rule 2 is enforced here, not per sub-type):")
    for g, n in sorted(bygrp.items()):
        print(f"      {g} {n}")
    if missing:
        print(f"   not yet written: {', '.join(missing)}")
    bad = [x["id"] for x in d if x["ambiguity_step"] >= len(x["plan_steps"])]
    assert not bad, f"scored step out of range: {bad}"
    ids = {x["id"] for x in d}
    unpaired = [x["id"] for x in d if x["paired_with"] not in ids]
    assert not unpaired, f"rule 3 violated, unpaired: {unpaired}"
    assert c == len(d) - c, "rule 1 violated, halves differ"
    if len(bygrp) > 1:
        assert len(set(bygrp.values())) == 1, f"rule 2 violated, groups differ: {dict(bygrp)}"
    # write only AFTER every rule passes, so a rejected build cannot leave an invalid
    # dataset on disk for a later command to pick up by mistake.
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / name).write_text(json.dumps(d, indent=1), encoding="utf-8")
    print(f"   rules 1 and 3 hold. saved to {OUT / name}")
