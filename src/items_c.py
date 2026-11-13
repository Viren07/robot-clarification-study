from items_a import A, C

S8 = dict(
    name="Dessert and snack kitchen",
    objects=("a fridge, a freezer, a counter, a kitchen table, a cupboard, a sink, a microwave, a blender, a tub of vanilla ice cream in the top freezer drawer, "
             "a tub of vanilla ice cream in the bottom freezer drawer, a tub of vanilla ice cream in the freezer door, a tub of chocolate ice cream, "
             "a tub of strawberry ice cream, chocolate sauce, caramel sauce, sprinkles, whipped cream, bananas, strawberries, blueberries, "
             "a red tin of cookies, a blue tin of crackers, brownies, a pie, a cake, a bag of microwave popcorn, a bag of chips, a bag of pretzels, "
             "sliced cheese, a glass bowl, a plastic bowl, a ceramic bowl, a paper bowl, a ceramic plate, a paper plate, a glass plate, "
             "four matching dinner plates on the shelf, four spoons, napkins, an ice cream scoop, a cake knife"),
    items=[
        A("Scoop two scoops of vanilla ice cream into the glass bowl.", "A3: three or more candidates",
          "Three tubs of vanilla ice cream (top drawer, bottom drawer, door) and nothing says which one.",
          ["Take a tub of vanilla ice cream.", "Take the ice cream scoop.", "Scoop two scoops into the glass bowl.", "Put the tub back in the freezer."], 1, 3, pair=(8, 1)),
        C("Scoop two scoops of vanilla ice cream from the top freezer drawer into the glass bowl.", "U1: explicit resolver next to distractors",
          "Three vanilla tubs exist, but the instruction names the one in the top drawer.",
          ["Take the tub of vanilla ice cream from the top freezer drawer.", "Take the ice cream scoop.", "Scoop two scoops into the glass bowl.", "Put the tub back in the top drawer."], 1, pair=(8, 1)),
        A("Make my usual dessert.", "A2: hidden user preference",
          "Flavor, sauce and toppings depend on a 'usual' the robot cannot know.",
          ["Take a bowl.", "Add a base.", "Add a sauce.", "Add a topping."], 2, 6, pair=(8, 2)),
        C("Put two scoops of chocolate ice cream in the ceramic bowl and top it with chocolate sauce and sprinkles.", "U2: fully specified parameters",
          "Flavor, bowl, sauce and topping are stated.",
          ["Take the ceramic bowl.", "Scoop two scoops of chocolate ice cream into it.", "Pour chocolate sauce on top.", "Add sprinkles."], 1, pair=(8, 2)),
        A("Set up for dessert.", "A1: vague verb, one salient object",
          "Could mean setting out plates and spoons, taking out the dessert itself, or both.",
          ["Pick up the dessert items.", "Place them on the kitchen table."], 1, 3, pair=(8, 3)),
        C("Put the four matching dinner plates, the four spoons and the napkins on the kitchen table.", "U3: conjunction of named objects",
          "Every item and its count are stated.",
          ["Take the four plates and put them on the kitchen table.", "Take the four spoons and put them on the kitchen table.", "Take the napkins and put them on the kitchen table."], 1, pair=(8, 3)),
        C("Open the red tin of cookies.", "U4: unique reference in a crowded scene",
          "Two tins exist, but only one is red and it holds the cookies.",
          ["Take the red tin.", "Open the lid."], 1),
        C("Microwave the bag of popcorn.", "U5: scene resolves a vague-sounding request",
          "Sounds underspecified (how long?), but the scene has one microwave and one popcorn bag and the bag gives the time.",
          ["Put the bag of popcorn in the microwave.", "Close the microwave.", "Switch on the microwave."], 1),
        A("Cut a slice of the cake and serve it.", "A4: choice late in a multi-step task",
          "Cutting is fixed. What to serve it on (ceramic, paper or glass plate) is the user's choice.",
          ["Take the cake knife.", "Cut a slice of cake.", "Lift the slice.", "Put the slice on a plate."], 4, 3),
        A("Get a snack ready.", "A1: vague verb, one salient object",
          "Could mean popcorn, chips, or cookies, in a bowl or on a plate.",
          ["Pick a snack.", "Put it in a container.", "Put it on the kitchen table."], 1, 4),
    ],
)

