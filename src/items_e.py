"""Batch 3 candidates. Written against docs/item_design_rules.md, not by guesswork.

TEMPLATE A (ambiguous): the generic term must have an OVERWHELMING DEFAULT in the scene, so the
probability concentrates on one option, AND the user's intent must be a NON-DEFAULT variant, so
the confident answer is wrong. Winners median top probability 0.973, losers 0.621.
Asymmetric pairs only: all-purpose vs whole wheat flour, olive vs vegetable oil, cheddar vs swiss.
NOT symmetric ones (glass/metal/wooden bowl, red/blue/green box), which are the known losers.

TEMPLATE B (clear): the scored step must be ONE OF SEVERAL INTERCHANGEABLE SUB-ACTIONS, so the
model cannot tell which comes next, even though every object in the step is named uniquely. The
item stays genuinely unambiguous to a human; the method asks anyway, which is its failure.
NOT a step that restates the whole instruction, which the model simply echoes at 0.984.

Tuple: (scene_no, instruction, why, candidate_readings, plan_steps, scored_step_0based, intent)
Intents are lowercase: AmbiK's is_similar lowercases the option text but not the pattern.
"""

# ---------------------------------------------------------------- Template A: ambiguous
AMB = [
 (3, "Mix the cookie dough: put the flour, the brown sugar and two eggs in the large mixing bowl and beat it with the stand mixer.",
  "all-purpose flour is the default; whole wheat is the marked alternative.", 2,
  ["Take the flour.", "Put it in the large mixing bowl.", "Add the brown sugar and two eggs.",
   "Beat it with the stand mixer."], 0, "whole wheat"),
 (3, "Cream the butter and the brown sugar in the large mixing bowl with the stand mixer, then fold in the chocolate chips.",
  "salted butter is the default; unsalted is the marked alternative.", 2,
  ["Take the butter.", "Put it in the large mixing bowl with the brown sugar.",
   "Cream them with the stand mixer.", "Fold in the chocolate chips."], 0, "unsalted"),
 (3, "Beat the sugar into the cookie dough in the large mixing bowl, then spoon the dough onto the nonstick baking sheet.",
  "white sugar is the default and three bags of it are in the scene; brown is the alternative.", 3,
  ["Take the sugar.", "Beat it into the cookie dough in the large mixing bowl.",
   "Spoon the dough onto the nonstick baking sheet."], 0, "brown"),
 (4, "Heat some oil in the frying pan, add the chopped onions and cook them until soft, then stir in the ground beef.",
  "olive oil is the default; vegetable oil is the marked alternative.", 2,
  ["Pour some oil into the frying pan.", "Heat the oil.", "Add the chopped onions.",
   "Cook them until soft.", "Stir in the ground beef."], 0, "vegetable"),
 (4, "Plate the spaghetti in the two pasta bowls, spoon the tomato sauce over it, grate cheese on top, and put a fork beside each bowl.",
  "parmesan is the default cheese for pasta; mozzarella is the alternative.", 2,
  ["Plate the spaghetti in the two pasta bowls.", "Spoon the tomato sauce over it.",
   "Grate cheese on top.", "Put a fork beside each bowl."], 2, "mozzarella"),
 (4, "Fill a pot with water, bring it to a boil on the stovetop, add the spaghetti, and cook it for nine minutes.",
  "the large pot is the default for pasta; the medium pot is the alternative.", 2,
  ["Fill a pot with water.", "Bring it to a boil on the stovetop.", "Add the spaghetti.",
   "Cook it for nine minutes."], 0, "medium"),
 (2, "Make a sandwich: put two slices of white bread on the cutting board, lay the sliced ham on one slice, add some cheese and lettuce, and close it.",
  "cheddar is the default cheese; swiss is the marked alternative.", 2,
  ["Put two slices of white bread on the cutting board.", "Lay the sliced ham on one slice.",
   "Add some cheese.", "Add lettuce.", "Close the sandwich."], 2, "swiss"),
 (2, "Pour the tomato soup from the pot into a thermos, screw the lid on tightly, and put the thermos in the lunch box with the bowl of chips.",
  "the steel thermos is the default; the plastic one is the alternative.", 2,
  ["Pour the tomato soup from the pot into a thermos.", "Screw the lid on tightly.",
   "Put the thermos in the lunch box.", "Add the bowl of chips."], 0, "plastic"),
 (1, "Pour the leftover soup from the saucepan into a food container, put the lid on, and put the container in the fridge.",
  "the plastic food container is the default; the glass one is the alternative.", 2,
  ["Pour the leftover soup from the saucepan into a food container.", "Put the lid on.",
   "Put the container in the fridge."], 0, "glass"),
 (6, "Take the cucumber from the fridge, rinse it in the sink, slice it on a cutting board with the chef's knife, and put the slices in the large salad bowl.",
  "the wooden cutting board is the default; the plastic one is the alternative.", 2,
  ["Take the cucumber from the fridge.", "Rinse it in the sink.",
   "Slice it on a cutting board with the chef's knife.", "Put the slices in the large salad bowl."], 2, "plastic"),
 (7, "Pick up the dirty mug from the counter, wash it with the sponge and dish soap, rinse it under the tap, dry it with a towel, and put it in the cupboard.",
  "the dish towel is the default for drying; paper towels are the alternative.", 2,
  ["Pick up the dirty mug from the counter.", "Wash it with the sponge and dish soap.",
   "Rinse it under the tap.", "Dry it with a towel.", "Put it in the cupboard."], 3, "paper"),
 (5, "Brew the black tea in the white mug with water from the electric kettle, sweeten it, stir it with the spoon, and take it to the kitchen table.",
  "sugar is the default sweetener; honey is the alternative.", 2,
  ["Brew the black tea in the white mug with water from the electric kettle.", "Sweeten it.",
   "Stir it with the spoon.", "Take it to the kitchen table."], 1, "honey"),
]

