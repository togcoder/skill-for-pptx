# -*- coding: utf-8 -*-
"""EXPERIMENTAL — quarantined by T034 (experiments/T033-20261016-argon-research/REPORT.md).
Not used by any product path. The canonical trigger writer is
pptx_animator.apply_timeline(trigger_spid=...), apply_interactive_actions(...)
and read_interactive_sequences / read_interactive_actions.

T061: this module is a thin compatibility layer over pptx_animator.
It keeps only the T033 plan vocabulary (trigger / action / targets / preset /
duration_ms / delay_ms) and the name resolution; it writes no XML of its own.
The T033 writer emitted non-schema ``customAction`` / ``customPreset`` /
``customDur`` attributes, wrote one ``<p:seq>`` per plan item even for the same
trigger, and put ``delay="indefinite"`` on the click step — all three are gone.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence, Union
import xml.etree.ElementTree as ET

try:
    from . import pptx_animator as anim
except ImportError:
    import pptx_animator as anim

__all__ = [
    "TimeNodeIDAllocator",
    "apply_interactive_triggers",
    "read_interactive_triggers",
]


class TimeNodeIDAllocator:
    """Monotonic ``<p:cTn id>`` allocator; the seed comes from pptx_animator."""

    def __init__(self, slide_root: ET.Element) -> None:
        self._current: int = anim.max_ctn_id(slide_root)

    @property
    def current_max(self) -> int:
        return self._current

    def allocate(self) -> int:
        self._current += 1
        return self._current

    def allocate_str(self) -> str:
        return str(self.allocate())


def _index_shapes(
    slide_root: ET.Element,
    external_map: Optional[Dict[str, Union[int, str]]] = None,
) -> Dict[str, str]:
    """``{name or spid: spid}`` for the slide, plus an optional external map."""
    _, by_name = anim.shape_ids(slide_root)
    index = {spid: spid for spid in by_name.values()}
    index.update(by_name)
    for key, value in (external_map or {}).items():
        spid = str(value).strip()
        index[str(key).strip()] = spid
        index[spid] = spid
    return index


def apply_interactive_triggers(
    slide_root: ET.Element,
    triggers_plan: Sequence[Dict[str, Any]],
    shape_id_map: Optional[Dict[str, Union[int, str]]] = None,
) -> List[Dict[str, Any]]:
    """Write a T033 trigger plan through the canonical interactive writer.

    Each item: ``{"trigger","action","targets","preset","duration_ms",
    "delay_ms"}``. ``action`` is reveal / hide / highlight / toggle.
    """
    if not triggers_plan:
        return []
    index = _index_shapes(slide_root, shape_id_map)
    resolved = []
    for spec in triggers_plan:
        if spec.get("trigger") is None:
            raise ValueError("Trigger specification is missing 'trigger' key.")
        item = dict(spec)
        key = str(item["trigger"]).strip()
        if key not in index:
            raise KeyError(f"Trigger shape '{key}' could not be resolved on slide.")
        item["trigger"] = index[key]
        raw = item.get("targets") or []
        if isinstance(raw, (str, int)):
            raw = [raw]
        targets = []
        for target in raw:
            tkey = str(target).strip()
            if tkey not in index:
                raise KeyError(f"Target shape '{tkey}' could not be resolved on slide.")
            targets.append(index[tkey])
        item["targets"] = targets or [item["trigger"]]
        resolved.append(item)
    return anim.apply_interactive_actions(slide_root, resolved)


def read_interactive_triggers(slide_root: ET.Element) -> List[Dict[str, Any]]:
    """Read interactive sequences back as T033-style semantic records."""
    by_id, _ = anim.shape_ids(slide_root)
    out: List[Dict[str, Any]] = []
    for record in anim.read_interactive_actions(slide_root):
        trigger = record["trigger_spid"]
        names = [by_id.get(spid, spid) for spid in record["target_spids"]]
        out.append({
            "seq_ctn_id": record["seq_ctn_id"],
            "trigger": by_id.get(trigger, trigger),
            "trigger_spid": trigger,
            "trigger_name": by_id.get(trigger, trigger),
            "action": record["action"],
            "preset": record["preset"],
            "target_spids": record["target_spids"],
            "targets": names,
            "duration_ms": record["duration_ms"],
            "delay_ms": record["delay_ms"],
            "click_groups": record["click_groups"],
        })
    return out
