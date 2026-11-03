# Which spruces should be felled?

**AIFo · HS2026 · Graded mini-project** · Bark Beetle Data Challenge

> *Figura: Spruce stands after a bark beetle outbreak, Harz (Germany) · Fährtenleser, CC BY-SA 4.0*

A forest office faces a bark beetle outbreak. It asks your team to analyse its tree data and recommend which spruces to fell this season. You deliver a script and a report, and you defend your recommendation in an oral exam.

- **Team:** two students. If the number of students is odd, one team has three students. The lecturers decide which team.
- **Weight:** 40% of the AIFo grade. The written exam counts 60%.
- **Effort:** about 10–15 hours per student. Part of it during exercise sessions.
- **You hand in:** your code and a report of at most 8 pages.
- **Assessment:** a 15-minute oral exam. Your project grade is based on it. We use your PDF report to prepare your exam.
- **Dates:** see Moodle.

---

## The mandate

After several hot, dry summers, the European spruce bark beetle is multiplying in the spruce stands (patches of forest) of a forest district in the Swiss Prealps.

An infested spruce usually dies within the season. Its wood dries out, cracks and turns blue, and it sells for less. After some weeks, a new generation of beetles leaves the tree and attacks nearby spruces. If the crew fells an infested tree and removes it from the forest before the beetles fly out, the spread stops there. But felling costs money, and the crew can fell only a limited number of trees.

> *Figura: The European spruce bark beetle (*Ips typographus*, German: Buchdrucker) is about 5 mm long. Photo: Francisco Welter-Schultes, CC0.*

The district forest office asks your team to support its decisions with data:

- estimate, for every spruce in the district, how likely it is infested and what its wood is worth,
- recommend which trees the crew should fell this season,
- recommend which trees a forester should check next,
- deliver a script that the office can run again when new data come in.

### AI tools and grading

You may use AI tools, for example to write code, but make sure that you understand every step of your pipeline.

**Your project grade is based on the oral exam.** In the oral, the examiners test your understanding of the problem, of the methods and of your results. Every team member must understand the full project, even if you split the work. All members of a team get the same grade, unless the lecturers identify obvious large differences in individual effort and understanding.

The questions in Tasks 1–5 set the scope of the project. Methods beyond the class material and additional analyses earn no extra points.

---

## Data

The forest office gives you two folders, `train/` and `test/`, and the file `facts.yaml`. Each folder holds the three CSV files below. Different people collected the data in the field, so expect data problems (Task 1).

| File | Content | Contains what you predict? |
|---|---|---|
| `felled_trees.csv` | Spruces that were felled and weighed | Yes: biomass in kg |
| `inspected_trees.csv` | Spruces that a forester checked for beetles | Yes: infested yes/no |
| `district_trees.csv` | All other spruces in the district. Some have the result of a bore-dust check: a forester looked for the drilling dust that beetles leave on the bark (Task 4). | No |
| `facts.yaml` | Price per kg, costs, crew capacity, the district share, and the sensitivity and specificity of the bore-dust check. One file for all folders. | — |

The CSV files have these columns:

| Column | Meaning | Unit |
|---|---|---|
| `tree_id` | Identifier of the tree | — |
| `crew` | Field crew that measured the tree | — |
| `survey_batch` | Survey in which the tree was measured | — |
| `east`, `north` | Position of the tree in Swiss coordinates (LV95) | m |
| `altitude_m` | Altitude above sea level | m |
| `aspect` | Direction the slope faces: N, E, S or W | — |
| `spruce_share` | Share of spruces in the stand | % |
| `water_deficit_mm` | How dry the site is | mm |
| `diameter_cm` | Stem diameter at breast height (1.3 m) | cm |
| `height_m` | Tree height | m |
| `biomass_kg` | Dry above-ground biomass. Only in `felled_trees.csv`. | kg |
| `infested` | yes or no. Only in `inspected_trees.csv`. | — |
| `bore_dust` | found, not found, or empty if the tree was not checked. Only in `district_trees.csv`. | — |

The tasks speak of tree properties and site properties:

