"""Score-layer construction, coverage and expression-scale decision rules."""

from __future__ import annotations

from collections.abc import Iterable, Sequence

import numpy as np

SINGLE_CELL_MODULES = (
    "EPH_RECEPTORS",
    "WNT_CTNNB1",
    "JAK_STAT",
    "VEGF_PDGF_AXIS",
    "HGF_MET_AXIS",
    "SRC_FAK",
    "ERBB_RECEPTORS",
    "ERBB_LIGANDS",
)

MARKER_PANEL = {
    "epi": ("EPCAM", "KRT18", "KRT8", "CDH1", "KRT19"),
    "fib": ("COL1A1", "COL1A2", "COL3A1", "DCN", "LUM", "FAP"),
    "end": ("PECAM1", "VWF", "CDH5", "CLDN5", "KDR"),
    "imm": ("PTPRC", "CD3D", "CD3E", "CD19", "MS4A1", "LYZ", "CD68", "NKG7"),
}


def module_coverage(module_genes: Iterable[str], retained_genes: Iterable[str]) -> dict[str, object]:
    """coverage(c,m)=|genes(m) intersect retained(c)|/|genes(m)|."""
    module = frozenset(module_genes)
    retained = frozenset(retained_genes)
    if not module:
        raise ValueError("A module must contain at least one gene")
    present = module & retained
    return {
        "members_total": len(module),
        "members_present": len(present),
        "coverage": len(present) / len(module),
        "retained_members": tuple(sorted(present)),
        "missing_members": tuple(sorted(module - retained)),
        "primary_scorable": len(present) >= 3,
    }


def common_members(gene_sets: Sequence[Iterable[str]], *, minimum: int = 2) -> frozenset[str]:
    """Members shared by every cohort; common-gene sensitivity has a two-gene floor."""
    if not gene_sets:
        raise ValueError("At least one cohort gene set is required")
    shared = frozenset.intersection(*(frozenset(genes) for genes in gene_sets))
    if len(shared) < minimum:
        raise ValueError(f"Fewer than {minimum} shared members; not re-scorable")
    return shared


def zscore(values: np.ndarray) -> np.ndarray:
    """Sample-SD z-standardisation, matching R scale() across a cohort/context."""
    array = np.asarray(values, dtype=float)
    if array.size < 2 or not np.all(np.isfinite(array)):
        raise ValueError("z-standardisation needs at least two finite values")
    sd = np.std(array, ddof=1)
    if sd == 0:
        raise ValueError("Zero-variance scores cannot be z-standardised")
    return (array - np.mean(array)) / sd


def member_mean_score(
    expression_genes_by_samples: np.ndarray,
    gene_names: Sequence[str],
    module_genes: Iterable[str],
    *,
    minimum: int = 3,
) -> tuple[np.ndarray, tuple[str, ...]]:
    """Average retained members first; standardisation, if any, happens afterwards."""
    expression = np.asarray(expression_genes_by_samples, dtype=float)
    if expression.ndim != 2 or expression.shape[0] != len(gene_names):
        raise ValueError("Expression must be genes x samples with one name per row")
    module = frozenset(module_genes)
    retained = tuple(gene for gene in gene_names if gene in module)
    if len(retained) < minimum:
        raise ValueError(f"Only {len(retained)} members present; at least {minimum} required")
    indices = [gene_names.index(gene) for gene in retained]
    return np.mean(expression[indices, :], axis=0), retained


def tcga_member_mean_z(
    expression_genes_by_patients: np.ndarray,
    gene_names: Sequence[str],
    module_genes: Iterable[str],
) -> np.ndarray:
    """TCGA order: patient-level member mean, then z-score within tumour context."""
    scores, _ = member_mean_score(expression_genes_by_patients, gene_names, module_genes)
    return zscore(scores)


def single_cell_member_means(
    counts_cells_by_genes: np.ndarray,
    gene_names: Sequence[str],
    module_genes: Iterable[str],
    *,
    target_library_size: float = 1e4,
) -> np.ndarray:
    """Library-size normalise to 1e4, log1p, then average retained module members."""
    counts = np.asarray(counts_cells_by_genes, dtype=float)
    if counts.ndim != 2 or counts.shape[1] != len(gene_names) or np.any(counts < 0):
        raise ValueError("Counts must be non-negative cells x genes with one name per column")
    library_sizes = counts.sum(axis=1)
    if np.any(library_sizes <= 0):
        raise ValueError("Cells with zero library size cannot be normalised")
    normalised = np.log1p(counts / library_sizes[:, None] * target_library_size)
    module = frozenset(module_genes)
    indices = [index for index, gene in enumerate(gene_names) if gene in module]
    if len(indices) < 3:
        raise ValueError("Single-cell module scoring requires at least three retained members")
    return normalised[:, indices].mean(axis=1)


def marker_proxy(
    expression_genes_by_samples: np.ndarray,
    gene_names: Sequence[str],
    compartment: str,
) -> np.ndarray:
    """Marker-proxy alternative: mean retained markers (min 2), then cohort z-score."""
    if compartment not in MARKER_PANEL:
        raise ValueError(f"Unknown compartment: {compartment}")
    scores, _ = member_mean_score(
        expression_genes_by_samples,
        gene_names,
        MARKER_PANEL[compartment],
        minimum=2,
    )
    return zscore(scores)


def classify_expression_scale(values: np.ndarray) -> dict[str, float | bool | str]:
    """Flag possible raw data; never apply log2(x+1) as a normalisation substitute."""
    array = np.asarray(values, dtype=float)
    finite = array[np.isfinite(array)]
    if not finite.size:
        raise ValueError("Expression matrix has no finite values")
    integer_fraction = float(np.mean(np.isclose(finite, np.round(finite))))
    maximum = float(np.max(finite))
    flag = integer_fraction > 0.90 and maximum > 50
    return {
        "integer_fraction": integer_fraction,
        "maximum": maximum,
        "flag_for_library_size_normalisation": flag,
        "action": "flag; do not transform in place" if flag else "leave unchanged as already log-scaled",
    }
