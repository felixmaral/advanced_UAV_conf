# performance.py — placeholders (no VSPAERO)
from typing import Tuple


def aerodynamics_performance(mass_props, flow) -> Tuple[float, float, float]:
    # valores fijos de prueba
    return 0.5, 0.1, 0.05


def structural_performance(comp_geom, Qaero: Tuple[float, float, float]) -> float:
    # valor fijo de prueba
    return 1000.0


def rcs_performance(comp_geom) -> float:
    # valor fijo de prueba
    return -20.0


def weights(vi, w_structure: float, cL: float, cD: float) -> float:
    # valor fijo de prueba (proporcional)
    return 1.2 * w_structure