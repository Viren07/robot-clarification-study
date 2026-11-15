"""GROUP 1 EXPANSION: 16 new test pairs, 10 referential and 6 instrumental.

Takes group 1 from 18 test pairs to 34 (17 referential + 17 instrumental), which is what
102 pairs per half needs.

Variety constraint, as for group 3. The existing referential pairs are all baking and cooking
ingredients (flour, butter, sugar, oil, cheese, sweetener, meat, bread, spread, dressing), so
the new ones move to drinks, tea, greens, dessert toppings, pasta shapes and packed lunches.
The existing instrumental pairs are vessels and cleaning tools (pot, thermos, container, board,
towel, mixer, bowls, peeler, scoop, wrapping), so the new ones are knives, stirring and
serving utensils, a scrubber and a cake tin.

Recipe, unchanged: the instruction names the thing generically, the scene supplies a dominant
default, the user wants the marked alternative. The clear partner names the choice explicitly
then adds two parallel actions over same-kind objects, scored at index 0.

is_similar patterns are lowercase: it lowercases the option text but not the pattern.
"""
PAIRS = [
 # ---------------- REFERENTIAL: which thing ----------------
 dict(sub="referential", sc=2, why="which sliced meat, ham is the default for a sandwich and the turkey is wanted",
   a="Make a sandwich: put two slices of rye bread on the cutting board, lay the sliced meat on one slice, and close it.",
   ap=["Put two slices of rye bread on the cutting board.", "Lay the sliced meat on one slice.",
       "Close the sandwich."], ai=1, intent="turkey",
   c="Lay the sliced turkey on the rye bread, then add the tomato and add the head of lettuce.",
   cp=["Lay the sliced turkey on the rye bread.", "Add the tomato.",
       "Add the head of lettuce."], ci=0, cintent="turkey"),

 dict(sub="referential", sc=2, why="which drink, the bottle of water is the default for a lunch and the can of soda is wanted",
   a="Put a drink in the lunch box with the bowl of chips and the bowl of grapes.",
   ap=["Put a drink in the lunch box.", "Put the bowl of chips in the lunch box.",
       "Put the bowl of grapes in the lunch box."], ai=0, intent="soda|can of soda|can",
   c="Put the can of soda in the lunch box, then put the bowl of chips in it and put the bowl of grapes in it.",
   cp=["Put the can of soda in the lunch box.", "Put the bowl of chips in the lunch box.",
       "Put the bowl of grapes in the lunch box."], ci=0, cintent="soda|can"),

 dict(sub="referential", sc=5, why="which tea, black is the default and the chamomile is wanted",
   a="Brew the tea in the white mug with water from the electric kettle and take it to the kitchen table.",
   ap=["Brew the tea in the white mug with water from the electric kettle.",
       "Take it to the kitchen table."], ai=0, intent="chamomile",
   c="Brew the chamomile tea in the white mug with water from the electric kettle, then put the sugar bowl on the kitchen table and put a spoon on the kitchen table.",
   cp=["Brew the chamomile tea in the white mug with water from the electric kettle.",
       "Put the sugar bowl on the kitchen table.",
       "Put a spoon on the kitchen table."], ci=0, cintent="chamomile"),

 dict(sub="referential", sc=5, why="which milk, whole milk is the default and the almond milk is wanted",
   a="Pour the milk into the blender with the strawberries and blend it.",
   ap=["Pour the milk into the blender.", "Add the strawberries.", "Blend it."],
   ai=0, intent="almond",
   c="Pour the almond milk into the blender, then add the strawberries to the blender and add the banana to the blender.",
   cp=["Pour the almond milk into the blender.", "Add the strawberries to the blender.",
       "Add the banana to the blender."], ci=0, cintent="almond"),

 dict(sub="referential", sc=6, why="which greens, the lettuce is the default for a salad and the kale is wanted",
   a="Put the greens in the large salad bowl and toss them with the tongs.",
   ap=["Put the greens in the large salad bowl.", "Toss them with the tongs."],
   ai=0, intent="kale",
   c="Put the kale in the large salad bowl, then put the cherry tomatoes in the bowl and put the red onion in the bowl.",
   cp=["Put the kale in the large salad bowl.", "Put the cherry tomatoes in the large salad bowl.",
       "Put the red onion in the large salad bowl."], ci=0, cintent="kale"),

 dict(sub="referential", sc=8, why="which sauce, the chocolate sauce is the default on ice cream and the caramel is wanted",
   a="Drizzle the sauce over the two scoops of vanilla ice cream in the glass bowl and add the sprinkles.",
   ap=["Drizzle the sauce over the two scoops of vanilla ice cream in the glass bowl.",
       "Add the sprinkles."], ai=0, intent="caramel",
   c="Drizzle the caramel sauce over the ice cream in the glass bowl, then add the sprinkles on top and add the blueberries on top.",
   cp=["Drizzle the caramel sauce over the ice cream in the glass bowl.",
       "Add the sprinkles on top.", "Add the blueberries on top."], ci=0, cintent="caramel"),

 dict(sub="referential", sc=8, why="which topping, the whipped cream is the default on a pie and the sprinkles are wanted",
   a="Put a slice of the pie on the ceramic plate and add the topping.",
   ap=["Put a slice of the pie on the ceramic plate.", "Add the topping."],
   ai=1, intent="sprinkles",
   c="Add the sprinkles to the slice of pie on the ceramic plate, then put the brownies on the glass plate and put the cake on the paper plate.",
   cp=["Add the sprinkles to the slice of pie on the ceramic plate.",
       "Put the brownies on the glass plate.", "Put the cake on the paper plate."],
   ci=0, cintent="sprinkles"),

 dict(sub="referential", sc=4, why="which pasta, the spaghetti is the default and the fusilli is wanted",
   a="Cook the pasta in the large pot of boiling water and drain it in the colander.",
   ap=["Add the pasta to the large pot of boiling water.", "Cook it.",
       "Drain it in the colander."], ai=0, intent="fusilli",
   c="Add the fusilli to the large pot of boiling water, then add the salt to the water and add the olive oil to the water.",
   cp=["Add the fusilli to the large pot of boiling water.", "Add the salt to the water.",
       "Add the olive oil to the water."], ci=0, cintent="fusilli"),

 dict(sub="referential", sc=4, why="which jarred sauce, the tomato sauce is the default for pasta and the pesto is wanted",
   a="Stir the jarred sauce into the drained penne and plate it in the two pasta bowls.",
   ap=["Stir the jarred sauce into the drained penne.",
       "Plate it in the two pasta bowls."], ai=0, intent="pesto",
   c="Stir the jar of pesto into the drained penne, then grate the parmesan over it and grind the black pepper over it.",
   cp=["Stir the jar of pesto into the drained penne.", "Grate the parmesan over it.",
       "Grind the black pepper over it."], ci=0, cintent="pesto"),

 dict(sub="referential", sc=10, why="which yogurt cup, the strawberry one is the default and the blueberry one is wanted",
   a="Put a yogurt cup in the blue lunch box with the crackers and a juice box.",
   ap=["Put a yogurt cup in the blue lunch box.", "Put the crackers in the blue lunch box.",
       "Put a juice box in the blue lunch box."], ai=0, intent="blueberry",
   c="Put the yogurt cup with the blueberry label in the blue lunch box, then put the crackers in it and put a juice box in it.",
   cp=["Put the yogurt cup with the blueberry label in the blue lunch box.",
       "Put the crackers in the blue lunch box.",
       "Put a juice box in the blue lunch box."], ci=0, cintent="blueberry"),

 # ---------------- INSTRUMENTAL: which tool ----------------
 dict(sub="instrumental", sc=6, why="which knife, the chef's knife is the default and the paring knife is wanted",
   a="Slice the cherry tomatoes with the knife on the wooden cutting board and put them in the large salad bowl.",
   ap=["Slice the cherry tomatoes with the knife on the wooden cutting board.",
       "Put them in the large salad bowl."], ai=0, intent="paring",
   c="Slice the cherry tomatoes with the paring knife on the wooden cutting board, then slice the cucumber with it and slice the avocado with it.",
   cp=["Slice the cherry tomatoes with the paring knife on the wooden cutting board.",
       "Slice the cucumber with the paring knife.",
       "Slice the avocado with the paring knife."], ci=0, cintent="paring"),

 dict(sub="instrumental", sc=1, why="which utensil for the eggs, the whisk is the default for scrambling and the spatula is wanted",
   a="Scramble two of the eggs in the frying pan with the utensil and slide them onto a clean white plate.",
   ap=["Scramble two of the eggs in the frying pan with the utensil.",
       "Slide them onto a clean white plate."], ai=0, intent="spatula",
   c="Scramble two of the eggs in the frying pan with the spatula, then toast two slices of the white bread and pour a glass of water.",
   cp=["Scramble two of the eggs in the frying pan with the spatula.",
       "Toast two slices of the white bread.", "Pour a glass of water."],
   ci=0, cintent="spatula"),

 dict(sub="instrumental", sc=4, why="which serving utensil, the ladle is canonical for a sauce and the wooden spoon is wanted",
   a="Serve the pot of tomato sauce over the two pasta bowls of spaghetti with the utensil.",
   ap=["Take the utensil.", "Serve the pot of tomato sauce over the two pasta bowls of spaghetti."],
   ai=0, intent="wooden spoon|wooden",
   c="Serve the pot of tomato sauce over the spaghetti with the wooden spoon, then grate the parmesan over both bowls and grind the black pepper over both bowls.",
   cp=["Serve the pot of tomato sauce over the spaghetti with the wooden spoon.",
       "Grate the parmesan over both bowls.",
       "Grind the black pepper over both bowls."], ci=0, cintent="wooden spoon|wooden"),

 dict(sub="instrumental", sc=7, why="which scrubber, the sponge is the default and the scrub brush is wanted",
   a="Clean the dirty frying pan in the sink with dish soap and stand it on the counter.",
   ap=["Clean the dirty frying pan in the sink with dish soap.",
       "Stand it on the counter."], ai=0, intent="scrub brush|brush",
   c="Clean the dirty frying pan with the scrub brush and dish soap, then clean the dirty saucepan with it and clean the dirty cutting board with it.",
   cp=["Clean the dirty frying pan with the scrub brush and dish soap.",
       "Clean the dirty saucepan with the scrub brush.",
       "Clean the dirty cutting board with the scrub brush."], ci=0, cintent="scrub brush|brush"),

 dict(sub="instrumental", sc=8, why="which utensil for the pie, the cake knife is canonical and a spoon is wanted",
   a="Serve the pie onto the ceramic plate with the utensil and add the whipped cream.",
   ap=["Take the utensil.", "Serve the pie onto the ceramic plate.",
       "Add the whipped cream."], ai=0, intent="spoon",
   c="Serve the pie onto the ceramic plate with a spoon, then put the brownies on the glass plate and put the cake on the paper plate.",
   cp=["Serve the pie onto the ceramic plate with a spoon.",
       "Put the brownies on the glass plate.",
       "Put the cake on the paper plate."], ci=0, cintent="spoon"),

 dict(sub="instrumental", sc=3, why="which tin, the plain round cake pan is the default and the springform pan is wanted",
   a="Pour the cookie dough into the pan and put it in the oven.",
   ap=["Pour the cookie dough into the pan.", "Put it in the oven."],
   ai=0, intent="springform",
   c="Pour the cookie dough into the springform pan, then line the muffin tray with parchment paper and line the square baking dish with parchment paper.",
   cp=["Pour the cookie dough into the springform pan.",
       "Line the muffin tray with parchment paper.",
       "Line the square baking dish with parchment paper."], ci=0, cintent="springform"),
]
