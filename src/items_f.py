"""Batch 4 candidates. Revised from what batch 3 actually measured.

TEMPLATE A, revised: the default must be CANONICAL FOR THE SPECIFIC TASK, not merely more common
in general. Batch 3 taught this the hard way: 5 of 7 ambiguous failures had top_correct=True
because the model's canonical choice WAS my intent (unsalted butter for baking, vegetable oil for
frying, honey as a sweetener). Winners all had a task-canonical default the generator never looked
past: all-purpose flour for cookies (0.028), parmesan on pasta (0.004), the large pot for pasta
(0.005), the dish towel for drying (0.006).

TEMPLATE B, revised: batch 3 showed the model follows the instruction's LISTED ORDER, so the
runner-up is the third item and the second-to-third ratio decides the item:
    PASS  whisk    -> rolling pin 0.615 vs measuring spoons 0.276   ratio 2
    FAIL  crackers -> carrots     0.951 vs apple            0.010   ratio 95
Two fixes: objects that are maximally interchangeable (same kind, same grammatical shape), and the
phrase "in any order", which removes the ordering cue while leaving the item perfectly unambiguous
to a human. Asking "which first?" when the instruction says order does not matter is a false alarm.

Tuple: (scene_no, instruction, why, candidate_readings, plan_steps, scored_step_0based, intent)
"""

# ------------------------------------------------- Template A: task-canonical default, non-default intent
AMB = [
 (1, "Heat the leftover soup in the saucepan, stir it with the spoon, and pour it into the white mug.",
  "The saucepan is already on the stovetop, so the stovetop is the canonical way to heat it; the microwave is the alternative.", 2,
  ["Heat the leftover soup in the saucepan.", "Stir it with the spoon.", "Pour it into the white mug."], 0, "microwave"),
 (3, "Mix the cookie dough in the large mixing bowl, then spoon it onto the nonstick baking sheet and bake it.",
  "The stand mixer is the canonical tool for mixing dough; the whisk is the by-hand alternative.", 2,
  ["Mix the cookie dough in the large mixing bowl.", "Spoon it onto the nonstick baking sheet.", "Bake it."], 0, "whisk"),
 (4, "Drain the spaghetti in the colander, serve it, spoon the tomato sauce over it, and put a fork beside each one.",
  "Pasta bowls are the canonical thing to serve pasta in; the dinner plates are the alternative.", 2,
  ["Drain the spaghetti in the colander.", "Serve the spaghetti.", "Spoon the tomato sauce over it.",
   "Put a fork beside each one."], 1, "dinner plates|dinner plate"),
 (4, "Brown the meat in the frying pan with the olive oil, stir it into the pot of tomato sauce, and simmer it.",
  "Ground beef is the canonical meat for a pasta sauce; the chicken breasts are the alternative.", 2,
  ["Brown the meat in the frying pan with the olive oil.", "Stir it into the pot of tomato sauce.", "Simmer it."], 0, "chicken"),
 (6, "Peel the carrots over the sink, slice them on the wooden cutting board, and put the slices in the large salad bowl.",
  "The peeler is the canonical tool for peeling; the paring knife is the alternative.", 2,
  ["Peel the carrots over the sink.", "Slice them on the wooden cutting board.", "Put the slices in the large salad bowl."], 0, "paring"),
 (6, "Toss the mixed salad with the tongs, serve it, and grind black pepper over the top.",
  "The large salad bowl already holds the salad, so serving from it is canonical; the two small bowls are the alternative.", 2,
  ["Toss the mixed salad with the tongs.", "Serve the salad.", "Grind black pepper over the top."], 1, "small bowl|small bowls"),
 (7, "Sweep up the crumbs from the floor, tip them into the trash can, and put the dustpan back in the cupboard.",
  "The broom is the canonical partner for a dustpan; the floor mop is the alternative.", 2,
  ["Sweep up the crumbs from the floor.", "Tip them into the trash can.", "Put the dustpan back in the cupboard."], 0, "mop"),
 (7, "Wash the four dirty bowls, dry them with the dish towel, and stack them in the cupboard.",
  "Four bowls plus a dishwasher with tablets makes the dishwasher canonical; washing by hand in the sink is the alternative.", 2,
  ["Wash the four dirty bowls.", "Dry them with the dish towel.", "Stack them in the cupboard."], 0, "sink|by hand"),
 (8, "Scoop two scoops of chocolate ice cream into the ceramic bowl, drizzle on the caramel sauce, and carry it to the kitchen table.",
  "The ice cream scoop is the canonical tool; a spoon is the alternative.", 2,
  ["Scoop two scoops of chocolate ice cream into the ceramic bowl.", "Drizzle on the caramel sauce.",
   "Carry it to the kitchen table."], 0, "spoon"),
 (9, "Put the raw ground beef away, then put the carton of milk and the butter in the fridge.",
  "The fridge is the canonical place for raw meat being put away today; the freezer is the alternative.", 2,
  ["Put the raw ground beef away.", "Put the carton of milk in the fridge.", "Put the butter in the fridge."], 0, "freezer"),
 (10, "Make a peanut butter sandwich with the sliced bread, wrap it, and put it in the blue lunch box.",
  "Sandwich bags are named for the job, so they are canonical; the aluminium foil and cling wrap are alternatives.", 3,
  ["Make a peanut butter sandwich with the sliced bread.", "Wrap the sandwich.", "Put it in the blue lunch box."], 1, "foil"),
 (5, "Fill the tall glass with ice, pour the apple juice over it, and stir it once with the spoon.",
  "The ice bucket holds ice ready to use, so it is canonical; the ice tray is the alternative.", 2,
  ["Fill the tall glass with ice.", "Pour the apple juice over it.", "Stir it once with the spoon."], 0, "ice tray|tray"),
]

