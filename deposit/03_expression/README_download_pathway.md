# From public accession to module scores

`download_and_rebuild_one_series.R` is a runnable pathway for a single series: it downloads the series matrix from GEO, applies a log2 rule that mirrors the decision recorded for the curated cohorts (see transformation_log.csv), maps probes to gene symbols, collapses multiple probes by the mean, and scores the frozen module definitions shipped in `04_modules/`.

Run it from the package root:

```bash
Rscript 03_expression/download_and_rebuild_one_series.R GSE13911
```

Output is written to `09_reuse_examples/output_rebuilt/<accession>_module_scores_z.csv` and can be compared with the shipped per-sample scores (a fully worked comparison for three cohorts is in 08_qc/qc_module_score_and_effect_verification.csv). Processed expression matrices for the curated cohorts are **not** redistributed in this deposit: they are regenerated from the public accessions listed in `01_cohort_registry/` using this pathway, and the transformation decision for every curated cohort is recorded in `transformation_log.csv`.
