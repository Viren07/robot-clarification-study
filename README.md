# robot-clarification-study

This project investigates how LLM based robot task planners fail on ambiguous natural language instructions. We build a labeled dataset of 100 instructions across four ambiguity categories, systematically evaluate a GPT-4o based planner on all categories, and test a lightweight confidence based clarification intervention. The goal is to characterize failure modes by ambiguity type and evaluate whether simple prompt based confidence estimation can reduce silent failures without calibration data or knowledge bases.
Related work: KNOWNO (Ren et al. 2023), Introspective Planning (Liang et al. 2024)
Status: Literature review complete. Dataset construction and baseline implementation in progress.