- **Tree properties:** `diameter_cm`, `height_m`.
- **Site properties:** `altitude_m`, `aspect`, `spruce_share`, `water_deficit_mm`.

Two numbers say how common infested trees are:

- **Sample share:** the share of infested trees among the inspected trees (`inspected_trees.csv`). You count it yourself.
- **District share:** the share of infested trees among the district trees (`district_trees.csv`). `facts.yaml` gives it as `district_share`, estimated from an aerial survey.

The sample share is much higher than the district share. Task 4 explains why.

### How to use `train/` and `test/`

- Both folders come from the same district. Their files have the same columns.
- Work on `train/` only. Build, compare, choose and fit all your models there. Use 5-fold cross-validation. If you need a validation set, split it off `train/` yourself.
- **Do not open `test/` until your pipeline is final.**
- When your pipeline is final, use `test/` once, as new data from the office. Check your models on its felled and inspected trees. Run your script on its `district_trees.csv`. Do not change or refit your models afterwards. Report the test performance of your model (see below).
- The district files of `train/`, `test/` and `test_exam/` (data the lecturers keep back to check your script) have the same size. K (the number of trees the crew can fell) and M (the number of trees a forester can still check) in `facts.yaml` apply to each of them.

### Compare `test/` with `train/`

Compare three numbers: the biomass RMSE in kg (Task 2), and the AUC and the log-loss of your model (Task 3).

- On `train/`, repeat the 5-fold cross-validation 10 times (`RepeatedKFold`, as seen in class). Give the mean and the standard deviation over all 50 folds.
- On `test/`, compute each number once.
- A `test/` value more than about two standard deviations from the mean needs an explanation.

**Example** from another district. Your numbers differ.

| Number | `train/`: mean ± SD (50 folds) | `test/` | Distance in SD |
|---|---|---|---|
| Biomass RMSE | 86.8 ± 8.8 kg | 76.2 kg | −1.2 |
| AUC | 0.917 ± 0.030 | 0.890 | −0.9 |
| Log-loss | 0.370 ± 0.067 | 0.426 | +0.8 |

SD: standard deviation. Distance in SD = (test value − mean) / SD. A value more than three SDs from the mean is very unlikely. It may point to a bug in your pipeline.

---

## The felling rule

The forest office decides tree by tree with a cost rule. The rule needs two inputs: the probability **p** that a tree is infested, and its timber value **V**. Your task is to develop two models: one to estimate the value V, and one to estimate the probability p. Then you correct p with Bayes' rule (Task 4).

### The cost table

For each tree, the office can fell it now or leave it standing. The cost of each choice depends on whether the tree is infested:

| | Tree is infested (probability **p**) | Tree is healthy (probability 1 − p) |
|---|---|---|
| **Fell now** | F | F |
| **Leave standing** | L × V + S | 0 |

- **Felling costs F, whether the tree is infested or healthy.** F pays for an unplanned felling and for removing the logs or their bark before the beetles fly out. The wood is not lost: the felled tree is sold now instead of later. Infested wood that is felled early still sells at almost the normal price.
- **An infested tree left standing costs L × V + S.** While it stands, its wood dries out, cracks and turns blue. It loses the share L of its value V. Its beetles fly out and attack neighbouring trees, which costs S.
- **A healthy tree left standing costs nothing.** It keeps growing and is harvested later as planned.

> **FELL THE TREE IF**
>
> **p × (L × V + S) > F**
>
> The left side is the **expected loss** of leaving the tree standing. The right side is the expected loss of felling it: felling costs F, whether the tree is infested or healthy. The difference is the **expected net saving** of felling the tree.
>
> The crew can fell at most K trees. If more than K trees meet the rule, fell the K trees with the largest expected net saving.

You can also read the rule as a threshold on p. Fell the tree if p is larger than its **break-even probability** F / (L × V + S). A valuable tree has a lower break-even probability, because it has more to lose.

### Symbols

