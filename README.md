# DWSIM Python Headless Automation - Screening Task

This repository contains an automated Python solution for simulating a **Plug Flow Reactor (PFR)** and a **Distillation Column** using DWSIM's headless automation libraries via `pythonnet`.

## Deliverables
- `run_screening.py`: Master automated simulation script with programmatic flowsheet setup and parametric sweep engine.
- `requirements.txt`: Python package requirements.
- `results.csv`: Combined parameter and output log for all simulation iterations.
- `pfr_parametric_sweep.png`: Parametric sweep visualization.

## Prerequisites
- DWSIM installed (macOS `/Applications/DWSIM.app`, Windows `C:\Program Files\DWSIM`, or Linux `/opt/dwsim`)
- .NET runtime (CoreCLR/.NET 8/10)
- Python 3.10+

## Setup & Execution

1. **Create and activate a virtual environment:**
```bash
python3 -m venv .venv
source .venv/bin/activate   # On Windows: .venv\Scripts\activate
```
2. **Run the project**
```bash
python run_screening.py
```
