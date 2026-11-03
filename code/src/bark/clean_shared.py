"""Cleaning rules for columns shared by all three files. Owner: Aristides (step S2).

Shared rules must behave identically for felled, inspected and district files,
so every file goes through clean_shared() first.
This module never reads files: it only transforms the DataFrame it receives.
"""

import pandas as pd

# Every spelling found in the data (step A3), mapped to the four aspect codes.
# The keys are already upper case and stripped of spaces, see clean_shared().
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


def clean_shared(df: pd.DataFrame) -> pd.DataFrame:
    """Return a cleaned copy of df with the shared columns repaired.

    Rules:
    1. aspect: remove spaces, use upper case, then map every known spelling
       to N, E, S or W. A spelling not in ASPECT_MAP becomes NaN (missing).
    """
    # Work on a copy, so the caller's DataFrame is never changed.
    out = df.copy()

    # .str.strip() removes leading/trailing spaces, .str.upper() makes "South" and "s" both "SOUTH" / "S".
    normalised = out["aspect"].astype("string").str.strip().str.upper()

    # .map(dict) replaces each value with its dictionary entry; unknown values become NaN.
    out["aspect"] = normalised.map(ASPECT_MAP)

    return out
