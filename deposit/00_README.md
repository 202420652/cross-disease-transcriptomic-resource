# Cross-disease growth-factor and tissue-composition transcriptomic resource (v20.0)

This directory **is** the data deposit described in the manuscript. It is shipped
as the `deposit/` folder of the GitHub repository
<https://github.com/202420652/cross-disease-transcriptomic-resource>, release tag
`v1.2`; every path quoted in the manuscript is relative to the repository root
(for example `03_expression/` is `deposit/03_expression/` in the repository).
The version of this package is recorded in `00_VERSION.txt` (v20.0, released
2026-11-10), and the mapping between the deposit version and the repository
release is given in `00_CHANGELOG.md`.

**Licence**
- Derivative data in this package (annotations, scores, coverage tables, estimates, quality-control records): **CC-BY-4.0** — full text in `../LICENSE-DATA` at the repository root.
- Code: MIT — `../LICENSE` at the repository root for the maintained code in `src/`, `R/`, `scripts/` and `tests/`; the original pipeline in `11_code/` is released under the same MIT licence.
- Upstream data remain under the terms of their original repositories (GEO, TCGA/GDC via cBioPortal, CELLxGENE). Accessions and origin publications are listed in `01_cohort_registry/`.

**How to cite**
Cite the Data Descriptor and this resource. The resource is citable through the
GitHub repository at the release tag `v1.2`. The archive is issued by Zenodo under
the concept DOI `10.5281/zenodo.24083603`, which always resolves to the latest
version; the version DOI of a given release is printed on that record page. Cite the
primary sources listed in `01_cohort_registry/` for the underlying measurements.

## What is in the package

| Folder | Contents | Key files |
|---|---|---|
| 01_cohort_registry | cohort registry, provenance, source versions and CELLxGENE identifiers | `cohort_registry.csv`, `source_versions.csv`, `cellxgene_sources.csv`, `TableS1_accessions.csv`, `TableS1b_cohort_pubmed_map.csv` |
| 02_sample_annotation | sample-level annotation for the GEO cohorts and the squamous oesophageal TCGA subset | `sample_annotation_geo_cohorts.csv`, `sample_annotation_escc_squamous_tcga.csv` |
| 03_expression | gene-mapping and transformation provenance (processed matrices are regenerated from the public accessions listed in 01) | `transformation_log.csv` |
| 04_modules | frozen module definitions, per-platform coverage, sample-level scores | `module_definitions.csv`, `platform_module_coverage.csv`, `sample_module_scores_gsva_z.csv` |
| 05_composition | expression-derived composition scores | `xcell_composition_scores.csv` |
| 06_single_cell | dataset audit, raw/curated label notes, donor-aware comparisons | `single_cell_dataset_audit.csv`, `single_cell_comparisons.csv` |
| 07_estimates | complete estimates layer, including non-significant and non-estimable results | `per_cohort_effects.csv`, `meta_*.csv`, `composition_model_summary.csv`, `driver_interactions.csv`, `external_validation_crc.csv`, `tcga_escc_squamous_*.csv` |
| 08_qc | coverage, exclusions, validation and layout checks | `platform_module_coverage.csv`, `exclusion_and_flag_log.csv`, `qc_*` tables, `curation_flow.csv`, `file_inventory_and_checksums.csv`, `checksums_sha256.txt` |
| 09_reuse_examples | three runnable reuse examples with expected outputs | `example1_replace_module_gene_set.R`, `example2_recompute_composition_scheme.R` |
| 11_code | analysis scripts and their README (see README_code.md) |
| 10_environment | software versions and run order | `environment.txt`, `run_order.md` |

## Field dictionary (main tables)

`02_sample_annotation/sample_annotation_geo_cohorts.csv`
| field | meaning |
|---|---|
| accession | GEO series accession |
| sample_id | within-cohort sample identifier (GSM) |
| patient_id | patient identifier; equals `sample_id` when the source provides no separate patient field |
| group | source case/control label as recorded in the processed series |
| case_control_role | normalised role (`case`, `control`, `unknown`) |
| paired_with | `patient_id\|paired` when the patient contributes both case and control samples |
| platform | platform annotation of the series |

`04_modules/sample_module_scores_gsva_z.csv`
| field | meaning |
|---|---|
| accession, sample_id | join keys to the annotation table |
| <module names> | GSVA scores computed within the cohort and z-scored **within that cohort**. Values are comparable within a cohort; across cohorts use `07_estimates/per_cohort_effects.csv` (standardized effect sizes) |

`06_single_cell/single_cell_comparisons.csv`
| field | meaning |
|---|---|
| context, module, cell_type | dataset, module and cell type compared |
| comparison_type | `tumour-vs-adjacent`, `tumour-vs-healthy`, `case-vs-healthy` or `cell-identity` |
| n_donors_a, n_donors_b, n_overlap_donors, n_pairs | donors per arm, donors present in both arms, complete pairs used |
| test_used | `wilcoxon-signed-rank (paired donors)`, `mann-whitney (donor-disjoint)` or `not testable` |
| p_used, fdr | p-value and BH-FDR within the context x module x comparison-type family |

