"""scdesign: validated electron-phonon T_c formulas and a vectorised mean-field BCS solver."""

from scdesign.allen_dynes import allen_dynes_tc, mcmillan_tc, strong_coupling_factors
from scdesign.bcs import (
    BCS_RATIO,
    KB_EV,
    Chain,
    bcs_universal_gap,
    coherence_length,
    density_of_states,
    solve_gap,
    solve_tc,
)

__version__ = "2.0.0"
__all__ = [
    "BCS_RATIO",
    "KB_EV",
    "Chain",
    "__version__",
    "allen_dynes_tc",
    "bcs_universal_gap",
    "coherence_length",
    "density_of_states",
    "mcmillan_tc",
    "solve_gap",
    "solve_tc",
    "strong_coupling_factors",
]
