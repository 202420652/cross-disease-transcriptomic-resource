# Analysis code shipped with the deposit

These 14 scripts reproduce the resource end to end: per-cohort effects and pooling (41), common-gene sensitivity (40),
proportional-hazards and collinearity diagnostics (42), composition keying (43), marker-based composition and expression QC (66),
module overlap/curation/coverage additions (65), figure generation (60), the two layout-QA reviewers (64, 77),
the reusable single-cell re-analysis (22) and the manuscript/table builders (70, 71).

Environment: R 4.4.1 (GSVA 1.52.3, metafor 5.0.1, survival 3.8.3, limma 3.60.6, GEOquery, xCell 1.0.0, ggplot2 4.0.3,
patchwork 1.3.2, tidyr, dplyr) and Python 3.11 (numpy, pandas, python-docx, Pillow). Paths inside the scripts point to the
author's working directories and must be adjusted to the deposit layout (see 10_environment/run_order.md).
