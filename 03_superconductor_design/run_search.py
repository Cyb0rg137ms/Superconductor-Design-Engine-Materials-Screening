"""
run_search.py
==============
Executable pipeline that runs the materials discovery process,
filtering and ranking candidate compounds based on pressure and Tc.
"""

from materials.database import MaterialsDatabase
from materials.designer import SuperconductorDesigner
from materials.visualizer import render_ascii_chart, try_save_plot

def run_materials_screening(max_pressure: float = 10.0, min_tc: float = 270.0):
    """
    Main entry point for screening compounds.
    
    Args:
        max_pressure: Maximum synthesis pressure in GPa.
        min_tc: Minimum transition temperature in Kelvin.
    """
    print("==================================================")
    print("      SUPERCONDUCTOR MATERIALS DISCOVERY PIPELINE ")
    print("==================================================")
    print(f"Screening parameters:")
    print(f"  Max Synthesis Pressure: {max_pressure} GPa")
    print(f"  Min Critical Temp (Tc): {min_tc} K")
    print("--------------------------------------------------")
    
    db = MaterialsDatabase()
    designer = SuperconductorDesigner()
    
    # Filter candidates from database
    pressure_candidates = db.filter_by_pressure(max_pressure)
    eligible_candidates = [c for c in pressure_candidates if c["tc_predicted"] >= min_tc]
    
    print(f"Found {len(eligible_candidates)} compounds matching screening parameters:")
    for idx, c in enumerate(eligible_candidates):
        print(f"\n[{idx + 1}] Compound: {c['composition']}")
        print(f"    Predicted Tc: {c['tc_predicted']:.1f} K ({c['tc_predicted'] - 273.15:.1f}°C)")
        print(f"    Required Pressure: {c['pressure_gpa']:.1f} GPa")
        print(f"    Theoretical Basis: {c['theoretical_basis']}")
        print(f"    Key Innovation: {c['key_innovation']}")
        print(f"    Synthesis Path: {c['synthesis_route']}")
        print(f"    Confidence Score: {c['confidence']:.2f}")
        
    # Render visual ASCII chart
    render_ascii_chart(db.get_all_materials())
    
    # Save PNG if matplotlib is available
    try_save_plot(db.get_all_materials(), "superconductor_distribution.png")
    
    # Evaluate a custom user-defined clathrate composition
    print("\nEvaluating custom hypothetical hydrogen clathrate cage:")
    # Cage with 10 hydrogen atoms and Calcium base
    custom_res = designer.evaluate_clathrate(hydrogen_count=10, heavy_atom_mass=40.0)
    print(f"  Composition Estimate: H10-Ca")
    print(f"  Predicted Tc: {custom_res['predicted_tc']:.1f} K")
    print(f"  Phonon Frequency average (omega_log): {custom_res['omega_log_k']:.1f} K")
    print(f"  Coupling Strength (lambda): {custom_res['lambda']:.2f}")
    print("==================================================")

if __name__ == "__main__":
    run_materials_screening(max_pressure=10.0, min_tc=270.0)
