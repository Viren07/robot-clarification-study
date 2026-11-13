"""Batch 6: 24 ambiguous items, balanced across the five thin cells of our slot taxonomy.

Counts: Preconditional 6, Parametric 6, Sequential 4, Spatial 4, Instrumental 4.
Referential is already well covered by own100, so it is not extended here.

THE MECHANISM (from batch 5): an item is missed when the omitted thing is NOT AN ARGUMENT OF THE
VERB, because the option generator then produces only ways of executing the stated action and the
omitted slot never becomes a candidate at all:

    "Frost the baked cake."        -> frost the cake         0.984   nothing about cooling
    "Start it."                   -> press start             0.984   no cycle named
    "Toast two slices until done."-> toast them              0.984   no doneness named

A destination IS an argument, so batch 5's Spatial items were all enumerated (fridge/freezer/
cupboard) and caught. Fix: make the location a SUB-location finer than the one named.
An ordering cannot be expressed by AmbiK's keyword matcher at all, and forcing it produced a false
match on amb_b5_004. Fix: re-encode Sequential as an INTERVENING STEP, which is a step, not an
argument, so it rides the winning mechanism.

Every intent passed the audit question batch 4 failed: given this instruction exactly as written,
could a user plausibly have wanted this?

Tuple: (scene_no, instruction, why, candidate_readings, plan_steps, scored_step_0based, intent)
"""

