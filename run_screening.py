"""
DWSIM Python Automation - Screening Task

Headless Python automation of DWSIM using Python.NET and
DWSIM.Automation.DynamicRunner.
"""

from pathlib import Path

from pythonnet import load


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent

DWSIM_DIR = Path("/Applications/DWSIM.app/Contents/MacOS")

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


# ---------------------------------------------------------------------------
# DWSIM dependency resolution
# ---------------------------------------------------------------------------

def setup_dwsim_dependency_resolver():
    """Resolve DWSIM assemblies from the installed DWSIM directory."""

    from System.Runtime.Loader import AssemblyLoadContext

    def resolve_assembly(load_context, assembly_name):
        dll_name = f"{assembly_name.Name}.dll"
        dll_path = DWSIM_DIR / dll_name

        if dll_path.exists():
            print(f"  Loading DWSIM dependency: {dll_name}")
            return load_context.LoadFromAssemblyPath(str(dll_path))

        return None

    AssemblyLoadContext.Default.Resolving += resolve_assembly


# ---------------------------------------------------------------------------
# DWSIM initialization
# ---------------------------------------------------------------------------

def initialize_dwsim():
    """Initialize .NET and load the headless DWSIM automation library."""

    if not DWSIM_DIR.exists():
        raise FileNotFoundError(
            f"DWSIM installation not found:\n{DWSIM_DIR}"
        )

    if not DWSIM_AUTOMATION_DLL.exists():
        raise FileNotFoundError(
            f"DWSIM automation DLL not found:\n"
            f"{DWSIM_AUTOMATION_DLL}\n\n"
            "Build DWSIM.Automation.DynamicRunner first."
        )

    load("coreclr")

    setup_dwsim_dependency_resolver()

    import clr

    clr.AddReference(str(DWSIM_AUTOMATION_DLL))

    from DWSIM.DynamicRunner import DynamicsAutomation

    print("  Creating DynamicsAutomation...")

    automation = DynamicsAutomation()

    return automation


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():

    print("=" * 60)
    print("DWSIM Python Automation - Screening Task")
    print("=" * 60)

    # ---------------------------------------------------------------
    # Initialize DWSIM
    # ---------------------------------------------------------------

    print("\nInitializing DWSIM...")

    automation = initialize_dwsim()

    print("DWSIM headless automation initialized successfully!")

    # ---------------------------------------------------------------
    # Create headless flowsheet
    # ---------------------------------------------------------------

    from DWSIM.DynamicRunner import Flowsheet

    print("\nCreating headless flowsheet...")

    flowsheet = Flowsheet(None, None)
    flowsheet.Init()

    print("Headless flowsheet created!")

    # ---------------------------------------------------------------
    # Add compounds
    # ---------------------------------------------------------------

    print("\nAdding compounds...")

    compounds = [
        "N-pentane",
        "Isopentane",
    ]

    for compound in compounds:

        print(f"  Adding: {compound}")

        flowsheet.AddCompound(compound)

    print(
        f"Selected compounds: "
        f"{flowsheet.SelectedCompounds.Count}"
    )

    # ---------------------------------------------------------------
    # Add Peng-Robinson property package
    # ---------------------------------------------------------------

    print("\nAdding Peng-Robinson property package...")

    property_package = flowsheet.CreateAndAddPropertyPackage(
        "Peng-Robinson (PR)"
    )

    print(f"Property package: {property_package.Tag}")

    print(
        f"Property packages: "
        f"{flowsheet.PropertyPackages.Count}"
    )

    
    # ---------------------------------------------------------------
    # Create PFR and material streams
    # ---------------------------------------------------------------

    print("\nCreating PFR and material streams...")

    feed = flowsheet.AddFlowsheetObject(
        "Material Stream",
        "PFR Feed"
    )

    pfr = flowsheet.AddFlowsheetObject(
        "Plug-Flow Reactor (PFR)",
        "PFR"
    )

    product = flowsheet.AddFlowsheetObject(
        "Material Stream",
        "PFR Product"
    )

    
    # ---------------------------------------------------------------
    # Configure PFR
    # ---------------------------------------------------------------

    print("\nConfiguring PFR...")

    pfr.Volume = 1.0
    pfr.dV = 0.01

    from DWSIM.UnitOperations.Reactors import OperationMode

    pfr.ReactorOperationMode = OperationMode.Isothermic

    print(f"  Volume : {pfr.Volume} m³")
    print(f"  dV     : {pfr.dV} m³")
    print(f"  Mode   : {pfr.ReactorOperationMode}")

    # ---------------------------------------------------------------
    # Configure PFR feed
    # ---------------------------------------------------------------

    print("\nConfiguring PFR feed...")

    # Get the actual MaterialStream .NET type.
    feed_type = feed.GetType()

    # Access the Phases property from the concrete MaterialStream type.
    phases_property = feed_type.GetProperty("Phases")
    phases = phases_property.GetValue(feed)

    # Get phase 0.
    phase0 = phases[0]

    # Temperature
    phase0.Properties.temperature = 500.0

    # Pressure
    phase0.Properties.pressure = 101325.0

    # Molar flow
    phase0.Properties.molarflow = 1.0

    # Pure n-pentane feed
    phase0.Compounds["N-pentane"].MolarFraction = 1.0
    phase0.Compounds["Isopentane"].MolarFraction = 0.0

    print("  Temperature : 500 K")
    print("  Pressure    : 101325 Pa")
    print("  Molar flow  : 1 mol/s")
    print("  N-pentane   : 1.0")
    print("  Isopentane  : 0.0")

    # ---------------------------------------------------------------
    # Create kinetic reaction
    # ---------------------------------------------------------------

    print("\nCreating kinetic reaction...")

    from System.Collections.Generic import Dictionary

    # Reaction:
    #
    # n-pentane -> isopentane
    #
    # Reactant = negative coefficient
    # Product  = positive coefficient

    stoich = Dictionary[str, float]()

    stoich["N-pentane"] = -1.0
    stoich["Isopentane"] = 1.0

    # First-order reaction in n-pentane.
    direct_orders = Dictionary[str, float]()

    direct_orders["N-pentane"] = 1.0
    direct_orders["Isopentane"] = 0.0

    # Irreversible reaction, so reverse order is zero.

    reverse_orders = Dictionary[str, float]()

    reverse_orders["N-pentane"] = 0.0
    reverse_orders["Isopentane"] = 0.0

    reaction = flowsheet.CreateKineticReaction(
        "Pentane_Isomerization",
        "Kinetic isomerization of n-pentane to isopentane",
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

    flowsheet.AddReaction(reaction)

    print("✓ Kinetic reaction created")
    print(f"  Reaction ID : {reaction.ID}")
    print(f"  Reaction   : {reaction.Name}")

    # ---------------------------------------------------------------
    # Create reaction set
    # ---------------------------------------------------------------

    print("\nCreating reaction set...")

    reaction_set = flowsheet.CreateReactionSet(
        "PFR_Reaction_Set",
        "Reaction set for n-pentane isomerization"
    )

    flowsheet.AddReactionSet(reaction_set)

    flowsheet.AddReactionToSet(
        reaction.ID,
        reaction_set.ID,
        True,
        0
    )

    print("✓ Reaction set created")
    print(f"  Set ID   : {reaction_set.ID}")
    print(f"  Set name : {reaction_set.Name}")

    # ---------------------------------------------------------------
    # Assign reaction set to PFR
    # ---------------------------------------------------------------

    pfr.ReactionSetID = reaction_set.ID
    pfr.ReactionSetName = reaction_set.Name

    print("\n✓ Reaction set assigned to PFR")
    print(f"  PFR reaction set : {pfr.ReactionSetID}")

    # ---------------------------------------------------------------
    # Connect streams
    # ---------------------------------------------------------------

    print("\nConnecting streams...")

    flowsheet.ConnectObjects(
        feed.GraphicObject,
        pfr.GraphicObject,
        0,
        0
    )

    flowsheet.ConnectObjects(
        pfr.GraphicObject,
        product.GraphicObject,
        0,
        0
    )

    print("✓ Feed connected to PFR")
    print("✓ PFR connected to product")

    # ---------------------------------------------------------------
    # Run PFR simulation
    # ---------------------------------------------------------------

    print("\nRunning PFR simulation...")

    try:
        errors = flowsheet.RequestCalculationAndWait()

        if errors is not None and errors.Count > 0:
            print("\n✗ DWSIM reported calculation errors:")

            for error in errors:
                print(f"  - {error}")

            raise RuntimeError("Flowsheet calculation failed.")

        print("✓ PFR simulation completed!")

    except Exception as e:
        print("✗ PFR simulation failed!")
        print(e)
        raise
    # ---------------------------------------------------------------
    # Status
    # ---------------------------------------------------------------

    print("\n" + "-" * 60)
    print("PFR FLOWSHEET STATUS")
    print("-" * 60)

    print(
        f"Simulation objects : "
        f"{flowsheet.SimulationObjects.Count}"
    )

    print(
        f"Property packages  : "
        f"{flowsheet.PropertyPackages.Count}"
    )

    print(
        f"Selected compounds : "
        f"{flowsheet.SelectedCompounds.Count}"
    )

    print(
        f"Reactions          : "
        f"{flowsheet.Reactions.Count}"
    )

    print(
        f"Reaction sets      : "
        f"{flowsheet.ReactionSets.Count}"
    )

    print(
        f"PFR reaction set   : "
        f"{pfr.ReactionSetID}"
    )

    print("-" * 60)

    print("\n✓ Thermodynamic setup successful!")
    print("✓ N-pentane loaded")
    print("✓ Isopentane loaded")
    print("✓ Peng-Robinson loaded")
    print("✓ PFR configured")
    print("✓ Feed configured")
    print("✓ Kinetic reaction created")
    print("✓ Reaction set created")
    print("✓ Reaction set assigned to PFR")
    print("✓ Streams connected")

    print("\nReady for PFR simulation.")


if __name__ == "__main__":
    main()