# Release v1.1 - pancreatic patient-level de-duplication (deposit v19.0)

Release date: 2026-11-10
Supersedes: v1.0 (2026-11-09, version DOI 10.5281/zenodo.24083604); concept DOI 10.5281/zenodo.24083603

## What changed

1. **Patient-level de-duplication of the pancreatic accessions.**
   GSE62452 and GSE28735 are the same patients. Using the patient-specific
   tumour-minus-adjacent expression profile on the 28,869 shared GPL6244 probes,
   all 42 patients of GSE62452 matched a distinct patient of GSE28735 one to one
   (profile r median 0.996, range 0.980-0.998; within-cohort baseline median 0.18,
   maximum 0.81). GSE15471 (GPL570) has no counterpart (best one-to-one r 0.73) and
   remains independent. GSE62452 stays in the deposit as data
   (`in_estimates_layer = no`, `duplicate_of = GSE28735`) and enters no pooled estimate.

2. **Counts revised** (before -> after). The delivered resource and the estimates
   layer are now reported separately, because a delivered cohort can be held out of
   pooling:
   - accessions delivered: 26 (unchanged); accessions in the estimates layer: 26 -> 25
   - samples: 2,711 delivered, 2,627 in the estimates layer
   - unique patients with identifiers: 1,086 delivered, 1,044 in the estimates layer
   - cohort-module pairs: 442 delivered, 425 in the estimates layer, of which 418 are
     estimable (183 SMDH + 235 SMCRPH) and 7 are not estimable
   - PAAD context: 3 accessions / 123 patients -> 2 accessions / 81 patients

3. **Every table derived from the estimates layer re-estimated.**
   `07_estimates/meta_primary_reml_knha.csv` (170 states: 165 with k >= 2, of which 82
   now rest on exactly two cohorts and 83 on three, against 66 and 99 before);
   `08_qc/qc_cross_cohort_consistency.csv` (fully concordant states at k >= 3 fall from
   67/99 to 57/83; the k >= 2 fraction is 112/165 before and after);
   `08_qc/qc_coverage_threshold_sensitivity.csv` (BH-significant states 13, 13, 12, 6 ->
   12, 12, 9, 6 at no threshold and at coverage 0.60, 0.80, 0.90; the number of pooled
   states is unchanged at 165, 165, 147, 130). The pre-deduplication PAAD table is kept
   as `07_estimates/paad_meta_before_dedup.csv`.

4. **New files**
   - `07_estimates/paad_dedup_mapping.csv` - the 42 one-to-one patient matches
   - `07_estimates/paad_meta_before_dedup.csv`, `paad_meta_after_dedup.csv` - PAAD states
     before and after removal
   - `01_cohort_registry/paad_sample_metadata.csv` - per-sample tissue and patient labels
     for the three pancreatic accessions, as parsed from the GEO series matrices
   - `08_qc/paad_cross_accession_correlation.csv` - the cross-accession profile correlations
   - `04_modules/module_definitions_five_column.csv` - the 99 genes with role, KEGG source
     pathway and arbitration basis (Supplementary Table S2b)
   - `08_qc/independent_reproduction_effects.csv`, `independent_reproduction_by_cohort.csv` -
     all 434 estimable pairs of the delivered set recomputed from the delivered score matrix
     (183 unpaired exact to 2e-6; 251 paired reproduced to a median 2.0e-4 under the
     implemented df = 2(n-1) convention, which the reproduction identifies)
   - `08_qc/sensitivity_paired_df.csv` - paired effects under df = n-1 versus 2(n-1)
     (median change 0.9%, no sign flips)
   - `08_qc/mc_target_alignment.csv` - Monte Carlo with the target set to the
     RMS-standardised estimand, including the unbalanced 81-versus-5 design and paired data
   - `08_qc/release_v1_1_summary_numbers.json` - every count quoted in this changelog

## What did not change

- Module definitions, the frozen module set, the score matrices and the sample annotation.
- The single-cell and xCell layers. The xCell recomputation with rnaseq = FALSE is still
  outstanding: no Windows binary exists for the release machine and the source build needs a
  full toolchain (see README_status_v1_1.md). It is reported as not done, not as unchanged.
