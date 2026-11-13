"""8 more clear-partner candidates. Isolating the two factors found in clrtest.

Both groups fold the precondition INTO step 0, so the scored step is the first action and the
generator sees no prior-action prefix (own100's U3 items hit 80% this way).

  group A (001-004): verb "put", which HAS a destination slot the generator may vary
  group B (005-008): verbs with no destination slot (wash, grate, scoop, slice)

If A works too, index 0 was the whole story. If only B works, the verb matters as well and all
clear partners must avoid put/place.
"""
AMB = []
CLR = [
 # ---- group A: precondition folded into step 0, "put" verb
 (6, "Rinse the cherry tomatoes and put them in the large salad bowl, then put the croutons and the feta cheese in the bowl too.",
  "A: precondition folded into step 0, put-verb, three same-kind objects.", 1,
  ["Rinse the cherry tomatoes and put them in the large salad bowl.",
   "Put the croutons in the large salad bowl.",
   "Put the feta cheese in the large salad bowl."], 0, "cherry tomatoes|tomatoes, salad bowl"),
 (1, "Let the saucepan of leftover soup cool and put it in the fridge, then put the plate of leftover pancakes and the slices of cheddar cheese in the fridge too.",
  "A: precondition folded into step 0, put-verb, three same-kind objects.", 1,
  ["Let the saucepan of leftover soup cool and put it in the fridge.",
   "Put the plate of leftover pancakes in the fridge.",
   "Put the slices of cheddar cheese in the fridge."], 0, "saucepan|soup, fridge"),
 (7, "Rinse the glass jar with the screw-top lid and put it in the recycling bin, then put the two empty cans and the empty milk carton in the bin too.",
  "A: precondition folded into step 0, put-verb, three same-kind objects.", 1,
  ["Rinse the glass jar with the screw-top lid and put it in the recycling bin.",
   "Put the two empty cans in the recycling bin.",
   "Put the empty milk carton in the recycling bin."], 0, "jar, recycling"),
 (9, "Wrap the cheese in the aluminium foil and put it in the fridge, then put the carton of milk and the yogurt in the fridge too.",
  "A: precondition folded into step 0, put-verb, three same-kind objects.", 1,
  ["Wrap the cheese in the aluminium foil and put it in the fridge.",
   "Put the carton of milk in the fridge.", "Put the yogurt in the fridge."], 0, "cheese, fridge"),
 # ---- group B: precondition folded into step 0, no destination slot in the verb
 (7, "Refill the sink with fresh water and wash the four dirty bowls, then wash the dirty cutlery and the dirty saucepan.",
  "B: precondition folded into step 0, destination-free verb, three same-kind objects.", 1,
  ["Refill the sink with fresh water and wash the four dirty bowls.", "Wash the dirty cutlery.",
   "Wash the dirty saucepan."], 0, "bowls"),
 (6, "Rinse the grater and grate the feta cheese into the large salad bowl, then grate the carrots and the red onion in as well.",
  "B: precondition folded into step 0, destination-free verb, three same-kind objects.", 1,
  ["Rinse the grater and grate the feta cheese into the large salad bowl.",
   "Grate the carrots into the large salad bowl.",
   "Grate the red onion into the large salad bowl."], 0, "feta, salad bowl|bowl"),
 (8, "Rinse the ice cream scoop and scoop the chocolate ice cream into the ceramic bowl, then scoop the strawberry ice cream and the vanilla ice cream in too.",
  "B: precondition folded into step 0, destination-free verb, three same-kind objects.", 1,
  ["Rinse the ice cream scoop and scoop the chocolate ice cream into the ceramic bowl.",
   "Scoop the strawberry ice cream into the ceramic bowl.",
   "Scoop the vanilla ice cream into the ceramic bowl."], 0, "chocolate, ceramic bowl|bowl"),
 (6, "Rinse the wooden cutting board and slice the cucumber on it, then slice the red onion and the avocado on the board too.",
  "B: precondition folded into step 0, destination-free verb, three same-kind objects.", 1,
  ["Rinse the wooden cutting board and slice the cucumber on it.",
   "Slice the red onion on the wooden cutting board.",
   "Slice the avocado on the wooden cutting board."], 0, "cucumber, cutting board|board"),
]
