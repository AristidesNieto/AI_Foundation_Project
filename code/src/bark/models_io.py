"""Save and load fitted models. Owner: Aristides (step A7, part 3).

This is the only place in the package that writes model files.
The cleaning modules never touch the disk.
"""

from pathlib import Path

import joblib

# Default location of the saved felled-trees estimators (handout: hand in the saved models).
FELLED_ESTIMATORS_PATH = Path(__file__).resolve().parents[2] / "models" / "felled_estimators.joblib"


def save_estimators(models: dict, path: Path = FELLED_ESTIMATORS_PATH) -> None:
    """Write the fitted models dict (from fit_estimators) to a joblib file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(models, path)


def load_estimators(path: Path = FELLED_ESTIMATORS_PATH) -> dict:
    """Read the fitted models dict back from a joblib file."""
    return joblib.load(path)
