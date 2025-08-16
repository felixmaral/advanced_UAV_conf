# run_design.py
# ─────────────────────────────────────────────
# Script to launch UAV design experiments
# This file can be edited directly to define:
#   - The design space (parameter limits)
#   - Number of configurations to generate
#   - Flow conditions (Reynolds, Mach, Alpha)
# Results will be automatically saved under ./designs

from advanced_uav_conf import design_space, FlowConditions
import openvsp as vsp  # Import OpenVSP API

# ─────────────────────────────────────────────
# Design variable limits (Xlimits):
# Each tuple (min, max) defines the range for a variable
# Wing: aspect, taper, sweep, dihedral, area
# Tail: aspect, taper, sweep, dihedral, area
# Fuselage: fore length, mid length, aft length, diameter
# ─────────────────────────────────────────────
Xlimits = [
    (8, 12),      # Wing aspect ratio
    (0.35, 0.70), # Wing taper ratio
    (0, 20),      # Wing sweep angle (deg)
    (0, 8),       # Wing dihedral angle (deg)
    (0.8, 2.7),   # Wing area (m^2)  -> ~ b ≈ 2.5–5.5 m para AR 8–12

    (4, 7),       # Tail aspect ratio
    (0.35, 0.80), # Tail taper ratio
    (0, 20),      # Tail sweep angle (deg)
    (0, 12),      # Tail dihedral angle (deg)
    (0.20, 0.80), # Tail area (m^2) ≈ 15–30% de S_alas

    (0.3, 0.9),   # Fuselage fore length (m)
    (1.0, 2.5),   # Fuselage mid length (m)
    (0.7, 1.6),   # Fuselage aft length (m)
    (0.12, 0.35), # Fuselage diameter (m) -> D/span ≤ ~0.12
]

# ─────────────────────────────────────────────
# Experiment setup
# nconfig: number of configurations (samples)
# seed: random seed for reproducibility
# FlowConditions: aerodynamic environment
#   Re   -> Reynolds number
#   Mach -> Mach number
#   Alpha-> Angle of attack (deg)
# ─────────────────────────────────────────────
vsp.ClearVSPModel()
df = design_space(
    nconfig=100,
    Xlimits=Xlimits,
    seed=44,
    flow=FlowConditions(Re=1e6, Mach=0.8, Alpha=5.0)
)

# ─────────────────────────────────────────────
# Results
# The DataFrame contains the design parameters + metrics
# Automatically saved under ./designs with experiment name
# ─────────────────────────────────────────────
# print(df.head())  # Show first few rows of the DataFrame

# Optional: uncomment to save also in this folder
# df.to_csv("uav_designs.csv", index=False)