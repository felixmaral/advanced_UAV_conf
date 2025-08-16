# save as quick_vsp_test.py
import openvsp as vsp
import os

def main():
    # 1) Modelo limpio
    vsp.ClearVSPModel()

    # 2) Crear un ala
    wing_id = vsp.AddGeom("WING")
    print("Wing ID:", wing_id)

    # 3) Ajustar algunos parámetros (ejemplos)
    #    Nota: estos nombres existen en builds recientes; si tu build cambia,
    #    puedes consultar parámetros con vsp.PrintMatLab("All")
    vsp.SetParmVal(wing_id, "Aspect",   "WingGeom", 8.0)
    vsp.SetParmVal(wing_id, "Taper",    "WingGeom", 0.4)
    vsp.SetParmVal(wing_id, "Area",     "WingGeom", 20.0)
    vsp.SetParmVal(wing_id, "Sweep",    "XSec_0",   15.0)
    vsp.SetParmVal(wing_id, "Dihedral", "XSec_0",   5.0)

    # 4) Actualizar
    vsp.Update()

    # 5) Guardar el modelo nativo .vsp3
    out_vsp3 = os.path.abspath("demo_wing.vsp3")
    # algunas versiones aceptan 2 argumentos: (path, set)
    try:
        vsp.WriteVSPFile(out_vsp3, vsp.SET_ALL)
    except TypeError:
        vsp.WriteVSPFile(out_vsp3)
    print("Saved:", out_vsp3)

    # 6) (Opcional) Exportar STL
    out_stl = os.path.abspath("demo_wing.stl")
    vsp.ExportFile(out_stl, vsp.SET_ALL, vsp.EXPORT_STL)
    print("Exported STL:", out_stl)

if __name__ == "__main__":
    main()