"""Build own_calib100 from src/calib_items.py: authored plans, steps and user_intent."""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from items_a import S1, S2, S3, S4
from items_b import S5, S6, S7
from items_c import S8, S9, S10
from calib_items import ITEMS

SC = {1:S1,2:S2,3:S3,4:S4,5:S5,6:S6,7:S7,8:S8,9:S9,10:S10}
LBL = {"U1":"U1: explicit resolver next to distractors","U2":"U2: fully specified parameters",
       "U3":"U3: conjunction of named objects","U4":"U4: unique reference in a crowded scene",
       "U5":"U5: scene resolves a vague-sounding request","U6":"U6: groundability gap",
       "A1":"A1: vague verb, one salient object","A2":"A2: hidden user preference",
       "A3":"A3: three or more candidates","A4":"A4: choice late in a multi-step task",
       "A5":"A5: mixed (referent and preference)",
       "A6":"A6: hidden preference buried in a long instruction"}

def build():
    out, n = [], {}
    for sc, ty, txt, why, cands, plan, step, intent in ITEMS:
        amb = ty.startswith("A")
        n[ty] = n.get(ty, 0) + 1
        out.append({
            "id": f"calib_{ty.lower()}_{n[ty]:03d}", "instruction": txt,
            "category": "ambiguous" if amb else "unambiguous",
            "ambiguity_type": ty if amb else None, "instruction_type": LBL[ty],
            "scene_context": "You are a robot in a kitchen. The kitchen contains: " + SC[sc]["objects"] + ".",
            "paired_with": None, "why_ambiguous": why, "candidate_readings": cands,
            "ambik_type": "preferences" if amb else None, "ambik_should_ask": amb,
            "plan_steps": plan, "ambiguity_step": step - 1,
            "user_intent": intent, "scene_id": f"S{sc}",
        })
    return out

OUT = Path(__file__).resolve().parent.parent / "data" / "own100"

if __name__ == "__main__":
    d = build()
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "own_calib100_instructions.json").write_text(json.dumps(d, indent=1), encoding="utf-8")
    c = sum(1 for x in d if x['category']=='unambiguous')
    print(f"{len(d)} items, {c} clear, {len(d)-c} ambiguous, all with plans and intents")
