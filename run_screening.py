"""
DWSIM Python Automation - Screening Task
Automated headless flowsheet construction, PFR simulation, Distillation Column
simulation, and parametric sweeps via Python.NET.
"""

import os
import sys
import csv
from pathlib import Path

#This code has some parts that cater to a macos (only the plots)
# set non-interactive backend BEFORE importing pyplot
import matplotlib
matplotlib.use("Agg") 
import matplotlib.pyplot as plt
import pandas as pd
from pythonnet import load

# ---------------------------------------------------------------------------
# Dynamic OS Path Detection
# ---------------------------------------------------------------------------
if sys.platform == "darwin":
    DWSIM_DIR = Path("/Applications/DWSIM.app/Contents/MacOS")
elif sys.platform == "win32":
    DWSIM_DIR = Path(os.environ.get("ProgramFiles", "C:\\Program Files")) / "DWSIM"
else:
    DWSIM_DIR = Path("/opt/dwsim")

PROJECT_ROOT = Path(__file__).resolve().parent

# Fallback paths for custom compiled DLLs vs Installed App DLLs
DWSIM_AUTOMATION_DLL = (
    PROJECT_ROOT
    / "dwsim10"
    / "engine"
    / "DWSIM.Automation.DynamicRunner"
    / "bin"
    / "Release"
    / "net10.0"
    / "DWSIM.Automation.DynamicRunner.dll"
)
DWSIM_SOLVER_DLL = (
    PROJECT_ROOT
    / "dwsim10"
    / "engine"
    / "DWSIM.FlowsheetSolver"
    / "bin"
    / "Release"
    / "net10.0"
    / "DWSIM.FlowsheetSolver.dll"
)

# ---------------------------------------------------------------------------
# DWSIM Initialization & Resolvers
# ---------------------------------------------------------------------------
def setup_dwsim_dependency_resolver():
    from System.Runtime.Loader import AssemblyLoadContext

    def resolve_assembly(load_context, assembly_name):
        dll_name = f"{assembly_name.Name}.dll"
        dll_path = DWSIM_DIR / dll_name
        if dll_path.exists():
            return load_context.LoadFromAssemblyPath(str(dll_path))
        return None

    AssemblyLoadContext.Default.Resolving += resolve_assembly


def initialize_dwsim():
    load("coreclr")
    setup_dwsim_dependency_resolver()

    import clr

    if DWSIM_AUTOMATION_DLL.exists():
        clr.AddReference(str(DWSIM_AUTOMATION_DLL))
    else:
        clr.AddReference(str(DWSIM_DIR / "DWSIM.Automation.dll"))

    if DWSIM_SOLVER_DLL.exists():
        clr.AddReference(str(DWSIM_SOLVER_DLL))
    else:
        clr.AddReference(str(DWSIM_DIR / "DWSIM.FlowsheetSolver.dll"))

    clr.AddReference(str(DWSIM_DIR / "DWSIM.Interfaces.dll"))
    clr.AddReference(str(DWSIM_DIR / "DWSIM.Thermodynamics.dll"))
    clr.AddReference(str(DWSIM_DIR / "DWSIM.UnitOperations.dll"))


def run_solver(flowsheet):
    """Executes the headless flowsheet calculation."""
    import System
    from DWSIM.GlobalSettings import Settings

    solver_dll = DWSIM_SOLVER_DLL if DWSIM_SOLVER_DLL.exists() else (DWSIM_DIR / "DWSIM.FlowsheetSolver.dll")
    solver_assembly = System.Reflection.Assembly.LoadFrom(str(solver_dll))
    solver_type = solver_assembly.GetType("DWSIM.FlowsheetSolver.FlowsheetSolver")

    solve_method = next((m for m in solver_type.GetMethods() if m.Name == "SolveFlowsheet"), None)
    if solve_method is None:
        raise RuntimeError("SolveFlowsheet method not found.")

    from System import Int32, Boolean

    arguments = [
        flowsheet,
        Int32(int(Settings.SolverMode)),
        None,
        Boolean(False),
        Boolean(False),
        None,
        None,
        None,
        Boolean(True),
    ]

    errors = solve_method.Invoke(None, arguments)
    if errors is not None and errors.Count > 0:
        err_list = [str(err) for err in errors]
        raise RuntimeError(f"Solver errors: {'; '.join(err_list)}")


