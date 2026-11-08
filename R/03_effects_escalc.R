# Step 03 - Per-cohort effect sizes with metafor::escalc.
#
# Manuscript (Methods, "Effect-size definitions"):
#   metafor 5.0.1 escalc. measure = "SMDH" for cohorts contributing
#   independent samples; measure = "SMCRPH" (standardised mean change,
#   raw-score standardisation, paired form) for paired cohorts. Both measures
#   standardise the mean difference by sdpi = sqrt((sd_case^2 + sd_control^2)/2)
#   and apply the small-sample bias correction J implemented in escalc.
#   vtype = "LS" (Bonett heteroscedastic large-sample variance).
#   The paired form uses the number of complete pairs and the cohort's
#   empirical within-pair correlation r (estimated from complete pairs, used
#   as a fixed value in the primary analysis; r = 0.5 and r = 0.7 are the two
#   fixed-correlation sensitivity analyses). Effect direction is case minus
#   control: a positive effect means a higher score in cases.
#
# Inputs (deposit): per-cohort group summaries of the module z-scores
#   (mean, SD, n per arm; complete-pair count and empirical within-pair r for
#   paired cohorts). These are derived from 04_modules/sample_module_scores_
#   gsva_z.csv joined to 02_sample_annotation/. The full-precision shipped
#   values live in 07_estimates/per_cohort_effects.csv and are NOT printed in
#   full in the manuscript tables; see data/placeholders/README.md.
# Outputs: per-cohort yi/vi per module (recomputed).

source(file.path("R", "config.R"))

# One row per cohort-module pair. group_stats must carry, per pair:
#   accession, module, design ("paired"/"unpaired"),
#   mean_case, sd_case, n_case, mean_control, sd_control, n_control,
#   and for paired cohorts npair and r_emp (empirical within-pair correlation).
compute_effects <- function(group_stats, vtype = "LS") {
  if (!requireNamespace("metafor", quietly = TRUE)) {
    stop("metafor 5.0.1 is required (pinned in environment.txt)")
  }
  rows <- vector("list", nrow(group_stats))
  for (i in seq_len(nrow(group_stats))) {
    g <- group_stats[i, ]
    if (g$design == "paired") {
      esc <- metafor::escalc(
        measure = "SMCRPH",
        m1i = g$mean_case, m2i = g$mean_control,
        sd1i = g$sd_case, sd2i = g$sd_control,
        ni = g$npair, ri = g$r_emp,
        vtype = vtype
      )
      measure <- "SMCRPH"
    } else {
      esc <- metafor::escalc(
        measure = "SMDH",
        m1i = g$mean_case, m2i = g$mean_control,
        sd1i = g$sd_case, sd2i = g$sd_control,
        n1i = g$n_case, n2i = g$n_control,
        vtype = vtype
      )
      measure <- "SMDH"
    }
    rows[[i]] <- data.frame(
      accession = g$accession, module = g$module, design = g$design,
      measure = measure, yi = esc$yi[1], vi = esc$vi[1],
      stringsAsFactors = FALSE
    )
  }
  do.call(rbind, rows)
}

# Fixed-correlation sensitivity: recompute paired cohorts with r fixed at
# 0.5 and 0.7 (manuscript, "Sensitivity analyses").
fixed_r_sensitivity <- function(group_stats, r_fixed) {
  paired <- group_stats$design == "paired"
  group_stats$r_emp[paired] <- r_fixed
  compute_effects(group_stats)
}

main <- function() {
  cfg <- load_config()
  group_stats <- read.csv(
    deposit_file(cfg, "07_estimates", "per_cohort_group_summaries.csv"),
    stringsAsFactors = FALSE
  )
  effects <- compute_effects(group_stats, vtype = cfg$effect_sizes$vtype)
  write.csv(
    effects,
    file.path(output_dir(cfg), "per_cohort_effects.csv"),
    row.names = FALSE
  )
  for (r_fixed in cfg$effect_sizes$sensitivity_r) {
    sens <- fixed_r_sensitivity(group_stats, r_fixed)
    write.csv(
      sens,
      file.path(
        output_dir(cfg),
        sprintf("per_cohort_effects_fixed_r_%.1f.csv", r_fixed)
      ),
      row.names = FALSE
    )
  }
}

if (sys.nframe() == 0L) main()
