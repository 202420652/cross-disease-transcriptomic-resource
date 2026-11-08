# Placeholder inventory — inputs that are NOT in this repository

This repository was extracted from the manuscript submission package
(manuscript, Tables 1–3, Supplementary Information PDF, five figures). The
submission package did **not** include the data deposit or the original
pipeline scripts. Everything listed below must come from the deposit (Zenodo,
DOI reserved at the time of submission: https://doi.org/10.5281/zenodo.XXXXXXX)
or from the analysis-code repository cited in the manuscript
(https://github.com/202420652/cross-disease-transcriptomic-resource, tag v1.0). Nothing here is reconstructed by guesswork; code that needs these
inputs stops with an explicit error instead of fabricating values.

| Missing input | Deposit location | Needed by |
|---|---|---|
| 99-gene module membership with role/source annotation | `04_modules/module_definitions.csv` | all scoring steps (module sizes and names are known from the manuscript; individual gene identities are not printed) |
| Per-cohort processed expression matrices (26 cohorts, TCGA contexts) | `03_expression/` | R steps 01, 02, 05 |
| Sample annotation (case/control, pairing, exclusions) | `02_sample_annotation/` | R step 03 |
| Full-precision per-cohort effects (`r_emp`, `npair`, member counts) | `07_estimates/per_cohort_effects.csv` | internal reproducibility of the estimates layer |
| Full-precision SMCRPH inputs (per-pair values behind `r_emp`) | deposit | the paired effect layer cannot be re-derived from printed summaries |
| Complete S26 sensitivity table (165 rows; printed: first 80) | `07_estimates/meta_classic_denominator_sensitivity.csv` | sensitivity comparison |
| Complete S29 single-cell donor effects (208 rows; printed: first 60) | `06_single_cell/single_cell_donor_level_effects_with_ci.csv` | single-cell layer |
| Patient-level OS annotation, driver alteration calls, module scores | deposit | R step 06 |
| Single-cell count matrices (CELLxGENE collections + GSE193816) | upstream only | `cdtr.single_cell` on real data |
| `manifest_checksum.txt`, `file_inventory_and_checksums.csv` | `08_qc/` | checksum verification of the deposit |
| Original `11_code/` scripts and `sessionInfo.txt` | deposit / original repo | byte-level internal reproducibility |

## Printed subsets shipped here

The following reference tables are **printed subsets**, marked in the file
name; do not treat them as complete data:

- `s26_classic_denominator_sensitivity_first80.csv` — first 80 of 165 rows
- `s29_single_cell_donor_effects_first60.csv` — first 60 of 208 rows
- `s19_discordant_pairs_first12.csv` — first 12 rows

All other `s*.csv` / `table*.csv` files in `data/reference/` are complete
printed tables, exported verbatim (cell text unchanged) from the
manuscript's Tables document; provenance is recorded in
`data/reference/table_manifest.json` (source SHA-256 included).
