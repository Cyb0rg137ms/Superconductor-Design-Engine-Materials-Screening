"""McMillan and Allen-Dynes estimates of the electron-phonon T_c (vectorised).

Allen & Dynes, Phys. Rev. B 12, 905 (1975):

    T_c = f1 f2 ω_log / 1.2 · exp[−1.04(1+λ) / (λ − μ*(1+0.62λ))]
    f1  = [1 + (λ/Λ1)^{3/2}]^{1/3},             Λ1 = 2.46 (1 + 3.8 μ*)
    f2  = 1 + (ω̄2/ω_log − 1) λ² / (λ² + Λ2²),    Λ2 = 1.82 (1 + 6.3 μ*) (ω̄2/ω_log)

All frequencies are in kelvin. Returns 0 where the exponent's denominator is ≤ 0
(Coulomb repulsion wins) or λ ≤ 0.
"""

from __future__ import annotations

import numpy as np
from numpy.typing import ArrayLike, NDArray


def _exponent(
    lam: NDArray[np.float64], mu: NDArray[np.float64]
) -> tuple[NDArray[np.float64], NDArray[np.bool_]]:
    den = lam - mu * (1.0 + 0.62 * lam)
    ok = (lam > 0) & (den > 0)
    safe = np.where(ok, den, 1.0)
    return np.where(ok, -1.04 * (1.0 + lam) / safe, -np.inf), ok


def mcmillan_tc(omega_log: ArrayLike, lam: ArrayLike, mu_star: ArrayLike = 0.1) -> NDArray[np.float64]:
    """McMillan formula in the Allen-Dynes form (f1 = f2 = 1)."""
    w, la, mu = (np.asarray(x, dtype=float) for x in (omega_log, lam, mu_star))
    ex, ok = _exponent(la, mu)
    return np.where(ok, w / 1.2 * np.exp(ex), 0.0)


def strong_coupling_factors(
    lam: ArrayLike, mu_star: ArrayLike = 0.1, omega2_ratio: ArrayLike = 1.0
) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    la, mu, r = (np.asarray(x, dtype=float) for x in (lam, mu_star, omega2_ratio))
    lam1 = 2.46 * (1.0 + 3.8 * mu)
    lam2 = 1.82 * (1.0 + 6.3 * mu) * r
    f1 = np.cbrt(1.0 + (np.clip(la, 0, None) / lam1) ** 1.5)
    f2 = 1.0 + (r - 1.0) * la**2 / (la**2 + lam2**2)
    return f1, f2


def allen_dynes_tc(
    omega_log: ArrayLike, lam: ArrayLike, mu_star: ArrayLike = 0.1, omega2_ratio: ArrayLike = 1.0
) -> NDArray[np.float64]:
    """Allen-Dynes T_c in K. ``omega2_ratio`` = ω̄2/ω_log (1.0 turns the shape correction off)."""
    f1, f2 = strong_coupling_factors(lam, mu_star, omega2_ratio)
    return f1 * f2 * mcmillan_tc(omega_log, lam, mu_star)