# ---------------------------------------------------------------- Template B: clear
CLR = [
 (3, "Put the whisk, the rolling pin and the measuring spoons away in the cupboard.",
  "Every object is named uniquely; only the order of three interchangeable sub-actions is open.", 1,
  ["Put the whisk in the cupboard.", "Put the rolling pin in the cupboard.",
   "Put the measuring spoons in the cupboard."], 0, "whisk, cupboard"),
 (4, "Set the kitchen table with the two dinner plates, the two forks and the grated parmesan.",
  "Every object is named uniquely; only the order of three interchangeable sub-actions is open.", 1,
  ["Put the two dinner plates on the kitchen table.", "Put the two forks on the kitchen table.",
   "Put the grated parmesan on the kitchen table."], 0, "dinner plates|plates, kitchen table"),
 (6, "Put the cherry tomatoes, the feta cheese and the croutons into the large salad bowl.",
  "Every object is named uniquely; only the order of three interchangeable sub-actions is open.", 1,
  ["Put the cherry tomatoes into the large salad bowl.", "Put the feta cheese into the large salad bowl.",
   "Put the croutons into the large salad bowl."], 0, "cherry tomatoes|tomatoes, salad bowl"),
 (7, "Take the two empty cans, the empty milk carton and the empty pizza box to the recycling bin.",
  "Every object is named uniquely; only the order of three interchangeable sub-actions is open.", 1,
  ["Take the two empty cans to the recycling bin.", "Take the empty milk carton to the recycling bin.",
   "Take the empty pizza box to the recycling bin."], 0, "cans, recycling"),
 (8, "Put the sprinkles, the whipped cream and the chocolate sauce on the kitchen table.",
  "Every object is named uniquely; only the order of three interchangeable sub-actions is open.", 1,
  ["Put the sprinkles on the kitchen table.", "Put the whipped cream on the kitchen table.",
   "Put the chocolate sauce on the kitchen table."], 0, "sprinkles, kitchen table"),
 (8, "Put the red tin of cookies, the bag of chips and the bag of pretzels on the kitchen table.",
  "Every object is named uniquely; only the order of three interchangeable sub-actions is open.", 1,
  ["Put the red tin of cookies on the kitchen table.", "Put the bag of chips on the kitchen table.",
   "Put the bag of pretzels on the kitchen table."], 0, "cookies, kitchen table"),
 (9, "Put the frozen peas, the ice cream and the raw ground beef in the freezer.",
  "Every object is named uniquely; only the order of three interchangeable sub-actions is open.", 1,
  ["Put the frozen peas in the freezer.", "Put the ice cream in the freezer.",
   "Put the raw ground beef in the freezer."], 0, "peas, freezer"),
 (10, "Put the crackers, the carrots and the apple into the red lunch box, then close it.",
  "Every object is named uniquely; only the order of three interchangeable sub-actions is open.", 1,
  ["Put the crackers into the red lunch box.", "Put the carrots into the red lunch box.",
   "Put the apple into the red lunch box.", "Close the red lunch box."], 0, "crackers, red lunch box|lunch box"),
 (1, "Put the strawberry jam, the peanut butter and the stick of butter in the cupboard.",
  "Every object is named uniquely; only the order of three interchangeable sub-actions is open.", 1,
  ["Put the strawberry jam in the cupboard.", "Put the peanut butter in the cupboard.",
   "Put the stick of butter in the cupboard."], 0, "jam, cupboard"),
 (5, "Put the lemon, the lime and the mint leaves on the counter.",
  "Every object is named uniquely; only the order of three interchangeable sub-actions is open.", 1,
  ["Put the lemon on the counter.", "Put the lime on the counter.",
   "Put the mint leaves on the counter."], 0, "lemon, counter"),
 # Two of the open-follow-up shape, to test where the boundary of Template B sits.
 (3, "Take the oven mitts, lift the baked cake off the cooling rack, and put it on the counter.",
  "The step names one object uniquely, but what follows it is open.", 1,
  ["Take the oven mitts.", "Lift the baked cake off the cooling rack.", "Put it on the counter."], 0,
  "oven mitts|mitts"),
 (4, "Take the colander, drain the spaghetti into it over the sink, and tip the spaghetti back into the large pot.",
  "The step names one object uniquely, but what follows it is open.", 1,
  ["Take the colander.", "Drain the spaghetti into it over the sink.",
   "Tip the spaghetti back into the large pot."], 0, "colander"),
]
