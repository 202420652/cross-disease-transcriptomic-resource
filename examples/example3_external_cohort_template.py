"""Example 3 - template: score one external cohort and compare directions.

The manuscript's reuse-cost demonstration rebuilds module scores for the
gastric cohort GSE54129 (a reuse-demonstration input that is NOT one of the
31 screened series) from its accession, with an observed wall-clock runtime
of 1.6 minutes and cross-cohort direction agreement for 9 of 17 modules —
reported as reuse-cost metrics, not as validation. A second demonstration
scores the held-out series GSE39582 (556 colorectal samples; tumour,
survival-eligible subset only) and fits per-module Cox models.

This repository does NOT ship the download/scoring inputs for those series,
so this file is a runnable TEMPLATE: it fails with an explicit message until
you supply the two inputs below. The deterministic annotation and scoring
rules applied to the external cohort are the same functions used inside the
resource pipeline (cdtr.scoring / cdtr.effect_sizes), not a separate path.

Inputs you must supply:
    expression_csv : genes x samples CSV of the processed, symbol-mapped
                     matrix for the external cohort (e.g. GSE54129)
    annotation_csv : columns sample_id, role ("case"/"control")

Run:
    python examples/example3_external_cohort_template.py \
        --expression-csv path/to/GSE54129_matrix.csv \
        --annotation-csv path/to/GSE54129_annotation.csv
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from cdtr.design import analysis_sample_counts, paired_design  # noqa: E402
from cdtr.effect_sizes import smdh  # noqa: E402
from cdtr.scoring import member_mean_score, module_coverage, zscore  # noqa: E402

# The 17 frozen module definitions (module_version = v12.0-frozen-2026-09)
# are shipped with the data deposit as 04_modules/module_definitions.csv and
# are NOT duplicated in this repository; pass them via --modules-csv.


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--expression-csv", type=Path)
    parser.add_argument("--annotation-csv", type=Path)
    parser.add_argument("--modules-csv", type=Path,
                        help="04_modules/module_definitions.csv from the deposit")
    args = parser.parse_args()
    if not (args.expression_csv and args.annotation_csv and args.modules_csv):
        parser.error(
            "external-cohort rescoring needs --expression-csv, "
            "--annotation-csv and --modules-csv. See the module docstring and "
            "data/placeholders/README.md."
        )

    with args.modules_csv.open(encoding="utf-8") as handle:
        module_sets: dict[str, list[str]] = {}
        for row in csv.DictReader(handle):
            module_sets.setdefault(row["module"], []).append(row["gene"])

    with args.expression_csv.open(encoding="utf-8") as handle:
        reader = csv.reader(handle)
        header = next(reader)
        sample_ids = header[1:]
        genes, rows = [], []
        for record in reader:
            genes.append(record[0])
            rows.append([float(value) for value in record[1:]])
    expression = np.array(rows)

    with args.annotation_csv.open(encoding="utf-8") as handle:
        roles = {row["sample_id"]: row["role"] for row in csv.DictReader(handle)}
    case_idx = [i for i, s in enumerate(sample_ids) if roles.get(s) == "case"]
    control_idx = [i for i, s in enumerate(sample_ids) if roles.get(s) == "control"]

    # External cohorts are annotated and scored with the same deterministic
    # rules as the resource cohorts; pairing is decided from metadata.
    design = paired_design(min(len(case_idx), len(control_idx)))
    n_case, n_control = analysis_sample_counts(design, len(case_idx), len(control_idx))
    print(f"design={design}, n_case={n_case}, n_control={n_control}")

    for module, members in sorted(module_sets.items()):
        cov = module_coverage(members, genes)
        if not cov["primary_scorable"]:
            print(f"{module}: not estimable (coverage {cov['coverage']:.2f})")
            continue
        scores, retained = member_mean_score(expression, genes, members)
        z = zscore(scores)
        if design == "unpaired":
            est = smdh(
                float(np.mean(z[case_idx])), float(np.mean(z[control_idx])),
                float(np.std(z[case_idx], ddof=1)), float(np.std(z[control_idx], ddof=1)),
                n_case, n_control,
            )
            print(f"{module}: SMDH={est.yi:.3f} (SE {est.se:.3f}), "
                  f"{len(retained)} members")


if __name__ == "__main__":
    main()
