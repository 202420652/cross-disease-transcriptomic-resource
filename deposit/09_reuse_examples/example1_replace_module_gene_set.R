#!/usr/bin/env Rscript
# Reuse example 1: replace a module gene set and re-score one cohort.
# Input: dataset_package/03_expression (or your own processed matrix) + 04_modules/module_definitions.csv
suppressPackageStartupMessages(library(GSVA))
dir.create("09_reuse_examples/expected_output", recursive=TRUE, showWarnings=FALSE)
expr <- as.matrix(read.csv("09_reuse_examples/example_input/demo_expression_matrix.csv", row.names=1, check.names=FALSE))  # 1298 genes x 20 samples (a real subset of GSE13911) (shipped demo; point this at your own matrix)
rownames(expr) <- toupper(rownames(expr))   # gene symbols are matched case-insensitively
genes <- read.csv("04_modules/module_definitions.csv")
my_set <- list(MY_MODULE = c("EGFR","ERBB2","ERBB3","AREG","HBEGF"))              # replace with your own set
# keep the frozen definition for the same module to compare
frozen <- unique(toupper(genes$gene[genes$module == "ERBB_RECEPTORS"]))
sets <- list(MY_MODULE = intersect(my_set$MY_MODULE, rownames(expr)),
             FROZEN_ERBB_RECEPTORS = intersect(frozen, rownames(expr)))
print(sapply(sets, length))                       # how many members are actually present
if (any(sapply(sets, length) == 0)) stop("No gene-set members matched the matrix: check that rownames are gene symbols (the demo matrix uses symbols).")
sc <- GSVA::gsva(GSVA::gsvaParam(expr, sets, minSize=3, kcdf="Gaussian"), verbose=FALSE)
sc_z <- t(scale(t(sc)))
out <- as.data.frame(t(sc_z)); out <- cbind(sample_id = rownames(out), out)
write.csv(out, "09_reuse_examples/expected_output/example1_module_scores.csv", row.names = FALSE)
cat("example 1 done: scores written for", nrow(sc),"module(s)\n")
