# Archive note — read before using the scripts in this folder

`11_code/` contains the analysis pipeline **as it was executed** to produce the
tables, figures and numbers deposited in this package (deposit version v18.0,
released as tag `v1.0` of the GitHub repository). It is archived for provenance
and is **not** the maintained, reusable implementation.

- Maintained code: `src/` (Python validation layer), `R/` (documented GSVA /
  metafor / xCell / survival calls), `scripts/`, `tests/`, at the repository
  root, with `README.md` and `config.yml` describing how to run it.
- Archived pipeline: this folder. Files are preserved byte-for-byte as run;
  they are not updated when the manuscript text changes.

Because the pipeline is preserved unmodified, it contains **historical
hard-coded strings** that no longer match the current availability statement.
These are records of what was run, not statements about the resource:

| Location | Historical string | Current statement |
|---|---|---|
| `70_v14_manuscript.py` | Data Availability boilerplate naming a Zenodo deposit and the former account URL | manuscript Data Availability / Code Availability; this package's `00_README.md` |
| `70_v14_manuscript.py` | "ten folders" (the v14 deposit had ten; the current deposit has eleven) | eleven folders: `01_cohort_registry/` … `11_code/` |
| `75_v14_checksum_tidy.py`, `92_v14_final_format_rebuild.py` | local Windows paths and package-ZIP names from the build machine | paths in `config.yml` at the repository root |
| `80_v14_fix_pass1.py` | writes the former update-policy line into `00_VERSION.txt` | `00_VERSION.txt` in this package |

Running these scripts is not required to use the resource: every table in this
package is final and verified by `08_qc/checksums_sha256.txt`. The scripts are
provided so that the derivation of each table can be inspected.

Execution order is recorded in `10_environment/run_order.md`; the software
environment at run time is in `10_environment/environment.txt` and
`sessionInfo.txt` in this folder.
