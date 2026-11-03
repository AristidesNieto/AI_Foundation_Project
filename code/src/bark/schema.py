"""Shared column contract for all CSV files.

Agreed by Aristides and Caspar (Task 1, step S1). Change only after discussing with the team.
"""

# Columns present in all three CSV files
COMMON_COLUMNS = [
    "tree_id",
    "crew",
    "survey_batch",
    "east",
    "north",
    "altitude_m",
    "aspect",
    "spruce_share",
    "water_deficit_mm",
    "diameter_cm",
    "height_m",
]

# Numeric columns among the common ones
NUMERIC_COLUMNS = [
    "east",
    "north",
    "altitude_m",
    "spruce_share",
    "water_deficit_mm",
    "diameter_cm",
    "height_m",
]

# Category columns among the common ones
CATEGORY_COLUMNS = ["crew", "survey_batch", "aspect"]

# File-specific columns
FELLED_TARGET = "biomass_kg"   # felled_trees.csv
INSPECTED_TARGET = "infested"  # inspected_trees.csv, values yes / no
DISTRICT_DUST = "bore_dust"    # district_trees.csv, values found / not found / empty

# Values allowed for the aspect (direction the slope faces)
ASPECT_VALUES = ["N", "E", "S", "W"]
