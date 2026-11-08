# Step 04 - Random-effects pooling and inference with metafor::rma.uni.
#
# Manuscript (Methods, "Pooling and inference" and "Multiplicity control"):
#   Within each disease context, estimable cohorts are pooled with
#   rma.uni(yi, vi), REML heterogeneity estimation and the Hartung-Knapp
#   variance correction (t distribution on k - 1 degrees of freedom).
#   Pooled estimates are reported only when k >= 2 cohorts contribute.
#   k = 2 states are annotated "two-cohort summary; heterogeneity
#   uninformative" rather than treated as meta-analytic estimates.
#   95% prediction intervals are reported for k >= 3 (for k = 3 they rest on
#   one degree of freedom and are reported for completeness only).
#   Multiplicity: Benjamini-Hochberg within disease context (the joint
#   primary table forms one family per context; the design-stratified table
#   forms its own families per context and stratum, and the two sets of
#   adjusted p values are not interchangeable).
#
# Inputs: per-cohort effects from step 03 (or the shipped
#   07_estimates/per_cohort_effects.csv for internal reproducibility).
# Outputs: meta_primary_reml_knha.csv and meta_by_design_stratum.csv
#   (recomputed).

source(file.path("R", "config.R"))

pool_state <- function(yi, vi, test = "knha") {
  if (!requireNamespace("metafor", quietly = TRUE)) {
    stop("metafor 5.0.1 is required (pinned in environment.txt)")
  }
  fit <- metafor::rma.uni(yi = yi, vi = vi, method = "REML", test = test)
  k <- fit$k
  pi_low <- pi_high <- NA_real_
  if (k >= 3) {
    pred <- predict(fit)
    pi_low <- pred$pi.lb
    pi_high <- pred$pi.ub
  }
  data.frame(
    k = k,
    effect = as.numeric(fit$beta),
    se = fit$se,
    p = fit$pval,
    ci_low = fit$ci.lb,
    ci_high = fit$ci.ub,
    tau2 = fit$tau2,
    i2 = fit$I2,
    pi_low = pi_low,
    pi_high = pi_high,
    annotation = if (k == 2) {
      "two-cohort summary; heterogeneity uninformative"
    } else {
      "REML + Hartung-Knapp"
    },
    stringsAsFactors = FALSE
  )
}

# Pool one context-module state; states with a single contributing cohort are
# kept and labelled, with no p value or intervals (manuscript convention).
pool_all_states <- function(effects, context_key = "context") {
  keys <- interaction(effects[[context_key]], effects$module, drop = TRUE)
  out <- vector("list", length(levels(keys)))
  for (j in seq_along(levels(keys))) {
    sub <- effects[keys == levels(keys)[j], ]
    pooled <- if (nrow(sub) >= 2) {
      pool_state(sub$yi, sub$vi)
    } else {
      data.frame(
        k = nrow(sub), effect = sub$yi, se = sqrt(sub$vi),
        p = NA_real_, ci_low = NA_real_, ci_high = NA_real_,
        tau2 = NA_real_, i2 = NA_real_, pi_low = NA_real_, pi_high = NA_real_,
        annotation = "single cohort; not a pooled estimate",
        stringsAsFactors = FALSE
      )
    }
    pooled$context <- sub[[context_key]][1]
    pooled$module <- sub$module[1]
    out[[j]] <- pooled
  }
  result <- do.call(rbind, out)
  # BH within disease context, over poolable states only.
  result$bh_adj_p <- NA_real_
  for (context in unique(result$context)) {
    rows <- which(result$context == context & !is.na(result$p))
    result$bh_adj_p[rows] <- p.adjust(result$p[rows], method = "BH")
  }
  result
}

main <- function() {
  cfg <- load_config()
  effects <- read.csv(
    deposit_file(cfg, "07_estimates", "per_cohort_effects.csv"),
    stringsAsFactors = FALSE
  )
  estimable <- effects[!is.na(effects$yi), ]
  primary <- pool_all_states(estimable)
  write.csv(
    primary,
    file.path(output_dir(cfg), "meta_primary_reml_knha.csv"),
    row.names = FALSE
  )
  # Pre-specified secondary analysis: pool separately within the paired
  # (SMCRPH) and unpaired (SMDH) strata; each context-stratum is its own
  # BH family.
  for (stratum in c("paired", "unpaired")) {
    sub <- estimable[estimable$design == stratum, ]
    stratified <- pool_all_states(sub)
    write.csv(
      stratified,
      file.path(output_dir(cfg), paste0("meta_by_design_stratum_", stratum, ".csv")),
      row.names = FALSE
    )
  }
}

if (sys.nframe() == 0L) main()
