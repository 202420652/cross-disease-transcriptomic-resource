#!/usr/bin/env python3
"""Refresh the three integrity manifests of the data deposit.

The deposit ships three mutually consistent verification files:

``08_qc/file_inventory_and_checksums.csv``
    One row per shipped file: relative path, byte size, number of data rows
    (CSV only) and SHA-256. ``08_qc/manifest_checksum.txt`` is excluded because
    it is the digest-of-manifests file. The two self-referential files carry the
    literal marker ``self-reference`` in the hash column instead of a digest.

``08_qc/checksums_sha256.txt``
    ``sha256sum``-compatible list (hash, two spaces, path) covering every file
    except the three manifest files themselves, so ``sha256sum -c`` from the
    deposit root passes without self-reference warnings.

``08_qc/manifest_checksum.txt``
    Digests of the two files above, which cannot contain their own digest.

Run this after any change to the deposit contents::

    python tools/refresh_deposit_manifests.py deposit
"""

from __future__ import annotations

import csv
import hashlib
import sys
from pathlib import Path

INVENTORY = "08_qc/file_inventory_and_checksums.csv"
CHECKSUMS = "08_qc/checksums_sha256.txt"
MANIFEST = "08_qc/manifest_checksum.txt"
SELF_REFERENTIAL = {INVENTORY, CHECKSUMS}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def data_rows(path: Path) -> str:
    """Number of data rows for a CSV file (header excluded); empty otherwise."""
    if path.suffix.lower() != ".csv":
        return ""
    with path.open("r", encoding="utf-8", newline="") as handle:
        return str(sum(1 for _ in csv.reader(handle)) - 1)


def main(root: str) -> int:
    base = Path(root).resolve()
    if not (base / "00_VERSION.txt").exists():
        print(f"error: {base} does not look like the deposit root", file=sys.stderr)
        return 2

    files = sorted(
        p.relative_to(base).as_posix()
        for p in base.rglob("*")
        if p.is_file() and p.relative_to(base).as_posix() != MANIFEST
    )

    inventory_rows = []
    for rel in files:
        path = base / rel
        if rel in SELF_REFERENTIAL:
            rows = data_rows(path) if rel == INVENTORY else ""
            inventory_rows.append([rel, "", rows, "self-reference"])
        else:
            inventory_rows.append([rel, str(path.stat().st_size), data_rows(path), sha256(path)])

    with (base / INVENTORY).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["file", "bytes", "rows", "sha256"])
        writer.writerows(inventory_rows)

    with (base / CHECKSUMS).open("w", encoding="utf-8", newline="") as handle:
        for rel in files:
            if rel in SELF_REFERENTIAL:
                continue
            handle.write(f"{sha256(base / rel)}  {rel}\n")

    with (base / MANIFEST).open("w", encoding="utf-8", newline="") as handle:
        handle.write("# digest of the manifest files themselves (they are not covered by the list)\n")
        for rel in (INVENTORY, CHECKSUMS):
            handle.write(f"{sha256(base / rel)}  {Path(rel).name}\n")

    print(f"files covered by the inventory : {len(files)}")
    print(f"files covered by the checksums : {len(files) - len(SELF_REFERENTIAL)}")
    print(f"deposit root                   : {base}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1] if len(sys.argv) > 1 else "deposit"))