S9 = dict(
    name="Grocery unpacking kitchen",
    objects=("a fridge, a freezer, a pantry cupboard, a counter, a kitchen table, a glass bowl, a wooden bowl, a metal bowl, "
             "a shopping bag on the kitchen table, a shopping bag on the counter, a shopping bag on the floor, a carton of milk, a carton of eggs, "
             "butter, yogurt, cheese, raw chicken breasts, raw ground beef, frozen peas, ice cream, a loaf of bread, apples, bananas, potatoes, "
             "onions, canned beans, a bag of rice with a green label, a bag of rice with a red label, pasta, a box of cereal, cookies, olive oil, "
             "paper towels, a bag of flour, freezer bags, a plastic food container, aluminum foil, a marker"),
    items=[
        A("Unpack the shopping bag.", "A3: three or more candidates",
          "Three shopping bags (table, counter, floor) and nothing says which one.",
          ["Take a shopping bag.", "Take the items out of the bag.", "Put the items on the counter."], 1, 3, pair=(9, 1)),
        C("Unpack the shopping bag on the kitchen table.", "U1: explicit resolver next to distractors",
          "Three bags exist, but the instruction names the one on the kitchen table.",
          ["Take the shopping bag from the kitchen table.", "Take the items out of the bag.", "Put the items on the counter."], 1, pair=(9, 1)),
        A("Put the groceries away the way I like.", "A2: hidden user preference",
          "Which shelf or drawer each item goes in depends on the user's habits.",
          ["Take an item.", "Choose its place.", "Put it there."], 2, 5, pair=(9, 2)),
        C("Put the carton of milk on the door shelf of the fridge.", "U2: fully specified parameters",
          "Item and exact place are stated.",
          ["Take the carton of milk.", "Open the fridge.", "Put the carton on the door shelf.", "Close the fridge."], 1, pair=(9, 2)),
        A("Sort out the groceries.", "A1: vague verb, one salient object",
          "Could mean putting them away by place, grouping them by type on the counter, or checking them against a list.",
          ["Take the groceries.", "Group them.", "Put them down."], 1, 3, pair=(9, 3)),
        C("Put the frozen peas and the ice cream in the freezer.", "U3: conjunction of named objects",
          "Both items are named and each exists once.",
          ["Take the frozen peas and put them in the freezer.", "Take the ice cream and put it in the freezer."], 1, pair=(9, 3)),
        C("Put the bag of rice with the green label in the pantry cupboard.", "U4: unique reference in a crowded scene",
          "Two rice bags exist, but only one has a green label.",
          ["Take the bag of rice with the green label.", "Open the pantry cupboard.", "Put the bag in the cupboard.", "Close the cupboard."], 1),
        C("Put the cereal in the pantry cupboard.", "U5: scene resolves a vague-sounding request",
          "Sounds underspecified, but the scene has one box of cereal and one pantry cupboard.",
          ["Take the box of cereal.", "Open the pantry cupboard.", "Put the box in the cupboard.", "Close the cupboard."], 1),
        A("Freeze the ground beef in portions.", "A4: choice late in a multi-step task",
          "Portioning is fixed. What to freeze it in (freezer bags, plastic container or foil) is the user's choice.",
          ["Take the ground beef.", "Divide it into portions.", "Wrap each portion.", "Put the portions in the freezer."], 3, 3),
        A("Put the fruit in a bowl.", "A3: three or more candidates",
          "Three bowls (glass, wooden, metal) and nothing says which one.",
          ["Take the apples and the bananas.", "Take a bowl.", "Put the fruit in the bowl.", "Put the bowl on the kitchen table."], 2, 3),
    ],
)

