#!/usr/bin/env Rscript
# Reuse example 2: recompute the base-versus-adjusted comparison from the shipped composition summary.
# Run from the dataset package root: Rscript 09_reuse_examples/example2_recompute_composition_scheme.R
dir.create("09_reuse_examples/expected_output", recursive = TRUE, showWarnings = FALSE)
d <- read.csv("07_estimates/composition_model_summary.csv")
need <- c("disease", "feature", "median_beta_base", "median_beta_adj")
stopifnot(all(need %in% names(d)))
d$ratio <- abs(d$median_beta_adj) / abs(d$median_beta_base)      # per-row (per state) ratio
d$attenuation <- 1 - d$ratio
write.csv(d[, c("disease", "feature", "median_beta_base", "median_beta_adj", "ratio", "attenuation")],
          "09_reuse_examples/expected_output/example2_composition_ratio.csv", row.names = FALSE)
cat("example 2 done:", nrow(d), "states | median per-state adjusted/base ratio =", round(median(d$ratio, na.rm = TRUE), 3),
    "| overall ratio from column medians =", round(abs(median(d$median_beta_adj, na.rm=TRUE))/abs(median(d$median_beta_base, na.rm=TRUE)), 3), "\n")
