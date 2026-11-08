"""Example 2 - re-score a cohort with a custom (possibly overlapping) gene set.

The resource's 17 modules are mutually exclusive by design (maximum pairwise
Jaccard overlap 0.00). The manuscript states that users requiring overlapping
definitions can re-score with their own gene sets. This example shows the
member-mean + cohort z-score construction on a small synthetic matrix; point
it at a real genes x samples matrix to use it on your own data.

Direction convention (same as the resource): higher score = higher member-
gene expression; effects are case minus control.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from cdtr.scoring import member_mean_score, zscore  # noqa: E402

# Custom gene set with intentional overlap with canonical pathway genes.
CUSTOM_SET = ["EGFR", "ERBB2", "MET", "AXL"]


def main() -> None:
    rng = np.random.default_rng(42)
    genes = ["EGFR", "ERBB2", "MET", "GAPDH"]  # AXL is absent from this matrix
    expression = rng.normal(8.0, 1.5, size=(len(genes), 12))
    scores, retained = member_mean_score(expression, genes, CUSTOM_SET)
    z = zscore(scores)
    print(f"retained members: {retained} (missing: {sorted(set(CUSTOM_SET) - set(retained))})")
    print(f"member-mean z-scores across 12 samples: {np.round(z, 3)}")
    print("Reminder: these z-scores are cohort-internal; do not compare them "
          "with another cohort's z-scores as if they shared a scale.")


if __name__ == "__main__":
    main()
