# Reuse examples

The manuscript ships three reuse examples (deposit folder `09_reuse_examples/`
with `expected_output/`). The corresponding scripts in this repository:

| File | What it does | Runs standalone? |
|---|---|---|
| `example1_gse13911_walkthrough.py` | The GSE13911 usage-notes walkthrough (steps 1, 3, 5) against the printed reference tables in `data/reference/`. | Yes |
| `example2_custom_geneset.py` | Re-score a synthetic matrix with a custom, overlapping gene set (the resource's modules are mutually exclusive by design; this is the documented way to use your own sets). | Yes |
| `example3_external_cohort_template.py` | Template for scoring one external cohort (the manuscript used GSE54129; runtime 1.6 min, direction agreement 9/17 modules reported as reuse-cost metrics, not validation). | No — requires inputs, fails explicitly without them |

Expected anchor values for example 1 (from the manuscript text): GSE13911 /
EPH_RECEPTORS per-cohort effect 1.72 (SMCRPH, 31 complete pairs); pooled
gastric state 1.57, k = 3, BH-adjusted p = 0.124.

The held-out series GSE39582 (556 colorectal samples, survival-eligible
tumour subset) is a second reuse demonstration with per-module Cox models —
a held-out reuse test, not an external validation of the effect layer.
