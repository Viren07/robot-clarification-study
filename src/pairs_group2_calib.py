"""GROUP 2 CALIBRATION: 9 pairs, same recipes as the group 2 test pairs, no items shared.

5 parametric and 4 spatial, matching the test half's 9/9 split as closely as 9 pairs allow.

The spatial pairs reuse the scenes whose three-of-a-kind the test half also uses (the honey
jars, the dirty mugs, the ice cream tubs), but pose a DIFFERENT task over them. That is what a
calibration set should be: same ambiguity, same scene, different instruction. No instruction
here appears in the test half.

Every pair carries calib=True, which keeps it out of the test half in build_paired.py.
is_similar patterns are lowercase.
"""
PAIRS = [
 # ---------- PARAMETRIC ----------
 dict(calib=True, sub="parametric", sc=7, why="which dishwasher cycle, normal is the default and the eco cycle is wanted",
   a="Load the dirty cutlery into the dishwasher, add a tablet, and start it.",
   ap=["Load the dirty cutlery into the dishwasher.", "Add a dishwasher tablet.",
       "Start the dishwasher."], ai=2, intent="eco",
   c="Start the dishwasher on the eco cycle, then wipe the counter with the spray cleaner and empty the trash can.",
   cp=["Start the dishwasher on the eco cycle.", "Wipe the counter with the spray cleaner.",
       "Empty the trash can."], ci=0, cintent="eco"),

 dict(calib=True, sub="parametric", sc=4, why="which heat, medium is the default and high is wanted to bring water to the boil",
   a="Fill the large pot with water and bring it to the boil on the stovetop.",
   ap=["Fill the large pot with water.", "Bring it to the boil on the stovetop."],
   ai=1, intent="high",
   c="Bring the large pot of water to the boil on high heat, then add the salt and add the box of penne.",
   cp=["Bring the large pot of water to the boil on high heat.", "Add the salt.",
       "Add the box of penne."], ci=0, cintent="high"),

 dict(calib=True, sub="parametric", sc=1, why="which microwave power, full power is the default and low is wanted for soup",
   a="Reheat the saucepan of leftover soup in the microwave and pour it into the red mug.",
   ap=["Reheat the leftover soup in the microwave.", "Pour it into the red mug."],
   ai=0, intent="low",
   c="Reheat the leftover soup in the microwave on low power, then pour it into the red mug and put a spoon beside it.",
   cp=["Reheat the leftover soup in the microwave on low power.", "Pour it into the red mug.",
       "Put a spoon beside it."], ci=0, cintent="low power|low"),

 dict(calib=True, sub="parametric", sc=8, why="which microwave setting, full power is the default and the popcorn setting is wanted",
   a="Pop the bag of microwave popcorn in the microwave and tip it into the plastic bowl.",
   ap=["Pop the bag of microwave popcorn in the microwave.",
       "Tip it into the plastic bowl."], ai=0, intent="popcorn setting|popcorn button|popcorn",
   c="Pop the bag of microwave popcorn on the popcorn setting, then tip it into the plastic bowl and put the napkins on the table.",
   cp=["Pop the bag of microwave popcorn on the popcorn setting.",
       "Tip it into the plastic bowl.", "Put the napkins on the table."],
   ci=0, cintent="popcorn setting|popcorn"),

 dict(calib=True, sub="parametric", sc=1, why="how dark the toast, golden is the default and well done is wanted",
   a="Toast two slices of the whole wheat bread in the toaster and spread the peanut butter on them.",
   ap=["Toast two slices of the whole wheat bread in the toaster.",
       "Spread the peanut butter on them."], ai=0, intent="dark|well done|well-done",
   c="Toast two slices of the whole wheat bread until dark in the toaster, then spread the peanut butter on them and pour a glass of water.",
   cp=["Toast two slices of the whole wheat bread until dark in the toaster.",
       "Spread the peanut butter on them.", "Pour a glass of water."], ci=0, cintent="dark"),

 # ---------- SPATIAL ----------
 dict(calib=True, sub="spatial", sc=1, why="which jar of honey, three stand in the cupboard, on the table and on the counter",
   a="Spread the honey on the sliced white bread and put it on a clean white plate.",
   ap=["Take the jar of honey.", "Spread the honey on the sliced white bread.",
       "Put it on a clean white plate."], ai=0, intent="counter",
   c="Take the jar of honey from the counter, then take the stick of butter from the fridge and take a clean white plate from the cupboard.",
   cp=["Take the jar of honey from the counter.", "Take the stick of butter from the fridge.",
       "Take a clean white plate from the cupboard."], ci=0, cintent="counter"),

 dict(calib=True, sub="spatial", sc=7, why="which dirty mug, three stand on the counter, on the table and in the sink",
   a="Put the dirty mug in the dishwasher and start the normal cycle.",
   ap=["Put the dirty mug in the dishwasher.", "Start the normal cycle."],
   ai=0, intent="sink",
   c="Put the dirty mug from the sink in the dishwasher, then put the dirty cutlery in the dishwasher and put the four dirty bowls in the dishwasher.",
   cp=["Put the dirty mug from the sink in the dishwasher.",
       "Put the dirty cutlery in the dishwasher.",
       "Put the four dirty bowls in the dishwasher."], ci=0, cintent="sink"),

 dict(calib=True, sub="spatial", sc=8, why="which tub of vanilla ice cream, three sit in the top drawer, the bottom drawer and the door",
   a="Put two scoops from the tub of vanilla ice cream into the ceramic bowl and pour the chocolate sauce over them.",
   ap=["Take the tub of vanilla ice cream.",
       "Put two scoops into the ceramic bowl.", "Pour the chocolate sauce over them."],
   ai=0, intent="freezer door|door",
   c="Take the tub of vanilla ice cream from the freezer door, then take the chocolate sauce from the cupboard and take the ice cream scoop from the cupboard.",
   cp=["Take the tub of vanilla ice cream from the freezer door.",
       "Take the chocolate sauce from the cupboard.",
       "Take the ice cream scoop from the cupboard."], ci=0, cintent="freezer door|door"),

 dict(calib=True, sub="spatial", sc=9, why="where the loaf of bread goes, the pantry cupboard is the default and the freezer is wanted",
   a="Put the loaf of bread away, then put the carton of eggs and the yogurt in the fridge.",
   ap=["Put the loaf of bread away.", "Put the carton of eggs in the fridge.",
       "Put the yogurt in the fridge."], ai=0, intent="freezer",
   c="Put the loaf of bread in the freezer, then put the frozen peas in the freezer and put the ice cream in the freezer.",
   cp=["Put the loaf of bread in the freezer.", "Put the frozen peas in the freezer.",
       "Put the ice cream in the freezer."], ci=0, cintent="freezer"),
]
