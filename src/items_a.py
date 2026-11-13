"""Scenes 1-4. Each scene: objects string + 10 items.
Item = dict(txt, cat, typ, pair, why, cands, plan, step); step is 1-based."""


def C(txt, typ, why, plan, step, pair=None, cands=1):
    return dict(txt=txt, cat="Unambiguous", typ=typ, pair=pair, why=why, cands=cands, plan=plan, step=step)


def A(txt, typ, why, plan, step, cands, pair=None):
    return dict(txt=txt, cat="Ambiguous", typ=typ, pair=pair, why=why, cands=cands, plan=plan, step=step)


S1 = dict(
    name="Breakfast kitchen",
    objects=("a toaster, a coffee machine with a full pot of fresh coffee, an electric kettle, a microwave, a stovetop, "
             "an oven, a fridge, a sink, a sponge, dish soap, a kitchen table, a cupboard, sliced white bread, "
             "sliced whole wheat bread, a stick of butter, slices of cheddar cheese, strawberry jam, a jar of honey in the cupboard, "
             "a jar of honey on the kitchen table, a jar of honey on the counter, peanut butter, six eggs, a frying pan, a saucepan, "
             "a spatula, a whisk, a mixing bowl, a red mug, a blue mug, a green mug with a chipped handle, "
             "a white mug of black coffee on the kitchen table, two clean drinking glasses, four clean white plates, "
             "a dirty plate with crumbs, a dirty fork and a dirty drinking glass on the kitchen table, "
             "a plate of leftover pancakes, a saucepan of leftover soup, a glass food container, a plastic food container, "
             "a spoon, a knife, a cutting board"),
    items=[
        A("Stir a spoonful of honey into the coffee in the white mug.", "A3: three or more candidates",
          "Three jars of honey (cupboard, table, counter). Nothing says which jar the user wants.",
          ["Take the white mug of coffee from the kitchen table.", "Take a jar of honey.", "Scoop a spoonful of honey with the spoon.",
           "Stir the honey into the coffee.", "Put the white mug back on the kitchen table."], 2, 3, pair=(1, 1)),
        C("Stir a spoonful of the honey from the cupboard into the coffee in the white mug.", "U1: explicit resolver next to distractors",
          "Three honey jars exist, but the instruction names the one in the cupboard.",
          ["Take the white mug of coffee from the kitchen table.", "Take the jar of honey from the cupboard.", "Scoop a spoonful of honey with the spoon.",
           "Stir the honey into the coffee.", "Put the white mug back on the kitchen table."], 2, pair=(1, 1)),
        A("Make toast the way I like it.", "A2: hidden user preference",
          "Bread type, darkness and topping depend on the user's taste. Nothing in the scene shows it.",
          ["Take slices of bread.", "Place the slices in the toaster.", "Set the toaster darkness.", "Start the toaster.", "Add a topping to the toast."], 1, 4, pair=(1, 2)),
        C("Toast two slices of sliced whole wheat bread on the medium setting and spread butter on both slices.", "U2: fully specified parameters",
          "Bread, toaster setting and topping are all stated.",
          ["Take two slices of sliced whole wheat bread.", "Place the slices in the toaster.", "Set the toaster to medium and start it.",
           "Take the toast out when it pops.", "Spread butter on both slices with the knife."], 1, pair=(1, 2)),
        A("Clean up after breakfast.", "A1: vague verb, one salient object",
          "'Clean up' could mean washing the dirty dishes, wiping the table, or putting food away.",
          ["Take the dirty plate, fork and glass to the sink.", "Wash them with the sponge and dish soap.", "Put the clean items on the counter."], 1, 3, pair=(1, 3)),
        C("Wash the dirty plate, the dirty fork and the dirty glass in the sink.", "U3: conjunction of named objects",
          "Every object to wash is named, and the scene has exactly one of each.",
          ["Take the dirty plate, fork and glass from the kitchen table to the sink.", "Wash the plate with the sponge and dish soap.",
           "Wash the fork.", "Wash the glass.", "Put the clean items on the counter."], 1, pair=(1, 3)),
        C("Pour the coffee from the pot into the mug with the chipped handle.", "U4: unique reference in a crowded scene",
          "Four mugs are present, but only the green one has a chipped handle.",
          ["Take the coffee pot from the coffee machine.", "Pick up the green mug with the chipped handle.", "Pour coffee into the green mug.", "Put the pot back."], 2),
        C("Grill a cheese sandwich on the panini press.", "U6: groundability gap",
          "The request is clear but the scene has no panini press. Score as a groundability case, not as a false alarm.",
          ["Take two slices of sliced white bread.", "Put a slice of cheddar cheese between the slices.", "Place the sandwich on the panini press.",
           "Close the press and wait until the cheese melts."], 3, cands=0),
        A("Boil two eggs and put them somewhere to cool.", "A4: choice late in a multi-step task",
          "All steps are fixed until the last one. Where to cool the eggs (bowl of cold water, plate, fridge) is the user's choice.",
          ["Fill the saucepan with water.", "Place the saucepan on the stovetop and switch it on.", "Put two eggs in the water.", "Boil the eggs for eight minutes.",
           "Remove the eggs with the spoon.", "Put the eggs somewhere to cool."], 6, 3),
        A("Pack the leftovers for tomorrow's lunch.", "A5: mixed (referent and preference)",
          "Which leftovers (pancakes, soup or both) and which container (glass or plastic) are both open.",
          ["Pick the leftovers to pack.", "Pick a food container.", "Transfer the food into the container.", "Close the container and put it in the fridge."], 1, 6),
    ],
)

