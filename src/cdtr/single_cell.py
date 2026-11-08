"""Donor-level single-cell summaries and design rules, including legacy definitions.

The signed-median summary and capped bootstrap are retained only to reproduce the
current release's descriptive layer. They are not presented as recommended new
analyses; difference of group medians and full-n donor resampling are provided as
the manuscript-required revision path.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

import numpy as np
from scipy import stats


@dataclass(frozen=True)
class ComparisonDesign:
    status: str
    complete_pairs: int
    donors_a: int
    donors_b: int
    reason: str


def classify_comparison(
    donors_a: Iterable[str],
    donors_b: Iterable[str],
    *,
    cell_identity: bool = False,
) -> ComparisonDesign:
    """Apply >=3 donors/arm, >=5 complete pairs, or donor-disjoint unpaired rules."""
    a, b = frozenset(donors_a), frozenset(donors_b)
    pairs = len(a & b)
    if len(a) < 3 or len(b) < 3:
        return ComparisonDesign("NOT TESTABLE", pairs, len(a), len(b), "fewer than three donors per arm")
    if cell_identity:
        return ComparisonDesign(
            "CELL IDENTITY DESCRIPTIVE",
            pairs,
            len(a),
            len(b),
            "same-donor cell types; unpaired rank p values are descriptive only",
        )
    if pairs >= 5:
        return ComparisonDesign("PAIRED", pairs, len(a), len(b), "at least five complete donor pairs")
    if pairs == 0:
        return ComparisonDesign("UNPAIRED", 0, len(a), len(b), "donor-disjoint arms")
    return ComparisonDesign(
        "NOT TESTABLE",
        pairs,
        len(a),
        len(b),
        "fewer than five complete pairs and arms are not donor-disjoint",
    )


def median_within_donor_difference(paired_differences: Iterable[float]) -> float:
    values = np.asarray(list(paired_differences), dtype=float)
    if not len(values) or not np.all(np.isfinite(values)):
        raise ValueError("At least one finite paired difference is required")
    return float(np.median(values))


def legacy_median_signed_donor_means(case_means: Iterable[float], control_means: Iterable[float]) -> float:
    """Legacy descriptive statistic: median(case means and negated control means)."""
    case = np.asarray(list(case_means), dtype=float)
    control = np.asarray(list(control_means), dtype=float)
    if not len(case) or not len(control):
        raise ValueError("Both arms require donor means")
    return float(np.median(np.concatenate([case, -control])))


def difference_of_group_medians(case_means: Iterable[float], control_means: Iterable[float]) -> float:
    """Required revision: an actual location difference between arm medians."""
    case = np.asarray(list(case_means), dtype=float)
    control = np.asarray(list(control_means), dtype=float)
    if not len(case) or not len(control):
        raise ValueError("Both arms require donor means")
    return float(np.median(case) - np.median(control))


def two_sided_rank_test(
    case_means: Iterable[float],
    control_means: Iterable[float],
    *,
    paired: bool,
) -> float:
    case = np.asarray(list(case_means), dtype=float)
    control = np.asarray(list(control_means), dtype=float)
    if paired:
        if len(case) != len(control) or len(case) < 5:
            raise ValueError("Paired signed-rank testing requires >=5 complete pairs")
        return float(stats.wilcoxon(case, control, alternative="two-sided").pvalue)
    if len(case) < 3 or len(control) < 3:
        raise ValueError("Unpaired testing requires >=3 donors per arm")
    return float(stats.mannwhitneyu(case, control, alternative="two-sided").pvalue)


def legacy_capped_percentile_bootstrap(
    values: Iterable[float],
    *,
    seed: int,
    resamples: int = 2000,
    cap: int = 12,
) -> tuple[float, float]:
    """Current-release descriptive interval with resample size min(n,cap), not full-n."""
    array = np.asarray(list(values), dtype=float)
    if not len(array) or not np.all(np.isfinite(array)) or resamples < 1 or cap < 1:
        raise ValueError("Invalid values or bootstrap settings")
    rng = np.random.default_rng(seed)
    size = min(len(array), cap)
    samples = rng.choice(array, size=(resamples, size), replace=True)
    medians = np.median(samples, axis=1)
    return tuple(np.percentile(medians, [2.5, 97.5]).tolist())


def full_n_unpaired_bootstrap(
    case_means: Iterable[float],
    control_means: Iterable[float],
    *,
    seed: int,
    resamples: int = 2000,
) -> tuple[float, float]:
    """Revision path: resample each arm at its own size and subtract medians."""
    case = np.asarray(list(case_means), dtype=float)
    control = np.asarray(list(control_means), dtype=float)
    if not len(case) or not len(control) or resamples < 1:
        raise ValueError("Both arms and at least one resample are required")
    rng = np.random.default_rng(seed)
    case_samples = rng.choice(case, size=(resamples, len(case)), replace=True)
    control_samples = rng.choice(control, size=(resamples, len(control)), replace=True)
    differences = np.median(case_samples, axis=1) - np.median(control_samples, axis=1)
    return tuple(np.percentile(differences, [2.5, 97.5]).tolist())


def full_n_paired_bootstrap(
    paired_differences: Iterable[float],
    *,
    seed: int,
    resamples: int = 2000,
) -> tuple[float, float]:
    """Revision path: resample complete donor pairs at the original pair count."""
    differences = np.asarray(list(paired_differences), dtype=float)
    if not len(differences) or resamples < 1:
        raise ValueError("Complete pairs and at least one resample are required")
    rng = np.random.default_rng(seed)
    samples = rng.choice(differences, size=(resamples, len(differences)), replace=True)
    medians = np.median(samples, axis=1)
    return tuple(np.percentile(medians, [2.5, 97.5]).tolist())
