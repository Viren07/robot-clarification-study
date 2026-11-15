"""GROUP 1 CALIBRATION: 9 pairs, same recipes as the group 1 test pairs, no items shared.

Conformal prediction needs the calibration set drawn from the same distribution as the test
set. These follow the identical construction: the instruction names a thing generically, the
scene supplies a dominant default, the user wants the marked alternative; and the clear partner
names the choice explicitly then adds two parallel actions over same-kind objects, scored at
index 0.

Three ambiguous halves are the batch-3/4 items left out of the test set, so they are already
screened. The other six are new. Every pair carries calib=True, which is what keeps it out of
the test half in build_paired.py.

is_similar patterns are lowercase: it lowercases the option text but not the pattern. That is
why "caesar" below is not capitalised.
"""
PAIRS = [
 # --- the three valid batch-3/4 ambiguous items the test set did not use ---
 dict(calib=True, sub="referential", sc=2, why="which cheese, cheddar is the default and swiss is wanted",
   a="Make a sandwich: put two slices of white bread on the cutting board, lay the sliced ham on one slice, add some cheese and lettuce, and close it.",
   ap=["Put two slices of white bread on the cutting board.", "Lay the sliced ham on one slice.",
       "Add some cheese.", "Add lettuce.", "Close the sandwich."], ai=2, intent="swiss",
   c="Lay the sliced Swiss cheese on the white bread, then add the lettuce and add the tomato.",
   cp=["Lay the sliced Swiss cheese on the white bread.", "Add the lettuce.",
       "Add the tomato."], ci=0, cintent="swiss"),

 dict(calib=True, sub="instrumental", sc=6, why="which serving vessel, the large salad bowl already holds the salad so it is canonical",
   a="Toss the mixed salad with the tongs, serve it, and grind black pepper over the top.",
   ap=["Toss the mixed salad with the tongs.", "Serve the salad.",
       "Grind black pepper over the top."], ai=1, intent="small bowl|small bowls",
   c="Serve the mixed salad into the two small bowls, then scatter the croutons and crumble the feta cheese over them.",
   cp=["Serve the mixed salad into the two small bowls.", "Scatter the croutons over them.",
       "Crumble the feta cheese over them."], ci=0, cintent="small bowl"),

 dict(calib=True, sub="referential", sc=5, why="which ice source, the ice bucket holds ice ready to use so it is canonical",
   a="Fill the tall glass with ice, pour the apple juice over it, and stir it once with the spoon.",
   ap=["Fill the tall glass with ice.", "Pour the apple juice over it.",
       "Stir it once with the spoon."], ai=0, intent="ice tray|tray",
   c="Fill the tall glass with ice from the ice tray, then pour in the apple juice and add a straw.",
   cp=["Fill the tall glass with ice from the ice tray.", "Pour in the apple juice.",
       "Add a straw."], ci=0, cintent="ice tray|tray"),

 # --- six new ones ---
 dict(calib=True, sub="referential", sc=2, why="which bread, white is the default and the rye is wanted",
   a="Make a turkey sandwich with two slices of the bread and put it in the lunch box.",
   ap=["Take two slices of the bread.", "Make a turkey sandwich with them.",
       "Put it in the lunch box."], ai=0, intent="rye",
   c="Take two slices of the rye bread, then take the sliced turkey from the fridge and take the head of lettuce from the fridge.",
   cp=["Take two slices of the rye bread.", "Take the sliced turkey from the fridge.",
       "Take the head of lettuce from the fridge."], ci=0, cintent="rye"),

 dict(calib=True, sub="referential", sc=2, why="which spread, mayonnaise is the default for a sandwich and the mustard is wanted",
   a="Spread the sauce on the white bread, lay the sliced ham on it, and close the sandwich.",
   ap=["Spread the sauce on the white bread.", "Lay the sliced ham on it.",
       "Close the sandwich."], ai=0, intent="mustard",
   c="Spread the mustard on the white bread, then lay the sliced ham on it and lay the sliced Swiss cheese on it.",
   cp=["Spread the mustard on the white bread.", "Lay the sliced ham on it.",
       "Lay the sliced Swiss cheese on it."], ci=0, cintent="mustard"),

 dict(calib=True, sub="referential", sc=6, why="which dressing, ranch is the default with three bottles in the scene and the caesar is wanted",
   a="Dress the mixed salad in the large salad bowl and toss it with the tongs.",
   ap=["Dress the mixed salad in the large salad bowl.", "Toss it with the tongs."],
   ai=0, intent="caesar",
   c="Dress the mixed salad with the Caesar dressing, then grind the pepper over it and scatter the croutons on it.",
   cp=["Dress the mixed salad with the Caesar dressing.", "Grind the pepper over it.",
       "Scatter the croutons on it."], ci=0, cintent="caesar"),

 dict(calib=True, sub="instrumental", sc=8, why="which bowl, the ceramic bowl is the default and the paper bowl is wanted",
   a="Put two brownies in a bowl and carry it to the kitchen table with a spoon.",
   ap=["Put two brownies in a bowl.", "Carry it to the kitchen table with a spoon."],
   ai=0, intent="paper",
   c="Put two brownies in the paper bowl, then put the whipped cream on them and put the sprinkles on them.",
   cp=["Put two brownies in the paper bowl.", "Put the whipped cream on them.",
       "Put the sprinkles on them."], ci=0, cintent="paper"),

 dict(calib=True, sub="instrumental", sc=9, why="which bowl, the glass bowl is the default and the wooden bowl is wanted",
   a="Put the apples in a bowl and leave it on the counter.",
   ap=["Put the apples in a bowl.", "Leave it on the counter."], ai=0, intent="wooden",
   c="Put the apples in the wooden bowl, then put the bananas in the wooden bowl and leave it on the counter.",
   cp=["Put the apples in the wooden bowl.", "Put the bananas in the wooden bowl.",
       "Leave the wooden bowl on the counter."], ci=0, cintent="wooden"),

 dict(calib=True, sub="referential", sc=10, why="which granola bar, the oat one is the default for a lunch and the chocolate one is wanted",
   a="Put a granola bar in the red lunch box with the crackers and the grapes.",
   ap=["Put a granola bar in the red lunch box.", "Put the crackers in the red lunch box.",
       "Put the grapes in the red lunch box."], ai=0, intent="chocolate",
   c="Put the chocolate granola bar in the red lunch box, then put the crackers and the grapes in it too.",
   cp=["Put the chocolate granola bar in the red lunch box.",
       "Put the crackers in the red lunch box.",
       "Put the grapes in the red lunch box."], ci=0, cintent="chocolate"),
]
