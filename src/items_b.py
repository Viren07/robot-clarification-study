from items_a import A, C

S5 = dict(
    name="Drinks kitchen",
    objects=("a fridge, a sink, a counter, a kitchen table, a cupboard, a blender, an electric kettle, a coffee grinder, a French press, "
             "black tea bags, green tea bags, chamomile tea bags, coffee beans, whole milk, a carton of oat milk on the counter, "
             "a carton of oat milk in the fridge, a carton of oat milk in the cupboard, almond milk, orange juice, apple juice, a lemon, a lime, "
             "three oranges, a banana, strawberries, an ice tray, an ice bucket, a sugar bowl, a jar of honey, mint leaves, a tall glass, "
             "two short glasses, a wine glass, a red mug, a blue mug, a white mug, a pitcher, a spoon, a box of straws, "
             "a bottle of sparkling water, a bottle of still water"),
    items=[
        A("Pour a splash of oat milk into the blue mug.", "A3: three or more candidates",
          "Three cartons of oat milk (counter, fridge, cupboard) and nothing says which one.",
          ["Take a carton of oat milk.", "Open the carton.", "Pour a splash of oat milk into the blue mug.", "Close the carton and put it back."], 1, 3, pair=(5, 1)),
        C("Pour a splash of the oat milk from the fridge into the blue mug.", "U1: explicit resolver next to distractors",
          "Three oat milk cartons exist, but the instruction names the one in the fridge.",
          ["Take the carton of oat milk from the fridge.", "Open the carton.", "Pour a splash of oat milk into the blue mug.", "Close the carton and put it back in the fridge."], 1, pair=(5, 1)),
        A("Make my morning tea.", "A2: hidden user preference",
          "Tea type, sweetener and milk depend on the user's taste.",
          ["Boil water in the kettle.", "Take a tea bag.", "Put the tea bag in a mug.", "Pour hot water into the mug.", "Add extras."], 2, 6, pair=(5, 2)),
        C("Make a cup of green tea in the white mug with one teaspoon of honey.", "U2: fully specified parameters",
          "Tea, mug and sweetener are stated.",
          ["Boil water in the kettle.", "Put a green tea bag in the white mug.", "Pour hot water into the white mug.", "Add a teaspoon of honey with the spoon.", "Stir."], 2, pair=(5, 2)),
        A("Get the drinks ready.", "A1: vague verb, one salient object",
          "Could mean setting out glasses, filling the pitcher, or filling the ice bucket.",
          ["Pick up the drink items.", "Place them on the kitchen table."], 1, 3, pair=(5, 3)),
        C("Put the pitcher, the ice bucket and the tall glass on the kitchen table.", "U3: conjunction of named objects",
          "All three objects are named and each exists once.",
          ["Take the pitcher and put it on the kitchen table.", "Take the ice bucket and put it on the kitchen table.", "Take the tall glass and put it on the kitchen table."], 1, pair=(5, 3)),
        C("Squeeze the lime into the tall glass.", "U4: unique reference in a crowded scene",
          "Several citrus fruits are present, but only one is a lime.",
          ["Take the lime.", "Take the tall glass.", "Squeeze the lime into the tall glass."], 1),
        C("Put the ice from the tray into the ice bucket.", "U5: scene resolves a vague-sounding request",
          "Sounds underspecified, but the scene has exactly one ice tray and one ice bucket.",
          ["Take the ice tray.", "Take the ice bucket.", "Pour the ice into the ice bucket."], 1),
        A("Blend the fruit into a smoothie and pour it into a glass.", "A4: choice late in a multi-step task",
          "Blending is fixed. Which glass (tall, short or wine) is the user's choice.",
          ["Put the strawberries and the banana in the blender.", "Add milk.", "Blend until smooth.", "Pour the smoothie into a glass."], 4, 3),
        A("Bring the drinks out for the guests.", "A5: mixed (referent and preference)",
          "Which drinks (juice, sparkling water or tea) and where to serve them are both open.",
          ["Pick the drinks.", "Pick a place to serve them.", "Carry the drinks there."], 1, 6),
    ],
)

