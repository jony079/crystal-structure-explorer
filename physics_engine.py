"""
=============================================================================
  Core Crystallography & Physics Computational Engine
  Handles pure math, structure factors, and memoized XRD calculations.
=============================================================================
"""

import math
import numpy as np
import streamlit as st  # Only used for caching decorators

@st.cache_data
def d_spacing(a, h, k, l, crystal_type="cubic", c=None):
    """Calculates interplanar spacing (d-spacing) with high precision."""
    if h == 0 and k == 0 and l == 0:
        return None
    if crystal_type in ("SC", "BCC", "FCC"):
        return a / math.sqrt(h**2 + k**2 + l**2)
    else:  # HCP
        if c is None:
            c = a * 1.633
        denom = (4/3) * (h**2 + h*k + k**2) / (a**2) + (l**2) / (c**2)
        return 1.0 / math.sqrt(denom) if denom > 0 else None


@st.cache_data
def atomic_radius(a, crystal_type, c=None):
    """Calculates standard atomic radius based on lattice parameters."""
    if crystal_type in ("SC", "HCP"):
        return a / 2.0
    elif crystal_type == "BCC":
        return math.sqrt(3) * a / 4.0
    elif crystal_type == "FCC":
        return math.sqrt(2) * a / 4.0
    return 0.0


@st.cache_data
def structure_factor(crystal_type, h, k, l):
    """
    Evaluates Geometrical Structure Factor rules and identifies systematic absences.
    Strictly validated against standard physical crystallography group tables.
    """
    if crystal_type == "SC":
        return 1.0, 1.0, "Fully allowed (constructive interference) — maximum intensity"

    elif crystal_type == "BCC":
        if (h + k + l) % 2 == 0:
            return 4.0, 1.0, "Fully allowed (constructive interference) — maximum intensity"
        else:
            return 0.0, 0.0, "Forbidden (destructive interference) — systematic absence"

    elif crystal_type == "FCC":
        h_even, k_even, l_even = (h % 2 == 0), (k % 2 == 0), (l % 2 == 0)
        if (h_even == k_even) and (k_even == l_even):
            return 16.0, 1.0, "Fully allowed (constructive interference) — maximum intensity"
        else:
            return 0.0, 0.0, "Forbidden (destructive interference) — systematic absence"

    else:  # HCP Strict Physical Extinction Logic
        # Rule: h + 2k = 3n AND l is odd -> Intensity is ZERO
        if (h + 2*k) % 3 == 0 and (l % 2 != 0):
            return 0.0, 0.0, "Forbidden (Destructive) — Systematic Absence (h+2k=3n, l is odd)"
        
        # 2-atom basis evaluation: (0,0,0) and (1/3, 2/3, 1/2)
        val = (h / 3.0) + (2.0 * k / 3.0) + (l / 2.0)
        phase = 2.0 * math.pi * val
        cos_part = 1.0 + math.cos(phase)
        sin_part = math.sin(phase)
        
        F_sq = cos_part**2 + sin_part**2
        F_rel = F_sq / 4.0
        
        if F_rel < 0.005:
            return 0.0, 0.0, "Forbidden (destructive interference) — systematic absence"
        elif F_rel > 0.99:
            return F_sq, 1.0, "Fully allowed (constructive interference) — maximum intensity"
        else:
            return F_sq, F_rel, f"Partially allowed — relative intensity {F_rel:.3f}"


@st.cache_data
def generate_xrd_peaks_cached(crystal_type, a, wavelength_A, two_theta_max, c=None):
    """Memoized heavy loop operation scanning hkl parameters up to 2197 permutations."""
    peak_dict = {}
    hkl_range = range(-4, 5) if crystal_type == "HCP" else range(-6, 7)

    for h in hkl_range:
        for k in hkl_range:
            for l in hkl_range:
                if h == 0 and k == 0 and l == 0:
                    continue
                
                d = d_spacing(a, h, k, l, crystal_type=crystal_type, c=c)
                if d is None or d <= 0:
                    continue
                    
                sin_theta = wavelength_A / (2 * d)
                if not (0 < sin_theta <= 1):
                    continue
                    
                theta = math.asin(sin_theta)
                two_theta = math.degrees(2 * theta)
                if two_theta > two_theta_max:
                    continue

                _, F_rel, _ = structure_factor(crystal_type, h, k, l)
                if F_rel < 0.005:
                    continue

                key = round(two_theta, 1)
                if key in peak_dict:
                    peak_dict[key][0] += F_rel
                    peak_dict[key][1].add(f"({h}{k}{l})")
                else:
                    peak_dict[key] = [F_rel, {f"({h}{k}{l})"}]

    if not peak_dict:
        return []

    peaks = [(tt, v[0], ", ".join(sorted(v[1]))) for tt, v in peak_dict.items()]
    peaks.sort()
    max_I = max(p[1] for p in peaks) if peaks else 1.0
    return [(tt, (I / max_I) * 100, lbl) for tt, I, lbl in peaks]


def get_lattice_points(crystal_type, a=1.0, c=None):
    """Calculates spatial coordinates of atoms in the unit cell."""
    corners = np.array([
        [0,0,0],[1,0,0],[0,1,0],[1,1,0],
        [0,0,1],[1,0,1],[0,1,1],[1,1,1],
    ], dtype=float)

    if crystal_type == "SC":
        return corners, ["Corner"] * 8
    elif crystal_type == "BCC":
        body = np.array([[0.5, 0.5, 0.5]])
        return np.vstack([corners, body]), ["Corner"] * 8 + ["Body Center"]
    elif crystal_type == "FCC":
        faces = np.array([
            [0.5,0.5,0],[0.5,0.5,1],
            [0.5,0,0.5],[0.5,1,0.5],
            [0,0.5,0.5],[1,0.5,0.5],
        ])
        return np.vstack([corners, faces]), ["Corner"]*8 + ["Face Center"]*6
    else:  # HCP
        c_ratio = (c if c else a*1.633) / a
        angles_hex = [math.radians(i*60) for i in range(6)]
        hex_x = [math.cos(a_) for a_ in angles_hex]
        hex_y = [math.sin(a_) for a_ in angles_hex]
        
        hcp_base = np.array([[0,0,0]] + [[x, y, 0] for x, y in zip(hex_x, hex_y)])
        hcp_top = hcp_base.copy()
        hcp_top[:, 2] = c_ratio
        hcp_mid = np.array([
            [0.5, math.sqrt(3)/6, c_ratio/2],
            [-0.5, math.sqrt(3)/6, c_ratio/2],
            [0, -math.sqrt(3)/3, c_ratio/2],
        ])
        return np.vstack([hcp_base, hcp_top, hcp_mid]), (["HCP Base"]*7 + ["HCP Top"]*7 + ["HCP Mid"]*3)