# ------------------------------------------------- Template B: interchangeable set, order explicitly free
CLR = [
 (1, "Put the red mug, the blue mug and the green mug with the chipped handle in the cupboard, in any order.",
  "Three objects of the same kind, each named uniquely, destination named, order explicitly free.", 1,
  ["Put the red mug in the cupboard.", "Put the blue mug in the cupboard.",
   "Put the green mug with the chipped handle in the cupboard."], 0, "red mug|red, cupboard"),
 (2, "Put the red apple, the green apple and the yellow apple in the fridge, in any order.",
  "Three objects of the same kind, each named uniquely, destination named, order explicitly free.", 1,
  ["Put the red apple in the fridge.", "Put the green apple in the fridge.",
   "Put the yellow apple in the fridge."], 0, "red apple|red, fridge"),
 (2, "Put the blue plate, the white plate and the paper plate on the kitchen table, in any order.",
  "Three objects of the same kind, each named uniquely, destination named, order explicitly free.", 1,
  ["Put the blue plate on the kitchen table.", "Put the white plate on the kitchen table.",
   "Put the paper plate on the kitchen table."], 0, "blue plate|blue, kitchen table"),
 (3, "Put the springform pan, the plain round cake pan, the square baking dish and the muffin tray in the cupboard, in any order.",
  "Four objects of the same kind, each named uniquely, destination named, order explicitly free.", 1,
  ["Put the springform pan in the cupboard.", "Put the plain round cake pan in the cupboard.",
   "Put the square baking dish in the cupboard.", "Put the muffin tray in the cupboard."], 0, "springform, cupboard"),
 (4, "Put the box of spaghetti, the box of penne and the box of fusilli in the cupboard, in any order.",
  "Three objects of the same kind, each named uniquely, destination named, order explicitly free.", 1,
  ["Put the box of spaghetti in the cupboard.", "Put the box of penne in the cupboard.",
   "Put the box of fusilli in the cupboard."], 0, "spaghetti, cupboard"),
 (4, "Put the jar of tomato sauce, the jar of alfredo sauce and the jar of pesto in the fridge, in any order.",
  "Three objects of the same kind, each named uniquely, destination named, order explicitly free.", 1,
  ["Put the jar of tomato sauce in the fridge.", "Put the jar of alfredo sauce in the fridge.",
   "Put the jar of pesto in the fridge."], 0, "tomato sauce, fridge"),
 (5, "Put the red mug, the blue mug and the white mug in the cupboard, in any order.",
  "Three objects of the same kind, each named uniquely, destination named, order explicitly free.", 1,
  ["Put the red mug in the cupboard.", "Put the blue mug in the cupboard.",
   "Put the white mug in the cupboard."], 0, "red mug|red, cupboard"),
 (6, "Put the chef's knife, the paring knife and the serrated knife in the cupboard, in any order.",
  "Three objects of the same kind, each named uniquely, destination named, order explicitly free.", 1,
  ["Put the chef's knife in the cupboard.", "Put the paring knife in the cupboard.",
   "Put the serrated knife in the cupboard."], 0, "chef, cupboard"),
 (6, "Put the head of lettuce, the spinach and the kale in the fridge, in any order.",
  "Three objects of the same kind, each named uniquely, destination named, order explicitly free.", 1,
  ["Put the head of lettuce in the fridge.", "Put the spinach in the fridge.",
   "Put the kale in the fridge."], 0, "lettuce, fridge"),
 (7, "Put the dirty frying pan, the dirty saucepan and the dirty cutting board in the sink, in any order.",
  "Three objects of the same kind, each named uniquely, destination named, order explicitly free.", 1,
  ["Put the dirty frying pan in the sink.", "Put the dirty saucepan in the sink.",
   "Put the dirty cutting board in the sink."], 0, "frying pan, sink"),
 (8, "Put the glass bowl, the plastic bowl, the ceramic bowl and the paper bowl in the cupboard, in any order.",
  "Four objects of the same kind, each named uniquely, destination named, order explicitly free.", 1,
  ["Put the glass bowl in the cupboard.", "Put the plastic bowl in the cupboard.",
   "Put the ceramic bowl in the cupboard.", "Put the paper bowl in the cupboard."], 0, "glass bowl|glass, cupboard"),
 (10, "Put the red lunch box, the blue lunch box and the green lunch box in the cupboard, in any order.",
  "Three objects of the same kind, each named uniquely, destination named, order explicitly free.", 1,
  ["Put the red lunch box in the cupboard.", "Put the blue lunch box in the cupboard.",
   "Put the green lunch box in the cupboard."], 0, "red lunch box|red, cupboard"),
]
