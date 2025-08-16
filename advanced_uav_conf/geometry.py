# geometry.py — placeholders robustos (sin VSPAERO), sin FindParm errors
try:
    import openvsp.vsp as vsp  # prefer core
except Exception:
    import openvsp as vsp


def clear_model():
    try:
        vsp.ClearVSPModel()
    except Exception:
        pass


# ---------- helpers: NO usan GetParm(nombre,grupo) ----------
def _index_params_by_group(geom_id):
    """Devuelve {grupo: {nombre_param: parm_id}} sin provocar logs de error."""
    mapping = {}
    try:
        pids = vsp.GetGeomParmIDs(geom_id)
    except Exception:
        pids = []
    for pid in pids:
        try:
            name = vsp.GetParmName(pid)
            group = vsp.GetParmGroupName(pid)
        except Exception:
            continue
        mapping.setdefault(group, {})[name] = pid
    return mapping


def _first_xsec_group(geom_id):
    idx = _index_params_by_group(geom_id)
    # prioriza el primer XSec_* existente
    for g in sorted(idx.keys()):
        if g.startswith("XSec_"):
            return g
    for g in ("XSec_0", "XSec_1", "XSec_2"):
        if g in idx:
            return g
    # fallback neutro
    return next(iter(idx.keys()), "XSec_0")


def _set_first(geom_id, names, group, value, idx_cache=None):
    """Intenta poner el primer alias disponible dentro de un grupo. Devuelve True/False."""
    if idx_cache is None:
        idx_cache = _index_params_by_group(geom_id)
    group_params = idx_cache.get(group, {})
    for name in names:
        pid = group_params.get(name, "")
        if pid:
            try:
                vsp.SetParmVal(pid, float(value))
                return True
            except Exception:
                continue
    return False


def _set_any(geom_id, names, groups, value, idx_cache=None):
    """Prueba múltiples grupos (p.ej. FuselageGeom, XSec_0, …). Devuelve True/False."""
    if idx_cache is None:
        idx_cache = _index_params_by_group(geom_id)
    for g in groups:
        if _set_first(geom_id, names, g, value, idx_cache):
            return True
    return False


# ---------- builders ----------
def build_wing(ar, taper, sweep, dihedral, area):
    gid = vsp.AddGeom("WING")
    idx = _index_params_by_group(gid)

    # Aspect ratio & taper: probar alias
    _set_first(gid, ["AR", "Aspect", "AspectRatio"], "WingGeom", ar, idx)
    _set_first(gid, ["TRat", "Taper", "TaperRatio"], "WingGeom", taper, idx)

    # Área: si no existe, calcular Span = sqrt(AR*S)
    set_area = _set_first(gid, ["Area", "PlanformArea", "Sref", "SRef"], "WingGeom", area, idx)
    if not set_area:
        try:
            span = (float(ar) * float(area)) ** 0.5
            _set_first(gid, ["Span", "TotalSpan", "BRef", "Bref"], "WingGeom", span, idx)
        except Exception:
            pass

    # Sweep y Dihedral en la primera sección disponible
    xsec = _first_xsec_group(gid)
    _set_first(gid, ["Sweep", "SweepAng", "SweepDeg"], xsec, sweep, idx)
    _set_first(gid, ["Dihedral", "Dihed"],           xsec, dihedral, idx)

    return gid


def build_tail(*args):
    # El estabilizador se modela como otro wing
    return build_wing(*args)


def build_fuselage(l_fore, l_mid, l_aft, diam):
    gid = vsp.AddGeom("FUSELAGE")
    idx = _index_params_by_group(gid)

    length_groups = ("FuselageGeom", "XSec_0", "XSec_1", "XSec_2")

    # OJO: el orden correcto es (geom_id, names, groups, value, idx)
    _set_any(gid, ["Length_Fore", "LengthFore", "Len_Fore", "Fore_Length"], length_groups, l_fore, idx)
    _set_any(gid, ["Length_Mid",  "LengthMid",  "Len_Mid",  "Mid_Length"],  length_groups, l_mid,  idx)
    _set_any(gid, ["Length_Aft",  "LengthAft",  "Len_Aft",  "Aft_Length"],  length_groups, l_aft,  idx)

    _set_any(gid, ["Diameter", "Dia", "MaxDiameter", "XSec_Diameter"],       length_groups, diam,   idx)

    return gid