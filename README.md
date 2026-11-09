# Cross-disease case–control transcriptome resource — analysis code

Analysis and validation code extracted from the manuscript submission package
of *"A cross-disease case–control transcriptome resource with coverage-aware
signalling-module scores"* (submitted as a Data Descriptor). The resource
combines 26 public case–control cohorts across 10 disease contexts, 17 frozen
signalling modules (99 genes), and 442 cohort–module pairs, scored in three
layers (bulk GSVA z-scores, TCGA member-mean z-scores, single-cell member
means) with coverage-aware standardised effect sizes.

**What is here — two parts, and the distinction matters.**

- the **data deposit** described in the manuscript, shipped as
  [`deposit/`](deposit): eleven folders `01_cohort_registry/` …
  `11_code/`, deposit version v18.0, with its own `00_README.md`,
  `00_CHANGELOG.md`, `00_VERSION.txt` and integrity manifests;
- the **maintained code**: a Python 3.11 validation layer, an R 4.4.1 pipeline
  mirroring the documented calls, the validation scripts, the pytest suite and
  the three reuse examples.

The archived pipeline in `deposit/11_code/` is preserved byte-for-byte as it was
run (see [`deposit/11_code/00_ARCHIVE_NOTE.md`](deposit/11_code/00_ARCHIVE_NOTE.md));
the maintained code in `src/`, `R/`, `scripts/` and `tests/` re-implements the
documented formulas, parameters and decision rules so that they can be reused
and checked independently. No values were invented: every input the code reads
is a file under `deposit/`, mapped in
[`data/placeholders/README.md`](data/placeholders/README.md), and a missing
input stops the run with an explicit error rather than being replaced.
Printed reference tables (complete, with three clearly marked subsets) are in
[`data/reference/`](data/reference) with per-file provenance in
`table_manifest.json`.

This repository is the resource cited in the manuscript's Data Availability and
Code Availability statements — release tag **v1.0**:
https://github.com/202420652/cross-disease-transcriptomic-resource

**Citable archived version.** Release v1.0 is archived at Zenodo:

