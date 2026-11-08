# File manifest — 文件名及用途清单

All paths are relative to the repository root. Reference CSVs under
`data/reference/` were exported verbatim from the manuscript's Tables
document; per-table provenance (source block, title, scope, row/column
counts) is machine-readable in `data/reference/table_manifest.json`.

## Root

| File | Purpose |
|---|---|
| `README.md` | Repository overview, provenance/scope statement, quickstart, conventions |
| `LICENSE` | MIT licence (as declared in the manuscript's Code Availability) |
| `config.yml` | Path configuration (`root_dir` → deposit) and the pre-specified analysis settings |
| `environment.txt` | Pinned software environment (R 4.4.1 + GSVA 1.52.3, metafor 5.0.1, xCell 1.1.0, …; Python 3.11) |
| `requirements.txt` | Minimal Python dependencies |
| `pyproject.toml` | Installable package definition for `src/cdtr` |
| `.gitignore` | Excludes caches and recomputed outputs |
| `.github/workflows/ci.yml` | CI: pytest + reference-table consistency check on Python 3.11 |

## Python validation layer — `src/cdtr/`

| File | Purpose |
|---|---|
| `effect_sizes.py` | SMDH / SMCRPH with shared RMS-SD denominator, exact gamma bias correction J, Bonett heteroscedastic LS variance |
| `meta_analysis.py` | REML + Hartung–Knapp pooling (independent numerical implementation), BH adjustment, Wilson interval, direction consistency |
| `scoring.py` | Module coverage, member-mean + cohort z-score rules, TCGA layer, single-cell scoring, marker-proxy panels, expression-scale flags |
| `single_cell.py` | Donor-level comparison design rules; legacy signed-median / capped bootstrap (reproduction only) and the required revision paths |
| `design.py` | Metadata-derived paired/unpaired decision (≥4 complete pairs) and measure/sample-count mapping |
| `__init__.py` | Public API |

## R pipeline — `R/` (requires the data deposit; fails explicitly without it)

| File | Purpose |
|---|---|
| `config.R` | Shared config loading and deposit-path resolution |
| `01_score_bulk_gsva.R` | Bulk layer: GSVA 1.52.3, `gsvaParam`, `kcdf="Gaussian"`, `minSize=3`, within-cohort z |
| `02_tcga_scores.R` | TCGA layer: patient-level member-mean z within tumour context |
| `03_effects_escalc.R` | metafor 5.0.1 `escalc` SMDH/SMCRPH, `vtype="LS"`, empirical-r + fixed-r sensitivity |
| `04_pool_metafor.R` | `rma.uni` REML + Hartung–Knapp, k≥2 rule, k=2 annotation, PI for k≥3, BH within context; design-stratified secondary table |
| `05_xcell_composition.R` | xCell 1.1.0 compartment scores as shipped (`rnaseq=TRUE`) plus the required platform-matched sensitivity variant |
| `06_tcga_survival.R` | OS Cox models (univariate + age/stage-adjusted), driver-eligibility floor (≥10 positives) |
| `run_all.R` | Executes steps in order (mirrors the deposit's `run_order.md`) |

## Scripts and tools

| File | Purpose |
|---|---|
| `scripts/validate_reference_tables.py` | Structural consistency checks on `data/reference/` (26 cohorts/10 contexts, 17 modules/99 genes, 312 S25 rows, subset markers, manifest coverage) |
| `scripts/verify_independent_implementation.py` | Monte Carlo check of the SMDH closed-form variance (mirrors S27, with the standardisation-target caveat documented) |
| `tools/export_docx_tables.py` | The verbatim cell-level exporter used to build `data/reference/` from Tables.docx |

## Tests — `tests/`

| File | Purpose |
|---|---|
| `test_effect_sizes.py` | Hand-computed SMDH/SMCRPH point estimates and variances, J(18) |
| `test_meta_analysis.py` | BH, Wilson, pooling behaviour (incl. k=2 annotation), direction consistency |
| `test_scoring.py` | Coverage, member floors, z-standardisation, single-cell normalisation, expression-scale flags |
| `test_single_cell.py` | Donor rules, legacy vs revision statistics, bootstrap reproducibility |
| `test_design.py` | Paired/unpaired thresholds and sample-count mapping |
| `test_reference_tables.py` | Runs the reference-table consistency checks as a test |

## Examples — `examples/`

| File | Purpose |
|---|---|
| `example1_gse13911_walkthrough.py` | Usage-notes walkthrough against the printed reference tables; reproduces the manuscript's anchor values |
| `example2_custom_geneset.py` | Custom/overlapping gene-set scoring (documented reuse path) |
| `example3_external_cohort_template.py` | External-cohort template (GSE54129-style); fails explicitly without inputs |
| `README_examples.md` | What each example does and its expected anchors |

## Data

| File | Purpose |
|---|---|
| `data/reference/*.csv` (36 files) | Printed tables S1–S32 and Tables 1–3, verbatim; `first80`/`first60`/`first12` in a name marks a printed subset, not complete data |
| `data/reference/table_manifest.json` | Per-table provenance incl. source SHA-256 and value policy |
| `data/placeholders/README.md` | Inventory of inputs that exist only in the deposit (nothing fabricated) |

## Docs

| File | Purpose |
|---|---|
| `docs/methodology_notes.md` | Rules, formulas, thresholds and parameters with manuscript section references |
| `docs/known_limitations.md` | The manuscript's limitations plus unresolved computational items (S27 labelling, SMCRPH full-precision inputs, original scripts) |
| `docs/file_manifest.md` | This list |
