# Deposit input map — where every input lives

The data deposit described in the manuscript is shipped in this repository as
`deposit/` (eleven folders `01_cohort_registry/` … `11_code/`, deposit version
v19.0, released as tag `v1.1`). Everything the code needs is therefore present in
the repository; this file maps each input to its path so that a reader can go
straight from a script to the file it consumes.

| Input | Path (relative to `deposit/`) | Used by |
|---|---|---|
| 99-gene module membership with role and module version | `04_modules/module_definitions.csv` | all scoring steps; module sizes, names and individual gene identities |
| Frozen module coverage per platform | `04_modules/platform_module_coverage.csv` | coverage-aware filtering |
| Sample-level bulk GSVA z-scores | `04_modules/sample_module_scores_gsva_z.csv` | effect-size layer |
| Sample annotation (case/control, pairing, exclusions) | `02_sample_annotation/sample_annotation_geo_cohorts.csv`, `…_escc_squamous_tcga.csv` | `R/03_effects_escalc.R` |
| Per-cohort processed expression matrices | regenerated from `03_expression/source_download_manifest.csv` + `download_and_rebuild_one_series.R` | `R/01`, `R/02`, `R/05` |
| Full-precision per-cohort effects (`r_emp`, `npair`, member counts) | `07_estimates/per_cohort_effects.csv` (442 delivered rows; 425 in the estimates layer) | reproducibility of the estimates layer |
| Complete S26 sensitivity table (165 rows; the printed table in `data/reference/` is the first 80) | `07_estimates/meta_classic_denominator_sensitivity.csv` | sensitivity comparison |
| Complete S29 single-cell donor effects (208 rows; printed: first 60) | `06_single_cell/single_cell_donor_level_effects_with_ci.csv` | single-cell layer |
| Patient-level TCGA scores, OS annotation, driver calls | `07_estimates/tcga_patient_module_scores.csv`, `07_estimates/driver_interactions.csv`, `07_estimates/tcga_escc_squamous_survival_cox.csv` | `R/06_tcga_survival.R` |
| Single-cell count matrices (CELLxGENE collections + GSE193816) | upstream only, identified by `01_cohort_registry/cellxgene_sources.csv` | `cdtr.single_cell` on real data |
| File inventory, checksum list, manifest digest | `08_qc/file_inventory_and_checksums.csv`, `08_qc/checksums_sha256.txt`, `08_qc/manifest_checksum.txt` | integrity verification |
| Original pipeline scripts and run information | `11_code/`, `10_environment/run_order.md`, `11_code/sessionInfo.txt` | provenance of every deposited table |

Paths quoted in the manuscript are relative to the deposit root; in the
repository that root is `deposit/`. Scripts that read these files take the root
from `config.yml` (`root_dir`) and stop with an explicit error when a file is
absent — they never substitute a value.

## Printed subsets kept in `data/reference/`

`data/reference/` holds tables exported verbatim from `Tables.docx` (the printed
supplementary tables). Three of them are **printed subsets**, marked in the file
name; use the deposit files above for complete data:

- `s26_classic_denominator_sensitivity_first80.csv` — first 80 of 165 rows
- `s29_single_cell_donor_effects_first60.csv` — first 60 of 208 rows
- `s19_discordant_pairs_first12.csv` — first 12 rows

All other `s*.csv` / `table*.csv` files in `data/reference/` are complete printed
tables, cell text unchanged; provenance is recorded in
`data/reference/table_manifest.json` (source SHA-256 included).
