# Known limitations and unresolved items

Transcribed from the manuscript's "Limitations of the resource" and Usage
Notes, plus the unresolved computational items. These are constraints on the
resource and on this code — do not silently "fix" them.

1. Comparability is limited to effect sizes; module scores are not on one
   common scale across diseases or across the three score layers.
2. 66 of 165 pooled states rest on exactly two cohorts ("two-cohort
   summaries", not meta-analytic estimates); prediction intervals for k = 3
   states rest on one degree of freedom.
3. 94 of 418 estimated pairs are scored from exactly three members;
   IGF_INSR_AXIS is reduced to 3 of 4 members in 17 of 25 cohorts; member
   counts must accompany any comparison.
4. Compartment scores share genes with module scores (12 of 17 modules fully
   inside the xCell signature universe); in an auxiliary regression the four
   compartment scores jointly explain up to 89% of the variance of disease
   status in some cohorts — composition adjustment is a sensitivity analysis,
   not an independent correction.
5. The empirical within-pair correlation used by SMCRPH is estimated from
   few pairs; its uncertainty is not propagated into pooled standard errors.
6. The single-cell layer is descriptive: small donor numbers, no minimum
   cells-per-donor filter in the primary analysis, signed-median donor
   summary instead of a difference of group medians, bootstrap resample size
   capped at 12, cell-identity contrasts treat non-independent donors as
   independent, significance counts depend on the multiplicity family, no
   independent re-implementation record, the asthma dataset contributed no
   testable comparison, and the lung dataset was excluded (tumour tissue
   only).
7. No new experiments, no prospective external validation; the held-out
   series GSE39582 is a reuse demonstration, not a validation; TCGA
   patient-level score reconstruction reaches rank agreement (Spearman
   0.95–0.98) rather than exact reproduction, exercised in three of six
   tumour contexts.
8. Screening was not logged as a systematic review (series accounting is
   reconciled in S21); the library-size-normalisation branch of the
   transformation rule was never exercised in this release and remains a
   specification; the Monte Carlo grid did not cover control arms as small
   as five samples.
9. xCell compartment scores were computed with RNA-seq calibration on
   microarray matrices; a platform-matched (`rnaseq = FALSE`) recomputation
   of all 26 cohorts is required before the compartment layer is more than
   an auxiliary annotation.

## Unresolved computational items (carried over, not fixed here)

- **S27 Monte Carlo labelling**: rows with unequal SDs label "True effect"
  with the raw mean difference rather than the standardised effect (hence
  mean estimates near 0.32 for a stated 0.5). The standardisation target of
  that simulation grid is under re-evaluation by the authors.
- **SMCRPH full-precision inputs** are not printed in the supplementary
  tables; the paired layer can only be re-derived from the deposit
  (`deposit/07_estimates/per_cohort_effects.csv`, columns `r_emp` and `npair`),
  not from the printed summaries in `data/reference/`.
- The original pipeline is shipped in `deposit/11_code/` and preserved
  unchanged; the R scripts in `R/` are faithful re-implementations of the
  documented calls, not copies of those files. The archive note
  (`deposit/11_code/00_ARCHIVE_NOTE.md`) lists the historical hard-coded
  strings that the preserved scripts still contain.
