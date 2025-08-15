from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Tuple

import numpy as np
import pandas as pd

try:
    import openvsp as vsp  # API típica: 'openvsp' y objeto 'vsp'
except ImportError as e:
    raise ImportError("openvsp is required. Install from the official source.") from e

from smt.sampling_methods import LHS


@dataclass(frozen=True)
class FlowConditions:
    Re: float = 1e6
    Mach: float = 0.8
    Alpha: float = 5.0  # deg


def _validate_limits(xlimits: Iterable[Tuple[float, float]], expected_dim: int = 14) -> np.ndarray:
    xlimits = np.asarray(xlimits, dtype=float)
    if xlimits.ndim != 2 or xlimits.shape != (expected_dim, 2):
        raise ValueError(f"Xlimits must be shape ({expected_dim}, 2). Got {xlimits.shape}.")
    if np.any(xlimits[:, 0] > xlimits[:, 1]):
        raise ValueError("Each (min, max) must satisfy min <= max.")
    return xlimits


def _set_param(geom_id: int, parm: str, group: str, value: float) -> None:
    """Wrapper con chequeo de errores para SetParmVal."""
    pid = vsp.GetParm(geom_id, parm, group)
    if pid == "":
        raise RuntimeError(f"Parameter not found: parm='{parm}' group='{group}'")
    vsp.SetParmVal(pid, float(value))


def aerodynamics_performance(mass_props, flow: FlowConditions) -> Tuple[float, float, float]:
    # TODO: sustituir por implementación real
    return 0.5, 0.1, 0.05  # cL, cD, cM


def structural_performance(comp_geom, Qaero: Tuple[float, float, float]) -> float:
    # TODO: sustituir por implementación real
    return 1000.0  # Wstructure


def rcs_performance(comp_geom) -> float:
    # TODO: sustituir por implementación real
    return -20.0  # sigma_dBsm


def weights(vi: np.ndarray, w_structure: float, cL: float, cD: float) -> float:
    # TODO: sustituir por implementación real
    return 1.2 * w_structure  # Wempty


def design_space(
    nconfig: int,
    Xlimits: Iterable[Tuple[float, float]],
    *,
    seed: int | None = None,
    flow: FlowConditions = FlowConditions(),
) -> pd.DataFrame:
    """
    Generate UAV configurations via LHS, build geometry in OpenVSP, and compute placeholder metrics.

    Args:
        nconfig: number of configurations to generate.
        Xlimits: iterable of (min, max) for 14 design variables, shape (14, 2).
        seed: random seed for reproducibility.
        flow: flow conditions (Re, Mach, Alpha).

    Returns:
        Pandas DataFrame with design variables and metrics per configuration.
    """
    xlimits = _validate_limits(Xlimits, expected_dim=14)

    sampling = LHS(xlimits=xlimits, criterion="m", random_state=seed)
    vconfig = sampling(nconfig)  # shape (nconfig, 14)

    rows: List[dict] = []

    for i in range(nconfig):
        vi = np.asarray(vconfig[i], dtype=float)

        # Limpia el modelo en cada iteración para no acumular geometrías
        vsp.ClearVSPModel()

        try:
            # Wing
            wing_id = vsp.AddGeom("WING")
            _set_param(wing_id, "Aspect", "WingGeom", vi[0])
            _set_param(wing_id, "Taper", "WingGeom", vi[1])
            _set_param(wing_id, "Sweep", "XSec_0", vi[2])
            _set_param(wing_id, "Dihedral", "XSec_0", vi[3])
            _set_param(wing_id, "Area", "WingGeom", vi[4])

            # Tail
            tail_id = vsp.AddGeom("WING")
            _set_param(tail_id, "Aspect", "WingGeom", vi[5])
            _set_param(tail_id, "Taper", "WingGeom", vi[6])
            _set_param(tail_id, "Sweep", "XSec_0", vi[7])
            _set_param(tail_id, "Dihedral", "XSec_0", vi[8])
            _set_param(tail_id, "Area", "WingGeom", vi[9])

            # Fuselage
            fuselage_id = vsp.AddGeom("FUSELAGE")
            _set_param(fuselage_id, "Length_Fore", "FuselageGeom", vi[10])
            _set_param(fuselage_id, "Length_Mid", "FuselageGeom", vi[11])
            _set_param(fuselage_id, "Length_Aft", "FuselageGeom", vi[12])
            _set_param(fuselage_id, "Diameter", "FuselageGeom", vi[13])

            vsp.Update()

            # Una sola pasada de cómputos geométricos
            mass_props = vsp.ComputeMassProps()
            comp_geom = vsp.ComputeCompGeom()

            cL, cD, cM = aerodynamics_performance(mass_props, flow)
            w_structure = structural_performance(comp_geom, (cL, cD, cM))
            sigma_dbsm = rcs_performance(comp_geom)
            w_empty = weights(vi, w_structure, cL, cD)

        except Exception as ex:
            # En caso de error, devuelve NaNs y la causa
            cL = cD = cM = sigma_dbsm = w_structure = w_empty = np.nan
            error_msg = str(ex)
        else:
            error_msg = ""

        rows.append(
            {
                # variables de diseño (explícitas para filtrado/analítica)
                "wing_aspect": vi[0],
                "wing_taper": vi[1],
                "wing_sweep": vi[2],
                "wing_dihedral": vi[3],
                "wing_area": vi[4],
                "tail_aspect": vi[5],
                "tail_taper": vi[6],
                "tail_sweep": vi[7],
                "tail_dihedral": vi[8],
                "tail_area": vi[9],
                "fuse_len_fore": vi[10],
                "fuse_len_mid": vi[11],
                "fuse_len_aft": vi[12],
                "fuse_diameter": vi[13],
                # métricas
                "cL": cL,
                "cD": cD,
                "cM": cM,
                "sigma_dBsm": sigma_dbsm,
                "Wstructure": w_structure,
                "Wempty": w_empty,
                # trazabilidad
                "error": error_msg,
            }
        )

    return pd.DataFrame.from_records(rows)


if __name__ == "__main__":
    # Ejemplo de uso (no se ejecuta en import)
    df = design_space(nconfig=10, Xlimits=[(0, 1)] * 14, seed=42)
    print(df.head())
