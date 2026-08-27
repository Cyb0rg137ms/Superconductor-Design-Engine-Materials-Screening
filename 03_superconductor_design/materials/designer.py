"""
designer.py
===========
Implements the Allen-Dynes-BCS physics formulas to calculate critical transition 
temperatures (Tc) of candidate materials under target configurations.
"""

import math
from typing import Dict, Any

def calculate_allen_dynes_tc(omega_log: float, lmbda: float, mu_star: float, 
                             ratio: float = 1.2) -> float:
    """
    Calculates the critical transition temperature (Tc) in Kelvin using the full 
    Allen-Dynes equation.
    
    Args:
        omega_log: Logarithmic average phonon frequency (in Kelvin).
        lmbda: Electron-phonon coupling strength coefficient (lambda).
        mu_star: Coulomb pseudopotential parameter (mu*).
        ratio: Ratio of average square frequency to omega_log. Default is 1.2.
        
    Returns:
        The transition temperature Tc in Kelvin.
    """
    if lmbda <= 0:
        return 0.0
        
    # Standard McMillan/Allen-Dynes exponent numerator and denominator
    num = 1.04 * (1.0 + lmbda)
    den = lmbda - mu_star * (1.0 + 0.62 * lmbda)
    
    if den <= 0:
        return 0.0
        
    exponent = -num / den
    
    # Allen-Dynes correction factors f1 and f2
    # f1 accounts for strong coupling correction
    f1 = (1.0 + (lmbda / (1.01 * (1.0 + 2.0 * mu_star))) ** 1.5) ** (1.0 / 3.0)
    
    # f2 accounts for shape correction of the Eliashberg spectral function
    a = (ratio - 1.0) * (lmbda ** 2)
    b = (lmbda ** 2) + (1.61 * (1.0 + 2.0 * mu_star)) ** 2
    f2 = 1.0 + a / b
    
    # Tc calculation
    tc = (f1 * f2 * omega_log) / 1.20 * math.exp(exponent)
    return tc

class SuperconductorDesigner:
    """Estimates and evaluates transition temperatures of candidate material stoichiometry."""
    
    def __init__(self, mu_star: float = 0.1):
        """
        Args:
            mu_star: General Coulomb pseudopotential. Default is 0.1 (standard value).
        """
        self.mu_star = mu_star
        
    def evaluate_clathrate(self, hydrogen_count: int, heavy_atom_mass: float) -> Dict[str, Any]:
        """
        Evaluates a hypothetical hydrogen-rich clathrate cage compound.
        Debye/phonon frequency scales inversely with square root of mass.
        """
        # Estimates based on LaH10 properties and modified by mass ratios
        base_hydrogen_mass = 1.0
        reduced_mass = math.sqrt(base_hydrogen_mass / (hydrogen_count * 0.1 + heavy_atom_mass * 0.9))
        
        # Estimate omega_log based on light clathrate scaling
        omega_log = 2000.0 * reduced_mass
        
        # Estimate electron-phonon coupling lambda based on hydrogen densities
        lmbda = 0.2 * hydrogen_count * (100.0 / heavy_atom_mass) ** 0.2
        lmbda = max(0.5, min(3.0, lmbda))
        
        tc = calculate_allen_dynes_tc(omega_log, lmbda, self.mu_star)
        
        return {
            "predicted_tc": tc,
            "lambda": lmbda,
            "omega_log_k": omega_log,
            "coulomb_pseudopotential": self.mu_star
        }
