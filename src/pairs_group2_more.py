"""GROUP 2 EXPANSION: 16 new test pairs, 8 parametric and 8 spatial.

Takes group 2 from 18 test pairs to 34 (17 parametric + 17 spatial).

Variety constraint. The existing parametric pairs have nearly used up the appliances with a
named setting: dishwasher cycle twice, stovetop heat twice, toast darkness twice, kettle
temperature, oven heat, oven mode, blender speed, microwave power twice, microwave popcorn,
tap temperature. So the new eight move from APPLIANCE SETTINGS to DEGREE parameters, which are
still parametric (the instruction leaves a setting open) but ground in the action rather than
in a dial: how finely, how thinly, how thick, how many, how much, how strong.

The existing spatial pairs use every three-of-a-kind in the scenes (honey jars, sugar bags, oat
milk cartons, ranch bottles, dirty mugs, ice cream tubs, shopping bags). So the new eight are
all DESTINATION ambiguities, where the instruction says to put something away and one
destination is the obvious default. Three use scene 7's trash, recycling and compost bins,
which are three same-kind destinations with genuinely contestable defaults.

Recipe unchanged; clear partner names the choice then adds two parallel actions, scored at 0.
is_similar patterns are lowercase.
"""
PAIRS = [
 # ---------------- PARAMETRIC: which setting or degree ----------------
 dict(sub="parametric", sc=4, why="how finely to chop the onions, roughly is the default and finely is wanted",
   a="Chop the onions on the cutting board and add them to the frying pan.",
   ap=["Chop the onions on the cutting board.", "Add them to the frying pan."],
   ai=0, intent="fine|finely",
   c="Chop the onions finely on the cutting board, then chop the garlic finely and chop the mushrooms finely.",
   cp=["Chop the onions finely on the cutting board.", "Chop the garlic finely.",
       "Chop the mushrooms finely."], ci=0, cintent="fine|finely"),

 dict(sub="parametric", sc=6, why="how thinly to slice the cucumber, ordinary rounds are the default and thin is wanted",
   a="Slice the cucumber on the plastic cutting board and put the slices in the large salad bowl.",
   ap=["Slice the cucumber on the plastic cutting board.",
       "Put the slices in the large salad bowl."], ai=0, intent="thin|thinly",
   c="Slice the cucumber thinly on the plastic cutting board, then slice the red onion thinly and slice the bell pepper thinly.",
   cp=["Slice the cucumber thinly on the plastic cutting board.",
       "Slice the red onion thinly.", "Slice the bell pepper thinly."],
   ci=0, cintent="thin|thinly"),

 dict(sub="parametric", sc=2, why="how thick to slice the bread, ordinary slices are the default and thick is wanted",
   a="Slice the loaf of rye bread with the bread knife and put two slices on the blue plate.",
   ap=["Slice the loaf of rye bread with the bread knife.",
       "Put two slices on the blue plate."], ai=0, intent="thick|thickly",
   c="Slice the loaf of rye bread thickly with the bread knife, then slice the loaf of white bread thickly and slice the cucumber thickly.",
   cp=["Slice the loaf of rye bread thickly with the bread knife.",
       "Slice the loaf of white bread thickly.", "Slice the cucumber thickly."],
   ci=0, cintent="thick|thickly"),

 dict(sub="parametric", sc=1, why="how many eggs, two is the default for one person and four is wanted",
   a="Scramble the eggs in the frying pan with the whisk and slide them onto a clean white plate.",
   ap=["Take the eggs.", "Scramble them in the frying pan with the whisk.",
       "Slide them onto a clean white plate."], ai=0, intent="four",
   c="Take four of the eggs and scramble them in the frying pan, then toast two slices of the white bread and pour two glasses of water.",
   cp=["Take four of the eggs and scramble them in the frying pan.",
       "Toast two slices of the white bread.", "Pour two glasses of water."],
   ci=0, cintent="four"),

 dict(sub="parametric", sc=8, why="how many scoops, one is the default and three are wanted",
   a="Scoop the chocolate ice cream into the ceramic bowl and drizzle the caramel sauce over it.",
   ap=["Scoop the chocolate ice cream into the ceramic bowl.",
       "Drizzle the caramel sauce over it."], ai=0, intent="three",
   c="Put three scoops of chocolate ice cream in the ceramic bowl, then drizzle the caramel sauce over them and add the sprinkles on top.",
   cp=["Put three scoops of chocolate ice cream in the ceramic bowl.",
       "Drizzle the caramel sauce over them.", "Add the sprinkles on top."],
   ci=0, cintent="three"),

 dict(sub="parametric", sc=4, why="how much salt, a pinch is the default and a tablespoon is wanted for pasta water",
   a="Add the salt to the large pot of boiling water and then add the penne.",
   ap=["Add the salt to the large pot of boiling water.", "Add the penne."],
   ai=0, intent="tablespoon|spoonful|generous",
   c="Add a tablespoon of salt to the large pot of boiling water, then add the penne to the water and add the olive oil to the water.",
   cp=["Add a tablespoon of salt to the large pot of boiling water.",
       "Add the penne to the water.", "Add the olive oil to the water."],
   ci=0, cintent="tablespoon"),

 dict(sub="parametric", sc=6, why="how much dressing, a generous pour is the default and a light one is wanted",
   a="Pour the Caesar dressing over the mixed salad in the large salad bowl and toss it with the tongs.",
   ap=["Pour the Caesar dressing over the mixed salad in the large salad bowl.",
       "Toss it with the tongs."], ai=0, intent="light|lightly|a little|sparingly",
   c="Pour the Caesar dressing lightly over the mixed salad, then scatter the croutons over it and crumble the feta cheese over it.",
   cp=["Pour the Caesar dressing lightly over the mixed salad.",
       "Scatter the croutons over it.", "Crumble the feta cheese over it."],
   ci=0, cintent="light|lightly"),

 dict(sub="parametric", sc=5, why="how strong to brew the coffee, ordinary strength is the default and strong is wanted",
   a="Brew the coffee beans in the French press and pour it into the red mug.",
   ap=["Brew the coffee beans in the French press.", "Pour it into the red mug."],
   ai=0, intent="strong|stronger|double",
   c="Brew the coffee beans strong in the French press, then pour it into the red mug and put the sugar bowl on the kitchen table.",
   cp=["Brew the coffee beans strong in the French press.", "Pour it into the red mug.",
       "Put the sugar bowl on the kitchen table."], ci=0, cintent="strong"),

 # ---------------- SPATIAL: which destination ----------------
 dict(sub="spatial", sc=7, why="where the two empty cans go, the trash can is the default and the recycling bin is wanted",
   a="Throw the two empty cans away and wipe the counter with the spray cleaner.",
   ap=["Throw the two empty cans away.", "Wipe the counter with the spray cleaner."],
   ai=0, intent="recycling",
   c="Put the two empty cans in the recycling bin, then put the empty milk carton in the recycling bin and put the empty pizza box in the recycling bin.",
   cp=["Put the two empty cans in the recycling bin.",
       "Put the empty milk carton in the recycling bin.",
       "Put the empty pizza box in the recycling bin."], ci=0, cintent="recycling"),

 dict(sub="spatial", sc=7, why="where the food scraps go, the trash can is the default and the compost bin is wanted",
   a="Scrape the plate of food scraps away and rinse the plate in the sink.",
   ap=["Scrape the plate of food scraps away.", "Rinse the plate in the sink."],
   ai=0, intent="compost",
   c="Scrape the plate of food scraps into the compost bin, then put the two empty cans in the recycling bin and put the empty milk carton in the recycling bin.",
   cp=["Scrape the plate of food scraps into the compost bin.",
       "Put the two empty cans in the recycling bin.",
       "Put the empty milk carton in the recycling bin."], ci=0, cintent="compost"),

 dict(sub="spatial", sc=7, why="where the greasy pizza box goes, the recycling bin looks right but the trash can is wanted",
   a="Put the empty pizza box away and wipe the kitchen table with the paper towels.",
   ap=["Put the empty pizza box away.", "Wipe the kitchen table with the paper towels."],
   ai=0, intent="trash",
   c="Put the empty pizza box in the trash can, then put the plate of food scraps in the compost bin and put the two empty cans in the recycling bin.",
   cp=["Put the empty pizza box in the trash can.",
       "Put the plate of food scraps in the compost bin.",
       "Put the two empty cans in the recycling bin."], ci=0, cintent="trash"),

 dict(sub="spatial", sc=2, why="where the wrapped sandwich goes, the fridge is the default and the lunch box is wanted",
   a="Put the wrapped sandwich from the counter away and put the bowl of grapes on the kitchen table.",
   ap=["Put the wrapped sandwich from the counter away.",
       "Put the bowl of grapes on the kitchen table."], ai=0, intent="lunch box",
   c="Put the wrapped sandwich from the counter in the lunch box, then put the bowl of chips in the lunch box and put the can of soda in the lunch box.",
   cp=["Put the wrapped sandwich from the counter in the lunch box.",
       "Put the bowl of chips in the lunch box.",
       "Put the can of soda in the lunch box."], ci=0, cintent="lunch box"),

 dict(sub="spatial", sc=5, why="where the strawberries go, the fridge is the default and the counter is wanted",
   a="Put the strawberries away and put the pitcher in the cupboard.",
   ap=["Put the strawberries away.", "Put the pitcher in the cupboard."],
   ai=0, intent="counter",
   c="Put the strawberries on the counter, then put the banana on the counter and put the three oranges on the counter.",
   cp=["Put the strawberries on the counter.", "Put the banana on the counter.",
       "Put the three oranges on the counter."], ci=0, cintent="counter"),

 dict(sub="spatial", sc=9, why="where the butter goes, the fridge is the default and the freezer is wanted",
   a="Put the butter away and put the carton of eggs in the fridge.",
   ap=["Put the butter away.", "Put the carton of eggs in the fridge."],
   ai=0, intent="freezer",
   c="Put the butter in the freezer, then put the frozen peas in the freezer and put the ice cream in the freezer.",
   cp=["Put the butter in the freezer.", "Put the frozen peas in the freezer.",
       "Put the ice cream in the freezer."], ci=0, cintent="freezer"),

 dict(sub="spatial", sc=10, why="where the packed red lunch box goes, the backpack is the default and the fridge is wanted",
   a="Put the packed red lunch box away and put the napkins in the cupboard.",
   ap=["Put the packed red lunch box away.", "Put the napkins in the cupboard."],
   ai=0, intent="fridge",
   c="Put the packed red lunch box in the fridge, then put the packed blue lunch box in the fridge and put the packed green lunch box in the fridge.",
   cp=["Put the packed red lunch box in the fridge.",
       "Put the packed blue lunch box in the fridge.",
       "Put the packed green lunch box in the fridge."], ci=0, cintent="fridge"),

 dict(sub="spatial", sc=3, why="where the baked cake goes, the cupboard is the default and the fridge is wanted",
   a="Put the baked cake from the cooling rack away and put the rolling pin in the cupboard.",
   ap=["Put the baked cake from the cooling rack away.",
       "Put the rolling pin in the cupboard."], ai=0, intent="fridge",
   c="Put the baked cake from the cooling rack in the fridge, then put the tub of vanilla frosting in the fridge and put the milk in the fridge.",
   cp=["Put the baked cake from the cooling rack in the fridge.",
       "Put the tub of vanilla frosting in the fridge.",
       "Put the milk in the fridge."], ci=0, cintent="fridge"),
]