| Symbol | Meaning | Where it comes from |
|---|---|---|
| p | Probability that the tree is infested, after both corrections of Task 4 | You estimate it (Tasks 3, 4) |
| V | Timber value in CHF: biomass in kg × price per kg | You estimate the biomass (Task 2); `facts.yaml` gives the price |
| L | Share of its value an infested tree loses by staying standing instead of being felled now | `facts.yaml` |
| S | Damage in CHF to neighbouring trees if an infested tree stays standing | `facts.yaml` |
| F | Cost in CHF of felling one tree and removing it in time | `facts.yaml` |
| K | Number of trees the crew can fell this season | `facts.yaml` |
| M | Number of further district trees a forester can check for bore dust before felling starts (Task 5) | `facts.yaml` |

### Two examples

The numbers in these examples are made up. Your district's numbers are in `facts.yaml`.

Both trees stand in the same district: price CHF 0.20 per kg, L = 0.5, S = CHF 250, F = CHF 120. Your model gives both trees the same probability, p = 0.40.

**Tree A** — a large spruce: 50 cm diameter, 35 m high, about 1600 kg biomass.

| | |
|---|---|
| V = 1600 kg × 0.20 | CHF 320 |
| L × V + S = 0.5 × 320 + 250 | CHF 410 |
| **Expected loss** = 0.40 × 410 | **CHF 164** |
| Felling cost F | CHF 120 |

**→ FELL.** CHF 164 is more than CHF 120. Expected net saving: CHF 44. Break-even probability: 120 / 410 = 0.29.

**Tree B** — a small spruce: 25 cm diameter, 22 m high, about 250 kg biomass.

| | |
|---|---|
| V = 250 kg × 0.20 | CHF 50 |
| L × V + S = 0.5 × 50 + 250 | CHF 275 |
| **Expected loss** = 0.40 × 275 | **CHF 110** |
| Felling cost F | CHF 120 |

**→ LEAVE STANDING.** CHF 110 is less than CHF 120. Break-even probability: 120 / 275 = 0.44. Tree B would be felled only if p were above 0.44.

Both trees have the same p, but the decisions differ. So the office needs correct values of both p and V. A correct ranking of the trees is not enough.

---

## Your five tasks

The sections above describe the problem. From here on, each section is one task. Each task ends with a result that your script produces or that goes into your report.

```
TASK 1 · Explore and clean
  felled_trees.csv     -> biomass in kg
  inspected_trees.csv  -> infested yes/no
  district_trees.csv
  facts.yaml

TASK 2 · Predict V      : biomass -> V
TASK 3 · Predict p      : probability p_model
TASK 4 · Correct p      : district share, bore dust  -> p
TASK 5 · Fell and check : fell if p × (L × V + S) > F, at most K trees
                          + next field checks
                          -> felling_list.csv, check_list.csv

Flow: Task 1 -> Task 2 (V) and Task 3 (p_model) -> Task 4 (p) -> Task 5
```

Each task names the class material it needs. You can start a task once these weeks are taught.

---

## Task 1 of 5 · Explore and clean it

**You deliver:** cleaning code that your script applies to every new file · the cleaned columns of `felling_list.csv` · report sections 2 and 3.

The data come from several field crews and surveys. Before you model anything, find out what the data look like and what is wrong with them.

### Step 1: Explore

Start with the raw data: most data problems show up there. In your report, show the statistics after cleaning, and only the plots that show a data problem or help you choose a model.

- Count the rows of each file. Count the infested and the healthy trees in `inspected_trees.csv`.
- For each numeric column, compute the count, mean, standard deviation, minimum, median, maximum and the number of missing values.
- For each category column (`aspect`, `crew`, `survey_batch`), count the rows per category.
- Plot:
  - a histogram of each numeric column,
  - biomass against diameter and against height,
  - a map of the inspected trees (`east` against `north`), coloured by infested,
  - the correlations between the numeric columns of `inspected_trees.csv` (you need them to read the odds ratios in Task 3),
  - each tree and site property for infested and for healthy trees, for example as box plots.

### Step 2: Check and clean

Check every column of every file. Typical problems in field data are:

- values that cannot be true,
- placeholders such as 0 or −999 that stand for "not measured",
- missing values,
- mixed units,
- the same category written in different ways,
- coordinates that do not fit the rest,
- duplicate rows.

Your district's data have some of these problems, not all of them. For each problem you find, show the evidence in the raw data. Then decide how your pipeline handles it.

