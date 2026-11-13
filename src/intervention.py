import os
import json
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# Provider toggle: set LLM_PROVIDER=groq (free, for testing/debugging)
# or LLM_PROVIDER=openai (for the actual paper experiments, keeps
# comparability with KNOWNO / Introspective Planning baselines).
LLM_PROVIDER = os.environ.get("LLM_PROVIDER", "openai").lower()

if LLM_PROVIDER == "groq":
    client = OpenAI(
        api_key=os.environ.get("GROQ_API_KEY"),
        base_url="https://api.groq.com/openai/v1"
    )
    MODEL_NAME = os.environ.get("GROQ_MODEL", "openai/gpt-oss-120b")
else:
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    MODEL_NAME = os.environ.get("OPENAI_MODEL", "gpt-4o")  # set OPENAI_MODEL=gpt-4o-mini in .env to match the other methods

SYSTEM_PROMPT = """You are a robot task planner operating
in a household environment. Given a natural language
instruction and a description of the current scene,
first enumerate every plausible, distinct interpretation
of the instruction that is groundable in the scene.

Rules for interpretations:
- Only include interpretations you could actually execute using
  objects and locations described in the scene. Do not invent
  objects or locations not mentioned.
- If the instruction assumes information you do not have access
  to, and no detail in the scene resolves it, output zero
  interpretations.
- If exactly one interpretation is groundable, treat the
  instruction as unambiguous.
- If more than one distinct interpretation is groundable, treat
  the instruction as ambiguous.

Available actions: walk_to(object), pick_up(object),
place(object, location), open(object), close(object),
switch_on(object), switch_off(object), pour(object, container)

Then decide:
- If exactly one interpretation exists, output "action": "execute"
  and provide the action plan.
- If zero or more than one interpretation exists, output
  "action": "clarify" and provide a clarifying_question a human
  could answer to resolve it.

Respond ONLY with valid JSON in this format:
{"interpretations": [...], "num_interpretations": <int>,
 "action": "clarify" or "execute", "plan": [...] or null,
 "clarifying_question": "..." or null}"""

def plan_task(instruction, scene_context):
    prompt = f"""Instruction: {instruction}
Scene: {scene_context}
Respond with the JSON object described in your instructions:"""

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        temperature=0.0
    )

    raw = response.choices[0].message.content.strip()

    # Print raw output so we can see what the model actually returns
    print(f"Raw output: {raw}")

    # Clean up common formatting issues
    cleaned = raw
    if cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[-1]
    if cleaned.endswith("```"):
        cleaned = cleaned.rsplit("```", 1)[0]
    cleaned = cleaned.strip()

    try:
        result = json.loads(cleaned)
        return {
            "interpretations": result.get("interpretations", []),
            "num_interpretations": result.get("num_interpretations", len(result.get("interpretations", []))),
            "action": result.get("action"),
            "plan": result.get("plan"),
            "clarifying_question": result.get("clarifying_question"),
            "raw": raw,
            "parsed": True
        }
    except json.JSONDecodeError:
        return {
            "interpretations": [],
            "num_interpretations": None,
            "action": None,
            "plan": None,
            "clarifying_question": None,
            "raw": raw,
            "parsed": False
        }

# Same 5 test cases used for the baseline planner, for direct comparison.
# scene_context now matches the prose style used in data/instructions.json.
test_cases = [
    {
        "instruction": "Pick up the red cup on the left side of the kitchen counter and place it in the sink",
        "category": "unambiguous",
        "scene_context": "Kitchen counter has one red cup on the left side and one blue cup on the right side. Sink is directly ahead."
    },
    {
        "instruction": "Clean up the kitchen",
        "category": "goal_ambiguous",
        "scene_context": "Kitchen counter has a red cup, a blue cup, and a plate. Sink is directly ahead. Microwave is on the counter."
    },
    {
        "instruction": "Get me something to drink",
        "category": "goal_ambiguous",
        "scene_context": "Kitchen counter has a water bottle, a juice carton, a coffee maker, and an empty cup."
    },
    {
        "instruction": "Put it away",
        "category": "referential_ambiguous",
        "scene_context": "Table has a red cup, a book, a remote control, and a plate on it."
    },
    {
        "instruction": "Turn off the lamp next to the green couch in the living room",
        "category": "unambiguous",
        "scene_context": "Living room has one green couch with a floor lamp next to it, a coffee table, a remote control, and a bookshelf."
    }
]

if __name__ == "__main__":
    print(f"Using provider: {LLM_PROVIDER} (model: {MODEL_NAME})\n")
    results = []
    for test in test_cases:
        print(f"\nInstruction: {test['instruction']}")
        print(f"Category: {test['category']}")
        result = plan_task(test['instruction'], test['scene_context'])
        print(f"Interpretations: {result['interpretations']}")
        print(f"Num interpretations: {result['num_interpretations']}")
        print(f"Action: {result['action']}")
        print(f"Plan: {result['plan']}")
        print(f"Clarifying question: {result['clarifying_question']}")
        print(f"Parsed: {result['parsed']}")
        results.append({
            "instruction": test['instruction'],
            "category": test['category'],
            "interpretations": result['interpretations'],
            "num_interpretations": result['num_interpretations'],
            "action": result['action'],
            "plan": result['plan'],
            "clarifying_question": result['clarifying_question'],
            "parsed": result['parsed']
        })

    output_path = Path(__file__).resolve().parent.parent / "data" / "intervention_test_results.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {output_path}")
