#!/usr/bin/env Rscript
# v16: resolve the deposit root from this script so that the example runs from a clean copy.
args <- commandArgs(trailingOnly = TRUE)
script_dir <- function() {
  a <- commandArgs(trailingOnly = FALSE); f <- sub("^--file=", "", a[grep("^--file=", a)])
  if (length(f)) normalizePath(dirname(f)) else getwd()
}
root <- if (length(args) >= 1) normalizePath(args[[1]]) else {
  d <- script_dir(); while (!file.exists(file.path(d, "00_VERSION.txt")) && dirname(d) != d) d <- dirname(d); d
}
setwd(root)
message("deposit root: ", root)
# Runnable pathway from a public accession to a processed matrix and module scores for one cohort.
# Usage: Rscript download_and_rebuild_one_series.R GSE13911
# Requires: GEOquery, limma, GSVA.
args <- commandArgs(trailingOnly = TRUE)
acc <- if (length(args) >= 1) args[1] else "GSE13911"
suppressPackageStartupMessages({library(GEOquery); library(GSVA); library(dplyr)})
# 1. download the series matrix from GEO and take the first expression matrix
gse <- getGEO(acc, GSEMatrix = TRUE, getGPL = TRUE)
eset <- gse[[1]]
expr <- Biobase::exprs(eset)
# transformation rule recorded per cohort in 03_expression/transformation_log.csv (input maximum and integer fraction);
# the approximation below mirrors that decision for a fresh series
if (max(expr, na.rm = TRUE) > 50 && mean(abs(expr - round(expr)) < 1e-8, na.rm = TRUE) > 0.9) expr <- log2(expr + 1)
md <- Biobase::pData(eset)
# 2. map probes to gene symbols (platform annotation; fall back to the feature data column)
fd <- Biobase::fData(eset)
sym_col <- intersect(c("Gene symbol","Gene Symbol","GENE_SYMBOL","Symbol","gene_assignment","ORF","ILMN_Gene"), names(fd))[1]
if (is.na(sym_col)) {                      # fall back to the platform annotation table shipped with the series
  gpl <- tryCatch(GEOquery::getGEO(Biobase::annotation(eset)), error = function(e) NULL)
  if (!is.null(gpl)) {
    tab <- GEOquery::Table(gpl)
    cand <- intersect(c("Gene symbol","Gene Symbol","GENE_SYMBOL","Symbol","gene_assignment"), names(tab))
    if (length(cand)) { fd <- data.frame(row.names = as.character(tab$ID), sym = as.character(tab[[cand[1]]])); sym_col <- "sym" }
  }
}
cat("using annotation column:", ifelse(is.na(sym_col), "NONE", sym_col), "\n")
if (!is.na(sym_col)) {
  sym <- toupper(as.character(fd[[sym_col]]))
  sym <- sub(" ?//.*$", "", sym)                                    # Affymetrix multi-mapping strings
  keep <- !is.na(sym) & sym != "" & sym != "NA"
  expr <- expr[keep, , drop = FALSE]; rownames(expr) <- sym[keep]
  expr <- limma::avereps(expr, ID = rownames(expr))                 # collapse multiple probes by mean
}
# 3. module scores with the frozen definitions shipped in this package
gs <- read.csv("04_modules/module_definitions.csv")
sets <- lapply(split(toupper(gs$gene), gs$module), unique)
usable <- names(sets)[sapply(sets, function(g) length(intersect(g, rownames(expr))) >= 3)]
sc <- GSVA::gsva(GSVA::gsvaParam(expr, sets[usable], minSize = 3, kcdf = "Gaussian"), verbose = FALSE)
z <- t(scale(t(sc)))
out <- as.data.frame(t(z)); out$sample_id <- colnames(z); out$accession <- acc
dir.create("09_reuse_examples/output_rebuilt", showWarnings = FALSE)
write.csv(out, file.path("09_reuse_examples/output_rebuilt", paste0(acc, "_module_scores_z.csv")), row.names = FALSE)
cat("rebuilt", nrow(out), "samples x", ncol(out) - 2, "modules for", acc, "\n")
cat("NOTE: compare with the shipped 04_modules/sample_module_scores_gsva_z.csv for cohorts that are already curated.\n")