# ---------------------------------------------------------------------------
# Part A: PFR Simulation Function
# ---------------------------------------------------------------------------
def simulate_pfr(volume=1.0, feed_temp_k=500.0, molar_flow=1.0):
    import System
    from DWSIM.DynamicRunner import Flowsheet
    from DWSIM.UnitOperations.Reactors import OperationMode
    from System.Collections.Generic import Dictionary

    flowsheet = Flowsheet(None, None)
    flowsheet.Init()

    flowsheet.AddCompound("N-pentane")
    flowsheet.AddCompound("Isopentane")
    flowsheet.CreateAndAddPropertyPackage("Peng-Robinson (PR)")

    feed = flowsheet.AddFlowsheetObject("Material Stream", "PFR Feed")
    pfr = flowsheet.AddFlowsheetObject("Plug-Flow Reactor (PFR)", "PFR")
    product = flowsheet.AddFlowsheetObject("Material Stream", "PFR Product")

    pfr.Volume = float(volume)
    pfr.dV = max(0.001, float(volume) / 100.0)
    pfr.ReactorOperationMode = OperationMode.Isothermic
    pfr.OutletTemperature = float(feed_temp_k)

    # Set feed stream
    feed_type = feed.GetType()
    defined_flow_prop = feed_type.GetProperty("DefinedFlow")
    flow_enum_type = defined_flow_prop.PropertyType
    flow_names = list(System.Enum.GetNames(flow_enum_type))
    molar_name = next((name for name in flow_names if name.lower() in ("molar", "mole")), None)
    molar_flow_spec = System.Enum.Parse(flow_enum_type, molar_name)
    defined_flow_prop.SetValue(feed, molar_flow_spec, None)

    phases = feed_type.GetProperty("Phases").GetValue(feed, None)
    phase0 = phases[0]
    phase0.Properties.temperature = float(feed_temp_k)
    phase0.Properties.pressure = 101325.0
    phase0.Properties.molarflow = float(molar_flow)
    phase0.Compounds["N-pentane"].MoleFraction = 1.0
    phase0.Compounds["Isopentane"].MoleFraction = 0.0

    # Kinetic reaction: N-pentane -> Isopentane
    stoich = Dictionary[str, float]()
    stoich["N-pentane"] = -1.0
    stoich["Isopentane"] = 1.0

    direct_orders = Dictionary[str, float]()
    direct_orders["N-pentane"] = 1.0
    direct_orders["Isopentane"] = 0.0

    reverse_orders = Dictionary[str, float]()
    reverse_orders["N-pentane"] = 0.0
    reverse_orders["Isopentane"] = 0.0

    rxn = flowsheet.CreateKineticReaction(
        "Pentane_Isomerization",
        "Kinetic isomerization",
        stoich,
        direct_orders,
        reverse_orders,
        "N-pentane",
        "Mixture",
        "Molar Concentration",
        "mol",
        "mol/m3/s",
        1.0e-3,
        50000.0,
        0.0,
        0.0,
        "",
        "",
    )
    flowsheet.AddReaction(rxn)

    rxn_set = flowsheet.CreateReactionSet("PFR_Set", "PFR Set")
    flowsheet.AddReactionSet(rxn_set)
    flowsheet.AddReactionToSet(rxn.ID, rxn_set.ID, True, 0)
    pfr.ReactionSetID = rxn_set.ID
    pfr.ReactionSetName = rxn_set.Name

    flowsheet.ConnectObjects(feed.GraphicObject, pfr.GraphicObject, 0, 0)
    flowsheet.ConnectObjects(pfr.GraphicObject, product.GraphicObject, 0, 0)

    run_solver(flowsheet)

    # Extract Results via Reflection
    prod_type = product.GetType()
    phases_array = prod_type.GetProperty("PhasesArray").GetValue(product, None)
    out_phase = phases_array[0]
    out_props = out_phase.GetType().GetProperty("Properties").GetValue(out_phase, None)

    t_out = float(out_props.GetType().GetProperty("temperature").GetValue(out_props, None))
    compounds = out_phase.GetType().GetProperty("Compounds").GetValue(out_phase, None)

    n_flow = float(compounds["N-pentane"].GetType().GetProperty("MolarFlow").GetValue(compounds["N-pentane"], None) or 0.0)
    iso_flow = float(compounds["Isopentane"].GetType().GetProperty("MolarFlow").GetValue(compounds["Isopentane"], None) or 0.0)
    conversion = ((molar_flow - n_flow) / molar_flow) * 100.0

    heat_duty = 0.0
    try:
        heat_duty = float(pfr.EnergyFlow)
    except Exception:
        pass

    return {
        "status": "Success",
        "volume_m3": volume,
        "feed_temp_k": feed_temp_k,
        "conversion_pct": conversion,
        "n_pentane_flow_mols": n_flow,
        "isopentane_flow_mols": iso_flow,
        "heat_duty_w": heat_duty,
        "outlet_temp_k": t_out,
    }