S10 = dict(
    name="Lunch box packing kitchen",
    objects=("a fridge, a counter, a kitchen table, a cupboard, a sink, a red lunch box, a blue lunch box, a green lunch box, "
             "a steel water bottle on the counter, a plastic water bottle on the kitchen table, a glass water bottle in the fridge door, a thermos, "
             "one ice pack, sandwich bags, aluminum foil, cling wrap, snack bags, sliced bread, peanut butter, jelly, cheese sticks, "
             "a yogurt cup with a strawberry label, a yogurt cup with a vanilla label, a yogurt cup with a blueberry label, crackers, carrots, "
             "grapes, an apple, an oat granola bar, a chocolate granola bar, juice boxes, napkins, a butter knife, a spoon, a backpack"),
    items=[
        A("Fill the water bottle with water.", "A3: three or more candidates",
          "Three water bottles (counter, table, fridge door) and nothing says which one.",
          ["Take a water bottle.", "Open the bottle.", "Fill it with water at the sink.", "Close the bottle."], 1, 3, pair=(10, 1)),
        C("Fill the water bottle on the counter with water.", "U1: explicit resolver next to distractors",
          "Three bottles exist, but the instruction names the one on the counter.",
          ["Take the steel water bottle from the counter.", "Open the bottle.", "Fill it with water at the sink.", "Close the bottle."], 1, pair=(10, 1)),
        A("Pack my lunch the way I like it.", "A2: hidden user preference",
          "Main item, snacks, drink and box depend on the user's habits.",
          ["Pick a lunch box.", "Pick the food.", "Put the food in the box.", "Close the box."], 1, 6, pair=(10, 2)),
        C("Make a peanut butter sandwich on sliced bread and wrap it in foil.", "U2: fully specified parameters",
          "Filling, bread and wrapping are stated.",
          ["Take two slices of sliced bread.", "Spread peanut butter on one slice.", "Close the sandwich.", "Wrap the sandwich in aluminum foil."], 1, pair=(10, 2)),
        A("Get the lunch things together.", "A1: vague verb, one salient object",
          "Could mean gathering containers, gathering food, or gathering both on the table.",
          ["Pick up the lunch items.", "Put them on the kitchen table."], 1, 3, pair=(10, 3)),
        C("Put the ice pack, the napkins and the sandwich bags on the kitchen table.", "U3: conjunction of named objects",
          "All three items are named and each exists once.",
          ["Take the ice pack and put it on the kitchen table.", "Take the napkins and put them on the kitchen table.", "Take the sandwich bags and put them on the kitchen table."], 1, pair=(10, 3)),
        C("Put the blueberry yogurt cup in the green lunch box.", "U4: unique reference in a crowded scene",
          "Three yogurt cups exist, but only one has a blueberry label.",
          ["Take the yogurt cup with the blueberry label.", "Open the green lunch box.", "Put the yogurt cup in the box.", "Close the box."], 1),
        C("Put the ice pack in the fridge.", "U5: scene resolves a vague-sounding request",
          "Sounds underspecified, but the scene has one ice pack and one fridge.",
          ["Take the ice pack.", "Open the fridge.", "Put the ice pack in the fridge.", "Close the fridge."], 1),
        A("Make a cheese sandwich and wrap it up.", "A4: choice late in a multi-step task",
          "Making is fixed. What to wrap it in (foil, cling wrap or a sandwich bag) is the user's choice.",
          ["Take two slices of sliced bread.", "Put cheese on one slice.", "Close the sandwich.", "Wrap the sandwich."], 4, 3),
        A("Put a snack in the green lunch box.", "A3: three or more candidates",
          "Several snacks (crackers, grapes, granola bars) and nothing says which one.",
          ["Take a snack.", "Open the green lunch box.", "Put the snack in the box.", "Close the box."], 1, 3),
    ],
)

SCENES_C = [S8, S9, S10]
