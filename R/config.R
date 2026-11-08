# Shared configuration helpers for the R pipeline.
#
# Every script resolves its paths through config.yml, so the pipeline runs
# from any directory once root_dir is set (manuscript, Code Availability).
# The data deposit itself is NOT part of this repository; scripts stop with
# an explicit message when a required deposit file is missing.

load_config <- function(config_path = "config.yml") {
  if (!requireNamespace("yaml", quietly = TRUE)) {
    stop("The 'yaml' package is required to read config.yml")
  }
  cfg <- yaml::read_yaml(config_path)
  if (is.null(cfg$root_dir) || !nzchar(cfg$root_dir)) {
    stop(
      "config.yml: root_dir is empty. Point it at the extracted data deposit ",
      "(folders 01_cohort_registry/ ... 10_environment/). See ",
      "data/placeholders/README.md for the inputs that are not shipped here."
    )
  }
  if (!dir.exists(cfg$root_dir)) {
    stop("config.yml: root_dir does not exist: ", cfg$root_dir)
  }
  cfg
}

# Resolve a path inside the deposit and stop with a clear message if absent.
deposit_file <- function(cfg, ...) {
  path <- file.path(cfg$root_dir, ...)
  if (!file.exists(path)) {
    stop(
      "Required deposit file is missing: ", path, "\n",
      "This repository ships code and printed reference tables only; see ",
      "data/placeholders/README.md."
    )
  }
  path
}

output_dir <- function(cfg) {
  dir.create(cfg$output_dir, showWarnings = FALSE, recursive = TRUE)
  cfg$output_dir
}
