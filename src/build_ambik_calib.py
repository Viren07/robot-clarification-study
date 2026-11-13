"""Convert AmbiK's ambik_calib_100.csv into this repo's instruction format.

KnowNo calibrates on a held-out set from the test distribution. AmbiK ships one, so AmbiK's runs use
it and the own* family uses own_calib100. Each row gives the task AmbiK itself calibrated on
(ambiguous when take_amb is 1, clear otherwise), so the calibration mix stays AmbiK's own.

Output: data/ambik/ambik_calib100_instructions.json
"""
import json
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TMAP = {"preferences": "preferences", "common_sense_knowledge": "common_sense", "safety": "safety"}

def build():
    d = pd.read_csv(ROOT / "data/ambik/ambik_calib100_raw.csv")
    out = []
    for i in range(len(d)):
        r = d.iloc[i]
        amb = int(r["take_amb"]) == 1
        t = TMAP[r["ambiguity_type"]]
        plan = r["plan_for_amb_task"] if amb else r["plan_for_clear_task"]
        out.append({
            "id": f"ambikcalib_{i:04d}",
            "instruction": str(r["ambiguous_task"] if amb else r["unambiguous_direct"]).strip(),
            "category": "ambiguous" if amb else "unambiguous",
            "ambiguity_type": t if amb else None,
            "scene_context": "You are a robot in a kitchen. The kitchen contains: "
                             + str(r["environment_full"]).strip().rstrip(".") + ".",
            "ambik_type": t,
            "ambik_should_ask": bool(amb and t == "preferences"),
            "plan_steps": [x.strip() for x in str(plan).split("\n") if x.strip()],
            "ambiguity_step": int(r["end_of_ambiguity"]),
            "user_intent": str(r["user_intent"]),
        "variants": str(r.get("variants", "")),
        })
    dst = ROOT / "data/ambik/ambik_calib100_instructions.json"
    dst.write_text(json.dumps(out, indent=1), encoding="utf-8")
    n = sum(1 for x in out if x["category"] == "ambiguous")
    print(f"{len(out)} items ({n} ambiguous, {len(out) - n} clear) -> {dst}")


if __name__ == "__main__":
    build()
