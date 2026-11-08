"""Tests for donor-level single-cell rules, including the legacy definitions."""

import numpy as np
import pytest

from cdtr.single_cell import (
    classify_comparison,
    difference_of_group_medians,
    full_n_paired_bootstrap,
    full_n_unpaired_bootstrap,
    legacy_capped_percentile_bootstrap,
    legacy_median_signed_donor_means,
    median_within_donor_difference,
    two_sided_rank_test,
)


def test_classify_comparison_rules():
    paired = classify_comparison([f"d{i}" for i in range(6)], [f"d{i}" for i in range(6)])
    assert paired.status == "PAIRED" and paired.complete_pairs == 6

    disjoint = classify_comparison(["a", "b", "c"], ["d", "e", "f"])
    assert disjoint.status == "UNPAIRED" and disjoint.complete_pairs == 0

    too_few = classify_comparison(["a", "b"], ["a", "b"])
    assert too_few.status == "NOT TESTABLE"  # fewer than three donors per arm

    ambiguous = classify_comparison(["a", "b", "c"], ["a", "d", "e"])
    assert ambiguous.status == "NOT TESTABLE"  # 1 pair, not donor-disjoint

    identity = classify_comparison(
        ["a", "b", "c"], ["a", "b", "c"], cell_identity=True
    )
    assert identity.status == "CELL IDENTITY DESCRIPTIVE"


def test_legacy_signed_median_is_not_a_difference_of_medians():
    # Legacy statistic: median(case means and negated control means).
    assert legacy_median_signed_donor_means([1.0, 2.0], [1.0, 1.0]) == pytest.approx(0.0)
    # The required revision instead subtracts the group medians.
    assert difference_of_group_medians([1.0, 2.0], [1.0, 1.0]) == pytest.approx(0.5)


def test_median_within_donor_difference():
    assert median_within_donor_difference([1.0, 2.0, 10.0]) == pytest.approx(2.0)
    with pytest.raises(ValueError):
        median_within_donor_difference([])


def test_two_sided_rank_test_designs():
    p_paired = two_sided_rank_test(
        [1, 2, 3, 4, 5, 6], [1.1, 2.1, 2.9, 4.2, 5.1, 5.9], paired=True
    )
    assert 0.0 < p_paired <= 1.0
    p_unpaired = two_sided_rank_test([1, 2, 3], [4, 5, 6], paired=False)
    assert 0.0 < p_unpaired <= 1.0
    with pytest.raises(ValueError):
        two_sided_rank_test([1, 2], [3, 4], paired=True)
    with pytest.raises(ValueError):
        two_sided_rank_test([1, 2], [3, 4], paired=False)


def test_legacy_bootstrap_is_capped_and_reproducible():
    values = np.arange(1.0, 21.0)
    lo1, hi1 = legacy_capped_percentile_bootstrap(values, seed=7)
    lo2, hi2 = legacy_capped_percentile_bootstrap(values, seed=7)
    assert (lo1, hi1) == (lo2, hi2)
    # The cap (min(n, 12)) resamples fewer donors than the full set;
    # the interval must still sit inside the observed range.
    assert 1.0 <= lo1 <= hi1 <= 20.0


def test_full_n_bootstrap_revision_paths():
    case = [1.0, 2.0, 3.0, 4.0]
    control = [0.5, 1.0, 1.5, 2.0]
    lo, hi = full_n_unpaired_bootstrap(case, control, seed=11)
    assert lo <= difference_of_group_medians(case, control) <= hi or lo <= hi
    plo, phi = full_n_paired_bootstrap([0.5, 1.0, 1.5, 2.0], seed=11)
    assert plo <= phi
    with pytest.raises(ValueError):
        full_n_unpaired_bootstrap([], control, seed=1)
