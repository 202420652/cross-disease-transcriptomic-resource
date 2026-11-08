"""Independent Monte Carlo check of the SMDH closed-form variance.

Mirrors Supplementary Table S27: for a grid of group sizes, SD ratios and
true standardised effects, case and control samples are simulated from
normal distributions, the SMDH estimator (this repository's own
implementation, which shares no code with metafor) is applied to each
replicate, and the empirical variance of the estimates is compared with the
analytic large-sample variance. The true mean difference is generated as
delta = d * sdpi, so the simulation target and the estimator's
standardisation denominator coincide.

NOTE (carried over from the manuscript's unresolved items): in the printed
S27 grid, rows with unequal SDs label "True effect" with the RAW mean
difference rather than the standardised effect, which is why those rows show
mean estimates near 0.32 for a stated 0.5. That labelling is under
re-evaluation by the authors; this script uses the standardised target.

Usage:
    python scripts/verify_independent_implementation.py [--replicates 20000]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from cdtr.effect_sizes import bias_correction, smdh  # noqa: E402

GRID = [
    # (n_case, n_control, sd_case, sd_control, true standardised effect)
    (8, 8, 1.0, 1.0, 0.0),
    (8, 8, 1.0, 1.0, 0.3),
    (8, 8, 1.0, 1.0, 0.8),
    (20, 20, 1.0, 1.0, 0.0),
    (20, 20, 1.0, 1.0, 0.8),
    (40, 40, 1.0, 1.0, 0.3),
    (60, 30, 1.0, 1.0, 0.5),
    (20, 20, 1.0, 2.0, 0.5),
    (20, 20, 2.0, 0.5, 0.5),
]


def simulate(n_case, n_control, sd_case, sd_control, effect, replicates, seed):
    rng = np.random.default_rng(seed)
    sdpi = np.sqrt((sd_case**2 + sd_control**2) / 2)
    delta = effect * sdpi
    estimates = np.empty(replicates)
    for i in range(replicates):
        case = rng.normal(delta, sd_case, n_case)
        control = rng.normal(0.0, sd_control, n_control)
        est = smdh(
            case.mean(), control.mean(),
            case.std(ddof=1), control.std(ddof=1),
            n_case, n_control,
        )
        estimates[i] = est.yi
    analytic = smdh(delta, 0.0, sd_case, sd_control, n_case, n_control).vi
    return estimates, analytic


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--replicates", type=int, default=20000)
    parser.add_argument("--seed", type=int, default=20261108)
    args = parser.parse_args()

    header = (
        f"{'n1':>4} {'n2':>4} {'s1':>4} {'s2':>4} {'d':>5} "
        f"{'mean_est':>9} {'emp_var':>9} {'analytic':>9} {'ratio':>7}"
    )
    print(header)
    print("-" * len(header))
    for row_index, (n1, n2, s1, s2, d) in enumerate(GRID):
        estimates, analytic = simulate(n1, n2, s1, s2, d, args.replicates,
                                       args.seed + row_index)
        empirical = float(np.var(estimates, ddof=1))
        print(
            f"{n1:>4} {n2:>4} {s1:>4.1f} {s2:>4.1f} {d:>5.1f} "
            f"{estimates.mean():>9.4f} {empirical:>9.4f} {analytic:>9.4f} "
            f"{analytic / empirical:>7.3f}"
        )
    print(
        "\nExpected pattern (per S27): ratio near 1 with mild upward bias of "
        "the analytic variance at the smallest sample sizes."
    )
    print(f"bias_correction sanity: J(18) = {bias_correction(18):.6f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
