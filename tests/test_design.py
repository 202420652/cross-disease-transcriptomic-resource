"""Tests for the metadata-derived design decisions."""

import pytest

from cdtr.design import analysis_measure, analysis_sample_counts, paired_design


def test_paired_design_requires_four_complete_pairs():
    assert paired_design(4) == "paired"
    assert paired_design(3) == "unpaired"
    assert paired_design(0) == "unpaired"
    with pytest.raises(ValueError):
        paired_design(-1)


def test_analysis_measure_mapping():
    assert analysis_measure("paired") == "SMCRPH"
    assert analysis_measure("unpaired") == "SMDH"
    with pytest.raises(ValueError):
        analysis_measure("crossover")


def test_analysis_sample_counts():
    # Paired cohorts contribute complete pairs only.
    assert analysis_sample_counts("paired", cases=38, controls=31, complete_pairs=31) == (31, 31)
    # Unpaired cohorts contribute all annotated samples.
    assert analysis_sample_counts("unpaired", cases=42, controls=28) == (42, 28)
    with pytest.raises(ValueError):
        analysis_sample_counts("paired", cases=5, controls=5, complete_pairs=6)
    with pytest.raises(ValueError):
        analysis_sample_counts("unpaired", cases=-1, controls=2)
