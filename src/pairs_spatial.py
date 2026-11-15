"""SPATIAL pairs: the spatial slice of merged group2.

Test pairs come from pairs_group2.py, calibration pairs from pairs_group2_calib.py.
Each pair carries a `sub` tag, and calibration pairs carry calib=True, so
build_paired.py can split test from calibration while rule 2 is checked per group.
"""
from pairs_group2 import PAIRS as _TEST
from pairs_group2_calib import PAIRS as _CALIB

PAIRS = [p for p in _TEST + _CALIB if p["sub"] == "spatial"]

# Expansion to 34 pairs per group; families chosen to not repeat the ones above.
from pairs_group2_more import PAIRS as _MORE
PAIRS = PAIRS + [p for p in _MORE if p["sub"] == "spatial"]