`test/` and `test_exam/` have the same kinds of problems as `train/`, on other trees. Your script must handle them without manual fixes. You do not need rules for problems that `train/` does not show.

Write the cleaned values to your felling list. Every cell must hold a value. Where you cannot repair a value, write your best estimate.

**Discussion.** In your report, close this task with 2–3 sentences: what did you learn in this task, and which of your choices are you least sure of?

**Class material:** W1 Python & Data · W2 Random Variables · W4 Linear Regression

---

## Task 2 of 5 · Predict the timber value V

**You deliver:** `biomass_kg` and `V` for every district tree · report section 4.

Weighing a tree means felling it. So the office weighed a sample of felled spruces. You predict the biomass in kg of every standing district tree from its measurements.

Foresters describe the biomass of a tree as a power law: **biomass ≈ a × d^b × h^c**, with diameter d and height h. Taking the logarithm of both sides gives a linear model.

- Compare two linear models: one on the raw values and one on the logarithms (the power law). Which one fits better? Show the residuals of both. Also plot the residuals against the other columns. A pattern means that the model misses something.
- Compute every RMSE in kg. For a model on the logarithms, transform the predictions back with `exp` before you compute the RMSE.
- Does a site property improve the model? Compare the mean RMSE across the cross-validation folds, with and without it.
- How well does your model predict trees it has not seen? Compare its cross-validated RMSE with a baseline that predicts the mean biomass of the felled trees for every tree.
- Compare the diameters and heights of the district trees with those of the felled trees. For which district trees must your model extrapolate?
- Fit a random forest as well. Plot the predictions of both models against diameter, for the district trees. Where do the two models disagree? Which one do you trust there?
- Choose one model for `biomass_kg` and explain why.
- Compute **V = biomass × price per kg** (`facts.yaml`).

**Discussion.** In your report, close this task with 2–3 sentences: what did you learn in this task, and which of your choices are you least sure of?

**Class material:** W4 Linear Regression · W6 Generalization · W7 Cross-validation · W11 Ensemble methods

---

## Task 3 of 5 · Predict the infestation probability

**You deliver:** `p_model` for every district tree · report section 5.

A forester checked a number of trees for beetles. From these, you predict for every district tree the probability that it is infested. In this task, p means the probability from your model, `p_model`. Task 4 turns it into the p of the felling rule.

- **Start with logistic regression.** Which tree and site properties raise the risk? Use odds ratios:
  - The odds of a tree are p / (1 − p). They say how many times more likely the tree is infested than healthy. Example: p = 0.8 gives odds of 4.
  - Logistic regression models the logarithm of the odds as a linear function of the features.
  - The odds ratio of a feature is exp(w), where w is the weight of the feature. If the feature grows by one unit, the odds are multiplied by exp(w). If you standardized the features, one unit is one standard deviation.
  - An odds ratio above 1 raises the risk. An odds ratio below 1 lowers it.
- **Do not use class weights** such as `class_weight='balanced'`. They make the model act as if half of the inspected trees were infested, so its probabilities come out too high. Task 4 needs calibrated probabilities (see the box below). The felling rule already takes into account what each wrong decision costs.
- **Beetles attack nearby trees. Does knowing a tree's neighbours help?** Try kNN on the coordinates. Try several values of k. For each k, compute the mean log-loss over the 5 cross-validation folds. Choose the k with the lowest mean log-loss.
  - *Hint:* kNN can also produce a feature for logistic regression: the share of infested trees among a tree's k nearest inspected neighbours. Compute it as follows:
    - Inspected trees: compute the feature with `cross_val_predict`, so that a tree is never its own neighbour.
    - District trees: use all inspected trees of `train/` as neighbours. Save their coordinates and labels with your model.
- Evaluate your models with cross-validation: the confusion matrix, precision and recall at the threshold 0.5, ROC/AUC and log-loss. Compare them with a baseline that gives every tree the sample share.
- Check for each model whether its probabilities are calibrated (see the box below). Task 4 works only with calibrated probabilities. Use the result when you choose your model.
- Choose one model and explain why.

