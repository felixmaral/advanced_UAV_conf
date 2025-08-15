from typing import Tuple

def aerodynamics_performance(mass_props, flow) -> Tuple[float, float, float]:
    return 0.5, 0.1, 0.05  # TODO: implementar

def structural_performance(comp_geom, Qaero: Tuple[float, float, float]) -> float:
    return 1000.0  # TODO: implementar

def rcs_performance(comp_geom) -> float:
    return -20.0  # TODO: implementar

def weights(vi, w_structure: float, cL: float, cD: float) -> float:
    return 1.2 * w_structure  # TODO: implementar