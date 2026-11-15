"""GROUP 1 (merged REFERENTIAL + INSTRUMENTAL): the instruction names a thing generically
and the scene supplies a dominant default for it, while the user wants the marked alternative.

18 pairs. The ambiguous halves are taken unchanged from batches 3 and 4, which were already
screened: 10 of these 18 sit below the 0.075 cut, i.e. the method stays silent and misses them.
That is the corrected mechanism: a missing OBJECT or TOOL is missed too, whenever the scene
makes one reading obvious. It is not specific to missing steps.

Dropped from the 22 valid batch-3/4 items, on pattern variety rather than on score:
  amb_b3_007  second "which cheese"          (amb_b3_005 keeps that pattern)
  amb_b4_006  second "which serving vessel"  (amb_b4_003 keeps that pattern)
  amb_b4_010  spatial, belongs to group 2
  amb_b4_012  spatial, belongs to group 2

Clear partner recipe, the one measured at 75% to 92% false alarms in batches 3 and 4:
same scene, same task, the ambiguous slot named explicitly, then two further PARALLEL actions
over same-kind objects with the destination given, and the scored step at index 0 so there is
no prior-action prefix.

is_similar patterns are lowercase throughout: it lowercases the option text but not the
pattern, so any capital in a pattern can never match.
"""
PAIRS = [
 dict(sub="referential", sc=3, why="which flour, all-purpose is the scene default and whole wheat is wanted",
   a="Mix the cookie dough: put the flour, the brown sugar and two eggs in the large mixing bowl and beat it with the stand mixer.",
   ap=["Take the flour.", "Put it in the large mixing bowl.", "Add the brown sugar and two eggs.",
       "Beat it with the stand mixer."], ai=0, intent="whole wheat",
   c="Put the whole wheat flour in the large mixing bowl, then add the brown sugar and the baking soda to the bowl too.",
   cp=["Put the whole wheat flour in the large mixing bowl.",
       "Add the brown sugar to the large mixing bowl.",
       "Add the baking soda to the large mixing bowl."], ci=0, cintent="whole wheat"),

 dict(sub="referential", sc=3, why="which butter, salted is the scene default and unsalted is wanted",
   a="Cream the butter and the brown sugar in the large mixing bowl with the stand mixer, then fold in the chocolate chips.",
   ap=["Take the butter.", "Put it in the large mixing bowl with the brown sugar.",
       "Cream them with the stand mixer.", "Fold in the chocolate chips."], ai=0, intent="unsalted",
   c="Cream the unsalted butter and the brown sugar in the large mixing bowl, then fold in the chocolate chips and the walnuts.",
   cp=["Cream the unsalted butter and the brown sugar in the large mixing bowl.",
       "Fold in the chocolate chips.",
       "Fold in the walnuts."], ci=0, cintent="unsalted"),

 dict(sub="referential", sc=3, why="which sugar, white is the default and three bags of it are in the scene",
   a="Beat the sugar into the cookie dough in the large mixing bowl, then spoon the dough onto the nonstick baking sheet.",
   ap=["Take the sugar.", "Beat it into the cookie dough in the large mixing bowl.",
       "Spoon the dough onto the nonstick baking sheet."], ai=0, intent="brown",
   c="Beat the brown sugar into the cookie dough in the large mixing bowl, then beat in the vanilla extract and the cinnamon.",
   cp=["Beat the brown sugar into the cookie dough in the large mixing bowl.",
       "Beat in the vanilla extract.",
       "Beat in the cinnamon."], ci=0, cintent="brown sugar|brown"),

 dict(sub="referential", sc=4, why="which oil, olive is the scene default and vegetable is wanted",
   a="Heat some oil in the frying pan, add the chopped onions and cook them until soft, then stir in the ground beef.",
   ap=["Pour some oil into the frying pan.", "Heat the oil.", "Add the chopped onions.",
       "Cook them until soft.", "Stir in the ground beef."], ai=0, intent="vegetable",
   c="Heat the vegetable oil in the frying pan, then add the chopped onions and the mushrooms to the pan.",
   cp=["Heat the vegetable oil in the frying pan.",
       "Add the chopped onions to the frying pan.",
       "Add the mushrooms to the frying pan."], ci=0, cintent="vegetable"),

 dict(sub="referential", sc=4, why="which cheese, parmesan is the default for pasta and mozzarella is wanted",
   a="Plate the spaghetti in the two pasta bowls, spoon the tomato sauce over it, grate cheese on top, and put a fork beside each bowl.",
   ap=["Plate the spaghetti in the two pasta bowls.", "Spoon the tomato sauce over it.",
       "Grate cheese on top.", "Put a fork beside each bowl."], ai=2, intent="mozzarella",
   c="Grate the mozzarella over the spaghetti in the two pasta bowls, then grind black pepper and sprinkle chili flakes over it.",
   cp=["Grate the mozzarella over the spaghetti in the two pasta bowls.",
       "Grind black pepper over the spaghetti.",
       "Sprinkle chili flakes over the spaghetti."], ci=0, cintent="mozzarella"),

 dict(sub="instrumental", sc=4, why="which pot, the large pot is the default for pasta and the medium one is wanted",
   a="Fill a pot with water, bring it to a boil on the stovetop, add the spaghetti, and cook it for nine minutes.",
   ap=["Fill a pot with water.", "Bring it to a boil on the stovetop.", "Add the spaghetti.",
       "Cook it for nine minutes."], ai=0, intent="medium",
   c="Bring the medium pot of water to a boil on the stovetop, then add the salt and the olive oil to the water.",
   cp=["Bring the medium pot of water to a boil on the stovetop.",
       "Add the salt to the water.",
       "Add the olive oil to the water."], ci=0, cintent="medium pot|medium"),

 dict(sub="instrumental", sc=2, why="which thermos, the steel one is the default and the plastic one is wanted",
   a="Pour the tomato soup from the pot into a thermos, screw the lid on tightly, and put the thermos in the lunch box with the bowl of chips.",
   ap=["Pour the tomato soup from the pot into a thermos.", "Screw the lid on tightly.",
       "Put the thermos in the lunch box.", "Add the bowl of chips."], ai=0, intent="plastic",
   c="Pour the tomato soup from the pot into the plastic thermos, then put the bowl of chips and the bowl of grapes in the lunch box.",
   cp=["Pour the tomato soup from the pot into the plastic thermos.",
       "Put the bowl of chips in the lunch box.",
       "Put the bowl of grapes in the lunch box."], ci=0, cintent="plastic thermos|plastic"),

 dict(sub="instrumental", sc=1, why="which food container, the plastic one is the default and the glass one is wanted",
   a="Pour the leftover soup from the saucepan into a food container, put the lid on, and put the container in the fridge.",
   ap=["Pour the leftover soup from the saucepan into a food container.", "Put the lid on.",
       "Put the container in the fridge."], ai=0, intent="glass",
   c="Pour the leftover soup from the saucepan into the glass food container, then put the plate of leftover pancakes and the slices of cheddar cheese in the fridge.",
   cp=["Pour the leftover soup from the saucepan into the glass food container.",
       "Put the plate of leftover pancakes in the fridge.",
       "Put the slices of cheddar cheese in the fridge."], ci=0, cintent="glass food container|glass container|glass"),

 dict(sub="instrumental", sc=6, why="which cutting board, the wooden one is the default and the plastic one is wanted",
   a="Take the cucumber from the fridge, rinse it in the sink, slice it on a cutting board with the chef's knife, and put the slices in the large salad bowl.",
   ap=["Take the cucumber from the fridge.", "Rinse it in the sink.",
       "Slice it on a cutting board with the chef's knife.",
       "Put the slices in the large salad bowl."], ai=2, intent="plastic",
   c="Slice the cucumber on the plastic cutting board, then slice the cherry tomatoes and the red onion on it too.",
   cp=["Slice the cucumber on the plastic cutting board.",
       "Slice the cherry tomatoes on the plastic cutting board.",
       "Slice the red onion on the plastic cutting board."], ci=0, cintent="plastic cutting board|plastic"),

 dict(sub="instrumental", sc=7, why="which towel for drying, the dish towel is the default and paper towels are wanted",
   a="Pick up the dirty mug from the counter, wash it with the sponge and dish soap, rinse it under the tap, dry it with a towel, and put it in the cupboard.",
   ap=["Pick up the dirty mug from the counter.", "Wash it with the sponge and dish soap.",
       "Rinse it under the tap.", "Dry it with a towel.", "Put it in the cupboard."],
   ai=3, intent="paper",
   c="Wash the dirty mug from the counter and dry it with the paper towels, then wash the dirty cutlery and the dirty knife.",
   cp=["Wash the dirty mug from the counter and dry it with the paper towels.",
       "Wash the dirty cutlery.",
       "Wash the dirty knife."], ci=0, cintent="paper towels|paper"),

 dict(sub="referential", sc=5, why="which sweetener, sugar is the default and honey is wanted",
   a="Brew the black tea in the white mug with water from the electric kettle, sweeten it, stir it with the spoon, and take it to the kitchen table.",
   ap=["Brew the black tea in the white mug with water from the electric kettle.", "Sweeten it.",
       "Stir it with the spoon.", "Take it to the kitchen table."], ai=1, intent="honey",
   c="Stir the honey into the black tea in the white mug, then add the mint leaves and a slice of the lemon to it.",
   cp=["Stir the honey into the black tea in the white mug.",
       "Add the mint leaves to the white mug.",
       "Add a slice of the lemon to the white mug."], ci=0, cintent="honey"),

 dict(sub="instrumental", sc=3, why="which mixing tool, the stand mixer is canonical for dough and the whisk is wanted",
   a="Mix the cookie dough in the large mixing bowl, then spoon it onto the nonstick baking sheet and bake it.",
   ap=["Mix the cookie dough in the large mixing bowl.",
       "Spoon it onto the nonstick baking sheet.", "Bake it."], ai=0, intent="whisk",
   c="Mix the cookie dough in the large mixing bowl with the whisk, then fold in the chocolate chips and the walnuts with it too.",
   cp=["Mix the cookie dough in the large mixing bowl with the whisk.",
       "Fold in the chocolate chips with the whisk.",
       "Fold in the walnuts with the whisk."], ci=0, cintent="whisk"),

 dict(sub="instrumental", sc=4, why="which serving vessel, pasta bowls are canonical and the dinner plates are wanted",
   a="Drain the spaghetti in the colander, serve it, spoon the tomato sauce over it, and put a fork beside each one.",
   ap=["Drain the spaghetti in the colander.", "Serve the spaghetti.",
       "Spoon the tomato sauce over it.", "Put a fork beside each one."],
   ai=1, intent="dinner plates|dinner plate",
   c="Serve the spaghetti on the two dinner plates, then spoon the tomato sauce over both plates and grate the parmesan over both plates.",
   cp=["Serve the spaghetti on the two dinner plates.",
       "Spoon the tomato sauce over both plates.",
       "Grate the parmesan over both plates."], ci=0, cintent="dinner plates|dinner plate"),

 dict(sub="referential", sc=4, why="which meat, ground beef is canonical for a pasta sauce and the chicken is wanted",
   a="Brown the meat in the frying pan with the olive oil, stir it into the pot of tomato sauce, and simmer it.",
   ap=["Brown the meat in the frying pan with the olive oil.",
       "Stir it into the pot of tomato sauce.", "Simmer it."], ai=0, intent="chicken",
   c="Brown the chicken breasts in the frying pan with the olive oil, then stir in the canned tomatoes and the garlic.",
   cp=["Brown the chicken breasts in the frying pan with the olive oil.",
       "Stir in the canned tomatoes.",
       "Stir in the garlic."], ci=0, cintent="chicken breasts|chicken"),

 dict(sub="instrumental", sc=6, why="which peeling tool, the peeler is canonical and the paring knife is wanted",
   a="Peel the carrots over the sink, slice them on the wooden cutting board, and put the slices in the large salad bowl.",
   ap=["Peel the carrots over the sink.", "Slice them on the wooden cutting board.",
       "Put the slices in the large salad bowl."], ai=0, intent="paring",
   c="Peel the carrots over the sink with the paring knife, then peel the cucumber and the avocado with it too.",
   cp=["Peel the carrots over the sink with the paring knife.",
       "Peel the cucumber with the paring knife.",
       "Peel the avocado with the paring knife."], ci=0, cintent="paring knife|paring"),

 dict(sub="instrumental", sc=7, why="how to wash, the dishwasher is canonical for four bowls and the sink is wanted",
   a="Wash the four dirty bowls, dry them with the dish towel, and stack them in the cupboard.",
   ap=["Wash the four dirty bowls.", "Dry them with the dish towel.",
       "Stack them in the cupboard."], ai=0, intent="sink|by hand",
   c="Wash the four dirty bowls by hand in the sink, then wash the dirty cutlery and the dirty saucepan in the sink too.",
   cp=["Wash the four dirty bowls by hand in the sink.",
       "Wash the dirty cutlery in the sink.",
       "Wash the dirty saucepan in the sink."], ci=0, cintent="sink|by hand|hand"),

 dict(sub="instrumental", sc=8, why="which scooping tool, the ice cream scoop is canonical and a spoon is wanted",
   a="Scoop two scoops of chocolate ice cream into the ceramic bowl, drizzle on the caramel sauce, and carry it to the kitchen table.",
   ap=["Scoop two scoops of chocolate ice cream into the ceramic bowl.",
       "Drizzle on the caramel sauce.", "Carry it to the kitchen table."], ai=0, intent="spoon",
   c="Scoop two scoops of chocolate ice cream into the ceramic bowl with a spoon, then put the strawberries and the blueberries on top.",
   cp=["Scoop two scoops of chocolate ice cream into the ceramic bowl with a spoon.",
       "Put the strawberries on top.",
       "Put the blueberries on top."], ci=0, cintent="spoon"),

 dict(sub="instrumental", sc=10, why="which wrapping, sandwich bags are canonical and the foil is wanted",
   a="Make a peanut butter sandwich with the sliced bread, wrap it, and put it in the blue lunch box.",
   ap=["Make a peanut butter sandwich with the sliced bread.", "Wrap the sandwich.",
       "Put it in the blue lunch box."], ai=1, intent="foil",
   c="Wrap the peanut butter sandwich in the aluminum foil, then put the crackers and the grapes in the blue lunch box.",
   cp=["Wrap the peanut butter sandwich in the aluminum foil.",
       "Put the crackers in the blue lunch box.",
       "Put the grapes in the blue lunch box."], ci=0, cintent="aluminum foil|foil"),
]