S2 = dict(
    name="Sandwich and lunch prep kitchen",
    objects=("a fridge, a sink, a kitchen table, a counter, a cupboard, a microwave, a stovetop, a loaf of rye bread, a loaf of white bread, "
             "a bag of bagels, a jar of mustard, a jar of mayonnaise, a bottle of ketchup, a block of cheddar cheese, sliced Swiss cheese, "
             "sliced ham, sliced turkey, a tomato, a head of lettuce, a cucumber, a jar of pickles, a bread knife, a butter knife, a cutting board, "
             "a blue plate, a white plate, a paper plate, a lunch box, a steel thermos with a dented lid, a plastic thermos, a zip bag, "
             "a red apple on the counter, a green apple in the fridge, a yellow apple on the kitchen table, a bottle of water, a juice box, "
             "a can of soda, a bowl of chips, a bowl of grapes, a wrapped sandwich on the counter, a pot of tomato soup on the stovetop, "
             "a saucepan, a blue bowl, a white bowl, a mug"),
    items=[
        A("Put the apple in the lunch box.", "A3: three or more candidates",
          "Three apples (red, green, yellow) and nothing says which one.",
          ["Take an apple.", "Open the lunch box.", "Place the apple in the lunch box.", "Close the lunch box."], 1, 3, pair=(2, 1)),
        C("Put the apple from the fridge in the lunch box.", "U1: explicit resolver next to distractors",
          "Three apples exist, but only one is in the fridge.",
          ["Take the green apple from the fridge.", "Open the lunch box.", "Place the apple in the lunch box.", "Close the lunch box."], 1, pair=(2, 1)),
        A("Make me a sandwich the usual way.", "A2: hidden user preference",
          "Bread, filling and sauce depend on a 'usual' the robot cannot know.",
          ["Take two slices of bread.", "Spread a sauce on one slice.", "Add fillings.", "Close the sandwich.", "Put the sandwich on a plate."], 1, 6, pair=(2, 2)),
        C("Make a sandwich with two slices of rye bread, a slice of Swiss cheese, a slice of turkey and mustard, and put it on the white plate.", "U2: fully specified parameters",
          "Bread, filling, sauce and plate are all stated.",
          ["Take two slices of rye bread.", "Spread mustard on one slice.", "Add a slice of Swiss cheese and a slice of turkey.", "Close the sandwich with the second slice.",
           "Put the sandwich on the white plate."], 1, pair=(2, 2)),
        A("Get the lunch ready.", "A1: vague verb, one salient object",
          "Could mean making a sandwich, packing the lunch box with what is already prepared, or setting out lunch on the table.",
          ["Pick up the lunch items.", "Open the lunch box.", "Put the items in the lunch box.", "Close the lunch box."], 1, 3, pair=(2, 3)),
        C("Put the wrapped sandwich, the grapes and the juice box into the lunch box.", "U3: conjunction of named objects",
          "All three items are named and the scene has exactly one of each.",
          ["Open the lunch box.", "Put the wrapped sandwich in the lunch box.", "Put the grapes in the lunch box.", "Put the juice box in the lunch box.", "Close the lunch box."], 2, pair=(2, 3)),
        C("Fill the thermos that has the dented lid with water.", "U4: unique reference in a crowded scene",
          "Two thermoses exist, but only the steel one has a dented lid.",
          ["Take the steel thermos with the dented lid.", "Open the thermos.", "Fill the thermos with water from the sink.", "Close the thermos."], 1),
        C("Slice the tomato with the electric slicer.", "U6: groundability gap",
          "The request is clear but the scene has no electric slicer. Score as a groundability case, not as a false alarm.",
          ["Take the tomato.", "Place the tomato on the cutting board.", "Slice the tomato with the electric slicer."], 3, cands=0),
        A("Warm up the tomato soup and serve it.", "A4: choice late in a multi-step task",
          "Heating is fixed. What to serve it in (blue bowl, white bowl or mug) is the user's choice.",
          ["Switch on the stovetop under the pot of tomato soup.", "Heat the soup until hot.", "Switch off the stovetop.", "Serve the soup in a container."], 4, 3),
        A("Pack a snack for the trip.", "A5: mixed (referent and preference)",
          "Which snack (chips, grapes or an apple) and which container (zip bag or lunch box) are both open.",
          ["Pick a snack.", "Pick a container.", "Put the snack in the container.", "Close the container."], 1, 6),
    ],
)

