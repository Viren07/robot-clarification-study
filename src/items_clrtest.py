"""8 clear-partner candidates in the CORRECTED shape, to validate before rewriting 34.

Shape: [state the omitted step] + [parallel list of three same-kind objects, one verb, one
destination], scored at the FIRST list item.

This is own100's U3 pattern (80% false alarms) and batch 4's pattern (92%), where the generator
offers the sibling actions as competing options. pilot68's clear items used heterogeneous
sequential trailing steps instead and collapsed to 6%, because the generator produced variants of
the scored step rather than candidates for what comes next.

Each item still states the precondition or intervening step, so it remains the RESOLVED partner of
its ambiguous item.
"""
AMB = []
CLR = [
 # resolved partners for preconditional items
 (1, "Let the saucepan of leftover soup cool, then put the saucepan, the plate of leftover pancakes and the glass food container in the fridge.",
  "Precondition stated; three same-kind objects to one destination.", 1,
  ["Let the saucepan of leftover soup cool.", "Put the saucepan in the fridge.",
   "Put the plate of leftover pancakes in the fridge.",
   "Put the glass food container in the fridge."], 1, "saucepan, fridge"),
 (7, "Rinse the glass jar with the screw-top lid, then put the jar, the two empty cans and the empty milk carton in the recycling bin.",
  "Precondition stated; three same-kind objects to one destination.", 1,
  ["Rinse the glass jar with the screw-top lid.", "Put the jar in the recycling bin.",
   "Put the two empty cans in the recycling bin.",
   "Put the empty milk carton in the recycling bin."], 1, "jar, recycling"),
 (6, "Rinse the cherry tomatoes in the sink, then put the cherry tomatoes, the croutons and the feta cheese in the large salad bowl.",
  "Precondition stated; three same-kind objects to one destination.", 1,
  ["Rinse the cherry tomatoes in the sink.", "Put the cherry tomatoes in the large salad bowl.",
   "Put the croutons in the large salad bowl.",
   "Put the feta cheese in the large salad bowl."], 1, "cherry tomatoes|tomatoes, salad bowl"),
 (9, "Wrap the cheese in the aluminium foil, then put the cheese, the carton of milk and the yogurt in the fridge.",
  "Precondition stated; three same-kind objects to one destination.", 1,
  ["Wrap the cheese in the aluminium foil.", "Put the cheese in the fridge.",
   "Put the carton of milk in the fridge.", "Put the yogurt in the fridge."], 1, "cheese, fridge"),
 # resolved partners for sequential items
 (7, "Wash the dirty frying pan, refill the sink with fresh water, then wash the four dirty bowls, the dirty cutlery and the dirty saucepan.",
  "Intervening step stated; three same-kind objects under one verb.", 1,
  ["Wash the dirty frying pan.", "Refill the sink with fresh water.", "Wash the four dirty bowls.",
   "Wash the dirty cutlery.", "Wash the dirty saucepan."], 2, "bowls"),
 (6, "Rinse the grater between uses, then grate the feta cheese, the carrots and the red onion into the large salad bowl.",
  "Intervening step stated; three same-kind objects under one verb.", 1,
  ["Rinse the grater between uses.", "Grate the feta cheese into the large salad bowl.",
   "Grate the carrots into the large salad bowl.",
   "Grate the red onion into the large salad bowl."], 1, "feta, salad bowl"),
 (2, "Wipe the butter knife between spreads, then spread the mustard, the mayonnaise and the ketchup on the white bread.",
  "Intervening step stated; three same-kind objects under one verb.", 1,
  ["Wipe the butter knife between spreads.", "Spread the mustard on the white bread.",
   "Spread the mayonnaise on the white bread.",
   "Spread the ketchup on the white bread."], 1, "mustard, white bread|bread"),
 (8, "Rinse the ice cream scoop between flavours, then scoop the chocolate ice cream, the strawberry ice cream and the vanilla ice cream into the ceramic bowl.",
  "Intervening step stated; three same-kind objects under one verb.", 1,
  ["Rinse the ice cream scoop between flavours.",
   "Scoop the chocolate ice cream into the ceramic bowl.",
   "Scoop the strawberry ice cream into the ceramic bowl.",
   "Scoop the vanilla ice cream into the ceramic bowl."], 1, "chocolate, ceramic bowl|bowl"),
]
