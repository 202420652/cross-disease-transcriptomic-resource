# Cross-disease case–control transcriptome resource — analysis code

Analysis and validation code extracted from the manuscript submission package
of *"A cross-disease case–control transcriptome resource with coverage-aware
signalling-module scores"* (submitted as a Data Descriptor). The resource
combines 26 public case–control cohorts across 10 disease contexts, 17 frozen
signalling modules (99 genes), and 442 cohort–module pairs, scored in three
layers (bulk GSVA z-scores, TCGA member-mean z-scores, single-cell member
means) with coverage-aware standardised effect sizes.

**Provenance and scope.** This repository is rebuilt from the manuscript, its
Tables document and its Supplementary Information. The original pipeline
(`11_code/` of the data deposit) was **not** part of the submission package;
the code here is a faithful re-implementation of the documented formulas,
parameters and decision rules — no values were invented. Inputs that only
exist in the deposit are declared in
[`data/placeholders/README.md`](data/placeholders/README.md), and every
script that needs them stops with an explicit error rather than fabricating
data. Printed reference tables (complete and clearly marked subsets) are in
[`data/reference/`](data/reference) with per-file provenance in
`table_manifest.json`.

This repository is the analysis-code repository cited in the manuscript's
Code Availability statement (release tag v1.0, MIT licence):
https://github.com/202420652/cross-disease-transcriptomic-resource
Data deposit: Zenodo, DOI reserved at submission.

## Layout

| Path | Contents |
|---|---|
| `src/cdtr/` | Python 3.11 validation layer: effect sizes (SMDH/SMCRPH, exact gamma J, Bonett LS variance), REML + Hartung–Knapp pooling, BH, direction consistency, score construction, single-cell donor rules, design decisions |
| `R/` | R 4.4.1 pipeline mirroring the documented calls: GSVA 1.52.3 scoring, metafor 5.0.1 `escalc`/`rma.uni`, xCell 1.1.0, survival Cox models, `run_all.R` |
| `scripts/` | `validate_reference_tables.py` (structural consistency of the printed tables), `verify_independent_implementation.py` (Monte Carlo check of the SMDH variance, mirroring S27) |
| `tests/` | pytest suite with hand-computed expected values |
| `examples/` | The three reuse paths from the manuscript's Usage Notes |
| `data/reference/` | Printed tables exported verbatim from Tables.docx (36 CSVs + manifest) |
| `data/placeholders/` | Inventory of inputs that exist only in the deposit |
| `docs/` | Methodology notes, known limitations, file manifest |
| `tools/` | `export_docx_tables.py` (the verbatim table exporter used to build `data/reference/`) |
| `config.yml`, `environment.txt` | Path configuration and pinned environment |

## Quickstart

```bash
pip install -e ".[test]"
python -m pytest tests -q
python scripts/validate_reference_tables.py data/reference
python scripts/verify_independent_implementation.py
python examples/example1_gse13911_walkthrough.py
```

The R pipeline requires the data deposit: set `root_dir` in `config.yml` to
the extracted deposit, then `Rscript R/run_all.R`. Without the deposit, each
step stops with a message naming the missing input.

## Conventions that matter

- Effect direction is **case minus control** everywhere.
- The three score layers are standardised against different reference sets
  and **must not be concatenated**.
- Pooled estimates are reported only for k ≥ 2; k = 2 states are annotated
  two-cohort summaries; prediction intervals only for k ≥ 3.
- Exact reproduction means |difference| ≤ 1 × 10⁻⁶ on full-precision
  recomputation, not on printed values.

## Licence

Code: MIT (see `LICENSE`). The manuscript states that author-generated data
in the deposit are CC-BY-4.0 and upstream expression matrices remain under
their original terms.
