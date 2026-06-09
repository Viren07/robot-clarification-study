import os
import json
from openai import OpenAI

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

SYSTEM_PROMPT = """You are a robot task planner operating 
in a household environment. Given a natural language 
instruction and the objects currently visible in the scene, 
output a JSON list of actions for the robot to execute.

Available actions: walk_to(object), pick_up(object), 
place(object, location), open(object), close(object), 
switch_on(object), switch_off(object), pour(object, container)

Respond ONLY with a valid JSON list. Example:
["walk_to(kitchen_counter)", "pick_up(red_cup)", 
"walk_to(sink)", "place(red_cup, sink)"]

Always output a plan. Never ask clarifying questions."""

def plan_task(instruction, visible_objects):
    prompt = f"""Instruction: {instruction}
Visible objects: {', '.join(visible_objects)}
Output the action plan as a JSON list:"""

    response = client.chat.completions.create(
        model="gpt-4o",
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
        plan = json.loads(cleaned)
        return {"plan": plan, "raw": raw, "parsed": True}
    except json.JSONDecodeError:
        return {"plan": [], "raw": raw, "parsed": False}

# Test instructions
test_cases = [
    {
        "instruction": "Pick up the red cup on the left side of the kitchen counter and place it in the sink",
        "category": "unambiguous",
        "objects": ["red_cup", "blue_cup", "kitchen_counter", "sink", "plate", "microwave"]
    },
    {
        "instruction": "Clean up the kitchen",
        "category": "goal_ambiguous",
        "objects": ["red_cup", "blue_cup", "kitchen_counter", "sink", "plate", "microwave"]
    },
    {
        "instruction": "Get me something to drink",
        "category": "goal_ambiguous",
        "objects": ["water_bottle", "juice_carton", "coffee_maker", "cup", "kitchen_counter"]
    },
    {
        "instruction": "Put it away",
        "category": "referential_ambiguous",
        "objects": ["red_cup", "book", "remote_control", "plate", "table"]
    },
    {
        "instruction": "Turn off the lamp next to the green couch in the living room",
        "category": "unambiguous",
        "objects": ["lamp", "green_couch", "coffee_table", "remote_control", "bookshelf"]
    }
]

if __name__ == "__main__":
    results = []
    for test in test_cases:
        print(f"\nInstruction: {test['instruction']}")
        print(f"Category: {test['category']}")
        result = plan_task(test['instruction'], test['objects'])
        print(f"Plan: {result['plan']}")
        print(f"Parsed: {result['parsed']}")
        results.append({
            "instruction": test['instruction'],
            "category": test['category'],
            "plan": result['plan'],
            "parsed": result['parsed']
        })

    with open("data/baseline_test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print("\nResults saved to data/baseline_test_results.json")