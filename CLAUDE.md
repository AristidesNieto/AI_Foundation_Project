# CLAUDE.md — Project context (shared by the whole team)

This file is read automatically by Claude Code at the start of every session. Keep it accurate.
Team: **Aristides** and **Caspar**. Course: AIFo HS2026, graded mini-project "Which spruces should be felled?".

All code, comments, docs and commit messages are in **English**.

---

## 1. The project in one paragraph

A forest office has a bark beetle outbreak. We must (a) estimate for every district spruce its
timber value `V` (from biomass) and its infestation probability `p`, (b) correct `p` with Bayes'
rule, (c) decide which trees to fell (at most `K`) and which trees a forester should check next
(`M` bore-dust checks), and (d) deliver a re-runnable script `predict.py` plus a report of at most
8 pages. The oral exam (15 min) decides our grade, so **both members must understand the whole
pipeline**, not only their part.

Source of truth for the task: `docs/handout.md` (same content as `docs/handout.pdf`).

## 2. Repository layout

```
AI_FoPrjt/
├── CLAUDE.md              this file (team context)
├── README.md              dataset description + setup
├── facts.yaml             office parameters (price, L, S, F, K, M, district_share, bore-dust sensitivity/specificity)
├── train/                 training data (felled_trees, inspected_trees, district_trees .csv)
├── test/                  test data — DO NOT USE until the pipeline is final (see section 4)
├── docs/                  handout (md + pdf)
├── code/                  the deliverable folder (what the office runs)
│   ├── pyproject.toml     dependencies (managed with uv)
│   ├── uv.lock            locked versions — commit it
│   ├── predict.py         entry point: uv run predict.py <district file> <facts file>
│   ├── src/bark/          cleaning and model code (importable package "bark")
│   ├── models/            saved fitted models (handout: hand them in)
│   ├── notebooks/         exploratory analysis (EDA) notebooks
│   └── figures/           plots used in the report
└── report/                the 8-page report (source + PDF)
```

Run commands from inside `code/`. The handout's example call is
`uv run predict.py ../test/district_trees.csv ../facts.yaml`, so paths are relative to `code/`.

## 3. Data — what is in the files

Columns shared by all three CSV files:
`tree_id, crew, survey_batch, east, north, altitude_m, aspect, spruce_share, water_deficit_mm, diameter_cm, height_m`

| File | Extra columns | Used for |
|---|---|---|
| `felled_trees.csv` | `biomass_kg` (target for Task 2) | predicting biomass → `V` |
| `inspected_trees.csv` | `infested` yes/no (target for Task 3) | predicting `p_model`; sample share |
| `district_trees.csv` | `bore_dust` (found / not found / empty) | Task 4 Bayes update; Task 5 decisions |

Units: `east`, `north` in LV95 metres; `altitude_m` m; `spruce_share` %; `water_deficit_mm` mm;
`diameter_cm` cm (at 1.3 m); `height_m` m; `biomass_kg` kg; `aspect` is N/E/S/W.

`facts.yaml` keys: `price_per_kg`, `L`, `S`, `F`, `K`, `M`, `district_share`, `bore_dust.sensitivity`,
`bore_dust.specificity`. Never hard-code these numbers; always read them from `facts.yaml`.

**Known: the data have quality problems** (placeholders, mixed labels, bad coordinates, etc.). We do
not yet know exactly which. Task 1 is where we find out — see section 5. Every problem found must be
backed by evidence from the raw data, and the cleaning must be **rule-based and general**, because
`test/` and `test_exam/` have the same kinds of problems on other trees. No manual fixes.

## 4. Hard rules (non-negotiable)

1. **Do not open or analyse `test/` (or `test_exam/`) until the pipeline is final.** Work only on
   `train/`. Build, compare, choose and fit everything on `train/` (5-fold CV).
2. Fix random seeds everywhere (`random_state=...`), so `predict.py` is reproducible.
3. Write numbers **unrounded** in output files.
4. `predict.py` must read every parameter from `facts.yaml` and must run unchanged on new data
   with the same columns and the same kinds of data problems.
5. Do not use `class_weight='balanced'` anywhere (Task 3 needs calibrated probabilities).
6. Every cell in `felling_list.csv` must have a value. If a value cannot be repaired, use the best
   estimate.
