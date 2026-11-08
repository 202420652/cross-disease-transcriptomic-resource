# run_all.R - execute the pipeline steps in order.
#
# Mirrors 10_environment/run_order.md of the deposit. Every step resolves
# paths through config.yml and stops with an explicit message if a required
# deposit input is missing (this repository ships code and printed reference
# tables only; see data/placeholders/README.md).
#
# Usage:
#   1. Edit config.yml and set root_dir to the extracted deposit.
#   2. From the repository root: Rscript R/run_all.R

steps <- c(
  "R/01_score_bulk_gsva.R",
  "R/02_tcga_scores.R",
  "R/03_effects_escalc.R",
  "R/04_pool_metafor.R",
  "R/05_xcell_composition.R",
  "R/06_tcga_survival.R"
)

for (step in steps) {
  message("=== ", step, " ===")
  source(step)
}
message("All steps finished.")
