# physics_engine.py
"""Core physics calculations for crystal lattices and X‑ray diffraction.

All functions are pure (no side‑effects) so they can be safely cached.
"""

import math
from typing import Dict, List, Tuple


# ------------------------
# Lattice generation helpers
# ------------------------
def generate_lattice(params: Dict) -> Tuple[List[Tuple[float, float, float]], float]:
    """Return a list of atom coordinates (in Å) and the unit‑cell volume.

    Supported lattice types are defined in ``config.LATTICE_TYPES``.
    """
    a = params["a"]
    b = params["b"]
    c = params["c"]
    α = math.radians(params["alpha"])
    β = math.radians(params["beta"])
    γ = math.radians(params["gamma"])
    lattice_type = params["lattice_type"]

    # Helper to compute volume from three vectors
    def volume(v1, v2, v3):
        return abs(
            v1[0] * (v2[1] * v3[2] - v2[2] * v3[1])
            - v1[1] * (v2[0] * v3[2] - v2[2] * v3[0])
            + v1[2] * (v2[0] * v3[1] - v2[1] * v3[0])
        )

    if lattice_type == "cubic":
        # Simple cubic with one atom at the origin
        atoms = [(0.0, 0.0, 0.0)]
        vol = a ** 3

    elif lattice_type == "hcp":
        # Hexagonal close‑packed: two atoms per cell
        vectors = [
            (a, 0, 0),
            (a / 2, a * math.sqrt(3) / 2, 0),
            (0, 0, c),
        ]
        atoms = [
            (0.0, 0.0, 0.0),
            (2 / 3 * a, 1 / 3 * a * math.sqrt(3), c / 2),
        ]
        vol = volume(*vectors)

    elif lattice_type == "fcc":
        # Face‑centered cubic – four atoms per conventional cell
        atoms = [
            (0.0, 0.0, 0.0),
            (0.0, a / 2, a / 2),
            (a / 2, 0.0, a / 2),
            (a / 2, a / 2, 0.0),
        ]
        vol = a ** 3

    else:
        # Fallback to orthorhombic (general case)
        atoms = [(0.0, 0.0, 0.0)]
        vol = a * b * c

    return atoms, vol


# ------------------------
# Physical property calculations
# ------------------------
def d_spacing(h: int, k: int, l: int, params: Dict) -> float:
    """Calculate the inter‑planar spacing dₕₖₗ using the metric tensor."""
    a = params["a"]
    b = params["b"]
    c = params["c"]
    α = math.radians(params["alpha"])
    β = math.radians(params["beta"])
    γ = math.radians(params["gamma"])

    # Metric tensor components
    G11 = a ** 2
    G22 = b ** 2
    G33 = c ** 2
    G12 = a * b * math.cos(γ)
    G13 = a * c * math.cos(β)
    G23 = b * c * math.cos(α)

    inv_d2 = (
        h * h * G11
        + k * k * G22
        + l * l * G33
        + 2 * h * k * G12
        + 2 * h * l * G13
        + 2 * k * l * G23
    )
    if inv_d2 <= 0:
        raise ValueError("Invalid lattice parameters leading to non‑positive d‑spacing.")
    return math.sqrt(1.0 / inv_d2)


def structure_factor(h: int, k: int, l: int, params: Dict) -> complex:
    """Structure factor for a monatomic lattice (placeholder for extensions)."""
    # For a single atom at the origin the phase factor is 1 → F = 1
    return 1 + 0j


def packing_fraction(params: Dict) -> float:
    """Fraction of the unit‑cell volume occupied by hard‑sphere atoms."""
    _, volume = generate_lattice(params)
    r = 1.2  # simple heuristic radius (Å)
    atom_vol = 4 / 3 * math.pi * r ** 3
    n_atoms = len(generate_lattice(params)[0])
    return n_atoms * atom_vol / volume


def apf(params: Dict) -> float:
    """Atomic packing factor – identical to packing_fraction for monatomic lattices."""
    return packing_fraction(params)


# ------------------------
# Helper utilities for XRD simulation
# ------------------------
def two_theta(d: float, wavelength: float = 1.5406) -> float:
    """Convert d‑spacing to Bragg angle 2θ (degrees) using Cu Kα radiation."""
    if d <= 0:
        raise ValueError("d must be positive for Bragg calculation.")
    theta_rad = math.asin(wavelength / (2 * d))
    return math.degrees(2 * theta_rad)


def simulate_xrd(params: Dict, max_hkl: int = 5) -> List[Tuple[float, float, float]]:
    """Return a list of (2θ, intensity, d) tuples for all h,k,l ≤ max_hkl."""
    peaks = []
    for h in range(max_hkl + 1):
        for k in range(max_hkl + 1):
            for l in range(max_hkl + 1):
                if h == k == l == 0:
                    continue
                try:
                    d_val = d_spacing(h, k, l, params)
                    twotheta = two_theta(d_val)
                    intensity = abs(structure_factor(h, k, l, params)) ** 2 / (d_val ** 2)
                    peaks.append((twotheta, intensity, d_val))
                except ValueError:
                    continue
    peaks.sort(key=lambda x: x[0])
    return peaks
