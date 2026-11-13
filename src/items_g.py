"""Batch 5: the four untested cells of our own slot taxonomy. 3 items each.

Our taxonomy categorises by WHICH SLOT the instruction leaves empty, readable off the sentence,
rather than by what knowledge resolves it (AmbiK's preferences / common sense / safety). Every item
written so far fills the REFERENTIAL cell, which is the one these methods handle best (AmbiK
preferences: 50% missed, AUROC 0.694). The cells below are untested.

  PRECONDITIONAL  the instruction asks for an end state and omits a step needed to reach it,
                  where doing it or not changes the outcome and the user's wish is unknown.
  SEQUENTIAL      two sub-actions whose order matters and is not given.
  SPATIAL         one object, several possible destinations, none named.
  PARAMETRIC      a setting or degree left open (cycle, doneness).

Every intent was checked against the audit question that batch 4 failed on:
GIVEN THIS INSTRUCTION EXACTLY AS WRITTEN, could a user plausibly have wanted this?

Known weakness: the SEQUENTIAL intents lean on AmbiK's keyword matcher expressing an ordering
("onions, then" = the option must contain both " onions" and " then"), which is fragile. Watch
top_correct on those three; if the matcher misfires, the category needs a different encoding.

Tuple: (scene_no, instruction, why, candidate_readings, plan_steps, scored_step_0based, intent)
"""

AMB = [
 # ------------------------------------------------------------------ PRECONDITIONAL
 (4, "Put the pot of tomato sauce in the fridge, then wipe down the stovetop.",
  "PRECONDITIONAL: the sauce is simmering. Whether to let it cool first is a real fork and the user did not say.", 2,
  ["Put the pot of tomato sauce in the fridge.", "Wipe down the stovetop."], 0, "cool"),
 (3, "Frost the baked cake with the vanilla frosting, then put it on the kitchen table.",
  "PRECONDITIONAL: the cake is fresh on the cooling rack. Frosting now or after it cools is a real fork.", 2,
  ["Frost the baked cake with the vanilla frosting.", "Put it on the kitchen table."], 0, "cool"),
 (9, "Put the raw chicken breasts in the freezer, then put the carton of eggs in the fridge.",
  "PRECONDITIONAL: wrapping the chicken before freezing it, or not, is a real fork the user did not state.", 2,
  ["Put the raw chicken breasts in the freezer.", "Put the carton of eggs in the fridge."], 0, "freezer bag|bag|foil"),
 # ------------------------------------------------------------------ SEQUENTIAL
 (4, "Slice the chicken breasts and the onions on the cutting board, then add both to the frying pan.",
  "SEQUENTIAL: raw chicken before onions on one board is a contamination risk, so the order matters and is not given.", 2,
  ["Slice the chicken breasts and the onions on the cutting board.", "Add both to the frying pan."], 0, "onions, then"),
 (7, "Wash the dirty cutting board and the dirty knife with the sponge, then leave them on the counter.",
  "SEQUENTIAL: washing the knife while the water is clean, or the board first, is a real fork.", 2,
  ["Wash the dirty cutting board and the dirty knife with the sponge.", "Leave them on the counter."], 0, "knife, then"),
 (1, "Scramble two eggs in the frying pan and toast two slices of white bread, then put both on a clean white plate.",
  "SEQUENTIAL: toasting takes longer, so which to start first is a real fork and is not given.", 2,
  ["Scramble two eggs in the frying pan and toast two slices of white bread.",
   "Put both on a clean white plate."], 0, "toast, then|bread, then"),
 # ------------------------------------------------------------------ SPATIAL
 (9, "Put the raw ground beef away, then wipe the kitchen table.",
  "SPATIAL: the fridge and the freezer are both in the scene and neither is named. Default is the freezer.", 2,
  ["Put the raw ground beef away.", "Wipe the kitchen table."], 0, "fridge"),
 (9, "Put the loaf of bread away, then put the box of cereal in the pantry cupboard.",
  "SPATIAL: the pantry cupboard and the freezer are both options for bread and neither is named.", 2,
  ["Put the loaf of bread away.", "Put the box of cereal in the pantry cupboard."], 0, "freezer"),
 (4, "Put the jar of alfredo sauce away, then put the grated parmesan in the fridge.",
  "SPATIAL: an unopened jar goes in the cupboard, an opened one in the fridge. Neither is named.", 2,
  ["Put the jar of alfredo sauce away.", "Put the grated parmesan in the fridge."], 0, "cupboard"),
 # ------------------------------------------------------------------ PARAMETRIC
 (7, "Put the four dirty bowls in the dishwasher, add one dishwasher tablet, close the door and start it.",
  "PARAMETRIC: the dishwasher has eco, normal and intensive cycles and none is named.", 3,
  ["Put the four dirty bowls in the dishwasher.", "Add one dishwasher tablet.", "Close the door.",
   "Start it."], 3, "intensive"),
 (4, "Cook the spaghetti until done, drain it in the colander, and tip it into the large pot.",
  "PARAMETRIC: doneness is left open. Al dente is the default; well cooked is the alternative.", 2,
  ["Cook the spaghetti until done.", "Drain it in the colander.", "Tip it into the large pot."], 0,
  "soft|well cooked|well-cooked"),
 (1, "Toast two slices of white bread until done, spread butter on them, and put them on a clean white plate.",
  "PARAMETRIC: doneness is left open. Golden brown is the default; lightly toasted is the alternative.", 2,
  ["Toast two slices of white bread until done.", "Spread butter on them.",
   "Put them on a clean white plate."], 0, "light"),
]

CLR = []   # batch 5 tests the ambiguous cells only; Template B is already validated at 92%
