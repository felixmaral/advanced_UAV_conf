# advanced_UAV_conf

Python package for generating **UAV (Unmanned Aerial Vehicle)** configurations, building their geometry in **OpenVSP**, and computing basic performance metrics (currently placeholders).

## Package Structure
advanced_uav_conf/  
├── init.py: Makes the folder a Python package; exposes main API  
├── types.py: Data classes and type definitions  
├── geometry.py: OpenVSP geometry creation and parameter setting  
├── performance.py: Placeholder performance analysis functions  
└── design.py: Main design_space workflow  

## Input / Output

**Input to `design_space`:**
- `nconfig`: number of configurations to generate
- `Xlimits`: list of `(min, max)` tuples for 14 design variables
- Optional:
  - `seed`: random seed for reproducible sampling
  - `flow`: `FlowConditions` dataclass (Re, Mach, Alpha)

**Output:**
- **Pandas DataFrame** with:
  - Design variables (wing, tail, fuselage parameters)
  - Performance metrics (`cL`, `cD`, `cM`, `sigma_dBsm`, `Wstructure`, `Wempty`)
  - Error messages if any geometry step fails

## Current Status
⏸ **Paused** – The package runs end-to-end with placeholder functions for performance.  
Integration with **OpenVSP** is in place but needs parameter name verification.  
Real aerodynamic, structural, RCS, and weight calculations are pending.

## Implemented
- Modular design for maintainability
- LHS sampling (`smt`) with reproducibility option
- OpenVSP geometry creation (wing, tail, fuselage)
- Clear DataFrame output with explicit columns
- Error handling and parameter validation

## Installation

1. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

2. **Install OpenVSP**  
- Download and install from the official site: [https://openvsp.org/](https://openvsp.org/)  
- Ensure the Python API (`openvsp`) is available in your environment  

## Example Usage
```python
from advanced_uav_conf import design_space, FlowConditions

df = design_space(
    nconfig=10,
    Xlimits=[(0, 1)] * 14,
    seed=42,
    flow=FlowConditions(Re=1e6, Mach=0.8, Alpha=5)
)
print(df.head())
```

## Acknowledgments
This work is an independent implementation based on existing concepts in UAV configuration and analysis.  
It is not affiliated with, nor derived from, any specific existing codebase.