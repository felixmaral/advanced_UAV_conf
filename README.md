# advanced_UAV_conf

Python package for generating **UAV (Unmanned Aerial Vehicle)** configurations, building their geometry in **OpenVSP**, and computing basic performance metrics (placeholders yet).

## Project Overview

**Advanced UAV Configurator** is a tool for **parametric exploration of UAV (Unmanned Aerial Vehicle) configurations** in an automated way.

This system allows an engineer to:

- Define a **design space** with key parameters for wing, tail, and fuselage.  
- Generate multiple UAV configurations using systematic or random variations.  
- Automatically evaluate basic aerodynamic metrics (lift, drag, moment) as well as structural and weight characteristics.  
- Store the results in a **DataFrame and CSV files** for further analysis or integration into optimization workflows.  
- Organize generated designs in the `./designs` folder, with the option to **name each experiment** for clarity.  

This environment is particularly useful for **preliminary conceptual design studies** and for **comparing configurations** in the early phases of UAV projects.

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
    nconfig=100,
    Xlimits=[(0, 1)] * 14, # Example
    seed=42,
    flow=FlowConditions(Re=1e6, Mach=0.8, Alpha=5)
)
print(df.head())
```

## Acknowledgments
This work is an independent implementation.  
It is not affiliated with, nor derived from, any specific existing codebase.
