#!/usr/bin/env python3
"""Fit a pinhole camera to the Quick Mill body box from the source photo.

Method: fSpy / single-view metrology idea (vanishing points) reduced to six
manually measured box corners and a least-squares look-at camera.  It is a
calibration check, not a trace: the scene remains object-space primitives.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from scipy.optimize import least_squares

HERE = Path(__file__).resolve().parent
EXP = HERE.parent
OUT = EXP / "preview"

# Object-space body box (T054 dimensions): x 10..90, y 18.5..118, z 0..60.
OBJ = np.array([
    [10.0, 118.0, 0.0],   # A front top-left
    [90.0, 118.0, 0.0],   # B front top-right
    [10.0, 18.5, 0.0],    # C front bottom-left
    [90.0, 18.5, 0.0],    # D front bottom-right
    [10.0, 118.0, 60.0],  # E back top-left
    [10.0, 18.5, 60.0],   # F back bottom-left
], dtype=float)

# Photo pixels, 1280 x 1512.
IMG = np.array([
    [390.0, 420.0],
    [930.0, 470.0],
    [390.0, 1230.0],
    [1000.0, 1280.0],
    [250.0, 370.0],
    [250.0, 1200.0],
], dtype=float)

W, H = 1280.0, 1512.0
PRINCIPAL = np.array([W / 2, H / 2])


def camera_matrix(params):
    cx, cy, cz, tx, ty, tz, f = params
    C = np.array([cx, cy, cz], dtype=float)
    T = np.array([tx, ty, tz], dtype=float)
    forward = T - C
    forward /= np.linalg.norm(forward)
    up = np.array([0.0, 1.0, 0.0])
    right = np.cross(up, forward)
    right /= np.linalg.norm(right)
    true_up = np.cross(forward, right)
    R = np.stack([right, true_up, forward])  # world -> camera rows
    return C, R, f


def project(params, points):
    C, R, f = camera_matrix(params)
    d = points - C
    cam = d @ R.T
    z = cam[:, 2]
    u = PRINCIPAL[0] + f * cam[:, 0] / z
    v = PRINCIPAL[1] - f * cam[:, 1] / z
    return np.stack([u, v], axis=1)


def residuals(params):
    return (project(params, OBJ) - IMG).ravel()


def main() -> None:
    x0 = np.array([-47.0, 94.0, -282.0, 50.0, 60.0, 0.0, 2100.0])
    lower = [-400, 0, -700, 0, 0, -50, 400]
    upper = [0, 300, -50, 100, 140, 50, 8000]
    res = least_squares(residuals, x0, bounds=(lower, upper), xtol=1e-12,
                        ftol=1e-12, max_nfev=20000)
    p = res.x
    pred = project(p, OBJ)
    err = pred - IMG
    rms = float(np.sqrt(np.mean(err ** 2)))
    print("success", res.success, "cost", res.cost, "rms_px", round(rms, 2))
    for name, o, i, q, e in zip("ABCDEF", OBJ, IMG, pred, err):
        print(name, "obj", o, "img", i, "pred", np.round(q, 1), "err", np.round(e, 1))
    C, R, f = camera_matrix(p)
    print("C", np.round(C, 2), "T", np.round(p[3:6], 2), "f", round(f, 1))
    print("f35mm", round(f / W * 36, 1), "distance", round(float(np.linalg.norm(p[3:6] - C)), 1))
    print("R", np.round(R, 4))
    data = {
        "object": OBJ.tolist(),
        "image": IMG.tolist(),
        "predicted": pred.tolist(),
        "rms_px": rms,
        "camera": {
            "C": C.tolist(), "T": p[3:6].tolist(), "f_px": float(f),
            "f_35mm": float(f / W * 36), "principal": PRINCIPAL.tolist(),
            "R": R.tolist(),
        },
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "camera-fit.json").write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(OUT / "camera-fit.json")


if __name__ == "__main__":
    main()
