# Status of the analyses requested in review (v1.1 / deposit v19.0)

| Item | Status | Where |
|---|---|---|
| 99-gene five-column table (S2b) | done | 04_modules/module_definitions_five_column.csv |
| Pancreatic de-duplication | done | 07_estimates/paad_dedup_mapping.csv, 01_cohort_registry/cohort_registry.csv |
| Tables derived from the estimates layer | done | 07_estimates/meta_primary_reml_knha.csv, 08_qc/qc_cross_cohort_consistency.csv, 08_qc/qc_coverage_threshold_sensitivity.csv |
| Full independent reproduction of the effect layer | done at score level | 08_qc/independent_reproduction_effects.csv |
| Monte Carlo aligned to the RMS estimand | done | 08_qc/mc_target_alignment.csv |
| Single-cell layer recomputation | not done | requires cell-level matrices (not in the deposit) plus Seurat/scanpy on the release machine |
| xCell with rnaseq = FALSE | not done | requires the 26 expression matrices plus R/xCell; no Windows binary and the source build needs a full toolchain |

Items marked not done are documented as not done; they are not silently unchanged, and no
number in the deposit depends on them.