7. Understand every step. AI tools are allowed, but each team member must be able to explain the
   full pipeline in the oral. Record AI use in the report (section 10).
8. **Do not commit or push** without the user's explicit go-ahead. Git is shared, so both members
   check with each other before pushing.

## 5. Task 1 — Explore and clean (current work)

**Deliverables of Task 1:** cleaning code that the script applies to every new file; the cleaned
columns of `felling_list.csv`; report sections 2 (exploratory data analysis) and 3 (data problems
and cleaning). Each task ends with a 2–3 sentence discussion: what we learned and which choices we
are least sure of.

### Work split

Owner = who does the work. Both review the other's steps (step J1).

**Shared (both, at the start)**
- [ ] **S1** Agree the column contract (section 3) and the rule for each shared column. Recorded in `code/src/bark/schema.py`.

**Aristides — `felled_trees.csv`**
- [x] **A1** Load `train/felled_trees.csv`; row count, dtypes, missing values per column.
- [x] **A2** Summary statistics of numeric columns (count, mean, sd, min, median, max, missing).
- [x] **A3** Category counts: `aspect`, `crew`, `survey_batch`.
- [x] **A4** Histograms of every numeric column.
- [x] **A5** Scatter plots of `biomass_kg` against `diameter_cm` and against `height_m` (check the power-law shape).
- [x] **A6** List the problems found in `felled_trees.csv`, with raw-data evidence (row examples).
- [x] **A7** Write `clean_felled()` in `code/src/bark/clean_felled.py`; check it on `train/` only.
- [x] **A8** Write the felled-trees part of report sections 2 and 3. (Draft in `report/felled_sections_2_3_draft.md`; final format waits for the report-tool decision.)

**Aristides — shared columns (proposal, to confirm with Caspar)**
- [x] **S2** Write `clean_shared()` in `code/src/bark/clean_shared.py`: normalise `aspect`, `crew`, `survey_batch`, and any shared-column placeholders found in A6 and C7. Owned by Aristides, reviewed by Caspar.

**Caspar — `inspected_trees.csv` and `district_trees.csv`**
- [ ] **C1** Row counts; count infested vs healthy in `inspected_trees.csv` (this gives the **sample share**).
- [ ] **C2** Summary statistics of numeric columns for both files; missing values; value counts of `bore_dust` in `district_trees.csv`.
- [ ] **C3** Category counts `aspect`, `crew`, `survey_batch` for both files.
- [ ] **C4** Map of inspected trees (`east` vs `north`), coloured by `infested`.
- [ ] **C5** Correlation matrix of the numeric columns of `inspected_trees.csv`.
- [ ] **C6** Box plots of tree and site properties for infested vs healthy trees.
- [ ] **C7** List problems in both files, with raw-data evidence, including any encoding problems in `infested` and `bore_dust`.
- [ ] **C8** Write `clean_inspected()` (`code/src/bark/clean_inspected.py`) and `clean_district()` (`code/src/bark/clean_district.py`); check on `train/` only.
- [ ] **C9** Write the inspected/district part of report sections 2 and 3.

**Joint (both)**
- [ ] **J1** Review each other's EDA and cleaning rules (read the notebooks and functions, ask questions).
- [ ] **J2** Integrate: one function that cleans all three files and returns the felling-list columns; confirm no missing values remain.
- [ ] **J3** Each member writes their own 2–3 sentence Task 1 discussion.

### Status

Update the checkboxes above as steps are finished, and say who did them in the commit message.

## 6. Conventions

- **Language:** English everywhere.
- **Python:** managed by `uv` inside `code/`. Use `uv add <package>` so `pyproject.toml` and `uv.lock` stay in sync.
- **Packages used:** pandas, numpy, scikit-learn, matplotlib, seaborn, pyyaml (see `pyproject.toml`).
- **Cleaning functions** take a DataFrame and return a DataFrame. They never read files directly.
  File reading happens in `predict.py` only.
- **Plots** go to `code/figures/`, and exploration notebooks to `code/notebooks/`. Name notebooks
  `01_eda_felled_<name>.ipynb`, `01_eda_inspected_district_<name>.ipynb`.
