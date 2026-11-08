"""Export the printed tables in Tables.docx without re-typing their values.

The block numbers refer to the supplied manuscript Tables.docx (DataDescriptor_v20).
They are intentionally checked so a changed input document cannot silently produce
mislabelled reference data. Only Python's standard library is required.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
M = "http://schemas.openxmlformats.org/officeDocument/2006/math"
NS = {"w": W, "m": M}

# block number -> (output filename, coverage of the underlying deposit table)
TABLE_FILES = {
    2: ("table01_context_composition.csv", "complete printed table"),
    5: ("table02_resource_comparison.csv", "complete printed table"),
    8: ("table03_deposit_structure.csv", "complete printed table"),
    10: ("s01_cohort_registry.csv", "26 case-control cohorts"),
    13: ("s02_module_coverage_summary.csv", "17 modules plus one design-note row"),
    16: ("s03_single_cell_datasets.csv", "complete printed table"),
    19: ("s04_exclusions_flags_design_corrections.csv", "complete printed table"),
    22: ("s05_decision_rules.csv", "complete printed table"),
    25: ("s06_not_estimable_pairs.csv", "all 8 not-estimable pairs"),
    28: ("s07_validation_evidence.csv", "complete printed table"),
    31: ("s08_score_layer_guide.csv", "complete printed table"),
    34: ("s09_comparability_coupling_collinearity.csv", "complete printed table"),
    37: ("s10_direction_consistency_summary.csv", "summary only; 165-row detail not supplied"),
    40: ("s11_expression_matrix_qc.csv", "26 cohorts plus GSE16879"),
    43: ("s12_module_overlap_summary.csv", "summary; gene-level membership not supplied"),
    46: ("s13_control_tissue_ontology.csv", "complete printed table"),
    49: ("s14_study_overlap_audit.csv", "complete printed table"),
    52: ("s15_survival_data_dictionary.csv", "printed summary"),
    55: ("s16_marker_proxy_xcell_agreement.csv", "complete printed table"),
    58: ("s17_single_cell_sensitivity.csv", "complete printed table"),
    61: ("s18_single_cell_thresholds_multiplicity.csv", "complete printed table"),
    64: ("s19_direction_discordance_summary.csv", "complete printed summary"),
    67: ("s19_discordant_pairs_first12.csv", "first 12 rows only"),
    70: ("s20_input_dataset_status.csv", "complete printed table"),
    73: ("s21_series_accounting.csv", "complete printed table"),
    76: ("s22_comparability_metrics.csv", "complete printed table"),
    79: ("s23_independent_reimplementation.csv", "complete printed ledger"),
    82: ("s24_supplementary_inventory.csv", "complete printed table"),
    85: ("s25_meta_by_design_stratum.csv", "all 312 printed rows"),
    89: ("s26_classic_denominator_sensitivity_first80.csv", "80 of 165 deposit rows"),
    93: ("s27_smdh_variance_monte_carlo.csv", "20 printed conditions; provisional coverage"),
    96: ("s28_low_control_exclusion_sensitivity.csv", "17 module rows"),
    98: ("s28_low_control_exclusion_metrics.csv", "summary metrics"),
    101: ("s29_single_cell_donor_effects_first60.csv", "60 of 208 deposit rows"),
    105: ("s30_cells_per_donor_cell_type_arm.csv", "complete printed table"),
    108: ("s32_analysis_sample_sizes.csv", "26 cohorts plus total row"),
}


def paragraph_text(paragraph: ET.Element) -> str:
    parts: list[str] = []
    for node in paragraph.iter():
        if node.tag in {f"{{{W}}}t", f"{{{M}}}t"} and node.text:
            parts.append(node.text)
        elif node.tag == f"{{{W}}}tab":
            parts.append("\t")
        elif node.tag in {f"{{{W}}}br", f"{{{W}}}cr"}:
            parts.append("\n")
    return "".join(parts)


def read_blocks(path: Path) -> list[dict[str, object]]:
    with zipfile.ZipFile(path) as archive:
        root = ET.fromstring(archive.read("word/document.xml"))
    body = root.find("w:body", NS)
    if body is None:
        raise ValueError(f"No document body found in {path}")
    blocks: list[dict[str, object]] = []
    for child in body:
        if child.tag == f"{{{W}}}p":
            blocks.append({"type": "paragraph", "text": paragraph_text(child)})
        elif child.tag == f"{{{W}}}tbl":
            rows = []
            for row in child.findall("w:tr", NS):
                cells = []
                for cell in row.findall("w:tc", NS):
                    paragraphs = [paragraph_text(p) for p in cell.findall(".//w:p", NS)]
                    cells.append("\n".join(p for p in paragraphs if p))
                rows.append(cells)
            blocks.append({"type": "table", "rows": rows})
    return blocks


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def export(source: Path, output_dir: Path) -> dict[str, object]:
    blocks = read_blocks(source)
    output_dir.mkdir(parents=True, exist_ok=True)
    entries = []
    title = ""
    for index, block in enumerate(blocks, start=1):
        if block["type"] == "paragraph":
            title = str(block.get("text", ""))
            continue
        if index not in TABLE_FILES:
            raise ValueError(f"Unmapped table at block {index}: {title}")
        filename, scope = TABLE_FILES[index]
        rows = block["rows"]
        if not rows or not rows[0]:
            raise ValueError(f"Empty table at block {index}")
        width = len(rows[0])
        for row_number, row in enumerate(rows, start=1):
            if len(row) != width:
                raise ValueError(
                    f"Ragged table at block {index}, row {row_number}: "
                    f"expected {width} cells, found {len(row)}"
                )
        destination = output_dir / filename
        with destination.open("w", encoding="utf-8", newline="") as handle:
            csv.writer(handle, lineterminator="\n").writerows(rows)
        entries.append(
            {
                "source_block": index,
                "source_title": title,
                "file": filename,
                "scope": scope,
                "data_rows": len(rows) - 1,
                "columns": rows[0],
                "sha256": sha256(destination),
            }
        )
    missing = sorted(set(TABLE_FILES) - {entry["source_block"] for entry in entries})
    if missing:
        raise ValueError(f"Expected tables were not found at blocks: {missing}")
    manifest = {
        "source_document": source.name,
        "source_sha256": sha256(source),
        "value_policy": "Cell text exported verbatim; no imputation or numeric reformatting.",
        "table_count": len(entries),
        "tables": entries,
    }
    manifest_path = output_dir / "table_manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="Path to the supplied Tables.docx")
    parser.add_argument("output_dir", type=Path, help="Directory for CSV files and table_manifest.json")
    args = parser.parse_args()
    manifest = export(args.source, args.output_dir)
    print(json.dumps({"tables": manifest["table_count"], "output_dir": str(args.output_dir)}))


if __name__ == "__main__":
    main()
