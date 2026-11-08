# Step 02 - TCGA layer: patient-level member-mean z-scores.
#
# Manuscript (Methods, "Scoring rules", layer 2):
#   Patient-level module scores are the mean expression of the member genes
#   retained in the tumour matrix, z-standardised across the patients of the
#   same tumour context (the squamous oesophageal subset is standardised
#   within that subset). Higher values mean higher member-gene expression.
#   Because standardisation is within context, these scores are NOT on a
#   common absolute scale across tumour types and must not be concatenated
#   with the bulk or single-cell layers.
#
# Inputs (deposit): 04_modules/module_definitions.csv and the TCGA processed
# matrices (one per tumour context; see data/placeholders/README.md).
# Outputs: patient-level module z-scores per tumour context.

source(file.path("R", "config.R"))

# expression_matrix: genes x patients (rownames are symbols).
# Returns a matrix modules x patients of within-context z-scores.
tcga_member_mean_z <- function(expression_matrix, module_sets) {
  present <- rownames(expression_matrix)
  out <- matrix(NA_real_, nrow = length(module_sets),
                ncol = ncol(expression_matrix),
                dimnames = list(names(module_sets), colnames(expression_matrix)))
  for (module in names(module_sets)) {
    retained <- intersect(module_sets[[module]], present)
    if (length(retained) < 3L) next  # same >=3 member floor as the bulk layer
    member_mean <- colMeans(expression_matrix[retained, , drop = FALSE])
    out[module, ] <- as.numeric(scale(member_mean))
  }
  out
}

main <- function() {
  cfg <- load_config()
  module_definitions <- read.csv(
    deposit_file(cfg, "04_modules", "module_definitions.csv"),
    stringsAsFactors = FALSE
  )
  module_sets <- split(module_definitions$gene, module_definitions$module)
  # One processed tumour matrix per TCGA context; file names follow the
  # deposit layout (03_expression/). Contexts per the manuscript:
  # TCGA-LUAD, TCGA-COADREAD, TCGA-STAD, TCGA-PAAD, TCGA-LIHC, TCGA-ESCA.
  contexts <- c("TCGA-LUAD", "TCGA-COADREAD", "TCGA-STAD",
                "TCGA-PAAD", "TCGA-LIHC", "TCGA-ESCA")
  for (context in contexts) {
    matrix_path <- deposit_file(
      cfg, "03_expression", paste0(context, "_tumour_matrix.csv")
    )
    expression_matrix <- as.matrix(
      read.csv(matrix_path, row.names = 1, check.names = FALSE)
    )
    z <- tcga_member_mean_z(expression_matrix, module_sets)
    write.csv(
      z, file.path(output_dir(cfg), paste0(context, "_module_scores_member_mean_z.csv"))
    )
  }
}

if (sys.nframe() == 0L) main()
