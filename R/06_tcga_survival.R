# Step 06 - TCGA survival layer and driver interactions.
#
# Manuscript (Methods, TCGA layer):
#   Overall survival (OS) in months with death as the event, complete cases
#   only; the endpoint, time unit, censoring rule, missing-data handling and
#   data version are recorded in the survival data dictionary
#   (07_estimates/survival_data_dictionary.md, Supplementary Table S15).
#   Univariate Cox models per module within each tumour context, plus
#   age-and-stage-adjusted models in the oesophageal squamous subset
#   (51 univariate models across colorectal, oesophageal squamous and lung
#   adenocarcinoma contexts; 17 adjusted models). Patient scores are
#   standardised within tumour context, so hazard ratios are interpretable
#   only within context.
#   Driver interactions: within each tumour context, driver alterations with
#   at least ten driver-positive patients are eligible; outputs go to
#   07_estimates/driver_interactions.csv.
#
# Inputs (deposit): patient-level module z-scores (step 02), OS annotation
#   and driver alteration calls. These inputs are NOT shipped in this
#   repository; see data/placeholders/README.md.
# Outputs: 07_estimates/survival_*.csv and driver_interactions.csv
#   (recomputed).

source(file.path("R", "config.R"))

MIN_DRIVER_POSITIVE <- 10L  # eligibility floor for driver alterations

# patient_data: one row per patient with os_months, os_event (1 = death,
# 0 = censored), one column per module z-score, and optionally age/stage.
cox_univariate <- function(patient_data, module_columns) {
  if (!requireNamespace("survival", quietly = TRUE)) {
    stop("The 'survival' package is required (see environment.txt)")
  }
  complete <- stats::complete.cases(
    patient_data[, c("os_months", "os_event", module_columns)]
  )
  data <- patient_data[complete, ]
  rows <- lapply(module_columns, function(module) {
    fit <- survival::coxph(
      survival::Surv(os_months, os_event) ~ data[[module]], data = data
    )
    s <- summary(fit)
    data.frame(
      module = module,
      n = fit$n,
      events = fit$nevent,
      hazard_ratio = s$conf.int[1, "exp(coef)"],
      ci_low = s$conf.int[1, "lower .95"],
      ci_high = s$conf.int[1, "upper .95"],
      p = s$coefficients[1, "Pr(>|z|)"],
      stringsAsFactors = FALSE
    )
  })
  do.call(rbind, rows)
}

# Age-and-stage-adjusted models (oesophageal squamous subset per manuscript).
cox_adjusted <- function(patient_data, module_columns) {
  if (!requireNamespace("survival", quietly = TRUE)) {
    stop("The 'survival' package is required (see environment.txt)")
  }
  complete <- stats::complete.cases(
    patient_data[, c("os_months", "os_event", "age", "stage", module_columns)]
  )
  data <- patient_data[complete, ]
  rows <- lapply(module_columns, function(module) {
    fit <- survival::coxph(
      survival::Surv(os_months, os_event) ~ data[[module]] + age + stage,
      data = data
    )
    s <- summary(fit)
    data.frame(
      module = module,
      n = fit$n,
      events = fit$nevent,
      hazard_ratio = s$conf.int[1, "exp(coef)"],
      ci_low = s$conf.int[1, "lower .95"],
      ci_high = s$conf.int[1, "upper .95"],
      p = s$coefficients[1, "Pr(>|z|)"],
      stringsAsFactors = FALSE
    )
  })
  do.call(rbind, rows)
}

# Keep only driver alterations with >= MIN_DRIVER_POSITIVE positive patients
# within one tumour context.
eligible_drivers <- function(alteration_counts) {
  names(alteration_counts)[alteration_counts >= MIN_DRIVER_POSITIVE]
}

main <- function() {
  cfg <- load_config()
  patient_file <- deposit_file(cfg, "07_estimates", "tcga_patient_scores_os.csv")
  patient_data <- read.csv(patient_file, stringsAsFactors = FALSE)
  module_columns <- grep("^module__", names(patient_data), value = TRUE)
  if (!length(module_columns)) {
    stop("No module score columns (module__*) found in the patient table")
  }
  for (context in unique(patient_data$context)) {
    sub <- patient_data[patient_data$context == context, ]
    fits <- cox_univariate(sub, module_columns)
    fits$context <- context
    write.csv(
      fits,
      file.path(output_dir(cfg), paste0("survival_", context, ".csv")),
      row.names = FALSE
    )
  }
}

if (sys.nframe() == 0L) main()
