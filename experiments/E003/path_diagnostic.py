#!/usr/bin/env python3
"""Continuous box-overlap diagnostic under synchronized linear interpolation.

This is a geometric proxy, not a renderer, animation simulation or native test.
Rotation is rejected. It evaluates selected plan boxes, not glyph outlines.
"""
import argparse
import itertools
import json
import math
from pathlib import Path


def box(frame):
    if frame.get('rotation_deg', 0) != 0:
        raise ValueError('Rotated boxes are outside this diagnostic')
    result = [frame['x'] * 1280, frame['y'] * 720, frame['w'] * 1280, frame['h'] * 720]
    if not all(math.isfinite(x) for x in result) or result[2] <= 0 or result[3] <= 0:
        raise ValueError('Boxes need finite geometry and positive dimensions')
    return result


def gaps(a, b):
    return [a[0]+a[2]-b[0], b[0]+b[2]-a[0], a[1]+a[3]-b[1], b[1]+b[3]-a[1]]


def overlap_interval(a0, a1, b0, b1):
    low, high = 0.0, 1.0
    for start, end in zip(gaps(a0, b0), gaps(a1, b1)):
        slope = end-start
        if abs(slope) < 1e-10:
            if start <= 0:
                return None
        elif slope > 0:
            low = max(low, -start/slope)
        else:
            high = min(high, -start/slope)
    return [low, high] if low < high else None


def evaluate(plan, ids):
    if len(ids) < 2 or len(set(ids)) != len(ids):
        raise ValueError('Select at least two distinct object IDs')
    pairs = []
    for a, b in zip(plan['states'], plan['states'][1:]):
        for i, j in itertools.combinations(ids, 2):
            ai, bi, aj, bj = [box(s['objects'][k]) for s,k in [(a,i),(b,i),(a,j),(b,j)]]
            interval = overlap_interval(ai, bi, aj, bj)
            centers = [[(p[0]+q[0])/2+(p[2]+q[2])/4,
                        (p[1]+q[1])/2+(p[3]+q[3])/4] for p,q in [(ai,bi),(aj,bj)]]
            pairs.append({'transition':a['id']+' -> '+b['id'], 'objects':[i,j],
                          'positive_area_overlap_interval':interval,
                          'midpoint_center_distance_px':math.dist(*centers)})
    return {'assumption':'Synchronized linear interpolation of unrotated plan boxes at 1280x720; not native playback',
            'selected_ids':ids,'pairs':pairs,'overlapping_pairs':sum(p['positive_area_overlap_interval'] is not None for p in pairs),
            'native_playback_verified':False,'motion_quality_score':None}


if __name__ == '__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('plan',type=Path);ap.add_argument('ids',nargs='+')
    args=ap.parse_args()
    print(json.dumps(evaluate(json.loads(args.plan.read_text()),args.ids),indent=2))
