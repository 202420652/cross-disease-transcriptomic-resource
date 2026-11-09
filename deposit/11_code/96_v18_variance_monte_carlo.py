#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Monte Carlo validation of the sampling variance used for the unpaired effects.

Variance: heteroscedastic large-sample variance of Bonett, as implemented in
metafor::escalc(measure = "SMDH", vtype = "LS"):
  v = y^2 (s1^4/(n1-1) + s2^4/(n2-1)) / (8 sdpi^4) + (s1^2/(n1-1) + s2^2/(n2-1)) / sdpi^2
Effect generated as case minus control (positive = higher in cases).
"""
import os
import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rng = np.random.default_rng(20261105)
REPS = 4000


def stats_smdh(m1, s1, n1, m2, s2, n2):
    sdpi = np.sqrt((s1 ** 2 + s2 ** 2) / 2.0)
    cmi = 1.0 - 3.0 / (4.0 * (n1 + n2) - 9.0)
    y = cmi * (m1 - m2) / sdpi
    v = (y ** 2) * (s1 ** 4 / (n1 - 1) + s2 ** 4 / (n2 - 1)) / (8 * sdpi ** 4) + \
        (s1 ** 2 / (n1 - 1) + s2 ** 2 / (n2 - 1)) / sdpi ** 2
    return y, v


conds = [(8, 8, 1, 1, 0), (8, 8, 1, 1, .3), (8, 8, 1, 1, .8),
         (12, 12, 1, 1, 0), (12, 12, 1, 1, .3), (12, 12, 1, 1, .8),
         (20, 20, 1, 1, 0), (20, 20, 1, 1, .3), (20, 20, 1, 1, .8),
         (40, 40, 1, 1, 0), (40, 40, 1, 1, .3), (40, 40, 1, 1, .8),
         (60, 30, 1, 1, 0), (60, 30, 1, 1, .3), (60, 30, 1, 1, .8),
         (20, 20, 1, 2, .5), (20, 20, 2, .5, .5), (60, 15, 1, 1, .5),
         (60, 15, 1, 2, .5), (15, 60, 2, 1, 0)]
rows = []
for n1, n2, s1, s2, delta in conds:
    est = np.empty(REPS); var = np.empty(REPS)
    for r in range(REPS):
        x1 = rng.normal(delta, s1, n1); x2 = rng.normal(0.0, s2, n2)
        est[r], var[r] = stats_smdh(x1.mean(), x1.std(ddof=1), n1, x2.mean(), x2.std(ddof=1), n2)
    half = 1.959963985 * np.sqrt(var)
    rows.append(dict(n_case=n1, n_control=n2, sd_case=s1, sd_control=s2, true_delta=delta,
                     mean_estimate=round(float(est.mean()), 4),
                     empirical_variance=round(float(est.var(ddof=1)), 6),
                     analytic_variance=round(float(var.mean()), 6),
                     ratio_analytic_over_empirical=round(float(var.mean() / est.var(ddof=1)), 3),
                     coverage_of_analytic_95CI=round(float(np.mean(np.abs(est - delta) <= half)), 3),
                     sign_convention="delta = case - control", replicates=REPS))
d = pd.DataFrame(rows)
d.to_csv(os.path.join(ROOT, "08_qc", "qc_smdh_variance_monte_carlo.csv"), index=False)
print(d[["ratio_analytic_over_empirical", "coverage_of_analytic_95CI"]].describe())