S6 = dict(
    name="Salad and chopping kitchen",
    objects=("a fridge, a sink, a counter, a kitchen table, a cupboard, a chef's knife, a paring knife, a serrated knife, a wooden cutting board, "
             "a plastic cutting board, a salad spinner, a large salad bowl containing a mixed salad, two small bowls, a colander, a grater, a peeler, a head of lettuce, "
             "spinach, kale, cherry tomatoes, a cucumber, carrots, a red onion, an avocado, a bell pepper, a jar of olives, feta cheese, croutons, "
             "olive oil, balsamic vinegar, lemon juice, a bottle of ranch dressing on the counter, a bottle of ranch dressing in the fridge, "
             "a bottle of ranch dressing in the cupboard, Caesar dressing, salt, pepper, tongs, two serving spoons"),
    items=[
        A("Pour ranch dressing over the salad in the large salad bowl.", "A3: three or more candidates",
          "Three bottles of ranch dressing (counter, fridge, cupboard) and nothing says which one.",
          ["Take a bottle of ranch dressing.", "Open the bottle.", "Pour dressing over the salad in the large salad bowl.", "Close the bottle and put it back."], 1, 3, pair=(6, 1)),
        C("Pour the ranch dressing from the counter bottle over the salad in the large salad bowl.", "U1: explicit resolver next to distractors",
          "Three ranch bottles exist, but the instruction names the one on the counter.",
          ["Take the bottle of ranch dressing from the counter.", "Open the bottle.", "Pour dressing over the salad in the large salad bowl.", "Close the bottle and put it back."], 1, pair=(6, 1)),
        A("Dress the salad how I like it.", "A2: hidden user preference",
          "Dressing, amount and tossing depend on the user's taste.",
          ["Take a dressing.", "Add dressing to the salad.", "Toss the salad."], 1, 5, pair=(6, 2)),
        C("Toss the salad in the large bowl with two tablespoons of olive oil and one tablespoon of balsamic vinegar.", "U2: fully specified parameters",
          "Ingredients and amounts are stated.",
          ["Add two tablespoons of olive oil to the large salad bowl.", "Add one tablespoon of balsamic vinegar.", "Toss the salad with the tongs."], 1, pair=(6, 2)),
        A("Prep the vegetables.", "A1: vague verb, one salient object",
          "Could mean washing, peeling and chopping, or only washing.",
          ["Pick up the vegetables.", "Process them.", "Put them in a bowl."], 1, 3, pair=(6, 3)),
        C("Wash the cucumber, the carrots and the cherry tomatoes in the sink.", "U3: conjunction of named objects",
          "All three are named and each exists once.",
          ["Take the cucumber and wash it in the sink.", "Take the carrots and wash them in the sink.", "Take the cherry tomatoes and wash them in the sink."], 1, pair=(6, 3)),
        C("Chop the red onion on the wooden cutting board.", "U4: unique reference in a crowded scene",
          "Two cutting boards are present, but the instruction names the wooden one.",
          ["Take the red onion.", "Place it on the wooden cutting board.", "Chop it with the chef's knife."], 2),
        C("Put the croutons in the large salad bowl.", "U5: scene resolves a vague-sounding request",
          "Sounds underspecified, but the scene has one box of croutons and one large salad bowl.",
          ["Take the croutons.", "Pour them into the large salad bowl."], 1),
        A("Chop the vegetables and put them in a bowl.", "A4: choice late in a multi-step task",
          "Chopping is fixed. Which bowl (large salad bowl or one of two small bowls) is the user's choice.",
          ["Take the vegetables.", "Place them on the cutting board.", "Chop them.", "Put the pieces in a bowl."], 4, 3),
        A("Make a quick salad and keep it somewhere cool.", "A5: mixed (referent and preference)",
          "Which ingredients to use and where to keep it (fridge shelf or bowl on the counter) are both open.",
          ["Pick the ingredients.", "Mix them in a bowl.", "Pick a cool place.", "Put the bowl there."], 1, 6),
    ],
)

