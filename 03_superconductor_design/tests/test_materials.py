import pytest
from materials.database import MaterialsDatabase
from materials.designer import SuperconductorDesigner, calculate_allen_dynes_tc

def test_database_loading():
    db = MaterialsDatabase()
    all_m = db.get_all_materials()
    assert len(all_m) > 0
    # Check that CaH12 is in database
    cah12 = next(m for m in all_m if m["composition"] == "CaH12")
    assert cah12["tc_predicted"] == 305.0
    assert cah12["pressure_gpa"] == 8.0

def test_database_filtering():
    db = MaterialsDatabase()
    
    # Filter for low pressure (ambient or <= 1.0 GPa)
    ambient_m = db.filter_by_pressure(1.0)
    assert len(ambient_m) > 0
    assert all(m["pressure_gpa"] <= 1.0 for m in ambient_m)
    
    # Filter for high Tc
    high_tc = db.filter_by_tc(300.0)
    assert len(high_tc) > 0
    assert all(m["tc_predicted"] >= 300.0 for m in high_tc)

def test_allen_dynes_math():
    # Test conventional parameters
    # High frequency, strong coupling
    tc = calculate_allen_dynes_tc(omega_log=1000.0, lmbda=2.0, mu_star=0.1)
    assert tc > 0
    assert tc < 1000.0
    
    # Zero coupling -> zero Tc
    tc_zero = calculate_allen_dynes_tc(omega_log=1000.0, lmbda=0.0, mu_star=0.1)
    assert tc_zero == 0.0
    
    # Coulomb pseudopotential overrides coupling -> zero Tc
    tc_choked = calculate_allen_dynes_tc(omega_log=1000.0, lmbda=0.1, mu_star=0.2)
    assert tc_choked == 0.0

def test_clathrate_evaluation():
    designer = SuperconductorDesigner(mu_star=0.1)
    # Estimate light clathrate (Hydrogen-rich + Lithium base)
    res = designer.evaluate_clathrate(hydrogen_count=12, heavy_atom_mass=6.94)
    assert res["predicted_tc"] > 0
    assert res["lambda"] >= 0.5
    assert res["omega_log_k"] > 0