# ---------------------------------------------------------------------------
# Part B: Distillation Column Simulation Function
# ---------------------------------------------------------------------------
def simulate_column(stages=15, feed_stage=8, reflux_ratio=2.0, distillate_rate=0.5):
    import System
    from DWSIM.DynamicRunner import Flowsheet

    flowsheet = Flowsheet(None, None)
    flowsheet.Init()

    flowsheet.AddCompound("N-pentane")
    flowsheet.AddCompound("Isopentane")
    flowsheet.CreateAndAddPropertyPackage("Peng-Robinson (PR)")

    col_feed = flowsheet.AddFlowsheetObject("Material Stream", "Col_Feed")
    distillate = flowsheet.AddFlowsheetObject("Material Stream", "Distillate")
    bottoms = flowsheet.AddFlowsheetObject("Material Stream", "Bottoms")
    cond_duty = flowsheet.AddFlowsheetObject("Energy Stream", "Condenser_Duty")
    reb_duty = flowsheet.AddFlowsheetObject("Energy Stream", "Reboiler_Duty")

    feed_type = col_feed.GetType()
    defined_flow_prop = feed_type.GetProperty("DefinedFlow")
    flow_enum = defined_flow_prop.PropertyType
    molar_name = next((n for n in list(System.Enum.GetNames(flow_enum)) if n.lower() in ("molar", "mole")), None)
    defined_flow_prop.SetValue(col_feed, System.Enum.Parse(flow_enum, molar_name), None)

    phases = feed_type.GetProperty("Phases").GetValue(col_feed, None)
    phase0 = phases[0]
    phase0.Properties.temperature = 310.0
    phase0.Properties.pressure = 150000.0
    phase0.Properties.molarflow = 1.0
    phase0.Compounds["N-pentane"].MoleFraction = 0.50
    phase0.Compounds["Isopentane"].MoleFraction = 0.50

    col = flowsheet.AddFlowsheetObject("Distillation Column", "Dist_Column")
    col.NumberOfStages = int(stages)
    col.FeedStage = int(feed_stage)
    col.RefluxRatio = float(reflux_ratio)

    try:
        col.DistillateFlow = float(distillate_rate)
    except Exception:
        pass

    flowsheet.ConnectObjects(col_feed.GraphicObject, col.GraphicObject, 0, 0)
    flowsheet.ConnectObjects(col.GraphicObject, distillate.GraphicObject, 0, 0)
    flowsheet.ConnectObjects(col.GraphicObject, bottoms.GraphicObject, 1, 0)
    flowsheet.ConnectObjects(col.GraphicObject, cond_duty.GraphicObject, 2, 0)
    flowsheet.ConnectObjects(col.GraphicObject, reb_duty.GraphicObject, 3, 0)

    run_solver(flowsheet)

    dist_phases = distillate.GetType().GetProperty("PhasesArray").GetValue(distillate, None)
    dist_comps = dist_phases[0].GetType().GetProperty("Compounds").GetValue(dist_phases[0], None)
    dist_iso_purity = float(dist_comps["Isopentane"].GetType().GetProperty("MoleFraction").GetValue(dist_comps["Isopentane"], None))

    bot_phases = bottoms.GetType().GetProperty("PhasesArray").GetValue(bottoms, None)
    bot_comps = bot_phases[0].GetType().GetProperty("Compounds").GetValue(bot_phases[0], None)
    bot_n_purity = float(bot_comps["N-pentane"].GetType().GetProperty("MoleFraction").GetValue(bot_comps["N-pentane"], None))

    c_duty = float(cond_duty.GetType().GetProperty("EnergyFlow").GetValue(cond_duty, None) or 0.0)
    r_duty = float(reb_duty.GetType().GetProperty("EnergyFlow").GetValue(reb_duty, None) or 0.0)

    return {
        "status": "Success",
        "stages": stages,
        "feed_stage": feed_stage,
        "reflux_ratio": reflux_ratio,
        "distillate_rate": distillate_rate,
        "distillate_isopentane_purity": dist_iso_purity,
        "bottoms_npentane_purity": bot_n_purity,
        "condenser_duty_kw": c_duty / 1000.0,
        "reboiler_duty_kw": r_duty / 1000.0,
    }


