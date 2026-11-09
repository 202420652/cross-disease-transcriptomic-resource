# Run order for the shipped scripts (`11_code/`)

The scripts were run in this order; paths inside them point to the author's working directories and must be
adjusted to the deposit layout (all inputs they need are shipped in this deposit except the raw source matrices,
which are downloaded from the accessions in `01_cohort_registry/`).

| step | script | produces |
|---|---|---|
| 1 | `41_v12_effects_meta.R` | per-cohort effects, pooled estimates, sensitivity meta-analyses |
| 2 | `40_v12_common_gene_sensitivity.R` | common-gene sensitivity of module scoring |
| 3 | `42_v12_audit_ph_collinearity.R` | proportional-hazards check and collinearity diagnostics |
| 4 | `43_v12_composition_keys.R` | composition keying and join audit |
| 5 | `22_v12_sc_reanalysis.py` | single-cell donor-aware comparisons (run with the single-cell environment) |
| 6 | `66_v14_marker_proxy_qc.R` | marker-based composition alternative and expression QC |
| 7 | `65_v14_analysis_additions.py` | module overlap matrix, control ontology, overlap audits, coverage columns |
| 8 | `93_v14_sc_sensitivity.py` | single-cell minimum-cells-per-donor and multiplicity sensitivities |
| 9 | `60_v14_figures.R` | the four figures (PNG and cairo PDF) |
| 10 | `64_v14_figure_qa_final.py`, `77_v14_figure_review.py` | figure layout and legibility reviews |
| 11 | `70_v14_manuscript.py`, `71_v14_tables_legends.py` | manuscript and table documents |
| 12 | `76_v14_external_reuse_example.R` | external-cohort reuse example (GSE54129) |