> ### Calibrated probabilities
>
> **What.** A model is calibrated if its probabilities match how often trees are actually infested: among all trees for which it says p ≈ 0.3, about 30% are infested. In this task you only check this. You do not change the probabilities.
>
> **Why.** The felling rule multiplies by p. A model can rank the trees well (high AUC) and still give probabilities that are too high or too low. Then the expected losses are wrong, and so are the decisions. Task 4 also assumes calibrated probabilities: its correction cannot repair probabilities that are already wrong. Log-loss grows when probabilities are badly calibrated. The calibration plot shows you where they are wrong.
>
> **How.**
> 1. Compute cross-validated probabilities for the inspected trees: `cross_val_predict(model, X, y, cv=5, method='predict_proba')[:, 1]`.
> 2. Sort the trees into 5 bins by p: 0–0.2, 0.2–0.4, and so on.
> 3. For each bin, compute the mean predicted p and the share of infested trees.
> 4. Plot the share of infested trees (y-axis) against the mean predicted p (x-axis), together with the diagonal. A calibrated model lies close to the diagonal.
>
> `sklearn.calibration.calibration_curve` does steps 2 and 3. It returns the share of infested trees first. Also count the trees in each bin.
>
> **Where.** You can check calibration only on the inspected trees, because only for them do you know which trees are infested. So your probabilities are calibrated, at best, for trees like the inspected ones, where the infested share is the sample share. Among the district trees, infested trees are much rarer, so the same probabilities are too high there. Task 4 corrects this. Check calibration here, before that correction.
>
> **What next.**
> - **What counts as close:** even a calibrated model does not hit the diagonal exactly. With about 100 trees in a bin, the share of infested trees varies by about ±0.1 by chance. So a point up to about 0.1 from the diagonal is close. In a bin with few trees, the point varies even more.
> - **Close to the diagonal:** nothing to fix. Use the probabilities as they are in Task 4. Show the plot in your report.
> - **Clearly off the diagonal** (more than about 0.1, in bins with many trees): where the curve lies below the diagonal, the model's p is too high; above it, too low. A p that is too high fells too many healthy trees. A p that is too low leaves infested trees standing. If another of your models is better calibrated and about as good in AUC and log-loss, choose it. Otherwise keep your model. In your report, say where it is off, and whether this makes your felling list too long or too short. Do not adjust the probabilities yourself.

**Discussion.** In your report, close this task with 2–3 sentences: what did you learn in this task, and which of your choices are you least sure of?

**Class material:** W7 Feature scaling, cross-validation · W8 Logistic regression · W9 Classifier evaluation, kNN

---

## Task 4 of 5 · Correct the probabilities with Bayes' rule

**You deliver:** `p_prior` and `p` for every district tree · the tree diagram for one tree · report section 6.

Your model from Task 3 gives `p_model`. This task corrects it in two steps. Each step uses Bayes' rule, as in weeks 2 and 3:

- **Step 1** corrects for the way the forester selected the inspected trees. The result is `p_prior`.
- **Step 2** adds the result of the bore-dust check, for the trees that have one. The result is `p`.

> **Bayes' rule**
>
> Pr(H | E) = [ Pr(E | H) × Pr(H) ] / Pr(E)
>
> Pr(E) = Pr(E | infested) × Pr(infested) + Pr(E | healthy) × Pr(healthy)

### Step 1: Correct for the sampling

Infested trees are rare. To get enough of them to learn from, the forester checked spruces at random across the district. The forester recorded every infested tree found, but only a random share of the healthy ones. So the sample share is much higher than the district share.

Your model learned from the inspected trees. So `p_model` has the sample share built in as its prior (you counted it in Task 1). For a district tree, the prior is the district share (`district_share` in `facts.yaml`).

| Bayes' rule | Step 1 |
|---|---|
| Hypothesis H | The tree is infested or healthy. |
| Evidence E | The properties of the tree: the features of your model. |
| Prior Pr(H = infested) | The district share. |
| Likelihood Pr(E \| H) | How common these properties are among infested trees and among healthy trees. It is unknown. It is the same for the inspected trees and for the district trees, because the forester chose the trees at random within each group. |
| Posterior Pr(H = infested \| E) | `p_prior` |

