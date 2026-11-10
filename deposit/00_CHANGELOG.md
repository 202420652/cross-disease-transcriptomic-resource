# Changelog

This changelog records the version history of the deposit. Deposit v19.0 is the
version released as tag `v1.1` and deposit v18.0 was released as tag `v1.0` of the GitHub repository
<https://github.com/202420652/cross-disease-transcriptomic-resource>; the
repository-level `CHANGELOG.md` is the release-notes file for that tag and lists
what the release contains.

## v19.0 (2026-11-10)
- patient-level de-duplication of the pancreatic accessions: GSE62452 and GSE28735 are the same
  patients. The patient-specific tumour-minus-adjacent profile on 28,869 shared GPL6244 probes
  matched 42 of 42 GSE62452 patients one to one (r median 0.996, range 0.980-0.998; within-cohort
  baseline median 0.18, maximum 0.81). GSE15471 (GPL570) has no counterpart (best one-to-one r 0.73)
- GSE62452 stays in the deposit as data and enters no pooled estimate
  (01_cohort_registry/cohort_registry.csv: in_estimates_layer = no, duplicate_of = GSE28735,
  exclusion_reason; 07_estimates/per_cohort_effects.csv carries the same row-level flag)
- re-estimate 07_estimates/meta_primary_reml_knha.csv on the 25-cohort estimates layer
  (170 states, 165 with k >= 2: 82 with k = 2 and 83 with k = 3, against 66 and 99 before)
- regenerate 08_qc/qc_cross_cohort_consistency.csv and
  08_qc/qc_coverage_threshold_sensitivity.csv on the same layer: fully concordant states at
  k >= 3 fall from 67/99 to 57/83 (one-sided binomial p = 7.7e-17 against the 0.25 baseline),
  the k >= 2 fraction stays 112/165, and BH-significant states fall from 13, 13, 12, 6 to
  12, 12, 9, 6 at no threshold and at coverage 0.60, 0.80 and 0.90
- add 07_estimates/paad_dedup_mapping.csv (42 one-to-one patient matches),
  08_qc/paad_cross_accession_correlation.csv, 01_cohort_registry/paad_sample_metadata.csv,
  08_qc/independent_reproduction_effects.csv and _by_cohort.csv (all 434 estimable pairs of the
  delivered set recomputed from the score matrix: 183 unpaired to 2e-6, 251 paired to 2e-4 median
  under the implemented df = 2(n-1) convention), 08_qc/sensitivity_paired_df.csv,
  08_qc/mc_target_alignment.csv, 08_qc/release_v1_1_summary_numbers.json,
  04_modules/module_definitions_five_column.csv (the 99 genes with role, KEGG source pathway and
  arbitration basis)
- regenerate the three integrity manifests over the new file set

## v18.0 (2026-11-05)
- regenerate 07_estimates/meta_by_design_stratum.csv from the frozen per-cohort effects under the primary rule
  (REML + Hartung-Knapp variance + t on k-1 df); all 165 all-cohort rows now reproduce the joint table
  (max |difference| 6.4e-6, print precision) and no shipped table mixes normal-approximation and t-based p values
- correct the documented sampling variance to the heteroscedastic large-sample variance of Bonett that the
  pipeline actually used (metafor escalc, SMDH, vtype LS); verify it against all 183 unpaired effects
  (max |difference| 1.1e-15) and re-run the Monte Carlo with 20 conditions including heteroscedastic and
  unbalanced designs (analytic/empirical variance ratio 0.98-1.13, mean 1.04; 95% coverage 91.2-97.2%)
- rebuild 08_qc/qc_independent_reimplementation.csv with four explicit states (PASS / FAIL / PARTIAL /
  NOT TESTED); add complete-family BH check (10 disease families, 165 states) and the variance identity check
- relabel 06_single_cell/single_cell_donor_cell_count_distribution.csv: the column named 'donors_total' held
  cell counts; it is now 'cells_total' and donor-level thresholds point to S17/S18
- add 08_qc/data_dictionary.csv (file, column, type, missingness, example, key flag, licence) generated from
  the shipped tables
- add 11_code/95_v18_regenerate_design_strata.py and 11_code/96_v18_variance_monte_carlo.py
- version metadata aligned with manuscript version 18.0
## v14.0 (2026-09-19)
- add single-cell sensitivity analyses (>=10 cells per donor; family versus joint multiplicity) and Supplementary Table S17
- single-cohort rows are labelled as not pooled throughout the meta tables
- analysis scripts shipped in 11_code/; figure QA notes shipped in 08_qc/
- run the external-cohort reuse example end to end (GSE54129, 111 tumour / 21 adjacent-normal samples; runtime 1.6 minutes)
- add module overlap matrix (maximum pairwise Jaccard 0.00), control-tissue ontology, per-cohort expression QC, deterministic transformation rule with summaries
- add study-level overlap audit, independent marker-based composition method and its agreement with xCell, and 95% prediction intervals
- reorder figures: Figure 4 (sensitivity analyses) added; all four figures rebuilt with label-overlap and clipping fixes
- version metadata aligned with the manuscript version

## v13.0 (2026-09-19)
- correct the mutation-prevalence denominator for the squamous oesophageal layer (185 profiles including 89 adenocarcinomas -> 96 squamous profiles); TP53 86/96 (89.6%), EGFR 2/96, KRAS 0/96, ERBB2 0/96
- add the complete cohort-by-module estimates matrix (442 rows = 434 estimated + 8 not estimable, each with a reason)
- add cross-cohort direction consistency per context-module pair (112 of 165 pairs, 68%, share the same sign in every cohort)
- add coverage-threshold sensitivity of the pooled results (BH-significant states: 13 / 13 / 12 / 6 at coverage 0.60 / 0.80 / 0.90)
- add module-versus-xCell signature overlap audit (all 17 modules share >20% of members with the xCell panel; maximum 100%) and reframe composition adjustment as a sensitivity analysis
- add per-predictor VIF within the disease-status model (median 2.09, maximum 4.53) alongside the overall model R-squared, with an explicit explanation of the difference
- state the score-construction rule for each layer and add a layer-selection table
- add curation-flow counts and the source-version/licence table
- separate exact reproduction from rank agreement in all validation statements

## v12.0
- pivot to a data-resource description; metadata-driven pairing; donor-aware single-cell design; complete estimates with negative results; SHA-256 inventory
