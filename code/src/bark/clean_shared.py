"""Cleaning rules for columns shared by all three files. Owner: Aristides (step S2)."""

import pandas as pd


def clean_shared(df: pd.DataFrame) -> pd.DataFrame:
    """Return a cleaned copy of df with the shared columns repaired.

    TODO (S2): normalise aspect, crew and survey_batch; handle placeholders
    and impossible values found in EDA (A6, C7). Must not read files.
    """
    raise NotImplementedError("S2 not written yet")
