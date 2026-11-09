#!/usr/bin/env Rscript
# Minimal entry point: reads config.yml and runs the shipped steps in order.
# Usage:  Rscript run_all.R [root_dir]
args <- commandArgs(trailingOnly = TRUE)
root <- if (length(args) >= 1) args[[1]] else "."
cfg  <- file.path(root, "11_code", "config.yml")
stopifnot(file.exists(cfg))
rd <- function(key) {
  lines <- readLines(cfg)
  setwd(root)
  switch(key, expression = "03_expression", estimates = "07_estimates", qc = "08_qc", single_cell = "06_single_cell", registry = "01_cohort_registry")
}
message("root: ", normalizePath(root))
steps <- c(
  "03_expression/download_and_rebuild_one_series.R",  # per-accession download + rebuild (reuse examples)
  "09_reuse_examples/example1_rebuild_one_cohort.R",
  "09_reuse_examples/example2_rebuild_one_state.R"
)
for (s in steps) {
  p <- file.path(root, s)
  if (file.exists(p)) { message("running ", s); system2("Rscript", shQuote(p)) } else message("skipped (not shipped): ", s)
}
message("done")
