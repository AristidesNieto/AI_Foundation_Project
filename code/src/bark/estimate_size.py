"""Estimate missing diameter_cm / height_m for trees WITHOUT biomass (inspected, district).

Felled trees use clean_felled.estimate_missing(), which also uses biomass_kg.
Inspected and district trees have no biomass, so here each size is estimated
from the other one only, again as a linear model on the logarithms:
    log(height)   = a + b * log(diameter)
    log(diameter) = c + d * log(height)
If a tree misses both, the train medians are used (best estimate, handout Task 1).

Fit on train/ only (all three cleaned files, rows with both values observed),
save with models_io, and reuse the saved models in predict.py.
This module never reads files.
"""

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression


def fit_size_estimators(cleaned_frames: list[pd.DataFrame]) -> dict:
    """Fit the two one-variable log-log models and store the medians.

    cleaned_frames: DataFrames already passed through clean_shared().
    """
    both = pd.concat([f[["diameter_cm", "height_m"]] for f in cleaned_frames], ignore_index=True)
    complete = both.dropna()
    log_d = np.log(complete[["diameter_cm"]].values)
    log_h = np.log(complete[["height_m"]].values)
    return {
        "height_from_diameter": LinearRegression().fit(log_d, log_h.ravel()),
        "diameter_from_height": LinearRegression().fit(log_h, log_d.ravel()),
        "median_diameter_cm": float(complete["diameter_cm"].median()),
        "median_height_m": float(complete["height_m"].median()),
    }


def estimate_size(cleaned: pd.DataFrame, models: dict) -> pd.DataFrame:
    """Fill missing diameter_cm and height_m. Returns a copy with no NaN in both columns."""
    out = cleaned.copy()
    d_missing = out["diameter_cm"].isna()
    h_missing = out["height_m"].isna()
    both = d_missing & h_missing

    # Both missing: nothing to estimate from, use the train medians.
    out.loc[both, "diameter_cm"] = models["median_diameter_cm"]
    out.loc[both, "height_m"] = models["median_height_m"]

    # Only diameter missing: estimate it from the observed height.
    only_d = d_missing & ~both
    if only_d.any():
        x = np.log(out.loc[only_d, ["height_m"]].values)
        out.loc[only_d, "diameter_cm"] = np.exp(models["diameter_from_height"].predict(x))

    # Only height missing: estimate it from the observed (or repaired) diameter.
    only_h = h_missing & ~both
    if only_h.any():
        x = np.log(out.loc[only_h, ["diameter_cm"]].values)
        out.loc[only_h, "height_m"] = np.exp(models["height_from_diameter"].predict(x))

    return out
