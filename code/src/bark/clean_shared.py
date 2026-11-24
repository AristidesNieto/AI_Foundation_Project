"""Cleaning rules for columns shared by all three files. Owner: Aristides (step S2).

Shared rules must behave identically for felled, inspected and district files,
so every file goes through clean_shared() first.
This module never reads files: it only transforms the DataFrame it receives.

All rules are idempotent: running clean_shared() twice gives the same result as
running it once (after the first pass no value is outside the plausible ranges).
"""

import numpy as np
import pandas as pd

# Every spelling found in the data (step A3), mapped to the four aspect codes.
# The keys are already upper case and stripped of spaces, see clean_aspect().
ASPECT_MAP = {
    "N": "N",
    "NORTH": "N",
    "E": "E",
    "EAST": "E",
    "S": "S",
    "SOUTH": "S",
    "SÜD": "S",  # German for south, found in the data
    "SUD": "S",  # same word without the umlaut
    "W": "W",
    "WEST": "W",
}

# Plausible ranges for a spruce in this district (evidence: train/, all three files).
# Real values after the unit fixes: diameter 12.4-79.7 cm, height 12.5-51.8 m.
# Bad values: diameters 124-6630 (mm), heights 179-373 (dm), heights 1.7-4.0 m, diameters 1.6-3.8 cm.
MIN_PLAUSIBLE_DIAMETER_CM = 5.0
MAX_PLAUSIBLE_DIAMETER_CM = 100.0
MIN_PLAUSIBLE_HEIGHT_M = 5.0
MAX_PLAUSIBLE_HEIGHT_M = 60.0


def clean_aspect(df: pd.DataFrame) -> pd.DataFrame:
    """Map every spelling of aspect to N, E, S or W. Unknown spellings become NaN."""
    out = df.copy()
    # .str.strip() removes leading/trailing spaces, .str.upper() makes "South" and "s" both "SOUTH" / "S".
    normalised = out["aspect"].astype("string").str.strip().str.upper()
    # .map(dict) replaces each value with its dictionary entry; unknown values become NaN.
    out["aspect"] = normalised.map(ASPECT_MAP)
    return out


def clean_measurements(df: pd.DataFrame) -> pd.DataFrame:
    """Repair diameter_cm and height_m. Missing values are NOT estimated here.

    Rules, in this order:
    1. A crew whose median diameter is above MAX_PLAUSIBLE_DIAMETER_CM measured in mm:
       divide all its diameters by 10. (In train/ this is crew B in all three files.)
    2. A single diameter above MAX_PLAUSIBLE_DIAMETER_CM is also in mm: divide by 10.
       Evidence: 1 row in inspected, 9 in district (crews A, C, D); after /10 their
       height/diameter ratio lies inside the range of the felled trees (0.6-1.3).
    3. A height above MAX_PLAUSIBLE_HEIGHT_M is in decimetres: divide by 10.
       Evidence: 1 row in inspected, 10 in district; after /10 the ratio fits again.
    4. Height 0 is a placeholder for "not measured": NaN.
    5. Values still outside [MIN, MAX] are impossible: NaN (estimated later).
       This covers diameters below 5 cm and heights below 5 m.
    """
    out = df.copy()
    out["diameter_cm"] = pd.to_numeric(out["diameter_cm"], errors="coerce")
    out["height_m"] = pd.to_numeric(out["height_m"], errors="coerce")

    # Rule 1: whole crew in mm. Decided by the crew's median, not by its name,
    # so the rule also works if another crew uses mm in a new file.
    crew_median = out.groupby("crew")["diameter_cm"].transform("median")
    crew_in_mm = crew_median > MAX_PLAUSIBLE_DIAMETER_CM
    out.loc[crew_in_mm, "diameter_cm"] = out.loc[crew_in_mm, "diameter_cm"] / 10

    # Rule 2: single diameters in mm.
    too_big_d = out["diameter_cm"] > MAX_PLAUSIBLE_DIAMETER_CM
    out.loc[too_big_d, "diameter_cm"] = out.loc[too_big_d, "diameter_cm"] / 10

    # Rule 3: single heights in dm.
    too_big_h = out["height_m"] > MAX_PLAUSIBLE_HEIGHT_M
    out.loc[too_big_h, "height_m"] = out.loc[too_big_h, "height_m"] / 10

    # Rule 4: height 0 is a placeholder.
    out.loc[out["height_m"] == 0, "height_m"] = np.nan

    # Rule 5: whatever is still implausible becomes missing.
    bad_d = ~out["diameter_cm"].between(MIN_PLAUSIBLE_DIAMETER_CM, MAX_PLAUSIBLE_DIAMETER_CM)
    bad_h = ~out["height_m"].between(MIN_PLAUSIBLE_HEIGHT_M, MAX_PLAUSIBLE_HEIGHT_M)
    out.loc[bad_d, "diameter_cm"] = np.nan
    out.loc[bad_h, "height_m"] = np.nan

    return out


def clean_shared(df: pd.DataFrame) -> pd.DataFrame:
    """Return a cleaned copy of df with the shared columns repaired.

    1. aspect: see clean_aspect().
    2. diameter_cm, height_m: see clean_measurements().
    """
    return clean_measurements(clean_aspect(df))
