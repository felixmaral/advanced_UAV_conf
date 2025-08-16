# Real Performance Development Plan

This document describes the goals and steps for the **`real-performance` branch**, which aims to replace placeholder performance models with actual computations using OpenVSP capabilities.

---

## 🎯 Goals

- Transition from **placeholder outputs** (`cL`, `cD`, `cM`, structural weights, RCS, etc.) to **real performance metrics**.  
- Ensure compatibility with the current `design_space` workflow.  
- Maintain robustness: handle cases where OpenVSP fails gracefully, logging errors without breaking the pipeline.  
- Export results to CSV as currently implemented, but now with real performance data.

---

## 📌 Work Plan

### 1. Aerodynamics
- Integrate **VSPAERO** solver:
  - Run `vsp.ExecVSPAERO` or equivalent solver interface.
  - Extract `CL`, `CD`, `CM` for the given flow conditions.
- Validate results against simple configurations (e.g., rectangular wing).

### 2. Structural Performance
- Use **Mass Properties** analysis:
  - Run `vsp.ComputeMassProps()`.
  - Extract inertia tensor, CG, and reference weights.
- Define a **structural performance metric** (e.g., structural efficiency, weight ratio).

### 3. Radar Cross Section (RCS)
- Employ **CompGeom analysis**:
  - Run `vsp.ComputeCompGeom()`.
  - Derive a simple approximation of RCS (e.g., based on projected area or bounding box).
- Optionally extend later with more advanced EM-based approximations.

### 4. Weight Estimation
- Combine **MassProps results** with structural metrics.
- Compute `Wstructure` and `Wempty` consistently with UAV configuration.

---

## ✅ Deliverables

- Updated versions of:
  - `aerodynamics_performance`
  - `structural_performance`
  - `rcs_performance`
  - `weights`
- Documentation of assumptions and limitations.
- Updated `test_advanced_UAV.py` to confirm the pipeline runs end-to-end with real metrics.

---

## 🔄 Development Strategy

1. Start with **stubs** calling OpenVSP analyses but returning safe defaults when failures occur.
2. Incrementally implement each module:
   - Aerodynamics → Structural → RCS → Weights.
3. Validate each stage with small UAV test cases.
4. Merge improvements back to `main` once stable.

---

## 📝 Notes

- The `designs/` directory remains the export target for generated CSVs.  
- All new computations must catch and log exceptions without halting sampling.  
- Placeholders will be fully removed once validation is complete.  