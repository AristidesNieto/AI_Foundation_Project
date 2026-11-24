"""Cleaning rules for inspected_trees.csv. Owner: Caspar (step C8).

Written into the package by Aristides (with Claude) during review J1, 2026-11-24,
from Caspar's notebook version. See "Review notes" below for what changed and why.
This module never reads files.

Review notes for Caspar (what was wrong in the notebook version, and the fix):
1. The functions only existed in the notebook; this file still raised
   NotImplementedError, so predict.py could not use them. -> now here.
2. Crew B diameters are in mm in this file too (all 141 crew B rows > 100 "cm",
   crew median 333). Not detected in C7. -> clean_shared(), rule 1.
3. Missed impossible values: 1 diameter in mm in crew C (589), 1 height in dm (273 m),
   1 diameter of 2.8 cm. -> clean_shared(), rules 2, 3, 5.
4. height_m was filled with interpolate(method="linear"): that copies the heights
   of the rows above and below in the file, so the result depends on the row order
   and not on the tree. -> estimate_size.estimate_size() (log-log model from diameter).
5. aspect was replaced with a separate list; it now uses the shared ASPECT_MAP via
   clean_shared(), so all three files follow one rule.
6. The function changed the caller's DataFrame (no .copy()). -> works on a copy.
7. The C1 cell printed yes/no = 0.739 as "Ratio between healthy and infested".
   The sample share needed in Task 4 is infested / all = 255 / 600 = 0.425.
"""

import pandas as pd

from bark.clean_shared import clean_shared

# Spellings of the label, after strip + lower case. Train has only "yes" / "no";
# the others are accepted so a new file with another spelling does not break.
INFESTED_MAP = {
    "yes": 1, "y": 1, "true": 1, "1": 1, "ja": 1, "infested": 1,
    "no": 0, "n": 0, "false": 0, "0": 0, "nein": 0, "healthy": 0,
}


def clean_inspected(df: pd.DataFrame) -> pd.DataFrame:
    """Return a cleaned copy of the inspected-trees DataFrame.

    1. Shared rules (aspect, diameter and height units, placeholders): clean_shared().
    2. infested: mapped to 1 (infested) / 0 (healthy). An unknown spelling becomes NaN;
       such rows cannot be used to train the model and are dropped there, not here.
    Missing diameter / height are NOT estimated here; call estimate_size() afterwards.
    """
    out = clean_shared(df)
    labels = out["infested"].astype("string").str.strip().str.lower()
    # float, so an unknown label can stay NaN (an int column cannot hold NaN).
    out["infested"] = labels.map(INFESTED_MAP).astype("float")
    return out


def sample_share(cleaned: pd.DataFrame) -> float:
    """Share of infested trees in the inspected sample (Task 4 needs it)."""
    return float(cleaned["infested"].mean())