- version DOI: [10.5281/zenodo.24083604](https://doi.org/10.5281/zenodo.24083604)
- concept DOI (all versions): [10.5281/zenodo.24083603](https://doi.org/10.5281/zenodo.24083603)
- record: https://zenodo.org/records/24083604

Cite the version DOI for exactly this snapshot and the concept DOI when pointing
at the resource in general. The Zenodo record is the persistent archive; this
repository remains the working access point (issues, fixes, later releases).

## Layout

| Path | Contents |
|---|---|
| `deposit/` | The data deposit described in the manuscript: eleven folders `01_cohort_registry/` … `11_code/`, 136 shipped files (133 covered by the checksum list, plus the three integrity manifests), deposit version v18.0. Start at `deposit/00_README.md` |
| `src/cdtr/` | Python 3.11 validation layer: effect sizes (SMDH/SMCRPH, exact gamma J, Bonett LS variance), REML + Hartung–Knapp pooling, BH, direction consistency, score construction, single-cell donor rules, design decisions |
| `R/` | R 4.4.1 pipeline mirroring the documented calls: GSVA 1.52.3 scoring, metafor 5.0.1 `escalc`/`rma.uni`, xCell 1.1.0, survival Cox models, `run_all.R` |
| `scripts/` | `validate_reference_tables.py` (structural consistency of the printed tables), `verify_independent_implementation.py` (Monte Carlo check of the SMDH variance, mirroring S27) |
| `tests/` | pytest suite with hand-computed expected values |
| `examples/` | The three reuse paths from the manuscript's Usage Notes |
| `data/reference/` | Printed tables exported verbatim from Tables.docx (36 CSVs + manifest) |
| `data/placeholders/` | Input map: each deposit input and where it lives |
| `docs/` | Methodology notes, known limitations, file manifest |
| `tools/` | `export_docx_tables.py` (table exporter used to build `data/reference/`), `refresh_deposit_manifests.py` (rebuilds the deposit's inventory, checksum list and manifest digest) |
| `config.yml`, `environment.txt` | Path configuration and pinned environment |
| `LICENSE`, `LICENSE-DATA` | MIT for code; CC-BY-4.0 for author-generated data |
| `CHANGELOG.md` | Release notes and version history of this repository |
| `CITATION.cff` | Machine-readable citation for the archived release (version and concept DOI) |

## Quickstart

```bash
# code checks
pip install -e ".[test]"
python -m pytest tests -q
python scripts/validate_reference_tables.py data/reference
python scripts/verify_independent_implementation.py
python examples/example1_gse13911_walkthrough.py

# deposit integrity (133 files; the two manifest files are checked separately)
cd deposit && sha256sum -c 08_qc/checksums_sha256.txt
cd 08_qc && sha256sum -c manifest_checksum.txt
```

The R pipeline runs against the shipped deposit: `root_dir` in `config.yml` is
`deposit`, so `Rscript R/run_all.R` works from the repository root. Point
`root_dir` at an absolute path if you run the scripts from elsewhere; without the
deposit each step stops with a message naming the missing input.

## Conventions that matter

- Effect direction is **case minus control** everywhere.
- The three score layers are standardised against different reference sets
  and **must not be concatenated**.
- Pooled estimates are reported only for k ≥ 2; k = 2 states are annotated
  two-cohort summaries; prediction intervals only for k ≥ 3.
- Exact reproduction means |difference| ≤ 1 × 10⁻⁶ on full-precision
  recomputation, not on printed values.

## Archiving and the citable identifier

Release v1.0 was archived from GitHub through the Zenodo integration on
2026-11-09; the metadata in [`.zenodo.json`](.zenodo.json) (title, description,
the nine creators with affiliations and the ORCID iDs the manuscript provides,
the CC-BY-4.0 data licence and the relation to this repository) is what the
record was built from. The record is published:

| Identifier | Value | Use |
|---|---|---|
| Version DOI | `10.5281/zenodo.24083604` | cite this exact snapshot (v1.0) |
| Concept DOI | `10.5281/zenodo.24083603` | cite the resource across versions |

The archived file is the repository snapshot at tag `v1.0`
(`202420652/cross-disease-transcriptomic-resource-v1.0.zip`, md5
`f1ed808c7c9195eba46cd22e8a47896f`). Later releases are archived automatically by
the same integration and receive their own version DOI under the concept DOI.

The DOI is recorded in the manuscript's Data Availability and Code Availability
statements, in [`CHANGELOG.md`](CHANGELOG.md), in [`CITATION.cff`](CITATION.cff)
and in [`LICENSE-DATA`](LICENSE-DATA). Files inside `deposit/` are deliberately
left byte-for-byte as archived, so `sha256sum -c 08_qc/checksums_sha256.txt`
still verifies 133/133; the DOI therefore lives in the repository-level files
listed above rather than inside the deposit.

## Licence

Split by content, as stated file by file in `deposit/08_qc/data_dictionary.csv`:

- **Code** — `src/`, `R/`, `scripts/`, `tests/`, `tools/` and the archived
  pipeline `deposit/11_code/`: MIT, see [`LICENSE`](LICENSE).
- **Author-generated data** — annotation, module definitions, derived score
  matrices, the estimates layer, quality-control records and the data
  dictionary in `deposit/`: CC-BY-4.0, full text in
  [`LICENSE-DATA`](LICENSE-DATA).
- **Upstream expression matrices** retrieved from GEO, TCGA/GDC (via
  cBioPortal) and CELLxGENE are **not** re-licensed here and remain under the
  terms of their original repositories. Where redistribution is not permitted,
  only the accession, the checksum and the download script are shipped.

If you use the resource, cite the Data Descriptor and the archived release:
version DOI `10.5281/zenodo.24083604` for this snapshot, concept DOI
`10.5281/zenodo.24083603` for the resource in general. [`CITATION.cff`](CITATION.cff)
carries the same information in machine-readable form. See
[`CHANGELOG.md`](CHANGELOG.md) for what the release contains.
