# AI_Foundation_Project

## Dataset

- `train/` contains the training CSV files: district trees, felled trees, and inspected trees.
- `test/` contains the corresponding test CSV files.
- `facts.yaml` contains the project assumptions and parameters.

The CSV files include tree identifiers and forestry measurements, including projected
coordinates. `.DS_Store` files are local macOS metadata and are excluded from version control.

## Project structure

- `CLAUDE.md`: team context and rules, read automatically by Claude Code. Start here.
- `docs/`: the project handout (`handout.md`, `handout.pdf`).
- `code/`: the deliverable folder (`predict.py`, `src/bark/`, notebooks, models, figures).
- `report/`: the 8-page report.

## Setup

Requires [uv](https://docs.astral.sh/uv/). From the `code/` folder:

```sh
uv sync                 # create the environment from uv.lock
uv run python -c "import bark"   # check the package imports
```

Do not use `test/` until the pipeline is final (see `CLAUDE.md`, section 4).
