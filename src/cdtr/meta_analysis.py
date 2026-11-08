"""Random-effects pooling and inference rules declared in the manuscript."""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
from scipy import optimize, stats


@dataclass(frozen=True)
class PooledEstimate:
    effect: float
    se: float
    p: float
    tau2: float
    i2: float
    ci_low: float
    ci_high: float
    k: int
    pi_low: float | None
    pi_high: float | None
    annotation: str


def benjamini_hochberg(p_values: list[float] | np.ndarray) -> np.ndarray:
    """BH step-up adjustment in the original order; NaNs remain unadjusted."""
    p = np.asarray(p_values, dtype=float)
    if np.any((p[np.isfinite(p)] < 0) | (p[np.isfinite(p)] > 1)):
        raise ValueError("P values must be in [0, 1]")
    result = np.full(p.shape, np.nan)
    valid = np.flatnonzero(np.isfinite(p))
    if not len(valid):
        return result
    order = valid[np.argsort(p[valid], kind="stable")]
    ranked = p[order] * len(order) / np.arange(1, len(order) + 1)
    adjusted = np.minimum.accumulate(ranked[::-1])[::-1]
    result[order] = np.minimum(adjusted, 1.0)
    return result


def wilson_interval(successes: int, total: int, confidence: float = 0.95) -> tuple[float, float]:
    """Wilson score interval used for descriptive direction consistency."""
    if total <= 0 or not 0 <= successes <= total:
        raise ValueError("Require total > 0 and 0 <= successes <= total")
    z = stats.norm.ppf(0.5 + confidence / 2)
    proportion = successes / total
    denominator = 1 + z**2 / total
    centre = (proportion + z**2 / (2 * total)) / denominator
    margin = z * math.sqrt(proportion * (1 - proportion) / total + z**2 / (4 * total**2)) / denominator
    return centre - margin, centre + margin


def pool_reml_knha(yi: list[float] | np.ndarray, vi: list[float] | np.ndarray) -> PooledEstimate:
    """Pool one context-module state using REML and Hartung-Knapp inference.

    This is an independent numerical implementation for validation. The primary
    R workflow deliberately calls metafor::rma.uni directly. k=2 heterogeneity
    is annotated as uninformative; prediction intervals use t on k-2 df and are
    returned only for k>=3, matching the manuscript's declared convention.
    """
    y = np.asarray(yi, dtype=float)
    v = np.asarray(vi, dtype=float)
    if y.ndim != 1 or v.shape != y.shape or len(y) < 2:
        raise ValueError("Pooling requires matched one-dimensional yi/vi arrays with k>=2")
    if not np.all(np.isfinite(y)) or not np.all(np.isfinite(v)) or np.any(v <= 0):
        raise ValueError("All yi must be finite and all vi must be positive")
    k = len(y)

    def weighted_mean(tau2: float) -> float:
        weights = 1 / (v + tau2)
        return float(np.sum(weights * y) / np.sum(weights))

    def negative_restricted_log_likelihood(tau2: float) -> float:
        weights = 1 / (v + tau2)
        mu = weighted_mean(tau2)
        return 0.5 * float(
            np.sum(np.log(v + tau2))
            + math.log(np.sum(weights))
            + np.sum(weights * (y - mu) ** 2)
        )

    upper = max(1.0, float(np.var(y, ddof=1) * 100 + np.max(v) * 100))
    optimum = optimize.minimize_scalar(
        negative_restricted_log_likelihood,
        bounds=(0.0, upper),
        method="bounded",
        options={"xatol": 1e-12},
    )
    candidates = [(0.0, negative_restricted_log_likelihood(0.0)), (float(optimum.x), float(optimum.fun))]
    tau2 = min(candidates, key=lambda item: item[1])[0]
    weights = 1 / (v + tau2)
    effect = weighted_mean(tau2)
    q_re = float(np.sum(weights * (y - effect) ** 2))
    hk_variance = q_re / ((k - 1) * np.sum(weights))
    se = math.sqrt(max(0.0, hk_variance))
    df = k - 1
    p = float(2 * stats.t.sf(abs(effect / se), df)) if se > 0 else (0.0 if effect else 1.0)
    critical = stats.t.ppf(0.975, df)

    fixed_weights = 1 / v
    fixed_effect = float(np.sum(fixed_weights * y) / np.sum(fixed_weights))
    q_fixed = float(np.sum(fixed_weights * (y - fixed_effect) ** 2))
    i2 = max(0.0, (q_fixed - df) / q_fixed) * 100 if q_fixed > 0 else 0.0
    pi_low = pi_high = None
    if k >= 3:
        predictive_sd = math.sqrt(tau2 + hk_variance)
        predictive_critical = stats.t.ppf(0.975, k - 2)
        pi_low = effect - predictive_critical * predictive_sd
        pi_high = effect + predictive_critical * predictive_sd
    annotation = "two-cohort summary; heterogeneity uninformative" if k == 2 else "REML + Hartung-Knapp"
    return PooledEstimate(
        effect=effect,
        se=se,
        p=p,
        tau2=tau2,
        i2=i2,
        ci_low=effect - critical * se,
        ci_high=effect + critical * se,
        k=k,
        pi_low=pi_low,
        pi_high=pi_high,
        annotation=annotation,
    )


def direction_consistency(effects: list[float] | np.ndarray) -> dict[str, float | int | bool]:
    """Summarise majority-sign fraction and complete agreement for one state."""
    values = np.asarray(effects, dtype=float)
    if len(values) < 2 or not np.all(np.isfinite(values)) or np.any(values == 0):
        raise ValueError("Direction consistency needs >=2 finite, non-zero effects")
    positive = int(np.sum(values > 0))
    negative = int(np.sum(values < 0))
    return {
        "k": len(values),
        "positive": positive,
        "negative": negative,
        "fully_concordant": positive == 0 or negative == 0,
        "majority_fraction": max(positive, negative) / len(values),
        "random_sign_complete_agreement": 2 * 0.5 ** len(values),
        "random_sign_majority_expectation": 0.75,
    }
