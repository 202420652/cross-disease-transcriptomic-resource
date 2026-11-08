# Step 01 - Bulk layer: per-cohort GSVA module scores.
#
# Manuscript (Methods, "Scoring rules", layer 1):
#   GSVA 1.52.3, gsvaParam, kcdf = "Gaussian", minSize = 3 (resource choice;
#   package default is 1), all other parameters at package defaults. Module
#   gene sets are restricted to the genes retained in each cohort; per-sample
#   scores are then z-standardised across the samples of that cohort.
#   All 26 cohorts are microarray platforms with continuous processed values,
#   so the Gaussian kernel is used for every cohort (no Poisson kernel).
#   A cohort-by-module pair with fewer than three retained members is not
#   scored and is reported as not estimable with that reason.
#
# Inputs (from the deposit, NOT shipped in this repository):
#   04_modules/module_definitions.csv          gene, module, role, source
#   03_expression/<processed matrix per cohort>  genes x samples, log-scaled
# Outputs:
#   04_modules/sample_module_scores_gsva_z.csv (recomputed)

source(file.path("R", "config.R"))

score_bulk_cohort <- function(expression_matrix, module_sets, min_size = 3L) {
  # expression_matrix: numeric matrix, genes x samples, rownames are symbols.
  # module_sets: named list of character vectors (module -> member genes).
  if (!requireNamespace("GSVA", quietly = TRUE)) {
    stop("GSVA 1.52.3 is required (pinned in environment.txt)")
  }
  not_estimable <- character(0)
  usable <- list()
  for (module in names(module_sets)) {
    retained <- intersect(module_sets[[module]], rownames(expression_matrix))
    if (length(retained) < min_size) {
      not_estimable <- c(not_estimable, module)
    } else {
      usable[[module]] <- retained
    }
  }
  if (!length(usable)) {
    stop("No module has >= ", min_size, " retained members in this cohort")
  }
  param <- GSVA::gsvaParam(
    exprData = as.matrix(expression_matrix),
    geneSets = usable,
    kcdf = "Gaussian",
    minSize = min_size
  )
  scores <- GSVA::gsva(param)
  # z-standardise each module's scores across the samples of this cohort.
  z_scores <- t(scale(t(scores)))
  list(scores = z_scores, not_estimable = not_estimable)
}

main <- function() {
  cfg <- load_config()
  module_definitions <- read.csv(
    deposit_file(cfg, "04_modules", "module_definitions.csv"),
    stringsAsFactors = FALSE
  )
  module_sets <- split(module_definitions$gene, module_definitions$module)
  registry <- read.csv(
    deposit_file(cfg, "01_cohort_registry", "cohort_registry.csv"),
    stringsAsFactors = FALSE
  )
  for (accession in registry$accession) {
    matrix_path <- deposit_file(
      cfg, "03_expression", paste0(accession, "_processed_matrix.csv")
    )
    expression_matrix <- as.matrix(
      read.csv(matrix_path, row.names = 1, check.names = FALSE)
    )
    result <- score_bulk_cohort(
      expression_matrix, module_sets, min_size = cfg$gsva$min_size
    )
    write.csv(
      result$scores,
      file.path(output_dir(cfg), paste0(accession, "_module_scores_gsva_z.csv"))
    )
    if (length(result$not_estimable)) {
      message(
        accession, ": not estimable (fewer than ", cfg$gsva$min_size,
        " retained members): ", paste(result$not_estimable, collapse = ", ")
      )
    }
  }
}

if (sys.nframe() == 0L) main()
