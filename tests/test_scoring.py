"""Tests for score-layer construction and expression-scale decision rules."""

import numpy as np
import pytest

from cdtr.scoring import (
    classify_expression_scale,
    common_members,
    marker_proxy,
    member_mean_score,
    module_coverage,
    single_cell_member_means,
    tcga_member_mean_z,
    zscore,
)


def test_module_coverage_definition():
    result = module_coverage(["A", "B", "C", "D"], ["A", "B", "C", "X"])
    assert result["members_total"] == 4
    assert result["members_present"] == 3
    assert result["coverage"] == pytest.approx(0.75)
    assert result["primary_scorable"] is True
    assert result["missing_members"] == ("D",)


def test_module_coverage_three_member_floor():
    two = module_coverage(["A", "B", "C", "D"], ["A", "B"])
    assert two["primary_scorable"] is False
    with pytest.raises(ValueError):
        module_coverage([], ["A"])


def test_common_members_two_gene_floor():
    shared = common_members([["A", "B", "C"], ["B", "C", "D"]])
    assert shared == frozenset({"B", "C"})
    with pytest.raises(ValueError):
        common_members([["A", "B"], ["B", "C"]])  # only one shared member
    with pytest.raises(ValueError):
        common_members([])


def test_zscore_uses_sample_sd():
    z = zscore(np.array([1.0, 2.0, 3.0]))
    assert np.mean(z) == pytest.approx(0.0)
    assert np.std(z, ddof=1) == pytest.approx(1.0)
    with pytest.raises(ValueError):
        zscore(np.array([5.0, 5.0]))


def test_member_mean_score_averages_retained_members():
    expression = np.array([[1.0, 3.0], [2.0, 4.0], [9.0, 9.0]])
    genes = ["A", "B", "OTHER"]
    scores, retained = member_mean_score(expression, genes, ["A", "B", "MISSING"], minimum=2)
    assert retained == ("A", "B")
    assert np.allclose(scores, [1.5, 3.5])
    with pytest.raises(ValueError):
        member_mean_score(expression, genes, ["A"], minimum=3)


def test_tcga_member_mean_z_is_within_context():
    expression = np.array(
        [[1.0, 2.0, 3.0, 4.0], [2.0, 2.0, 2.0, 2.0], [0.0, 1.0, 0.0, 1.0]]
    )
    genes = ["A", "B", "C"]
    z = tcga_member_mean_z(expression, genes, ["A", "B", "C"])
    assert np.mean(z) == pytest.approx(0.0)
    assert np.std(z, ddof=1) == pytest.approx(1.0)


def test_single_cell_member_means_library_size_log1p():
    # Two cells with library sizes 100 and 1000; three member genes, each at
    # 10% of the library in both cells, plus one non-member.
    counts = np.array([[10.0, 10.0, 10.0, 70.0], [100.0, 100.0, 100.0, 700.0]])
    genes = ["A", "B", "C", "OTHER"]
    scores = single_cell_member_means(counts, genes, ["A", "B", "C", "MISSING"])
    expected = np.log1p(0.1 * 1e4)
    assert scores[0] == pytest.approx(expected)
    assert scores[1] == pytest.approx(expected)
    with pytest.raises(ValueError):
        single_cell_member_means(np.zeros((1, 3)), genes[:3], genes[:3])


def test_marker_proxy_minimum_two_markers():
    expression = np.array([[1.0, 2.0, 3.0], [1.0, 3.0, 2.0]])
    genes = ["EPCAM", "KRT18"]
    z = marker_proxy(expression, genes, "epi")
    assert len(z) == 3
    with pytest.raises(ValueError):
        marker_proxy(expression, genes, "unknown_compartment")


def test_classify_expression_scale_flags_raw_counts():
    raw = np.array([0.0, 1.0, 2.0, 500.0])
    flagged = classify_expression_scale(raw)
    assert flagged["flag_for_library_size_normalisation"] is True
    assert flagged["action"].startswith("flag")
    logged = np.log2(raw + 1)
    unflagged = classify_expression_scale(logged)
    assert unflagged["flag_for_library_size_normalisation"] is False
    with pytest.raises(ValueError):
        classify_expression_scale(np.array([np.nan]))