`07_estimates/per_cohort_effects.csv`
| field | meaning |
|---|---|
| measure | `SMDH` (unpaired) or `SMCRPH` (paired, empirical within-pair correlation); both use the root-mean-variance denominator |
| yi, vi | standardized effect and its sampling variance |
| beta_base, beta_adj, se_*, p_* | disease coefficients from the composition **base** and **adjusted** models on identical samples |
| r_emp, npair | empirical within-pair correlation and number of pairs (paired cohorts) |

## Scoring layers are not interchangeable
- bulk GSVA z-scores (`04_modules`) — cohort-internal
- member-mean z-scores (TCGA layer, `07_estimates`)
- single-cell member-mean expression (`06_single_cell`)
These are different quantities and must not be concatenated into one matrix.

## What is deliberately excluded
See `08_qc/exclusion_and_flag_log.csv`: 89 adenocarcinoma samples excluded from the squamous oesophageal layer; 1,277 in utero cells excluded; a tumour-only single-cell dataset (117,266 cells) excluded for having no control arm; 358 malignant-labelled cells in non-tumour colorectal samples flagged but not reassigned; 80 single-cell comparisons reported as not testable because donors overlap between arms without forming five complete pairs.

## Known limitations
Module gene coverage is incomplete in part of the cohorts (worst case: RET/ALK/NTRK modules down to 33% of members in one platform). Composition scores are enrichment scores, not cell proportions. Cohort count is not patient count: 27 curated series contain 26 case-control cohorts, of which 17 provide patient identifiers and 9 do not. One cohort (GSE62452) is a patient-level duplicate of GSE28735 and is held out of pooling, so the estimates layer covers 25 accessions and 2,627 samples; 1,044 is the number of patients with identifiers that enter the estimates layer (1,086 delivered) (the patient count of the remaining 9 cohorts is unknown, not one). The resource is not a patient-level multi-omics resource: the same disease label in different layers does not imply the same patients. Control tissue differs between cohorts and is classified in 01_cohort_registry/contrast_ontology.csv (adjacent non-tumour, non-inflamed, healthy donor, non-diseased); classes are not pooled silently. One cohort (GSE62232, hepatocellular carcinoma) contributes only five control samples, so its control-side variance is estimated from very few samples. Zero-variance genes are absent by construction (matrices were filtered before scoring), which is why the QC column reports zero for every cohort. Module scores are not validated prognostic or predictive tools.

## Which score layer to use
| Question | Layer | File | Notes |
|---|---|---|---|
| Does a module differ between case and control within this cohort? | bulk GSVA z-scores | `04_modules/sample_module_scores_gsva_z.csv` | cohort-internal; cross-cohort only as effect sizes |
| Does a module differ across tumour contexts at patient level? | TCGA member-mean z-scores | `07_estimates/per_cohort_effects.csv` (TCGA context rows) + `tcga_patient_module_scores.csv` | construction rule in Methods |
| Does a module differ between cell types or within a cell type between conditions? | single-cell member means | `06_single_cell/` | donor-level means tested, not cells |
| Is tissue composition a confounder here? | xCell compartment scores | `05_composition/composition_scores_per_sample.csv` | enrichment scores, not proportions; shares genes with module scores -> sensitivity analysis only |

## Versioning and maintenance
The deposit carries a version number (`00_VERSION.txt`) and a changelog (`00_CHANGELOG.md`). Updates are published as new tagged releases of the GitHub repository, so earlier releases remain accessible and citable; `00_CHANGELOG.md` and the repository-level `CHANGELOG.md` record the version history. The frozen module configuration is identified by `module_version` in `04_modules/module_definitions.csv`; the analysis code is shipped in `11_code/` (the original pipeline, preserved unchanged) and maintained as the reusable implementation in the repository's `src/`, `R/`, `scripts/` and `tests/` directories.

## CSV encoding
All CSV files are UTF-8 without a byte-order mark. The `rows` column of `08_qc/file_inventory_and_checksums.csv` counts data rows (header excluded), and the two verification files record their own pre-finalisation hashes (a self-reference note is given in `checksums_sha256.txt`).

## Licence compliance
Derived data in this package are released under CC-BY-4.0 by the authors of this resource. Upstream data remain under their own terms: GEO series terms as declared by each submitter, TCGA/GDC open-access terms (no controlled-access data were used), and CELLxGENE dataset terms. Redistributing source matrices requires observing those upstream terms; see `01_cohort_registry/source_versions.csv`.

Verification: `08_qc/checksums_sha256.txt` covers every data file and does not contain itself; the digest of the manifest files is recorded in `08_qc/manifest_checksum.txt`. Run `sha256sum -c 08_qc/checksums_sha256.txt` from the deposit root.
