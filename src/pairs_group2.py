"""GROUP 2 (merged PARAMETRIC + SPATIAL), 18 pairs.

PARAMETRIC: the instruction names an action on an appliance and leaves the SETTING open, with
one setting being the obvious default. A setting is not a scene object, so the scene text does
not list the alternatives. That is the point: the generator has nothing visible to vary, so it
should collapse onto the default harder than it does when a rival object is sitting in the room.
Every alternative is a nameable word rather than a number, because is_similar matches text.

SPATIAL: either the object named exists in three places and only the location distinguishes them
(the scene text lists all three), or the destination is left open with one obvious default.

Clear partner recipe, as in group 1: same scene, same task, the open slot named explicitly, then
two further PARALLEL actions over same-kind objects, scored at index 0.

Known blemish to avoid, found in group 1: four clear items there had the excluded alternative
reappear as a generated option (e.g. a clear item saying "whole wheat flour" was offered
"take the bag of all-purpose flour"). It did no harm, since the method still stayed silent on
all four, but here the clear partner names its choice in the scored step itself wherever the
phrasing allows, which gives the generator less room to reach for the alternative.

is_similar patterns are lowercase throughout: it lowercases the option text but not the pattern.
"""
PAIRS = [
 # ---------- PARAMETRIC: which setting ----------
 dict(sub="parametric", sc=7, why="which dishwasher cycle, normal is the default and intensive is wanted",
   a="Load the four dirty bowls into the dishwasher, add a dishwasher tablet, and start it.",
   ap=["Load the four dirty bowls into the dishwasher.", "Add a dishwasher tablet.",
       "Start the dishwasher."], ai=2, intent="intensive",
   c="Start the dishwasher on the intensive cycle, then empty the recycling bin and empty the compost bin.",
   cp=["Start the dishwasher on the intensive cycle.", "Empty the recycling bin.",
       "Empty the compost bin."], ci=0, cintent="intensive"),

 dict(sub="parametric", sc=4, why="which heat, medium is the default for a sauce and low is wanted",
   a="Stir the canned tomatoes into the pot of tomato sauce on the stovetop and simmer it.",
   ap=["Stir the canned tomatoes into the pot of tomato sauce.", "Simmer it on the stovetop."],
   ai=1, intent="low",
   c="Simmer the pot of tomato sauce on low heat, then grate the parmesan and chop the garlic.",
   cp=["Simmer the pot of tomato sauce on low heat.", "Grate the parmesan.",
       "Chop the garlic."], ci=0, cintent="low"),

 dict(sub="parametric", sc=1, why="how dark the toast, golden is the default and light is wanted",
   a="Toast two slices of the white bread in the toaster, then spread the butter on them.",
   ap=["Toast two slices of the white bread in the toaster.", "Spread the butter on them."],
   ai=0, intent="light",
   c="Toast two slices of the white bread lightly in the toaster, then spread the strawberry jam on them and pour a glass of water.",
   cp=["Toast two slices of the white bread lightly in the toaster.",
       "Spread the strawberry jam on them.", "Pour a glass of water."], ci=0, cintent="light"),

 dict(sub="parametric", sc=5, why="how hot the water, boiling is the default and cooler is wanted for green tea",
   a="Heat the water in the electric kettle and brew the green tea in the blue mug.",
   ap=["Heat the water in the electric kettle.", "Brew the green tea in the blue mug."],
   ai=0, intent="cooler|off the boil|not boiling|below boiling",
   c="Heat the water in the electric kettle to just below boiling, then take the green tea bags from the cupboard and take the blue mug from the cupboard.",
   cp=["Heat the water in the electric kettle to just below boiling.",
       "Take the green tea bags from the cupboard.",
       "Take the blue mug from the cupboard."], ci=0, cintent="below boiling|just below"),

 # NOTE: this cell was originally a coffee-grind-coarseness item, but its instruction came out
 # word for word identical to the existing preconditional item amb_C09, which wants the water
 # boiled first. Same sentence, two different ground truths, so it was replaced.
 dict(sub="parametric", sc=3, why="which oven heat, a hot oven is the default and a low heat is wanted",
   a="Put the cookie dough on the nonstick baking sheet and bake it in the oven.",
   ap=["Put the cookie dough on the nonstick baking sheet.", "Bake it in the oven."],
   ai=1, intent="low heat|low|cooler|gentle",
   c="Bake the cookie dough on the nonstick baking sheet in the oven on a low heat, then set the timer and put the oven mitts on the counter.",
   cp=["Bake the cookie dough on the nonstick baking sheet in the oven on a low heat.",
       "Set the timer.", "Put the oven mitts on the counter."], ci=0, cintent="low heat|low"),

 dict(sub="parametric", sc=5, why="which blender speed, high is the default and pulsing is wanted",
   a="Put the strawberries and the whole milk in the blender and blend them.",
   ap=["Put the strawberries and the whole milk in the blender.", "Blend them."],
   ai=1, intent="pulse|pulsing|low",
   c="Blend the strawberries and the whole milk on low, then pour it into the tall glass and add a straw.",
   cp=["Blend the strawberries and the whole milk on low.", "Pour it into the tall glass.",
       "Add a straw."], ci=0, cintent="low"),

 dict(sub="parametric", sc=8, why="which microwave power, full power is the default and defrost is wanted",
   a="Soften the tub of chocolate ice cream in the microwave, then scoop it into the glass bowl.",
   ap=["Soften the tub of chocolate ice cream in the microwave.",
       "Scoop it into the glass bowl."], ai=0, intent="defrost|low power|low",
   c="Soften the tub of chocolate ice cream in the microwave on the defrost setting, then take the ice cream scoop from the cupboard and put the sprinkles on the counter.",
   cp=["Soften the tub of chocolate ice cream in the microwave on the defrost setting.",
       "Take the ice cream scoop from the cupboard.", "Put the sprinkles on the counter."],
   ci=0, cintent="defrost"),

 dict(sub="parametric", sc=4, why="which oven mode, baking is the default and the grill is wanted to brown the top",
   a="Spread the mozzarella over the penne in the frying pan and put it in the oven to brown the top.",
   ap=["Spread the mozzarella over the penne in the frying pan.",
       "Put it in the oven to brown the top."], ai=1, intent="grill|broil|broiler",
   c="Put the frying pan of penne under the oven grill to brown the top, then grate more parmesan and chop the mushrooms.",
   cp=["Put the frying pan of penne under the oven grill to brown the top.",
       "Grate more parmesan.", "Chop the mushrooms."], ci=0, cintent="grill|broil|broiler"),

 dict(sub="parametric", sc=7, why="which tap temperature, hot is the default for washing up and cold is wanted",
   a="Rinse the dirty cutting board under the tap and stand it by the sink to dry.",
   ap=["Rinse the dirty cutting board under the tap.", "Stand it by the sink to dry."],
   ai=0, intent="cold",
   c="Rinse the dirty cutting board under the cold tap, then rinse the dirty knife and rinse the wooden spoon.",
   cp=["Rinse the dirty cutting board under the cold tap.", "Rinse the dirty knife.",
       "Rinse the wooden spoon."], ci=0, cintent="cold"),

 # ---------- SPATIAL: which place, or which destination ----------
 dict(sub="spatial", sc=1, why="which jar of honey, three stand in the cupboard, on the table and on the counter",
   a="Bring me the jar of honey and put it on the kitchen table with a spoon.",
   ap=["Bring me the jar of honey.", "Put it on the kitchen table with a spoon."],
   ai=0, intent="cupboard",
   c="Bring the jar of honey from the cupboard, then bring the peanut butter and bring the strawberry jam.",
   cp=["Bring the jar of honey from the cupboard.", "Bring the peanut butter.",
       "Bring the strawberry jam."], ci=0, cintent="cupboard"),

 dict(sub="spatial", sc=3, why="which bag of white sugar, three stand on the counter, in the cupboard and in the fridge",
   a="Take the bag of white sugar and beat two spoonfuls of it into the cookie dough.",
   ap=["Take the bag of white sugar.", "Beat two spoonfuls of it into the cookie dough."],
   ai=0, intent="fridge|top shelf",
   c="Take the bag of white sugar from the fridge, then take the baking soda from the cupboard and take the cinnamon from the cupboard.",
   cp=["Take the bag of white sugar from the fridge.", "Take the baking soda from the cupboard.",
       "Take the cinnamon from the cupboard."], ci=0, cintent="fridge"),

 dict(sub="spatial", sc=5, why="which carton of oat milk, three stand on the counter, in the fridge and in the cupboard",
   a="Pour the oat milk into the tall glass and stir in the jar of honey.",
   ap=["Pour the oat milk into the tall glass.", "Stir in the jar of honey."],
   ai=0, intent="cupboard",
   c="Pour the oat milk from the cupboard into the tall glass, then pour the orange juice into a short glass and pour the apple juice into the other short glass.",
   cp=["Pour the oat milk from the cupboard into the tall glass.",
       "Pour the orange juice into a short glass.",
       "Pour the apple juice into the other short glass."], ci=0, cintent="cupboard"),

 dict(sub="spatial", sc=6, why="which bottle of ranch dressing, three stand on the counter, in the fridge and in the cupboard",
   a="Pour the ranch dressing over the mixed salad in the large salad bowl and toss it with the tongs.",
   ap=["Pour the ranch dressing over the mixed salad in the large salad bowl.",
       "Toss it with the tongs."], ai=0, intent="fridge",
   c="Pour the ranch dressing from the fridge over the mixed salad, then scatter the croutons and crumble the feta cheese over it.",
   cp=["Pour the ranch dressing from the fridge over the mixed salad.",
       "Scatter the croutons over the salad.",
       "Crumble the feta cheese over the salad."], ci=0, cintent="fridge"),

 dict(sub="spatial", sc=7, why="which dirty mug, three stand on the counter, on the table and in the sink",
   a="Wash the dirty mug with the sponge and put it in the cupboard.",
   ap=["Wash the dirty mug with the sponge.", "Put it in the cupboard."],
   ai=0, intent="kitchen table|table",
   c="Wash the dirty mug from the kitchen table with the sponge, then wash the dirty saucepan and wash the dirty knife.",
   cp=["Wash the dirty mug from the kitchen table with the sponge.", "Wash the dirty saucepan.",
       "Wash the dirty knife."], ci=0, cintent="kitchen table|table"),

 dict(sub="spatial", sc=8, why="which tub of vanilla ice cream, three sit in the top drawer, the bottom drawer and the door",
   a="Take the tub of vanilla ice cream and scoop two scoops into the glass bowl.",
   ap=["Take the tub of vanilla ice cream.", "Scoop two scoops into the glass bowl."],
   ai=0, intent="bottom",
   c="Take the tub of vanilla ice cream from the bottom freezer drawer, then take the chocolate sauce from the cupboard and take four spoons from the cupboard.",
   cp=["Take the tub of vanilla ice cream from the bottom freezer drawer.",
       "Take the chocolate sauce from the cupboard.", "Take four spoons from the cupboard."],
   ci=0, cintent="bottom"),

 dict(sub="spatial", sc=9, why="which shopping bag, three stand on the table, on the counter and on the floor",
   a="Unpack the shopping bag and put the carton of milk and the butter in the fridge.",
   ap=["Unpack the shopping bag.", "Put the carton of milk in the fridge.",
       "Put the butter in the fridge."], ai=0, intent="floor",
   c="Unpack the shopping bag on the floor, then unpack the shopping bag on the counter and unpack the shopping bag on the kitchen table.",
   cp=["Unpack the shopping bag on the floor.", "Unpack the shopping bag on the counter.",
       "Unpack the shopping bag on the kitchen table."], ci=0, cintent="floor"),

 dict(sub="spatial", sc=9, why="where the raw ground beef goes, the fridge is the default and the freezer is wanted",
   a="Put the raw ground beef away, then put the carton of milk and the butter in the fridge.",
   ap=["Put the raw ground beef away.", "Put the carton of milk in the fridge.",
       "Put the butter in the fridge."], ai=0, intent="freezer",
   c="Put the raw ground beef in the freezer, then put the frozen peas in the freezer and put the ice cream in the freezer.",
   cp=["Put the raw ground beef in the freezer.", "Put the frozen peas in the freezer.",
       "Put the ice cream in the freezer."], ci=0, cintent="freezer"),

 dict(sub="spatial", sc=9, why="where the apples go, the fridge is the default and the pantry cupboard is wanted",
   a="Put the apples away, then put the potatoes and the onions in the pantry cupboard.",
   ap=["Put the apples away.", "Put the potatoes in the pantry cupboard.",
       "Put the onions in the pantry cupboard."], ai=0, intent="pantry|cupboard",
   c="Put the apples in the pantry cupboard, then put the potatoes and the onions in the pantry cupboard too.",
   cp=["Put the apples in the pantry cupboard.", "Put the potatoes in the pantry cupboard.",
       "Put the onions in the pantry cupboard."], ci=0, cintent="pantry|cupboard"),
]