S3 = dict(
    name="Baking kitchen",
    objects=("an oven, a stand mixer, a fridge, a counter, a sink, a cupboard, a bag of all-purpose flour, a bag of whole wheat flour, "
             "a bag of white sugar on the counter, a bag of white sugar in the cupboard, a bag of white sugar on the top shelf of the fridge, "
             "a bag of brown sugar, powdered sugar, baking soda, baking powder, a carton of eggs, salted butter, unsalted butter, milk, "
             "vanilla extract, chocolate chips, walnuts, cinnamon, a bowl of cookie dough, a springform pan, a plain round cake pan, "
             "a square baking dish, a muffin tray, a nonstick baking sheet, a rusty baking sheet, a rolling pin, a whisk, a spatula, "
             "a large mixing bowl, a small bowl, measuring cups, measuring spoons, a wire cooling rack, oven mitts, a timer, parchment paper, "
             "a baked cake on the cooling rack, a tub of vanilla frosting"),
    items=[
        A("Add a cup of sugar to the large mixing bowl.", "A3: three or more candidates",
          "Three bags of white sugar (counter, cupboard, fridge shelf) and nothing says which one.",
          ["Take a bag of sugar.", "Measure one cup of sugar with the measuring cups.", "Pour the sugar into the large mixing bowl.", "Put the bag back."], 1, 3, pair=(3, 1)),
        C("Add a cup of the sugar from the cupboard to the large mixing bowl.", "U1: explicit resolver next to distractors",
          "Three bags of sugar exist, but the instruction names the one in the cupboard.",
          ["Take the bag of sugar from the cupboard.", "Measure one cup of sugar with the measuring cups.", "Pour the sugar into the large mixing bowl.", "Put the bag back in the cupboard."], 1, pair=(3, 1)),
        A("Bake the cookies the way I like them.", "A2: hidden user preference",
          "Chewy or crisp, size and baking time depend on the user's taste.",
          ["Preheat the oven.", "Shape the cookie dough.", "Place the dough on a baking sheet.", "Bake the cookies.", "Take the cookies out."], 2, 4, pair=(3, 2)),
        C("Bake the cookie dough on the nonstick baking sheet at 350 degrees for 12 minutes.", "U2: fully specified parameters",
          "Pan, temperature and time are stated.",
          ["Preheat the oven to 350 degrees.", "Put balls of cookie dough on the nonstick baking sheet.", "Place the sheet in the oven.", "Bake for 12 minutes.",
           "Take the sheet out with the oven mitts."], 2, pair=(3, 2)),
        A("Prepare the baking station.", "A1: vague verb, one salient object",
          "Could mean setting out tools, setting out ingredients, or preheating the oven.",
          ["Pick up the baking items.", "Place them on the counter."], 1, 3, pair=(3, 3)),
        C("Put the whisk, the measuring cups and the large mixing bowl on the counter.", "U3: conjunction of named objects",
          "All three objects are named and each exists once.",
          ["Take the whisk and put it on the counter.", "Take the measuring cups and put them on the counter.", "Take the large mixing bowl and put it on the counter."], 1, pair=(3, 3)),
        C("Line the springform pan with parchment paper.", "U4: unique reference in a crowded scene",
          "Three pans are present, but only one is a springform pan.",
          ["Take the springform pan.", "Take a sheet of parchment paper.", "Line the pan with the paper."], 1),
        C("Frost the cake with the piping bag.", "U6: groundability gap",
          "The request is clear but the scene has no piping bag. Score as a groundability case, not as a false alarm.",
          ["Take the cake from the cooling rack.", "Fill the piping bag with frosting.", "Pipe the frosting onto the cake."], 2, cands=0),
        A("Mix the cake batter and bake it.", "A4: choice late in a multi-step task",
          "Mixing is fixed. Which pan to bake in (springform, round pan or square dish) is the user's choice.",
          ["Pour flour, sugar and eggs into the large mixing bowl.", "Mix them with the whisk.", "Preheat the oven.", "Pour the batter into a pan.", "Bake the cake."], 4, 3),
        A("Set out the toppings for the cookies somewhere handy.", "A5: mixed (referent and preference)",
          "Which toppings (chocolate chips, walnuts, cinnamon) and where to put them (counter or table) are both open.",
          ["Pick the toppings.", "Pick a place.", "Put the toppings there."], 1, 6),
    ],
)