S7 = dict(
    name="Cleanup kitchen",
    objects=("a sink, a dishwasher with eco, normal and intensive cycles, a counter, a kitchen table, a cupboard, a fridge, a trash can, "
             "a recycling bin, a compost bin, a sponge, a scrub brush, dish soap, dishwasher tablets, a dish towel, paper towels, spray cleaner, "
             "a floor mop, a broom, a dustpan, a dirty frying pan in the sink, a dirty saucepan, four dirty bowls, a dirty mug on the counter, "
             "a dirty mug on the kitchen table, a dirty mug in the sink, dirty cutlery, a glass jar with a screw-top lid, a glass jar with a clip lid, "
             "two empty cans, an empty pizza box, an empty milk carton, a plate of food scraps, a dirty cutting board, a dirty knife, a wooden spoon"),
    items=[
        A("Put the mug in the dishwasher.", "A3: three or more candidates",
          "Three dirty mugs (counter, table, sink) and nothing says which one.",
          ["Take a mug.", "Open the dishwasher.", "Place the mug in the dishwasher.", "Close the dishwasher."], 1, 3, pair=(7, 1)),
        C("Put the mug from the counter in the dishwasher.", "U1: explicit resolver next to distractors",
          "Three mugs exist, but the instruction names the one on the counter.",
          ["Take the dirty mug from the counter.", "Open the dishwasher.", "Place the mug in the dishwasher.", "Close the dishwasher."], 1, pair=(7, 1)),
        A("Wash the frying pan the way I prefer.", "A2: hidden user preference",
          "Scrub brush or sponge, soaking or not, and drying all depend on the user's habit.",
          ["Take the dirty frying pan.", "Wash it.", "Dry it.", "Put it on the counter."], 2, 4, pair=(7, 2)),
        C("Wash the frying pan with the scrub brush and dish soap, then dry it with the dish towel.", "U2: fully specified parameters",
          "Tools and steps are stated.",
          ["Take the dirty frying pan from the sink.", "Wash it with the scrub brush and dish soap.", "Rinse it.", "Dry it with the dish towel."], 2, pair=(7, 2)),
        A("Tidy the kitchen.", "A1: vague verb, one salient object",
          "Could mean taking out trash and recycling, washing the dishes, or wiping surfaces.",
          ["Pick up the items to tidy.", "Put them away."], 1, 3, pair=(7, 3)),
        C("Put the empty pizza box, the two empty cans and the empty milk carton in the recycling bin.", "U3: conjunction of named objects",
          "All items are named and the scene has exactly these.",
          ["Take the empty pizza box and put it in the recycling bin.", "Take the empty cans and put them in the recycling bin.",
           "Take the empty milk carton and put it in the recycling bin."], 1, pair=(7, 3)),
        C("Rinse the glass jar that has the clip lid.", "U4: unique reference in a crowded scene",
          "Two glass jars are present, but only one has a clip lid.",
          ["Take the glass jar with the clip lid.", "Open the lid.", "Rinse the jar in the sink."], 1),
        C("Put the dirty knife in the sink.", "U5: scene resolves a vague-sounding request",
          "Sounds underspecified, but the scene has exactly one dirty knife and one sink.",
          ["Take the dirty knife.", "Put the knife in the sink."], 1),
        A("Load the dishwasher with the four bowls and start it on a cycle.", "A4: choice late in a multi-step task",
          "Loading is fixed. Which cycle (eco, normal or intensive) is the user's choice.",
          ["Open the dishwasher.", "Place the four dirty bowls in the dishwasher.", "Add a dishwasher tablet.", "Close the dishwasher.", "Select a cycle and start it."], 5, 3),
        A("Deal with the trash.", "A1: vague verb, one salient object",
          "Could mean emptying the trash can, sorting recycling, or moving the food scraps to compost.",
          ["Pick up the trash items.", "Put them in a bin."], 1, 3),
    ],
)

SCENES_B = [S5, S6, S7]
