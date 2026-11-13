# Where the intervention planner fails (gpt-4o-mini, prompt hash 555c8229896d, one run each)
Written 2026-11-05. Sources: results/own114/planner/own114__gpt-4o-mini__planner__repeat1_20261105T191946Z.json and results/ambik/planner/ambik_sample200__gpt-4o-mini__planner__repeat1_20261105T192905Z.json, raw outputs from the run logs.
One run each, so single items can flip between runs (earlier runs differed by about 7 points).

## A. False alarms: the planner asks on a clear instruction (own114 4/50, AmbiK 21/50)
| Cause | own114 | AmbiK | Items |
|---|---|---|---|
| A1 Invents alternatives the instruction already rules out ("with ice or without", "same table or different place", "just one item or both", "honey in cupboard or on table" when the instruction says cupboard) | 4 | 14 | unamb_028, 034, 036, 048; ambik_0817, 0082, 0742, 0127, 0362, 0359, 0058, 0420, 0745, 0623, 0178, 0492, 0706, 0846 |
| A2 Instruction names something the scene does not contain (no pan, no microwave or stove, no plate, a beer mug but no beer, no dirty dishes listed) | 0 | 5 | ambik_0138, 0117, 0252, 0193, 0357 |
| A3 The "clear" label itself is debatable | 0 | 2 | ambik_0458 (ricotta, goat cheese and a plain cheese in the scene), ambik_0880 ("chili and beans") |

No false alarm cites a missing ACTION. gpt-4o-mini ignores the 8-action list and writes plans with chop, peel, mix, sauté and so on.
The "lack of action words" explanation fits the earlier Groq run (e.g. no "cut" action) but not these.

## B. Missed ambiguity: the planner executes an ambiguous instruction (own114 7/64, AmbiK 14/50)
- own114 (7): amb_goal_003 "Clean the living room", amb_goal_005 "Tidy up the bookcase", amb_goal_013 "Put away the cleaning equipment", amb_imp_004 "Set the lighting how I like it", amb_imp_007 "Move the laundry to the next step", amb_imp_012 "Run the trash disposal the usual way", amb_mixed_006 "Tidy up a bit and leave things somewhere accessible".
  Pattern: a vague verb or a hidden user preference, but the scene offers one salient object, so the planner commits to it.
- AmbiK (14): 11 are Common Sense or Safety (AmbiK's own rule says do NOT ask there, so executing is arguably correct) and 3 are Preferences (ambik_0680, 0138, 0139). Only those 3 are real misses by AmbiK's rule.

## C. What to grow the dataset from
1. Clear instructions with a nearby distractor and an explicit resolver (two honeys, instruction names one). Tests A1.
2. Clear instructions with conjunctions or fully specified parameters. Tests A1.
3. Clear instructions that mention an object the scene lacks. Score separately as a groundability case, not as a false alarm (H2).
4. Ambiguous instructions with a vague verb or a preference phrase where the scene has exactly one salient object. Tests B.
5. Check A3 items by hand before using any AmbiK item as ground truth.
