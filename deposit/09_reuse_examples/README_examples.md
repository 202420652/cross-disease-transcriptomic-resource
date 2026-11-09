# Reuse examples

Run from the dataset package root so that relative paths resolve.

1. `example1_replace_module_gene_set.R` — swap in your own gene set, re-score one cohort, and compare with the frozen definition; prints how many members are actually present per set (coverage awareness).
2. `example2_recompute_composition_scheme.R` — recompute the base-versus-adjusted comparison from the shipped estimates and report the median adjusted/base coefficient ratio.

Both examples write to `expected_output/`. If a file is missing, the example did not complete.

## Example 3 - external cohort rebuilt from its accession (executed)
`example3_external_cohort_rebuild.R` (kept in `scripts/` of the working folder) downloads a gastric cancer series that is **not** part of
the resource (GSE54129; 111 tumour and 21 adjacent-normal samples), maps probes to symbols, applies the same deterministic transformation
rule, scores the frozen modules and compares the effect directions with the pooled gastric estimates of the resource.

Result of the executed run (`example3_external_cohort_summary.txt`, `example3_external_cohort_rebuild.csv`):
all 17 modules were scorable, the direction agreed for 9 of 17 modules, and the complete path took **1.6 minutes**.
This documents reuse cost and the limits of cross-cohort direction agreement; it is not an external validation claim.

## Note on the demo matrix

The demo matrix shipped for example 1 is a real 1,298-gene x 20-sample subset of GSE13911 (its GSM identifiers match the sample annotation table),
not synthetic data; `demo_sample_metadata.csv` carries the corresponding sample identifiers and case/control labels.
