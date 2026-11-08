# Methodology notes (extracted from the manuscript)

Every rule below is transcribed from the manuscript or its tables; bracketed
references point at the source section. Nothing here is extrapolated.

## Design decisions [Methods, Design]

- A cohort is analysed as **paired** only when metadata establish **at least
  four complete patient pairs**; otherwise unpaired. GSE62232 (one
  both-tissue patient) and GSE87473 (none) are analysed as unpaired despite
  available patient identifiers [S32 note].
- Paired estimates use complete pairs only; unpaired estimates use all
  annotated samples [S32].

## Modules [Methods, Module definitions]

- 17 signalling modules, 99 genes, frozen at `module_version =
  v12.0-frozen-2026-09`; role annotation counts: ligand 22, receptor 36,
  core pathway 33, downstream 2, response gene 6.
- Mutually exclusive by construction (max pairwise Jaccard 0.00).
- `coverage(c, m) = |genes(m) ∩ retained(c)| / |genes(m)|`.
- A cohort–module pair with fewer than **3 retained members** is not scored
  and reported as not estimable (8 of 442 pairs; resource choice — GSVA
  `minSize` default is 1, the resource sets 3).
- Pre-specified coverage sensitivity thresholds: 0.60 / 0.80 / 0.90;
  poolable states 165/165/147/130 drawing on 429/428/382/335 cohort–module
  pairs.
- Common-gene sensitivity uses a **two-member floor** (pre-specified
  exception to minSize = 3).

## Score layers [Methods, Scoring rules; S8]

Three layers, **not on a common scale — never concatenate**:

1. **Bulk**: GSVA 1.52.3, `gsvaParam`, `kcdf = "Gaussian"`, `minSize = 3`,
   all other parameters at package defaults; per-sample scores z-standardised
   within each cohort. All 26 cohorts are microarray; no Poisson kernel used.
2. **TCGA**: patient-level member-mean, z-standardised within tumour context
   (ESCC squamous subset standardised within the subset).
3. **Single-cell**: library-size normalised to 10^4, log1p, per-cell member
   mean; covers 8 modules (EPH_RECEPTORS, WNT_CTNNB1, JAK_STAT,
   VEGF_PDGF_AXIS, HGF_MET_AXIS, SRC_FAK, ERBB_RECEPTORS, ERBB_LIGANDS).

The within-cohort z step does not affect the estimates layer: SMDH/SMCRPH
are invariant to within-cohort linear rescaling.

## Effect sizes [Methods, Effect-size definitions]

- metafor 5.0.1 `escalc`, `vtype = "LS"` (Bonett heteroscedastic
  large-sample variance), direction **case minus control**.
- SMDH (independent) and SMCRPH (paired) share the denominator
  `sdpi = sqrt((sd_case^2 + sd_control^2)/2)` and the exact gamma-function
  bias correction J.
- Unpaired variance:
  `v = y²·(s1⁴/(n1−1) + s2⁴/(n2−1))/(8·sdpi⁴) + (s1²/(n1−1) + s2²/(n2−1))/sdpi²`
  — explicitly **not** the homoscedastic approximation.
- Paired form: complete pairs + empirical within-pair correlation `r`
  (fixed value in the primary analysis; r = 0.5 and r = 0.7 as sensitivity).
- Classical-convention full sensitivity analysis: 163 of 165 pooled states
  keep direction; median |change| 0.014, max 0.49.

## Pooling and inference [Methods, Pooling and inference; Multiplicity control]

- `rma.uni`, REML + Hartung–Knapp (t on k − 1 df); pooled estimates only for
  k ≥ 2 (165 of 170 states; 66 rest on exactly two cohorts).
- k = 2: annotated "two-cohort summary; heterogeneity uninformative".
- 95% prediction intervals for k ≥ 3 (k = 3 intervals rest on 1 df, reported
  for completeness, not calibrated).
- Single-cohort states labelled "single cohort; not a pooled estimate", no
  p/CI/PI.
- BH within disease context (10 families, ≤ 17 states each) for the joint
  primary table; the design-stratified table forms separate families
  (per context × stratum) — adjusted values are not interchangeable.
- No shipped table mixes the normal approximation and the Hartung–Knapp t.
- Exact reproduction tolerance: absolute difference ≤ 1 × 10⁻⁶ on
  full-precision recomputation (not on printed-table comparisons).

## Composition [Methods, Composition scores]

- xCell 1.1.0 `xCellAnalysis(matrix)` with package defaults
  (`rnaseq = TRUE, scale = TRUE`); four direct outputs: "Epithelial cells",
  "Fibroblasts", "Endothelial cells", "ImmuneScore". Enrichment scores, not
  proportions; no aggregation or weighting.
- **Known deviation**: RNA-seq calibration used on microarray matrices;
  platform-matched (`rnaseq = FALSE, scale = TRUE, alpha = 0.5`)
  recomputation required before the layer is more than auxiliary; shipped
  results retained as a documented sensitivity version.
- 12 of 17 modules are fully inside the xCell signature gene universe (489
  signatures; remaining five at 75–89%).
- Marker-proxy alternative (not xCell, not a validation of xCell): epi =
  EPCAM/KRT18/KRT8/CDH1/KRT19; fib = COL1A1/COL1A2/COL3A1/DCN/LUM/FAP;
  end = PECAM1/VWF/CDH5/CLDN5/KDR; imm = PTPRC/CD3D/CD3E/CD19/MS4A1/LYZ/
  CD68/NKG7; mean of retained markers (min 2), then cohort z-score.

## Single-cell comparisons [Methods; S18; Limitations]

- Donor rules: ≥ 3 donors per arm; paired when ≥ 5 complete pairs;
  donor-disjoint arms unpaired; otherwise NOT TESTABLE. Cell-identity
  contrasts (same-donor cell types) are descriptive only.
- Legacy statistics retained for reproduction only: signed-median donor
  summary and capped bootstrap (resample size min(n, 12)) — neither is a
  standard two-sample summary; the required revision is the difference of
  group medians with donor-resampled full-n intervals, and donor-paired
  tests for cell-identity contrasts.
- The layer has no independent re-implementation record.

## Validation tiers [Technical Validation]

1. Internal reproducibility (same code, same frozen inputs) — never labelled
   independent verification.
2. Independent re-implementation (plain Python, shares no project code).
3. Rank-level agreement — always labelled as such.

Every record is PASS / FAIL / PARTIAL / NOT TESTED; a row never passes on a
partial comparison. Known NOT TESTED items include the second-pass
re-adjudication of sample labels and the pancreatic cross-accession
sample-overlap audit.
