"""Cleaning rules and estimation for felled_trees.csv. Owner: Aristides (step A7).

Rules come from the evidence in step A6 and are recorded in CLAUDE.md, section 8.
This module never reads files: it only transforms the DataFrame it receives.
"""

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

# A diameter below this value is impossible for a spruce in this data (A6, finding 4).
MIN_PLAUSIBLE_DIAMETER_CM = 5.0


def clean_felled(df: pd.DataFrame) -> pd.DataFrame:
    """Apply the repair rules to felled_trees. Missing values are NOT estimated here.

    Rules, in this order:
    1. Crew B measured diameters in millimetres, so divide them by 10.
    2. A height of exactly 0 means "not measured", so replace it with NaN.
    3. A diameter below MIN_PLAUSIBLE_DIAMETER_CM is impossible, so replace it with NaN.
    """
    # Work on a copy, so the caller's DataFrame is never changed.
    out = df.copy()

    # Rule 1: crew B's diameters are in mm.
    # np.where(condition, value_if_true, value_if_false) decides row by row:
    # crew B rows are divided by 10, all other rows keep their value.
    is_crew_b = out["crew"] == "B"
    out["diameter_cm"] = np.where(is_crew_b, out["diameter_cm"] / 10, out["diameter_cm"])

    # Rule 2: height 0 is a placeholder, not a real height.
    # .loc[rows, column] = value changes only the rows that match the condition.
    out.loc[out["height_m"] == 0, "height_m"] = np.nan

    # Rule 3: impossible diameters (too small to be a spruce in this data) become missing.
    out.loc[out["diameter_cm"] < MIN_PLAUSIBLE_DIAMETER_CM, "diameter_cm"] = np.nan

    return out


def fit_estimators(cleaned: pd.DataFrame) -> dict:
    """Fit the two linear models used to fill missing values. Use TRAIN data only.

    Both models are linear regressions on the logarithms (the power law from Task 2):
    - diameter model: log(diameter) from log(height) and log(biomass)
    - height model:   log(height) from log(diameter) and log(biomass)

    Each model is fitted only on rows where all three values are observed,
    so no estimated value is ever used to fit a model.

    Returns a dict with the fitted models under the keys "diameter" and "height".
    """
    # Keep only rows where diameter, height and biomass are all observed.
    complete = cleaned.dropna(subset=["diameter_cm", "height_m", "biomass_kg"])

    # Diameter model: inputs are log(height) and log(biomass), target is log(diameter).
    model_diameter = LinearRegression().fit(
        np.log(complete[["height_m", "biomass_kg"]].values),
        np.log(complete["diameter_cm"].values),
    )

    # Height model: inputs are log(diameter) and log(biomass), target is log(height).
    model_height = LinearRegression().fit(
        np.log(complete[["diameter_cm", "biomass_kg"]].values),
        np.log(complete["height_m"].values),
    )

    return {"diameter": model_diameter, "height": model_height}


def estimate_missing(cleaned: pd.DataFrame, models: dict) -> pd.DataFrame:
    """Fill missing diameters and heights with the fitted models.

    Order matters: diameter first, because the height model uses diameter as an input.
    Raises an error if a row misses both diameter and height, because neither can be
    estimated from the other.
    """
    out = cleaned.copy()

    # Step 1: estimate missing diameters from height and biomass.
    missing_diameter = out["diameter_cm"].isna()
    if missing_diameter.any():
        if out.loc[missing_diameter, "height_m"].isna().any():
            raise ValueError("A row misses both diameter and height: cannot estimate it.")
        inputs = np.log(out.loc[missing_diameter, ["height_m", "biomass_kg"]].values)
        # The model predicts log(diameter); np.exp undoes the log, giving cm again.
        out.loc[missing_diameter, "diameter_cm"] = np.exp(models["diameter"].predict(inputs))

    # Step 2: estimate missing heights from diameter and biomass.
    # Diameters are complete at this point, including the ones estimated in step 1.
    missing_height = out["height_m"].isna()
    if missing_height.any():
        inputs = np.log(out.loc[missing_height, ["diameter_cm", "biomass_kg"]].values)
        out.loc[missing_height, "height_m"] = np.exp(models["height"].predict(inputs))

    return out
