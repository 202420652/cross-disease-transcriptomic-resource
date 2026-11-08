"""Consistency checks for the printed reference tables in data/reference/.

These tables were exported verbatim from the manuscript's Tables.docx; this
script verifies the structural invariants stated in the manuscript text so a
broken or truncated export fails loudly:

  * 26 case-control cohorts across 10 disease contexts (S1)
  * 17 mutually exclusive modules, 99 member genes in total (S2)
  * the design-stratified pooled table has 312 printed rows (S25)
  * S26 / S29 / S19 discordant-pair files are PRINTED SUBSETS
    (first 80 of 165, first 60 of 208, first 12 rows respectively) and their
    file names must keep that marker
  * table_manifest.json accounts for every exported CSV

Exit code is non-zero if any check fails. Run:
    python scripts/validate_reference_tables.py data/reference
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

# Module membership counts stated in the manuscript (Methods, "Module
# definitions"; module_version = v12.0-frozen-2026-09).
MODULE_MEMBERS = {
    "ERBB_RECEPTORS": 4,
    "ERBB_LIGANDS": 6,
    "RAS_MAPK": 12,
    "PI3K_AKT": 9,
    "FGFR_AXIS": 8,
    "VEGF_PDGF_AXIS": 9,
    "PDGFR_KIT_CSF1R": 5,
    "HGF_MET_AXIS": 3,
    "TAM_AXL_AXIS": 3,
    "IGF_INSR_AXIS": 4,
    "RET_ALK_NTRK": 6,
    "EPH_RECEPTORS": 4,
    "TIE_ANGPT_AXIS": 3,
    "JAK_STAT": 9,
    "SRC_FAK": 5,
    "TGFB_SMAD": 5,
    "WNT_CTNNB1": 4,
}

EXPECTED_COHORTS = 26
EXPECTED_CONTEXTS = 10
EXPECTED_S25_ROWS = 312
SUBSET_MARKERS = {
    "s26_classic_denominator_sensitivity_first80.csv": 80,
    "s29_single_cell_donor_effects_first60.csv": 60,
    "s19_discordant_pairs_first12.csv": 12,
}


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def collect_failures(reference_dir: Path) -> list[str]:
    failures: list[str] = []

    def check(condition: bool, message: str) -> None:
        if not condition:
            failures.append(message)

    # S1: cohort registry
    registry = _read_csv(reference_dir / "s01_cohort_registry.csv")
    check(len(registry) == EXPECTED_COHORTS,
          f"S1 cohort count {len(registry)} != {EXPECTED_COHORTS}")
    accessions = [row["Accession"] for row in registry]
    check(len(set(accessions)) == len(accessions), "S1 accessions are not unique")
    contexts = {row["Context"] for row in registry}
    check(len(contexts) == EXPECTED_CONTEXTS,
          f"S1 context count {len(contexts)} != {EXPECTED_CONTEXTS}: {sorted(contexts)}")

    # S2: module coverage summary (17 module rows; the last row is a note)
    coverage = _read_csv(reference_dir / "s02_module_coverage_summary.csv")
    module_rows = [row for row in coverage if row["Module (short label)"] in MODULE_MEMBERS]
    check(len(module_rows) == len(MODULE_MEMBERS),
          f"S2 module row count {len(module_rows)} != {len(MODULE_MEMBERS)}")
    total_members = sum(int(row["Members"]) for row in module_rows)
    check(total_members == 99, f"S2 member total {total_members} != 99")
    for row in module_rows:
        name = row["Module (short label)"]
        check(int(row["Members"]) == MODULE_MEMBERS[name],
              f"S2 member count for {name} is {row['Members']}, "
              f"expected {MODULE_MEMBERS[name]}")
        min_cov = float(row["Minimum coverage"])
        check(0.0 < min_cov <= 1.0, f"S2 minimum coverage out of range for {name}")

    # S25: design-stratified pooled table (complete printed table, 312 rows)
    s25 = _read_csv(reference_dir / "s25_meta_by_design_stratum.csv")
    check(len(s25) == EXPECTED_S25_ROWS,
          f"S25 row count {len(s25)} != {EXPECTED_S25_ROWS}")
    strata = {row["Stratum"] for row in s25}
    check(strata == {"all cohorts", "paired cohorts only", "unpaired cohorts only"},
          f"S25 unexpected strata: {sorted(strata)}")
    check({row["Disease"] for row in s25} == contexts,
          "S25 disease set differs from the S1 context set")

    # S32: analysis sample sizes (26 cohort rows + one total row)
    s32 = _read_csv(reference_dir / "s32_analysis_sample_sizes.csv")
    cohort_rows = [row for row in s32 if row["Accession"].startswith("GSE")]
    check(len(cohort_rows) == EXPECTED_COHORTS,
          f"S32 cohort row count {len(cohort_rows)} != {EXPECTED_COHORTS}")
    measures = {row["Measure"] for row in cohort_rows}
    check(measures <= {"SMDH", "SMCRPH"}, f"S32 unexpected measures: {measures}")

    # Printed subsets must keep their marker in the file name and row count.
    for filename, expected_rows in SUBSET_MARKERS.items():
        path = reference_dir / filename
        check(path.exists(), f"missing printed-subset file {filename}")
        if path.exists():
            check(len(_read_csv(path)) == expected_rows,
                  f"{filename} row count != {expected_rows}")

    # The manifest must account for every exported CSV.
    manifest_path = reference_dir / "table_manifest.json"
    check(manifest_path.exists(), "table_manifest.json is missing")
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        listed = {entry["file"] for entry in manifest["tables"]}
        on_disk = {p.name for p in reference_dir.glob("*.csv")}
        check(listed == on_disk,
              f"manifest/disk mismatch: only in manifest {sorted(listed - on_disk)}, "
              f"only on disk {sorted(on_disk - listed)}")

    return failures


def main() -> int:
    reference_dir = Path(sys.argv[1] if len(sys.argv) > 1 else "data/reference")
    failures = collect_failures(reference_dir)
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1
    print(f"All reference-table consistency checks passed for {reference_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
