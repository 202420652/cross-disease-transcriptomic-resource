# Step 05 - Tissue-compartment scores with xCell.
#
# Manuscript (Methods, "Composition scores"):
#   xCell v1.1.0, called as xCell::xCellAnalysis(expression_matrix) with
#   package defaults, which include rnaseq = TRUE and scale = TRUE, on every
#   cohort's processed matrix. Four compartment scores are used, each a direct
#   xCell output with no aggregation or weighting: epithelial ("Epithelial
#   cells"), fibroblast ("Fibroblasts"), endothelial ("Endothelial cells")
#   and immune ("ImmuneScore"). The scores are enrichment scores, not
#   proportions.
#
# KNOWN DEVIATION (disclosed in the manuscript): all 26 cohorts are
# microarray matrices, so the shipped scores use xCell's RNA-seq calibration
# on microarray data. A platform-matched recomputation with rnaseq = FALSE,
# scale = TRUE, alpha = 0.5 is REQUIRED before the compartment layer can be
# read as more than an auxiliary annotation; the shipped rnaseq = TRUE
# results are retained as a documented sensitivity version. No conclusion in
# the resource depends on the absolute level of a compartment score.
#
# Inputs (deposit): per-cohort processed expression matrices (03_expression/).
# Outputs: 05_composition/xcell_composition_scores.csv (recomputed) and the
#   platform-matched sensitivity table.

source(file.path("R", "config.R"))

COMPARTMENTS <- c(
  epithelial = "Epithelial cells",
  fibroblast = "Fibroblasts",
  endothelial = "Endothelial cells",
  immune = "ImmuneScore"
)

xcell_compartments <- function(expression_matrix, rnaseq = TRUE,
                               scale = TRUE, alpha = 0.5) {
  if (!requireNamespace("xCell", quietly = TRUE)) {
    stop("xCell 1.1.0 is required (pinned in environment.txt)")
  }
  scores <- xCell::xCellAnalysis(
    expression_matrix, rnaseq = rnaseq, scale = scale, alpha = alpha
  )
  missing <- setdiff(COMPARTMENTS, rownames(scores))
  if (length(missing)) {
    stop("xCell output lacks expected rows: ", paste(missing, collapse = ", "))
  }
  scores[COMPARTMENTS, , drop = FALSE]
}

main <- function() {
  cfg <- load_config()
  registry <- read.csv(
    deposit_file(cfg, "01_cohort_registry", "cohort_registry.csv"),
    stringsAsFactors = FALSE
  )
  for (accession in registry$accession) {
    expression_matrix <- as.matrix(read.csv(
      deposit_file(cfg, "03_expression", paste0(accession, "_processed_matrix.csv")),
      row.names = 1, check.names = FALSE
    ))
    shipped <- xcell_compartments(expression_matrix)  # rnaseq = TRUE as shipped
    write.csv(
      shipped,
      file.path(output_dir(cfg), paste0(accession, "_xcell_rnaseqTRUE.csv"))
    )
    sensitivity <- xcell_compartments(
      expression_matrix, rnaseq = FALSE, scale = TRUE, alpha = 0.5
    )
    write.csv(
      sensitivity,
      file.path(output_dir(cfg), paste0(accession, "_xcell_platform_matched.csv"))
    )
  }
}

if (sys.nframe() == 0L) main()