# ---------------------------------------------------------------------------
# Main Execution & Sweeps
# ---------------------------------------------------------------------------
def main():
    print("=" * 70)
    print("DWSIM HEADLESS SCREENING AUTOMATION TASK")
    print("=" * 70)

    initialize_dwsim()
    import System

    # 1. Base Simulations
    print("\n[PART A] Running Base PFR Case...")
    pfr_base = simulate_pfr(volume=1.0, feed_temp_k=500.0)
    print(f"  -> PFR Conversion: {pfr_base['conversion_pct']:.2f}%")
    print(f"  -> Outlet n-pentane: {pfr_base['n_pentane_flow_mols']:.4f} mol/s")
    print(f"  -> Outlet isopentane: {pfr_base['isopentane_flow_mols']:.4f} mol/s")

    print("\n[PART B] Running Base Distillation Column Case...")
    try:
        col_base = simulate_column(stages=15, feed_stage=8, reflux_ratio=2.5, distillate_rate=0.5)
        print(f"  -> Distillate Isopentane Purity: {col_base['distillate_isopentane_purity']*100:.2f}%")
        print(f"  -> Bottoms N-pentane Purity: {col_base['bottoms_npentane_purity']*100:.2f}%")
    except Exception as e:
        print(f"  -> Column baseline calculation note: {e}")

    # 2. Parametric Sweep - PFR
    print("\n[PART C] Executing Parametric Sweeps...")
    pfr_results = []
    volumes = [0.5, 1.0, 1.5, 2.0]
    temperatures = [450.0, 480.0, 500.0, 520.0]

    for v in volumes:
        for t in temperatures:
            try:
                res = simulate_pfr(volume=v, feed_temp_k=t)
                pfr_results.append(res)
                print(f"  PFR Sweep [V={v} m³, T={t} K] -> Conversion: {res['conversion_pct']:.2f}%")
            except Exception as ex:
                print(f"  PFR Sweep [V={v} m³, T={t} K] -> Failed: {ex}")
                pfr_results.append({
                    "status": "Failed",
                    "volume_m3": v,
                    "feed_temp_k": t,
                    "conversion_pct": None,
                    "n_pentane_flow_mols": None,
                    "isopentane_flow_mols": None,
                    "heat_duty_w": None,
                    "outlet_temp_k": None,
                })

    # 3. Parametric Sweep - Column
    col_results = []
    stages_sweep = [10, 15, 20]
    reflux_sweep = [1.5, 2.5, 3.5]

    for s in stages_sweep:
        for r in reflux_sweep:
            feed_s = max(2, s // 2)
            try:
                res = simulate_column(stages=s, feed_stage=feed_s, reflux_ratio=r, distillate_rate=0.5)
                col_results.append(res)
                print(f"  Col Sweep [Stages={s}, RR={r}] -> Dist Purity: {res['distillate_isopentane_purity']*100:.2f}%")
            except Exception as ex:
                print(f"  Col Sweep [Stages={s}, RR={r}] -> Handled: {ex}")
                col_results.append({
                    "status": "Failed",
                    "stages": s,
                    "feed_stage": feed_s,
                    "reflux_ratio": r,
                    "distillate_rate": 0.5,
                    "distillate_isopentane_purity": None,
                    "bottoms_npentane_purity": None,
                    "condenser_duty_kw": None,
                    "reboiler_duty_kw": None,
                })

    # Export to results.csv
    df_pfr = pd.DataFrame(pfr_results)
    df_pfr["unit_operation"] = "PFR"
    df_col = pd.DataFrame(col_results)
    df_col["unit_operation"] = "DistillationColumn"

    combined_df = pd.concat([df_pfr, df_col], ignore_index=True)
    combined_df.to_csv("results.csv", index=False)
    print("\n✓ Results logged successfully to results.csv")

    # 4. Generate Robust Plots
    print("\nGenerating Parametric Plots...")
    try:
        valid_pfr = df_pfr[df_pfr["status"] == "Success"].copy()
        
        if not valid_pfr.empty:
            # Explicit numeric conversion to ensure clean Matplotlib series
            valid_pfr["volume_m3"] = pd.to_numeric(valid_pfr["volume_m3"])
            valid_pfr["conversion_pct"] = pd.to_numeric(valid_pfr["conversion_pct"])
            valid_pfr["feed_temp_k"] = pd.to_numeric(valid_pfr["feed_temp_k"])

            fig, ax = plt.subplots(figsize=(8, 5))
            for t in sorted(valid_pfr["feed_temp_k"].unique()):
                subset = valid_pfr[valid_pfr["feed_temp_k"] == t].sort_values("volume_m3")
                if not subset.empty:
                    ax.plot(
                        subset["volume_m3"],
                        subset["conversion_pct"],
                        marker="o",
                        linewidth=2,
                        label=f"T = {t:.0f} K"
                    )

            ax.set_title("PFR Isomerization: Conversion vs. Reactor Volume", fontsize=12, fontweight="bold")
            ax.set_xlabel("Reactor Volume (m³)", fontsize=10)
            ax.set_ylabel("Conversion (%)", fontsize=10)
            ax.grid(True, linestyle="--", alpha=0.6)
            ax.legend(title="Feed Temperature")
            plt.tight_layout()

            plot_path = PROJECT_ROOT / "pfr_parametric_sweep.png"
            fig.savefig(str(plot_path), dpi=300)
            plt.close(fig)
            print(f"✓ Saved plot successfully: {plot_path}")
        else:
            print("⚠ Plotting skipped: No successful PFR data points found.")

    except Exception as plot_err:
        print(f"✗ Could not generate plots: {type(plot_err).__name__}: {plot_err}")


if __name__ == "__main__":
    main()