Compute `p_prior` for each district tree:

- **a.** Infested: `p_model` ÷ sample share × district share.
- **b.** Healthy: (1 − `p_model`) ÷ (1 − sample share) × (1 − district share).
- **c.** `p_prior` = result (a) / (result (a) + result (b)).

**Example with made-up numbers:** sample share 0.40, district share 0.10, `p_model` = 0.60.

| | Infested | Healthy |
|---|---|---|
| From the model | 0.60 | 0.40 |
| Divided by the sample share (healthy: 1 − sample share) | ÷ 0.40 | ÷ 0.60 |
| Multiplied by the district share (healthy: 1 − district share) | × 0.10 | × 0.90 |
| Result | 0.15 | 0.60 |
| Divided by the sum, 0.75 | **`p_prior` = 0.20** | 0.80 |

- The felling rule uses the values of the probabilities, not only their ranking. What are `p_prior` and `p` of a tree with `p_model` exactly 0 or exactly 1? Can your model from Task 3 output such values?

### Step 2: Add the bore-dust check

For some district trees, a forester looked for bore dust, the brown drilling dust that beetles leave on the bark and at the foot of the trunk. The result is "dust found" or "no dust".

| Bayes' rule | Step 2 |
|---|---|
| Hypothesis H | The tree is infested or healthy. |
| Evidence E | The bore-dust result: dust found or no dust. |
| Prior Pr(H = infested) | `p_prior` from Step 1. |
| Likelihood Pr(E \| H) | The sensitivity Pr(dust found \| infested) and the specificity Pr(no dust \| healthy), from `facts.yaml`. |
| Posterior Pr(H = infested \| E) | `p`. For trees without a bore-dust result, `p` = `p_prior`. |

> *Figura: Tree diagram of the bore-dust check for one district tree. From left to right, it is the generative model: the hidden state of the tree causes the observation. Bayes' rule goes from right to left: from the observation back to the hidden state.*
>
> ```
> District tree --Pr(H=infested)--> infested --Pr(E=dust found | infested)--> dust found
>               |                           --Pr(E=no dust | infested)----> no dust
>               --Pr(H=healthy)-----> healthy --Pr(E=dust found | healthy)--> dust found
>                                           --Pr(E=no dust | healthy)------> no dust
> ```

- Compute `p` with Bayes' rule, as in week 3. The posterior of Step 1 is the prior of Step 2: this is a sequential update.
- This step assumes that the bore-dust result depends only on whether the tree is infested. Discuss in your report whether this is plausible. For example: could the weather, the crew or the bark of old trees change how often dust is found?
- For one tree from your check list (you make it in Task 5), draw this tree diagram with numbers, as in week 3. Write the number on every branch, the joint probability of every path, and both posteriors: Pr(infested | dust found) and Pr(infested | no dust).

**Discussion.** In your report, close this task with 2–3 sentences: what did you learn in this task, and which of your choices are you least sure of?

**Class material:** W2 Random Variables · W3 Bayes' rule

---

## Task 5 of 5 · Decide which trees to fell and which to check

**You deliver:** `fell` in `felling_list.csv` · `check_list.csv` · the expected-loss table and the what-if answers · report section 7.

Use the district trees of `train/`.

- Apply the felling rule and write the felling list.
- Report the number of trees felled.
- Report the expected net saving of your list: the expected loss that the felled trees would cause if they stayed standing, minus their felling costs.
- Fill in the expected-loss table for your felling list, as in the example below. It has one row for each box of the cost table: fell or leave, infested or healthy. Which box holds most of the expected loss, and why?
- The office asks two what-if questions. For each, change one number from `facts.yaml`, keep all other numbers (including K), redo Task 4 and this task without refitting the models of Tasks 2 and 3, and compare the new felling list with your list: how many trees are felled, which trees join or leave the list, and the expected net saving.
  - What if the district share (`district_share`, the share of infested trees among the district trees) were twice as high? For example, the aerial survey may have missed half of the infested trees.
  - What if the felling cost F were 50% higher?

