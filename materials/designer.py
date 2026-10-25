"""
designer.py
===========
Implements the Allen-Dynes-BCS physics formulas to calculate critical transition
temperatures (Tc) of candidate materials under target configurations.
"""

import math
from typing import Any

from scdesign.allen_dynes import allen_dynes_tc


def calculate_allen_dynes_tc(omega_log: float, lmbda: float, mu_star: float, ratio: float = 1.2) -> float:
    """
    Allen-Dynes T_c in kelvin (v1 signature kept).

    v2: delegates to :func:`scdesign.allen_dynes.allen_dynes_tc`. v1 used wrong
    constants in the correction factors (Λ1 = 1.01(1+2μ*) instead of 2.46(1+3.8μ*),
    Λ2 = 1.61(1+2μ*) instead of 1.82(1+6.3μ*)·ω̄2/ω_log), which overestimated T_c
    (e.g. 8.9 K instead of 6.9 K for the Pb-like inputs ω_log=58 K, λ=1.55, μ*=0.13).

    Args:
        omega_log: logarithmic average phonon frequency (K).
        lmbda: electron-phonon coupling λ.
        mu_star: Coulomb pseudopotential μ*.
        ratio: ω̄2/ω_log (default 1.2 as in v1).
    """
    return float(allen_dynes_tc(omega_log, lmbda, mu_star, ratio))


class SuperconductorDesigner:
    """Estimates and evaluates transition temperatures of candidate material stoichiometry."""

    def __init__(self, mu_star: float = 0.1):
        """
        Args:
            mu_star: General Coulomb pseudopotential. Default is 0.1 (standard value).
        """
        self.mu_star = mu_star

    def evaluate_clathrate(self, hydrogen_count: int, heavy_atom_mass: float) -> dict[str, Any]:
        """
        Evaluates a hypothetical hydrogen-rich clathrate cage compound.

        HEURISTIC, NOT A PREDICTION: λ and ω_log come from ad-hoc scaling rules
        (ω_log ∝ 1/sqrt(effective mass), λ ∝ H count), not from DFT/Eliashberg
        calculations, so the resulting T_c only illustrates the formula.
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
            "coulomb_pseudopotential": self.mu_star,
        }
