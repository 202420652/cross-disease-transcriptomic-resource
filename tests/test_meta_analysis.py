"""Tests for pooling, multiplicity and direction-consistency rules."""

import math

import numpy as np
import pytest

from cdtr.meta_analysis import (
    benjamini_hochberg,
    direction_consistency,
    pool_reml_knha,
    wilson_interval,
)


def test_benjamini_hochberg_step_up():
    adjusted = benjamini_hochberg([0.001, 0.01, 0.04])
    assert np.allclose(adjusted, [0.003, 0.015, 0.04])


def test_benjamini_hochberg_keeps_nan_and_order():
    adjusted = benjamini_hochberg([0.04, np.nan, 0.001])
    assert adjusted[0] == pytest.approx(0.04)
    assert math.isnan(adjusted[1])
    assert adjusted[2] == pytest.approx(0.002)


def test_benjamini_hochberg_rejects_out_of_range():
    with pytest.raises(ValueError):
        benjamini_hochberg([1.2])


def test_wilson_interval_known_value():
    low, high = wilson_interval(5, 10)
    assert low == pytest.approx(0.2366, abs=1e-3)
    assert high == pytest.approx(0.7636, abs=1e-3)
    with pytest.raises(ValueError):
        wilson_interval(11, 10)


def test_pool_identical_effects():
    pooled = pool_reml_knha([1.0, 1.0, 1.0], [0.1, 0.1, 0.1])
    assert pooled.k == 3
    assert pooled.effect == pytest.approx(1.0)
    assert pooled.tau2 == pytest.approx(0.0, abs=1e-8)
    assert pooled.i2 == pytest.approx(0.0)
    assert pooled.annotation == "REML + Hartung-Knapp"


def test_pool_heterogeneous_effects():
    pooled = pool_reml_knha([1.0, 1.2, 0.8], [0.1, 0.1, 0.1])
    assert pooled.k == 3
    assert pooled.effect == pytest.approx(1.0)
    assert pooled.se > 0
    assert pooled.pi_low is not None and pooled.pi_high is not None
    assert pooled.pi_low < pooled.effect < pooled.pi_high


def test_pool_two_cohorts_is_annotated_summary():
    pooled = pool_reml_knha([0.5, 1.5], [0.2, 0.2])
    assert pooled.k == 2
    assert pooled.annotation == "two-cohort summary; heterogeneity uninformative"
    assert pooled.pi_low is None and pooled.pi_high is None


def test_pool_requires_two_inputs_and_positive_variance():
    with pytest.raises(ValueError):
        pool_reml_knha([1.0], [0.1])
    with pytest.raises(ValueError):
        pool_reml_knha([1.0, 1.0], [0.1, 0.0])


def test_direction_consistency():
    result = direction_consistency([1.0, 2.0, -0.5])
    assert result["k"] == 3
    assert result["positive"] == 2 and result["negative"] == 1
    assert result["fully_concordant"] is False
    assert result["majority_fraction"] == pytest.approx(2 / 3)
    concordant = direction_consistency([0.1, 0.2, 0.3])
    assert concordant["fully_concordant"] is True
    assert concordant["random_sign_complete_agreement"] == pytest.approx(2 * 0.5**3)
    with pytest.raises(ValueError):
        direction_consistency([0.0, 1.0])
