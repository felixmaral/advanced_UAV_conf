from typing import Iterable, Tuple, List
import numpy as np
import pandas as pd
import openvsp as vsp
from smt.sampling_methods import LHS

from .types import FlowConditions
from .geometry import clear_model, build_wing, build_tail, build_fuselage
from .performance import (
    aerodynamics_performance, structural_performance, rcs_performance, weights
)

def _validate_limits(Xlimits: Iterable[Tuple[float, float]], expected_dim=14) -> np.ndarray:
    xl = np.asarray(Xlimits, dtype=float)
    if xl.shape != (expected_dim, 2) or np.any(xl[:,0] > xl[:,1]):
        raise ValueError(f"Xlimits must be ({expected_dim},2) with min<=max.")
    return xl

def design_space(nconfig: int, Xlimits: Iterable[Tuple[float, float]],
                 *, seed=None, flow: FlowConditions = FlowConditions()) -> pd.DataFrame:
    xlimits = _validate_limits(Xlimits)
    sampling = LHS(xlimits=xlimits, criterion="m", random_state=seed)
    V = sampling(nconfig)

    rows: List[dict] = []
    for i in range(nconfig):
        vi = np.asarray(V[i], dtype=float)
        clear_model()
        try:
            build_wing(*vi[0:5])
            build_tail(*vi[5:10])
            build_fuselage(*vi[10:14])
            vsp.Update()

            mass_props = vsp.ComputeMassProps()
            comp_geom  = vsp.ComputeCompGeom()

            cL, cD, cM = aerodynamics_performance(mass_props, flow)
            Wstructure = structural_performance(comp_geom, (cL, cD, cM))
            sigma_dBsm = rcs_performance(comp_geom)
            Wempty     = weights(vi, Wstructure, cL, cD)
            err = ""
        except Exception as ex:
            cL = cD = cM = sigma_dBsm = Wstructure = Wempty = np.nan
            err = str(ex)

        rows.append({
            "wing_aspect": vi[0], "wing_taper": vi[1], "wing_sweep": vi[2], "wing_dihedral": vi[3], "wing_area": vi[4],
            "tail_aspect": vi[5], "tail_taper": vi[6], "tail_sweep": vi[7], "tail_dihedral": vi[8], "tail_area": vi[9],
            "fuse_len_fore": vi[10], "fuse_len_mid": vi[11], "fuse_len_aft": vi[12], "fuse_diameter": vi[13],
            "cL": cL, "cD": cD, "cM": cM, "sigma_dBsm": sigma_dBsm,
            "Wstructure": Wstructure, "Wempty": Wempty,
            "error": err
        })
    return pd.DataFrame.from_records(rows)