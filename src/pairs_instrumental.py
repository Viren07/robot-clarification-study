"""INSTRUMENTAL pairs: the instrumental slice of merged group1.

Test pairs come from pairs_group1.py, calibration pairs from pairs_group1_calib.py.
Each pair carries a `sub` tag, and calibration pairs carry calib=True, so
build_paired.py can split test from calibration while rule 2 is checked per group.
"""
from pairs_group1 import PAIRS as _TEST
from pairs_group1_calib import PAIRS as _CALIB

PAIRS = [p for p in _TEST + _CALIB if p["sub"] == "instrumental"]

# Expansion to 34 pairs per group; families chosen to not repeat the ones above.
from pairs_group1_more import PAIRS as _MORE
PAIRS = PAIRS + [p for p in _MORE if p["sub"] == "instrumental"]
