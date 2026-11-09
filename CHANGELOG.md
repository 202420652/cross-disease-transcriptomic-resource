# Changelog and release notes

This file is the release-notes record for the repository. It is the document
referred to as "release notes" in the manuscript's Data Availability statement.

## v1.0 — release accompanying the Data Descriptor submission (2026-11-09)

**What this release contains**

| Component | Path | Contents |
|---|---|---|
| Data deposit | `deposit/` | 11 folders (`01_cohort_registry/` … `11_code/`) + `00_README.md`, `00_CHANGELOG.md`, `00_VERSION.txt`; deposit version v18.0 |
| Maintained code | `src/cdtr/`, `R/`, `scripts/`, `tests/` | Python 3.11 validation layer, R 4.4.1 pipeline, validation scripts, pytest suite |
| Archived pipeline | `deposit/11_code/` | the scripts as executed for the deposit (preserved unchanged; see `deposit/11_code/00_ARCHIVE_NOTE.md`) |
| Printed reference tables | `data/reference/` | 36 tables exported cell-by-cell from `Tables.docx`, with `table_manifest.json` provenance and source SHA-256 |
| Documentation | `README.md`, `docs/`, `examples/` | methodology notes, known limitations, file manifest, three reuse examples |
| Licences | `LICENSE`, `LICENSE-DATA` | MIT (code), CC-BY-4.0 (author-generated data) |

**Version correspondence.** This release is deposit v18.0 (internal pre-release
iteration 18). `deposit/00_VERSION.txt` records the deposit version;
`deposit/00_CHANGELOG.md` records the deposit's own version history (v12 → v18).

**Integrity.** `deposit/08_qc/file_inventory_and_checksums.csv` lists every
shipped file with byte size, row count and SHA-256;
`deposit/08_qc/checksums_sha256.txt` is directly checkable with
`sha256sum -c 08_qc/checksums_sha256.txt` from inside `deposit/`; the digests of
those two manifest files are recorded in `deposit/08_qc/manifest_checksum.txt`.

**Changes relative to the previous tag.** The tag `v1.0` was first created on an
earlier commit that contained only the code and the printed reference tables.
It was re-cut on this commit before submission so that the tag, the manuscript's
Data Availability statement and the shipped files all describe the same
snapshot: the release now contains the full data deposit. No tag other than
`v1.0` has been published, and the release has not been cited externally.

**Archival record (Zenodo).** This release is archived and published:

| Identifier | Value |
|---|---|
| Version DOI | `10.5281/zenodo.24083604` — https://doi.org/10.5281/zenodo.24083604 |
| Concept DOI | `10.5281/zenodo.24083603` — https://doi.org/10.5281/zenodo.24083603 |
| Record | https://zenodo.org/records/24083604 |
| Archived file | `202420652/cross-disease-transcriptomic-resource-v1.0.zip` (1.9 MB, md5 `f1ed808c7c9195eba46cd22e8a47896f`) |
| Archived commit | `4f7283f` (tag `v1.0`) |
| Archived on | 2026-11-09 |

The record was created by the GitHub–Zenodo integration from `.zenodo.json` at
the tagged commit: nine creators in manuscript order, affiliations, the three
ORCID iDs the manuscript provides, `dataset` / open access / CC-BY-4.0, and the
relation `isSupplementTo` this repository. The record is the citable persistent
identifier; later releases are archived the same way and get their own version
DOI under the concept DOI.

**Known gaps (declared, not hidden)**

- `deposit/03_expression/` ships provenance, checksums and download scripts
  rather than redistributable matrices wherever the upstream terms forbid
  redistribution; the matrices are regenerated from the public accessions.
- Files inside `deposit/` are left byte-for-byte as archived so the 133 checksums
  still verify; the DOI is therefore recorded in `README.md`, `CITATION.cff`,
  `LICENSE-DATA` and this file, not inside `deposit/`.
- Software Heritage registration is not claimed for this release.

**Verification performed for this release**

```bash
pip install -e ".[test]"
python -m pytest tests -q                       # 37 tests
python scripts/validate_reference_tables.py data/reference
python scripts/verify_independent_implementation.py     # SMDH variance Monte Carlo
cd deposit && sha256sum -c 08_qc/checksums_sha256.txt
```
