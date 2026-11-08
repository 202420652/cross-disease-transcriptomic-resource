"""Effect-size formulas stated in the manuscript and metafor 5.0.1.

SMDH is used for independent groups and SMCRPH for complete pairs. Both use
case minus control and the same root-mean-square SD denominator. The exact
gamma-function correction is used; no large-sample approximation for J is made.
"""

from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class EffectEstimate:
    yi: float
    vi: float
    sdpi: float
    j: float
    measure: str

    @property
    def se(self) -> float:
        return math.sqrt(self.vi)


def bias_correction(df: float) -> float:
    """Return metafor's c(m): Gamma(m/2)/(sqrt(m/2)*Gamma((m-1)/2))."""
    if df <= 1:
        raise ValueError("The bias-correction degrees of freedom must exceed 1")
    return math.exp(math.lgamma(df / 2) - 0.5 * math.log(df / 2) - math.lgamma((df - 1) / 2))


def rms_sd(sd_case: float, sd_control: float) -> float:
    """Shared standardisation denominator sqrt((sd_case^2+sd_control^2)/2)."""
    if sd_case < 0 or sd_control < 0:
        raise ValueError("Standard deviations cannot be negative")
    denominator = math.sqrt((sd_case**2 + sd_control**2) / 2)
    if denominator == 0:
        raise ValueError("Zero-variance modules are not estimable")
    return denominator


def smdh(
    mean_case: float,
    mean_control: float,
    sd_case: float,
    sd_control: float,
    n_case: int,
    n_control: int,
    *,
    correct: bool = True,
) -> EffectEstimate:
    """Independent-group SMDH with Bonett's heteroscedastic LS variance."""
    if n_case < 2 or n_control < 2:
        raise ValueError("SMDH requires at least two observations per group")
    sdpi = rms_sd(sd_case, sd_control)
    j = bias_correction(n_case + n_control - 2) if correct else 1.0
    yi = j * (mean_case - mean_control) / sdpi
    vi = (
        yi**2
        * (sd_case**4 / (n_case - 1) + sd_control**4 / (n_control - 1))
        / (8 * sdpi**4)
        + (sd_case**2 / (n_case - 1) + sd_control**2 / (n_control - 1)) / sdpi**2
    )
    return EffectEstimate(yi=yi, vi=vi, sdpi=sdpi, j=j, measure="SMDH")


def smcrph(
    mean_case: float,
    mean_control: float,
    sd_case: float,
    sd_control: float,
    n_pairs: int,
    within_pair_r: float,
    *,
    correct: bool = True,
) -> EffectEstimate:
    """Paired SMCRPH using complete pairs and empirical within-pair correlation."""
    if n_pairs < 2:
        raise ValueError("SMCRPH requires at least two complete pairs")
    if not -1 <= within_pair_r <= 1:
        raise ValueError("within_pair_r must be in [-1, 1]")
    sdpi = rms_sd(sd_case, sd_control)
    j = bias_correction(2 * (n_pairs - 1)) if correct else 1.0
    yi = j * (mean_case - mean_control) / sdpi
    vi = (
        (sd_case**2 + sd_control**2 - 2 * within_pair_r * sd_case * sd_control)
        / (n_pairs * sdpi**2)
        + yi**2 * (sd_case**4 + sd_control**4) / (8 * (n_pairs - 1) * sdpi**4)
    )
    return EffectEstimate(yi=yi, vi=vi, sdpi=sdpi, j=j, measure="SMCRPH")
