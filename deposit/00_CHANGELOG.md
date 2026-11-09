# Changelog

This changelog records the version history of the deposit. Deposit v18.0 is the
version released as tag `v1.0` of the GitHub repository
<https://github.com/202420652/cross-disease-transcriptomic-resource>; the
repository-level `CHANGELOG.md` is the release-notes file for that tag and lists
what the release contains.

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