S4 = dict(
    name="Dinner (pasta) kitchen",
    objects=("a stovetop, an oven, a fridge, a sink, a counter, a kitchen table, a cupboard, a large pot, a medium pot with a glass lid, a pot of tomato sauce simmering on the stovetop, "
             "a colander, a frying pan, a wooden spoon, a ladle, a knife, a cutting board, a box of spaghetti in the cupboard, "
             "a box of penne on the counter, a box of fusilli on top of the fridge, a jar of tomato sauce, a jar of alfredo sauce, a jar of pesto, "
             "grated parmesan, mozzarella, olive oil, vegetable oil, salt, black pepper, chili flakes, garlic, onions, red bell peppers, mushrooms, "
             "ground beef, chicken breasts, canned tomatoes, two pasta bowls, two dinner plates, two forks"),
    items=[
        A("Cook the pasta in the large pot.", "A3: three or more candidates",
          "Three kinds of pasta (spaghetti, penne, fusilli) and nothing says which one.",
          ["Fill the large pot with water.", "Put the pot on the stovetop and switch it on.", "Take a box of pasta.", "Pour the pasta into the boiling water.", "Cook until done."], 3, 3, pair=(4, 1)),
        C("Cook the penne from the box on the counter in the large pot.", "U1: explicit resolver next to distractors",
          "Three pasta boxes exist, but the instruction names the one on the counter.",
          ["Fill the large pot with water.", "Put the pot on the stovetop and switch it on.", "Take the box of penne from the counter.", "Pour the pasta into the boiling water.", "Cook until done."], 3, pair=(4, 1)),
        A("Season the simmering sauce to my taste.", "A2: hidden user preference",
          "Salt, pepper and chili amounts depend on the user's taste.",
          ["Take the seasonings.", "Add seasoning to the sauce.", "Stir the sauce."], 2, 4, pair=(4, 2)),
        C("Season the simmering sauce with a teaspoon of salt and a pinch of chili flakes.", "U2: fully specified parameters",
          "Seasonings and amounts are stated.",
          ["Take the salt and the chili flakes.", "Add a teaspoon of salt to the sauce.", "Add a pinch of chili flakes to the sauce.", "Stir the sauce."], 2, pair=(4, 2)),
        A("Get dinner started.", "A1: vague verb, one salient object",
          "Could mean taking ingredients out, boiling water, or heating a pan.",
          ["Pick up dinner ingredients.", "Place them on the counter."], 1, 3, pair=(4, 3)),
        C("Take the ground beef, the onions and the garlic out of the fridge.", "U3: conjunction of named objects",
          "All three items are named and each exists once.",
          ["Take the ground beef from the fridge.", "Take the onions from the fridge.", "Take the garlic from the fridge."], 1, pair=(4, 3)),
        C("Fill the pot that has the glass lid with water.", "U4: unique reference in a crowded scene",
          "Three pots are present, but only one has a glass lid.",
          ["Take the pot with the glass lid.", "Fill it with water at the sink.", "Put the pot on the counter."], 1),
        C("Saute the onions in the wok.", "U6: groundability gap",
          "The request is clear but the scene has no wok. Score as a groundability case, not as a false alarm.",
          ["Take the onions.", "Slice the onions.", "Put the onions in the wok and saute them."], 3, cands=0),
        A("Cook the ground beef and add a sauce.", "A4: choice late in a multi-step task",
          "Cooking is fixed. Which sauce (tomato, alfredo or pesto) is the user's choice.",
          ["Put the frying pan on the stovetop.", "Add the ground beef.", "Cook until brown.", "Add a sauce.", "Stir and heat."], 4, 3),
        A("Serve dinner for two.", "A5: mixed (referent and preference)",
          "Which dishes make up dinner (pasta, chicken, both) and which plates or bowls to use are both open.",
          ["Pick the dishes to serve.", "Pick the plates or bowls.", "Serve the food.", "Put the plates on the kitchen table."], 1, 6),
    ],
)

SCENES_A = [S1, S2, S3, S4]
