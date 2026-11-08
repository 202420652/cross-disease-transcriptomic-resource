"""Tests for the effect-size formulas transcribed from the manuscript.

Expected values are hand-computed from the manuscript's formulas
(Methods, "Effect-size definitions"): y = J * (m1 - m2) / sdpi with
sdpi = sqrt((s1^2 + s2^2) / 2), J the exact gamma-function correction,
and Bonett's heteroscedastic LS variance.
"""

import math

import pytest

from cdtr.effect_sizes import bias_correction, rms_sd, smcrph, smdh

# Gamma(9) / (sqrt(9) * Gamma(8.5)) with Gamma(8.5) = 14034.4072935,
# hand-computed from the Gamma recurrence. This is metafor's c(m = 18).
J18 = 0.957646


def test_bias_correction_exact_gamma():
    assert bias_correction(18) == pytest.approx(J18, abs=1e-5)
    assert bias_correction(2) < bias_correction(18) < 1.0
    with pytest.raises(ValueError):
        bias_correction(1)


def test_rms_sd():
    assert rms_sd(1.0, 1.0) == pytest.approx(1.0)
    assert rms_sd(2.0, 4.0) == pytest.approx(math.sqrt(10.0))
    with pytest.raises(ValueError):
        rms_sd(0.0, 0.0)
    with pytest.raises(ValueError):
        rms_sd(-1.0, 1.0)


def test_smdh_point_estimate_and_variance():
    # m1=1, m2=0, s1=s2=1, n1=n2=10 -> sdpi=1, J(18), vi from the
    # manuscript's closed form:
    # v = y^2 * (1/9 + 1/9) / 8 + (1/9 + 1/9)
    est = smdh(1.0, 0.0, 1.0, 1.0, 10, 10)
    assert est.measure == "SMDH"
    assert est.yi == pytest.approx(J18, rel=1e-5)
    expected_vi = est.yi**2 * (2 / 9) / 8 + 2 / 9
    assert est.vi == pytest.approx(expected_vi, rel=1e-9)
    assert est.vi == pytest.approx(0.2477, abs=1e-3)
    assert est.se == pytest.approx(math.sqrt(est.vi))


def test_smdh_direction_is_case_minus_control():
    assert smdh(1.0, 0.0, 1.0, 1.0, 10, 10).yi > 0
    assert smdh(0.0, 1.0, 1.0, 1.0, 10, 10).yi < 0


def test_smdh_minimum_group_size():
    with pytest.raises(ValueError):
        smdh(1.0, 0.0, 1.0, 1.0, 1, 10)


def test_smcrph_uses_pairs_and_within_pair_correlation():
    # m1=1, m2=0, s1=s2=1, npair=10, r=0.5 ->
    # df = 2*(npair-1) = 18 (same J as above);
    # v = (1 + 1 - 2*0.5)/(10) + y^2 * 2 / (8*9)
    est = smcrph(1.0, 0.0, 1.0, 1.0, 10, 0.5)
    assert est.measure == "SMCRPH"
    assert est.yi == pytest.approx(J18, rel=1e-5)
    expected_vi = (1 + 1 - 2 * 0.5) / 10 + est.yi**2 * 2 / (8 * 9)
    assert est.vi == pytest.approx(expected_vi, rel=1e-9)
    assert est.vi == pytest.approx(0.12547, abs=1e-4)


def test_smcrph_correlation_changes_variance_not_point_estimate():
    low = smcrph(1.0, 0.0, 1.0, 1.0, 10, 0.1)
    high = smcrph(1.0, 0.0, 1.0, 1.0, 10, 0.9)
    assert low.yi == pytest.approx(high.yi)
    assert high.vi < low.vi  # higher within-pair r shrinks the variance


def test_smcrph_validation():
    with pytest.raises(ValueError):
        smcrph(1.0, 0.0, 1.0, 1.0, 1, 0.5)
    with pytest.raises(ValueError):
        smcrph(1.0, 0.0, 1.0, 1.0, 10, 1.5)


def test_no_correction_returns_uncorrected_estimate():
    est = smdh(1.0, 0.0, 1.0, 1.0, 10, 10, correct=False)
    assert est.j == 1.0
    assert est.yi == pytest.approx(1.0)
