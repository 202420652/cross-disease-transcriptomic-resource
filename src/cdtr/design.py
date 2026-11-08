"""Metadata-derived design decisions used by the resource."""

from __future__ import annotations


def paired_design(both_tissue_patients: int, *, minimum_complete_pairs: int = 4) -> str:
    """Paired only when metadata establish at least four complete patient pairs."""
    if both_tissue_patients < 0:
        raise ValueError("both_tissue_patients cannot be negative")
    return "paired" if both_tissue_patients >= minimum_complete_pairs else "unpaired"


def analysis_measure(design: str) -> str:
    if design == "paired":
        return "SMCRPH"
    if design == "unpaired":
        return "SMDH"
    raise ValueError("design must be 'paired' or 'unpaired'")


def analysis_sample_counts(
    design: str,
    cases: int,
    controls: int,
    complete_pairs: int = 0,
) -> tuple[int, int]:
    """Complete pairs enter paired estimates; all annotated samples enter unpaired ones."""
    if min(cases, controls, complete_pairs) < 0:
        raise ValueError("Counts cannot be negative")
    if design == "paired":
        if complete_pairs > min(cases, controls):
            raise ValueError("Complete pairs cannot exceed either arm")
        return complete_pairs, complete_pairs
    if design == "unpaired":
        return cases, controls
    raise ValueError("design must be 'paired' or 'unpaired'")