### How to fill in the expected-loss table

You do not know which district trees are infested. So each tree counts in the column "infested" with the weight p, and in the column "healthy" with the weight 1 − p. Each box of the cost table becomes one row:

- **Expected trees:** the sum of the weights of the trees in the box.
- **% of trees:** the expected trees as a percentage of all district trees.
- **Expected loss:** the sum of weight × cost over the trees in the box, in CHF. The cost of each box is in the cost table.
- **% of loss:** the expected loss as a percentage of the total expected loss.

**Example:** the expected-loss table of a felling list for another district with 3,666 trees and F = CHF 90. The crew fells 150 trees. Your numbers differ.

| Box | Expected trees | % of trees | Expected loss (CHF) | % of loss |
|---|---|---|---|---|
| Fell, infested | 66.4 | 1.8 | 5,980 | 13.4 |
| Fell, healthy | 83.6 | 2.3 | 7,520 | 16.8 |
| Leave, infested | 116.5 | 3.2 | 31,145 | 69.8 |
| Leave, healthy | 3,399.5 | 92.7 | 0 | 0 |
| **Total** | **3,666** | **100** | **44,645** | **100** |

**How to read this example:**

- The crew fells 150 trees. About 66 of them are expected to be infested, and about 84 to be healthy.
- The two "fell" rows together cost 150 × F = CHF 13,500. Felling costs the same for infested and for healthy trees.
- About 117 infested trees are expected to stay standing. They cause 70% of the expected loss. This box, CHF 31,145, is the expected loss from the trees left standing.
- Nobody knows which trees these are. The 117 is the sum of the probabilities p over the 3,516 trees left standing.
- In this example, every tree left standing has a p below its break-even probability. Felling any of them would cost more than it saves, on average.
- The list has an expected net saving of CHF 9,086. Without any felling, the expected loss would be CHF 9,086 higher.

### Choose the next field checks

Before felling starts, a forester can check M more district trees for bore dust. `facts.yaml` gives M. Which trees should the forester check?

- Choose among the trees without a bore-dust result.
- A check is worth doing only if its result can change your decision for that tree.
- Rank the trees by the value of the check in CHF:
  - The expected loss of a decision is F if you fell the tree, and p × (L × V + S) if you leave it standing. The better decision is the one with the smaller expected loss.
  - The value of the check is the expected loss of the better decision now, minus the expected loss of the better decision after the check.
  - For the second term, update p for each result as in Task 4, Step 2. Weight the two results by their probabilities.
- Ignore the crew limit K for this question.
- Write the M trees with the highest value to `check_list.csv`. Explain your ranking.
- Show the felled trees and the trees to check on one map of the district.

**Discussion.** In your report, close this task with 2–3 sentences: what did you learn in this task, and which of your choices are you least sure of?

**Class material:** W2 Random Variables · W3 Bayes' rule · W9 Classifier evaluation

---

## What you hand in

### 1. A script `predict.py` that the forest office can run again on new data

- Hand in one folder with `predict.py`, the code that fits your models, your saved models, `pyproject.toml` and `uv.lock`.
- In this folder, the call `uv run predict.py <district file> <facts file>` writes `felling_list.csv` and `check_list.csv` into the folder. The two arguments are the paths of the input files. Example: `uv run predict.py ../test/district_trees.csv ../facts.yaml`.
- The script reads all numbers from `facts.yaml`. It may load models that you saved before.
- The script must run on a new file with the same columns and the same kinds of data problems.
- Fix the random seeds in your code, so that the script gives the same results every time it runs.
- Write the numbers unrounded. The lecturers recompute `p_prior`, `p` and `fell` from your own numbers, with a small tolerance.

**`felling_list.csv`** has one row per district tree and these columns:

| Column | Content |
|---|---|
| `tree_id` | As in the input file |
| `east`, `north`, `aspect`, `diameter_cm`, `height_m` | The values after your cleaning (Task 1) |
| `biomass_kg` | Predicted biomass in kg (Task 2) |
| `V` | Timber value in CHF |
| `p_model` | Probability from your model (Task 3) |
| `p_prior` | Probability after Step 1 of Task 4 |
| `p` | Probability after Step 2 of Task 4. For trees without a bore-dust check, it equals `p_prior`. |
| `fell` | 1 if the crew fells the tree, otherwise 0 |

