#!/usr/bin/env python3
"""Required vertical gap for equal label boxes cycling over a symmetric triangle.

This is a plan geometry bound under synchronized linear interpolation, not
PowerPoint playback. Labels must share constant width/height and zero rotation.
The slots are (-d,H), (0,0), (d,H), with one cyclic permutation per transition.
"""
import argparse
import json
import math


def clearance(half_span, width, height, vertical_gap):
    values = (half_span, width, height, vertical_gap)
    if any(isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) or v <= 0 for v in values):
        raise ValueError('All dimensions must be finite positive numbers')
    if width > half_span:
        raise ValueError('Label width exceeds half-span: two diagonal routes overlap at mid-progress regardless of vertical gap')
    minimum = 3 * half_span * height / (2 * half_span - width)
    return {'assumption': 'Three equal unrotated constant-size label boxes, symmetric triangle, synchronized linear cyclic routing',
            'half_span_px': half_span, 'label_width_px': width, 'label_height_px': height,
            'vertical_gap_px': vertical_gap, 'minimum_vertical_gap_px': minimum,
            'predicted_positive_area_overlap_free': vertical_gap >= minimum,
            'vertical_margin_px': vertical_gap - minimum,
            'native_playback_verified': False, 'motion_quality_score': None}


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    for field in ('half-span','width','height','gap'):
        ap.add_argument('--'+field, type=float, required=True)
    a = ap.parse_args()
    try:
        print(json.dumps(clearance(a.half_span,a.width,a.height,a.gap),indent=2))
    except ValueError as exc:
        ap.error(str(exc))
