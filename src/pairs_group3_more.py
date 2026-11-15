"""GROUP 3 EXPANSION: 16 new test pairs, 8 sequential and 8 preconditional.

Takes group 3 from 18 test pairs to 34, which is what 102 pairs per half needs.

Written against a deliberate variety constraint. The existing 17 sequential pairs are 13
variations on "clean the tool between two uses" (wash, rinse or wipe a board, knife, scoop,
grater, measuring cup, sponge, bowl or cake knife), and the existing preconditional pairs
cluster on "wash before" and "wrap before storing". Not one family below is reused:

  sequential      turn the heat off, let the dough rest, stir between additions, take the
                  tea bag out, replace a lid first, seal a bag first, label between batches,
                  spin the salad dry
  preconditional  soften the butter, take the pan off the heat, thaw the chicken, empty the
                  sink, take the lid off before microwaving, peel before blending, unwrap
                  before plating, let the cake cool before cutting

Recipe, unchanged and now measured rather than guessed (group 3 averages 0.3750 over four
runs, the hardest of the three groups):
  ambiguous  two sub-actions whose order is given, with the step BETWEEN them left unstated,
             scored at the step before the gap
  clear      same scene, same task, the missing step stated, then two further PARALLEL
             actions over same-kind objects, scored at index 0

is_similar patterns are lowercase: it lowercases the option text but not the pattern.
"""
PAIRS = [
 # ---------------- SEQUENTIAL ----------------
 dict(sub="sequential", sc=4, why="turning the stovetop off between moving two pots",
   a="Take the pot of tomato sauce off the stovetop and put the frying pan on in its place.",
   ap=["Take the pot of tomato sauce off the stovetop.",
       "Put the frying pan on the stovetop."], ai=0, intent="turn off|turn it off|switch off|off",
   c="Turn the stovetop off and take the pot of tomato sauce off it, then take the frying pan off the stovetop and take the medium pot off the stovetop.",
   cp=["Turn the stovetop off and take the pot of tomato sauce off it.",
       "Take the frying pan off the stovetop.",
       "Take the medium pot off the stovetop."], ci=0, cintent="turn off|stovetop off|off"),

 dict(sub="sequential", sc=3, why="letting the dough rest between mixing and rolling",
   a="Mix the cookie dough in the large mixing bowl and then roll it out with the rolling pin.",
   ap=["Mix the cookie dough in the large mixing bowl.",
       "Roll it out with the rolling pin."], ai=0, intent="rest|chill|refrigerate|fridge",
   c="Let the cookie dough rest and then roll it out with the rolling pin, then line the nonstick baking sheet with parchment paper and line the rusty baking sheet with parchment paper.",
   cp=["Let the cookie dough rest and then roll it out with the rolling pin.",
       "Line the nonstick baking sheet with parchment paper.",
       "Line the rusty baking sheet with parchment paper."], ci=0, cintent="rest"),

 dict(sub="sequential", sc=4, why="stirring the sauce between two additions",
   a="Add the canned tomatoes to the pot of tomato sauce and then add the mozzarella.",
   ap=["Add the canned tomatoes to the pot of tomato sauce.",
       "Add the mozzarella."], ai=0, intent="stir",
   c="Add the canned tomatoes to the pot of tomato sauce and stir it, then add the salt to the pot and add the chili flakes to the pot.",
   cp=["Add the canned tomatoes to the pot of tomato sauce and stir it.",
       "Add the salt to the pot.",
       "Add the chili flakes to the pot."], ci=0, cintent="stir"),

 dict(sub="sequential", sc=5, why="taking the tea bag out between brewing and sweetening",
   a="Brew the chamomile tea in the red mug with water from the electric kettle and then stir in the jar of honey.",
   ap=["Brew the chamomile tea in the red mug with water from the electric kettle.",
       "Stir in the jar of honey."], ai=0, intent="take out|remove|tea bag out|lift out",
   c="Take the chamomile tea bag out of the red mug and stir in the honey, then add the mint leaves to the mug and add a slice of the lemon to the mug.",
   cp=["Take the chamomile tea bag out of the red mug and stir in the honey.",
       "Add the mint leaves to the red mug.",
       "Add a slice of the lemon to the red mug."], ci=0, cintent="take out|tea bag|out"),

 dict(sub="sequential", sc=8, why="putting the lid back on the first tub before the second is opened",
   a="Scoop the chocolate ice cream into the glass bowl and then scoop the strawberry ice cream into it.",
   ap=["Scoop the chocolate ice cream into the glass bowl.",
       "Scoop the strawberry ice cream into the glass bowl."], ai=0, intent="lid|close|put the lid",
   c="Put the lid back on the tub of chocolate ice cream and scoop the strawberry ice cream into the glass bowl, then put the brownies on the ceramic plate and put the pie on the glass plate.",
   cp=["Put the lid back on the tub of chocolate ice cream and scoop the strawberry ice cream into the glass bowl.",
       "Put the brownies on the ceramic plate.",
       "Put the pie on the glass plate."], ci=0, cintent="lid"),

 dict(sub="sequential", sc=10, why="sealing the first sandwich bag before the next item goes in",
   a="Put the cheese sticks in a sandwich bag and then put the crackers in a sandwich bag.",
   ap=["Put the cheese sticks in a sandwich bag.",
       "Put the crackers in a sandwich bag."], ai=0, intent="seal|close|zip|shut",
   c="Seal the sandwich bag of cheese sticks and put the crackers in another sandwich bag, then put the carrots in a snack bag and put the grapes in a snack bag.",
   cp=["Seal the sandwich bag of cheese sticks and put the crackers in another sandwich bag.",
       "Put the carrots in a snack bag.",
       "Put the grapes in a snack bag."], ci=0, cintent="seal|sealed"),

 dict(sub="sequential", sc=9, why="labelling the first container before the next batch is packed",
   a="Pack the raw ground beef into a freezer bag and then pack the raw chicken breasts into a freezer bag.",
   ap=["Pack the raw ground beef into a freezer bag.",
       "Pack the raw chicken breasts into a freezer bag."], ai=0, intent="label|marker|write",
   c="Label the freezer bag of raw ground beef with the marker and pack the raw chicken breasts into another freezer bag, then put the frozen peas in the freezer and put the ice cream in the freezer.",
   cp=["Label the freezer bag of raw ground beef with the marker and pack the raw chicken breasts into another freezer bag.",
       "Put the frozen peas in the freezer.",
       "Put the ice cream in the freezer."], ci=0, cintent="label|marker"),

 dict(sub="sequential", sc=6, why="spinning the leaves dry between washing and dressing",
   a="Wash the spinach in the sink and then dress it with the Caesar dressing in the large salad bowl.",
   ap=["Wash the spinach in the sink.",
       "Dress it with the Caesar dressing in the large salad bowl."], ai=0,
   intent="spin|salad spinner|dry",
   c="Spin the washed spinach dry in the salad spinner and dress it with the Caesar dressing, then scatter the croutons over it and crumble the feta cheese over it.",
   cp=["Spin the washed spinach dry in the salad spinner and dress it with the Caesar dressing.",
       "Scatter the croutons over the spinach.",
       "Crumble the feta cheese over the spinach."], ci=0, cintent="spin|salad spinner"),

 # ---------------- PRECONDITIONAL ----------------
 dict(sub="preconditional", sc=3, why="letting the butter soften before it is creamed",
   a="Cream the unsalted butter with the white sugar in the large mixing bowl using the stand mixer.",
   ap=["Take the unsalted butter.",
       "Cream it with the white sugar in the large mixing bowl using the stand mixer."],
   ai=0, intent="soften|room temperature|soft",
   c="Let the unsalted butter soften and cream it with the white sugar in the large mixing bowl, then measure the all-purpose flour with the measuring cups and measure the baking soda with the measuring spoons.",
   cp=["Let the unsalted butter soften and cream it with the white sugar in the large mixing bowl.",
       "Measure the all-purpose flour with the measuring cups.",
       "Measure the baking soda with the measuring spoons."], ci=0, cintent="soften|soft"),

 dict(sub="preconditional", sc=4, why="taking the pan off the heat before the garlic goes in",
   a="Add the garlic to the frying pan of browned ground beef and stir it through.",
   ap=["Add the garlic to the frying pan of browned ground beef.",
       "Stir it through."], ai=0, intent="off the heat|off the stovetop|remove from the heat|take it off",
   c="Take the frying pan off the heat and add the garlic to it, then add the black pepper to the pan and add the chili flakes to the pan.",
   cp=["Take the frying pan off the heat and add the garlic to it.",
       "Add the black pepper to the pan.",
       "Add the chili flakes to the pan."], ci=0, cintent="off the heat|off the"),

 dict(sub="preconditional", sc=9, why="thawing the chicken before it is cooked",
   a="Cook the raw chicken breasts from the freezer and put them on the metal bowl to rest.",
   ap=["Take the raw chicken breasts from the freezer.",
       "Cook them.", "Put them on the metal bowl to rest."], ai=0,
   intent="thaw|defrost|let it thaw",
   c="Thaw the raw chicken breasts from the freezer and cook them, then put the frozen peas in the glass bowl and put the rice with the green label in the wooden bowl.",
   cp=["Thaw the raw chicken breasts from the freezer and cook them.",
       "Put the frozen peas in the glass bowl.",
       "Put the bag of rice with the green label in the wooden bowl."], ci=0,
   cintent="thaw|defrost"),

 dict(sub="preconditional", sc=7, why="emptying the sink before the washing up starts",
   a="Wash the dirty saucepan in the sink and stand it on the counter to dry.",
   ap=["Wash the dirty saucepan in the sink.",
       "Stand it on the counter to dry."], ai=0, intent="empty|drain|clear",
   c="Empty the sink and wash the dirty saucepan in it, then wash the dirty cutting board and wash the dirty knife.",
   cp=["Empty the sink and wash the dirty saucepan in it.",
       "Wash the dirty cutting board.",
       "Wash the dirty knife."], ci=0, cintent="empty|drain"),

 # NOTE: this cell was a "take the lid off before microwaving" item on scene 1. Its instruction
 # came out word for word identical to the calibration item amb_P03, which wants a low microwave
 # power for the same soup. Same sentence, two different ground truths, and across the
 # test/calibration boundary, so it was replaced with a preheating item on a different scene.
 dict(sub="preconditional", sc=3, why="preheating the oven before the tray goes in",
   a="Put the nonstick baking sheet of cookie dough in the oven and set the timer.",
   ap=["Put the nonstick baking sheet of cookie dough in the oven.",
       "Set the timer."], ai=0, intent="preheat|heat the oven|up to temperature",
   c="Preheat the oven and put the nonstick baking sheet of cookie dough in it, then set the timer and put the oven mitts on the counter.",
   cp=["Preheat the oven and put the nonstick baking sheet of cookie dough in it.",
       "Set the timer.", "Put the oven mitts on the counter."], ci=0, cintent="preheat"),

 dict(sub="preconditional", sc=5, why="peeling the orange before it goes in the blender",
   a="Blend three oranges with the whole milk in the blender and pour it into the tall glass.",
   ap=["Put three oranges and the whole milk in the blender.",
       "Blend them.", "Pour it into the tall glass."], ai=0, intent="peel",
   c="Peel the three oranges and blend them with the whole milk, then put the strawberries in the blender and put the banana in the blender.",
   cp=["Peel the three oranges and blend them with the whole milk.",
       "Put the strawberries in the blender.",
       "Put the banana in the blender."], ci=0, cintent="peel"),

 dict(sub="preconditional", sc=2, why="unwrapping the sandwich before it goes on the plate",
   a="Put the wrapped sandwich from the counter on the blue plate and take it to the kitchen table.",
   ap=["Put the wrapped sandwich from the counter on the blue plate.",
       "Take it to the kitchen table."], ai=0, intent="unwrap|take the wrapping|open",
   c="Unwrap the sandwich from the counter and put it on the blue plate, then put the bowl of chips on the white plate and put the bowl of grapes on the paper plate.",
   cp=["Unwrap the sandwich from the counter and put it on the blue plate.",
       "Put the bowl of chips on the white plate.",
       "Put the bowl of grapes on the paper plate."], ci=0, cintent="unwrap"),

 dict(sub="preconditional", sc=8, why="letting the cake cool before it is cut",
   a="Cut the cake with the cake knife and put two slices on the ceramic plate.",
   ap=["Cut the cake with the cake knife.",
       "Put two slices on the ceramic plate."], ai=0, intent="cool|let it cool",
   c="Let the cake cool and cut it with the cake knife, then put the brownies on the glass plate and put the pie on the paper plate.",
   cp=["Let the cake cool and cut it with the cake knife.",
       "Put the brownies on the glass plate.",
       "Put the pie on the paper plate."], ci=0, cintent="cool"),

# NOTE: a ninth preconditional pair (emptying the thermos before refilling it) was written and
# then dropped. It would have made group 3 uneven at 17 sequential and 18 preconditional, and
# "empty a vessel before using it" already appears above as the empty-the-sink pair.
]
