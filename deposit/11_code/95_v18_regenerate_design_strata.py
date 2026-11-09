#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Regenerate 07_estimates/meta_by_design_stratum.csv from the frozen per-cohort effects.

Same pooling and inference rule as 07_estimates/meta_primary_reml_knha.csv:
REML heterogeneity, inverse-variance weights, Hartung-Knapp variance, t on k-1 df.
Reads 07_estimates/per_cohort_effects.csv; writes the design-stratified table.
"""
import os
import numpy as np
import pandas as pd
from scipy import stats, optimize

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ef = pd.read_csv(os.path.join(ROOT, "07_estimates", "per_cohort_effects.csv"))


def pool(y, v):
    def dev(tau2):
        w = 1.0 / (v + tau2); sw = w.sum(); ybar = (w * y).sum() / sw
        return np.sum(np.log(v + tau2)) + np.log(sw) + (w * (y - ybar) ** 2).sum()
    tau2 = max(0.0, float(optimize.minimize_scalar(dev, bounds=(0, 500), method="bounded").x))
    w = 1.0 / (v + tau2); sw = w.sum()
    est = float((w * y).sum() / sw)
    se = float(np.sqrt(((w * (y - est) ** 2).sum()) / (sw * (len(y) - 1))))
    tq = float(stats.t.ppf(0.975, len(y) - 1))
    p = float(2 * stats.t.sf(abs(est) / se, len(y) - 1))
    return est, se, p, tau2, est - tq * se, est + tq * se


out = []
for (dis, feat), g in ef[ef.yi.notna()].groupby(["disease", "feature"]):
    g = g[g.vi > 0]
    strata = [("all cohorts", g)]
    if len(g[g.paired]) >= 2:
        strata.append(("paired cohorts only", g[g.paired]))
    if len(g[~g.paired]) >= 2:
        strata.append(("unpaired cohorts only", g[~g.paired]))
    for name, sub in strata:
        if len(sub) < 2:
            continue
        est, se, p, tau2, lo, hi = pool(sub.yi.values.astype(float), sub.vi.values.astype(float))
        out.append(dict(disease=dis, feature=feat, stratum=name, k=len(sub),
                        cohorts=";".join(sub.accession),
                        measures="|".join(f"{m} {n}" for m, n in sub.measure.value_counts().items()),
                        est=est, se=se, p=p, tau2=tau2, ci_lo=lo, ci_hi=hi,
                        inference="REML, Hartung-Knapp variance, t(k-1)"))
d = pd.DataFrame(out)
d["fdr_within_disease"] = np.nan
for (dis, strat), idx in d.groupby(["disease", "stratum"]).groups.items():
    d.loc[idx, "fdr_within_disease"] = stats.false_discovery_control(d.loc[idx, "p"].values, method="bh")
d.to_csv(os.path.join(ROOT, "07_estimates", "meta_by_design_stratum.csv"), index=False)
print("rows:", len(d))
