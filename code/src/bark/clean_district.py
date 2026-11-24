"""Cleaning rules for district_trees.csv. Owner: Caspar (step C8).

Written into the package by Aristides (with Claude) during review J1, 2026-11-24,
from Caspar's notebook version. See "Review notes" below for what changed and why.
This module never reads files.

Review notes for Caspar (what was wrong in the notebook version, and the fix):
1. The functions only existed in the notebook; this file still raised
   NotImplementedError. -> now here.
2. Crew B diameters are in mm (all 924 crew B rows > 100 "cm", crew median 308).
   -> clean_shared(), rule 1.
3. Missed impossible values (each checked: after the fix the height/diameter ratio
   matches the felled trees):
   - 9 diameters in mm in crews A, C, D (174-465)       -> clean_shared(), rule 2
   - 10 heights in dm (179-373 m)                        -> clean_shared(), rule 3
   - 9 heights of 1.7-4.0 m on trees of 18-66 cm         -> rule 5, then estimated
   - 2 diameters of 3.0 and 3.8 cm                        -> rule 5, then estimated
4. height_m was filled with interpolate(method="linear") (row-order dependent).
   -> estimate_size.estimate_size().
5. bore_dust NaN was replaced by the string "missing". The handout defines empty as
   "not checked"; it is kept as NaN so Task 4 can test isna() (p = p_prior) and
   Task 5 can pick check candidates from it.
6. aspect replaced with a separate list; the function changed the caller's DataFrame.
   -> clean_shared(), works on a copy.
"""

import pandas as pd

from bark.clean_shared import clean_shared

# Spellings of the bore-dust result, after strip + lower case. Train has only
# "found" / "not found" / empty; the others are accepted for robustness.
BORE_DUST_MAP = {
    "found": "found", "yes": "found", "dust found": "found",
    "not found": "not found", "notfound": "not found", "not_found": "not found",
    "no": "not found", "no dust": "not found", "none": "not found",
}


def clean_district(df: pd.DataFrame) -> pd.DataFrame:
    """Return a cleaned copy of the district-trees DataFrame.

    1. Shared rules (aspect, diameter and height units, placeholders): clean_shared().
    2. bore_dust: "found" / "not found", or NaN = not checked. Unknown spellings
       become NaN, i.e. the tree is treated as not checked (no Bayes update).
    Missing diameter / height are NOT estimated here; call estimate_size() afterwards.
    """
    out = clean_shared(df)
    labels = out["bore_dust"].astype("string").str.strip().str.lower()
    out["bore_dust"] = labels.map(BORE_DUST_MAP).astype(object)
    out.loc[out["bore_dust"].isna(), "bore_dust"] = None
    return out
