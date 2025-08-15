import openvsp as vsp

def clear_model():
    vsp.ClearVSPModel()

def set_param(geom_id: int, parm: str, group: str, value: float):
    pid = vsp.GetParm(geom_id, parm, group)
    if not pid:
        raise RuntimeError(f"Param not found: {parm}@{group}")
    vsp.SetParmVal(pid, float(value))

def build_wing(vi0, vi1, vi2, vi3, vi4):
    gid = vsp.AddGeom("WING")
    set_param(gid, "Aspect", "WingGeom", vi0)
    set_param(gid, "Taper", "WingGeom", vi1)
    set_param(gid, "Sweep", "XSec_0", vi2)
    set_param(gid, "Dihedral", "XSec_0", vi3)
    set_param(gid, "Area", "WingGeom", vi4)
    return gid

def build_tail(vi5, vi6, vi7, vi8, vi9):
    gid = vsp.AddGeom("WING")
    set_param(gid, "Aspect", "WingGeom", vi5)
    set_param(gid, "Taper", "WingGeom", vi6)
    set_param(gid, "Sweep", "XSec_0", vi7)
    set_param(gid, "Dihedral", "XSec_0", vi8)
    set_param(gid, "Area", "WingGeom", vi9)
    return gid

def build_fuselage(vi10, vi11, vi12, vi13):
    gid = vsp.AddGeom("FUSELAGE")
    set_param(gid, "Length_Fore", "FuselageGeom", vi10)
    set_param(gid, "Length_Mid", "FuselageGeom", vi11)
    set_param(gid, "Length_Aft", "FuselageGeom", vi12)
    set_param(gid, "Diameter", "FuselageGeom", vi13)
    return gid