**Example:** three lines of `felling_list.csv` for another district. The second and the third tree are felled. The third tree had a bore-dust check with dust found, so its `p` is larger than its `p_prior`.

```csv
tree_id,east,north,aspect,diameter_cm,height_m,biomass_kg,V,p_model,p_prior,p,fell
T532991,2691972.2,1217009.2,E,24.5,21.1,251.31167164870683,42.722984180280164,0.7960937983359188,0.21057679193738296,0.21057679193738296,0
T908138,2690258.5,1217290.9,E,61.8,47.5,3848.7543895865197,654.2882462297084,0.9328719208980967,0.48704200211620086,0.48704200211620086,1
T520256,2690356.5,1217312.5,E,38.2,33.7,1009.9950126291611,171.6991521469574,0.5223274051453263,0.06951651107751362,0.5413726624588432,1
```

**`check_list.csv`** has M rows, ranked from first to last, with the columns `tree_id` and `value`: the value of the check in CHF (Task 5).

**Example:** the first three lines of `check_list.csv` for another district.

```csv
tree_id,value
T580213,54.403483800210665
T361400,52.60679425244152
T410374,52.543758228428594
```

### 2. A report of at most 8 A4 pages, as PDF, figures included

Body text in 12 pt; tables, captions and text in figures at least 10 pt. The examiners prepare the oral with your report. Use these sections:

1. **Recommendation.** For the forest office, in a few sentences: how many trees to fell, the expected net saving, the expected loss from the trees left standing, and which trees to check next.
2. **Exploratory data analysis.** The statistics and key plots of Task 1, Step 1, for the cleaned `train/` data.
3. **Data problems and cleaning.** Each problem you found, its evidence in the raw data, and how your pipeline handles it.
4. **Timber value.** Your answers to Task 2.
5. **Infestation probability.** Your answers to Task 3.
6. **Correcting the probabilities.** Your answers to Task 4, including the tree diagram.
7. **Decision and field checks.** Your answers to Task 5, including the expected-loss table and the what-if questions.
8. **`test/` compared with `train/`.** The table from "Compare `test/` with `train/`" in the Data section, with your explanation.
9. **Limitations.** What limits your pipeline as a whole, and what you would check next.
10. **AI use.** Which AI tools you used, and for which steps.

End each of sections 3 to 7 with the short discussion of its task (Tasks 1 to 5): 2–3 sentences on what you learned and which of your choices you are least sure of.

Give each figure a caption. Label the axes, with units.

**Optional appendix.** You may add figures or analyses that you want to keep but that are not part of the report. Put them in an appendix at the end of the same PDF. The appendix does not count toward the 8 pages. The examiners read only the 8 pages of the report, not the appendix. The oral does not use the appendix.

### 3. A 15-minute oral exam (see below)

On `test_exam/`, the lecturers compare your two output files with the true values. They measure:

- which data problems your script repairs,
- the biomass error in kg, for all trees and for the largest trees,
- AUC and log-loss of `p_model`,
- whether `p_prior`, `p` and `fell` follow from your own numbers as Tasks 4 and 5 say,
- the expected loss that your check list saves, computed from your own `p` and `V`,
- the loss of your felling list: the total of your expected-loss table (Task 5), computed with the true infestation probability and the true value of each tree. Only the lecturers know these.

The lecturers compute these results before the oral and may ask you about them.

### The oral

- The examiners may ask general questions about your pipeline and the methods you used.
- They ask about your district's data and your results.
- Before the oral, the lecturers run your script unchanged on `test_exam/`. This checks whether your script runs on new data and whether your results hold there.

---

*The districts and their data are fictional, but modelled on real spruce forests and bark beetle outbreaks.*

*Photos: Rabenklippe im Harz mit Waldschäden by Fährtenleser, CC BY-SA 4.0, via Wikimedia Commons. Ips typographus by Francisco Welter-Schultes, CC0, via Wikimedia Commons. Both images resized.*
