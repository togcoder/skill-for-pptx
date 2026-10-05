#!/usr/bin/env python3
"""Remove stale OOXML content-type overrides without changing package parts.

Some otherwise loadable PPTX files retain ``Override`` entries for parts that
are no longer present.  The host integrity validator rejects those packages.
This repair is intentionally narrow: it removes only overrides whose exact
``PartName`` has no ZIP member and copies every other member byte-for-byte.
"""

import argparse
import hashlib
import json
import shutil
import tempfile
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

CONTENT_TYPES = "[Content_Types].xml"
CONTENT_TYPES_NS = "http://schemas.openxmlformats.org/package/2006/content-types"


def _sha256(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def repair_stale_content_type_overrides(source, destination):
    source = Path(source)
    destination = Path(destination)
    if source.resolve() == destination.resolve():
        raise ValueError("destination must differ from source")

    with zipfile.ZipFile(source, "r") as zin:
        infos = zin.infolist()
        names = {info.filename for info in infos}
        if CONTENT_TYPES not in names:
            raise ValueError("package has no [Content_Types].xml")

        root = ET.fromstring(zin.read(CONTENT_TYPES))
        # Preserve the package convention required by the host validator:
        # a default namespace, not an auto-generated ``ns0`` prefix.
        ET.register_namespace("", CONTENT_TYPES_NS)
        removed = []
        for child in list(root):
            if child.tag.rsplit("}", 1)[-1] != "Override":
                continue
            part_name = child.attrib.get("PartName")
            if not part_name:
                continue
            member = part_name.lstrip("/")
            if member not in names:
                removed.append(part_name)
                root.remove(child)

        replacement = ET.tostring(root, encoding="utf-8", xml_declaration=True)
        destination.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(
            dir=destination.parent, prefix=f".{destination.name}.", suffix=".tmp", delete=False
        ) as tmp:
            temp_path = Path(tmp.name)

        try:
            with zipfile.ZipFile(temp_path, "w") as zout:
                for info in infos:
                    data = replacement if info.filename == CONTENT_TYPES else zin.read(info.filename)
                    zout.writestr(info, data)
            shutil.move(temp_path, destination)
        finally:
            temp_path.unlink(missing_ok=True)

    return {
        "source_sha256": _sha256(source),
        "output_sha256": _sha256(destination),
        "removed_override_count": len(removed),
        "removed_part_names": removed,
        "changed_members": [CONTENT_TYPES] if removed else [],
        "claim_boundary": (
            "Only stale Override elements in [Content_Types].xml were removed; "
            "this does not prove PowerPoint playback."
        ),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()
    receipt = repair_stale_content_type_overrides(args.source, args.destination)
    payload = json.dumps(receipt, indent=2) + "\n"
    if args.receipt:
        args.receipt.parent.mkdir(parents=True, exist_ok=True)
        args.receipt.write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")


if __name__ == "__main__":
    main()