- **Branches:** two long-lived personal branches, `aristides` (Aristides) and `caspar` (Caspar).
  - Each person does all their work on their own branch. Nobody commits directly to `main`.
  - Before starting a session, update the branch from `main` (`git pull` / merge `main`).
  - When a step or task is ready, open a pull request from your branch into `main`. The other
    member reviews it (step J1) before it is merged.
  - Do not edit files that belong to the other member's part without agreeing first in the
    decision log (section 8).
  - Do not force-push `main` or the personal branches.
  - Status: created from `main` (see log, section 8). Workflow steps are in section 9.
- **Commits:** small and descriptive, prefixed with the step ID, for example `A4: histograms of felled trees`.
  No `Co-Authored-By` or AI-tool attribution lines in commits or PR descriptions (see log, section 8).

## 7. Open decisions (to settle as a team)

- Which tool writes the 8-page report (LaTeX, Typst or Word). Default: LaTeX in `report/`.
- Exact placeholder values and encodings. These are decided by the Task 1 EDA, not in advance.
- Whether `felling_list.csv` and `check_list.csv` are committed (default: git-ignored; they are regenerated by `predict.py`).
- Whether the branch workflow in section 6 is accepted by both members.
- Who owns `clean_shared()` (proposed: Aristides, reviewed by Caspar).

## 8. Decision log (project memory)

**Rule:** every time something is changed, decided or ruled out, append one entry here in the same
session, before finishing. This applies to Aristides, Caspar, and any AI agent working on either
branch. The log is the project's memory: anyone (or any agent) reading this file must be able to
see what was decided, when, by whom, and why.

**Entry format** (newest entries at the bottom, never delete old entries; if a decision is
reversed, add a new entry that references the old one):

```
### YYYY-MM-DD · <short title>
- **Who:** Aristides / Caspar / both
- **Status:** DECIDED | PROPOSED | REVERSED (see entry ...)
- **What:** the change or decision, in one or two sentences
- **Why:** the reason
- **Affects:** files, steps (e.g. A7), or sections of this file
```

### Log

### 2026-11-03 · Project context file is CLAUDE.md
- **Who:** Aristides
- **Status:** DECIDED
- **What:** Team context lives in `CLAUDE.md` at the repo root, not `CONTEXT.md`.
- **Why:** Claude Code loads `CLAUDE.md` automatically, so both members' agents read it without being told.
- **Affects:** `CLAUDE.md`

### 2026-11-03 · Task 1 split by file
- **Who:** Aristides and Caspar (proposed by Claude, to confirm)
- **Status:** PROPOSED
- **What:** Aristides: `felled_trees.csv` (A1–A8). Caspar: `inspected_trees.csv` and `district_trees.csv` (C1–C9). Both: shared contract (S1), cross-review (J1), integration (J2), discussion (J3).
- **Why:** Each file feeds a different downstream task, and the files are independent apart from shared columns.
- **Affects:** `CLAUDE.md` section 5

### 2026-11-03 · Shared-column cleaning owned by Aristides
- **Who:** Aristides (proposed), Caspar to review
- **Status:** PROPOSED
- **What:** `clean_shared()` (S2) for `aspect`, `crew`, `survey_batch` and shared placeholders is written by Aristides and reviewed by Caspar.
- **Why:** Shared rules must be identical for all three files, so one owner avoids divergence.
- **Affects:** `code/src/bark/clean_shared.py`

### 2026-11-03 · Handout moved into docs/
- **Who:** Aristides
- **Status:** DECIDED
- **What:** `Miniproj2026_Handout_v1_21Oct26.md` and `.pdf` moved to `docs/handout.md` and `docs/handout.pdf`.
- **Why:** Keep the root clean and give the handout a stable path for agents.
- **Affects:** `docs/`

### 2026-11-03 · Deliverable folder is code/, managed with uv
- **Who:** Aristides
- **Status:** DECIDED
- **What:** `code/` holds `pyproject.toml`, `uv.lock`, `predict.py`, `src/bark/`, `models/`, `notebooks/`, `figures/`. Python 3.12 pinned in `code/.python-version`; `requires-python >=3.11`.
- **Why:** The handout's required call `uv run predict.py ../test/district_trees.csv ../facts.yaml` runs from inside a folder next to `test/`.
- **Affects:** `code/`, `CLAUDE.md` section 2