AMB = [
 # ---------------------------------------------------------------- PRECONDITIONAL (6)
 (1, "Put the saucepan of leftover soup in the fridge, then wipe down the stovetop.",
  "PRECONDITIONAL: the soup is in a saucepan off the stove. Cooling it first, or not, is a real fork.", 2,
  ["Put the saucepan of leftover soup in the fridge.", "Wipe down the stovetop."], 0, "cool"),
 (3, "Take the nonstick baking sheet out of the oven and put it on the wire cooling rack.",
  "PRECONDITIONAL: the sheet is hot and oven mitts are in the scene, but the instruction does not mention them.", 2,
  ["Take the nonstick baking sheet out of the oven.", "Put it on the wire cooling rack."], 0, "mitts"),
 (7, "Put the glass jar with the screw-top lid in the recycling bin, then wipe the counter with the spray cleaner.",
  "PRECONDITIONAL: rinsing a jar before recycling it, or not, is a real fork the user did not state.", 2,
  ["Put the glass jar with the screw-top lid in the recycling bin.",
   "Wipe the counter with the spray cleaner."], 0, "rinse"),
 (6, "Put the cherry tomatoes in the large salad bowl, then toss the salad with the tongs.",
  "PRECONDITIONAL: rinsing the tomatoes first, or not, is a real fork and the sink is in the scene.", 2,
  ["Put the cherry tomatoes in the large salad bowl.", "Toss the salad with the tongs."], 0, "rinse|wash"),
 (8, "Put the tub of chocolate ice cream back in the freezer, then wipe the counter.",
  "PRECONDITIONAL: putting the lid on before it goes back, or not, is a real fork.", 2,
  ["Put the tub of chocolate ice cream back in the freezer.", "Wipe the counter."], 0, "lid"),
 (9, "Put the cheese in the fridge, then put the canned beans in the pantry cupboard.",
  "PRECONDITIONAL: wrapping the cheese first is a real fork; foil and freezer bags are in the scene.", 2,
  ["Put the cheese in the fridge.", "Put the canned beans in the pantry cupboard."], 0, "foil|wrap|container"),
 # ---------------------------------------------------------------- PARAMETRIC (6)
 (3, "Preheat the oven, then put the nonstick baking sheet of cookie dough in it and set the timer.",
  "PARAMETRIC: no temperature is given.", 2,
  ["Preheat the oven.", "Put the nonstick baking sheet of cookie dough in it.", "Set the timer."], 0, "325"),
 (4, "Boil the water in the large pot, add the spaghetti, and cook it.",
  "PARAMETRIC: no cooking time is given.", 2,
  ["Boil the water in the large pot.", "Add the spaghetti.", "Cook it."], 2, "seven"),
 (7, "Put the dirty cutlery in the dishwasher, add one dishwasher tablet, and start it.",
  "PARAMETRIC: the dishwasher has eco, normal and intensive cycles and none is named.", 3,
  ["Put the dirty cutlery in the dishwasher.", "Add one dishwasher tablet.", "Start it."], 2, "eco"),
 (1, "Scramble two eggs in the frying pan, then slide them onto a clean white plate.",
  "PARAMETRIC: no heat level is given and the stovetop is in the scene.", 2,
  ["Scramble two eggs in the frying pan.", "Slide them onto a clean white plate."], 0, "low"),
 (8, "Warm the brownies in the microwave, then put them on the ceramic plate.",
  "PARAMETRIC: no warming time is given.", 2,
  ["Warm the brownies in the microwave.", "Put them on the ceramic plate."], 0, "forty"),
 (5, "Put a chamomile tea bag in the white mug, pour hot water from the electric kettle over it, and let it steep.",
  "PARAMETRIC: no steeping time is given.", 2,
  ["Put a chamomile tea bag in the white mug.", "Pour hot water from the electric kettle over it.",
   "Let it steep."], 2, "five"),
 # ---------------------------------------------------------------- SEQUENTIAL, as an intervening step (4)
 (4, "Slice the raw chicken breasts and then the onions on the cutting board, and add both to the frying pan.",
  "SEQUENTIAL: raw chicken before onions on one board needs the board washed between, which is not stated.", 2,
  ["Slice the raw chicken breasts and then the onions on the cutting board.",
   "Add both to the frying pan."], 0, "wash|rinse"),
 (6, "Peel the carrots and then slice the cucumber on the wooden cutting board, and put both in the large salad bowl.",
  "SEQUENTIAL: whether the board is rinsed between the two is a real fork and is not stated.", 2,
  ["Peel the carrots and then slice the cucumber on the wooden cutting board.",
   "Put both in the large salad bowl."], 0, "rinse|wash"),
 (7, "Wash the dirty frying pan and then the four dirty bowls in the sink, and leave them on the counter.",
  "SEQUENTIAL: whether the water is changed between the greasy pan and the bowls is a real fork.", 2,
  ["Wash the dirty frying pan and then the four dirty bowls in the sink.",
   "Leave them on the counter."], 0, "fresh|change the water|refill"),
 (1, "Whisk two eggs in the mixing bowl and then pour them into the frying pan.",
  "SEQUENTIAL: whether the pan is heated before the eggs go in is a real fork and is not stated.", 2,
  ["Whisk two eggs in the mixing bowl.", "Pour them into the frying pan."], 1, "heat|preheat|hot"),
 # ---------------------------------------------------------------- SPATIAL, as a sub-location (4)
 (8, "Put the tub of strawberry ice cream in the freezer, then put the whipped cream in the fridge.",
  "SPATIAL: the freezer has a top drawer, a bottom drawer and a door, and none is named.", 3,
  ["Put the tub of strawberry ice cream in the freezer.", "Put the whipped cream in the fridge."], 0, "top"),
 (10, "Put the glass water bottle in the fridge, then put the juice boxes in the cupboard.",
  "SPATIAL: the fridge door is where the glass bottle lives, but the instruction says only 'the fridge'.", 2,
  ["Put the glass water bottle in the fridge.", "Put the juice boxes in the cupboard."], 0, "door"),
 (3, "Put the bag of white sugar in the fridge, then put the bag of brown sugar in the cupboard.",
  "SPATIAL: the scene puts white sugar on the top shelf of the fridge; the instruction names no shelf.", 2,
  ["Put the bag of white sugar in the fridge.", "Put the bag of brown sugar in the cupboard."], 0, "top shelf|top"),
 (9, "Put the butter away, then put the potatoes in the pantry cupboard.",
  "SPATIAL: the fridge and the counter are both plausible for butter and neither is named.", 2,
  ["Put the butter away.", "Put the potatoes in the pantry cupboard."], 0, "counter"),
 # ---------------------------------------------------------------- INSTRUMENTAL (4)
 (4, "Stir the pot of tomato sauce, then taste it and add salt.",
  "INSTRUMENTAL: the wooden spoon and the ladle are both in the scene and neither is named.", 2,
  ["Stir the pot of tomato sauce.", "Taste it and add salt."], 0, "ladle"),
 (1, "Beat two eggs in the mixing bowl, then pour them into the frying pan.",
  "INSTRUMENTAL: the whisk, the spatula and the spoon are all in the scene and none is named.", 3,
  ["Beat two eggs in the mixing bowl.", "Pour them into the frying pan."], 0, "spatula"),
 (7, "Wipe the counter, then put the dish towel back on the rail.",
  "INSTRUMENTAL: the sponge, the paper towels, the dish towel and the spray cleaner are all in the scene.", 4,
  ["Wipe the counter.", "Put the dish towel back on the rail."], 0, "paper towel|paper towels"),
 (6, "Toss the mixed salad, then serve it in the two small bowls.",
  "INSTRUMENTAL: the tongs and the two serving spoons are both in the scene and neither is named.", 2,
  ["Toss the mixed salad.", "Serve it in the two small bowls."], 0, "serving spoon|serving spoons"),
]

CLR = []
