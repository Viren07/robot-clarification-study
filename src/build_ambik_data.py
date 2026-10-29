"""Convert AmbiK's ambik_test_900.csv into this repo's instruction format.
Each AmbiK row gives two items: the clear task (unambiguous_direct) and the ambiguous task.
ambik_should_ask follows AmbiK's own rule: only Preferences ambiguity should trigger a question.
Outputs (data/ambik/): ambik_all1800_instructions.json (all rows) and
ambik_sample200_instructions.json (100 pairs = 200 instructions, seeded, stratified by type,
shuffled so a run cut short is still a fair mix)."""
import pandas as pd, json, random
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
d = pd.read_csv(ROOT / "data/ambik/ambik_test900_raw.csv")
tmap = {"preferences": "preferences", "common_sense_knowledge": "common_sense", "safety": "safety"}

def scene(env):
    return "You are a robot in a kitchen. The kitchen contains: " + str(env).strip().rstrip(".") + "."

def build(sub):
    out = []
    for _, r in sub.iterrows():
        n = int(r["Unnamed: 0"]); t = tmap[r["ambiguity_type"]]
        base = {"pair_id": f"ambik_{n:04d}", "ambik_type": t, "scene_context": scene(r["environment_full"])}
        out.append({**base, "id": f"ambik_{n:04d}_clear", "instruction": str(r["unambiguous_direct"]).strip(),
                    "category": "unambiguous", "ambiguity_type": None, "ambik_should_ask": False})
        out.append({**base, "id": f"ambik_{n:04d}_amb", "instruction": str(r["ambiguous_task"]).strip(),
                    "category": "ambiguous", "ambiguity_type": t, "ambik_should_ask": t == "preferences"})
    return out

if __name__ == "__main__":
    out = ROOT / "data/ambik"
    (out / "ambik_all1800_instructions.json").write_text(json.dumps(build(d), indent=1), encoding="utf-8")
    parts = [d[d.ambiguity_type == k].sample(n=m, random_state=0)
             for k, m in [("preferences", 40), ("common_sense_knowledge", 40), ("safety", 20)]]
    s = build(pd.concat(parts))
    by_pair = {}
    for x in s:
        by_pair.setdefault(x["pair_id"], []).append(x)
    ids = list(by_pair)
    random.Random(0).shuffle(ids)
    s = [x for i in ids for x in sorted(by_pair[i], key=lambda r: r["category"] == "ambiguous")]
    (out / "ambik_sample200_instructions.json").write_text(json.dumps(s, indent=1), encoding="utf-8")
    print(len(build(d)), "items in full file;", len(s), "in sample")