### 2026-11-03 · Shared column contract in schema.py
- **Who:** Aristides (step S1 draft; needs Caspar's agreement)
- **Status:** PROPOSED
- **What:** Common columns, numeric and category columns, and target/extra columns are defined in `code/src/bark/schema.py`.
- **Why:** One agreed contract for both members' code.
- **Affects:** `code/src/bark/schema.py`, step S1

### 2026-11-03 · Test data not analysed during setup
- **Who:** Aristides (via Claude during setup)
- **Status:** DECIDED
- **What:** During setup, Claude printed the header and first data row of each `test/` file to read the column names. No analysis was done on `test/`. Going forward, `test/` stays closed until the pipeline is final (section 4, rule 1).
- **Why:** The handout forbids opening `test/` before the pipeline is final. Recording it here keeps the history honest.
- **Affects:** section 4, rule 1

### 2026-11-03 · Outputs git-ignored, saved models committed
- **Who:** Aristides
- **Status:** DECIDED
- **What:** `code/felling_list.csv` and `code/check_list.csv` are in `.gitignore`. `code/models/` is committed.
- **Why:** The two CSVs are regenerated by `predict.py`. The handout requires the saved models to be handed in.
- **Affects:** `.gitignore`, `code/models/`

### 2026-11-03 · Two personal branches (aristides, caspar)
- **Who:** Aristides (proposed)
- **Status:** PROPOSED
- **What:** Two long-lived branches, one per member; PRs into `main`; reviewed by the other member.
- **Why:** Keeps each person's work separate while both work on the same repo.
- **Affects:** section 6, Branches

### 2026-11-03 · Commit attribution: no co-author lines
- **Who:** Aristides
- **Status:** DECIDED
- **What:** Commits and PR descriptions do not get `Co-Authored-By` or AI-tool attribution lines. Commits are authored by the person who makes them (`AristidesNieto` / Caspar's own git identity).
- **Why:** The team wants commit history to show the people, not the tools.
- **Affects:** section 6, Commits

### 2026-11-03 · Initial project setup committed to main
- **Who:** Aristides
- **Status:** DECIDED
- **What:** First commit with the base structure (CLAUDE.md, README, docs/, code/ skeleton, report/ placeholder, .gitignore update) pushed directly to `main`. This is the only direct commit to `main` planned; everything after goes through the personal branches.
- **Why:** The base must exist on `main` before the two personal branches are created from it.
- **Affects:** whole repo

### 2026-11-03 · Personal branches created from main
- **Who:** Aristides
- **Status:** DECIDED
- **What:** Branches `aristides` and `caspar` created from `main` and pushed to GitHub.
- **Why:** Each member works on their own branch as described in section 6.
- **Affects:** section 6, Branches

### 2026-11-03 · GitHub workflow guide added to CLAUDE.md
- **Who:** Aristides
- **Status:** DECIDED
- **What:** Section 9 explains the GitHub workflow step by step for members new to git.
- **Why:** Caspar has little experience with the GitHub workflow; the guide lets him and his agent follow the same process.
- **Affects:** section 9

### 2026-11-03 · Findings in felled_trees.csv (step A6)
- **Who:** Aristides (with Claude)
- **Status:** DECIDED (these are facts from the data, not choices)
- **What:**
  1. Diameters in mm for crew B: 136 rows, all of crew B; crew B has no diameter below 100 cm (evidence: crosstab of `crew` vs `diameter_cm > 100`, and the biomass vs diameter scatter, two separate clouds).
  2. Height placeholder 0: 18 rows, spread over all crews (evidence: crosstab of `crew` vs `height_m == 0`).
  3. Height missing (NaN): 40 rows, spread over all crews (evidence: `isna()` by crew).
  4. Impossible diameter 1.6 cm, crew A, row T742819: biomass 85.7 kg and height 15.0 m both match a diameter of about 16 cm (probable decimal error).
  5. Single outlier check: no other diameter below 5 cm was found.
- **Why:** Needed for the cleaning rules in A7.
- **Affects:** step A6, `code/src/bark/clean_felled.py` (A7)

### 2026-11-03 · Impossible diameter estimated, not hand-fixed
- **Who:** Aristides
- **Status:** DECIDED
- **What:** A diameter that is impossible (below a plausible minimum, for example 5 cm) is treated as missing and estimated from the other measurements of the tree, the same way as missing heights. No single row is corrected by hand.
- **Why:** Hand fixes are forbidden (section 4, rule 6 and the project rules: every rule must be general and work on test/ and test_exam/). Estimating from other measurements uses the handout's instruction "write your best estimate".
- **Affects:** step A7, `clean_felled()`

### 2026-11-03 · Diameter for crew B divided by 10
- **Who:** Aristides and Claude (proposed)
- **Status:** DECIDED (confirmed by Aristides)
- **What:** Diameters of crew B are divided by 10 (mm to cm).
- **Why:** Finding 1 above. Evidence: the B-only values after dividing fall into the same cloud as the other crews.
- **Affects:** step A7, `clean_felled()`

### 2026-11-03 · Height placeholder 0 treated as missing
- **Who:** Aristides and Claude (proposed)
- **Status:** DECIDED (confirmed by Aristides)
- **What:** Height 0 is treated as missing, then estimated like the other missing heights (method to be decided, likely a regression on diameter, class material week 4).
- **Why:** Finding 2 above; a tree cannot be 0 m tall.
- **Affects:** step A7, `clean_felled()`

### 2026-11-03 · Findings: aspect spellings in felled_trees.csv (step A3)
- **Who:** Aristides (with Claude)
- **Status:** DECIDED (fact from the data)
- **What:** The `aspect` column uses several spellings for the same directions: `S`, `South`, `s`, `SÜD` (for south). Counts before cleaning: E 190, W 105, S 92, N 50, South 40, s 36, SÜD 27.
- **Why:** Same category written in different ways is a typical field-data problem (handout, Task 1).
- **Affects:** step A3, `code/src/bark/clean_shared.py`

### 2026-11-03 · Aspect spellings mapped to N, E, S, W (shared rule)
- **Who:** Aristides (proposed), Caspar to review
- **Status:** PROPOSED
- **What:** `clean_shared()` removes spaces, uses upper case, and maps every known spelling to N, E, S or W (`ASPECT_MAP`). Unknown spellings become missing. After the mapping, `S` has 195 rows in `train/felled_trees.csv`.
- **Why:** The rule must be identical for all three files, so it belongs to the shared cleaning.
- **Affects:** `code/src/bark/clean_shared.py`, step S2

### 2026-11-03 · Impossible diameter threshold: 5 cm
- **Who:** Aristides
- **Status:** DECIDED
- **What:** Diameters below 5 cm are treated as impossible and become missing (`MIN_PLAUSIBLE_DIAMETER_CM = 5.0`). In `train/` the smallest valid diameter after the crew B fix is 12.5 cm, so 5 cm separates the impossible value (1.6 cm) from real trees with a wide margin.
- **Why:** Rule 3 of `clean_felled()`, agreed in the decision "Impossible diameter estimated, not hand-fixed".
- **Affects:** `code/src/bark/clean_felled.py`

### 2026-11-03 · Missing diameters and heights estimated with linear models on the logarithms
- **Who:** Aristides (with Claude)
- **Status:** DECIDED
- **What:** Two linear regressions on the logarithms, fitted only on rows with diameter, height and biomass observed in `train/`. Diameter model: log(diameter) from log(height) and log(biomass). Height model: log(height) from log(diameter) and log(biomass). Diameter is estimated first, because the height model uses it. R² on the fit data: about 0.97 (diameter), 0.90 (height). The 58 height values and 1 diameter value are filled this way.
- **Why:** The biomass relation is a power law (Task 2), so its logarithm is linear. Using biomass as input uses information that is observed for every felled tree. Fitting only on observed rows avoids using estimated values to fit the model.
- **Affects:** `code/src/bark/clean_felled.py` (`fit_estimators`, `estimate_missing`), notebook `01_eda_felled_aristides.ipynb`

### 2026-11-03 · Estimation lives in the module, not only in the notebook
- **Who:** Aristides (with Claude)
- **Status:** DECIDED
- **What:** `fit_estimators()` and `estimate_missing()` are in `clean_felled.py`, and the notebook calls them. The notebook and `predict.py` must use the same code.
- **Why:** `predict.py` has to apply the same fitted models to `test/` and `test_exam/`, without refitting.
- **Affects:** `code/src/bark/clean_felled.py`, notebook

### 2026-11-03 · Open items after step A7
- **Who:** Aristides
- **Status:** PROPOSED (to do next)
- **What:** (1) Save the two fitted models in `code/models/` so `predict.py` can reuse them. (2) `estimate_missing()` raises an error if a row misses both diameter and height. This did not happen in `train/`, but it could in new data; decide how to handle it. (3) Write the felled-trees part of the report (A8). (4) Caspar reviews `clean_shared()` and agrees the schema (S1).
- **Why:** Needed for `predict.py` and for the report.
- **Affects:** steps A8, S1, S2, `code/models/`

### 2026-11-03 · Estimators saved to code/models/
- **Who:** Aristides (with Claude)
- **Status:** DECIDED
- **What:** The two fitted models (diameter and height) are fitted on `train/` only and saved to `code/models/felled_estimators.joblib` by `code/src/bark/models_io.py`. Reloading gives identical estimates (checked).
- **Why:** `predict.py` must apply the same models to `test/` and `test_exam/` without refitting. The handout asks for the saved models to be handed in.
- **Affects:** `code/src/bark/models_io.py`, `code/models/`

### 2026-11-03 · Figures for the felled-trees report section
- **Who:** Aristides (with Claude)
- **Status:** DECIDED
- **What:** Four figures in `code/figures/`: `felled_histograms_clean.png`, `felled_biomass_vs_diameter_raw.png`, `felled_biomass_vs_diameter_clean.png`, `felled_height_vs_diameter_clean.png`.
- **Why:** Figures required by the report (section 2 and 3, captions with labelled axes).
- **Affects:** `code/figures/`, report sections 2 and 3

### 2026-11-03 · Report draft in Markdown until the tool is chosen
- **Who:** Aristides (with Claude)
- **Status:** DECIDED (temporary)
- **What:** The felled-trees text for sections 2 and 3 is in `report/felled_sections_2_3_draft.md`. It will be moved to the final report tool once that is decided (section 7).
- **Why:** The report tool is still open. A Markdown draft keeps the content and the numbers reviewable now.
- **Affects:** `report/`, section 7 (open decisions)

## 9. GitHub workflow guide (read this if you are new to git)

Repository: `https://github.com/AristidesNieto/AI_Foundation_Project`

**Words**
- **Repository (repo):** the project folder plus its full history.
- **Branch:** a separate line of work. Your branch can change without touching anyone else's.
- **Commit:** a saved snapshot of changes, with a message. Make small commits, one per step (for example `A4: histograms of felled trees`).
- **Push:** send your local commits to GitHub.
- **Pull:** bring new commits from GitHub into your local copy.
- **Pull request (PR):** a request to merge your branch into `main`. The other member reviews it before merging.

**First time only: get the project**
```sh
git clone https://github.com/AristidesNieto/AI_Foundation_Project.git
cd AI_Foundation_Project
git checkout caspar          # Caspar's branch (Aristides uses: git checkout aristides)
```

**Start of every work session**
```sh
git checkout caspar          # make sure you are on your own branch
git pull                     # get the latest changes from GitHub
git merge main               # bring in what has been merged into main
```

**While working**
```sh
git status                   # what changed
git add <file> ...           # choose the files for this commit (do not use `git add -A` blindly)
git commit -m "C4: map of inspected trees coloured by infested"
git push                     # send your commits to GitHub
```

**Finishing a step or task**
1. Make sure your code runs and the decision log (section 8) is updated.
2. Push your branch (`git push`).
3. On GitHub, open a pull request from your branch (`caspar`) into `main`.
4. Ask the other member to review it. They check the code and the log, then approve and merge.
5. After merging, update your local branch: `git checkout caspar && git pull && git merge main`.

**Rules**
- Never commit directly to `main`.
- Never force-push (`git push --force`). It overwrites the other person's history.
- Never commit secrets, API keys or `.venv/`. `.gitignore` already excludes `.venv/` and generated CSVs.
- If `git pull` reports a conflict, stop and ask the other member or Aristides. Do not guess which version to keep.
- Do not add `Co-Authored-By` or AI-tool lines to commits or PRs (section 6, Commits).
