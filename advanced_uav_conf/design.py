# design.py — muestreo + construcción geométrica con placeholders
import time
import logging
import os
import contextlib
from typing import Iterable, Tuple, List

import numpy as np
import pandas as pd

try:
    import openvsp.vsp as vsp  # prefer core
except Exception:
    import openvsp as vsp

from smt.sampling_methods import LHS

from .uav_types import FlowConditions
from .geometry import clear_model, build_wing, build_tail, build_fuselage
from .performance import (
    aerodynamics_performance, structural_performance, rcs_performance, weights
)

_logger = logging.getLogger("advanced_uav_conf")
if not _logger.handlers:
    _level = getattr(logging, os.environ.get("ADV_UAV_LOG_LEVEL", "INFO").upper(), logging.INFO)
    logging.basicConfig(level=_level, format="[%(levelname)s] %(message)s")
    _logger.setLevel(_level)


@contextlib.contextmanager
def _silence_vsp_io(enabled=True):
    if not enabled:
        yield
        return
    devnull = os.open(os.devnull, os.O_WRONLY)
    saved_out, saved_err = os.dup(1), os.dup(2)
    try:
        os.dup2(devnull, 1)
        os.dup2(devnull, 2)
        yield
    finally:
        os.dup2(saved_out, 1)
        os.dup2(saved_err, 2)
        os.close(devnull)


def _validate_limits(Xlimits: Iterable[Tuple[float, float]], expected_dim=14) -> np.ndarray:
    xl = np.asarray(Xlimits, dtype=float)
    if xl.shape != (expected_dim, 2) or np.any(xl[:, 0] > xl[:, 1]):
        raise ValueError(f"Xlimits must be ({expected_dim},2) with min<=max. Got {xl.shape}.")
    return xl


# opcionales (no se usan por ahora, pero quedan por si el test los llama)
def _compute_mass_props_safe():
    try:
        return vsp.ComputeMassProps()
    except Exception:
        return None


def _compute_comp_geom_safe():
    try:
        return vsp.ComputeCompGeom()
    except Exception:
        return None


def design_space(
    nconfig: int,
    Xlimits: Iterable[Tuple[float, float]],
    *,
    seed=None,
    flow: FlowConditions = FlowConditions(),
) -> pd.DataFrame:
    t0 = time.perf_counter()
    _logger.info("design_space: start (nconfig=%d, seed=%s)", nconfig, str(seed))

    xlimits = _validate_limits(Xlimits)
    sampling = LHS(xlimits=xlimits, criterion="m", random_state=seed)
    V = sampling(nconfig)

    rows: List[dict] = []
    for i in range(nconfig):
        ti = time.perf_counter()
        vi = np.asarray(V[i], dtype=float)
        errs: List[str] = []

        clear_model()
        with _silence_vsp_io(enabled=os.environ.get("ADV_UAV_SILENCE", "1") == "1"):
            try:
                build_wing(*vi[0:5])
            except Exception as e:
                errs.append(f"build_wing: {e}")
            try:
                build_tail(*vi[5:10])
            except Exception as e:
                errs.append(f"build_tail: {e}")
            try:
                build_fuselage(*vi[10:14])
            except Exception as e:
                errs.append(f"build_fuselage: {e}")
            try:
                vsp.Update()
            except Exception as e:
                errs.append(f"vsp.Update: {e}")

        try:
            cL, cD, cM = aerodynamics_performance(None, flow)
            Wstructure = structural_performance(None, (cL, cD, cM))
            sigma_dBsm = rcs_performance(None)
            Wempty     = weights(vi, Wstructure, cL, cD)
            err = "; ".join(errs)
        except Exception as ex:
            cL = cD = cM = sigma_dBsm = Wstructure = Wempty = np.nan
            prefix = "; ".join(errs)
            err = f"{prefix}; {ex}" if prefix else str(ex)

        rows.append({
            "wing_aspect": vi[0], "wing_taper": vi[1], "wing_sweep": vi[2], "wing_dihedral": vi[3], "wing_area": vi[4],
            "tail_aspect": vi[5], "tail_taper": vi[6], "tail_sweep": vi[7], "tail_dihedral": vi[8], "tail_area": vi[9],
            "fuse_len_fore": vi[10], "fuse_len_mid": vi[11], "fuse_len_aft": vi[12], "fuse_diameter": vi[13],
            "cL": cL, "cD": cD, "cM": cM, "sigma_dBsm": sigma_dBsm,
            "Wstructure": Wstructure, "Wempty": Wempty,
            "error": err
        })
        _logger.info("[case %d] done in %.3fs%s", i, time.perf_counter() - ti, "" if not err else f" (errors: {err})")

    df = pd.DataFrame.from_records(rows)
    _logger.info("design_space: end in %.3fs (rows=%d, cols=%d)", time.perf_counter() - t0, *df.shape)

    # Mostrar el DataFrame
    print(df)

    # Pedir al usuario un nombre para el archivo
    filename = input("Introduce un nombre para guardar el diseño (sin extensión): ").strip()
    if not filename:
        filename = "design_output"

    # Crear carpeta designs si no existe
    os.makedirs("designs", exist_ok=True)
    outpath = os.path.join("designs", f"{filename}.csv")
    df.to_csv(outpath, index=False)
    print(f"[INFO] Diseño guardado en {outpath}")

    return df