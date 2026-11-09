"""Example 1 - the GSE13911 walkthrough from the manuscript's Usage Notes.

The manuscript's intended reuse path (Usage Notes, worked example):
  1. find the cohort in the registry (context, platform, design, control
     class, origin publication);
  2. join sample annotation on (accession, sample_id);
  3. check module coverage before using a score;
  4. read within-cohort GSVA z-scores (never compare them across cohorts);
  5. read the per-cohort effect and the pooled state.

The shipped anchor numbers for GSE13911 / EPH_RECEPTORS are:
  per-cohort effect 1.72 (SMCRPH on 31 complete pairs); pooled gastric state
  1.57 with k = 3 and BH-adjusted p = 0.124.

This script exercises steps 1, 3 and 5 against the printed reference tables
in data/reference/ (registry, module coverage, design-stratified pooled
table), so it runs without reading the deposit. Steps 2 and 4 read the deposit
itself (02_sample_annotation/ and 04_modules/ under deposit/); the input map
is in data/placeholders/README.md.
"""

from __future__ import annotations

import csv
from pathlib import Path

REFERENCE = Path(__file__).resolve().parents[1] / "data" / "reference"
ACCESSION = "GSE13911"
MODULE = "EPH_RECEPTORS"


def main() -> None:
    with (REFERENCE / "s01_cohort_registry.csv").open(encoding="utf-8") as handle:
        registry = {row["Accession"]: row for row in csv.DictReader(handle)}
    cohort = registry[ACCESSION]
    print(f"[1] {ACCESSION}: context={cohort['Context']}, "
          f"platform={cohort['Platform']}, paired={cohort['Paired used']}, "
          f"control class={cohort['Control class']}, PMID={cohort['Origin PMID']}")

    with (REFERENCE / "s02_module_coverage_summary.csv").open(encoding="utf-8") as handle:
        coverage = {row["Module (short label)"]: row for row in csv.DictReader(handle)
                    if row["Module (short label)"].isupper()}
    module = coverage[MODULE]
    print(f"[3] {MODULE}: {module['Members']} members, minimum per-cohort "
          f"coverage {module['Minimum coverage']}")

    with (REFERENCE / "s25_meta_by_design_stratum.csv").open(encoding="utf-8") as handle:
        pooled = [row for row in csv.DictReader(handle)
                  if row["Disease"] == cohort["Context"] and row["Module"] == MODULE
                  and row["Stratum"] == "all cohorts"]
    if pooled:
        state = pooled[0]
        print(f"[5] pooled {cohort['Context']}/{MODULE}: effect={state['Effect']}, "
              f"k={state['k']}, BH adj. p={state['BH adj. p']}")
    print("\nManuscript anchor values: per-cohort 1.72 (SMCRPH, 31 complete "
          "pairs); pooled 1.57, k=3, BH adj. p=0.124. Compare against the "
          "full-precision deposit files, not the printed values, for any "
          "quantitative reuse (pre-specified reproduction tolerance 1e-6).")


if __name__ == "__main__":
    main()
