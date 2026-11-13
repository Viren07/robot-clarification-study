# How to write an item that beats the baselines

Derived 2026-11-12 from 138 already-scored items, by reading the 43 that pass against the 95 that
do not. Nothing here changes any method; it describes what the published methods do, so items can
be written against their actual behaviour instead of by trial and error.

## The quantity that decides every item

KnowNo keeps every option scoring at or above `1 - qhat` (about 0.075 in our runs) and asks when
more than one survives. So the deciding number is the **runner-up probability**, never the top one.

    balanced accuracy = 1 - (false_alarm_rate + miss_rate) / 2

The two halves therefore have OPPOSITE targets:

| half | we want the method to | so we want |
|---|---|---|
| ambiguous | stay silent (a miss) | runner-up **below** 0.04 |
| clear | falsely ask (a false alarm) | runner-up **above** 0.15 |

Reference: AmbiK 36% false alarms + 54% misses = 0.90, giving 0.55 predicted against 0.53 measured.
To beat AmbiK the two rates must sum above about 0.90.

## Template A, ambiguous items: a strong default plus a non-default intent

Two conditions, both required. **16 of 19 winners satisfy both; only 5 of 50 losers do.**

1. **The generic term must have an overwhelming default in that scene.** The model will enumerate
   the variants either way; what matters is whether one of them takes nearly all the probability.
   Winners have a median top probability of **0.973**, losers **0.621**.
2. **The user's intent must be a non-default variant**, so the confident answer is wrong.

The clearest evidence is two items with the SAME scored step and opposite outcomes:

    WINNER  "Take two slices of bread."   A) white 0.925   B) whole wheat 0.034   -> SILENT
    LOSER   "Take two slices of bread."   D) white 0.504   B) rye      0.338      -> ASKS

    WINNER  "Take a knife."   D) chef's 0.948   C) paring 0.017   B) serrated 0.015  -> SILENT
    LOSER   "Take a bowl."    D) glass  0.465   B) metal  0.328   C) wooden   0.140  -> ASKS

Bread, knife and tea have a default. Bowl material, sauce flavour, lunch-box colour and granola-bar
flavour do not: the alternatives are symmetric, the model hedges, and the method catches it.

**Write:** a generic term whose scene variants are asymmetric (white vs whole wheat bread, chef's vs
serrated knife, black vs chamomile tea, whole vs almond milk, tap vs sparkling water, sponge vs
scrub brush), with the intent set to the marked alternative.

**Do not write:** a choice among symmetric variants (glass/metal/wooden bowl, red/blue/green lunch
box, caramel/chocolate sauce). Those are the losers, and they are most of own100's A1 to A3 items.

Pass rate by type: A6 42%, A4 40%, A5 33%, A1 17%, A3 17%, A2 10%.

## Template B, clear items: an underdetermined next action

A clear item earns its place by making the method ask when it should not. That happens when the
scored step is one of several interchangeable sub-actions, so the model is unsure which comes
**next**, even though every object in the step is named uniquely.

    unamb_v2_008  step: "Put the wrapped sandwich in the lunch box."
                  B) put the juice box in the lunch box   0.473
                  C) put the grapes in the lunch box      0.450     -> ASKS (false alarm)

    unamb_v2_050  step: "Take the ice pack."
                  B) open the fridge door and put the ice pack inside  0.500
                  A) leave the ice pack on the counter                 0.453  -> ASKS

The item is genuinely unambiguous: a human reads it and knows what to do. The method still asks.
That is the method's failure, not an item defect, and it is exactly what we want.

**Do not write** a step that restates the whole instruction. The model simply echoes it:

    unamb_b2_013  step: "Drizzle on caramel sauce."   B) drizzle on caramel sauce   0.984  -> SILENT

The batch 2 minimal-pair twins are all of this shape, median runner-up **0.0043**, and only 4 of 19
pass against own100's 20 of 50. They are a controlled sub-study, not the basis for the clear half.

## The transfer problem, which limits what this buys

Selecting on the runner-up is selecting on KnowNo's decision boundary. Measured on own100:

| | also missed by LofreeCP |
|---|---|
| the 11 KnowNo winners | 6/11 (55%) |
| the other 39 ambiguous | 19/39 (49%) |

**No transfer.** LofreeCP scores by sampling entropy, not token probability, so an item built to
slip past KnowNo does not slip past LofreeCP. Expect this template to lower KnowNo and LAP, which
share the probability signal, and to leave LofreeCP where it is. Binary and No Help are at the floor
on every dataset.

To move all five, each candidate has to clear BOTH screens: KnowNo's runner-up below 0.04 AND
LofreeCP's prediction set a singleton. That is one extra sampling call per item and it will cut the
yield again.

## Yield, and what it means for authoring

Blind hit rates over the 138 scored items: ambiguous 19/69 (28%), clear 24/69 (35%). To reach 50
and 50 from the 43 current keepers, 31 more ambiguous and 26 more clear are needed, which blind
costs roughly 111 + 74 = 185 items written. Writing to these templates should raise both rates;
screen every candidate before keeping it, and re-measure the hit rate after the first 20 so the
estimate is grounded rather than assumed.
